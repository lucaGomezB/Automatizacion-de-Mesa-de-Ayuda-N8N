# Verification Report — Fixes W1-W3 (+ nits N1-N3) — c-54-directorio-usuarios

**Change**: `c-54-directorio-usuarios`
**Scope**: Independent, adversarial re-verification of the fixes delivered in commit `040f688` (`fix(c-54): corregir warnings de la verificacion (W1-W3)`), on top of `abe2308`.
**Mode**: Adversarial / independent (did NOT trust the apply summary; every claim re-confirmed in code AND by executing tests)
**Verified by**: sdd-verify executor
**Date**: 2026-09-23
**Production code modified**: NONE (report only). One temporary adversarial test file was created under `App/Backend/tests/` to obtain runtime evidence and was deleted afterwards; `git status` is clean.

---

## Executive verdict

| Item | Verdict | One-line evidence |
|------|---------|-------------------|
| **W1** — 422 no longer echoes submitted values | **STILL BROKEN (partial)** | `input`/`ctx`/`url` are dropped, but custom-validator messages kept in `msg` still interpolate the submitted value. Directory + built-in-constraint paths are safe; incident/classification custom validators leak. |
| **W2** — retention "contract + 1 year" | **CONFIRMED FIXED** | `fecha_baja` model+migration `010` (down_revision `009`), seal/clear on deactivate/reactivate, `purgar_vencidos` idempotent; 364-day kept / 366-day purged; leap-year clamp correct. |
| **W3** — `PATCH /incidentes/{id}` role scope | **CONFIRMED FIXED** | `alcance` propagated through route → service → `get_by_id`; out-of-scope = 404 and row NOT modified (asserted); admin allowed. |
| **N1** — empty-scope point access GET+PATCH ⇒ 404 | **CONFIRMED** | `test_acceso_puntual_sin_empleado_404` exercises both verbs. |
| **N2** — role does not affect classification | **CONFIRMED** | `test_directorio_clasificacion_independiente.py` (behavioral + structural). |
| **N3** — `get_by_user_id` robust to duplicates | **CONFIRMED** | `scalars().first()` with `order_by(id)`; `test_get_by_user_id_robusto_ante_duplicados`. |

**Overall: PASS WITH WARNINGS.** W2/W3/nits are properly fixed and evidenced. W1 is only a *partial* fix: the PII-bearing directory path is safe, but the global claim ("no longer echo submitted values") is false for endpoints whose schemas use custom validators that interpolate the offending value into the exception message. A new pre-existing scope bypass on the classification endpoints was also found.

---

## W1 — Sanitization of validation errors (HTTP 422)

### What the fix does (correct part)
`app/core/error_handlers.py` now defines `_sanitize_validation_errors(errors)` and the `RequestValidationError` handler uses it instead of `jsonable_encoder(exc.errors())`. It keeps only `loc`, `msg`, `type`, dropping `input`, `ctx` and `url`.

### Independent execution evidence (temporary adversarial tests, now deleted)
Submitted a PII-looking value (`pii.leak+5491100000111@example.test`, and a 42-char phone) and inspected the raw 422 body:

| Endpoint / field | Field class | Result |
|------------------|-------------|--------|
| `POST /api/v1/directorio/empleados` `telefono` (over max_length) | built-in constraint | PASS — value NOT in body |
| `POST /api/v1/directorio/empleados` `email` (over max_length) | built-in constraint | PASS — value NOT in body |
| `POST /api/v1/incidentes/` `origen_message_id` (over max_length) | built-in constraint | PASS — value NOT in body |
| `POST /api/v1/incidentes/` `origen_evento` | **custom validator** | **FAIL — value echoed in `msg`** |
| `POST /api/v1/incidentes/` `clasificacion.sector_predicho` | **custom validator** | **FAIL — value echoed in `msg`** |
| `PATCH /api/v1/clasificaciones/{id}/validar` `sector_validado` | **custom validator** | **FAIL — value echoed in `msg`** |

Raw 422 bodies captured during the run (verbatim):

```
{"error":{"code":"VALIDATION_ERROR","message":"Request validation failed.","details":{"errors":[
 {"loc":["body","origen_evento"],
  "msg":"Value error, El evento 'pii.leak+5491100000111@example.test' no crea incidentes; se esperaba uno de ['creacion', 'creacion_incidente'].",
  "type":"value_error"}]}}}
```

