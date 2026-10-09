# Verification Report — c-63c-rotacion-claves-secretos

**Change**: c-63c-rotacion-claves-secretos (Fase C del workstream de identidad y claves)
**Spec version**: identity-access-hardening (delta c-63c)
**Governance**: CRITICO (criptografia / claves y secretos)
**Mode**: Standard verify + evidencia adversarial de ejecucion independiente
**Date**: 2026-10-08
**Verifier**: sdd-verify (ejecucion real, no se confio en resumenes)
**Base**: working tree sobre `main`, HEAD `066a6cc`

---

## 1. Alcance verificado

Ejecucion independiente sobre el working tree, sin confiar en el estado declarado. Evidencia
por lectura de codigo + ejecucion real de suites + pruebas adversariales propias + verificacion
de higiene.

Artefactos leidos: `proposal.md`, `design.md`, `tasks.md`,
`specs/identity-access-hardening/spec.md` y los archivos de codigo/test/documentacion
declarados.

**Archivos de c-63c (confirmados por `git status` / `git show`):**

| Area | Archivo | Estado |
|------|---------|--------|
| Core (N) | `App/Backend/app/core/jwt_keyring.py` | Nuevo (no existe en HEAD) |
| Core | `App/Backend/app/core/security.py` | M (decodificacion con keyring) |
| Config | `App/Backend/app/config/settings.py`, `.env.example` | M (keyring + Fernet anterior) |
| Servicio | `App/Backend/app/services/auth_service.py` | M (firma con `kid`) |
| Ruta | `App/Backend/app/routes/auth.py` | M (pasa `key_id`) |
| Util | `App/Backend/app/utils/encryption.py` | M (`MultiFernet`) |
| Script (N) | `App/Backend/scripts/rotate_fernet_key.py` | Nuevo |
| Tests (N) | `tests/test_c63c_jwt_rotation.py`, `tests/test_c63c_fernet_rotation.py` | Nuevos |
| Docs (N) | `docs/seguridad/gestion-secretos-y-rotacion.md`, `docs/seguridad/ciclo-vida-identidades-y-revision-accesos.md` | Nuevos |
| Docs | `docs/seguridad/README.md` | M (indice) |

Fuera de alcance NO tocados y confirmado por `git status`: `n8n/workflow.json`,
`docker-compose.yml`, `CHANGES.md` (los tres sin cambios).

---

## 2. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 28 |
| Tasks complete `[x]` | 28 |
| Tasks incomplete `[ ]` | 0 |

Secciones 0 a 5 completas (0.1-0.5, 1.1-1.5, 2.1-2.6, 3.1-3.4, 4.1-4.3, 5.1-5.5).

---

## 3. Build & Tests Execution (evidencia real)

### Backend — subconjunto SQLite (offline)
```
cd App/Backend; pytest -m "not integration" -q
1203 passed, 42 deselected, 1 xfailed, 331 warnings in 269.27s
```
Exit code 0. Conteo exacto del esperado (~1203).

### Backend — subconjunto PostgreSQL integration
```
docker compose up -d postgres          # name: mesa_local; healthy en 127.0.0.1:5433
cd App/Backend; pytest -m integration -q
42 passed, 1204 deselected, 6 warnings in 36.28s
docker compose stop postgres
```
Exit code 0. Base descartable `mesa_de_ayuda_test` (guard de nombre de base activo).

### Tests dedicados c-63c + contrato auth + OpenAPI
```
cd App/Backend; pytest tests/test_c63c_jwt_rotation.py tests/test_c63c_fernet_rotation.py tests/test_auth.py tests/test_openapi_sync.py -q
46 passed, 1 warning in 7.57s
```
Exit code 0. 22 tests c-63c (14 JWT + 8 Fernet) + contrato `test_auth.py` + sync de OpenAPI.

### Lint backend
```
cd App/Backend; ruff check .   -> All checks passed! (exit 0)
```

