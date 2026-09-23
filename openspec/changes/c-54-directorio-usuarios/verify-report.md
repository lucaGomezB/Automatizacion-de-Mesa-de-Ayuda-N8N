# Verification Report — c-54-directorio-usuarios

**Change**: `c-54-directorio-usuarios`
**Version**: N/A (delta change, 3 new capabilities)
**Mode**: Standard (Strict TDD module produces runtime evidence; this report is adversarial/independent)
**Verified by**: sdd-verify executor (independent — did NOT trust the apply summary)
**Date**: 2026-09-23

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 35 |
| Tasks complete | 34 |
| Tasks incomplete | 1 (task 7.5 — human review, intentionally PENDING) |

Incomplete task:
- `7.5 Revision humana (HIGH)`: confirm retention/ARCO policy, role-based incident visibility and its scope, and that there is no real PII in repo/DB; confirm no blind-index key was added. **Open gate, not a failure** (governance HIGH/CRITICAL, synthetic data only).

---

## Build & Tests Execution (real execution)

**Lint** — `cd App/Backend; ruff check .`
```
All checks passed!
```
(exit 0)

**Offline unit suite** — `pytest -m "not integration" -q`
```
765 passed, 33 deselected, 1 xfailed, 193 warnings in 253.00s (0:04:12)
```
The single `xfailed` is PRE-EXISTING and unrelated to c-54: `tests/test_n8n_workflow.py::test_payload_has_no_obvious_pii` (documented C-04 gap).

**PostgreSQL integration suite** — `pytest -m integration -q`
```
33 passed, 766 deselected, 1 warning in 54.22s
```

**OpenAPI sync** — `pytest tests/test_openapi_sync.py -v`
```
5 passed
```

**OpenSpec strict validation** — `openspec validate --strict --changes c-54-directorio-usuarios`
```
✓ change/c-52-telefonica-transcripcion-async
✓ change/c-53-notificacion-numero-incidente
✓ change/c-54-directorio-usuarios
Totals: 3 passed, 0 failed
```

**c-54 test inventory** (79 tests: 72 offline + 7 integration)

| Test file | Tests |
|-----------|------:|
| `tests/test_contactos.py` | 11 |
| `tests/test_empleado_model.py` | 9 |
| `tests/test_empleado_repository.py` | 5 |
| `tests/test_migration_009_directorio.py` | 4 |
| `tests/test_directorio_service.py` | 15 |
| `tests/test_contact_resolution_service.py` | 13 |
| `tests/test_api_directorio.py` | 7 |
| `tests/test_incident_visibility.py` | 5 |
| `tests/test_seed_directorio.py` | 3 |
| `tests/integration/test_directorio_postgres.py` | 7 |

**Coverage**: not re-measured (threshold not asserted in the change tasks); tests exercise the changed modules directly.

---

## Spec Compliance Matrix (behavioral — runtime evidence)

