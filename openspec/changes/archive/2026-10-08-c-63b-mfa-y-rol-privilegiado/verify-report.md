# Verification Report — c-63b-mfa-y-rol-privilegiado

**Change**: c-63b-mfa-y-rol-privilegiado (Fase B del workstream de identidad)
**Spec version**: identity-access-hardening (delta c-63b)
**Governance**: CRITICO (autenticacion)
**Mode**: Standard verify + evidencia TDD (RED/GREEN/TRIANGULATE) de los tasks
**Date**: 2026-10-08
**Verifier**: sdd-verify (ejecucion independiente, no se confio en resumenes)

---

## 1. Alcance verificado

Ejecucion independiente sobre el working tree (`main`, HEAD `066a6cc`), sin
confiar en el estado declarado. Evidencia recolectada por lectura de codigo +
ejecucion real de suites + migracion real sobre PostgreSQL.

Artefactos leidos: `proposal.md`, `design.md`, `tasks.md`,
`specs/identity-access-hardening/spec.md` y los archivos de codigo/test declarados.

**Inventario de cambios del change (confirmado por `git diff --stat` y `git status`):**

| Area | Archivo | Estado |
|------|---------|--------|
| Modelo | `App/Backend/app/models/user.py` | M |
| Servicio | `App/Backend/app/services/mfa_service.py` | N |
| Servicio | `App/Backend/app/services/privilege_service.py` | N |
| Servicio | `App/Backend/app/services/auth_service.py` | M |
| Servicio | `App/Backend/app/services/directorio_service.py` | M |
| Core | `App/Backend/app/core/security.py` | M |
| Rutas | `App/Backend/app/routes/auth.py` | M |
| Schemas | `App/Backend/app/schemas/auth.py` | M |
| Config | `App/Backend/app/config/settings.py`, `.env.example` | M |
| Migracion | `App/Backend/alembic/versions/016_mfa_privilege.py` | N |
| Tests | `tests/test_c63b_privilege.py`, `test_c63b_mfa.py`, `test_c63b_login_two_step.py`, `test_migration_016_mfa_privilege.py` | N |
| Deps | `App/Backend/requirements.txt` (`pyotp==2.9.0`) | M |
| Frontend | `src/contexts/AuthContext.tsx`, `src/pages/LoginPage/index.tsx`, `src/main.tsx`, `src/pages/MfaEnrollmentPage/**`, tests | M/N |
| Docs | `docs/seguridad/procedimiento-reset-mfa.md`, `docs/seguridad/README.md`, `docs/openapi.json` | N/M |

Fuera de alcance NO tocados y confirmado por `git status`: `n8n/workflow.json`,
`docker-compose.yml`, `CHANGES.md` (los tres sin cambios).

---

## 2. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 26 |
| Tasks complete `[x]` | 26 |
| Tasks incomplete `[ ]` | 0 |

`tasks.md` (secciones 0 a 5) esta 100% marcado. El `git diff` de `tasks.md`
confirma que las unicas modificaciones son el cambio de `[ ]` a `[x]` (sin
reescritura de contenido, salvo el reflow de lineas por el checkbox).

---

## 3. Build & Tests Execution (evidencia real)

### Backend — subconjunto SQLite (offline)
```
cd App/Backend; pytest -m "not integration" -q
1203 passed, 42 deselected, 1 xfailed, 331 warnings in 262.26s
```
Exit code 0. El conteo esperado (~1181) se supera porque la corrida incluye
ademas los tests de c-63c presentes en el mismo tree (ver Issues, W1).

### Backend — subconjunto PostgreSQL integration
```
docker compose -p mesa_local up -d postgres   # healthy en :5433
cd App/Backend; pytest -m integration -q
42 passed, 1204 deselected, 6 warnings in 29.00s
docker compose -p mesa_local stop postgres
```
Exit code 0. La suite provisiona la base descartable `mesa_de_ayuda_test`
(guard de nombre de base activo).

### Migracion 016 sobre PostgreSQL (manual, base descartable propia)
```
alembic upgrade head   -> 015 -> 016 "privilegio de identidad y MFA TOTP" OK
columnas en users: is_privileged, mfa_recovery_codes, totp_enabled, totp_secret
SELECT username,is_privileged,totp_enabled FROM users WHERE username='admin'
  -> admin|t|f        (admin marcado privilegiado)
usuario 'otro'        -> f   (no privilegiado)
alembic downgrade 015 -> columnas eliminadas
alembic upgrade head  -> re-aplicada OK
```
Base temporal `c63b_mig_check` eliminada al finalizar.

