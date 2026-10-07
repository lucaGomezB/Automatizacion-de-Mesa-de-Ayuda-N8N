# Verification Report

**Change**: c-70-softphone-corpus-telefonia
**Version**: N/A
**Mode**: Strict TDD (repo-local OpenSpec workflow — no apply-progress artifact; TDD evidence lives in tasks.md inline annotations)
**Date**: 2026-10-06
**Verifier**: independent verification gate (executed, not static)

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 72 |
| Tasks complete | 72 |
| Tasks incomplete | 0 |

`openspec list --json` reports `completedTasks: 72, totalTasks: 72, status: complete` — matches `tasks.md` exactly. The three tasks that were blocked in the prior report (8.1, 8.2, 8.3) are now marked `[x]` and each carries operational evidence. Tasks 9.1–9.7 (post-smoke bugfix) are also complete.

---

## Build & Tests Execution

**Lint (`ruff check .`)**: ✅ PASSED — `All checks passed!`

**OpenSpec validate**: ✅ PASSED — `openspec validate c-70-softphone-corpus-telefonia --strict` → `Change 'c-70-softphone-corpus-telefonia' is valid` (exit 0). The batch form (`--changes`) reported 6 passed / 0 failed across active changes.

| Suite | Command | Result |
|-------|---------|--------|
| Backend offline | `App/Backend; pytest -m "not integration" -q` | ✅ 991 passed, 39 deselected, 1 xfailed (125.5 s) |
| Backend integration (PostgreSQL) | `App/Backend; pytest -m integration -q` | ✅ 39 passed, 992 deselected (25.1 s) |
| Evaluation corpus | `evaluation; pytest -q` | ✅ 79 passed (no `CorpusError`) |
| corpus_ingest | `scripts/corpus_ingest; pytest -q` | ✅ 153 passed |
| voip_softphone | `scripts/voip_softphone; pytest -q` | ✅ 69 passed |

**PostgreSQL reachable**: both stacks up. `mesa_local-postgres-1` (host 5433, app DB) and `mesa_local-postgres-corpus-1` (host 5434, `mesa_de_ayuda_corpus`) healthy. The integration subset ran against the disposable DB provisioned by the fixtures; `TEST_PG_ALLOW_APP_DB` was NOT set. Not blocked.

**Note on counts**: the prior report recorded 920 offline / 37 integration; the current tree has 991 offline / 39 integration. The growth is from unrelated changes merged since (c-60, c-72) plus the c-70 section-9 regression tests. Zero failures in any suite.

**Coverage**: ➖ Not run — no coverage threshold configured for this change; the brief requested exact pass counts, not a coverage gate.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ | No formal "TDD Cycle Evidence" table exists. The repo-local OpenSpec workflow produces no apply-progress artifact; evidence is inline in `tasks.md` (every code task tagged RED/GREEN/TRIANGULATE/REFACTOR with its test file). Honest limitation, not a missing artifact that could be recovered. |
| All tasks have tests | ✅ | 7 change-specific test files exist and pass: `test_telefonia_corpus_case_id.py`, `test_telefonia_pending_call.py`, `test_api_telefonia_corpus.py`, `test_migration_011_telefonia_corpus.py`, `test_ingest_telefonia_corpus.py`, `test_corpus_cases.py`, `test_softphone_html.py`. |
| RED confirmed (tests exist) | ✅ | All referenced files present and collected. |
| GREEN confirmed (tests pass) | ✅ | Cross-referenced against executed runs: backend offline 991, integration 39, evaluation 79, corpus_ingest 153, voip_softphone 69. |
| Triangulation adequate | ✅ | Distinct cases per behavior: null/zero/negative/explicit anomaly without clamping; rounding variants; upsert idempotence; purge expired vs still-valid; dry-run vs `--confirm-replace`; scoped delete vs other cases; reproceso with/without `corpus_case_id`. |
| Safety Net for modified files | ✅ | `tasks.md` records baselines (878 passed for sections 1–2; 52 passed for section 4; 920 for section 9). |

