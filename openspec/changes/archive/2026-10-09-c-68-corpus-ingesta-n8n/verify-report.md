# Verification Report — c-68-corpus-ingesta-n8n

**Change**: c-68-corpus-ingesta-n8n
**Capability**: corpus-n8n-ingest
**Version**: N/A (delta spec)
**Mode**: Strict TDD (active per orchestrator injection)
**Governance**: MEDIO
**Verified**: 2026-10-08
**Verifier**: sdd-verify (independent execution)

The real N8N ingestion run ran on 2026-10-02 in a prior session and CANNOT be re-executed here (no live N8N/inbox). This report independently verifies every REPRODUCIBLE part and judges the sufficiency of the documented run as evidence.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 63 |
| Tasks complete `[x]` | 63 |
| Tasks incomplete `[ ]` | 0 |

All 63 tasks are marked `[x]`. Tasks that depend on the past real run (0.8, 6.2, 6.3, 6.4, 6.6) carry explicit dated evidence and are judged below (see "Evidence Quality for the Past Real Run"). No task is marked done with zero evidence; however, tasks 6.1/6.5 embed a now-stale expected output (see SUGGESTION-1).

---

## Build & Tests Execution

**Build / lint** (`ruff check ingest_via_n8n.py test_ingest_via_n8n.py`): PASS

```
All checks passed!
```

**c-68 harness suite** (`cd scripts/corpus_ingest; pytest -q test_ingest_via_n8n.py`): 86 passed

```
86 passed in 2.80s
```

**Full corpus_ingest dir** (`cd scripts/corpus_ingest; pytest -q`): 160 passed, 1 failed

```
FAILED test_pseudonymize_corpus.py::test_no_pii_produces_zero_counts_and_unchanged_text
1 failed, 160 passed in 3.82s
```

The single failure is NOT c-68: it is caused by archived change `c-73-pseudonimizacion-tarjeta` (2026-10-07), which added the `tarjeta` category to the backend pseudonymizer (`App/Backend/app/utils/pseudonymizer.py`). The script-level test (from the c-68 era) still expects the four original categories (`email/telefono/host/persona`). It is a pre-existing cross-change regression at HEAD, unrelated to the ingestion harness. See WARNING-3.

**Dry-run** (`python3 scripts/corpus_ingest/ingest_via_n8n.py --dry-run`): exit 0

```
Casos en el corpus: 200 | seleccionados: 200
  canal 'correo': 66
  canal 'telefono': 81
  canal 'web': 53
DRY-RUN: ingesta=119 telefono_omitido=81 sin_mapear=0 pendientes_nulos=0. No se ejecuto red ni escritura.
```

`pendientes_nulos=0` reflects the CURRENT corpus (200/200 complete). Note: the task prompt expected only the counts (`correo=66 web=53 telefono=81 ingesta=119 telefono_omitido=81`); those match exactly.

**Dry-run side effects**: none. MD5 of every `data/*.json`, `data/*.csv`, `data/*.xlsx` was captured before and after; `diff` shows NO DATA CHANGES. (`data/` is gitignored, so `git status` alone cannot prove this — hash comparison is the real evidence.)

**Evaluation** (`cd evaluation; pytest -q`): 118 passed, exit 0, no `CorpusError`

```
118 passed in 6.82s
```

**Backend regression** (`cd App/Backend; pytest -m "not integration" -q`): 1217 passed, 42 deselected, 1 xfailed, exit 0

```
1217 passed, 42 deselected, 1 xfailed, 331 warnings in 249.82s
```

**Working tree** (`git status --porcelain`): only `openspec/changes/c-68-corpus-ingesta-n8n/tasks.md` modified. NO changes under `App/**`. Independent confirmation: the four c-68 commits (69b5328, 1d32538, 3840246, 24ab238) touch ONLY `scripts/corpus_ingest/{ingest_via_n8n.py,test_ingest_via_n8n.py,README.md}`, `docs/como_cargar_datos_corpus.md`, `n8n/workflow.json`, `.gitignore`, and the change's `tasks.md`. Zero `App/**` files.