```
{"error":{"code":"VALIDATION_ERROR","message":"Request validation failed.","details":{"errors":[
 {"loc":["body","clasificacion","sector_predicho"],
  "msg":"Value error, Sector precalculado 'pii.leak+5491100000111@example.test' no pertenece al vocabulario canonico.",
  "type":"value_error"}]}}}
```

```
{"error":{"code":"VALIDATION_ERROR","message":"Request validation failed.","details":{"errors":[
 {"loc":["body","sector_validado"],
  "msg":"Value error, Sector 'pii.leak+5491100000111@example.test' no pertenece al vocabulario canonico.",
  "type":"value_error"}]}}}
```

### Root cause
Pydantic wraps a custom-validator `ValueError` into `msg = "Value error, <text>"`. The offending value is interpolated **inside the exception message** by the validators themselves, so dropping `input`/`ctx` does not help:

- `app/schemas/incidente.py:116` → `f"Sector precalculado '{v}' ..."`
- `app/schemas/incidente.py:126` → `f"Sectores adicionales ... {invalidos}"`
- `app/schemas/incidente.py:229-232` → `f"El evento '{v}' no crea incidentes; ..."`
- `app/schemas/clasificacion.py:109` → `f"Sector '{v}' ..."`
- `app/schemas/clasificacion.py:118-120` → `f"Sectores adicionales ... {invalidos}"`

The existing suite tests (`test_validation_error_sanitization.py`, `test_api_directorio.py::test_error_de_schema_no_refleja_el_telefono`) only exercise **built-in** length constraints, so they cannot detect this class of leak. The sanitizer comment ("`input` ... y `ctx` ... NUNCA se serializan") is honest about `input`/`ctx`, but the handler docstring's broader claim is not met.

### Assessment
- **DIR-006 for the directory (the actual PII domain of c-54) is satisfied**: directory schemas contain no value-interpolating custom validators, and both the telefono and email paths were independently confirmed clean.
- **The W1 claim as stated ("GLOBALLY ... confirm the value does NOT appear in the 422 body") is NOT satisfied** for the incident/classification endpoints.
- Severity: **WARNING** (not CRITICAL). The leaking fields are not contact fields in the directory model, but they are free-form strings an operator could populate with PII, and the fix's own stated goal is contradicted.

**Suggested remediation (not applied — verification only):** drop `msg` as well and expose a stable `type`/generic message, or prevent schemas from interpolating submitted values into `ValueError` (replace `f"...'{v}'..."` with a static message; keep `loc` for the client).

---

## W2 — Retention "employment contract + 1 year"

### Model / migration
- `app/models/empleado.py:92-94` — `fecha_baja: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)`. Column set now exactly 12 (`id, legajo, nombre, email, telefono, sector_id, rol, activo, fecha_baja, user_id, created_at, updated_at`), verified by introspection.
- `alembic/versions/010_directorio_fecha_baja.py` — `revision="010"`, `down_revision="009"`, `op.add_column` nullable, `downgrade` drops it. **009 untouched** (still `revision="009"`, `down_revision="008"`).
- Migration chain verified linear and consistent: `001 → 002 → ... → 009 → 010` (no branching).

### Lifecycle
- `desactivar_empleado` sets `activo=False` and seals `fecha_baja = utcnow()`.
- `reactivar_empleado` sets `activo=True` and clears `fecha_baja = None`.
- `retencion_vencida(fecha_baja, ahora)` is pure; `None` never purges; naive datetimes normalized to UTC; `_sumar_un_anio` clamps 29-Feb to 28-Feb.
- `DirectorioService.purgar_vencidos` selects `activo=false` rows, deletes those with `fecha_baja + 1 year <= now`, logs only the count + actor (no PII), returns count. Idempotent (second run returns 0).
- CLI `scripts/purgar_directorio.py`: importable module, entrypoint `python -m scripts.purgar_directorio`; `python3 -c "import scripts.purgar_directorio"` succeeded.

### Independent execution evidence
- Temporary test: a row deactivated **364 days ago** was KEPT; a row deactivated **366 days ago** was physically DELETED (purged == 1). PASS.
- Leap-year/boundary: `2024-02-29 + 1yr → 2025-02-28` (clamp) marked vencido; exactly `2025-09-23 12:00` vs `2026-09-23 12:00` marked vencido (boundary inclusive); 1 second later kept. PASS.
- In-suite: `test_retencion_vencida_limites_y_borde_bisiesto`, `test_desactivacion_registra_fecha_baja_y_reactivacion_la_limpia`, `test_purgar_vencidos_borra_solo_bajas_mayores_a_un_anio`, `test_purgar_vencidos_es_idempotente`, `test_purgar_vencidos_loggea_conteo_sin_pii`, `test_migration_010_fecha_baja.py` (3) and `test_purgar_directorio_script.py` — all green.

