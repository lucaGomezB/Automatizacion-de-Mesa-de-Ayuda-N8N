# Verification Report — c-46-telefonia-ingreso-sellado

**Change**: `c-46-telefonia-ingreso-sellado`
**Spec**: `N8N-TIMING-003` (delta `specs/n8n-workflow/spec.md`)
**Mode**: Strict TDD (orchestrator-injected; test runner available)
**Verifier**: independent re-verification (apply report NOT trusted)
**Date**: 2026-09-22

---

## Verdict

**PASS WITH WARNINGS — archivable, no blockers.**

The implementation genuinely satisfies the five spec scenarios at the structural
level. RED→GREEN was independently reproduced against the pre-change workflow.
The backend is untouched. Two non-blocking warnings (residual `.item` in an
out-of-scope node; no runtime harness for `.first()`) do not block archive.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 15 |
| Tasks complete | 13 |
| Tasks incomplete | 2 (5.2, 5.3) |

Incomplete tasks: `5.2` and `5.3` — manual live-N8N verifications, DELIBERATELY
left pending by human decision and documented in `tasks.md` and the guide. Not a
blocker by the accepted-limitations contract.

---

## Build & Tests Execution

**Build**: ➖ Not applicable (workflow JSON + tests + markdown only; no Python
source under `App/Backend/app/` changed). `n8n/workflow.json` parses as valid
JSON (`json.load` OK).

**Tests** (all commands executed from `App/Backend`):

| Command | Result |
|---------|--------|
| `pytest tests/test_n8n_workflow.py -q` | 134 passed, 1 xfailed (135 collected, exit 0) |
| `pytest tests/test_n8n_workflow.py -q -k "c46"` | 5 passed, exit 0 |
| `pytest -m "not integration" -q` | 550 passed, 25 deselected, 1 xfailed, exit 0 |
| `pytest tests/test_openapi_sync.py -q` | 5 passed, exit 0 |
| `openspec validate --strict --changes c-46-telefonia-ingreso-sellado` | 1 passed, 0 failed |
| `ruff check tests/test_n8n_workflow.py` | All checks passed |

**Independent RED evidence** (adversarial): swapped `git show HEAD:n8n/workflow.json`
into place, ran `pytest -k c46`:

```
4 failed, 1 passed, 130 deselected
FAILED test_c46_validador_referencia_sello_por_primer_item
FAILED test_c46_terminal_referencia_sello_por_primer_item
FAILED test_c46_ausencia_sello_no_se_silencia
FAILED test_c46_sello_ausente_deriva_revision_conservando_ticket
```

Working tree restored and byte-verified identical afterwards. This reproduces the
apply report's RED numbers and proves the tests are NOT vacuous.

**Coverage**: ➖ Not meaningful — the changed "product" files are `n8n/workflow.json`
and `docs/n8n-workflow-guide.md` (non-Python). No Python source changed, so line
coverage adds no signal for this change.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ Partial | Apply memory `#972` records baseline/RED/GREEN counts but no formal "TDD Cycle Evidence" table |
| All tasks have tests | ✅ | 4 code tasks (1.1–1.3) map to test functions; 1.4/2.x regression-covered |
| RED confirmed (tests exist and fail pre-change) | ✅ | 4/5 new tests fail against HEAD workflow (reproduced by verifier) |
| GREEN confirmed (tests pass post-change) | ✅ | 5/5 pass on current workflow |
| Triangulation adequate | ✅ | 5 distinct test cases, one per spec scenario, distinct assertions |
| Safety Net for modified files | ✅ | Baseline 129 passed / 1 xfailed recorded; full suite green after |

**TDD Compliance**: 5/6 checks clean, 1 partial. The absent formal table is a
process-format gap only; the underlying RED→GREEN evidence is independently
reproducible. Not classified CRITICAL.

---

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit / structural (JSON inspection) | 5 | `tests/test_n8n_workflow.py` | pytest 8.3 |
| Integration (runtime N8N) | 0 | — | not available (accepted) |
| E2E | 0 | — | not available (accepted) |
| **Total** | **5** | **1** | |

All C-46 evidence is structural. No runtime harness exists in CI (documented,
accepted limitation).

---

## Spec Compliance Matrix

| # | Scenario | Evidence (file:line) | Result |
|---|----------|----------------------|--------|
| 1 | El validador referencia el sello por el primer item | `n8n/workflow.json:323` node `Se verifica lo que trajo la IA` jsCode uses `$('Sellar ingreso telefonia').first().json.ingresado_en`; no `.item`. Test `tests/test_n8n_workflow.py:3468` PASSED | ✅ COMPLIANT (structural) |
| 2 | El terminal referencia el sello por el primer item | `n8n/workflow.json:655` node `Derivar a revision humana` jsCode uses `.first().json`; no `.item`. Test `test_n8n_workflow.py:3487` PASSED | ✅ COMPLIANT (structural) |
| 3 | La ausencia del sello no se silencia | Validador catch emits `console.warn('[N8N][N8N-TIMING-003] ingreso_sellado_ausente', ...)` (`workflow.json:323`), sets marker + `revision_forzada`; no `return null` anywhere in code nodes (whole-workflow scan clean). Test `test_n8n_workflow.py:3512` PASSED | ✅ COMPLIANT (structural) |
| 4 | Sello ausente deriva a revisión humana conservando el ticket | Validador sets `requiere_revision_humana`/`revision_forzada` in BOTH branches (`workflow.json:323`); normalizer propagates marker + revision (`workflow.json:336`); gate `Entrada valida` combinator `"or"` includes `revision_forzada == true`; terminal reaches `HTTP POST a MTM-SRU` via `_connections_reachable`. Test `test_n8n_workflow.py:3536` PASSED | ✅ COMPLIANT (structural) — runtime ticket creation not proven (accepted) |
| 5 | El contrato de persistencia del backend no cambia | POST body `ingresado_en = "={{ $('Normalizar entrada del incidente').item.json.ingresado_en }}"`, marker absent from body; `IncidenteCreate.ingresado_en: datetime \| None = None` (`app/schemas/incidente.py:136`). Test `test_n8n_workflow.py:3572` PASSED | ✅ COMPLIANT (structural) |