**TDD Compliance**: 5/6 checks fully passed, 1 partial (no formal evidence table — repo-local constraint).

---

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit (pure logic, structural HTML, mocked HTTP) | ~200+ | `test_ingest_telefonia_corpus.py`, `test_corpus_cases.py`, `test_softphone_html.py` | pytest |
| Integration (ASGI client + real DB session, SQLite/PostgreSQL) | ~60+ | `test_api_telefonia_corpus.py`, `test_telefonia_corpus_case_id.py`, `test_telefonia_pending_call.py`, `test_migration_011_telefonia_corpus.py` | pytest + pytest-asyncio |
| E2E (browser) | 0 | — | not installed |

The operational 81-case run is a manual end-to-end exercise through the real Twilio/N8N flow (not automatable in CI). Its *result* is verified against the corpus DB and files.

---

### Changed File Coverage

➖ Coverage analysis skipped — no coverage tool configured for this change. Behavioral coverage is instead proven by the executed suites below and by direct DB/file inspection.

---

### Assertion Quality

**Assertion quality**: ✅ No tautologies, no ghost loops, no production-code-free assertions. The `assert x is not None` matches found are **precondition guards immediately followed by value assertions** in the same test (e.g. `test_api_telefonia_corpus.py` lines 342/365/393 then assert on `fila.call_sid`/`fila.corpus_case_id`), which the audit rule explicitly permits. Mock/assertion ratios are healthy (mocks ≪ 2× assertions in every file; the softphone/corpus-cases files have 0 mocks).

---

### Quality Metrics

**Linter**: ✅ ruff — `All checks passed!` (no errors/warnings)
**Type Checker**: ➖ not configured for this project (ruff only enforces pycodestyle E rules)
**OpenAPI sync**: ✅ `tests/test_openapi_sync.py` passes within the offline suite (5 assertions), so the new endpoints are reflected in `docs/openapi.json`

---

## Spec Compliance Matrix

35 scenarios across 3 delta specs (25 + 5 + 5). Result: **31/35 COMPLIANT with executed tests**, 4 PARTIAL/MANUAL (3 infra-only scenarios + 1 static secrets review). Zero FAILING, zero UNTESTED for implementation gaps.

### telefonia-corpus-medicion (8 requirements, 25 scenarios)