**OpenSpec validation** (`openspec validate c-68-corpus-ingesta-n8n --strict`): valid, exit 0

```
Change 'c-68-corpus-ingesta-n8n' is valid
```

---

## TDD Compliance (Strict TDD Mode)

There is NO standalone `apply-progress` artifact with a tabular "TDD Cycle Evidence". In this project's openspec convention the TDD evidence is embedded inline in `tasks.md` as RED/GREEN/TRIANGULATE/REFACTOR annotations for every code task (1.1–1.15, 2.1–2.4, 3.1–3.11, 4.1–4.11). That inline evidence is cross-referenced against the actual execution below.

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Inline RED/GREEN/TRIANGULATE/REFACTOR per code task in `tasks.md` (no separate apply-progress table) |
| All tasks have tests | ✅ | `test_ingest_via_n8n.py` (86 tests) covers every pure/behavioral code task |
| RED confirmed (tests exist) | ✅ | 86 tests exist and collect |
| GREEN confirmed (tests pass) | ✅ | 86/86 passed on independent execution |
| Triangulation adequate | ✅ | Multiple cases per behavior: 6 anomaly-derivation tests, 5 CSV/4 XLSX preservation tests, 9 sidecar-merge tests, 3 confirmation-separation tests |
| Safety Net for modified files | ✅ | `tasks.md` 0.6 records the pre-change baseline; new files (not modified) for the harness |

**TDD Compliance**: 6/6 checks passed (format deviation noted as SUGGESTION-3).

---

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 86 | 1 (`test_ingest_via_n8n.py`) | pytest 8.3.3 |
| Integration | 0 | 0 | not applicable (I/O injectable/mocked; `# pragma: no cover - I/O`) |
| E2E | 0 | 0 | real N8N run cannot be re-executed here |
| **Total** | **86** | **1** | |

The design deliberately keeps the harness at the unit layer by injecting HTTP/SMTP/IMAP transports; the live end-to-end path is covered only by the (non-reproducible) 2026-10-02 run.

---

## Changed File Coverage

```
Name                Stmts   Miss  Cover   Missing
ingest_via_n8n.py     622     47    92%   122,124,127,129,236,263,284,292,411,419,554,638,682,693,696,724,
                                          781,801-802,883-893,959-960,962,1020-1021,1023,1032,1035,1063,
                                          1102-1103,1189-1190,1202,1236-1242,1259-1264,1273,1279,1285
TOTAL                 622     47    92%
```

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `scripts/corpus_ingest/ingest_via_n8n.py` | 92% | n/a | real I/O (`_send_via_smtp`, `_fetch_confirmation_messages`), CLI branches, and the missing-credentials guard (1236-1242) | ✅ Acceptable |

**Average changed file coverage**: 92% (>= 80%). Uncovered lines are dominated by intentional `# pragma: no cover - I/O` and one untested guard branch (see WARNING-1).

---

## Assertion Quality

Scanned `test_ingest_via_n8n.py` (236 assertions, 86 tests). No tautologies (`assert True`, `1 == 1`), no ghost loops, no assertion-free tests. Type-corroborating checks (`is not None`, e.g. `observer is not None`) always appear alongside behavioral/value assertions in the same test. Mock/injection helpers are used to drive real production functions; assertion count vastly exceeds mock plumbing.

**Assertion quality**: ✅ All assertions verify real behavior.

---

## Quality Metrics

**Linter**: ✅ ruff — `All checks passed!` on the changed files
**Type Checker**: ➖ Not applicable (script is plain Python; no mypy config for `scripts/`)
**Secret scan**: ✅ No literal secrets in `ingest_via_n8n.py`; `n8n/workflow.json` retains `"active": false` and `REPLACE_WITH_*` placeholders (no real credentials committed)

---

## Corpus State (independently measured)

`data/corpus_evaluacion_pseudonimizado.json` = 200/200 with numeric `tiempo_automatizado_s`, 0 nulls:

| `canal_origen` | with value / total |
|----------------|--------------------|
| `correo electrónico` | 66 / 66 |
| `formulario web` | 53 / 53 |
| `llamada telefónica` | 81 / 81 |
| **Total** | **200 / 200** |

