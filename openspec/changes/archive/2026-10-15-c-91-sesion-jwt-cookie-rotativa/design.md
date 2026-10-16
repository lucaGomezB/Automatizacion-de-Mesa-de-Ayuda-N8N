## Context

Ver `proposal.md` — Why, y las specs delta (`specs/identity-access-hardening/spec.md`, `specs/frontend-session-lifecycle/spec.md`) para los requisitos. Estado actual verificado:

- Backend ya tiene rotacion con deteccion de reuso: `app/services/auth_service.py` (`issue_refresh_token`, `rotate_refresh_token`, `revoke_refresh_token`, `revoke_all_sessions`), rutas `/login` `/refresh` `/logout` (`app/routes/auth.py`) y `RefreshToken` (`app/models/refresh_token.py`, con `expires_at`, `revoked_at`, `rotated_from`).
- `settings.py`: `jwt_access_expire_minutes = 15`, `jwt_refresh_expire_minutes = 10080`. `jwt_expire_minutes = 1440` es config muerta (nadie la lee). `.env.example` documenta los tres.
- La rotacion actual ya es deslizante (cada rotacion emite `expires_at = now + 7 dias`), de modo que la semantica de inactividad de facto ya existe pero no esta declarada.
- El refresh viaja HOY en el cuerpo (`TokenResponse.refresh_token`; `RefreshRequest`/`LogoutRequest` lo reciben por cuerpo). Los tests lo asumen.
- Frontend en memoria (`src/services/api.ts` `_authToken`/`_refreshToken`; `src/contexts/AuthContext.tsx` sin rehidratacion). Refresco silencioso single-flight ante 401. No hay modal de expiracion.
- Topologia prod same-origin: nginx (`nginx/nginx.conf`) sirve el frontend en `/` y proxya `/api/` a `backend:8000`; `mesa.local` es un unico origen. Dev es cross-origin (`localhost:3000` -> `localhost:8000`). `main.py` usa `allow_credentials=False` con `allow_origins=["*"]`.
- N8N (`n8n/workflow.json`, nodo "Login operador") consume SOLO `access_token` del login; no usa refresh.
- **Gobernanza CRITICAL (auth/seguridad): el apply requiere aprobacion humana explicita.**

## Goals / Non-Goals

**Goals:**
- Access token de 30 min y sesion que sobrevive el reload via cookie de refresh `HttpOnly`.
- Gobierno explicito de la inactividad de 7 dias (por sesion), con refresh deslizante y sin tope absoluto de vida.
- Aviso proactivo de expiracion con continuidad por consentimiento y cierre automatico tras una ventana de gracia de 30 s.
- CSRF resuelto sobre la superficie que opera con cookie; `get_current_user`/`token_version` intactos.

**Non-Goals:**
- No se rediseña el modelo `RefreshToken` ni la deteccion de reuso.
- No se implementa MFA ni el keyring (ya existen; el login en dos pasos solo cambia su transporte de cookie).
- No se agrega un proveedor de identidad ni sesiones server-side.
- No se migran datos de incidentes ni catalogos.

## Decisions

### D1 — TTL de access: 15 -> 30 min

Default de `jwt_access_expire_minutes` a 30. `expires_in` ya se calcula del settings (`auth.py::_build_token_response`), por lo que el cambio se propaga a login y MFA verify. `.env.example` documenta `# JWT_ACCESS_EXPIRE_MINUTES=30`. `jwt_expire_minutes` es DEAD: se marca como DEPRECADA y documentada en `settings.py` y en `.env.example`, **sin eliminar la setting** (OQ-8 resuelto: deprecar + documentar). Tests `test_auth_tokens.py:90`, `test_c63b:161`, `test_c63a:64` se actualizan a `30 * 60` / `== 30`.

- **Rationale**: cambio pedido por el autor; el valor es configurable y no toca la logica de firma.
- **Alternativas**: dejarlo configurable sin cambiar el default — rechazada, el autor fijo 30.

### D2 — Inactividad de 7 dias: refresh deslizante gobernado en spec (sin columna nueva)

Se mantiene el mecanismo actual: cada rotacion exitosa emite un refresh nuevo con ventana completa (`now + jwt_refresh_expire_minutes`). Un token cuya ventana vence se rechaza y revoca (`rotate_refresh_token` ya lo hace). "7 dias sin acceso" == "7 dias sin rotar". El cambio es de gobierno: la spec IAH-013 lo declara y lo parametriza. La cadena de rotacion (`rotated_from`) acota la inactividad a la SESION, no a la cuenta.