| Requirement | Scenario | Test / Evidence | Result |
|-------------|----------|-----------------|--------|
| Corrida sobre base descartable | Base descartable aislada de la operativa | Operational: corpus DB `mesa_de_ayuda_corpus` on :5434 holds 81 incidentes / 81 ingresos; app DB `mesa_de_ayuda` on :5433 untouched (still at alembic 010, 8 pre-existing ingresos). Distinct volumes inspected. No automated test. | ⚠️ PARTIAL (operational/infra) |
| Corrida sobre base descartable | Wipe sin tocar la base de la aplicacion | Runbook §6 (scoped wipe); volumes `mesa_local_postgres_corpus_data`/`mesa_local_n8n_corpus_data` exist separately from `mesa_local_postgres_data`/`mesa_local_n8n_data`. No automated test. | ⚠️ MANUAL (infra) |
| Corrida sobre base descartable | Conmutacion de la Voice URL documentada | Runbook §7 (swap + restore). No automated test. | ⚠️ MANUAL (doc) |
| Correlacion exacta | Correlacion exacta de la llamada | `test_api_telefonia_corpus.py::test_voice_con_corpus_case_id_persiste_pendiente`, `::test_callback_resuelve_borra_pendiente_y_persiste_en_ingreso`, `test_telefonia_corpus_case_id.py::test_get_latest_by_corpus_case_id_devuelve_el_ultimo` | ✅ COMPLIANT |
| Correlacion exacta | Llamada sin caso no se altera | `test_api_telefonia_corpus.py::test_voice_sin_corpus_case_id_no_escribe_nada`, `::test_callback_sin_pendiente_deja_el_ingreso_sin_corpus` | ✅ COMPLIANT |
| Correlacion exacta | Idempotencia por CallSid preservada | `test_telefonia_corpus_case_id.py::test_call_sid_sigue_siendo_la_clave_unica` (+ live: incidente 2 `origen_message_id=CA596ab2…` in corpus DB) | ✅ COMPLIANT |
| Metrica canonica | Metrica identica a los otros canales | `test_ingest_telefonia_corpus.py::test_derive_telefonia_metric_valid_equals_pipeline_and_e2e` | ✅ COMPLIANT |
| Metrica canonica | Espera no medible en telefonia | `::test_build_telefonia_result_shape_and_no_wait`, `::test_write_back_fills_csv_columns_and_wait_blank` (+ CSV R002 `Tiempo espera (s)` blank, `t_e2e==t_pipeline==13.012`) | ✅ COMPLIANT |
| Metrica canonica | Caso anomalo excluido | `::test_derive_telefonia_metric_null_is_anomalous`, `::_zero_`, `::_negative_`, `::_explicit_anomaly_flag` | ✅ COMPLIANT |
| Recuperacion por corpus_case_id | Recuperacion del ultimo ingreso | `test_api_telefonia_corpus.py::test_get_ingresos_devuelve_el_ultimo_con_latencia`, `test_ingest_telefonia_corpus.py::test_recover_telefonia_case_ok_builds_metric` | ✅ COMPLIANT |
| Recuperacion por corpus_case_id | Credenciales desde el entorno | `test_ingest_telefonia_corpus.py::test_run_missing_credentials_aborts_without_network` | ✅ COMPLIANT |
| Recuperacion por corpus_case_id | Caso sin ingreso reportado | `::test_recover_telefonia_case_404_is_pending`, `::test_run_pending_case_reported_and_not_written` | ✅ COMPLIANT |
| Write-back | Columnas del corpus con valores de telefonia | `::test_write_back_fills_csv_columns_and_wait_blank`, `::test_write_back_fills_xlsx_columns_and_wait_blank` | ✅ COMPLIANT |
| Write-back | Escritura idempotente | `::test_write_back_is_idempotent_and_no_duplicate_columns` | ✅ COMPLIANT |
| Write-back | Ninguna descripcion en la salida | `::test_run_does_not_log_descriptions`, `::test_write_back_sidecar_is_description_free` (+ live sidecar: 0 occurrences of "descripcion") | ✅ COMPLIANT |
| Write-back | El validador no se debilita | `::test_evaluation_a_float_still_rejects_non_numeric` + `git diff --stat evaluation/corpus.py` empty | ✅ COMPLIANT |
| Reemplazo | Reemplazo conserva solo la medicion nueva | `::test_run_replace_confirmed_deletes_and_writes`, `test_api_telefonia_corpus.py::test_delete_conserva_el_ultimo_y_borra_previos_con_cascada` | ✅ COMPLIANT |
| Reemplazo | Sin replace conserva el historial | `::test_run_without_replace_never_deletes` | ✅ COMPLIANT |
| Reemplazo | Borrado acotado al caso | `test_api_telefonia_corpus.py::test_delete_no_afecta_otros_corpus_case_id`, `test_ingest_telefonia_corpus.py::test_run_replace_is_scoped_to_each_selected_case` | ✅ COMPLIANT |
| Reemplazo | Dry-run sin escritura | `test_api_telefonia_corpus.py::test_delete_dry_run_por_defecto_no_borra`, `::test_delete_marca_dry_run_no_dry_run`, `test_ingest_telefonia_corpus.py::test_run_replace_dry_run_neither_deletes_nor_writes` | ✅ COMPLIANT |
| Cobertura 81 casos | Los 81 casos medidos | Operational: corpus DB 81 incidentes, 81 ingresos, 81 `corpus_case_id` distintos, 0 pendientes; JSON 81 telefono numeric; sidecar 81 medidos / 0 anomalos. | ✅ COMPLIANT (operational) |
| Cobertura 81 casos | Sin muestreo | No sample mode in `ingest_telefonia_corpus.py`; `select_cases(..., limit=None)` selects all 81; operational count = 81/81. | ✅ COMPLIANT (static + operational) |
| Cobertura 81 casos | Corpus cargable al completar | `evaluation; pytest -q` → 79 passed, no `CorpusError`; JSON 200/200 numeric (81 telefono + 66 correo + 53 web). | ✅ COMPLIANT |
| Privacidad y secretos | Sin secretos en el codigo | Static review of the script/compose: env references only; targeted secret scan clean. No automated test. | ⚠️ PARTIAL (static) |
| Privacidad y secretos | Sidecar sin descripciones | `::test_write_back_sidecar_is_description_free` + live sidecar inspection (0 descriptions) | ✅ COMPLIANT |