Range observed: min 0.525 s, max 65.834 s. The CSV twin (`data/Corpus Tesis - Hoja 1.csv`) and XLSX (`data/Corpus Tesis.xlsx`) both expose the same 10 columns — `TIempo de Registro Automatico (Segundos)`, `Latencia e2e (ms)`, `Tiempo pipeline (s)`, `Tiempo espera (s)` — with values filled 53/53 web, 66/66 correo, 81/81 teléfono (teléfono `Tiempo espera (s)` blank by design, no SMTP wait). Sample R001 (correo): auto=21.009, lat=3721 ms, pipeline=3.721, espera=17.288 (3.721 + 17.288 = 21.009, consistent).

**Sidecar `data/corpus_resultados_n8n.json`**: only 4 cases (R001, R004, R010, R012), 0 descriptions, full traceability fields present. This is the documented consequence of the overwrite bug fixed in task 4.11 (the sidecar used to be rewritten per run; a 3-case re-measure destroyed the 119-case trace). The corpus itself preserves the measured values; the sidecar now merges by `case_id` going forward. See WARNING-2.

---

## Spec Compliance Matrix (behavioral validation)

27 scenarios across 8 requirements. Status uses actual execution results (86/86 passed) plus integration evidence where noted.

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Ingesta por flujo N8N real | Ingesta web por webhook | `test_ingest_web_posts_to_webhook_and_reads_detail` | ✅ COMPLIANT |
| Ingesta por flujo N8N real | Ingesta correo por buzón dedicado | `test_ingest_email_correlates_exact_and_derives_metric` | ✅ COMPLIANT |
| Ingesta por flujo N8N real | Teléfono fuera de alcance | `test_dry_run_reports_counts_without_writing`, `test_dry_run_does_not_touch_data_files` | ✅ COMPLIANT |
| Derivación de la métrica híbrida | Componentes derivados por caso | `test_derive_metric_pipeline_espera_e2e_sum` | ✅ COMPLIANT |
| Derivación de la métrica híbrida | Correo incluye espera del poller | `test_derive_metric_email_includes_poller_wait`, `test_tiempo_automatizado_is_e2e_for_web_and_correo` | ✅ COMPLIANT |
| Derivación de la métrica híbrida | Comportamiento asincrónico | `test_derive_metric_null_latency_is_anomalous`, `test_derive_metric_non_positive_e2e_is_anomalous` | ✅ COMPLIANT |
| Escritura en el corpus de registro | Columnas del corpus actualizadas | `test_write_csv_fills_auto_latency_and_decomposition_columns`, `test_write_xlsx_fills_columns_and_is_idempotent` | ✅ COMPLIANT |
| Escritura en el corpus de registro | Descomposición en ambos formatos | `test_write_xlsx_fills_columns_and_is_idempotent` | ✅ COMPLIANT |
| Escritura en el corpus de registro | Escritura idempotente | `test_write_csv_is_idempotent` | ✅ COMPLIANT |
| Escritura en el corpus de registro | Sidecar sin descripciones | `test_sidecar_json_has_no_description_and_has_trace_fields`, `test_write_sidecar_merge_never_adds_description` | ✅ COMPLIANT |
| Carga sin debilitar el validador | Corpus de evaluación cargable | `cd evaluation; pytest -q` → 118 passed, no `CorpusError` | ✅ COMPLIANT |
| Carga sin debilitar el validador | Caso sin medición no se marca nulo | `test_merge_json_does_not_overwrite_non_null_with_null` | ✅ COMPLIANT |
| Carga sin debilitar el validador | Telefonía pendiente reportada | `test_merge_json_writes_numeric_and_counts_pending`, `test_dry_run_reports_counts_without_writing` | ✅ COMPLIANT |
| Carga sin debilitar el validador | El validador no se debilita | static: `evaluation/corpus.py::_a_float` (L138-144) intact; no diff under `evaluation/` | ✅ COMPLIANT |
| Trazabilidad e idempotencia correo | Correlación exacta por contrato | `test_ingest_email_correlates_exact_and_derives_metric` (`find_incidente_by_origen` filters `origen_message_id`) | ✅ COMPLIANT |
| Trazabilidad e idempotencia correo | Fallback documentado | `test_select_incident_by_window_documented_fallback`, `test_select_incident_by_window_excludes_unrelated_old_and_claimed` | ✅ COMPLIANT |
| Trazabilidad e idempotencia correo | Message-ID determinístico | `test_build_email_message_sets_deterministic_message_id`, `test_ingest_email_replay_same_message_id_is_deterministic` | ✅ COMPLIANT |
| Trazabilidad e idempotencia correo | Correlación tolerante al formato | `test_correlation_keys_cover_bracketed_and_plain`, `test_normalize_message_id_repeated_and_whitespace` | ✅ COMPLIANT |
| Chequeo secundario de confirmación | Confirmación observada por camino separado | `test_ingest_email_confirmation_observed_separately`, `test_run_wires_confirmation_observer_when_configured` | ✅ COMPLIANT |
| Chequeo secundario de confirmación | Confirmación ausente no bloquea | `test_ingest_email_confirmation_absent_keeps_primary`, `test_confirmation_observer_exception_does_not_leak_message` | ✅ COMPLIANT |
| Chequeo secundario de confirmación | La confirmación no contamina | `test_confirmation_path_must_be_separate`, `test_run_aborts_when_confirmation_path_equals_ingestion` | ✅ COMPLIANT |
| Privacidad de las descripciones | Ninguna descripción en la salida | `test_sidecar_json_has_no_description_and_has_trace_fields`, `test_confirmation_observer_has_no_description_or_secret_leak` | ✅ COMPLIANT |
| Privacidad de las descripciones | Error reportado sin cuerpo | `test_ingest_web_timeout_reports_short_label`, `test_ingest_web_4xx_is_not_retried` | ✅ COMPLIANT |
| Prerrequisitos y anomalías | Credenciales desde el entorno | (no test found; branch L1236-1242 uncovered) | ⚠️ UNTESTED |
| Prerrequisitos y anomalías | Prerrequisitos de N8N documentados | static: `README.md` runbook sections (N8N import, credentials, separate path) | ✅ COMPLIANT |
| Prerrequisitos y anomalías | Dependencia c-69 documentada | static: `README.md` L326 + `design.md` D3/D10 | ✅ COMPLIANT |
| Prerrequisitos y anomalías | Anomalía excluida | `test_derive_metric_negative_espera_beyond_skew_is_anomalous`, `test_write_csv_anomalous_result_preserves_prior_values`, `test_write_xlsx_anomalous_result_preserves_prior_values` | ✅ COMPLIANT |

