## Why

La sesion actual no sobrevive a un reload de pagina y no tiene gobierno explicito de inactividad: el frontend guarda access y refresh token SOLO en memoria (`app.ts` / `AuthContext.tsx`), de modo que refrescar la pestana expulsa al usuario; el access token dura 15 min; y la regla "7 dias sin acceso" existe de hecho (refresh deslizante) pero no esta declarada en ninguna spec. Ademas, la sesion nunca se cierra por inactividad del usuario ni avisa que el token esta por expirar: el unico mecanismo es un refresco silencioso ante 401. Este change formaliza el ciclo de vida de sesion (TTL de access 30 min, inactividad de 7 dias explicitada, transporte del refresh en cookie HttpOnly) y agrega el aviso proactivo de expiracion con cierre automatico.

## What Changes

- **TTL de access 15 -> 30 min** (`jwt_access_expire_minutes`). Se actualiza `.env.example` y se documenta `jwt_expire_minutes` como **DEPRECADA** (no se elimina la setting).
- **Inactividad explicita de 7 dias con refresh DESLIZANTE**: la spec pasa a gobernar la regla "sesion revocada tras una semana sin acceso". Se mantiene el refresh deslizante (cada rotacion renueva la ventana); NO se agrega columna de inactividad ni migracion. **NO hay tope absoluto de vida de sesion**: la unica regla de cierre temporal es la inactividad de 7 dias.
- **Persistence Option A (BREAKING para el transporte del refresh)**: el backend entrega el refresh token en una cookie `HttpOnly` + `Secure` + `SameSite`, la setea en login/refresh y la limpia en logout; el access token sigue en memoria del frontend; el arranque de la app rehidrata la sesion con un `/refresh` silencioso que lee la cookie. `refresh_token` deja de exponerse en el cuerpo de la respuesta para el flujo de navegador.
- **UX de expiracion en el frontend**: temporizador proactivo derivado de `expires_in`/`exp`; ante la expiracion, un modal pide "continuar o cerrar sesion"; "continuar" refresca y extiende; sin respuesta dentro de una **ventana de gracia de 30 s** (constante configurable del frontend, default 30 s), la sesion se cierra sola (revoca + redirige a `/login`). Se reconcilia con el refresco silencioso ante 401 existente (que se CONSERVA como fallback) y la coherencia multi-pestana se resuelve con **`BroadcastChannel`** (logout/refresh se propagan a todas las pestanas).
- **CSRF**: `SameSite=Strict` en la cookie + verificacion del header `Origin` en `/refresh` y `/logout`; NO se usa doble-submit token. Solo esos dos endpoints operan sobre la cookie; el resto queda protegido por bearer en memoria y se preserva la interaccion con `get_current_user`/`token_version`.
- **CORS con credenciales**: `allow_credentials=True` con origenes EXACTOS — dev `http://localhost:3000`; prod same-origin via nginx (sin CORS cross-origin).

## Capabilities

### New Capabilities

- `frontend-session-lifecycle`: ciclo de vida de la sesion en el frontend — rehidratacion al arranque, aviso proactivo de expiracion del access token, extension por consentimiento del usuario, cierre automatico ante falta de respuesta y coherencia multi-pestana, sin almacenar el refresh token en ningun medio accesible por JS.

### Modified Capabilities

- `identity-access-hardening`: IAH-003 cambia el TTL por defecto del access token (15 -> 30 min) y declara el gobierno de inactividad; IAH-004 incorpora el borrado de la cookie en logout y la revocacion por cierre automatico. Se AGREGAN IAH-013 (cierre por inactividad de 7 dias) e IAH-014 (transporte del refresh en cookie y rehidratacion).

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Backend/app/config/settings.py` | Modified | `jwt_access_expire_minutes` 15 -> 30; `jwt_expire_minutes` marcada como DEPRECADA (no se elimina) |
| `App/Backend/.env.example` | Modified | Documentar `JWT_ACCESS_EXPIRE_MINUTES=30`, la cookie y que `jwt_expire_minutes` esta deprecada |
| `App/Backend/app/routes/auth.py` | Modified | login/refresh/logout setean/limpian la cookie; `/refresh` lee la cookie |
| `App/Backend/app/services/auth_service.py` | Modified | Semantica explicita de inactividad (rotacion deslizante) |
| `App/Backend/app/schemas/auth.py` | Modified | `refresh_token` sale del cuerpo del flujo de navegador |
| `App/Backend/app/main.py` | Modified | CORS: `allow_credentials` + origenes exactos para cookies en dev |
| `App/Frontend/src/services/api.ts` | Modified | Elimina el refresh en memoria; requests con `withCredentials`; boot rehydration |
| `App/Frontend/src/contexts/AuthContext.tsx` | Modified | Rehidratacion al arranque; estado de expiracion |
| `App/Frontend/src` (nuevo) | New | Modal de expiracion, temporizador, sincronizacion multi-pestana |
| `App/Backend/tests/test_auth_tokens.py` | Modified | `expires_in == 30 * 60` (hoy `15 * 60`) |
| `App/Backend/tests/test_c63a_auth_hardening.py` | Modified | Default 15 -> 30 |
| `App/Backend/tests/test_c63b_login_two_step.py` | Modified | `expires_in == 30 * 60` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Romper el contrato de refresh/logout al pasar a cookie | Alta | Change BREAKING declarado; N8N solo consume `access_token` (verificado en `n8n/workflow.json`, nodo "Login operador"); tests y frontend se actualizan |
| CSRF sobre `/refresh` y `/logout` | Media | `SameSite=Strict` + verificacion del header `Origin`; el resto de la API sigue protegida por bearer en memoria |
| Cookies cross-origin en dev (`localhost:3000` -> `:8000`) | Media | En prod nginx es same-origin (`/api/` proxied); en dev `allow_credentials=True` con origen exacto `http://localhost:3000` |
| Timer proactivo que expulsa al usuario en medio de una tarea | Media | Ventana de gracia configurable (default 30 s) antes del cierre automatico; "continuar" extiende sin recargar |
| Duplicar mecanismos (prompt + refresco silencioso 401) | Media | Precedencia fijada: prompt proactivo primario; 401 silencioso CONSERVADO como fallback |