### Frontend
```
cd App/Frontend; npm run test
Test Files 29 passed (29); Tests 133 passed (133); exit 0
```
Los archivos frontend modificados pertenecen a c-63b (AuthContext/LoginPage/MfaEnrollment), no a c-63c.

### OpenSpec
```
openspec validate c-63c-rotacion-claves-secretos --strict
-> Change 'c-63c-rotacion-claves-secretos' is valid (exit 0)
```

### Higiene de secretos
```
python3 scripts/security/scan_engram_secrets.py .engram
-> Total: 0 hallazgo(s)   (exit 0)
```
No hay `.env` versionado; `.env.example` no contiene valores reales.

---

## 4. Spec Compliance Matrix (validacion conductual IAH-008..IAH-011)

| Requirement | Scenario | Test / Evidencia | Result |
|-------------|----------|------------------|--------|
| IAH-008 keyring JWT | Token de clave anterior aceptado en ventana | `test_c63c_jwt_rotation.py::test_token_signed_with_previous_key_is_accepted_within_window`, `::test_get_current_user_accepts_previous_key_within_window` | COMPLIANT |
| IAH-008 | Token de clave anterior rechazado tras la ventana | `::test_token_with_previous_key_is_rejected_after_window`, `::test_window_closes_exactly_at_expiry`, `::test_get_current_user_rejects_previous_key_after_window` (401) | COMPLIANT |
| IAH-008 | Token legacy sin `kid` aceptado en transicion | `::test_legacy_token_without_kid_is_accepted_via_active_key`, `::test_legacy_token_without_kid_falls_back_to_previous_key` | COMPLIANT |
| IAH-008 | La firma nueva usa la clave activa | `::test_new_token_uses_active_key_and_carries_kid` + prueba adversarial propia | COMPLIANT |
| IAH-008 | Verificacion acotada (no ilimitada) | `::test_unknown_kid_is_rejected_without_trying_extra_keys` (0 intentos), `::test_verification_is_bounded_to_two_keys` (2 intentos) | COMPLIANT |
| IAH-009 Fernet | Inventario exhaustivo de columnas | `test_c63c_fernet_rotation.py::test_script_inventory_covers_all_encrypted_columns` (igualdad exacta con `EncryptedText`) | COMPLIANT |
| IAH-009 | La rotacion exige respaldo previo | `::test_rotation_requires_previous_backup`, `::test_cli_aborts_without_existing_backup`; CLI real `--backup-path /nope.dump` -> exit 2 sin tocar datos | COMPLIANT |
| IAH-009 | El dato antiguo se descifra durante la rotacion | `::test_multi_fernet_decrypts_data_encrypted_with_previous_key`, `::test_rotation_reencrypts_inventory_and_reports_counts` | COMPLIANT |
| IAH-009 | El re-cifrado es transaccional | `::test_rotation_reverts_on_mid_failure` (rollback total; valor crudo identico al previo) | COMPLIANT |
| IAH-009 | Dato re-cifrado legible con la clave nueva | `::test_rotation_reencrypts_inventory_and_reports_counts` (descifra con `new`), `::test_encryption_uses_active_key` | COMPLIANT |
| IAH-009 | La rotacion es reversible | `::test_rotation_is_reversible` (repone la anterior como activa y vuelve a ser legible) | COMPLIANT |
| IAH-010 higiene | No hay secretos en el repositorio | `scan_engram_secrets.py .engram` = 0 hallazgos; sin `.env` versionado | COMPLIANT |
| IAH-010 | Inventario de secretos y runbook existen | `gestion-secretos-y-rotacion.md` §2 (inventario) y §6/§7 (runbooks JWT y Fernet) | COMPLIANT |
| IAH-010 | KMS/PAM/CA encuadrados como futuros | `gestion-secretos-y-rotacion.md` §5 "NO implementado" | COMPLIANT |
| IAH-010 | Postura `.env` + opciones no adoptadas | `gestion-secretos-y-rotacion.md` §4 (SOPS/Docker secrets/Vault como NO adoptadas) | COMPLIANT |
| IAH-011 organizacional | Ciclo de vida de identidades documentado | `ciclo-vida-identidades-y-revision-accesos.md` §2 (5.16) | COMPLIANT |
| IAH-011 | Revision de accesos documentada y marcada (O) | mismo doc §3 y encabezado "(O)" (5.18) | COMPLIANT |
| IAH-011 | Referenciada desde el indice | `docs/seguridad/README.md` §5, §6.1 (5.16/5.18 -> documento), §6.2 (IAH-011) | COMPLIANT |