**Compliance summary**: 26/27 scenarios compliant; 1 UNTESTED (credentials guard). Two documentation scenarios are validated by structural/static evidence (no runtime behavior to test).

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Ingesta por flujo N8N real | ✅ Implemented | `ingest_web_case` POSTs to webhook then GETs detail by id; `ingest_email_case` sends SMTP then polls the exact filter |
| Derivación de la métrica híbrida | ✅ Implemented | `derive_metric` (L161) derives pipeline/wait/e2e; `tiempo_automatizado_s` = e2e for both channels |
| Escritura en el corpus de registro | ✅ Implemented | `write_csv_results`/`write_xlsx_results` idempotent; `write_sidecar_json` description-free |
| Carga sin debilitar el validador | ✅ Implemented | `merge_evaluation_json` (L768) skips non-numeric and never writes null |
| Trazabilidad e idempotencia correo | ✅ Implemented | `build_message_id`/`normalize_message_id`/`correlation_keys`; `find_incidente_by_origen` uses `origen_message_id` |
| Chequeo secundario de confirmación | ✅ Implemented | `confirmation_path_is_separate` + `confirmation_separation_error` + non-blocking `_observe_confirmation` |
| Privacidad de las descripciones | ✅ Implemented | `CaseResult` has no description; `_error_label` returns short labels only |
| Prerrequisitos y anomalías | ✅ Implemented | env-only credentials; `anomalo` exclusion; exit != 0 on failures/anomalies |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 métrica híbrida (t_pipeline/t_espera/t_e2e; canonical = e2e) | ✅ Yes | `derive_metric` + corpus R001 consistency (3.721+17.288=21.009) |
| D2 camino web sincrónico (POST + GET by id) | ✅ Yes | `ingest_web_case` |
| D3 correlación exacta c-69 primary, window fallback documented | ✅ Yes | `find_incidente_by_origen`; `select_incident_by_window` marked fallback-only |
| D4 source JSON default; tolerant channel mapping; teléfono omitted | ✅ Yes | `map_canal` + `select_cases`; dry-run reports 119 ingestable / 81 teléfono omitted |
| D5 write-back both XLSX+CSV, no validator weakening | ✅ Yes | CSVs/XLSX verified with the 4 columns; `_a_float` untouched |
| D6 deterministic Message-ID + bracket normalization | ✅ Yes | `build_message_id`/`normalize_message_id` |
| D7 sidecar without descriptions | ✅ Yes | Verified: 4/4 n8n entries and 81/81 teléfono entries have no `descripcion` |
| D8 anomaly exclusion (no clamp) | ✅ Yes | `anomalo` flag; writers skip invalid metrics |
| D9 noisy failures + partial run | ✅ Yes | `run` returns 1 on failures/anomalies; `--dry-run` no net/write |
| D10 operation prereqs (env login, admin scope) | ✅ Yes | `run` abort 2 without env creds; README runbook |
| D11 privacy | ✅ Yes | No description in output/sidecar; short error labels |
| D12 TDD of pure logic | ✅ Yes | 86 offline tests |
| D13 governance MEDIO | ✅ Yes | No credentials committed; `active: false` with placeholders |
| D14 confirmation as secondary, separate path, non-blocking | ✅ Yes | Guard rejects same mailbox; observer exceptions swallowed |