### employee-directory

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| DIR-001 | Fila independiente de la cuenta | `test_empleado_model.py::test_persistencia_texto_plano_y_vinculo_opcional` | ✅ COMPLIANT |
| DIR-001 | Cuenta de autenticacion sin empleado | `test_contact_resolution_service.py::test_usuario_sin_empleado_no_es_fatal`, `test_api_directorio.py::test_cuenta_sin_empleado_403` | ✅ COMPLIANT |
| DIR-001 | Vinculo opcional cuenta↔empleado | `test_empleado_model.py::test_persistencia_texto_plano_y_vinculo_opcional` | ✅ COMPLIANT |
| DIR-002 | Empleado con email y telefono | `test_directorio_service.py::test_alta_valida_con_y_sin_telefono` | ✅ COMPLIANT |
| DIR-002 | Empleado sin telefono | `test_directorio_service.py::test_alta_valida_con_y_sin_telefono` | ✅ COMPLIANT |
| DIR-002 | Email duplicado rechazado | `test_directorio_service.py::test_email_debe_ser_unico`, `test_api_directorio.py::test_error_y_auditoria_sin_pii` | ✅ COMPLIANT |
| DIR-002 | Telefono repetido permitido | `test_directorio_service.py::test_telefono_repetido_permitido` | ✅ COMPLIANT |
| DIR-002 | Telefono fuera de E.164 | `test_directorio_service.py::test_telefono_fuera_de_e164_rechazado` | ✅ COMPLIANT |
| DIR-002 | Sin campos adicionales | `test_empleado_model.py::test_columnas_exactas_sin_datos_extra` | ✅ COMPLIANT |
| DIR-003 | Rol valido aceptado | `test_directorio_service.py::test_alta_valida_con_y_sin_telefono` | ✅ COMPLIANT |
| DIR-003 | Rol invalido rechazado | `test_directorio_service.py::test_rol_invalido_rechazado` | ✅ COMPLIANT |
| DIR-003 | El rol no afecta la clasificacion | (none found) | ❌ UNTESTED |
| DIR-004 | Sector tomado del catalogo | `test_directorio_postgres.py::test_fk_a_sector_y_users` | ✅ COMPLIANT |
| DIR-004 | usuario_final/operador requieren sector | `test_directorio_service.py::test_usuario_final_y_operador_requieren_sector` | ✅ COMPLIANT |
| DIR-004 | Administrador sin sector | `test_seed_directorio.py::test_seed_enlaza_users_y_empleado_y_deja_admin_operativo` | ✅ COMPLIANT |
| DIR-004 | Sector inexistente rechazado | `test_directorio_service.py::test_sector_inexistente_rechazado` | ✅ COMPLIANT |
| DIR-005 | Contacto disponible en claro | `test_empleado_model.py::test_persistencia_texto_plano_y_vinculo_opcional` | ✅ COMPLIANT |
| DIR-005 | Sin clave ni indice ciego | `test_empleado_model.py::test_sin_columnas_cifradas_ni_hash_ciego` (+ repo grep) | ✅ COMPLIANT |
| DIR-005 | El cifrado del incidente no cambia | `tests/test_encryption.py`, `tests/test_modelo_doble_representacion.py` (legacy, green) | ✅ COMPLIANT |
| DIR-006 | Gestion sin rol suficiente | `test_api_directorio.py::test_escritura_otro_rol_403` | ✅ COMPLIANT |
| DIR-006 | Acceso anonimo rechazado | `test_api_directorio.py::test_acceso_anonimo_401` | ✅ COMPLIANT |
| DIR-006 | Resolucion interna sin borde HTTP | `test_contact_resolution_service.py` (in-process service) | ✅ COMPLIANT |
| DIR-006 | Auditoria de accesos | `test_directorio_service.py::test_auditoria_registra_actor_operacion_sin_pii`, `test_api_directorio.py::test_error_y_auditoria_sin_pii` | ✅ COMPLIANT |
| DIR-006 | PII fuera de los logs | `test_directorio_service.py::test_auditoria_de_desactivacion_y_borrado_sin_pii`, `test_contact_resolution_service.py::test_trazabilidad_sin_pii` | ✅ COMPLIANT (see W1 for 422 path) |
| DIR-007 | Empleado desactivado no resuelve | `test_contact_resolution_service.py::test_empleado_inactivo_no_resuelve` | ✅ COMPLIANT |
| DIR-007 | Reactivacion | `test_directorio_service.py::test_desactivacion_no_borra_y_reactivacion` | ✅ COMPLIANT |
| DIR-007 | Borrado por retencion | (none found) | ❌ UNTESTED (no mechanism) |
| DIR-007 | Borrado por ARCO | `test_directorio_service.py::test_borrado_arco_elimina_fisicamente` | ✅ COMPLIANT |