**Compliance summary**: 18/18 escenarios COMPLIANT. Los escenarios de IAH-010/IAH-011 son
documentales: se verifican por inspeccion de archivos (no existe doc-lint automatizado, por
decision de C-61). Los de IAH-008/IAH-009 se verifican por test en verde y ejecucion real.

---

## 5. Verificacion adversarial (probar, no confiar)

Script independiente (`PYTHONPATH=. python3`) mas CLI real, ademas de la suite. Resultados:

### JWT (IAH-008)
- Firma con la clave activa -> header `kid=v1`; verifica con la activa. PROBADO.
- Token firmado con la clave anterior + `kid=v0`, ventana abierta -> aceptado. PROBADO.
- Mismo token tras cerrarse la ventana (`expires_at` en el pasado) -> `JWTError`. PROBADO.
- Token legacy sin `kid` firmado con la anterior -> validado probando activa y luego la anterior. PROBADO.
- `kid` desconocido -> `candidate_keys == []`; se rechaza SIN intentar ninguna clave (0 llamadas a `jwt.decode`; el test lo fija con monkeypatch). PROBADO, verificacion acotada a <= 2.
- La firma SIEMPRE usa la clave activa: con clave anterior configurada, el header sigue siendo el `kid` activo y el token solo verifica con el secreto activo. PROBADO.

### Fernet (IAH-009)
- `MultiFernet` descifra ciphertext de la clave anterior estando en el conjunto. PROBADO.
- El cifrado nuevo usa la activa (la anterior NO abre el ciphertext nuevo). PROBADO.
- Cache invalidado por el CONJUNTO (activa+anterior), no solo por la activa. PROBADO.
- Ciphertext de una clave ajena al conjunto -> `InvalidToken`. PROBADO.
- `scripts/rotate_fernet_key.py` aborta (exit 2) sin respaldo valido, sin abrir transaccion. PROBADO en CLI.
- El inventario enumera EXACTAMENTE las 4 columnas `EncryptedText`
  (`incidente.descripcion_original`, `telefonia_ingreso.caller_cifrado`,
  `telefonia_ingreso.transcript_original`, `users.totp_secret`). PROBADO por test de igualdad.
- Re-cifrado en UNA transaccion, reporte por columna (`total`, `counts`), rollback ante fallo
  a mitad sin estado parcial. PROBADO.
- Reversion: reponer la clave anterior como activa deja todos los datos legibles y sin filas
  ilegibles. PROBADO.

### Docs
- `gestion-secretos-y-rotacion.md`: inventario de secretos (§2), inventario de columnas Fernet
  (§3), runbooks JWT (§6) y Fernet (§7), postura `.env` y opciones no adoptadas (§4),
  KMS/PAM/CA como futuro/no implementado (§5). EXISTE y cubre lo exigido.
- `ciclo-vida-identidades-y-revision-accesos.md`: 5.16 (§2) y 5.18 (§3) marcados como control
  organizacional (O) en encabezado y §4. EXISTE.
- `docs/seguridad/README.md`: §5 lista ambos documentos; §6.1 y §6.2 mapean 8.2/8.24/5.16/5.18
  e IAH-008..011. Las referencias cruzadas resuelven a archivos existentes.

