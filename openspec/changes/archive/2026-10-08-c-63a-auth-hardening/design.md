# Design: c-63a-auth-hardening

## Context

Ver `proposal.md` para la motivacion. Es la Fase A del change original `c-63-identidad-accesos-claves` (referencia maestra: `openspec/changes/c-63-identidad-accesos-claves/{proposal.md,design.md}`, decisiones D1-D14 y OQ-1..OQ-13).

Estado actual verificado sobre el repositorio:

- **Autenticacion.** bcrypt (`auth_service.verify_password`/`get_password_hash`) + JWT HS256 con `exp` obligatorio (`core/security.py`), `jwt_expire_minutes=1440` (24 h), sin refresco ni revocacion. `POST /api/v1/auth/login` devuelve `{access_token, token_type}` (`schemas/auth.py`). El frontend guarda el token en memoria (`AuthContext.tsx`, `services/api.ts`) y el interceptor de respuesta limpia el token ante 401.
- **No hay alta/cambio de usuario.** El unico punto que fija contrasenas es el seed de la migracion `003_add_users_table.py` (via `get_password_hash`); no existe endpoint de creacion/cambio de contrasenas ni historial de hashes.
- **Modelo `User` minimo** (`models/user.py`): `id`, `username`, `hashed_password`, `is_active`. Sin lockout ni `token_version`.
- **Migraciones:** la ultima es `012_directorio_rol_mesa_ayuda.py`; las nuevas son `013_*` (lockout) y `014_*` (refresh/`token_version`).
- **Tests.** `test_auth.py` fija el contrato: `admin`/`admin123`, `INVALID_CREDENTIALS` en 401, envelope de error uniforme, `exp` obligatorio y `jwt_expire_minutes` como default. Subconjunto SQLite offline (modelos via `Base.metadata`) + `@pytest.mark.integration` PostgreSQL.
- **nginx (c-62).** `limit_req_zone ... zone=login_limit:10m rate=10r/m;` aplicado a `location /api/v1/auth/login` con `burst=5 nodelay;` y `limit_req_status 429`.

## Goals / Non-Goals

**Goals:**

- Cerrar lo tecnico y reversible de Fase A: politica de contrasenas, bloqueo por intentos, expiracion corta/refresco rotativo/revocacion de JWT, y coherencia del limite de tasa de login.
- Preservar de forma aditiva el contrato de login y el flujo dev/CI documentado.
- Dejar el esquema y la configuracion listos para que c-63b y c-63c construyan sin re-trabajo.

**Non-Goals:**

- MFA/TOTP y rol privilegiado (c-63b).
- Rotacion del secreto JWT (keyring/`kid`) y de la clave Fernet, inventario/runbook de secretos (c-63c).
- Alta/cambio de usuario como endpoint nuevo (ver Open Question).
- Cambiar roles, sectores, catalogo ni visibilidad por sector.

## Decisions

Las decisiones de alcance, lockout, tokens y compatibilidad fueron **resueltas por el autor**; se registran aqui como decisiones a implementar, no como opciones abiertas.

### D1 — Alcance y fasing (Fase A reversible)

`c-63a` implementa solo el nucleo de autenticacion (8.5/5.17). `c-63b` (MFA/rol privilegiado) y `c-63c` (rotacion de claves) dependen de este change. Alternativa considerada: mantener el change unico con tasks en tres fases (master D1/OQ-11). Se eligio el **split** por gobernanza CRITICO: revisiones mas pequenas y reversibles.

### D2 — Politica de contrasenas

Validador propio en `app/utils/password_policy.py`, sin dependencias nuevas (descartado `zxcvbn` por no determinismo y el corpus HaveIBeenPwned por requerir red y romper el subconjunto offline; master D2/OQ-3). Parametros: longitud minima 12, lista local de claves comunes, rechazo derivable del username y de reutilizacion reciente (ultimas N hasheadas). Sin composicion obligatoria y sin rotacion forzada (NIST 800-63B); se aceptan passphrases. Rechazo con el envelope estandar. **Aplica solo en alta/cambio**; las credenciales sembradas dev quedan grandfathered y son dev-only (produccion no las siembra).

### D3 — Bloqueo por intentos fallidos

Columnas `failed_attempts` y `locked_until` en `users` (persistente, sin dependencia nueva, visible en tests SQLite; master D3). Ambito **por cuenta, no por IP**. Umbral 5, duracion 15 min y ventana configurables via `settings`. Reset por login exitoso. Flag `account_lockout_enabled` default `false`. Para no depender de tiempos reales, la logica recibe un reloj/funcion de "ahora" inyectable (o `now` por parametro) y es mockeable en la suite. Se agrega un codigo de error distinguible (por ejemplo `ACCOUNT_LOCKED`) sin revelar existencia del usuario. El path de credenciales invalidas por debajo del umbral sigue devolviendo `INVALID_CREDENTIALS` (no rompe `test_auth.py`).

### D4 — Modelo de tokens