**Deviation (documented, acceptable)**: `design.md` D2 said the web channel does NOT send `origen_message_id` and dedup is c-69's job. The implemented harness DOES send `origen_message_id = corpus-<ID>` (using c-69's caller-supplied id) to make web replays idempotent. This is recorded in `tasks.md` "Notas de desviación" and is consistent with c-69's implemented contract. No coherence concern.

---

## Evidence Quality for the Past Real Run (tasks 0.8, 6.2, 6.3, 6.4, 6.6)

| Task | Evidence | Assessment |
|------|----------|------------|
| 6.4 Full run (119 web+correo) | Engram #1143 (2026-10-02) states "web 53/53 con valor, correo 66/66"; independently corroborated by the corpus JSON (53/53 web, 66/66 correo) and the CSV/XLSX values | **Sufficient**, with a traceability caveat (WARNING-2) |
| 6.2/6.3 Limited web/correo runs | Subsumed by 6.4; same memory + corpus evidence | **Sufficient** |
| 6.6 Complete corpus load | Independently re-executed: `evaluation` 118 passed, no `CorpusError`; corpus 200/200 (incl. 81 teléfono) | **Sufficient (strong)** |
| 0.8 Separate confirmation path | `ingest.env` configures a DIFFERENT mailbox (same host, different user → separate account, D14 option B); `confirmation_path_is_separate` implemented and tested; author confirmed receipt per `tasks.md` | **Sufficient** |

**Residual gap**: the real run's raw per-case traceability survives only for 4/119 cases (sidecar overwrite bug; fixed in 4.11). The canonical deliverable (numeric corpus) is fully verifiable and IS verified; the historical run itself is not replayable and its per-case sidecar evidence is partially lost. For a thesis audit this materially weakens provenance, so it is flagged (WARNING-2) even though it does not block archive.

---

## Issues Found

**CRITICAL** (must fix before archive):
None. The canonical deliverable (corpus loadable, reproducible harness, regression-free `App/**`) is independently verified.