### telefonia-stt-intake (1 requirement, 5 scenarios)

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Correlacion opcional | El caso viaja del webhook al ingreso | `test_api_telefonia_corpus.py::test_voice_con_corpus_case_id_persiste_pendiente`, `::test_callback_resuelve_borra_pendiente_y_persiste_en_ingreso` | ✅ COMPLIANT |
| Correlacion opcional | El mapeo de la tabla corta es efimero | `test_telefonia_pending_call.py::test_delete_by_call_sid_borra_y_es_idempotente`, `::test_purge_expired_purga_vencidas_y_respeta_vigentes`, `test_api_telefonia_corpus.py::test_callback_purga_pendientes_vencidas` | ✅ COMPLIANT |
| Correlacion opcional | Sin caso de corpus el ingreso es valido | `test_api_telefonia_corpus.py::test_callback_sin_pendiente_deja_el_ingreso_sin_corpus` | ✅ COMPLIANT |
| Correlacion opcional | El reproceso preserva el caso de corpus | `test_api_telefonia_corpus.py::test_reproceso_preserva_corpus_case_id` | ✅ COMPLIANT |
| Correlacion opcional | Idempotencia y origen no cambian | `test_telefonia_corpus_case_id.py::test_call_sid_sigue_siendo_la_clave_unica` | ✅ COMPLIANT |

### telephony-test-softphone (1 requirement, 5 scenarios)

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Seleccion + listado | Selector solo con casos telefonicos | `test_corpus_cases.py::test_load_telephone_cases_returns_only_phone_channel`, `::test_corpus_cases_endpoint_returns_phone_cases` | ✅ COMPLIANT |
| Seleccion + listado | Valor por defecto vacio | `test_softphone_html.py::test_page_has_corpus_case_select_defaulting_to_empty`, `::test_page_select_has_no_preselected_case` | ✅ COMPLIANT |
| Seleccion + listado | El caso seleccionado viaja con la llamada | `test_softphone_html.py::test_page_sends_corpus_case_id_only_when_selected` | ✅ COMPLIANT |
| Seleccion + listado | Sin reproduccion de audio | `test_softphone_html.py::test_page_shows_selected_case_for_recitation_without_playback` | ✅ COMPLIANT |
| Seleccion + listado | Solo loopback y sin logueo de descripciones | `test_corpus_cases.py::test_corpus_cases_endpoint_does_not_log_descriptions` + loopback host refusal in `mint_token.py` | ✅ COMPLIANT |