### Migracion 016 sobre SQLite (suite dedicada)
36 tests dedicados (migracion + privilegio + MFA + two-step) `PASSED`.

### Lint backend
```
cd App/Backend; ruff check .   -> All checks passed! (exit 0)
```

### Frontend
```
cd App/Frontend; npm run lint  -> 0 errors, 2 warnings (shadcn ui preexistentes)
cd App/Frontend; npm run test  -> Test Files 29 passed, Tests 133 passed (exit 0)
```

### OpenSpec
```
openspec validate c-63b-mfa-y-rol-privilegiado --strict  -> "is valid" (exit 0)
```
`docs/openapi.json` incluye `/api/v1/auth/mfa/enroll` y `/api/v1/auth/mfa/verify`
y el schema `LoginResponse` aditivo; `test_openapi_sync.py` paso en la suite.

---

## 4. TDD Cycle Evidence

| Task | Test file | Layer | RED/GREEN/TRIANGULATE |
|------|-----------|-------|----------------------|
| 1.2/1.3/1.4 | `tests/test_c63b_privilege.py` | Unit (async) | 11 tests; degradacion, desvinculacion, relink y derivacion defensiva |
| 2.2/2.3/2.4 | `tests/test_c63b_mfa.py` | Unit (async) | 10 tests; borde de ventana, reuso de recuperacion, URI |
| 3.1/3.2/3.3/3.4 | `tests/test_c63b_login_two_step.py` | API (ASGI) | 11 tests; scope `mfa`, ticket expirado, contrato aditivo |
| 1.1/2.1 | `tests/test_migration_016_mfa_privilege.py` | Migracion (SQLite file) | 5 tests; chain, upgrade, admin, downgrade reversible |
| 4.1/4.2/4.3 | `AuthContext.test.tsx`, `LoginPage.test.tsx`, `MfaEnrollmentPage.test.tsx` | Frontend (vitest) | 5+2+2 tests; reto, verify, enrollment, error |

Los tasks documentan explicitamente el ciclo RED -> GREEN -> TRIANGULATE y la
evidencia de ejecucion lo confirma. No se pudo reconstruir el orden temporal
RED-first desde el estado final, por lo que la evidencia es de cobertura, no de
secuencia.

---

## 5. Spec Compliance Matrix (IAH-005..IAH-007, validacion conductual)

| Requirement | Scenario | Test (resultado real) | Result |
|-------------|----------|-----------------------|--------|
| IAH-005 Rol privilegiado | El admin sembrado es privilegiado | `test_migration_016_mfa_privilege.py::test_upgrade_marks_admin_privileged` + verificacion manual PostgreSQL (`admin|t`) | COMPLIANT |
| IAH-005 | Cuenta vinculada a empleado privilegiado es privilegiada | `test_c63b_privilege.py::test_linking_privileged_role_marks_user_privileged` | COMPLIANT |
| IAH-005 | Cuenta de usuario final no es privilegiada | `test_c63b_privilege.py::test_linking_usuario_final_does_not_mark_privileged` | COMPLIANT |
| IAH-005 | Cuenta nueva sin vinculo tiene el valor por defecto | `test_c63b_privilege.py::test_new_user_defaults_to_not_privileged` | COMPLIANT |
| IAH-006 MFA TOTP | Enrollment entrega el URI otpauth y el secreto | `test_c63b_mfa.py::test_enrollment_returns_otpauth_uri_and_secret` (+ `test_enrollment_confirms_with_otpauth_secret`) | COMPLIANT |
| IAH-006 | Codigo TOTP valido verifica | `test_c63b_mfa.py::test_valid_totp_verifies` | COMPLIANT |
| IAH-006 | Codigo TOTP invalido o expirado es rechazado | `test_c63b_mfa.py::test_invalid_totp_is_rejected`, `test_expired_totp_is_rejected` | COMPLIANT |
| IAH-006 | Codigo de recuperacion de un solo uso | `test_c63b_mfa.py::test_recovery_code_is_single_use` | COMPLIANT |
| IAH-006 | El secreto TOTP no se almacena en claro | `test_c63b_mfa.py::test_totp_secret_is_encrypted_at_rest` | COMPLIANT |
| IAH-006 | Bandera apagada no exige MFA | `test_c63b_login_two_step.py::test_flag_off_keeps_dev_admin_single_step` | COMPLIANT |
| IAH-007 Login dos pasos | Cuenta privilegiada recibe el reto sin token | `test_c63b_login_two_step.py::test_challenge_and_verify_flow` | COMPLIANT |
| IAH-007 | Verificacion correcta emite el token con los campos actuales | `test_c63b_login_two_step.py::test_challenge_and_verify_flow`, `test_recovery_code_completes_login` | COMPLIANT |
| IAH-007 | Ticket invalido o expirado es rechazado | `test_c63b_login_two_step.py::test_invalid_ticket_is_rejected`, `test_expired_ticket_is_rejected` | COMPLIANT |
| IAH-007 | Cuenta no privilegiada usa el flujo de un paso | `test_c63b_login_two_step.py::test_non_privileged_uses_single_step` | COMPLIANT |
| IAH-007 | Flag apagado mantiene el flujo dev de un paso | `test_c63b_login_two_step.py::test_flag_off_keeps_dev_admin_single_step` | COMPLIANT |
| IAH-007 | El frontend presenta el reto MFA | `LoginPage.test.tsx::con mfaRequired muestra el paso de verificacion y completa el login`, `AuthContext.test.tsx::verifyMfa con codigo valido completa el login` | COMPLIANT |

