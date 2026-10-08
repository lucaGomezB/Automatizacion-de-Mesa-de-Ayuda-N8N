# Design: c-63b — MFA y rol privilegiado (Fase B)

## Context

Ver `proposal.md — Why` y el design maestro `../c-63-identidad-accesos-claves/design.md` (D1-D14, base de este split). Restricciones verificadas que moldean el enfoque:

- **`User` no distingue privilegio.** `User` (`App/Backend/app/models/user.py`) solo tiene `id`, `username`, `hashed_password`, `is_active`. El rol vive en `Empleado` (`App/Backend/app/models/empleado.py`, `RolEmpleado`) via `directorio_empleado.user_id` (FK nullable, ON DELETE SET NULL). El `admin` sembrado (migracion `003_add_users_table.py`) no tiene `Empleado`.
- **Flujo de login actual.** `POST /api/v1/auth/login` (`routes/auth.py`) valida con `authenticate_user` (`services/auth_service.py`) y emite `{access_token, token_type}`. El token se firma/valida con HS256 en `core/security.py`.
- **Cifrado at-rest ya disponible.** `utils/encryption.py` expone `_get_fernet()` y el `TypeDecorator EncryptedText` (Fernet, cache invalidado si cambia la clave).
- **Frontend.** `AuthContext.tsx` guarda el token en memoria y `login()` asume una unica respuesta con `access_token`.
- **Compatibilidad.** `admin`/`admin123` y `directorio.admin` son usados por runbooks, dry-run y tests. No pueden romperse en dev/test.
- **Governance CRITICO.** El agente propone; el autor ya resolvio mecanismo (TOTP), roles (incluye `admin` via el flag), default de bandera y compatibilidad. Las tensiones nuevas se registran como Open Questions.

## Goals / Non-Goals

**Goals:**

- Exponer el privilegio a nivel identidad y usarlo como fuente unica para exigir MFA.
- Implementar el segundo factor TOTP (enrollment, verificacion, codigos de recuperacion, secreto cifrado at-rest).
- Mantener el login en dos pasos de forma aditiva, preservando el contrato actual y el flujo dev con la bandera apagada.

**Non-Goals:**

- WebAuthn/passkeys, OTP por correo/SMS (mejora futura documentada).
- Politica de contrasenas, bloqueo por intentos, expiracion/refresco/revocacion (Fase A, `c-63a`).
- Rotacion de claves/secretos (Fase C, `c-63c`).
- Reset administrativo de MFA (ver OQ-B2).

## Decisions

### D-B1 — Flag privilegiado a nivel identidad

**Recomendado: columna `User.is_privileged` (bool, default `false`, `nullable=False`) + migracion alembic.**

- La migracion agrega la columna y `UPDATE users SET is_privileged = true WHERE username = 'admin'` para que el seed existente quede privilegiado.
- Alternativa considerada: derivar el privilegio solo desde `Empleado` en cada chequeo (sin columna). Descartada como unica fuente porque `admin` no tiene `Empleado` y obligaria a un caso especial disperso; la columna da una fuente unica y consultable.

### D-B2 — Materializacion del privilegio (ver OQ-B1)

**Recomendado: flag persistido, sincronizado al crear/actualizar el vinculo, con derivacion defensiva en el chequeo.**

- Al crear/actualizar un `Empleado` con `user_id` y rol privilegiado → `is_privileged = true`; rol `usuario_final` → no privilegiado (salvo seed `admin`).
- El chequeo de autenticacion combina el flag persistido con una derivacion defensiva (si el flag esta apagado pero existe vinculo privilegiado, se considera privilegiado). Evita depender de que la sincronizacion haya corrido.
- La eleccion exacta (persistido vs. derivado puro vs. mixto) es OQ-B1; no se asume. Las tareas de materializacion esperan su resolucion.

### D-B3 — Libreria TOTP

**Recomendado: `pyotp` (RFC 6238), pure-Python, offline y testeable.**

- Permite calcular el codigo en tests sin reloj real (inyectando tiempo).
- Alternativa considerada: implementacion propia de HMAC-SHA1/TOTP(n). Evita una dependencia pero agrega criptografia a mano; `pyotp` es mas defendible.
- La eleccion de libreria no cambia el comportamiento observable del spec.

### D-B4 — Cifrado del secreto TOTP

**Recomendado: reutilizar `utils/encryption.py` (Fernet).** El secreto se persiste cifrado at-rest. Se prefiere `EncryptedText` para la columna (transparente para el ORM); si el esquema exige callar el valor en memoria, usar `_get_fernet()` directamente en el servicio. El cifrado enlaza con la rotacion Fernet de la Fase C (`c-63c`).

### D-B5 — Codigos de recuperacion

**Recomendado: N=10 codigos de un solo uso, generados en el enrollment, mostrados una sola vez, almacenados como hashes bcrypt.**

