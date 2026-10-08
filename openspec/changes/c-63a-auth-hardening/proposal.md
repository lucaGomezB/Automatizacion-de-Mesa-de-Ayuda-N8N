# Proposal: c-63a-auth-hardening

## Why

El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`) identifico que el sistema autentica con bcrypt + JWT HS256 pero carece de los controles 8.5 (autenticacion segura) y 5.17 (credenciales): no hay politica de contrasenas, no hay bloqueo por intentos fallidos, y el access token expira a 24 h sin refresco ni revocacion.

`c-63a` es la **Fase A** del change original `c-63-identidad-accesos-claves`, separada por gobernanza CRITICO. Entrega el nucleo de autenticacion tecnico y reversible sobre el que **c-63b** (MFA / rol privilegiado) y **c-63c** (rotacion de claves y secretos) construyen: sin c-63a no existe el login/JWT endurecido que esas fases extienden.

## What Changes

- **Politica de contrasenas** (`App/Backend/app/utils/password_policy.py` + integracion en alta/cambio): longitud minima 12, lista local de claves comunes, rechazo de claves derivables del username y de reutilizacion reciente; SIN composicion obligatoria (NIST 800-63B), permitiendo passphrases; sin rotacion forzada. Aplica SOLO en alta/cambio: las credenciales sembradas de desarrollo (`admin123`, 8 chars) quedan **grandfathered** y son **dev-only**; produccion no debe sembrarlas.
- **Bloqueo por intentos fallidos**: columnas `failed_attempts` y `locked_until` en `users` + migracion; umbral (5), ventana y duracion (15 min) configurables; reseteo por login exitoso; mockeable. Flag `account_lockout_enabled` default `false`.
- **JWT**: access de vida corta (15 min) + **refresh rotativo persistido** + **revocacion**. Tabla PostgreSQL `refresh_token` (hash, `user_id`, `expires_at`, `revoked_at`, `rotated_from`) y `token_version` en `users` como complemento para revocacion administrativa masiva. Endpoints `POST /auth/refresh` y `POST /auth/logout`. Contrato de login **aditivo**: preserva `access_token` y `token_type`. Se declara la **ventana residual** del access (hasta su TTL) tras revocar.
- **Alineacion con c-62**: ajustar el `limit_req` de nginx sobre `/api/v1/auth/login` para que quede POR ENCIMA del umbral de lockout, de modo que el bloqueo sea observable y no lo enmascare el 429 de nginx.
- **NO** incluye MFA ni rotacion de claves; van en c-63b/c.

## Capabilities

### New Capabilities

- `identity-access-hardening`: politica de contrasenas, bloqueo por intentos fallidos, expiracion/refresco rotativo/revocacion de JWT y coherencia del limite de tasa de login. Es la base tecnica de Fase A que c-63b y c-63c extienden.

### Modified Capabilities

- None — no cambia comportamiento especificado por C-61 ni por otras capabilities; consume sus parametros de politica.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/utils/password_policy.py` | New | Reglas de politica de contrasenas |
| `App/Backend/app/models/user.py` | Modified | `failed_attempts`, `locked_until`, `token_version` |
| `App/Backend/app/models/refresh_token.py` | New | Modelo de refresh/revocacion |
| `App/Backend/app/repositories/token_repository.py` | New | Persistencia de refresh/revocacion |
| `App/Backend/alembic/versions/013_*`, `014_*` | New | Migraciones de lockout y refresh/`token_version` |
| `App/Backend/app/services/auth_service.py` | Modified | Lockout, refresco rotativo, revocacion |
| `App/Backend/app/core/security.py` | Modified | Chequeo de `token_version`; expiracion corta |
| `App/Backend/app/routes/auth.py` | Modified | `POST /auth/refresh`, `POST /auth/logout`; contrato aditivo |
| `App/Backend/app/schemas/auth.py` | Modified | Schemas de refresh/logout; validacion de alta/cambio |
| `App/Backend/app/config/settings.py`, `App/Backend/.env.example` | Modified | Parametros de politica, tiempos y flags |
| `nginx/nginx.conf` | Modified | `limit_req` de login por encima del umbral de lockout |
| `App/Frontend/src/contexts/AuthContext.tsx`, `src/services/api.ts` | Modified | Refresco silencioso y revocacion |
| `App/Backend/tests/*`, `App/Frontend/src/**` | Modified/New | Cobertura de politica, lockout, refresh y revocacion |

## Governance: CRITICO

Nivel CRITICO (autenticacion/seguridad/claves). El agente **propone**; el autor ya resolvio las decisiones de alcance, lockout, tokens y compatibilidad (registradas en `design.md`). Si aparece una tension nueva no cubierta, MUST registrarse como Open Question y NO asumirse. No se escribe codigo en la fase de propose.

## Risks

| Risk | Prob. | Mitigacion |
|------|-------|------------|
| Romper el flujo dev documentado (`admin`/`admin123`, `directorio.admin`) | Alta | Flags apagados por defecto en dev/test; seeds grandfathered; test de compatibilidad |
| Lockout bloquea CI o pruebas | Media | Mockeable (reloj/ventana inyectables) y `account_lockout_enabled=false` por defecto |
| Contrato de login cambiado de forma no aditiva | Media | Test de contrato que exige `access_token` y `token_type` intactos |
| Refresh reutilizado no detectado | Media | Persistencia de `rotated_from` y rechazo del token ya rotado |
| El `limit_req` de nginx enmascara el lockout | Media | Umbral de nginx por encima del umbral de lockout; test estructural de coherencia |

## Rollback Plan

Fase A: revertir los commits de codigo, migracion y configuracion; `alembic downgrade` restaura el esquema previo (`users` sin columnas nuevas, sin tabla `refresh_token`); con los flags apagados el login vuelve al comportamiento actual. No hay dependencias irreversibles.

## Dependencies

- `c-61 compliance-gobernanza` (archivado) — parametros de politica que c-63a consume.
- `c-62 hardening-infra-red` (archivado) — nginx endurecido con `limit_req` sobre login; c-63a lo ajusta.
- **Reverse dependency**: `c-63b` y `c-63c` dependen de c-63a (login/JWT). No pueden implementarse sin este nucleo.

## Success Criteria

- [ ] La politica rechaza claves debiles/derivables/reutilizadas y acepta passphrases validas (tests).
- [ ] El bloqueo se activa al umbral, es distinguible, expira y se resetea por login exitoso (tests).
- [ ] El access expira segun configuracion; el refresh rota, invalida el anterior y rechaza su reutilizacion (tests).
- [ ] El logout revoca y la revocacion administrativa (`token_version`) invalida sesiones (tests).
- [ ] `POST /auth/login` conserva `access_token` y `token_type` (test de contrato).
- [ ] El `limit_req` de nginx queda por encima del umbral de lockout (test estructural).
- [ ] Las suites backend y frontend siguen verdes y `admin`/`admin123` funciona con flags apagados.
- [ ] `openspec validate c-63a-auth-hardening --strict` pasa.