### Spec alignment
`specs/employee-directory/spec.md` DIR-002 now lists `fecha_baja`; DIR-007 now defines the retention rule, the `fecha_baja` seal/clear, idempotency, active/recent preservation and audited count. The previously "aspirational / UNTESTED" DIR-007 retention scenario is now IMPLEMENTED and tested. **CONFIRMED FIXED.**

---

## W3 — Incident `PATCH` role scope

### Fix
- `app/routes/incidentes.py:201` adds `alcance: AlcanceDep` to the PATCH handler and passes it to `service.update_incidente(..., alcance=alcance)` (`:228`).
- `app/services/incidente_service.py:364-395` — `update_incidente` now accepts `alcance` and calls `self.get_by_id(incidente_id, alcance=alcance)` **before** any mutation; `get_by_id` raises `EntityNotFoundError` (404) when out of scope (`:144-149`). The post-update read at `:422` also re-applies scope.

### Execution evidence
In-suite `test_incident_visibility.py`, all green:
- `test_no_admin_patch_fuera_de_sector_404_y_no_modifica` — 404 AND `prioridad` remains `media` (re-read with admin scope)
- `test_no_admin_patch_dentro_de_sector_200` — positive control
- `test_admin_patch_fuera_de_sector_200` — admin allowed
- `test_acceso_puntual_sin_empleado_404` — empty scope GET+PATCH = 404 (N1)

### Other by-ID paths (adversarial sweep)
Inventory of all by-ID paths touching incidents (from `docs/openapi.json`):
- `/api/v1/incidentes/{incidente_id}` GET/PATCH → scoped (fixed).
- `/api/v1/clasificaciones/incidente/{incidente_id}` GET → **NOT scoped**.
- `/api/v1/clasificaciones/{log_id}/validar` PATCH → **NOT scoped**.

**NEW FINDING (WARNING, PRE-EXISTING — see below).** `app/routes/clasificaciones.py` depends only on `get_current_user`; `ClasificacionService.validate_payload`/`validate` (`app/services/clasificacion_service.py:120-141`) calls `_incidente_repo.update_fields(log.incidente_id, sector_id=..., requiere_revision_humana=False)` with no `alcance`. Thus any authenticated user (including a non-admin with no directory employee) can read classification history for any incident by ID and reassign any incident's sector — an incident by-ID read/write path that bypasses the c-54 isolation. This file was last modified in `ef656ac` (c-29/c-30/c-32) and was NOT touched by c-54, so it is pre-existing and outside VIS-001's literal "lectura/listado de incidentes" wording, but it defeats the isolation intent and belongs in a follow-up change.

For the `incidentes` router itself, no remaining bypass was found: `POST` creates (no scope needed), `GET /` and `GET /{id}` are scoped, `PATCH /{id}` is now scoped. **CONFIRMED FIXED for the declared scope.**

---

## Nits N1-N3

- **N1 (empty-scope point access GET+PATCH ⇒ 404):** CONFIRMED. `test_acceso_puntual_sin_empleado_404` asserts both verbs return 404 with `NOT_FOUND`.
- **N2 (role does not affect classification):** CONFIRMED. `test_directorio_clasificacion_independiente.py` asserts identical sector/confidence before and after creating `usuario_final`/`operador`/`administrador_directorio` employees, plus a structural regression (`DeterministicClassifier` source does not mention `RolEmpleado` or `directorio_empleado`).
- **N3 (`get_by_user_id` robust to duplicates):** CONFIRMED. `EmpleadoRepository.get_by_user_id` filters `activo IS TRUE`, `order_by(Empleado.id)`, returns `scalars().first()`; `test_get_by_user_id_robusto_ante_duplicados` links two active rows to one user and gets `DUP-1` deterministically.

---

## Regression checks