**Compliance summary**: 31/35 scenarios compliant with executed tests or verified operational evidence; 4 scenarios are PARTIAL/MANUAL (3 infra-isolation scenarios covered by runbook evidence, 1 static secrets review). No scenario is FAILING and no scenario is UNTESTED due to an implementation gap.

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Base descartable | ✅ Implemented | `docker-compose.yml` corpus profile: `postgres-corpus` (:5434, `mesa_de_ayuda_corpus`, `postgres_corpus_data`) + `backend-corpus` (:8001, DATABASE_URL→postgres-corpus, alembic head) + `n8n-corpus` (:5679, `n8n_corpus_data`, BACKEND_URL→backend-corpus); all `profiles: ["corpus"]`. Live inspection confirms distinct volumes and both DBs running. |
| Correlacion exacta | ✅ Implemented | `telefonia_ingreso.corpus_case_id` String(64) nullable+indexed (migration 011); `telefonia_pending_call` (call_sid PK, corpus_case_id, created_at); webhook upsert → callback resolve+delete+TTL purge; link into ingreso on seal. Live: 81 distinct corpus_case_id. |
| Metrica canonica | ✅ Implemented | `derive_telefonia_metric`: `t_pipeline_s = t_e2e_s = round(latencia/1000, 3)`, `t_espera_s = None`; anomalies excluded without clamping. Live CSV R002: auto 13.012, latencia 13012, pipeline 13.012, espera blank. |
| Recuperacion | ✅ Implemented | `GET /api/v1/telefonia/ingresos?corpus_case_id=X&latest=true` admin-only (`AdminDep`), routes→services→repositories with explicit `selectinload(incidente)`. |
| Write-back | ✅ Implemented | `ingest_telefonia_corpus.py` reuses `ingest_via_n8n` writers; `git diff evaluation/corpus.py` empty. |
| Reemplazo | ✅ Implemented | `DELETE ...&dry_run=true` default; `--replace` dry-run unless `--confirm-replace`. `eliminar_previos_por_corpus_case_id` keeps `ingresos[0]`, scoped by `corpus_case_id`, deletes incidente (CASCADE clasificacion_log) before ingreso (SET NULL). |
| Cobertura 81 | ✅ Complete | 81/81 measured; sidecar `medidos=81 anomalos=0 pendientes=0 fallidos=0`. |
| Privacidad/secretos | ✅ Implemented | env-only credentials (`INGEST_OPERATOR_USERNAME/PASSWORD`); short error labels only; sidecar description-free; softphone serves pseudonymized corpus on loopback only. |

**Layer discipline**: ✅ routes → services → repositories → models. No layer skipped.

**Migration chain**: ✅ linear and non-colliding: `010 → 011 (c-70) → 012 (c-60, already archived)`. `011.downgrade()` drops index+table+index+column (lines 62-66). `test_migration_011_telefonia_corpus.py::test_downgrade_quita_columna_tabla_y_upgrade_la_recrea` passes.

**`evaluation/corpus.py` untouched**: ✅ `git diff --stat -- evaluation/corpus.py` empty.

**Isolation guarantee (scrutinized)**: ✅ The corpus run cannot touch the app DB — `backend-corpus.DATABASE_URL` resolves exclusively to `postgres-corpus:5432/mesa_de_ayuda_corpus`; corpus containers mount only `mesa_local_postgres_corpus_data`/`mesa_local_n8n_corpus_data`; distinct host ports (5434/8001/5679). The app DB on :5433 holds only its pre-existing 8 ingresos and remains at alembic 010 — untouched by the run.

**Scoped `--replace` (scrutinized)**: ✅ `list_by_corpus_case_id` returns rows ordered by `id DESC`; `a_eliminar = ingresos[1:]` keeps the latest; deletion is filtered by `corpus_case_id` only; FK order is incidente→ingreso, so `clasificacion_log` cascades with no orphans and other cases/canales are never touched. Proven by `test_delete_no_afecta_otros_corpus_case_id`, `test_delete_conserva_el_ultimo_y_borra_previos_con_cascada`, `test_run_replace_is_scoped_to_each_selected_case`.

**Telephony metric contract (scrutinized)**: ✅ `t_espera_s` is `None` end-to-end (script → `CaseResult` → CSV/XLSX blank, never 0); `t_e2e = t_pipeline = latencia_e2e_ms/1000`. Confirmed in tests and in real artifacts.