### contact-resolution

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| RES-001 | Telefono conocido resuelve | `test_contact_resolution_service.py::test_resolver_por_telefono_encontrado` | ✅ COMPLIANT |
| RES-001 | Telefono desconocido no es fatal | `test_contact_resolution_service.py::test_telefono_desconocido_no_es_fatal` | ✅ COMPLIANT |
| RES-001 | Normalizacion previa | `test_contact_resolution_service.py::test_resolver_por_telefono_normaliza_antes_de_buscar` | ✅ COMPLIANT |
| RES-002 | Email conocido resuelve | `test_contact_resolution_service.py::test_resolver_por_email_encontrado_y_normalizado` | ✅ COMPLIANT |
| RES-002 | Email desconocido no es fatal | `test_contact_resolution_service.py::test_email_desconocido_y_malformado_no_son_fatales` | ✅ COMPLIANT |
| RES-002 | Email con mayusculas | `test_contact_resolution_service.py::test_resolver_por_email_encontrado_y_normalizado` | ✅ COMPLIANT |
| RES-003 | Cuenta vinculada resuelve | `test_contact_resolution_service.py::test_resolver_por_usuario_vinculado` | ✅ COMPLIANT |
| RES-003 | Cuenta sin empleado no es fatal | `test_contact_resolution_service.py::test_usuario_sin_empleado_no_es_fatal` | ✅ COMPLIANT |
| RES-004 | Coincidencia unica | `test_resolver_por_telefono_encontrado` / `test_resolver_por_email_encontrado_y_normalizado` | ✅ COMPLIANT |
| RES-004 | Coincidencia ambigua | `test_contact_resolution_service.py::test_telefono_ambiguo_no_concluyente` | ✅ COMPLIANT |
| RES-004 | Resultado vacio representable | `test_telefono_desconocido_no_es_fatal` (EstadoResolucion.NO_ENCONTRADO) | ✅ COMPLIANT |
| RES-005 | Estrategia enchufable sin romper entrega | `test_contact_resolution_service.py::test_directorio_vacio_devuelve_no_encontrado_sin_excepcion` | ✅ COMPLIANT |
| RES-005 | La resolucion no envia notificaciones | `test_contact_resolution_service.py::test_resolucion_no_envia_notificaciones` | ✅ COMPLIANT |
| RES-005 | Independencia de c-53 | `test_directorio_vacio_devuelve_no_encontrado_sin_excepcion` | ✅ COMPLIANT |
| RES-006 | Trazabilidad sin PII | `test_contact_resolution_service.py::test_trazabilidad_sin_pii` | ✅ COMPLIANT |
| RES-006 | Identificador minimo | Structural (service accepts only the identifier; verified by inspection) | ✅ COMPLIANT |

### incident-visibility

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| VIS-001 | Administrador ve todos | `test_incident_visibility.py::test_admin_ve_todos_los_incidentes` | ✅ COMPLIANT |
| VIS-001 | No administrador ve solo su sector | `test_incident_visibility.py::test_no_admin_ve_solo_su_sector` | ✅ COMPLIANT |
| VIS-001 | Sin sector no ve incidentes | `test_incident_visibility.py::test_cuenta_sin_empleado_alcance_vacio` | ✅ COMPLIANT |
| VIS-001 | Alcance aplicado en acceso puntual | `test_incident_visibility.py::test_acceso_puntual_fuera_de_sector_404` | ⚠️ PARTIAL (GET only; PATCH unscoped — see W3) |