Access de vida corta (**15 min** por defecto, configurable) + **refresh opaco rotativo persistido** en PostgreSQL; el access se valida por firma, el refresh en servidor (master D6/D7, OQ-5/OQ-6). Se guarda solo el **hash** del refresh. Modelo `refresh_token` con `hash`, `user_id`, `expires_at`, `revoked_at`, `rotated_from`. `token_version` en `users` como **complemento** para revocacion administrativa masiva. Descartado Redis (aumenta el blast radius y rompe el subconjunto offline). El modelo MUST ser compatible con SQLite para el subconjunto offline.

### D5 — Revocacion y ventana residual

- **Logout:** revoca el refresh del usuario; el access ya emitido sigue valido hasta su TTL (**ventana residual declarada**, no se promete invalidacion inmediata del access).
- **Revocacion administrativa:** incrementa `token_version`; `get_current_user` compara la version embebida en el access contra la de la cuenta y rechaza las anteriores (invalidacion inmediata de todas las sesiones).
- La revocacion MUST ser persistente y observable mediante evento estructurado sin datos sensibles.

### D6 — Contrato aditivo de login

`POST /api/v1/auth/login` conserva `access_token` y `token_type`; agrega `refresh_token` y `expires_in` de forma aditiva. Endpoints nuevos: `POST /api/v1/auth/refresh` y `POST /api/v1/auth/logout`. El child design del master D14 proponia login en dos pasos para MFA; eso queda en c-63b y NO se implementa aqui.

### D7 — Coherencia del limite de tasa con el lockout (c-62)

nginx aplica `limit_req` por IP; el lockout es por cuenta. Para que el lockout sea observable, la capacidad de rafaga de nginx sobre login MUST superar el umbral de bloqueo. Implementacion: subir `burst` de `5` a `10` (>= 2 x umbral) manteniendo `rate=10r/m` y `nodelay`, de modo que un cliente alcance los 5 intentos fallidos antes de recibir 429. Trade-off: una rafaga mayor por IP permite mas intentos rapidos, pero el control primario para ataque dirigido a una cuenta es el lockout por cuenta; nginx queda como freno secundario por IP. Descartado bajar el umbral de lockout por debajo de la capacidad de nginx.

### D8 — Compatibilidad dev/test/CI

Flags apagados por defecto en entornos no productivos: `account_lockout_enabled=false` y politica configurable. En `environment != production` los seeds (`admin`/`admin123`, `directorio.admin`) siguen funcionando intactos. TOTP/MFA no aplica en esta fase. El endpoint de refresh y la revocacion se prueban con tests deterministas. Nota: `settings.environment` default es `"production"`, por lo que un despliegue productivo real MUST habilitar `account_lockout_enabled=true` explicitamente; el default `false` es conservador para no romper el arranque.

## Risks / Trade-offs

- [Romper el flujo dev documentado] -> Flags apagados por defecto + seeds grandfathered + test de compatibilidad (`admin`/`admin123` un solo paso).
- [Lockout bloquea CI] -> Reloj/ventana inyectables y flag apagado por defecto; el subconjunto offline no depende de tiempos reales.
- [Contrato de login no aditivo] -> Test de contrato que exige `access_token` y `token_type`; los campos nuevos son opcionales en la respuesta.
- [La tabla de refresh en PostgreSQL afecta el subconjunto SQLite] -> Modelo SQLAlchemy compatible con SQLite; el subconjunto offline la crea via `Base.metadata`.
- [Ventana residual del access entendida como bug] -> Se declara explicitamente en el spec (IAH-004) y en la documentacion.
- [El `limit_req` de nginx enmascara el lockout] -> `burst` por encima del umbral + test estructural de coherencia.

## Migration Plan

1. **Pre-apply:** resolver la Open Question nueva con el autor (gobernanza CRITICO) y capturar baseline de suites.
2. Migracion `013` (lockout) y `014` (refresh/`token_version`); `upgrade`/`downgrade` verificados.
3. Politica de contrasenas + configuracion y tests (IAH-001).
4. Lockout en `auth_service` + flag + tests (IAH-002).
5. Access corto + refresh rotativo persistido + `POST /auth/refresh` + tests (IAH-003).
6. `POST /auth/logout` + `token_version` en `security.py` + ajuste de nginx + frontend + tests (IAH-004).
7. Verificacion final (suites backend/frontend, higiene de secretos, `openspec validate --strict`).

**Rollback:** revertir commits y `alembic downgrade` (restaura el esquema previo); con los flags apagados el login vuelve al comportamiento actual. Sin migracion de datos irreversible.

## Open Questions — RESUELTAS (autor, 2026-10-08)

- **OQ-1 (enforcement de la politica de contrasenas) = A.** Entregar `password_policy.py` como modulo reutilizable, cablearlo al unico punto de provisionamiento existente (`get_password_hash`/seeds y scripts) y cubrirlo con tests. El endpoint de alta/cambio de usuario y el almacen de historial de contrasenas (necesario para "reutilizacion reciente") se **DIFIEREN a c-63b**. Consecuencia para el grupo 2: se implementa el validador + su cableado al provisionamiento + tests; el "reuso reciente" queda cubierto por el validador pero SIN historial persistido aun (documentar la limitacion en el codigo/design); el endpoint y el historial son follow-up. No cambia IAH-001.