**Compliance summary**: 5/5 scenarios compliant (all structural; behavioral
runtime verification is the accepted limitation).

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| `.first()` recovery in validador | ✅ Implemented | `workflow.json:323`, `.item` absent |
| `.first()` recovery in terminal | ✅ Implemented | `workflow.json:655`, `.item` absent |
| WARN structured on seal absence | ✅ Implemented | `console.warn` with event `ingreso_sellado_ausente` in both nodes |
| Human-review marker in BOTH validador branches | ✅ Implemented | `resultadoInvalido()` and valid branch both set `revision_forzada`/`ingreso_sellado_ausente`/`requiere_revision_humana` |
| Never aborts / never silent null | ✅ Implemented | No `throw`; no `return null` in any code node |
| Normalizer propagates marker without leak into POST | ✅ Implemented | marker propagated at `workflow.json:336`; body uses explicit fields (no spread), marker absent |
| POST `ingresado_en` by expression, null-tolerant | ✅ Implemented | `={{ $('Normalizar entrada del incidente').item.json.ingresado_en }}` |
| Backend contract unchanged | ✅ Verified | `IncidenteCreate.ingresado_en` nullable; `git diff --stat` shows no `App/Backend/app/` or `alembic/` changes |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 — `.first()` instead of `.item` in both nodes | ✅ Yes | Confirmed by code + tests |
| D2 — Seal absence → WARN + forced review, ticket still created | ✅ Yes | Marker + both branches; gate OR routes by `revision_forzada` |
| D3 — Terminal same correction, keeps `requiere_revision_humana=true` | ✅ Yes | `workflow.json:655` |
| D4 — Backend contract untouched | ✅ Yes | No app/alembic diff; schema nullable |
| D5 — Extended structural tests (regression guard, not runtime) | ✅ Yes | 5 tests, one per scenario |

---

## Assertion Quality Audit

- No tautologies (`assert True`, etc.) found.
- No ghost loops, no smoke-only assertions, no implementation-detail coupling.
- Assertions exercise the real artifact (parsed `workflow.json` + real schema class).
- Two assertions are negative (`SELLO_ITEM_REF not in code`, `"return null" not in code`);
  both were independently RED against the old workflow, so they are meaningful.

**Assertion quality**: ✅ All assertions verify real behavior.

---

## Docs Check

- `docs/n8n-workflow-guide.md:541` declares "Verifica 135 propiedades estructurales".
- Suite has exactly 135 `^def test_` functions; pytest collects 135 items.
- `test_c40_guide_test_count_matches_suite` PASSED.
- New C-46 guide section at `docs/n8n-workflow-guide.md:217` documents `.first()`,
  WARN + review behavior, the internal-marker caveat, and the runtime caveat.

## Scope Discipline

`git diff --stat` = exactly 3 files: `n8n/workflow.json`, `App/Backend/tests/test_n8n_workflow.py`,
`docs/n8n-workflow-guide.md`. Confirmed untouched:
- `Guard de costo` node (c-47) — unchanged (pre-existing content intact).
- `IncidenteListItem` (c-48) — no schema change.
- `evaluation/` (c-49/c-50) — no change.

---

## Issues Found

**CRITICAL** (must fix before archive):
None.

**WARNING** (should fix / track):
1. **Residual `.item` on the seal in `Guard de costo`** — `n8n/workflow.json:779`
   `caller: "={{ $('Sellar ingreso telefonia').item.json.From || ... }}"`. This is the
   SAME pairedItem fragility that C-46 fixed, but the node is explicitly out of scope
   (c-47 owns `Guard de costo`). Pre-existing, not introduced by C-46. Residual risk:
   the cost-guard `caller` field may resolve null when pairing breaks. Track in c-47.
2. **Scenario 5 test was never RED** — `test_c46_contrato_persistencia_backend_sin_cambios`
   passed against the pre-change workflow (contract guard). It is a legitimate,
   meaningful guard (expression, no marker leak, nullable schema) but does not
   demonstrate a RED→GREEN transition. Informational, not a defect.
3. **No runtime proof of `.first()`** — the suite inspects JSON, it does not execute
   N8N JS. That `.first()` resolves at runtime and that a ticket is actually created
   on seal-absence is unproven until tasks 5.2/5.3 are performed live. Accepted
   limitation; residual risk remains.

**SUGGESTION** (nice to have):
1. Scenario 4's ticket-creation claim is verified via static propagation + graph
   connectivity (`_connections_reachable`), not execution. A future N8N runtime
   harness (c-47/phase scope) would close this gap.
2. The normalizer retains `ingresado_en: item.json.ingresado_en || null`. Acceptable
   because the absence signal is emitted upstream and the marker/review are
   propagated (not a silent swallow). No action required.

---

## Blockers Before Archive

None. Verdict **PASS WITH WARNINGS** — the change may be archived; warnings 1–3
should be tracked (warning 1 is c-47 scope; warnings 2–3 are informational/accepted).