**WARNING** (should fix):
1. **Untested scenario — credentials guard (REQ "Prerrequisitos de operacion y anomalias" / "Credenciales desde el entorno")**: `run()` returns exit 2 when `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD` are missing (L1233-1242), but no test exercises it and coverage confirms L1236-1242 are uncovered. The change is not strictly spec-complete at the behavioral level. (A strict-TDD reading would count this as CRITICAL; it is downgraded here because the guard is trivially implemented, statically evident, and low-risk. A one-test addition would close it.)
2. **Historical traceability gap (real run)**: `data/corpus_resultados_n8n.json` holds only 4/119 cases from the 2026-10-02 run. The overwrite bug was fixed in task 4.11 (merge by `case_id`), but the prior run's per-case sidecar evidence is unrecoverable. The corpus values remain intact and independently verified; the loss affects audit provenance only.
3. **Repo-wide red test unrelated to c-68**: `scripts/corpus_ingest/test_pseudonymize_corpus.py::test_no_pii_produces_zero_counts_and_unchanged_text` fails because archived `c-73-pseudonimizacion-tarjeta` added the `tarjeta` category to the backend pseudonymizer without updating this test's expected dict. Not introduced by c-68 (pre-existing at HEAD), but the exact `pytest -q` command in the verification brief is not green because of it. Should be fixed by c-73's owners.

**SUGGESTION** (nice to have):
1. `tasks.md` 6.1 and 6.5 record `pendientes_nulos=200`; the current dry-run reports `pendientes_nulos=0` (corpus now complete). Update the recorded evidence for consistency.
2. `data/corpus_evaluacion_pseudonimizado.json` `metadata.descripcion` still reads "tiempos automatizados pendientes de medicion end-to-end" although 200/200 are complete (D5 asked to update it "si corresponde").
3. No standalone `apply-progress` artifact with a tabular TDD Cycle Evidence exists; TDD evidence lives inline in `tasks.md`. Acceptable for this repo's openspec convention, but a tabular artifact would ease strict-TDD verification.
4. Consider a test for the missing-credentials guard (see WARNING-1) — cheap, closes the only UNTESTED scenario.

---

## Verdict

**PASS WITH WARNINGS**

All 63 tasks are complete; the c-68 harness suite (86/86), evaluation (118/118), and backend regression (1217 passed) are green; the dry-run is exit 0 with zero data side effects; `App/**` is untouched; `openspec validate --strict` passes. The corpus is independently confirmed at 200/200 with per-channel values and the write-back columns are present in both CSV and XLSX. Residual gaps are evidence-quality/traceability items and one untested (but statically implemented) credential guard — none block archive.

**CRITICAL count**: 0

---

## Addendum (2026-10-09) — Post-verify fixes

Re-ejecucion tras corregir los warnings. Cambios SOLO en archivos de test (sin produccion, sin `App/**`).

| Issue | Estado | Evidencia |
|-------|--------|-----------|
| W1 (guard de credenciales sin test) | RESUELTO | Nuevo `test_run_missing_credentials_aborts_without_network` (`test_ingest_via_n8n.py`). Coverage de `ingest_via_n8n.py` 93% (lineas 1236-1242 cubiertas). |
| W2 (trazabilidad sidecar 4/119) | ACEPTADO | Irrecuperable: la corrida real del 2026-10-02 no es re-ejecutable y la evidencia per-case perdida no se puede reconstruir. El corpus canonico 200/200 esta intacto y verificado. Gap de trazabilidad historica documentado. |
| W3 (test rojo de c-73 en `corpus_ingest`) | RESUELTO | `test_pseudonymize_corpus.py` alineado a 5 categorias (`tarjeta`). `scripts/corpus_ingest` = `162 passed`, `0 failed`. |
| SUGGESTION-1 (textos stale) | RESUELTO | `tasks.md` 6.1 y 6.5 actualizadas a `pendientes_nulos=0`. |

Comandos exactos:

```
$ cd scripts/corpus_ingest && python3 -m pytest -q
162 passed in 3.93s

$ python3 scripts/corpus_ingest/ingest_via_n8n.py --dry-run
DRY-RUN: ingesta=119 telefono_omitido=81 sin_mapear=0 pendientes_nulos=0. No se ejecuto red ni escritura.
(exit 0)

$ git status --porcelain
 M scripts/corpus_ingest/test_ingest_via_n8n.py
 M scripts/corpus_ingest/test_pseudonymize_corpus.py
```

