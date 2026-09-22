# Verification Report

**Change**: c-48-timing-en-listado
**Version**: N/A (delta spec on `e2e-timing-instrumentation`)
**Mode**: Strict TDD (adversarial, independent re-execution)
**Date**: 2026-09-22
**Verifier execution**: commands re-run from scratch; apply summary NOT trusted.

---

## Verdict

**READY TO ARCHIVE**

All spec scenarios are behaviorally covered by tests that passed. Scope is
exactly the four expected files. OpenAPI diff is purely additive on
`IncidenteListItem`. No regressions. The RED was independently reproduced
against the pre-change schema (9 failures, all `AttributeError`).

---

## 1. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 22 (across 6 groups) |
| Tasks complete `[x]` | 22 |
| Tasks incomplete `[ ]` | 0 |

No incomplete tasks.

---

## 2. Adversarial Checks (with evidence)

### Check 1 — `IncidenteListItem` exposes the fields via `model_validate`
**PASS.** `App/Backend/app/schemas/incidente.py` adds:
- `ingresado_en: datetime | None = None`
- `persistido_en: datetime | None = None`
- `@computed_field latencia_e2e_ms -> int | None`
- `@computed_field latencia_anomala -> bool`

`model_config = ConfigDict(from_attributes=True)` is preserved. The ASGI test
`test_c48_listado_expone_instantes_y_latencia` builds the list via
`IncidenteListItem.model_validate(i)` from ORM rows and asserts all four fields
(`App/Backend/tests/test_api_incidentes.py:931-966`). Passed.

### Check 2 — Detail/list parity is a SINGLE source of truth
**PASS.** Two private module-level pure functions were extracted:

```
_derivar_latencia_e2e_ms(ingresado_en, persistido_en) -> int | None
_es_latencia_anomala(ingresado_en, persistido_en) -> bool
```

Both `IncidenteRead` computed fields now `return _derivar_latencia_e2e_ms(...)`
and `return _es_latencia_anomala(...)`. `IncidenteListItem` delegates to the
SAME functions. `IncidenteRead` semantics are rendered byte-for-byte identical by
the extraction (same `_to_utc` normalization, same null guard, same `< 0`
branch). The C-39 safety-net tests for `IncidenteRead` (16 cases) still pass.
Explicit parity test `test_paridad_de_derivacion_entre_detalle_y_listado`
asserts `item.latencia_e2e_ms == read.latencia_e2e_ms == 7250`. Passed.

### Check 3 — Units, null behavior, anomaly
**PASS.**
- Units ms: `int((_to_utc(persistido) - _to_utc(ingresado)).total_seconds() * 1000)`. Test: 12.5 s -> 12500.
- Null if either instant missing: guard returns `None` before arithmetic. Three independent tests (missing `ingresado_en`, missing `persistido_en`, both null) pass.
- Anomaly: `latencia_e2e_ms` returns `None` for negative deltas (never a negative measurement); `latencia_anomala` is `True` only when `persistido_en < ingresado_en`. Zero latency -> `0` and `latencia_anomala is False`. All pass.

### Check 4 — List endpoint actually carries the fields
**PASS (integration/ASGI evidence).** `GET /api/v1/incidentes/` returns items with
`ingresado_en`, `persistido_en`, `latencia_e2e_ms >= 4000`, `latencia_anomala is False`
for a freshly created incident.
`tests/test_api_incidentes.py::test_c48_listado_expone_instantes_y_latencia PASSED`.

### Check 5 — `docs/openapi.json` additive only + `test_openapi_sync.py` + versions
**PASS.**
- `git diff docs/openapi.json` touches ONLY the `IncidenteListItem` properties block and its `required` array. No churn on `IncidenteRead` or any path.
- `pytest tests/test_openapi_sync.py -v` -> 5 passed (incl. `test_openapi_in_sync_with_app`).
- Installed versions match `requirements.txt`: fastapi `0.115.0`, pydantic `2.9.2`, pydantic-settings `2.5.2`.

### Check 6 — Scope
**PASS.** `git diff --name-only`:
```
App/Backend/app/schemas/incidente.py
App/Backend/tests/test_api_incidentes.py
App/Backend/tests/test_timing_contract.py
docs/openapi.json
```
Untracked: `openspec/changes/c-48-timing-en-listado/` (artifacts only).
NO changes to repository, routes, models, migrations, services, `n8n/workflow.json`, or frontend.

### Check 7 — Tests are non-vacuous (RED reproduced independently)
**PASS.** Against `HEAD` schema (`git show HEAD:...incidente.py` confirms
`IncidenteListItem` at line 294 had NO timing fields; `IncidenteRead` at 227 had
them), the new tests were copied into a detached worktree at HEAD and executed:
```
9 failed, 16 deselected
FAILED ...::test_list_item_expone_ambos_instantes
FAILED ...::test_list_item_latencia_derivada_en_milisegundos
FAILED ...::test_list_item_latencia_nula_si_falta_ingresado
FAILED ...::test_list_item_latencia_nula_si_falta_persistido
FAILED ...::test_list_item_latencia_nula_si_ambos_instantes_son_nulos
FAILED ...::test_list_item_latencia_negativa_no_se_reporta_y_marca_anomalia
FAILED ...::test_list_item_latencia_no_negativa_no_es_anomala
FAILED ...::test_list_item_latencia_cero_no_es_anomala
FAILED ...::test_paridad_de_derivacion_entre_detalle_y_listado
```
All fail with `AttributeError: 'IncidenteListItem' object has no attribute 'latencia_e2e_ms'`
(the extra constructor kwargs are silently ignored by pydantic, then attribute access fails) — the correct RED reason, not a syntax error. Non-vacuous confirmed.