### Flujo dev
- Sin clave anterior (default `""`), el keyring se comporta como antes
  (`test_settings_keyring_defaults_are_retrocompatible`).
- `admin`/`admin123` y `directorio.admin`: la suite completa (1203 + 42) pasa, incluidos
  `test_auth.py` y los tests de directorio; la bandera MFA esta apagada por defecto. Sin
  regresiones.

---

## 6. Acoplamiento entre changes (c-63b <-> c-63c)

**Direccion confirmada (la marcada por el verify de c-63b):** c-63b DEPENDE de c-63c.

- `app/services/auth_service.py` (seccion MFA, c-63b) importa `from app.core import jwt_keyring`
  (archivo nuevo de c-63c) y `create_mfa_ticket` / `decode_mfa_ticket` pasan
  `key_id=settings.jwt_key_id` y usan `jwt_keyring.decode_token`.
- Confirmado con `git show HEAD`: `jwt_keyring.py` NO existe en HEAD; `is_privileged` y
  `totp_secret` tampoco, por lo que ambos changes se aplican sobre el mismo working tree.

**Acoplamiento en la otra direccion (nuevo, hallado en esta verificacion):** c-63c tambien
referencia a c-63b. El inventario del script de rotacion incluye `users.totp_secret` (columna
introducida por c-63b) y `test_script_inventory_covers_all_encrypted_columns` exige que esa
columna exista. Sin c-63b, el script no importa (`AttributeError` sobre `User.totp_secret`) y el
test de inventario no puede pasar.

**Consecuencia:** el acoplamiento es MUTUO. Ninguno de los dos changes es revertible/archivable
de forma independiente en el estado actual.

**Orden correcto de commit/archivo:**
1. **Commit**: los dos applies deben ir en UN mismo commit atomico (o c-63b inmediatamente
   despues de c-63c en la misma serie). No separarlos en commits que dejen el arbol no
   importable.
2. **Archivo**: archivar `c-63c` PRIMERO (es el proveedor del `jwt_keyring` del que c-63b
   importa) y luego `c-63b`. El sync de specs de c-63c no depende de c-63b; a la inversa, el
   codigo de c-63b no arranca sin c-63c.
3. Corregir en `c-63b/proposal.md` la afirmacion "Sin dependencia de c-63c" (ya señalada como
   W1 en `c-63b/verify-report.md`).

---

## 7. Correctness (evidencia estructural)

| Requirement | Status | Notes |
|------------|--------|-------|
| IAH-008 keyring JWT | Implemented | `jwt_keyring.py`: `active_key`/`previous_key`/`candidate_keys`/`decode_token`; cota <= 2; `kid` aditivo en firma (`create_access_token(..., key_id=...)`); `security.get_current_user` usa `decode_token` |
| IAH-009 MultiFernet + script | Implemented | `encryption.py` con `MultiFernet([activa, anterior?])` y cache por conjunto; `scripts/rotate_fernet_key.py` con respaldo obligatorio, inventario explicito, transaccion unica y reporte |
| IAH-010 higiene/gestion | Implemented | Doc de gestion + runbooks + encuadre KMS/PAM/CA; scan de higiene en 0 hallazgos |
| IAH-011 organizacional | Implemented | Doc 5.16/5.18 como (O) referenciado desde el indice |

---

## 8. Coherence (design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D-C1 keyring <= 2 claves, prueba acotada, `kid` aditivo | Yes | `candidate_keys` acota; `unknown kid` -> lista vacia; tests de cota |
| D-C2 config aditiva y retrocompatible | Yes | `jwt_key_id=v1`, `jwt_previous_*` default vacio; defaults verificados |
| D-C3 `MultiFernet` + cache por conjunto | Yes | `_fernet_key` guarda `(active, previous)` |
| D-C4 script con respaldo previo + UNA transaccion + orden | Yes | `assert_backup`, `rollback` en `except`, CLI exit 2 |
| D-C5 inventario como prerequisito, 3 columnas + TOTP c-63b | Yes | OQ-C1 resuelta; INVENTORY de 4 columnas; test de igualdad |
| D-C6 doc nuevo + indice | Yes | `gestion-secretos-y-rotacion.md` + README actualizado |
| D-C7 5.16/5.18 como (O) documental | Yes | `ciclo-vida-identidades-...md` |
| D-C8 compatibilidad dev/CI | Yes | Sin clave anterior el comportamiento es el actual; suite completa verde |
| D-C4 "respaldo" valida contenido del dump | No aplica | Solo exige existencia/no-vacio (ver S2); el spec no pide validar el contenido |