- **Rationale**: cumple el requisito sin migracion ni riesgo de datos; el comportamiento observable es equivalente al de un ancla explicita.
- **Alternativas**: agregar `last_used_at` (o `idle_expires_at`) como columna y anclar explicitamente — mayor claridad y observabilidad, pero exige migracion Alembic y logica adicional. **Descartada (OQ-4 resuelto): se mantiene el refresh deslizante, sin columna nueva ni migracion.** No se define un tope absoluto de vida total de la sesion; es un concepto distinto y queda **descartado (OQ-3 resuelto: NINGUNO)**.

### D3 — Option A: refresh en cookie `HttpOnly`; access en memoria

- **Set**: `login` (un paso), `mfa/verify` y `refresh` setean la cookie con el valor opaco recien emitido, `Path=/api/v1/auth`, `HttpOnly`, `Secure`, `SameSite=Strict`, `Max-Age = jwt_refresh_expire_minutes * 60`.
- **Read**: `refresh` y `logout` leen el valor desde la cookie (no del cuerpo). `RefreshRequest`/`LogoutRequest` dejan de ser requeridos para el flujo de navegador.
- **Clear**: `logout` responde con `Set-Cookie` de borrado (max-age 0).
- **Body**: la respuesta de login/MFA/refresh deja de incluir `refresh_token` para el flujo de navegador (**BREAKING**); conserva `access_token`, `token_type`, `expires_in`. N8N no se ve afectado (solo usa `access_token`).
- **Boot**: el frontend, al arrancar, invoca `/refresh` con `withCredentials`; si hay cookie vigente obtiene access nuevo; si no, queda no autenticado.

- **Rationale**: el refresh deja de ser legible por JS (mitiga robo por XSS) y la sesion sobrevive el reload. Es la opcion elegida por el autor.
- **Alternativas consideradas**: (a) `localStorage`/cookie legible por JS — descartada por XSS; (b) doble token con access en cookie — reabre CSRF en toda la API; (c) mantener el refresh en el cuerpo y ademas cookie — anula el beneficio de `HttpOnly`.

### D4 — CSRF sobre la superficie de cookie

Solo `/refresh` y `/logout` derivan autoridad de la cookie. Mitigacion: `SameSite=Strict` (la cookie no viaja en navegacion cross-site) + verificacion del header `Origin` contra la lista permitida en esos endpoints. El resto de la API sigue autenticada por `Authorization: Bearer` en memoria (inmune a CSRF). **NO se usa doble envio de token (double-submit): descartado (OQ-5 resuelto).** `/refresh` y `/logout` dejan de aceptar el refresh por cuerpo para el flujo de navegador.

- **Rationale**: prohibir de plano el origen cruzado cierra el vector de CSRF sin infraestructura extra; el bearer en memoria ya protege el resto.
- **Alternativas**: doble-submit con cookie CSRF adicional (mas robusto ante navegadores viejos, mas superficie); token anti-CSRF por sesion (mas estado).

### D5 — CORS y credenciales por entorno

En prod (same-origin) no hace falta CORS con credenciales. En dev cross-origin, `fetch`/axios deben enviar `withCredentials` y el backend necesita `allow_credentials=True` con `allow_origins` EXACTOS (no `*`), `allow_methods` con `POST` y los headers usados. **Decision (OQ-9 resuelto): SI se habilita `allow_credentials=True` con origen exacto en dev `http://localhost:3000`; en prod el trafico es same-origin via nginx (`/api/` proxied) y no requiere CORS cross-origin.** Con `SameSite=Strict`, el dev cross-origin (distinto origen/puerto) puede exigir `SameSite=None; Secure` sobre HTTPS local; se documenta el modo dev de la cookie. Se centraliza en `cors_allow_origins`.

- **Rationale**: la cookie de origen cruzado es el unico punto que rompe en dev; aislarlo evita un falso `Secure`/"cookie no viaja" dificil de depurar.

### D6 — Validacion y revocacion sin cambios

`get_current_user` y `token_version` no se tocan: el access sigue bearer y la revocacion administrativa sigue inmediata. La ventana residual del access (IAH-004) se mantiene: cerrar sesion revoca el refresh y limpia la cookie, pero el access ya emitido vive hasta su TTL. El cierre automatico del frontend (FSL-003) invoca el logout de backend para revocar el refresh.

### D7 — Frontend: rehidratacion, temporizador y modal