Lint resuelto (2026-10-09): los 5 errores preexistentes de `ruff check .` en `scripts/corpus_ingest` (E402/F401/F841) en `ingest_telefonia_corpus.py` y `test_ingest_telefonia_corpus.py` fueron corregidos; `ruff check .` -> `All checks passed!`.

**Verdict post-fix**: PASS (0 CRITICAL; W1 y W3 resueltos; W2 aceptado como gap de trazabilidad historica no reparable).

---

## Independent Re-verification (2026-10-09)

Independent verifier re-run on the CURRENT working tree (includes post-verify fixes). All commands executed by the verifier; no prior claim was trusted. Host has no `python` binary — `python3` used throughout.

### Exact command outputs

**1. `cd scripts/corpus_ingest && ruff check .`** — exit 0

```
All checks passed!
```

**2. `cd scripts/corpus_ingest && python3 -m pytest -q`** — exit 0

```
162 passed in 7.88s
```

Old W3 failure (`test_pseudonymize_corpus.py::test_no_pii_produces_zero_counts_and_unchanged_text`) is GONE. Suite is fully green.

**3. `cd scripts/corpus_ingest && python3 -m pytest test_ingest_via_n8n.py -q`** — exit 0

```
87 passed in 5.47s
```

(was 86 before W1; +1 = the new guard test). The test `test_run_missing_credentials_aborts_without_network` EXISTS at `test_ingest_via_n8n.py:1489` and passes.

**4. Coverage of the W1 guard** — exit 0

```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
ingest_via_n8n.py     622     45    93%   122, 124, 127, 129, 236, 263, 284, 292, 411, 419, 554, 638, 682, 693, 696, 724, 781, 801-802, 883-893, 959-960, 962, 1020-1021, 1023, 1032, 1035, 1063, 1102-1103, 1189-1190, 1202, 1259-1264, 1273, 1279, 1285
-------------------------------------------------
TOTAL                 622     45    93%
87 passed in 11.95s
```

Lines 1236-1242 are NO LONGER in the missing list (previous missing list included `1236-1242`). Coverage rose 92% -> 93%. The guard `run()` exit 2 (L1233-1242) is now exercised.

**5. `python3 scripts/corpus_ingest/ingest_via_n8n.py --dry-run`** — exit 0

```
Casos en el corpus: 200 | seleccionados: 200
  canal 'correo': 66
  canal 'telefono': 81
  canal 'web': 53
DRY-RUN: ingesta=119 telefono_omitido=81 sin_mapear=0 pendientes_nulos=0. No se ejecuto red ni escritura.
```

`pendientes_nulos=0` confirmed.

**6. `cd evaluation && pytest -q`** — exit 0

```
118 passed in 12.08s
```

No `CorpusError`.

**7. `git status --porcelain` / `git --no-pager diff --stat`**

```
 M README.md
 M openspec/changes/c-68-corpus-ingesta-n8n/tasks.md
 M openspec/changes/c-68-corpus-ingesta-n8n/verify-report.md
 M scripts/corpus_ingest/ingest_telefonia_corpus.py
 M scripts/corpus_ingest/test_ingest_telefonia_corpus.py
 M scripts/corpus_ingest/test_ingest_via_n8n.py
 M scripts/corpus_ingest/test_pseudonymize_corpus.py
```

```
 README.md                                          |  7 ++++-
 openspec/changes/c-68-corpus-ingesta-n8n/tasks.md  | 16 +++++++++--
 .../c-68-corpus-ingesta-n8n/verify-report.md       | 32 ++++++++++++++++++++++
 scripts/corpus_ingest/ingest_telefonia_corpus.py   |  2 +-
 .../corpus_ingest/test_ingest_telefonia_corpus.py  |  5 ++--
 scripts/corpus_ingest/test_ingest_via_n8n.py       | 28 +++++++++++++++++++
 scripts/corpus_ingest/test_pseudonymize_corpus.py  |  8 +++++-
 7 files changed, 89 insertions(+), 9 deletions(-)
```

