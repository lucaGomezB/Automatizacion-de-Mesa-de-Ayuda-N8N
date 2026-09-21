# Verification Report — c-44-docs-evaluation-sync

**Change**: `c-44-docs-evaluation-sync`
**Schema / Version**: spec-driven (4/4 planning artifacts complete)
**Mode**: Standard verify (openspec/config.yaml has no `strict_tdd` key; apply executed under Strict TDD — TDD structure inspected as supplementary evidence)
**Verifier**: independent (re-derived from repo + real execution; apply reports not trusted)
**Date**: 2026-09-21

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 22 |
| Tasks complete `[x]` | 22 |
| Tasks incomplete `[ ]` | 0 |

`openspec status --change c-44-docs-evaluation-sync` → `4/4 artifacts complete` (proposal, specs, design, tasks).

---

## Changed-File Scope

Tracked/untracked changes vs. HEAD (working tree):

| Status | Path |
|--------|------|
| M | `docs/operational-guide.md` |
| M | `evaluation/README.md` |
| M | `App/Backend/scripts/export_openapi.py` |
| M | `docs/como_cargar_datos_corpus.md` |
| ?? | `App/Backend/tests/test_docs_evaluation_sync.py` |
| ?? | `openspec/changes/c-44-docs-evaluation-sync/` (`.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`, `specs/evaluation-framework/spec.md`, `specs/project-documentation/spec.md`) |

`git status --porcelain docs/anexo_f_corpus.md docs/Tesis` → **(empty)**. Out-of-scope artifacts untouched. Scope integrity: **CONFIRMED**, no file outside the declared Impact table changed.

---

## Build & Tests Execution (real)

All backend commands run from `App/Backend/`.

**1. Focused module**
```
$ pytest tests/test_docs_evaluation_sync.py -q
12 passed, 1 warning in 21.86s
```

**2. Docs sync trio (c-42 + c-43 + c-44)**
```
$ pytest tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py tests/test_docs_evaluation_sync.py -q
38 passed, 1 warning in 20.68s
```

**3. Offline backend suite**
```
$ pytest -m "not integration" -q
469 passed, 22 deselected, 1 xfailed, 121 warnings in 68.62s
```
No regressions.

**4. OpenSpec strict validation**
```
$ openspec validate --strict --changes c-44-docs-evaluation-sync
- Validating...
✓ change/c-44-docs-evaluation-sync
Totals: 1 passed, 0 failed (1 items)   [exit 0]
```

**5. Evaluation framework suite** (run from `evaluation/`, own `pytest.ini`) — provides runtime evidence for the inherited runner scenarios:
```
$ pytest -q
69 passed in 2.65s
```

**Coverage**: ➖ Not re-measured (change is docs + dev script; no runtime code path introduced).

---

## Independent Reproduction of the Script Bugfix

Not relying on the new test, the fix was re-derived from the repo:

**Bug reproduced against the pre-change script** (`git show HEAD:App/Backend/scripts/export_openapi.py`, run with `JWT_SECRET_KEY` + the other three Settings vars unset, `PYTHONPATH=App/Backend`, cwd without `.env`):
```
ERROR: 1 validation error for Settings
jwt_secret_key
  Field required [type=missing, ...]
EXIT CODE: 1
```

**Post-fix script**, same scrubbed environment, cwd = temp dir with no discoverable `.env`, output to a temp file (`/tmp/opencode/repro_export_openapi.py`):
```
=== CASE 1: JWT_SECRET_KEY absent, cwd without .env ===
exit code: 0
stdout: OpenAPI versión : 3.1.0 | Rutas exportadas: 13
openapi: 3.1.0 | paths: 13

=== CASE 2: external JWT_SECRET_KEY provided ===
exit code: 0
WRAPPER_EXIT 0
JWT_AFTER EXTERNAL-SENTINEL-VALUE

=== RESULT ===
PASS: fix reproduced; external JWT preserved
```
Case 2 uses a `runpy` wrapper that sets `JWT_SECRET_KEY` before the script runs and prints `os.environ` after; the external value is **not overwritten** (the dummy injection is guarded by `if _key not in os.environ`).