- `AuthContext` gana un estado de arranque (`isHydrating`): mientras rehidrata, no se renderizan pantallas protegidas como no autenticadas.
- Al fijar el access token (login, rehidratacion, refresh) se programa un temporizador desde `expires_in`/`exp`. Al dispararse se abre un modal accesible "continuar o cerrar sesion".
- "Continuar" -> `/refresh` (con `withCredentials`); exito: cierra el modal y reinicia el timer. Fallo: cierra sesion y redirige a `/login`.
- Sin respuesta dentro de la ventana de gracia configurable (**default 30 s**, OQ-2 resuelto) -> logout (revoca + limpia) y redirige a `/login`.
- Precedencia: el aviso proactivo es PRIMARIO; el refresco silencioso ante 401 (`api.ts`) se conserva SOLO como respaldo de carrera (timer deriva, pestana en segundo plano) y no sustituye el consentimiento (FSL-005).
- `api.ts`: elimina `_refreshToken` en memoria, agrega `withCredentials: true` a la instancia y a la instancia cruda del refresh, y expone la rehidratacion.

- **Rationale**: el aviso explicito es el requisito del autor; mantener el 401 como respaldo evita expulsar por deriva del timer.

### D8 — Multi-pestana

Un canal de sincronizacion **`BroadcastChannel('session')`** (OQ-7 resuelto) propaga logout/refresh/prompt entre pestanas: un logout cierra el estado en todas; una extension mantiene autenticadas a las demas; el prompt puede mostrarse una vez y difundirse.

### D9 — Estrategia de pruebas (TDD)

- Backend (SQLite unit subset + integration subset cuando toque): cookie seteada/limpiada, `/refresh` lee cookie, TTL 30 min, inactividad con reloj inyectable, reuso, CSRF (origen cruzado rechazado). Reutiliza fixtures `token_client`/`make_client_with_classifier`.
- Frontend (Vitest): rehidratacion al arranque, timer/modal, "continuar" extiende, sin respuesta cierra y redirige, multi-pestana, ausencia de refresh en almacenamiento JS.

## Risks / Trade-offs

- Contrato `/refresh` y `/logout` cambia (BREAKING) -> declarado; N8N no usa refresh (verificado); tests y frontend se actualizan en el mismo change.
- Cookie no viaja en dev cross-origin -> D5; documentar `withCredentials` + `allow_credentials` + origenes exactos.
- `SameSite=Strict` rompe el dev cross-origin -> variante dev resuelta (OQ-9): `allow_credentials=True` con origen exacto `http://localhost:3000`; documentar el modo dev de la cookie.
- Timer proactivo expulsa en medio de una tarea -> ventana de gracia configurable + "continuar" sin recargar.
- Duplicacion prompt/401 -> precedencia declarada (FSL-005); el 401 no extiende sin consentimiento.
- Falsos "no autenticado" parpadeando al arrancar -> estado `isHydrating` bloquea el render de rutas protegidas.
- Rotacion de keys JWT durante sesion en vuelo -> ya cubierta por IAH-008; no se toca.

## Migration Plan

1. Backend: config (D1) + transporte cookie (D3/D4/D5) + inactividad gobernada (D2). Ajustar tests.
2. Frontend: rehidratacion (D7), timer/modal, multi-pestana (D8). Ajustar tests.
3. Verificar suites backend y frontend, y `openspec validate --strict`.
4. Rollback: reponer `refresh_token` en el cuerpo y el envio por body en `/refresh`/`/logout`; quitar `withCredentials`. Volver `jwt_access_expire_minutes` a 15 si hiciera falta. Sin datos irreversibles.

## Open Questions

Todas RESUELTAS por el autor (ver `proposal.md` -> Resolved Decisions). Ninguna queda abierta.

1. **Timeout del modal: RESUELTO — 30 s** (ventana de gracia configurable del frontend, default 30 s).
2. **Tope absoluto de sesion: RESUELTO — NINGUNO**; solo aplica la inactividad de 7 dias.
3. **Ancla de inactividad vs deslizante: RESUELTO — refresh DESLIZANTE**; sin `last_used_at`, sin migracion.
4. **CSRF: RESUELTO — `SameSite=Strict` + verificacion de `Origin`**; sin doble-submit; `/refresh` y `/logout` dejan de aceptar el refresh por cuerpo.
5. **Precedencia prompt vs 401: RESUELTO — prompt proactivo primario; el 401 silencioso se CONSERVA como respaldo.**
6. **Multi-pestana: RESUELTO — `BroadcastChannel`**; logout/refresh se propagan a todas las pestanas.
7. **`jwt_expire_minutes`: RESUELTO — DEPRECAR + documentar**; no se elimina la setting.
8. **CORS/dev cross-origin: RESUELTO — `allow_credentials=True` con origenes EXACTOS** (dev `http://localhost:3000`; prod same-origin por nginx).