---

## 9. Issues Found

**CRITICAL** (deben corregirse antes de archivar):
None. **CRITICAL count = 0.**

**WARNING** (deberian corregirse):

- **W1 — Acoplamiento mutuo no declarado c-63b <-> c-63c y working tree mezclado.**
  c-63b importa `app.core.jwt_keyring` (c-63c) y c-63c referencia `users.totp_secret` (c-63b)
  en el inventario y su test. Evidencia: `git show HEAD` no contiene `jwt_keyring.py`,
  `is_privileged` ni `totp_secret`; `git status` muestra artefactos de ambos changes en el
  mismo arbol. Impacto: ninguno de los dos es revertible/archivable por separado. Mitigacion:
  commit atomico conjunto y archivo de c-63c antes que c-63b (ver §6).

**SUGGESTION** (deseables):

- **S1 — `jwt_previous_key_id` no se valida contra `jwt_key_id`.** El design dice que deben
  diferir, pero no hay guard de arranque ni test. Con `jwt_previous_key_id == jwt_key_id`, un
  token de la clave anterior seria resuelto solo a la activa y rechazado, y un token realmente
  firmado por la activa seguiria validando (fallo silencioso de configuracion). Añadir un guard
  de arranque o un test de configuracion invalida.
- **S2 — `--backup-path` no valida que el archivo sea un dump utilizable.** Solo exige
  existencia y tamano > 0; un operador podria pasar el archivo equivocado y el script
  re-cifraria igual. Cumple el spec (que solo exige declarar un respaldo), pero conviene
  documentar la expectativa o validar un encabezado/formato.
- **S3 — `jwt_previous_key_expires_at` malformado se interpreta como "sin vencimiento".** Es
  una decision intencional documentada en `jwt_keyring.py` (no invalidar sesiones por formato),
  pero un typo mantendria la clave anterior valida indefinidamente. Con governance CRITICO,
  merece al menos un log de advertencia cuando el parseo falla.

---

## 10. Verdict

**PASS WITH WARNINGS**

Implementacion completa (28/28 tasks), 18/18 escenarios del spec COMPLIANT, suites backend
(SQLite 1203 + integration 42) y frontend (133) verdes, `ruff` y
`openspec validate --strict` en verde, higiene de secretos en 0 hallazgos, y las dos rotaciones
probadas de forma adversarial e independiente (JWT: ventana/legacy/cota/firma activa; Fernet:
descifrado previo, cifrado activo, respaldo obligatorio, transaccionalidad, reversibilidad).
Un unico WARNING (acoplamiento mutuo c-63b/c-63c, ya advertido por c-63b) y tres sugerencias;
**0 CRITICAL**.

---

## 11. Post-verify update (2026-10-08)

Continuacion del apply para resolver las SUGGESTIONS y re-confirmar el desacople W1.

### W1 — RESUELTO (desacople unidireccional)

El acoplamiento mutuo quedo resuelto del lado de c-63b: `c-63b` ya NO importa
`jwt_keyring`. El ticket MFA se firma/verifica DIRECTAMENTE con el secreto JWT
activo (`settings.jwt_secret_key`, HS256), sin `kid` (documentado en
`auth_service.create_mfa_ticket` / `decode_mfa_ticket`).