| Check | Result | Evidence |
|-------|--------|----------|
| Directory stays PLAINTEXT (no blind index / encryption residue) | PASS | `grep` over model/service/repo/schemas/migrations 009-010: no `EncryptedText`, `blind_index`, `email_hash`, `telefono_hash`. Columns are `String`. |
| Fernet incident encryption untouched | PASS | `app/utils/encryption.py` not present in `git show 040f688 --stat`; last change unrelated; file still uses Fernet. |
| Five category strings untouched | PASS | `app/constants.py:18-22` exactly `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas` (no accents, exact casing). |
| `docs/openapi.json` matches code | PASS | `pytest tests/test_openapi_sync.py -v` → 5 passed. |
| Migration chain 001..010 consistent | PASS | All revisions linear `001→...→010`, single head `010`. |
| No uncommitted residue | PASS | `git status --short` empty; temporary adversarial test deleted. |

---

## Test / lint execution (real)

| Command | Result |
|---------|--------|
| `ruff check .` (App/Backend) | `All checks passed!` (exit 0) |
| `pytest -m "not integration"` | **785 passed, 33 deselected, 1 xfailed** in 265.72s |
| `pytest -m integration` | **33 passed, 786 deselected** in 65.51s |
| `pytest tests/test_openapi_sync.py -v` | **5 passed** |
| `openspec validate --strict --changes c-54-directorio-usuarios` | **3 passed, 0 failed** |
| Temporary adversarial file (deleted after run) | 5 passed / 3 failed — the 3 failures are the W1 leaks above (2 incident custom validators + 1 classification validator); the 5 passes are directory telefono/email, incident built-in, purge 364/366, leap clamp |

The single `xfailed` is pre-existing and unrelated (`tests/test_n8n_workflow.py::test_payload_has_no_obvious_pii`, documented C-04 gap).

Regression delta vs the original verify report: offline **765 → 785 passed** (+20 tests from the W1-W3/nit fixes); integration unchanged at 33.

---

## New findings

**NIT-1 (NEW, WARNING, PRE-EXISTING):** Unscoped `clasificaciones` by-incident endpoints (see W3 section). `GET /api/v1/clasificaciones/incidente/{id}` and `PATCH /api/v1/clasificaciones/{log_id}/validar` require only authentication; the PATCH mutates the incident's `sector_id`/`requiere_revision_humana` without applying `alcance`. Not introduced by c-54, but it is the same class of isolation bypass W3 fixed on the incidentes router. Recommend a follow-up change (add the same `alcance` gate or an explicit reviewer role).

**NIT-2 (NEW, SUGGESTION, OPS):** Inactive rows with `fecha_baja IS NULL` are never purged by `retencion_vencida` (returns False for `None`). This is a defensible "can't evaluate ⇒ don't delete" choice, and migration `010` leaves pre-existing inactive rows NULL. Because 009+010 shipped together and only synthetic data exists, impact is currently nil, but any future backfill/import that deactivates rows without sealing `fecha_baja` would make them retention-immortal. Consider a one-time backfill of `fecha_baja` for inactive rows and/or making it NOT NULL for inactive rows at the data layer.

**Unchanged from the original report (not addressed by the fixes, still valid):** N4 — migration `009`/`010` are validated only via SQLite in the suite; the PostgreSQL integration fixtures use `Base.metadata.create_all`, not Alembic. Low priority.

---

## Open gates (by design)

- **Task 7.5 — human review (HIGH): PENDING.** It remains unchecked in `tasks.md:55`. This is an intentional open gate, not a failure: synthetic data only; activating real data (and confirming retention/ARCO policy, role visibility, and absence of a blind-index key) is blocked until the human approval is recorded.
- **Archive order:** `c-52` MUST be archived before `c-53` (both carry the shared `runtime-cost-guard` delta spec). **`c-54` is independent** — it touches only new specs (`employee-directory`, `contact-resolution`, `incident-visibility`). Recommended order: **c-52 → c-53**, then **c-54** (c-54 may technically go at any time, but sequencing it last avoids concurrent edits under `openspec/specs/`).

---

## Verdict

**PASS WITH WARNINGS.**

- **W2 CONFIRMED FIXED**, **W3 CONFIRMED FIXED** (for the declared incidentes scope), **N1/N2/N3 CONFIRMED**.
- **W1 STILL BROKEN (partial)**: `input`/`ctx`/`url` are dropped and the directory PII path is safe, but custom-validator messages retained in `msg` still echo the submitted value on the incident and classification endpoints. This contradicts the fix's global claim and should be closed (drop/neutralize `msg`, and stop interpolating submitted values in schema validators) before considering W1 done.
- One NEW pre-existing scope bypass on the classification endpoints (WARNING) is reported for a follow-up; it does not block c-54, whose own incident router is correctly scoped.