---

## Spec Compliance Matrix

Legend: COMPLIANT = a covering test exists and passed; PARTIAL = test exists/passes but covers only part of the scenario; UNTESTED = no test (file content verified statically).

### Delta: `project-documentation` — Requirement: Especificación OpenAPI 3.1 estática generada desde la app

| Scenario | Test | Result |
|----------|------|--------|
| openapi.json es un OpenAPI 3.1 bien formado | `App/Backend/tests/test_openapi_sync.py::test_openapi_file_exists / test_openapi_is_valid_json / test_openapi_version_is_31 / test_openapi_contains_expected_paths` | ✅ COMPLIANT |
| El spec se genera desde la app, no a mano | `App/Backend/tests/test_openapi_sync.py` (regenera `app.openapi()` y compara con el archivo) | ✅ COMPLIANT |
| El script corre con dummies suficientes, sin JWT_SECRET_KEY real | `test_docs_evaluation_sync.py::test_export_openapi_runs_without_jwt_env` (+ reproduction above) | ✅ COMPLIANT |
| El uso documentado del script no referencia la ruta obsoleta | `test_docs_evaluation_sync.py::test_export_script_drops_obsolete_module_path` | ⚠️ PARTIAL (see W-01) |

### Delta: `project-documentation` — Requirement: Anexo G — Guía operativa

| Scenario | Test | Result |
|----------|------|--------|
| Despliegue presenta el comando único como camino recomendado | `test_docs_bootstrap_sync.py::test_guide_documents_single_command_and_cost_gate` | ✅ COMPLIANT |
| Gate de costo y bypass documentados en la guía | `test_docs_bootstrap_sync.py::test_guide_documents_single_command_and_cost_gate` | ✅ COMPLIANT |
| Camino manual permanece documentado | `test_docs_bootstrap_sync.py::test_guide_keeps_manual_path` | ✅ COMPLIANT |
| Sección 1.2 lista JWT_SECRET_KEY | `test_docs_restructure_sync.py::test_guide_env_section_lists_jwt_secret_key` | ✅ COMPLIANT |
| Comandos de la guía usan rutas post-reestructuración | `test_docs_restructure_sync.py::test_stale_path_docs_reference_current_module_path` / `..._do_not_present_obsolete_module_path` (parametrizado) | ✅ COMPLIANT |
| Sección de backup referencia scripts | (none found) | ⚠️ UNTESTED (pre-existing clause; content verified statically — see S-02) |
| Comando manual permanece documentado (backup) | (none found) | ⚠️ UNTESTED (pre-existing clause; static) |
| Sección 8 usa la invocación real del runner | `test_docs_evaluation_sync.py::test_guide_section_8_uses_real_runner_invocation` | ✅ COMPLIANT |
| Sección 8 no referencia el generador de corpus eliminado | `test_docs_evaluation_sync.py::test_guide_section_8_drops_deleted_corpus_generator` | ✅ COMPLIANT |
| Gate de corrida paga documentado en la guía | `test_docs_evaluation_sync.py::test_paid_run_gate_tokens_documented[guide]` | ⚠️ PARTIAL (see W-02) |

### Delta: `evaluation-framework` — Requirement: Runner de evaluación sobre el corpus

| Scenario | Test | Result |
|----------|------|--------|
| Recolección de predicciones por caso | `evaluation/tests/test_run_evaluation.py::test_runner_recolecta_una_prediccion_por_caso` | ✅ COMPLIANT |
| Generación del reporte de métricas | `evaluation/tests/test_run_evaluation.py::test_runner_genera_report_md_con_metricas` | ✅ COMPLIANT |
| Corpus real ausente no rompe el framework | `evaluation/tests/test_run_evaluation.py::test_runner_corpus_real_ausente_falla_claro` | ✅ COMPLIANT |
| Gate de corrida paga documentado junto al comando | `test_docs_evaluation_sync.py::test_paid_run_gate_tokens_documented[README]` + `test_evaluation_readme_keeps_command_and_gemini_key` | ⚠️ PARTIAL (see W-02) |