**Compliance summary**: 16/16 escenarios COMPLIANT.

---

## 6. Verificacion adversarial (probar, no confiar)

### Privilegio (IAH-005)
- `admin` privilegiado: PROBADO por migracion 016 (`UPDATE ... WHERE username='admin'`)
  y por consulta real sobre PostgreSQL (`admin|t`) y SQLite.
- Cuenta vinculada a `Empleado` privilegiado queda privilegiada: PROBADO
  (`test_linking_privileged_role_marks_user_privileged`).
- `usuario_final` NO privilegiado: PROBADO (`test_linking_usuario_final_...`).
- Cuenta nueva default `false`: PROBADO (`server_default=false()` + test).
- Desvinculacion (`user_id=NULL`) apaga el flag: PROBADO (`test_unlink_clears_flag`).
- Degradacion a `usuario_final` apaga el flag: PROBADO
  (`test_degrade_role_to_usuario_final_clears_flag`).
- Derivacion defensiva con flag y vinculo en desacuerdo: PROBADO
  (`test_defensive_derivation_uses_linked_empleado`: flag false + vinculo
  privilegiado -> `user_is_privileged == True`). `user_is_privileged` combina
  `user.is_privileged OR empleado.rol privilegiado`.
- El seed `admin` NUNCA se degrada por la sincronizacion
  (`sync_user_privilege` hace early-return para `username == "admin"`).

### MFA (IAH-006)
- URI `otpauth://`: PROBADO (`startswith("otpauth://totp/")` + `pyotp.parse_uri`).
- TOTP valido verifica: PROBADO con codigo calculado (`pyotp.TOTP(secret).now()`),
  sin reloj real.
- TOTP invalido/expirado rechazado: PROBADO (`000000`; y codigo de hace 10 min).
- Borde de ventana: PROBADO (codigo del periodo anterior aceptado con
  `valid_window=1`).
- Codigos de recuperacion bcrypt, single-use y normalizados: PROBADO hasheados
  (`$2` prefix, `test_recovery_codes_are_hashed`) y single-use
  (`test_recovery_code_is_single_use`). La forma almacenada se normaliza
  (sin guiones, mayusculas) y la verificacion normaliza la entrada.
- Secreto TOTP NO en claro: PROBADO leyendo la columna cruda por SQL
  (`SELECT totp_secret`), distinta del secreto devuelto y sin contenerlo. La
  columna usa `EncryptedText` (Fernet/MultiFernet).
- Cuenta privilegiada SIN MFA (`totp_enabled=False`) entra en un paso:
  PROBADO por la condicion de `login` (`... and user.totp_enabled and ...`) y
  el codigo nunca desafia si no hay MFA; no hay test dedicado con flag ON (ver
  S2).
- `mfa_required_for_privileged=false` mantiene el dev funcionando: PROBADO
  (`test_flag_off_keeps_dev_admin_single_step`, `admin`/`admin123` -> un paso y
  token usable en `/api/v1/incidentes/`).

### Login en dos pasos (IAH-007)
- Privilegiada + MFA + flag ON recibe reto SIN access token: PROBADO
  (`mfa_required is True`, `mfa_ticket` presente, `access_token` ausente; además
  `response_model_exclude_none=True` omite los nulos).