## Rollback Plan

Revertir el commit del change. El cambio de TTL y la semantica de inactividad son configurables; volver a `jwt_access_expire_minutes=15` restaura el valor previo. Para el transporte: reponer la entrega de `refresh_token` en el cuerpo y el envio por `Authorization`/body en `/refresh` y `/logout`, y revertir `withCredentials` en el cliente. No se elimina la tabla ni se agregan campos de datos irreversibles: la inactividad se mantiene con el refresh deslizante (SIN migracion), por lo que el rollback no revierte esquema alguno. Las sesiones vigentes con cookie se invalidan con la revocacion administrativa (`token_version`).

## Dependencies

- Ninguna nueva de runtime. Se reutilizan `RefreshToken`, `auth_service` y el flujo de rotacion existentes.
- **Gobernanza CRITICAL (auth/seguridad): la ejecucion (apply) requiere aprobacion humana explicita antes de escribir codigo.**
- **Leer antes**: `openspec/specs/identity-access-hardening/spec.md` (IAH-003, IAH-004), `openspec/specs/frontend-session-ui/spec.md` (FSU-001), `App/Backend/app/services/auth_service.py`, `App/Backend/app/core/security.py`, `App/Frontend/src/contexts/AuthContext.tsx`, `CHANGES.md`.

## Success Criteria

- [ ] El access token dura 30 min por defecto y `expires_in` refleja `30 * 60` en login y MFA verify.
- [ ] La sesion sobrevive un reload de pagina mediante rehidratacion silenciosa por cookie (`/refresh`).
- [ ] Una sesion sin acceso durante 7 dias queda revocada y exige re-login.
- [ ] Al expirar el access token, la UI pide continuar o cerrar; sin respuesta dentro del timeout, la sesion se cierra y redirige a `/login`.
- [ ] El refresh token viaja en cookie `HttpOnly`+`Secure`+`SameSite`, nunca accesible por JS, y el logout la limpia.
- [ ] `openspec validate c-91-sesion-jwt-cookie-rotativa --strict` pasa.

## Resolved Decisions

Todas las preguntas abiertas quedaron RESUELTAS por el autor y pasan a ser decisiones fijas del change:

1. **Option A (cookie), 30 min de access, inactividad de 7 dias, prompt con cierre automatico: RESUELTO.**
2. **Timeout del modal de expiracion: RESUELTO — 30 SEGUNDOS.** Ventana de gracia de 30 s antes del cierre automatico; constante configurable del frontend con default 30 s; reflejada en FSL-003.
3. **Tope absoluto de sesion: RESUELTO — NINGUNO.** Solo aplica la inactividad de 7 dias; no se define vida maxima absoluta.
4. **Ancla de inactividad vs refresh deslizante: RESUELTO — refresh DESLIZANTE.** Sin columna de inactividad, sin migracion; gobernado solo en spec (IAH-013).
5. **CSRF: RESUELTO — `SameSite=Strict` + verificacion de `Origin`** en `/refresh` y `/logout`; NO se usa doble-submit token.
6. **Precedencia prompt vs 401 silencioso: RESUELTO — prompt proactivo PRIMARIO; el refresco silencioso 401 se CONSERVA como fallback** (FSL-005).
7. **Multi-pestana: RESUELTO — `BroadcastChannel`.** El logout/refresh se propaga a todas las pestanas (FSL-005).
8. **Retiro de `jwt_expire_minutes`: RESUELTO — DEPRECAR + documentar.** No se elimina la setting.
9. **CORS/`allow_credentials`: RESUELTO — SI.** `allow_credentials=True` con origenes EXACTOS: dev `http://localhost:3000`; prod same-origin via nginx.