**Compliance summary**: 13/17 scenarios fully COMPLIANT; 2 PARTIAL (documentation prose clauses not test-asserted but statically verified); 2 UNTESTED pre-existing backup clauses (outside c-44's delta, content statically verified). Every scenario introduced/modified by c-44 is satisfied by the files.

---

## Correctness (Static — Structural Evidence)

| Requirement / claim | Status | Evidence |
|---------------------|--------|----------|
| Guide §8 uses `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` | ✅ | `docs/operational-guide.md:420-423` |
| Guide §8 contains no `python run_evaluation.py` | ✅ | `grep` across guide/README/corpus doc → 0 matches |
| Guide §8 contains no `generate_corpus.py` / no "seed fijo" | ✅ | `grep` → 0 matches; §8.4 replaces the generator with a pointer |
| Guide §8 points to `docs/como_cargar_datos_corpus.md` | ✅ | `docs/operational-guide.md:455-459` |
| Guide §8 documents the paid gate (`--confirm-paid`, `EVALUATION_CONFIRM_PAID`, exit code 2, cost estimate) | ✅ | §8.2 lines 431-446 |
| Legitimate `cd evaluation` for framework tests remains | ✅ | guide §8.3 lines 448-453; README lines 145, 152 — untouched |
| `evaluation/README.md` documents the paid gate next to the run command and `GEMINI_API_KEY` | ✅ | README §"Gate de Corrida Paga" lines 83-99, right after "Comando Único de Corrida"; cross-ref at lines 134-136 |
| `export_openapi.py` declares `JWT_SECRET_KEY` in `_DUMMIES` | ✅ | `App/Backend/scripts/export_openapi.py:56-61` |
| `export_openapi.py` contains no `Gestion_Incidentes` | ✅ | `grep -c` → 0 |
| Docstring `--output` example consistent with real default | ✅ | docstring `--output ../../docs/openapi.json` from `cd App/Backend` = `_DEFAULT_OUTPUT` (`_REPO_ROOT/docs/openapi.json`) |
| `como_cargar_datos_corpus.md` runner block has no `cd evaluation` | ✅ | diff removes only that line; runner block lines 186-189 now correct |
| Runner gate behavior matches documented prose | ✅ | `evaluation/run_evaluation.py`: `CONFIRM_PAID_ENV_VAR = "EVALUATION_CONFIRM_PAID"` (72), `PaidRunNotConfirmedError` (64), `raise SystemExit(2)` (617), `format_cost_estimation` (81) |
| `docs/anexo_f_corpus.md` / `docs/Tesis` untouched | ✅ | `git status --porcelain` empty for both |

The `paths` in `docs/openapi.json` include two top-level `/health` entries in addition to the `/api/v1` routes; the scenario only requires a non-empty `paths` containing `/api/v1` routes, which holds (13 paths).

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 — new test module `test_docs_evaluation_sync.py` reusing `parents[3]` pattern | ✅ Yes | Module created; path/heading/token helpers reused |
| D2 — stable-token asserts + negative control | ✅ Yes | Asserts on commands/tokens only; section isolated by heading |
| D3 — subprocess functional test with scrubbed env + temp cwd | ✅ Yes (superset) | Strips all four Settings vars, not only `JWT_SECRET_KEY`; strengthened, not weakened. Independently reproduced |
| D4 — §8.3 generator subsection removed, replaced by pointer | ✅ Yes | Generator block removed; pointer lives at §8.4 after renumbering |
| D5 — gate documented in both guide §8 and `evaluation/README.md` | ✅ Yes | Guide §8.2 and README §"Gate de Corrida Paga" |
| D6 — `JWT_SECRET_KEY` dummy with stable dummy value | ✅ Yes | `"ci-dummy-jwt-secret-key-for-testing-only"` |
| D7 — correct docstring, don't rewrite | ✅ Yes | Only erroneous lines changed (`Gestion_Incidentes` → `App/Backend`, `--output`, sys.path comment) |

Deviation: subsection renumbering (gate is §8.2; tests moved to §8.3; corpus pointer §8.4). Consistent with D4's intent; the test that excludes `cd evaluation` from runner blocks does not rely on the subsection number, so it remains valid.

---

## Test Quality Inspection (`test_docs_evaluation_sync.py`)

- No tautologies (`assert True`, self-referential asserts) and no ghost loops: every `for` loop iterates a collection that is asserted non-empty first (`runner_blocks`), or filters `os.environ`.
- `read_dummies_block()` regex-isolates the `_DUMMIES` dict body, so a stray `JWT_SECRET_KEY` mention elsewhere cannot make the assert pass.
- Negative controls are real: absence of `python run_evaluation.py`, absence of `cd evaluation` inside runner blocks, absence of `generate_corpus.py`/`seed fijo`, absence of `Gestion_Incidentes`.
- The functional test genuinely exercises the missing-dummy path: env is rebuilt from `os.environ` minus the four Settings vars, `cwd` is pytest `tmp_path` (no `.env`), output to a temp file. It is not trivially green — the pre-change script exits 1 under exactly these conditions (reproduced above), while the post-change script exits 0 with a valid OpenAPI 3.1 document (13 paths).
- TDD structure is visible: RED/GREEN/TRIANGULATE/REFACTOR cycles documented in `tasks.md` §1-6 and mirrored in the test grouping; task 7 closes the `como_cargar_datos_corpus.md` drift with its own RED/GREEN cycle.

---

## Issues Found

**CRITICAL** (must fix before archive):
None.

**WARNING** (should fix; non-blocking here):
- **W-01** — Scenario "El uso documentado del script no referencia la ruta obsoleta" is PARTIAL. The test asserts only the absence of `Gestion_Incidentes`; the second clause ("su ejemplo de `--output` es consistente con la salida por defecto real") is verified statically, not asserted. Evidence: `test_export_script_drops_obsolete_module_path` only checks `TOKEN_OBSOLETE_MODULE`. Static check confirms the example is correct. Impact: low; a future docstring regression of the `--output` example would not be caught.
- **W-02** — Gate scenarios (guide and README) are PARTIAL. Tests assert the tokens `confirm-paid` / `EVALUATION_CONFIRM_PAID` (plus command and `GEMINI_API_KEY`), but not the prose clauses "aborta con código de salida 2" and "imprime una estimación de costo". Those clauses are present in the files (guide §8.2 lines 444-446; README lines 97-99) and match runner behavior (`run_evaluation.py:617`, `format_cost_estimation`), but a regression deleting that prose would not turn a test red. This is an intentional consequence of design D2 (stable-token asserts, not sentence snapshots).

**SUGGESTION** (nice to have):
- **S-01** — `test_export_openapi_respects_existing_jwt_env` only asserts exit code 0 with `JWT_SECRET_KEY` present; it does not directly assert the external value is preserved (the script's guard makes both outcomes exit 0). A wrapper or env-probe assert would make the "dummy no pisa el entorno" claim test-verified. Independently reproduced here (preserved).
- **S-02** — Backup scenarios ("Sección de backup referencia scripts", "Comando manual permanece documentado") have no test. They are pre-existing clauses inherited by the MODIFIED requirement, were already untested before c-44, and are outside this change's delta. Content verified statically (`docs/operational-guide.md:240-285`).

---

## Verdict

**READY TO ARCHIVE** (PASS WITH WARNINGS)

All c-44 success criteria and all acquired/modified scenarios are satisfied with real execution evidence: the script bug is independently reproduced and fixed, both documentation drifts are closed, the offline suite is green (469 passed), the three documentation-sync modules pass (38), the evaluation framework passes (69), and strict OpenSpec validation passes. Two WARNINGS are test-coverage partials (prose clauses not asserted) that are non-blocking and consistent with the change's stated design; no CRITICAL defects, no scope violations, no out-of-scope files touched.

**Recommended next action**: proceed to archive (`/opsx:archive c-44-docs-evaluation-sync`). Optionally fold W-01/W-02 and S-01 into a follow-up hardening change, not this one.