- `/auth/mfa/verify` emite `access_token`/`token_type` (+`refresh_token`/
  `expires_in`): PROBADO.
- Ticket de scope `mfa` rechazado por `get_current_user`: PROBADO
  (`test_mfa_ticket_is_rejected_on_protected_route`, 401 en
  `/api/v1/incidentes/`). `security.get_current_user` rechaza explicitamente
  `payload.get("scope") == "mfa"`.
- Ticket invalido/expirado rechazado: PROBADO (token malformado y token con
  `exp` pasado).
- Contrato aditivo del login preservado: PROBADO (flujo de un paso sigue
  devolviendo `access_token`/`token_type`; `LoginResponse` es aditivo).

### Flujo dev
- `admin`/`admin123` con bandera apagada: PROBADO.
- `directorio.admin` y dry-run: la suite completa (1203+42) pasa, incluyendo los
  tests de directorio y los scripts de dry-run; la bandera apagada por defecto no
  altera el login de un paso. Sin regresiones detectadas.
- `docs/openapi.json` en sync: PROBADO (`test_openapi_sync.py` verde).

### Alcance (ver Section 9 / Issues W1)

---

## 7. Correctness (evidencia estructural)

| Requirement | Status | Notes |
|------------|--------|-------|
| IAH-005 flag de identidad | Implemented | `User.is_privileged` (bool, `nullable=False`, `server_default=false()`); migracion 016; sincronizacion en `directorio_service` + derivacion defensiva en `privilege_service` |
| IAH-006 TOTP | Implemented | `mfa_service.py` con `pyotp`, bcrypt para recuperacion, `EncryptedText` para el secreto; endpoints enroll/verify |
| IAH-007 login dos pasos | Implemented | Ticket JWT de scope `mfa` (`create_mfa_ticket`/`decode_mfa_ticket`); branch en `/auth/login`; `/auth/mfa/verify`; `LoginResponse` aditivo |
| Frontend | Implemented | `AuthContext` con `mfaRequired`/`verifyMfa`/`enrollMfa`; `LoginPage` con paso de verificacion; `MfaEnrollmentPage` |

---

## 8. Coherence (design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D-B1 columna `is_privileged` + migracion | Yes | Columna y migracion 016 exactas |
| D-B2 persistir + sincronizar + derivacion defensiva (OQ-B1) | Yes | `sync_user_privilege` + `user_is_privileged`; degradacion/desvinculacion apagan el flag |
| D-B3 `pyotp` | Yes | Dependencia anclada, sin reloj real en tests |
| D-B4 cifrado Fernet del secreto | Yes | `EncryptedText` sobre `totp_secret` |
| D-B5 N=10 codigos de recuperacion bcrypt | Yes | `mfa_recovery_code_count=10`, hashes bcrypt en columna texto JSON |
| D-B6 ticket JWT dedicado scope `mfa` | Yes | `MFA_TICKET_SCOPE="mfa"`; `get_current_user` lo rechaza |
| D-B7 contrato aditivo del login | Yes | `LoginResponse` aditivo; verify devuelve el contrato de token |
| D-B8 configuracion con defaults dev-safe | Yes | Flag `False`; TTL 5; issuer; count 10 |
| D-B9 frontend | Yes | Reto + enrollment en `AuthContext`/`LoginPage` |
| D-B10 compatibilidad dev/test/CI | Yes | Suites verdes con flag apagado |
| Proposal "Sin dependencia de c-63c" | NO | Ver Issues W1: el codigo de c-63b importa `app.core.jwt_keyring` (c-63c) |

---

## 9. Issues Found

### CRITICAL (deben corregirse antes de archivar)
Ninguno. `CRITICAL count = 0`.

### WARNING (deberian corregirse)

**W1 — c-63b depende de c-63c y comparte el working tree (contradice el
"Sin dependencia de c-63c" del proposal y el alcance esperado).**
Evidencia:
- `git status` muestra artefactos de c-63c NO declarados en el alcance de c-63b:
  `app/core/jwt_keyring.py` (N), `scripts/rotate_fernet_key.py` (N),
  `tests/test_c63c_jwt_rotation.py` (N), `tests/test_c63c_fernet_rotation.py` (N),
  `app/utils/encryption.py` (M), `openspec/changes/c-63c-.../tasks.md` (M), y
  `settings.py`/`.env.example` con los campos de c-63c (`jwt_key_id`,
  `jwt_previous_*`, `pseudonymization_encryption_key_previous`).