- Consumo: se compara contra los hashes con `bcrypt.checkpw` y se elimina el hash usado.
- Alternativa considerada: hash en tabla aparte (`mfa_recovery_code`) vs. columna JSON de hashes. Se recomienda **columna de texto (JSON/array de hashes)** por simplicidad y suficiente para el alcance; una tabla aparte no aporta trazabilidad exigida por el spec.

### D-B6 — Ticket de segundo factor

**Recomendado: JWT corto dedicado, con `scope` distinto del access token y `aud`/`sub` = usuario, TTL ~5 min, firmado con la misma clave (`kid` de la Fase A).**

- El ticket NO es un access token: `get_current_user` MUST NOT aceptarlo en rutas protegidas (se valida `scope`).
- Alternativa considerada: token opaco persistido en servidor. Mas control de revocacion pero agrega almacen; el ticket corto y de un solo proposito acota la ventana.

### D-B7 — Contrato aditivo del login

**Recomendado: `POST /auth/login` devuelve `mfa_required: true` + `mfa_ticket` para cuenta privilegiada con MFA activo y bandera encendida; en todos los demas casos sigue devolviendo `access_token` y `token_type`.**

- `POST /auth/mfa/verify` recibe `{mfa_ticket, code}` (o `recovery_code`) y devuelve la respuesta de token actual.
- `POST /auth/mfa/enroll` inicia/confirma el enrollment (devuelve `otpauth_uri`, `secret`, `recovery_codes`).
- Los campos actuales (`access_token`, `token_type`) se preservan. La respuesta de login pasa a un modelo de union/discriminado o campos opcionales aditivos.

### D-B8 — Configuracion

**Recomendado (todos con default seguro para dev/test):** `mfa_required_for_privileged=False`, `mfa_ticket_expire_minutes=5`, `mfa_issuer` (nombre de la app), `mfa_recovery_code_count=10`. En produccion, `mfa_required_for_privileged` MUST habilitarse (se documenta como requisito de despliegue).

### D-B9 — Frontend

**Recomendado: extender `AuthContext.login()` para manejar la respuesta intermedia y exponer un estado `mfaRequired` + `verifyMfa(code)`; la pantalla de login muestra el paso de verificacion y, en el primer acceso, el enrollment.** El token se fija en memoria recien al completar el segundo factor.

### D-B10 — Compatibilidad dev/test/CI

**Recomendado: bandera apagada por defecto; en la suite, MFA mockeable y TOTP verificado con codigos calculados.** `admin`/`admin123` inicia en un solo paso. Verificacion explicita de ambos subconjuntos backend y de la suite frontend (IAH-007).

## Risks / Trade-offs

- **[Doble fuente de verdad (`is_privileged` vs `Empleado`)] →** sincronizacion al vincular + derivacion defensiva; resolver OQ-B1 antes de apply.
- **[Ticket de segundo factor reutilizable en la ventana] →** TTL corto y `scope` dedicado; el ticket se consume al verificar (si se persiste) o caduca por `exp`.
- **[Secreto TOTP en claro en logs/memoria] →** cifrado at-rest y no registrar el secreto.
- **[MFA bloquea CI/pruebas] →** bandera apagada por defecto y TOTP sin reloj real.
- **[Romper el flujo dev] →** `admin`/`admin123` y `directorio.admin` intactos con la bandera apagada (IAH-007).

## Migration Plan

1. **Pre-apply:** el autor resuelve OQ-B1 y OQ-B2; se registran en este documento.
2. Migracion: `is_privileged` + campos MFA (`totp_secret`, `totp_enabled`, codigos de recuperacion) y marca de `admin` privilegiado; verificar `alembic upgrade head` y `downgrade`.
3. `mfa_service.py` (enrollment/verificacion/recuperacion) + configuracion + flag.
4. Login en dos pasos y endpoints `/auth/mfa/enroll`, `/auth/mfa/verify` + schemas.
5. Frontend: reto MFA y enrollment.
6. Verificacion: suites backend/frontend verdes, compatibilidad dev con bandera apagada, `openspec validate --strict`.
7. **Rollback:** bajar la migracion y apagar la bandera restaura el flujo actual; no hay dependencias irreversibles.

## Open Questions — RESUELTAS (autor, 2026-10-08)

- **OQ-B1 (materializacion del privilegio) = persistir + sincronizar + derivacion defensiva.** Se persiste `User.is_privileged` y se sincroniza al crear/actualizar/desvincular el `Empleado`; el chequeo de MFA ademas deriva de forma defensiva (`is_privileged OR Empleado.rol privilegiado`). Al desvincular (`user_id = NULL`) o al degradar el rol a `usuario_final`, el flag se pone en falso.
- **OQ-B2 (recuperacion/reset de MFA) = documentar.** El reset administrativo de MFA / re-enrollment forzado se documenta como procedimiento (fuera del codigo de esta fase); no se implementa endpoint de reset en este change.
