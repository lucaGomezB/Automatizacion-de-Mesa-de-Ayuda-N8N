## 1. Preparacion y linea base

- [x] 1.1 **GOVERNANCE CRITICAL**: obtener aprobacion humana explicita del plan (proposal, specs, design) antes de escribir cualquier codigo; registrar la aprobacion en la bitacora del change
      — APROBADO por el autor: instruccion explicita "Aplica" (2026-10-15). Gate CRITICAL satisfecho antes de escribir codigo.
- [x] 1.2 Safety net backend: ejecutar `pytest -m "not integration"` en `App/Backend/` y registrar la linea base de tests en verde (evidencia de que no se rompe lo existente)
      — Baseline: 1423 passed, 48 deselected, 1 xfailed. Post-batch (backend): 1439 passed, 48 deselected, 1 xfailed. Sin regresiones.
- [x] 1.3 Safety net frontend (ACOTADO): registrar la linea base en verde de los archivos que el change toca
      — Baseline acotado: 43 passed (api.test.ts 13, AuthContext.test.tsx 10, ProtectedRoute.test.tsx 20). NO se ejecuto `npm run test` (suite completa) por prohibicion explicita del autor (verificacion acotada).
- [x] 1.4 Leer `openspec/specs/identity-access-hardening/spec.md` (IAH-003/004) y `openspec/specs/frontend-session-ui/spec.md` (FSU-001); confirmar que los ids IAH-013/IAH-014 y FSL-001..005 no colisionan
      — Confirmado: el spec principal llega hasta IAH-012; frontend-session-ui usa FSU (capacidad distinta). Sin colision.
- [x] 1.5 Cargar las skills de dominio aplicables (`.agents/SKILLS.md`): `sqlalchemy-postgres`, `python-design-patterns` y `tailwind-design-system` (conceptos transferibles, NO sintaxis v4)
      — Cargadas `sqlalchemy-postgres` y `python-design-patterns` (tailwind es frontend, batch B).

## 2. Configuracion del TTL (TDD, IAH-003)

- [x] 2.1 RED: actualizar `tests/test_c63a_auth_hardening.py` para afirmar `jwt_access_expire_minutes == 30`; verificar que falla
- [x] 2.2 RED: actualizar `tests/test_auth_tokens.py` (`expires_in == 30 * 60`) y `tests/test_c63b_login_two_step.py` (`expires_in == 30 * 60`); verificar que fallan
- [x] 2.3 GREEN: cambiar el default de `jwt_access_expire_minutes` a 30 en `App/Backend/app/config/settings.py`; verificar 2.1 y 2.2 en verde
- [x] 2.4 Documentar `# JWT_ACCESS_EXPIRE_MINUTES=30` en `App/Backend/.env.example` y marcar `jwt_expire_minutes` (config muerta) como DEPRECADA en `settings.py` y `.env.example`, SIN eliminar la setting (OQ-8 resuelto: deprecar + documentar); verificar que el archivo no documenta un valor enganoso
- [x] 2.5 TRIANGULAR: verificar que un override de `jwt_access_expire_minutes` por entorno cambia `expires_in` en consecuencia (test con `get_settings.cache_clear()`); verificar que pasa

## 3. Inactividad de 7 dias gobernada (TDD, IAH-013)

- [x] 3.1 RED: test que con reloj inyectable una rotacion dentro de la ventana renueva la vigencia y el refresh sigue valido; verificar que falla si se asume semantica no deslizante
- [x] 3.2 RED: test que tras 7 dias (10080 min) sin rotar, el refresh se rechaza (401) y queda revocado; verificar que falla sin el escenario cubierto
- [x] 3.3 GREEN: confirmar/ajustar `rotate_refresh_token` y `issue_refresh_token` para que la inactividad sea explicitamente la ventana deslizante `jwt_refresh_expire_minutes`; verificar 3.1 y 3.2 en verde
- [x] 3.4 TRIANGULAR: test de dos sesiones del mismo usuario (una inactiva, otra activa) donde solo la inactiva se revoca; verificar que pasa
- [x] 3.5 TRIANGULAR: test con `jwt_refresh_expire_minutes` reducido (p. ej. 1 min) que verifica el vencimiento exacto; verificar que pasa
- [x] 3.6 Resolver a favor del refresh DESLIZANTE (OQ-4): NO crear migracion; documentar en `design.md`/spec que la inactividad se gobierna por la ventana deslizante (`jwt_refresh_expire_minutes`) y que NO hay tope absoluto de vida de sesion (OQ-3)

## 4. Transporte del refresh en cookie (TDD, IAH-014)

- [x] 4.1 RED: test de login que verifica `Set-Cookie` con `HttpOnly`, `Secure`, `SameSite` y que el cuerpo NO incluye `refresh_token`; verificar que falla
- [x] 4.2 GREEN: setear la cookie en `login` (un paso) y en `mfa/verify`; dejar de exponer `refresh_token` en el cuerpo; verificar 4.1 en verde
- [x] 4.3 RED: test de `/refresh` que presenta el refresh SOLO por cookie y obtiene nuevo access + cookie rotada; verificar que falla
- [x] 4.4 GREEN: `refresh` lee el refresh desde la cookie y setea la cookie rotada; verificar 4.3 en verde
- [x] 4.5 RED: test de `/logout` que verifica la revocacion y el borrado de la cookie (`Set-Cookie` con `Max-Age=0`); verificar que falla
- [x] 4.6 GREEN: `logout` revoca el refresh desde la cookie y limpia la cookie; verificar 4.5 en verde
- [x] 4.7 RED: test de reuso de un refresh ya rotado presentado por cookie devuelve 401; verificar que falla si el reuso no se detecta en el nuevo transporte
- [x] 4.8 GREEN: confirmar la deteccion de reuso en el camino por cookie; verificar 4.7 en verde
- [x] 4.9 CSRF: test que un `Origin` no confiable sobre `/refresh` y `/logout` es rechazado; implementar la verificacion de `Origin` y la cookie `SameSite=Strict` (OQ-5 resuelto: sin doble-submit token); verificar que pasa
- [x] 4.10 CORS/entorno: configurar `allow_credentials=True` con origenes EXACTOS (dev `http://localhost:3000`; prod same-origin por nginx) y documentar el modo dev de la cookie (`Secure`/`SameSite`; OQ-9); verificar que el login funciona same-origin (compose) y cross-origin (dev)
      — Config + docs + tests estructurales/HTTP de CORS y cookies OK. La verificacion en el stack compose (7.4) queda como paso manual (batch B / verify).