- `app/services/auth_service.py` de c-63b importa `from app.core import
  jwt_keyring` y `create_mfa_ticket` pasa `key_id=settings.jwt_key_id`; ambos
  son c-63c (el commit de c-63a, `32ab0ba`, no los contenia: verificado con
  `git show`).
- `proposal.md` afirma explicitamente "Sin dependencia de c-63c".
Impacto: c-63b NO es revertible/archivable de forma independiente; si c-63c se
revierte, c-63b rompe al importar `jwt_keyring`. Funcionalmente el estado
conjunto pasa todas las suites. Recomendacion: archivar c-63c antes (o junto) de
c-63b y corregir la declaracion de dependencias del proposal.

### SUGGESTION (deseables)

**S1 — Registro de la dependencia de supply-chain `pyotp==2.9.0`.**
Anclada exactamente en `requirements.txt` con comentario de auditoria. Es
pure-Python, sin red. Se registra como nota de cadena de suministro: conviene
verificar el paquete resuelve al owner oficial (`pyauth/pyotp`) y no a un
paquete lookalike antes de release. No bloquea.

**S2 — Falta test dedicado de "privilegiada sin MFA activo + flag ON".**
El comportamiento es correcto por la condicion `... and user.totp_enabled and
...`, pero no hay test explicito que lo fije (los tests de reto siempre hacen
enrollment antes). Agregar un caso evita una regresion futura.

**S3 — Normalizacion de codigo de recuperacion no cubierta por test.**
El codigo hashea/verifica la forma normalizada (sin guiones, mayusculas), pero
no hay test que presente el codigo en minusculas o sin guiones. La logica es
correcta; conviene un caso.

**S4 — Reutilizacion del ticket MFA / replay del TOTP dentro de la ventana.**
Sin persistencia del ticket, el mismo `mfa_ticket` es aceptado durante sus ~5
minutos (el test de recuperacion lo reutiliza y falla por el codigo consumido,
no por el ticket). El design D-B6 acepta esto como tradeoff (TTL corto + scope
dedicado). El replay de un TOTP valido dentro de la ventana tampoco se previene
(comportamiento estandar RFC 6238). Documentado como tradeoff; no rompe spec.

**S5 — `token_type: "bearer"` (default) viaja en la respuesta del reto sin
`access_token`.** No es una violacion (el spec exige no emitir el token), pero
es semanticamente enganoso. Evaluar quitarlo o excluirlo del reto.

**S6 — `POST /auth/mfa/enroll` no restringe a cuentas privilegiadas.** Cualquier
usuario autenticado puede enrolar TOTP. Inocuo (el flag exige privilegio en el
login), pero el spec lo enmarca como "para cuentas privilegiadas". Considerar
restringir o documentar.

**S7 — `proposal.md` lista `src/services/api.ts` como Modified; no fue
modificado.** Desviacion menor de documentacion (el frontend usa el `apiClient`
existente). Ajustar el impacto del proposal.

---

## 10. Verdict

**PASS WITH WARNINGS**

Implementacion completa (26/26 tasks), 16/16 escenarios del spec COMPLIANT con
test en verde, suites backend (SQLite 1203 + integration 42) y frontend (133)
verdes, ruff y `openspec validate --strict` en verde, y migracion 016 verificada
en PostgreSQL (upgrade marca `admin` privilegiado, downgrade reversible).
Unicamente W1 (acoplamiento no declarado con c-63c) y sugerencias; 0 CRITICAL.

---

## 11. Post-verify fixes (W1 + suggestions)

**Date**: 2026-10-08 (post-verify). Governance CRITICO. Strict TDD (tests primero, luego GREEN).

### W1 — Desacople de c-63c (RESUELTO)

`App/Backend/app/services/auth_service.py` ya NO usa el keyring de c-63c para el
ticket MFA:

- `create_mfa_ticket` firma con `settings.jwt_secret_key` (HS256) y NO pasa
  `key_id=settings.jwt_key_id` (se elimino el `kid` del header).
- `decode_mfa_ticket` verifica directamente con `jwt.decode(token,
  settings.jwt_secret_key, ...)`, sin `jwt_keyring.decode_token`.
- Se elimino el import `from app.core import jwt_keyring` del modulo.
- `create_access_token` conserva su parametro `key_id` y su uso de keyring del
  access token (alcance de c-63c, NO tocado).