**PII (scrutinized)**: ✅ No real PII exposed — the served list comes from `data/corpus_evaluacion_pseudonimizado.json`; the sidecar contains only ids/instants/times (0 "descripcion" occurrences); descriptions are never logged (request logging silenced); loopback binding is enforced (`LOOPBACK_HOSTS`).

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 nullable `corpus_case_id` + index | ✅ Yes | Model + migration 011 match; no backfill. |
| D2 store keyed-by-CallSid via `telefonia_pending_call` (OQ1=B) | ✅ Yes | Model, repo (`upsert/get/delete/purge`), service, TTL purge, callback delete — all present; no new dependency. |
| D3 `GET /corpus-cases` + `<select>` (OQ3) | ✅ Yes | Loopback-only, tolerant channel filter, no playback, descriptions not logged. |
| D4 `t_espera_s=None` (OQ4) | ✅ Yes | CaseResult omits wait; CSV/XLSX blank. |
| D5 dedicated read endpoint + admin role (OQ5) | ✅ Yes | `GET /ingresos` requires `administrador_directorio`; credentials from env. |
| D6 reuse `ingest_via_n8n` writers | ✅ Yes | Imports `CaseResult`, `_should_write_metric`, writers. |
| D7 `--replace` scoped + FK order | ✅ Yes | `--replace`/`--confirm-replace`, dry-run default, cascade/SET NULL, scoped. |
| D8 corpus Compose profile + scoped wipe | ✅ Yes | All three services under `profiles: ["corpus"]`; compose comments + runbook document the scoped wipe and reject the bare `down -v`. |
| D9 full 81 coverage, no sampling | ✅ Yes | 81/81 measured; no sample mode. |
| D10 TDD offline | ✅ Yes | Suites present and green. |
| D11 governance ALTO | ✅ Yes | Destructive ops gated behind explicit flags/dry-run. |
| D12 migration 011 `down_revision=010` | ✅ Yes | Confirmed; 012 (c-60) chains off 011 with no branch. |

---

## Issues Found

**CRITICAL** (must fix before archive):
- None.

**WARNING** (should fix):
- The operational database `mesa_de_ayuda` (host :5433) is still at Alembic revision **010** and its `telefonia_ingreso` table lacks `corpus_case_id`; the running base `backend` container also does not contain the c-70 code. This is expected environment drift (c-70 has never been deployed to the base stack), not a defect of the change: the migration is additive and the base compose `backend` runs `alembic upgrade head` on (re)start, so `011` will apply automatically at deployment. Flagged so the author is not surprised that the operational API does not yet expose `corpus_case_id`. No action required before archiving.
- Three isolation scenarios (base aislada, wipe, Voice URL switch) have no automated test; their evidence is the runbook + live inspection of volumes/DBs. Acceptable for infra, but they remain the only scenarios without executed automated proof.

**SUGGESTION** (nice to have):
- `docs/runbook-corpus-telefonia.md` §4 line 82 still says the base is migrated "hoy `010`". §9 already clarifies that c-70 later added `011` (current head `011`/`012`). Minor staleness in a dated note.
- The change's completion evidence currently lives in **uncommitted** working-tree edits (`tasks.md` and `CHANGES.md` show as modified in `git status`, plus untracked `c-73`). The archive step should stage/commit those so the audit trail is complete. (The verifier did not modify anything.)
- No formal "TDD Cycle Evidence" table exists (repo-local workflow produces no apply-progress artifact). Inline tasks.md annotations are adequate; a table would ease future audits.

---

## Verdict

**PASS WITH WARNINGS**

All 72/72 tasks are complete; every executed suite and the strict OpenSpec validation pass with zero failures (backend offline 991, integration 39, evaluation 79, corpus_ingest 153, voip_softphone 69; ruff clean). The change is behaviorally compliant: 31/35 spec scenarios are proven by passing tests or verified operational evidence, with the remaining 4 being infra/static scenarios covered by live inspection and the runbook — none failing, none untested for a real gap. The scrutinized invariants hold: the corpus stack is genuinely isolated (distinct DB/volumes/ports; app DB untouched), `--replace` is case-scoped and keeps the latest with correct FK cascades, the telephony metric contract is `t_espera=None` / `t_e2e=t_pipeline=latencia/1000`, and no PII is exposed. The corpus is fully measured (81/81 telefono, 200/200 numeric, loadable without `CorpusError`). Warnings are operational notes, not blockers: the base stack has not yet been redeployed with migration 011, and three infra scenarios rely on runbook/live evidence rather than automated tests. Ready to archive.