Evidencia:
```
grep -rn "jwt_keyring\|jwt_key_id" App/Backend/app/services/auth_service.py
-> 110: (solo docstring de create_access_token, helper de ACCESS TOKEN de c-63c)

grep -rln "jwt_keyring" App/Backend/app (sin __pycache__)
-> App/Backend/app/core/security.py   (c-63c)
```
Dependencia resultante (unidireccional): `c-63c` depende de `c-63a` (contrato de
tokens) y de `c-63b` (rota `users.totp_secret`); `c-63b` NO depende de `c-63c`.
El orden de archivo ya no exige c-63c primero; ambos pueden revertirse/archivarse
por separado.

### S1 — RESUELTO (guard de ids identicos)

`Settings` valida con `@model_validator(mode="after")`: si hay clave anterior
configurada, `jwt_previous_key_id` DEBE diferir de `jwt_key_id`; ids iguales
levantan un error de configuracion claro en el arranque.
Tests: `test_settings_rejects_identical_keyring_ids`,
`test_settings_accepts_distinct_keyring_ids`,
`test_settings_allows_same_id_without_previous_key`.

### S2 — RESUELTO (respaldo usable)

`assert_backup` ya no se limita a existencia/no-vacio: exige tamano >=
`MIN_BACKUP_BYTES` (1024) y el marcador de un dump de `pg_dump` en el encabezado
(formato plano `-- PostgreSQL database dump` o custom `PGDMP`). Un archivo
equivocado aborta con codigo no-cero SIN tocar datos (se valida antes de abrir
cualquier transaccion).
Tests: `test_backup_rejects_tiny_file`, `test_backup_rejects_content_without_marker`,
`test_backup_accepts_plain_dump_marker`, `test_backup_accepts_custom_format_marker`,
`test_cli_aborts_without_existing_backup` (incluye contenido invalido -> exit 2).

### S3 — RESUELTO (ventana malformada fail-closed)

`Settings` rechaza con `@field_validator` un `jwt_previous_key_expires_at` no
vacio que no sea ISO-8601 valido (no abre una ventana indefinida). Defensa
adicional en el keyring: `_parse_instant` lanza y `previous_key` trata la ventana
como CERRADA (fail-closed) ante un valor ilegible en un objeto duck-typed.
Tests: `test_settings_rejects_malformed_previous_expiry`,
`test_settings_accepts_valid_and_empty_previous_expiry`,
`test_previous_key_fails_closed_on_malformed_expiry`.

### Re-verificacion (ejecucion real)

```
cd App/Backend; pytest tests/test_c63c_jwt_rotation.py tests/test_c63c_fernet_rotation.py -q
-> 32 passed

cd App/Backend; pytest tests/test_c63a_auth_hardening.py tests/test_c63b_mfa.py \
    tests/test_c63b_login_two_step.py tests/test_c63b_privilege.py \
    tests/test_auth.py tests/test_auth_tokens.py tests/test_encryption.py \
    tests/test_settings_pseudonymization.py -q
-> 84 passed   (decouple sin regresiones de c-63a/c-63b)

cd App/Backend; pytest -m "not integration" -q
-> 1217 passed, 42 deselected, 1 xfailed

docker compose -p mesa_local up -d postgres
cd App/Backend; pytest -m integration -q
-> 42 passed   (luego docker compose -p mesa_local stop postgres)

cd App/Backend; ruff check .   -> All checks passed!
openspec validate c-63c-rotacion-claves-secretos --strict
-> Change 'c-63c-rotacion-claves-secretos' is valid
```

### Verdict post-verify

**PASS** (sin WARNING pendiente y con S1/S2/S3 resueltos). 28/28 tasks, 18/18
escenarios del spec COMPLIANT, suites backend (SQLite 1217 + integration 42) en
verde, `ruff` y `openspec validate --strict` en verde. El acoplamiento c-63b/c-63c
es ahora unidireccional (c-63c -> c-63b).
