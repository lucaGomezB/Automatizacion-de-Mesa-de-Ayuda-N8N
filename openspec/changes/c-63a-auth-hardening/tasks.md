# Tasks: c-63a-auth-hardening

> BLOQUEANTE: ninguna tarea de implementacion (grupos 2-5) puede empezar sin cerrar el grupo 1. La Open Question nueva (OQ-1) de `design.md` cambia el punto de enforcement de la politica de contrasenas (grupo 2).
>
> Dependencia: `c-63b` (MFA/rol privilegiado) y `c-63c` (rotacion de claves) dependen de c-63a (login/JWT). No arrancan hasta cerrar este change.

## 1. Pre-apply: baseline y decision

- [x] 1.1 Resolver la Open Question OQ-1 (nueva) con el autor y registrar la opcion elegida en `design.md`. Verificacion: no queda OQ sin respuesta y las tareas del grupo 2 quedan alineadas a la opcion elegida.
- [x] 1.2 Capturar la linea base de pruebas: `cd App/Backend; pytest -m "not integration" -q` y `cd App/Frontend; npm run test`, y registrar el conteo de tests verdes. Verificacion: baseline registrado; si hay fallas preexistentes se reportan sin corregirlas.
- [x] 1.3 Inventariar los puntos de consumo del JWT (`App/Backend/app/core/security.py`, `App/Backend/app/routes/*`, `App/Backend/app/services/auth_service.py`, `App/Frontend/src/services/api.ts`, `App/Frontend/src/contexts/AuthContext.tsx`) y confirmar que el listado cubre todos los usos. Verificacion: listado completo registrado.

## 2. Politica de contrasenas (IAH-001)

- [x] 2.1 RED: escribir los tests de politica (debil rechazada, passphrase aceptada, derivable del username rechazada, reutilizada rechazada, sembradas grandfathered) y verificar que fallan.
- [x] 2.2 GREEN: implementar `App/Backend/app/utils/password_policy.py` con parametros configurables (longitud minima, lista de comunes, historial N) y verificar que los tests de 2.1 pasan.
- [x] 2.3 Cablear el validador al punto de enforcement elegido en OQ-1 y verificar con un test que ese camino aplica la politica y usa el sobre de error estandar.
- [x] 2.4 Triangular con casos borde (longitud exacta = 12, passphrase con espacios, clave comun, borde de la ventana de reutilizacion) y verificar que cubre todos los escenarios de IAH-001.
- [x] 2.5 Exponer los parametros en `App/Backend/app/config/settings.py` y `App/Backend/.env.example`, y verificar que los defaults no invalidan las credenciales sembradas de desarrollo.

## 3. Bloqueo por intentos fallidos (IAH-002)

- [x] 3.1 Agregar la migracion `013` con las columnas `failed_attempts` y `locked_until` en `users` y verificar `alembic upgrade head` y `alembic downgrade` sin error.
- [x] 3.2 RED: escribir los tests de lockout (umbral alcanzado, cuenta bloqueada rechaza credenciales validas, codigo distinguible, reset por exito, expiracion, flag apagado) y verificar que fallan.
- [x] 3.3 GREEN: implementar el lockout en `App/Backend/app/services/auth_service.py` con `account_lockout_enabled`, el codigo `ACCOUNT_LOCKED` y la configuracion (umbral/ventana/duracion), y verificar que los tests de 3.2 pasan.
- [x] 3.4 Triangular inyectando reloj/ventana y configuracion y verificar que el bloqueo es mockeable y no depende de tiempos reales en la suite.
- [x] 3.5 Verificar que el path por debajo del umbral conserva `INVALID_CREDENTIALS` y que `App/Backend/tests/test_auth.py` sigue verde.

## 4. Expiracion y refresco rotativo de tokens (IAH-003)

- [x] 4.1 Agregar la migracion `014` con la tabla `refresh_token` (hash, `user_id`, `expires_at`, `revoked_at`, `rotated_from`) y `token_version` en `users`, y verificar upgrade/downgrade.
- [x] 4.2 Implementar `App/Backend/app/models/refresh_token.py` y `App/Backend/app/repositories/token_repository.py` y verificar que el subconjunto SQLite offline crea la tabla via `Base.metadata`.
- [x] 4.3 RED: escribir los tests de tokens (access expira, login conserva `access_token` y `token_type`, refresco rota, reuso rechazado, refresh persistido hasheado) y verificar que fallan.
- [x] 4.4 GREEN: implementar el access corto (15 min) + emision de refresh + `POST /api/v1/auth/refresh` con rotacion e invalidacion del anterior; verificar que los tests de 4.3 pasan.
- [x] 4.5 Escribir el test explicito de contrato aditivo del login y verificar que el frontend sigue autenticando (tests/lint de frontend).

## 5. Revocacion y coherencia del limite de tasa (IAH-004)

- [x] 5.1 RED: escribir los tests de revocacion (logout revoca el refresh, refresh revocado devuelve 401, `token_version` invalida los access previos) y verificar que fallan.
- [x] 5.2 GREEN: implementar `POST /api/v1/auth/logout`, el chequeo de `token_version` en `App/Backend/app/core/security.py` y el evento estructurado sin datos sensibles; verificar que los tests de 5.1 pasan.
- [x] 5.3 Ajustar `nginx/nginx.conf` para que la capacidad del `limit_req` de login quede por encima del umbral de lockout y verificar con un test estructural que lee la configuracion.
- [x] 5.4 Adaptar el frontend (`App/Frontend/src/contexts/AuthContext.tsx`, `App/Frontend/src/services/api.ts`) al refresco silencioso y al logout revocatorio, y verificar con los tests de frontend.
- [x] 5.5 Triangular la ventana residual: test que confirma que el access sigue valido hasta su TTL tras el logout y que `token_version` lo invalida de inmediato.

## 6. Verificacion final

- [x] 6.1 Verificar de forma explicita la seguridad: lockout (umbral/reseteo/expulsion), refresh (rotacion/reuso/revocacion) y contrato aditivo, mediante sus tests dedicados.
- [x] 6.2 Ejecutar la suite backend completa (`cd App/Backend; pytest`) incluyendo el subconjunto `integration` y verificar que pasa.
- [x] 6.3 Ejecutar la suite frontend (`cd App/Frontend; npm run test`) y verificar que pasa.
- [x] 6.4 Verificar la higiene de secretos (`.githooks/pre-commit` y `python3 scripts/security/scan_engram_secrets.py .engram`) sin hallazgos sin resolver.
- [x] 6.5 Verificar que el flujo de desarrollo documentado sigue operativo con los flags apagados (`admin`/`admin123`, `directorio.admin`, dry-run).
- [x] 6.6 Ejecutar `openspec validate c-63a-auth-hardening --strict` y verificar que pasa.
- [x] 6.7 Confirmar que la dependencia de `c-63b`/`c-63c` con c-63a (login/JWT) queda documentada sin modificar `CHANGES.md` ni otros changes.