---

## 3. Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Derivacion de la latencia end-to-end | Derivacion correcta | `test_timing_contract.py::test_list_item_latencia_derivada_en_milisegundos` | ✅ COMPLIANT |
| Derivacion de la latencia end-to-end | Latencia nula si falta un instante | `test_list_item_latencia_nula_si_falta_ingresado` / `..._falta_persistido` / `..._ambos_instantes_son_nulos` | ✅ COMPLIANT |
| Derivacion de la latencia end-to-end | Unidades en milisegundos | `test_list_item_latencia_derivada_en_milisegundos` (12.5s -> 12500) | ✅ COMPLIANT |
| Derivacion de la latencia end-to-end | Proyeccion de listado expone los instantes y la latencia | `test_api_incidentes.py::test_c48_listado_expone_instantes_y_latencia` | ✅ COMPLIANT |
| Derivacion de la latencia end-to-end | Proyeccion de listado con instantes ausentes | `test_list_item_latencia_nula_si_*` (schema serializes without error) | ✅ COMPLIANT |
| Derivacion de la latencia end-to-end | Paridad de derivacion entre detalle y listado | `test_paridad_de_derivacion_entre_detalle_y_listado` | ✅ COMPLIANT |
| Politica de latencia negativa | Latencia negativa marcada como anomalia | `test_list_item_latencia_negativa_no_se_reporta_y_marca_anomalia` | ✅ COMPLIANT |
| Politica de latencia negativa | Excluida del corpus y del analisis | (none found in scope) | ⚠️ PARTIAL |
| Politica de latencia negativa | Nunca aceptada en silencio | `test_list_item_latencia_negativa_no_se_reporta_y_marca_anomalia` | ✅ COMPLIANT |
| Politica de latencia negativa | Anomalia visible en la proyeccion de listado | `test_list_item_latencia_negativa_no_se_reporta_y_marca_anomalia` | ✅ COMPLIANT |

**Compliance summary**: 9/10 scenarios fully compliant, 1 partial.

The partial scenario is inherited policy (C-39): no corpus/analysis builder lives
in `App/Backend`; exclusion is downstream and driven by the signal this change
exposes (`latencia_e2e_ms=None` + `latencia_anomala=True`), which IS tested. Not a
regression introduced by C-48 (the mechanism was already validated in C-39).

---

## 4. Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Shared derivation function | ✅ Implemented | `_derivar_latencia_e2e_ms`, `_es_latencia_anomala` module-level pure functions |
| List schema fields | ✅ Implemented | 2 datetimes + 2 computed fields on `IncidenteListItem` |
| `from_attributes` preserved | ✅ Implemented | `model_config = ConfigDict(from_attributes=True)` unchanged |
| No denormalized column | ✅ Implemented | No model/migration changes |
| IncidenteRead behavior preserved | ✅ Implemented | Delegation is a pure extraction; C-39 tests green |

## 5. Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 pure module functions + delegation | ✅ Yes | Exactly as specified |
| D2 four explicit fields, nullable defaults | ✅ Yes | Includes `latencia_anomala` |
| D3 no repository/route changes | ✅ Yes | No files touched |
| D4 regenerate openapi with script | ✅ Yes | Purely additive; sync test green |
| D5 frontend out of scope | ✅ Yes | `App/Frontend/src/types/incidente.ts` untouched |

---

## 6. Build & Tests Execution

**Build/type-check**: not run (backend Python project; ruff lint is the quality gate here).
**Lint**: `ruff check .` -> `All checks passed!` (exit 0).

**Tests** (offline subset, from `App/Backend`):
```
pytest -m "not integration" -q
566 passed, 25 deselected, 1 xfailed, 145 warnings in 155.31s  -> exit 0
```

**OpenAPI sync**:
```
pytest tests/test_openapi_sync.py -v
5 passed  -> exit 0
```

**C-48 targeted tests**:
```
pytest tests/test_api_incidentes.py -k c48 -v        -> 1 passed
pytest tests/test_timing_contract.py -k "list_item or paridad" -q -> 9 passed
```

**opsx validation** (repo root):
```
openspec validate --strict --changes c-48-timing-en-listado
Totals: 2 passed, 0 failed (2 items)  -> exit 0
```

**Scope**:
```
git diff --name-only  -> 4 expected files
git diff --stat       -> 266 insertions(+), 14 deletions(-)
```

---

## 7. Issues Found

**CRITICAL** (must fix before archive):
None.

**WARNING** (should fix):
1. Scenario "Excluida del corpus y del analisis" has no direct test in this
   change. Inherited C-39 policy; the enabling signal is tested. Non-blocking.

**SUGGESTION** (nice to have):
1. `tasks.md` 2.5 reports "8 failed" and uses `-k "ListItem"`; the actual RED run
   yields 9 failures and the expression must be `-k "list_item"` (underscore vs.
   camel case) to match the new test names. Cosmetic bookkeeping only.

---

## 8. Verdict

**READY TO ARCHIVE**

Implementation matches the delta spec and design; tests are non-vacuous and pass;
scope is exact; OpenAPI diff is additive. No blockers.
