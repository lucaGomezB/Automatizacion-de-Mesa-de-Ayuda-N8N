# Verification Report

**Change**: c-39-e2e-timing-instrumentation
**Version**: N/A (delta specs, no version field)
**Mode**: Strict TDD (orchestrator-injected) + OpenSpec artifact store
**Verifier**: independent, executed tests and migration, no production code modified

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 21 (1.1-1.4, 2.1-2.4, 3.1-3.4, 4.1-4.4, 5.1-5.5) |
| Tasks complete `[x]` | 21 |
| Tasks incomplete `[ ]` | 0 |
| Tasks genuinely implemented | 20 |
| Tasks partial | 1 (5.4 — migration cycle verified by hand on PG, NOT by the automated integration subset) |

All checked tasks were cross-checked against real code/tests. Task 5.4's checkbox overstates
automation: the Alembic 006 upgrade/downgrade test (`test_migration_006_timing.py`) runs on SQLite
file, not PostgreSQL, and the `@pytest.mark.integration` subset contains no Alembic 006 coverage.
The cycle WAS independently reproduced by hand against a disposable PG database (see below), so the
underlying claim holds — the task description ("correr pytest -m integration ... y verificar")
does not match how it was actually verified.

---

## Build & Tests Execution

**Build**: N/A (Python, no build step). **Type check**: N/A (no mypy configured for this suite).

**Lint (ruff)**: PASS — `ruff check .` → "All checks passed!"
**OpenSpec strict validate**: PASS — `openspec validate --strict c-39-e2e-timing-instrumentation` → "Change ... is valid"
**OpenAPI sync**: PASS — 5 passed (`tests/test_openapi_sync.py`)

**Tests — targeted C-39 (3 files)**: 27 passed / 0 failed
```
tests/test_timing_contract.py        16 passed
tests/test_timing_service.py          6 passed
tests/test_migration_006_timing.py    5 passed
```

**Tests — full offline SQLite subset**: 431 passed / 0 failed / 22 deselected (integration) / 1 xfailed
```
pytest -m "not integration" -q  →  431 passed, 22 deselected, 1 xfailed in 77.03s
```

**Tests — PostgreSQL integration subset**: 22 passed / 0 failed (with explicit disposable target)
```
TEST_PG_URL=postgresql+asyncpg://mesa:mesa@localhost:5433/mesa_de_ayuda_verify pytest -m integration -q
→ 22 passed, 432 deselected
```
NOTE: default run (no `TEST_PG_URL`) errors 22/22 with
`password authentication failed for user "mesa"` because the harness default password
(`mesa_local_dev`) does not match the live container (`mesa`). This is an environment/credential
mismatch, NOT a code defect. See BLOCKED section.

**Migration 006 on real PostgreSQL (independent reproduction)**:
```
upgrade head  → ingresado_en / persistido_en = timestamp with time zone, is_nullable=YES
downgrade 005 → 0 rows (both dropped)
upgrade head  → both columns recreated
```
Running app DB (`mesa_local-backend-1`) also reports `alembic current == 006 (head)`.

**Coverage (informational, changed backend files)**:
| File | Cover | Missing |
|------|-------|---------|
| `app/config/settings.py` | 100% | — |
| `app/models/incidente.py` | 97% | 204 (repr) |
| `app/schemas/incidente.py` | 96% | 84, 150, 177, 202 |
| `app/services/incidente_service.py` | 82% | 129, 253-267, 317-320, 357, 365-367, 372-374, 461, 486-490 |

Missing service lines are pre-existing non-C-39 branches (IntegrityError race, catalog-not-found).
No C-39 line is uncovered. Aggregate 91%.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD evidence reported | ⚠️ | No `apply-progress` artifact in repo. Engram #924 (apply) narrates Strict TDD but has no "TDD Cycle Evidence" table. OPSX artifact set does not include apply-progress. |
| All tasks have tests | ✅ | Every behavioral task has a corresponding test file/function |
| RED confirmed (tests exist) | ✅ | 5 test files verified on disk |
| GREEN confirmed (tests pass) | ✅ | 40/40 C-39 tests pass on execution |
| Triangulation adequate | ✅ | Each requirement has happy path + edge cases (naive, nulo, future-in/out-of-tolerance, zero, replay, distinct ids) |
| Safety Net for modified files | ➖ | Not documented; existing suites pass post-change (431 offline) |