**CONFIRMED: NO file under `App/**` is modified.** The two c-68 deliverables are `test_ingest_via_n8n.py` (+28) and `test_pseudonymize_corpus.py` (+8). TANGENTIAL (not c-68): `README.md` (clone-readiness docs), `ingest_telefonia_corpus.py` + `test_ingest_telefonia_corpus.py` (pre-existing ruff lint fixes: F841 `exc` removed, F401 unused `ic` import removed, E402 noqa added). `tasks.md` and `verify-report.md` are the change's own post-verify records.

**8. `openspec validate c-68-corpus-ingesta-n8n --strict`** — exit 0

```
Change 'c-68-corpus-ingesta-n8n' is valid
```

**9. Backend regression `cd App/Backend && python3 -m pytest -m "not integration" -q`** — exit 0 (216.26s)

```
1217 passed, 42 deselected, 1 xfailed, 331 warnings in 216.26s (0:03:36)
```

Matches the prior verify exactly (1217/42/1). Consistent with `App/**` being untouched.

### Additional independent checks

- Sidecar `data/corpus_resultados_n8n.json`: independently parsed = **4 cases** (`R004, R010, R012, R001`). W2 claim of 4/119 holds.
- Corpus `data/corpus_evaluacion_pseudonimizado.json`: **200 cases, 0 null/non-numeric `tiempo_automatizado_s`**. Corpus is 200/200 complete, consistent with `pendientes_nulos=0`.
- Guard code inspected at `ingest_via_n8n.py:1233-1242`: reads `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD`, prints a credential-free ERROR to stderr, returns 2. The new test monkeypatches `login` to raise and asserts `run(...) == 2` and no `None` leakage.
- W3 fix inspected: expected dict now has 5 keys (`email/telefono/host/persona/tarjeta`), aligned with c-73.
- tasks.md diff inspected: 6.1/6.5 changed `pendientes_nulos=200` -> `pendientes_nulos=0`; 6.7 updated to `87 passed` / `162 passed` / `1217 passed`.

### Per-issue status

| Issue | Status | Independent evidence |
|-------|--------|----------------------|
| W1 — credentials guard UNTESTED | **RESOLVED** | `test_run_missing_credentials_aborts_without_network` exists + passes; coverage L1236-1242 no longer missing; 86 -> 87 harness tests |
| W2 — historical sidecar 4/119 | **ACCEPTED** | Sidecar independently parsed = 4 cases; real run not replayable; canonical corpus 200/200 intact and verified |
| W3 — red c-73 test in corpus_ingest | **RESOLVED** | `scripts/corpus_ingest` = `162 passed, 0 failed` with exact `pytest -q`; expected dict aligned to 5 categories |
| SUGGESTION-1 — stale `pendientes_nulos=200` | **RESOLVED** | tasks.md 6.1/6.5 now record `pendientes_nulos=0`; dry-run confirms 0 |

### New issue found (non-blocking, documentation only)

The "Post-verify (2026-10-09)" notes in `tasks.md` and the prior Addendum state that `ruff check .` in `scripts/corpus_ingest` still reports 5 errors (E402/F401/F841). This is STALE: the tangential telefonia lint fixes are now in the tree and an independent `ruff check .` returns `All checks passed!` (exit 0). The note describes a pre-existing debt that has since been resolved by changes outside c-68. It does not affect c-68 and requires no action; recorded for accuracy.

### Independent verdict

**PASS**

**CRITICAL count**: 0

Every reproducible claim holds under independent execution: harness 87/87, full corpus_ingest 162/162 (W3 gone), evaluation 118/118 without `CorpusError`, backend regression 1217 passed identical to prior, dry-run exit 0 with `pendientes_nulos=0`, sidecar 4 cases, corpus 200/200 with zero nulls, `openspec validate --strict` valid, and `App/**` untouched. W1 and W3 are RESOLVED, SUGGESTION-1 is DONE, W2 is ACCEPTED as an unrecoverable historical traceability gap. The only new finding is a stale documentation note (no impact).