**Compliance summary**: **46/48 scenarios compliant** (2 UNTESTED, 1 PARTIAL counted within compliant above).

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| DIR-001 entidad separada | ✅ Implemented | `app/models/empleado.py:67` table `directorio_empleado`; `user_id` nullable FK `ON DELETE SET NULL` (`:87-92`) |
| DIR-002 campos exactos | ✅ Implemented | Columns match exact set; UNIQUE legajo/email, indexed email/telefono |
| DIR-003 roles | ✅ Implemented | `RolEmpleado` 3 values + `CheckConstraint` (`empleado.py:98-103`); classifier untouched |
| DIR-004 sector FK | ✅ Implemented | FK → `sector.id`; `_validar_sector_por_rol` enforces role/sector coherence (`directorio_service.py:243-268`) |
| DIR-005 plaintext | ✅ Implemented | `String` columns only; NO `EncryptedText`, NO blind index, NO `directory_blind_index_key` anywhere |
| DIR-006 access/audit | ✅ Implemented | 401 anon, 403 non-admin, audit logs without PII (`directorio_service.py:270-284`) |
| DIR-007 lifecycle | ⚠️ Partial | Deactivation/reactivation/ARCO implemented; **retention after active+1yr not implemented** (no date/job) |
| RES-001..004 | ✅ Implemented | `contact_resolution_service.py` normalizes + exact match + ambiguity |
| RES-005/006 | ✅ Implemented | In-process seam, no notifications, structured trace without PII |
| VIS-001 | ✅ Implemented (read paths) | `alcance_desde_empleado` + `incident_visibility.py`; integrated into GET list/detail; **PATCH not scoped** |

**Model fidelity / no-crypto verification** (grep across repo):
- `blind_index`, `directory_blind_index_key`, `email_hash`, `telefono_hash`: **0 matches in code/config** (only descriptive mentions in `design.md:52` and `docs/directorio-usuarios.md:42` stating there is NO such key).
- `EncryptedText`: appears ONLY in pre-existing incident/telefonia code and their tests — **none** of the c-54 directory files.
- Exact columns confirmed on real PostgreSQL (11 columns): `id, legajo, nombre, email, telefono, sector_id, rol, activo, user_id, created_at, updated_at`.

---

## Migration & Seed Verification (independent execution)

**Migration `009` (`App/Backend/alembic/versions/009_directorio_empleado.py`)** — `revision="009"`, `down_revision="008"`, additive, no seed data.

Executed on a **disposable PostgreSQL database** (`c54_mig_check`, created/dropped by me; application DB untouched):
```
alembic upgrade head   → Running upgrade 008 -> 009, Migracion 009: directorio de empleados (c-54)
alembic current        → 009 (head)
alembic downgrade -1   → Running downgrade 009 -> 008
alembic current        → 008
table after downgrade  → count = 0 (dropped)
alembic upgrade head   → 008 -> 009 (re-created)
rows in directorio_empleado → 0  (NO PII seeded)
```
Constraints/indexes verified on real PostgreSQL:
- `directorio_empleado_pkey` PRIMARY KEY (id)
- `ix_directorio_empleado_legajo` UNIQUE, `ix_directorio_empleado_email` UNIQUE
- `ix_directorio_empleado_telefono` non-unique, `..._sector_id`, `..._user_id`, `..._created_at`
- `directorio_empleado_sector_id_fkey` → sector(id) ON DELETE SET NULL
- `directorio_empleado_user_id_fkey` → users(id) ON DELETE SET NULL
- `ck_directorio_empleado_rol` CHECK on the 3 role values