**Assertion quality**: no tautologies, no ghost loops, no type-only-only assertions. Assertions
call real production code (Pydantic validators, computed fields, real ASGI requests, real Alembic).
The N8N Grupo-22 tests are substring/structural assertions (inherent to a no-runtime workflow suite)
— accepted repo pattern, flagged SUGGESTION for behavior-coupledness.

### Test Layer Distribution
| Layer | Tests | Files |
|-------|-------|-------|
| Unit (schema/model) | 16 | `tests/test_timing_contract.py` |
| Integration (service + SQLite session) | 6 | `tests/test_timing_service.py` |
| Migration (SQLite + Alembic) | 5 | `tests/test_migration_006_timing.py` |
| Integration (ASGI HTTP) | 5 | `tests/test_api_incidentes.py` (Grupo C-39) |
| Structural (workflow JSON) | 8 | `tests/test_n8n_workflow.py` (Grupo 22) |
| **Total** | **40** | **5** |

---

## Spec Compliance Matrix

### Delta spec: `e2e-timing-instrumentation`

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Instante de ingreso | Ingreso persistido y normalizado a UTC | `test_timing_contract.py::test_ingresado_en_acepta_z_y_normaliza_a_utc`, `::test_ingresado_en_acepta_offset_y_normaliza_a_utc`, `test_timing_service.py::test_create_and_classify_persiste_ingresado_en_normalizado` | ✅ COMPLIANT |
| Instante de ingreso | Ausencia del instante no bloquea el alta | `test_timing_contract.py::test_ingresado_en_acepta_nulo`, `test_timing_service.py::test_create_and_classify_sin_ingresado_deja_nulo`, `test_api_incidentes.py::test_c39_alta_sin_ingreso_deja_latencia_nula` | ✅ COMPLIANT |
| Instante de ingreso | El ingreso refleja el borde del trigger (telefonía) | `test_n8n_workflow.py::test_c39_telefonia_sella_ingreso_aguas_arriba_del_agente` | ⚠️ PARTIAL (structural only; runtime path unverified — see HIGH concern #3) |
| Persistencia confirmada | Sellado en el alta | `test_timing_service.py::test_create_and_classify_sella_persistido_en`, `test_api_incidentes.py::test_c39_alta_con_ingreso_expone_latencia_e2e` | ✅ COMPLIANT |
| Persistencia confirmada | Inmutable ante updates posteriores | `test_timing_service.py::test_patch_modifica_updated_at_pero_no_persistido_en` | ✅ COMPLIANT |
| Persistencia confirmada | Independiente de `updated_at` | `test_timing_service.py::test_patch_modifica_updated_at_pero_no_persistido_en` | ✅ COMPLIANT |
| Derivación de latencia | Derivación correcta | `test_timing_contract.py::test_latencia_derivada_en_milisegundos`, `test_api_incidentes.py::test_c39_alta_con_ingreso_expone_latencia_e2e` | ✅ COMPLIANT |
| Derivación de latencia | Latencia nula si falta un instante | `test_timing_contract.py::test_latencia_nula_si_falta_ingresado`, `::test_latencia_nula_si_falta_persistido` | ✅ COMPLIANT |
| Derivación de latencia | Unidades en milisegundos (12.5 s → 12500) | `test_timing_contract.py::test_latencia_derivada_en_milisegundos` | ✅ COMPLIANT |
| Política de latencia negativa | Latencia negativa marcada como anomalía | `test_timing_contract.py::test_latencia_negativa_no_se_reporta_y_marca_anomalia`, `test_api_incidentes.py::test_c39_ingreso_futuro_dentro_de_tolerancia_marca_anomalia` | ✅ COMPLIANT |
| Política de latencia negativa | Excluida del corpus y del análisis | (none — no corpus in this change) | ⚠️ PARTIAL: mechanism (`latencia_e2e_ms=None` + `latencia_anomala=True`) tested; corpus wiring explicitly deferred (design Non-Goals / proposal) |
| Política de latencia negativa | Nunca aceptada en silencio | `test_latencia_negativa_no_se_reporta_y_marca_anomalia` | ✅ COMPLIANT |
| Validación del ingreso | Valor con zona horaria aceptado | `test_ingresado_en_acepta_z_y_normaliza_a_utc`, `::test_ingresado_en_acepta_offset_y_normaliza_a_utc` | ✅ COMPLIANT |
| Validación del ingreso | Valor sin zona horaria rechazado | `test_ingresado_en_rechaza_naive`, `test_api_incidentes.py::test_c39_ingreso_naive_rechazado_422` | ✅ COMPLIANT |
| Validación del ingreso | Futuro fuera de tolerancia rechazado | `test_ingresado_en_rechaza_futuro_fuera_de_tolerancia`, `test_api_incidentes.py::test_c39_ingreso_futuro_fuera_de_tolerancia_rechazado_422` | ✅ COMPLIANT |
| Validación del ingreso | Desfase dentro de tolerancia aceptado | `test_ingresado_en_acepta_futuro_dentro_de_tolerancia` | ✅ COMPLIANT |
| Validación del ingreso | Tolerancia por defecto 30 s | `test_tolerancia_de_futuro_por_defecto_es_30s` | ✅ COMPLIANT |
| Replays idempotentes | Replay conserva medición original | `test_timing_service.py::test_replay_idempotente_conserva_instantes_y_no_crea_fila` | ✅ COMPLIANT |
| Replays idempotentes | Replay no crea fila nueva | `test_replay_idempotente_conserva_instantes_y_no_crea_fila`, `test_alta_con_identificadores_distintos_crea_dos_filas` | ✅ COMPLIANT |
| Caveats por canal | Caveat de correo declarado | `docs/medicion-latencia-e2e.md:55-58` (inspection; no automated test) | ⚠️ PARTIAL (doc verified, not test-enforced) |
| Caveats por canal | Caveat de telefonía declarado | `docs/medicion-latencia-e2e.md:59-62` (inspection) | ⚠️ PARTIAL (doc verified, not test-enforced) |
| Caveats por canal | Análisis separado por canal | `docs/medicion-latencia-e2e.md:52-53` (inspection) | ⚠️ PARTIAL (documented practice, no enforcement) |

### Delta spec: `n8n-workflow`

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| N8N-TIMING-001 | Telefonía captura antes del agente | `test_n8n_workflow.py::test_c39_telefonia_sella_ingreso_aguas_arriba_del_agente` | ✅ COMPLIANT (structural) |
| N8N-TIMING-001 | Correo sella al recoger el mensaje (no `receivedDateTime`) | `test_c39_correo_sella_al_inicio_del_flujo_y_no_usa_received_date` | ✅ COMPLIANT (structural; validator is the first node after the Outlook trigger) |
| N8N-TIMING-001 | Web usa el instante de recepción | `test_c39_web_sella_en_marcar_canal_web` | ✅ COMPLIANT (structural) |
| N8N-TIMING-001 | Propagación al normalizador | `test_c39_normalizador_propaga_ingresado_en`, `test_c39_cada_trigger_sella_ingreso_hacia_el_normalizador` | ✅ COMPLIANT (structural) |
| N8N-TIMING-002 | El body incluye `ingresado_en` | `test_c39_body_incluye_ingresado_en_por_expresion` | ✅ COMPLIANT (structural) |
| N8N-TIMING-002 | Formato ISO-8601 con zona | seal uses `new Date().toISOString()`; `test_c39_web_sella_en_marcar_canal_web`/`test_c39_telefonia...` assert `toISOString` | ✅ COMPLIANT (structural) |
| N8N-TIMING-002 | Sin hardcodeo de host ni credenciales | `test_c39_body_sin_credenciales_y_host_por_env`, `test_http_backend_nodes_use_env_backend_url` | ✅ COMPLIANT |

**Compliance summary**: 31/40 scenarios COMPLIANT; 9/40 PARTIAL (structural-only or doc-only or deferred corpus); 0 FAILING; 0 UNTESTED.

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| `ingresado_en` persisted, nullable, UTC-normalized | ✅ Implemented | `models/incidente.py:155-158`; validator `schemas/incidente.py:138-163`; service `incidente_service.py:250` |
| `persistido_en` sealed once, immutable, no onupdate | ✅ Implemented | `models/incidente.py:166-169`; seal `incidente_service.py:276-282`; absent from `IncidenteUpdate` |
| `latencia_e2e_ms` derived, null on missing, negative→anomaly | ✅ Implemented | `schemas/incidente.py:258-291` |
| Tolerance default 30 s, configurable | ✅ Implemented | `settings.py:91-97` |
| Replay exclusion by construction | ✅ Implemented | `incidente_service.py:207-217`, `253-267` |
| Migration 006 additive/reversible, down_revision 005 | ✅ Implemented | `alembic/versions/006_add_timing_instrumentation.py`; verified on real PG |
| Approval recorded in migration header (governance HIGH, task 1.1) | ✅ Implemented | Migration docstring lines 29-33 |
| N8N telephony seal before agent | ✅ Implemented | node `Sellar ingreso telefonia`; `Llamada telefonica → Sellar → AI Agent` |
| N8N email/web seal at trigger edge | ✅ Implemented | email validator (first node after trigger); `Marcar canal web` |
| Normalizer propagates `ingresado_en` | ✅ Implemented | normalizer jsCode emits `ingresado_en: item.json.ingresado_en \|\| null` |
| POST body sends `ingresado_en` by expression | ✅ Implemented | workflow.json body `"ingresado_en": "={{ $('Normalizar entrada del incidente').item.json.ingresado_en }}"` |
| Documented contract + operational-guide pointer | ✅ Implemented | `docs/medicion-latencia-e2e.md`; referenced at `docs/operational-guide.md:444` |
| OpenAPI regenerated | ✅ Implemented | `docs/openapi.json` exposes `ingresado_en`, `persistido_en`, `latencia_e2e_ms`, `latencia_anomala` on `IncidenteRead` |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 ingress at trigger edge, before `AI Agent` in telephony | ✅ Yes | Connection chain verified |
| D2 `persistido_en` = last write before commit, immutable, no `onupdate`, not in update contract | ✅ Yes | `incidente_service.py:276-282`; model has no `onupdate`; `IncidenteUpdate` lacks the field |
| D3 derive latency, no denormalized column | ✅ Yes | computed_field; no latency column in migration |
| D4 ISO-8601 with tz required, naive rejected, future tolerance 30 s, nullable | ✅ Yes | validator + settings |
| D5 replay exclusion by construction (no workflow marker) | ✅ Yes | short-circuit before pseudonymization/classification |
| D6 per-channel caveats documented | ✅ Yes | doc §5 |
| D7 migration 006 additive, no backfill/indices, downgrade drops both | ✅ Yes | verified on PG |
| D8 boundary with c-40 (no c-40 wiring fixes duplicated) | ✅ Yes | C-39 structural tests only touch timing; no c-40 defects introduced |
| D9 negative latency → flagged anomalous, excluded, not clamped | ✅ Yes | `latencia_e2e_ms=None` + `latencia_anomala=True` (extra field, additive) |

---

## Deviations Found

**#1 — Extra field `latencia_anomala` (not named in delta specs)** — Severity: LOW / SUGGESTION
- Evidence: `schemas/incidente.py:279-291`; present in `docs/openapi.json` required list.
- Judgment: NOT a spec violation. The spec mandates "el valor SHALL marcarse como anomalo ... la
  anomalia SHALL quedar registrada para diagnostico" but does not name a field. `latencia_anomala`
  is the concrete fulfillment of D9 and is documented in `docs/medicion-latencia-e2e.md:15`. Recommend
  adding it to the delta spec for contract clarity.

**#2 — `latencia_e2e_ms` exposed only on `IncidenteRead` (detail), not `IncidenteListItem` (list)** — Severity: MEDIUM / WARNING
- Evidence: `schemas/incidente.py:294-310` (list item has no timing fields); `routes/incidentes.py:96`
  list endpoint returns `list[IncidenteListItem]`; OpenAPI list schema lacks latency.
- Judgment: Not a strict spec violation ("la representacion de lectura" is satisfied by the full read
  schema), and corpus wiring is an explicit Non-Goal. But it materially weakens the stated purpose
  ("dejar la latencia consultable para derivar `tiempo_automatizado_s`"): a corpus builder must issue
  one detail request per incident, not a single paginated list scan. Flag for the deferred corpus
  change; consider adding the derived latency to `IncidenteListItem`.

**#3 — Telephony ingress paired via `$('Sellar ingreso telefonia')` across the AI Agent — runtime UNVERIFIED** — Severity: HIGH
- Evidence: `n8n/workflow.json` validator jsCode:
  `return $('Sellar ingreso telefonia').item.json.ingresado_en || null;` wrapped in try/catch;
  chain `Llamada telefonica → Sellar ingreso telefonia → AI Agent → Se verifica lo que trajo la IA`.
- Judgment: Structurally correct and the only structurally-verifiable option (the agent does not
  propagate input fields). BUT n8n paired-item resolution across a LangChain agent node is a runtime
  contract; if pairing fails, the catch returns `null` and telephony `latencia_e2e_ms` is silently
  `null` for the DOMINANT (paid-LLM) channel — defeating the primary measurement goal without any
  error surfaced. Cannot be verified without an N8N runtime execution (not performed; would invoke
  the paid Gemini agent and Twilio trigger). Not a proven failure, therefore not classified CRITICAL,
  but it is the single largest residual risk in this change. Recommend a runtime smoke test on the
  telephony path BEFORE relying on telephony latency in the thesis, and/or a more defensive expression
  (`$('Sellar ingreso telefonia').first().json.ingresado_en`) with an explicit WARN log when null.

---

## Issues Found

**CRITICAL** (must fix before archive):
- None.

**WARNING** (should fix):
- Deviation #2: latency unavailable in the list projection; corpus consumer is detail-bound.
- Task 5.4 checkbox overstates automation: the automated integration subset does not exercise the
  Alembic 006 cycle on PostgreSQL (the test is SQLite-only). The cycle was verified manually and
  passed, but there is no regression guard. Recommend an integration-marked Alembic 006 test.
- Default integration invocation fails on credentials (`mesa_local_dev` vs live `mesa`). Environment
  configuration issue, not code, but it makes `pytest -m integration` unusable out of the box.

**SUGGESTION** (nice to have):
- Deviation #1: document `latencia_anomala` in the delta spec.
- `test_c39_ingreso_futuro_dentro_de_tolerancia_marca_anomalia` depends on request latency staying
  under the 10 s tolerance window — mild flakiness risk under a loaded CI; consider mocking the clock.
- N8N Grupo-22 assertions are substring/structural; inherent to the no-runtime pattern, but behavior
  runtime coverage for `#3` is missing.

---

## Governance Concern

HIGH governance domain (backend contract + DB migration + ingestion instrumentation):
- Migration is additive nullable with reversible downgrade — verified on real PostgreSQL. Good.
- Human approval is recorded in the migration header (task 1.1). Good.
- Residual HIGH concern: deviation #3 (telephony runtime pairing) is unverified for the dominant
  channel of the thesis measurement. No blocking code defect, but the measurement reliability that
  justified the HIGH governance level rests on an unproven runtime assumption.

---

## Verdict

**PASS WITH WARNINGS → READY TO ARCHIVE.**

No CRITICAL issue and no proven scenario failure. All 21 tasks are genuinely implemented (one
over-stated in method, not outcome), 40 C-39 tests pass, the full offline suite is green (431 passed /
1 xfailed), the integration subset passes (22/22) against a disposable PostgreSQL, the Alembic 006
upgrade/downgrade/re-upgrade cycle was independently reproduced on real PostgreSQL, ruff is clean,
OpenAPI is in sync, and `openspec validate --strict` passes.

Non-blocking residual risk to carry forward: (a) runtime-verify telephony `ingresado_en` propagation
across the AI Agent before trusting telephony latency (HIGH); (b) the deferred corpus change must
read latency via the detail endpoint or list exposure must be added (WARNING); (c) add an
integration-marked Alembic 006 regression test (WARNING).