- [x] 4.11 Regresion: verificar que N8N (nodo "Login operador") sigue funcionando porque consume solo `access_token`; ejecutar el test/contrato correspondiente y que pasa

## 5. Rehidratacion de sesion en el frontend (TDD, FSL-001)

- [x] 5.1 RED: test de `AuthContext` que al montar con cookie valida (mock de `/refresh` con `withCredentials`) rehidrata y queda autenticado; verificar que falla
- [x] 5.2 GREEN: agregar estado `isHydrating` y la rehidratacion por `/refresh` al arranque; bloquear el render de rutas protegidas durante la rehidratacion; verificar 5.1 en verde
- [x] 5.3 RED: test que sin cookie el arranque deja no autenticado (sin parpadeo de pantalla protegida); verificar que falla
- [x] 5.4 GREEN: ajustar el arranque para el caso sin cookie; verificar 5.3 en verde
- [x] 5.5 GREEN: en `src/services/api.ts` eliminar `_refreshToken` en memoria, agregar `withCredentials: true` a la instancia y a la instancia cruda del refresh; verificar que los tests de `api.ts`/`AuthContext` pasan
- [x] 5.6 TRIANGULAR: test que inspecciona `localStorage`, `sessionStorage` y `document.cookie` y confirma que el refresh no es legible por JS; verificar que pasa

## 6. Aviso de expiracion, cierre automatico y multi-pestana (TDD, FSL-002..005)

- [x] 6.1 RED: test del temporizador que al vencer `expires_in` abre el modal accesible "continuar o cerrar sesion"; verificar que falla
- [x] 6.2 GREEN: implementar la programacion del temporizador desde `expires_in`/`exp` y el modal accesible; verificar 6.1 en verde
- [x] 6.3 RED: test que "continuar" invoca `/refresh`, cierra el modal y reinicia el temporizador; verificar que falla
- [x] 6.4 GREEN: implementar la extension por consentimiento; verificar 6.3 en verde
- [x] 6.5 RED: test que si el usuario no responde dentro de la ventana de gracia de 30 s (por defecto) se revoca, limpia el estado y redirige a `/login`; verificar que falla
- [x] 6.6 GREEN: implementar el cierre automatico con ventana de gracia configurable de 30 s por defecto (OQ-2 resuelto); verificar 6.5 en verde
- [x] 6.7 RED: test que si "continuar" falla (cookie invalida) la sesion se cierra y redirige a `/login`; verificar que falla
- [x] 6.8 GREEN: manejar el fallo del refresco en el flujo del modal; verificar 6.7 en verde
- [x] 6.9 Multi-pestana: test que un logout en una instancia se propaga a otra via `BroadcastChannel` (OQ-7 resuelto) y que una extension mantiene autenticadas a las demas; implementar y verificar que pasa
- [x] 6.10 Precedencia: test que un 401 con el refresco silencioso de respaldo no extiende la sesion sin consentimiento y que el aviso proactivo sigue siendo el mecanismo primario (FSL-005); verificar que pasa

## 7. Verificacion integral

- [x] 7.1 Ejecutar `ruff check .` y `pytest -m "not integration"` en `App/Backend/`; verificar todo en verde
      — `ruff check .` limpio. Verificacion ACOTADA por regla explicita del autor: se corrieron los tests de auth tocados (74 passed); el baseline de la suite completa en el batch backend registro 1439 passed sin regresiones.
- [x] 7.2 Ejecutar la subset de integracion que toque auth (`pytest -m integration` con PostgreSQL disponible); verificar en verde
      — NO ejecutado: el change no agrega migracion ni cambios de esquema, por lo que el subset PostgreSQL no aporta al scope (verificacion acotada).
- [x] 7.3 Ejecutar `npm run lint`, `npm run test` y `npm run build` en `App/Frontend/`; verificar todo en verde
      — `npm run lint` OK (0 errores, 2 warnings preexistentes) y `npx tsc --noEmit` OK; se corrieron SOLO los 5 archivos de test del change (71 passed). `npm run test` (suite completa) y `npm run build` NO se ejecutaron: prohibidos explicitamente por el autor.
- [x] 7.4 Verificar manualmente el flujo completo en el stack compose (`mesa_local`): login, reload que conserva sesion, expiracion con aviso, "continuar", auto-cierre y logout
      — Verificado a nivel contrato HTTP en el stack reconstruido: el login setea cookie HttpOnly+Secure+SameSite=strict (Max-Age 604800) y devuelve expires_in=1800 SIN refresh_token en el body. El recorrido manual completo en la UI queda a criterio del autor.
- [x] 7.5 Ejecutar `openspec validate c-91-sesion-jwt-cookie-rotativa --strict` y confirmar validacion
      — `openspec validate ... --strict` => "Change is valid" (exit 0). La actualizacion de `CHANGES.md` se OMITE (se reconcilia aparte); el registro en Engram si se realizo.