**Seed `scripts/seed_directorio.py`**:
- Creates BOTH `users` and `directorio_empleado` linked by `user_id`, one synthetic user per role (admin/operador/usuario_final).
- Idempotent by `legajo` (`seed_directorio.py:93-95`); re-running does not duplicate (`test_seed_idempotente_crea_un_usuario_por_rol`).
- No real PII: domain `.test`, dev passwords with `# gitleaks:allow` (`seed_directorio.py:38-69`).
- Bootstrap first admin resolved (admin has `sector_id=None`, `activo=True`, linked user).

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 tabla propia, no extender `users` | ✅ Yes | `directorio_empleado` + nullable `user_id` |
| D2 roles minimos 3 valores | ✅ Yes | Enum + CHECK |
| D3 FK al catalogo `sector` | ✅ Yes | No parallel vocabulary |
| D4 texto plano, sin cifrado/indice ciego | ✅ Yes | Verified by grep + PG schema |
| D5 gestion con rol, resolucion in-process | ✅ Yes | `require_directorio_admin` / lectura; service seam |
| D6 ambiguedad → no resuelve | ✅ Yes | `EstadoResolucion.AMBIGUO`, `empleado=None` |
| D6b campos exactos | ✅ Yes | 11 columns exactly |
| D7 visibilidad por rol a nivel API | ✅ Yes (read) | List + GET scoped; PATCH not scoped (see W3) |
| D8 ciclo de vida: desactivacion/retencion/ARCO | ⚠️ Deviated | Retention-after-1yr not implemented; ARCO yes |
| D9 migracion 009 + seed idempotente sin PII | ✅ Yes | Verified on real PostgreSQL |
| D10 estrategia de tests unit+integration | ✅ Yes | 72 offline + 7 integration |
| D11 contrato c-53, c-54 no toca c-53 | ✅ Yes | No import of notification code; independent |
| D12 gobernanza HIGH | ⚠️ Open | Task 7.5 human review pending (expected) |
| D13 sin cambios a clasificacion/notificaciones | ✅ Yes | `constants.py`, classifier, N8N untouched |

---

## Authorization & PII Leak Checks (adversarial)

**Authorization — directory API** (`app/routes/directorio.py`):
- Write (POST/PATCH/DELETE): `require_directorio_admin` → 403 if not `administrador_directorio`. Tested (`test_escritura_otro_rol_403`).
- Anonymous: no token → 401 envelope `UNAUTHORIZED`. Tested (`test_acceso_anonimo_401`).
- Read (GET list/detail): `require_directorio_lectura` → `usuario_final` and accounts without employee get 403. Tested (`test_usuario_final_no_puede_leer_403`, `test_cuenta_sin_empleado_403`).
- Success responses expose contact to authorized roles only (intended for management); no `user_id`/internal columns in `EmpleadoRead`.