Evidencia de desacople (`grep -n "jwt_keyring\|jwt_key_id"
app/services/auth_service.py`):

```
110:    produccion pasan `settings.jwt_key_id`; sin `key_id` el token no lleva el
```

La unica coincidencia es documentacion del ACCESS TOKEN (`create_access_token`);
NO hay uso de keyring ni `jwt_key_id` en el ticket MFA.

Documentacion del tradeoff de rotacion: docstrings de `create_mfa_ticket` /
`decode_mfa_ticket`. Durante una rotacion de claves JWT, un ticket MFA en vuelo
emitido antes del cambio PUEDE fallar la verificacion; se acepta por su TTL corto
(5 min por defecto). Agregado tambien en `design.md` D-B6.

Test que fija el desacople: `test_mfa_ticket_has_no_kid_header`
(assert `"kid" not in header` del ticket).

### S5 — `token_type` fuera del reto MFA (RESUELTO)

`LoginResponse.token_type` pasa a `str | None = None`. En el reto, el campo nulo
se omite (`response_model_exclude_none=True`); en el flujo de un paso y en
`/auth/mfa/verify` sigue `bearer`. Assert agregado en
`test_challenge_and_verify_flow` (`"token_type" not in body`).

### S2 — Privilegiada sin MFA + bandera ON (RESUELTO)

Nuevo `test_privileged_flag_on_without_enrollment_single_step`: sin enrollment
(`totp_enabled=False`) la cuenta privilegiada entra en un solo paso (el reto solo
aplica con MFA activo, D-B7).

### S3 — Normalizacion de codigo de recuperacion (RESUELTO)

Nuevo `test_recovery_code_accepts_normalized_variants`: el codigo se acepta sin
guiones y en minusculas, y tambien en su forma canonica con guion.

### S6 — Enrollment restringido a privilegiadas (RESUELTO)

`POST /auth/mfa/enroll` ahora exige una cuenta privilegiada (403 `FORBIDDEN` en
caso contrario). El gating NO reintroduce el bloqueo circular: una cuenta
privilegiada SIN MFA activo inicia sesion en un solo paso, obtiene token y
enrola; el reto solo aparece cuando el MFA YA esta activo, y si se pierde el
dispositivo y los codigos aplica el reset administrativo (OQ-B2). Racional
documentado en el docstring del endpoint y en `design.md` D-B7. Test:
`test_enroll_forbidden_for_non_privileged`.

### S7 — Impact table del proposal (RESUELTO)

`proposal.md` ya no lista `src/services/api.ts`; la fila frontend apunta a
`AuthContext.tsx`, `LoginPage/index.tsx` y `MfaEnrollmentPage/**`. Se corrigio
ademas la fila del privilegio (`privilege_service.py` +
`directorio_service.py`) y la descripcion de `auth_service.py` (ticket, no
derivacion).

### S1 / S4 — Sin cambios (tradeoffs aceptados)

- S1: `pyotp==2.9.0` anclado y comentado en `requirements.txt` (nota de
  supply-chain; verificar owner oficial antes de release). Aceptado.
- S4: replay del ticket dentro de su TTL y del TOTP dentro de la ventana RFC 6238
  es un tradeoff declarado (D-B6); no rompe spec. Aceptado.

### Re-verificacion post-fix (evidencia real)

```
cd App/Backend; pytest -m "not integration" -q
  -> 1207 passed, 42 deselected, 1 xfailed  (antes: 1203; +4 tests)
docker compose -p mesa_local up -d postgres
cd App/Backend; pytest -m integration -q
  -> 42 passed
docker compose -p mesa_local stop postgres
cd App/Backend; ruff check .                 -> All checks passed!
openspec validate c-63b-mfa-y-rol-privilegiado --strict -> is valid
tests/test_openapi_sync.py                   -> 5 passed (docs/openapi.json regenerado)
cd App/Frontend; npm run test               -> 133 passed
```

Suites de c-63c (`test_c63c_jwt_rotation.py`, `test_c63c_fernet_rotation.py`)
siguen verdes: el keyring del ACCESS TOKEN no fue alterado.

### Post-verify verdict

**PASS** — W1 resuelto (c-63b sin dependencia de c-63c en el ticket MFA) y
sugerencias S2/S3/S5/S6/S7 cerradas con tests y documentacion. Sin CRITICAL ni
WARNING pendientes.