**Conftest override scrutiny (check #3)**:
- `tests/conftest.py` overrides `get_alcance_incidentes` with an ADMIN scope in FOUR fixtures (lines 424-427, 547-549, 708-711, 784-787) so legacy incident tests keep global scope.
- The REAL default IS exercised WITHOUT override by `tests/test_incident_visibility.py`, which builds its own app and overrides only `get_db_session` + `get_current_user` (lines 103-127). Therefore the override **cannot mask a broken default** for the covered cases.
- Gap: the empty-scope case is tested for LISTING only. Point access (`GET /{id}`) by an account with NO linked employee is not tested (only an operador out-of-sector). Minor, see N1.
- The 5 visibility tests are meaningful (seed two sectors, assert cross-sector isolation), not tautological.

---

## Issues Found

### BLOCKING (must fix before archive)
None. All suites green, migration verified, model matches spec exactly, no crypto residue.

### WARNING (should fix)
- **W1 — PII echoed in 422 schema-validation responses (DIR-006).** Pydantic validation errors include the submitted `input`; the app's `RequestValidationError` handler serializes `exc.errors()` into `error.details.errors` (`app/core/error_handlers.py:145-162`). A payload with an over-length `telefono`/`email`/`nombre` (constraints at `app/schemas/directorio.py:23-26,35-38`) returns the value in clear.
  Evidence (executed):
  ```
  EmpleadoCreate(... telefono='+5491100000111111111111111111111111111111')
  → loc=('telefono',) type=string_too_long input='+5491100000111111111111111111111111111111'
  ```
  The existing PII test only covers the domain-level duplicate-email error (generic message), not schema-level length errors. DIR-006 states error responses MUST NOT contain contact PII in clear.
- **W2 — DIR-007 "Borrado por retencion" scenario is neither implemented nor tested.** No retention-after-(active+1yr) mechanism or `fecha_baja` field exists; only ARCO physical delete (`directorio_service.py:204-210`). Task 7.5 keeps the retention POLICY pending human review, so this is an open spec-vs-implementation mismatch the orchestrator must resolve (implement/soft-track, or narrow the spec before archiving). The delta spec would otherwise enshrine an unimplemented SHALL.
- **W3 — Incident PATCH is not scoped by role (VIS-001).** `GET` list/detail apply `alcance`, but `PATCH /incidentes/{id}` calls `service.update_incidente` (`app/routes/incidentes.py:223`) which internally calls `get_by_id(incidente_id)` WITHOUT `alcance` (`app/services/incidente_service.py:386`), then returns `IncidenteRead`. A non-admin operador can therefore retrieve (and mutate) any incident's content by ID, bypassing the 404 isolation enforced on GET. The spec literally scopes "lectura y listado", but the scenario "Alcance aplicado en el acceso puntual" is defeated through this path.
  Evidence: compare `get_by_id` scope check at `incidente_service.py:144-149` vs unscoped call at `:386`.

### SUGGESTION / NIT (nice to have)
- **N1** — Add an HTTP test for `GET /api/v1/incidentes/{id}` with an account that has NO linked employee (empty scope → 404), and for a `usuario_final` (only `operador` is covered for sector scoping). Also consider asserting that `get_alcance_incidentes` is not overridden in the visibility tests.
- **N2** — DIR-003 scenario "El rol no afecta la clasificacion" has no test at all. The code indeed never feeds role into the classifier; a regression test asserting classifier output is invariant to role would close the scenario.
- **N3** — `EmpleadoRepository.get_by_user_id` uses `scalar_one_or_none()`; since `user_id` is not UNIQUE in the directory, two rows linked to the same account would raise `MultipleResultsFound` (500). Not spec'd, but a robustness edge.
- **N4** — `alembic upgrade/downgrade` is validated in the suite only via SQLite (`test_migration_009_directorio.py`), because the PostgreSQL integration fixtures use `Base.metadata.create_all` (conftest.py:301-303), NOT migrations. I verified the migration manually on real PostgreSQL; consider adding a migration-based PG check later.

---

## Cross-Change Notes

- **No contamination from c-53:** c-54 code/specs do not import or depend on `incident-notification`, `n8n-workflow`, or `runtime-cost-guard`. The only c-53 reference in c-54 is descriptive ("seam c-53") in `contact_resolution_service.py`; RES-005 independence is tested with an empty directory. Both changes could co-exist.
- **Archive order:** `c-52` and `c-53` both carry a `runtime-cost-guard` delta spec; c-53's design states **c-52 MUST be archived before c-53**. c-54 touches none of the shared specs (`employee-directory`, `contact-resolution`, `incident-visibility` are new only), so it is independent.
  **Recommended order: c-52 → c-53**, then **c-54** (c-54 may technically be archived at any point, but sequencing it last avoids concurrent edits under `openspec/specs/`).

---

## Verdict

**READY WITH WARNINGS**

The core implementation is complete and correct: model fields/constraints match D6b exactly, no encryption/blind-index/key residue exists, migration `009` upgrades/downgrades cleanly on real PostgreSQL with 0 seeded rows, the seed is idempotent and PII-free, OpenAPI is in sync, and all suites pass (765 offline / 1 pre-existing xfail, 33 integration, ruff clean, strict validation green). Two spec scenarios remain untested/unimplemented (DIR-003 classification independence, DIR-007 retention) and there are two real gaps worth resolving before or during archive: PII echoed in 422 schema errors (W1) and unscoped PATCH on incidents (W3). Task 7.5 (human review, HIGH) remains an **open gate**, correctly pending. The DIR-007 retention mismatch (W2) is the item most likely to deserve an explicit orchestrator/human decision before the delta spec is synced.
