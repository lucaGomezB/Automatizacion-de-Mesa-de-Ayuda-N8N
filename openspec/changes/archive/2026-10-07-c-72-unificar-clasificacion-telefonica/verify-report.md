# Verification Report

**Change**: c-72-unificar-clasificacion-telefonica
**Version**: spec-driven (delta) — N/A versioning
**Mode**: Strict TDD
**Governance**: ALTO
**Date**: 2026-10-07
**Verifier**: independent (sdd-verify), evidence from code + executed commands

---

## Verdict

**PASS WITH WARNINGS** — 0 CRITICAL.

All 37/37 tasks are complete, the four required commands pass, every non-conditional
spec scenario is backed by a passing test, and the measurement numbers reconcile
exactly with `evaluation/predicciones.json` (hybrid-v3) and `evaluation/report.md`.
Warnings are residual and non-blocking: one normalization scenario lacks a dedicated
test (pre-existing behavior), the main specs still carry the pre-archive AI Agent
requirements (synced only at archive time), no standalone TDD-evidence artifact exists
(OPSX mode), and the boundary-prompt tests are substring-based.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 37 |
| Tasks complete | 37 |
| Tasks incomplete | 0 |

`openspec list --json` → `completedTasks: 37, totalTasks: 37, status: complete`.
The last outstanding item (task 5.2, hybrid measurement) is checked `[x]` and the
uncommitted working-tree change is exactly `tasks.md` + the two docs (the closure).

---

## Build & Tests Execution (exact outputs)

### Backend unit subset
`cd App/Backend; pytest -m "not integration"`
```
1016 passed, 39 deselected, 1 xfailed, 251 warnings in 131.34s (0:02:11)
```
Exit code 0. The 39 deselected are the `@pytest.mark.integration` PostgreSQL subset.

### Lint
`cd App/Backend; ruff check .`
```
All checks passed!
```
Exit code 0.

### Evaluation suite
`cd evaluation; pytest`
```
118 passed in 9.99s
```
Exit code 0.

### OpenSpec strict validation
`openspec validate c-72-unificar-clasificacion-telefonica --strict`
```
Change 'c-72-unificar-clasificacion-telefonica' is valid
```
Exit code 0.

### Structural workflow suite (exists, ran)
`cd App/Backend; pytest tests/test_c72_n8n_workflow.py tests/test_c72_telefonia_cascade.py tests/test_c72_cost_guard.py tests/test_c72_prompt_boundaries.py tests/test_n8n_workflow.py -v`
```
180 passed, 1 xfailed, 1 warning in 2.66s
```

### Backend resilience + handoff contract
`cd App/Backend; pytest tests/test_gemini_retry.py tests/test_telefonia_handoff.py -q`
```
32 passed, 1 warning in 0.48s
```

**Coverage**: not enforced by `openspec/config.yaml` (no `coverage_threshold`);
reported as not-available. All four c-72 files are exercised by the passing runs above.

---

## Spec Compliance Matrix

Legend: PROVEN = passing test exercises the scenario; N/A = scenario is conditional on
a state the author's binding decision removed (vacuously satisfied, not a gap).

### classification-resilience (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| CR-1 | Resiliencia canal telefonico | Falla transitoria no aborta la clasificacion | `test_gemini_retry.py > test_timeout_se_reintenta_y_agotado_es_fallback`, `test_max_retries_cero_restaura_un_solo_intento` | PROVEN |
| CR-2 | Resiliencia canal telefonico | El tope total de invocaciones pagas queda acotado | `test_gemini_retry.py > test_settings_defaults_de_resiliencia_seguros`; `test_n8n_workflow.py > test_c36_no_paid_node_has_unbounded_or_implicit_retry` | PROVEN |
| CR-3 | Resiliencia canal telefonico | Agotado el reintento de transporte se conserva camino terminal | `test_gemini_retry.py > test_timeout_se_reintenta_y_agotado_es_fallback`; `test_c72_n8n_workflow.py > test_2_5_existe_camino_terminal_con_revision_humana` | PROVEN |
| CR-4 | Clasificacion telefonica determinista-primero | El cortocircuito determinista evita la llamada paga | `test_c72_cost_guard.py > test_4_3_cortocircuito_deterministico_no_reserva` | PROVEN |
| CR-5 | Clasificacion telefonica determinista-primero | La escalacion de telefonia queda sujeta a la guarda | `test_c72_cost_guard.py > test_4_1_escalacion_reserva_backend_gemini` | PROVEN |
| CR-6 | Clasificacion telefonica determinista-primero | El pipeline telefonico es el mismo que correo y web | `test_c72_telefonia_cascade.py > test_1_2..., test_1_4...`; `test_n8n_workflow.py > test_three_channels_converge_on_normalizer` | PROVEN |

### n8n-workflow (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| V-1 | Validacion respuesta (§H.3) | Respuesta valida aceptada | (conditional on conserved reduced agent) | N/A |
| V-2 | Validacion respuesta (§H.3) | Categoria fuera del conjunto | (conditional) | N/A |
| V-3 | Validacion respuesta (§H.3) | Sector adicional invalido | (conditional) | N/A |
| V-4 | Validacion respuesta (§H.3) | JSON malformado | (conditional) | N/A |
| V-5 | Validacion respuesta (§H.3) | Confianza fuera de rango | (conditional) | N/A |
| R-1 | Ruteo por umbral | Confianza por encima del umbral crea el incidente | `test_n8n_workflow.py > test_if_nodes_use_threshold_070, test_if_nodes_use_gte_operator` (node `Entrada valida`, `gte 0.7`) | PROVEN |
| R-2 | Ruteo por umbral | Confianza por debajo deriva a revision humana | `test_n8n_workflow.py > test_if_nodes_have_conditions, test_if_nodes_use_threshold_070` (false branch) | PROVEN |
| R-3 | Ruteo por umbral | Entrada valida acepta revision forzada con confianza baja | `test_n8n_workflow.py > test_if_nodes_reference_confianza` (combinator `or`, condition `revision_forzada == true`) | PROVEN |
| R-4 | Ruteo por umbral | Telefono valida su entrada como los demas canales | `test_n8n_workflow.py > test_c69_normalizer_correo_y_telefonia_intactos`; `test_c52_webhook_telefonia_existe_y_esta_autenticado` | PROVEN |
| R-5 | Ruteo por umbral | Confianza en el limite exacto | `test_n8n_workflow.py > test_if_nodes_use_gte_operator` (operator `gte`, 0.70 inclusive) | PROVEN |
| R-6 | Ruteo por umbral | El gate post-POST lee el flag del backend | `test_n8n_workflow.py > test_revision_humana_condition_references_flag` | PROVEN |
| R-7 | Ruteo por umbral | Flag verdadero deriva a notificacion y auditoria | `test_n8n_workflow.py > test_revision_humana_true_branch_notifies_operator` | PROVEN |
| R-8 | Ruteo por umbral | Flag falso continua con las confirmaciones | `test_n8n_workflow.py > test_revision_humana_false_branch_routes_and_audits` | PROVEN |
| N-1 | Normalizacion de canales | Correo electronico normalizado | `test_n8n_workflow.py > test_normalizer_canal_correo` | PROVEN |
| N-2 | Normalizacion de canales | Transcripcion telefonica normalizada (sin nodo de clasificacion) | `test_n8n_workflow.py > test_normalizer_canal_telefonia, test_c69_normalizer_correo_y_telefonia_intactos` | PROVEN |
| N-3 | Normalizacion de canales | Canal de origen invalido rechazado | (no dedicated test; code path present) | ⚠️ PARTIAL |
| T-1 | Trigger Webhook Twilio | El disparador telefonico existe y alimenta el flujo | `test_n8n_workflow.py > test_c52_webhook_telefonia_existe_y_esta_autenticado` | PROVEN |
| T-2 | Trigger Webhook Twilio | No hay parsing de CloudEvent | `test_n8n_workflow.py > test_c52_sin_parsing_de_cloudevent` | PROVEN |
| T-3 | Trigger Webhook Twilio | El canal telefonico queda identificado como "telefonia" | `test_n8n_workflow.py > test_normalizer_canal_telefonia, test_c52_sello_telefonia_es_passthrough` | PROVEN |
| C-1 | Credenciales declaradas | Los nodos que requieren credenciales las declaran | `test_n8n_workflow.py > test_c55_email_send_nodes_declare_smtp_credentials, test_c52_webhook_telefonia_existe_y_esta_autenticado` | PROVEN |
| I-1 | N8N-INTAKE-002 | El POST telefonico NO incluye clasificacion precalculada | `test_c72_n8n_workflow.py > test_2_2_post_no_incluye_clasificacion_precalculada` | PROVEN |
| I-2 | N8N-INTAKE-002 | El POST de correo incluye el Message-ID de origen | `test_n8n_workflow.py > test_c55_normalizer_origen_message_id_from_metadata_with_uid_fallback, test_c69_post_envia_origen_message_id_del_normalizador` | PROVEN |
| I-3 | N8N-INTAKE-002 | El marcador de origen es explicito | `test_c72_n8n_workflow.py > test_2_2...` (asserts `origen_evento`) | PROVEN |
| U-1 | N8N-UNIFY-001 | Los tres canales clasifican en el backend | `test_c72_telefonia_cascade.py > test_1_2..., test_1_4...`; `test_c72_n8n_workflow.py > test_2_4_no_existe_ai_agent_ni_modelo_de_lenguaje` | PROVEN |
| U-2 | N8N-UNIFY-001 | n8n no saltea la cascada | `test_c72_n8n_workflow.py > test_2_2_post_no_incluye_clasificacion_precalculada` | PROVEN |
| TM-1 | N8N-TIMING-001 | Telefonia captura antes de la cascada (Sellar -> Normalizar) | `test_n8n_workflow.py > test_c52_sello_telefonia_es_passthrough, test_c39_telefonia_sella_ingreso_aguas_arriba_del_agente` | PROVEN |
| TM-2 | N8N-TIMING-001 | Telefonia propaga el sello del backend | `test_n8n_workflow.py > test_c52_f1_sello_lee_el_body_anidado_y_aplana_al_item` | PROVEN |
| TM-3 | N8N-TIMING-001 | Correo sella al recoger el mensaje | `test_n8n_workflow.py > test_c39_cada_trigger_sella_ingreso_hacia_el_normalizador`; `test_timing_contract.py` | PROVEN |
| TM-4 | N8N-TIMING-001 | Web usa el instante de recepcion | `test_n8n_workflow.py > test_c39_cada_trigger_sella_ingreso_hacia_el_normalizador` | PROVEN |
| TM-5 | N8N-TIMING-001 | Propagacion al normalizador | `test_n8n_workflow.py > test_c39_normalizador_propaga_ingresado_en` | PROVEN |
| P-1 | N8N-PHONE-003 | El webhook recibe el payload del handoff | `test_telefonia_handoff.py > test_build_payload_tiene_exactamente_las_cuatro_claves` | PROVEN |
| P-2 | N8N-PHONE-003 | La cascada consume la descripcion pseudonimizada | `test_c72_telefonia_cascade.py > test_1_5_cascada_recibe_la_descripcion_pseudonimizada` | PROVEN |
| P-3 | N8N-PHONE-003 | El CallSid se envia como identificador de origen | `test_n8n_workflow.py > test_c52_post_persistencia_envia_callsid_como_origen` | PROVEN |

### runtime-cost-guard (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| RC-1 | Enforcement AI Agent n8n | La guarda permite y el AI Agent se invoca | (conditional on conserved reduced agent) | N/A |
| RC-2 | Enforcement AI Agent n8n | La guarda deniega y el AI Agent no se invoca | `test_c72_cost_guard.py > test_4_3_guarda_deniega_degrada_a_fallback_con_revision_humana` (backend equivalent) | PROVEN |
| RC-3 | Enforcement AI Agent n8n | La clasificacion telefonica no reserva `n8n_gemini` | `test_c72_cost_guard.py > test_4_1_workflow_no_reserva_n8n_gemini` | PROVEN |
| RC-4 | Enforcement AI Agent n8n | La escalacion telefonica reserva `backend_gemini` | `test_c72_cost_guard.py > test_4_1_escalacion_reserva_backend_gemini` | PROVEN |

### sector-assignment (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| SA-1 | ASG-012 | Telefono usa la misma cascada que correo y web | `test_c72_telefonia_cascade.py > test_1_4_telefonia_sin_precalculada_usa_la_cascada` | PROVEN |
| SA-2 | ASG-012 | No se persiste una clasificacion precalculada de telefonia | `test_c72_telefonia_cascade.py > test_1_2_telefonia_con_precalculada_gana_la_cascada` | PROVEN |
| SA-3 | ASG-012 | El contrato del resultado no cambia | `test_c72_telefonia_cascade.py > test_1_2...` + existing API contract suite `test_api_incidentes.py` | PROVEN |

### sector-taxonomy (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| TX-1 | TAX-003 | Regla Software para accesos a aplicaciones | `test_c72_prompt_boundaries.py > test_3_1_regla_software_para_accesos_a_aplicaciones` | PROVEN |
| TX-2 | TAX-003 | Regla Hardware para digitalizacion | `test_c72_prompt_boundaries.py > test_3_1_regla_hardware_para_digitalizacion` | PROVEN |
| TX-3 | TAX-003 | Regla Sistemas para infraestructura | `test_c72_prompt_boundaries.py > test_3_1_regla_sistemas_para_infraestructura` | PROVEN |
| TX-4 | TAX-003 | El prompt es unico y no introduce sectores nuevos | `test_c72_prompt_boundaries.py > test_3_1_prompt_usa_los_cinco_strings_canonicos_sin_tildes` | PROVEN |
| TX-5 | TAX-003 | No hay prompt divergente en telefonia | `test_c72_prompt_boundaries.py > test_3_3_no_hay_prompt_divergente_en_n8n` | PROVEN |

### telefonia-stt-intake (delta)

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| ST-1 | Clasificacion propiedad del backend | La clasificacion telefonica se resuelve en el backend | `test_c72_telefonia_cascade.py > test_1_4_telefonia_sin_precalculada_usa_la_cascada` | PROVEN |
| ST-2 | Clasificacion propiedad del backend | El handoff no lleva clasificacion precalculada | `test_telefonia_handoff.py > test_build_payload_tiene_exactamente_las_cuatro_claves` (4 keys exactly) | PROVEN |
| ST-3 | Clasificacion propiedad del backend | La clasificacion usa la representacion pseudonimizada | `test_c72_telefonia_cascade.py > test_1_5_cascada_recibe_la_descripcion_pseudonimizada` | PROVEN |

**Compliance summary**: 48/54 scenarios PROVEN, 6 N/A-by-retirement (V-1..V-5, RC-1 — the
spec text makes them conditional on "si el workflow conserva una invocacion reducida al
AI Agent"; OQ1=A retired the agent entirely), 1 ⚠️ PARTIAL (N-3), 0 FAILING, 0 untested.

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Telefonia clasifica por la cascada (D1) | ✅ Implemented | `incidente_service.py:381-384` — `es_telefonia` bypasses `_result_from_precalculated`; always `await self._classifier.classify(texto_pseudonimizado)`. Proven at runtime by `test_1_2`. |
| Cascada recibe la pseudonimizada (D1/ST-3) | ✅ Implemented | `create_and_classify` pseudonymizes at the single canonical point then passes `resultado_pseudo.texto` to `_resolve_classification`. `test_1_5` asserts `[EMAIL]` present and raw email absent. |
| n8n POST no envia `clasificacion` (D2) | ✅ Implemented | POST `jsonBody` = `{descripcion, prioridad, canal_origen_id, origen_message_id, origen_evento, ingresado_en}`. No `clasificacion`/`sector_predicho`. |
| AI Agent retirado del workflow (D3, OQ1=A) | ✅ Implemented | `grep` of `n8n/workflow.json`: 0 matches for `AI Agent`, `langchain`, `Google Gemini`, `n8n_gemini`. Node count reduced 38→28. |
| Camino terminal con revision humana (D3, OQ3) | ✅ Implemented | Post-POST IF `Requiere revision humana` reads `$json.requiere_revision_humana`, route to `Notificar operador designado` + `Registro de auditoria`. |
| Cost guard trasladado (D5, OQ2=A) | ✅ Implemented | Workflow has no cost-guard reserve; `classifiers/hybrid.py:197` reserves `PROVIDER_BACKEND_GEMINI` on escalation; deterministic short-circuit reserves nothing. |
| Reglas de frontera en prompt compartido (D4) | ✅ Implemented | `docs/prompt_gemini.txt` §`REGLAS DE FRONTERA` with acceder/iniciar sesion→Software, digitalizacion/escaner/impresora→Hardware, servidor/red/SMTP/VM→Sistemas; five canonical strings, no tilde variant in the rules block. |
| Handoff telefonico sin clasificacion (ST-2) | ✅ Implemented | `build_telefonia_handoff_payload` returns exactly `{descripcion_pseudonimizada, call_sid, caller_number, ingresado_en}`. |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 Telefonia por cascada | ✅ Yes | `_resolve_classification` keys off resolved channel name via `es_canal_telefonia`. |
| D2 Retiro del atajo precalculado | ✅ Yes | Field kept in `IncidenteCreate` for compatibility; ignored for telephony only (correo/web preserved, `test_1_4_correo/web`). |
| D3 Reestructuracion workflow (OQ1=A, OQ3=A) | ✅ Yes | Agent and refinement loop fully removed; terminal revision preserved. |
| D4 Prompt unico con reglas de frontera | ✅ Yes | Single prompt; no divergent n8n prompt (`sector_predicho` absent from workflow). |
| D5 Traslado de costo | ✅ Yes | `n8n_gemini` unused; `backend_gemini` on escalation. |
| D6 Medicion offline determinista-primero | ✅ Yes | Numbers in §4.2/§4.3 reconciled (see below). |
| D7 Documentacion | ✅ Yes | `docs/anexo_h_prompt_gemini.md`, thesis sections, and the c-72 note updated (commit `3f8a0ff`). |
| D8 TDD + tests estructurales | ⚠️ Partial | TDD-shaped tests exist and pass; no standalone "TDD Cycle Evidence" artifact (OPSX mode does not emit `apply-progress`). |
| D9 Governance ALTO | ✅ Yes | OQ decisions recorded and binding. |

---

## Measurement Spot-Check (task 5.2 closure)

Independently recomputed from `evaluation/predicciones.json`
(`cache_meta.classifier_version = hybrid-v3`, 200 cases) filtered to the 81 telephony
cases (`canal_origen == "llamada telefónica"`), using `evaluation/metrics.py` and the
`generar_reporte` conventions:

| Metric (telephony, 81) | Doc value | Recomputed | Match |
|---|---|---|---|
| Etapa determinista / Gemini | 58 / 23 | 58 / 23 (fallback 0) | ✅ |
| Exactitud estricta | 0.6543 | 53/81 = 0.6543 | ✅ |
| Macro-F1 (canonical pairs) | 0.4783 | 0.4783 (per-class: SI .5833 / HW .8387 / SW .6538 / BD 0 / Sis .3158) | ✅ |
| Micro-F1 | 0.6034 | 0.6034 | ✅ |
| Subset accuracy | 0.3580 | 0.3580 | ✅ |
| Short-circuit rate | 0.7160 (58/81) | 0.7160 | ✅ |
| Strict acc. of short-circuited subset | 0.6207 (36/58) | 36/58 = 0.6207 | ✅ |
| Deterministic strict acc. (81) | 0.4444 | 36/81 = 0.4444 | ✅ |

Global (`evaluation/report.md`, 200 cases): strict 0.7350, macro-F1 0.5207, micro 0.6654,
subset 0.4300, etapas det 131 / gemini 69 — all match `docs/c-72-...md` §4.3. No
inconsistency found. The determinista-only macro-F1 0.3810 (telefonia) and 0.4196
(global) come from the separate offline `evaluation/deterministic_measurement.py` run and
are referenced consistently with `docs/deterministic_calibration.md`.

Minor note: `0.4783 - 0.3810 = 0.0973`, reported as `+0.0974`; both inputs are themselves
rounded to 4 decimals, so this is a display-rounding artifact, not a data inconsistency.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ | No `apply-progress` artifact (OPSX mode). TDD structure is embedded in `tasks.md` and in the test-module docstrings. |
| All tasks have tests | ✅ | Code-bearing tasks (1.x, 2.x, 3.x, 4.x) each map to the four c-72 test modules; all exist and pass. |
| RED confirmed (tests exist) | ✅ | `test_c72_telefonia_cascade.py`, `test_c72_n8n_workflow.py`, `test_c72_cost_guard.py`, `test_c72_prompt_boundaries.py` all present. |
| GREEN confirmed (tests pass) | ✅ | 180 passed / 1 xfailed on the targeted run; 1016 passed on the full offline subset. |
| Triangulation adequate | ✅ | Each module has 3-8 distinct cases covering happy path + edge + regression (correo/web preserved; guard-denied fallback; retired-agent assertions). |
| Safety Net for modified files | ➖ | Not verifiable from artifacts; tasks 1.1/2.1/0.7 declare baselines but no raw logs persisted. |

**TDD Compliance**: 4/6 verified, 2 not independently verifiable from stored artifacts.

---

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | ~5 | `test_c72_cost_guard.py` (HybridClassifier + fake guard) | pytest |
| Integration (ASGI) | ~5 | `test_c72_telefonia_cascade.py` | pytest + httpx ASGI |
| Structural (workflow/prompt JSON+text) | ~27 | `test_c72_n8n_workflow.py`, `test_c72_prompt_boundaries.py`, `test_n8n_workflow.py` | pytest |
| **Total (c-72 focused)** | **39** | **4** | |

No E2E layer (n8n UI not scripted) — acceptable given the structural suites assert the
exported workflow invariants.

---

## Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `test_c72_prompt_boundaries.py` | 100-130 | `assert "acceder" in text` / `any(k in text ...)` | Substring presence only; does not prove the rule *direction*. Direction is covered by the companion `test_3_1_regla_*` assertions. | SUGGESTION |

**Assertion quality**: 0 CRITICAL, 0 WARNING (1 SUGGESTION). No tautologies, no ghost
loops over possibly-empty collections, no type-only-only assertions; every test calls
production code (API client, classifier, or workflow JSON).

---

## Issues Found

**CRITICAL** (must fix before archive):
- None.

**WARNING** (should fix):
1. **N-3 untested**: the "canal de origen invalido rechazado" normalization scenario has
   no dedicated executing test. The code path exists (`canal_invalido`, `es_valido=false`,
   `confianza=0.0`) but is unverified. Pre-existing behavior, not changed by c-72.
2. **Main specs not yet synced**: `openspec/specs/n8n-workflow/spec.md` and
   `openspec/specs/runtime-cost-guard/spec.md` still mandate the pre-c-72 AI Agent
   requirements (e.g. main n8n-workflow line 192 routes the webhook through the AI Agent;
   line 277 caps agent refinement). These are removed/rewritten by the c-72 delta but the
   sync happens only at archive. Expected for an unarchived change — run the archive step
   to reconcile. The workflow itself is clean (0 AI Agent / 0 `n8n_gemini`).
3. **No TDD-evidence artifact**: Strict TDD was enabled but no `apply-progress`/TDD table
   exists to cross-check RED/GREEN per task. Evidence was reconstructed from test files.

**SUGGESTION** (nice to have):
4. Boundary-prompt tests are substring-based; consider asserting the rule→sector mapping
   semantically (e.g. one rule line per frontier case).
5. `+0.0974` delta in §4.3 is a rounding display of `0.4783 - 0.3810 = 0.0973`; consider
   stating it with matching precision.
6. `n8n/workflow.json` normalizer `jsCode` retains a stale comment: "telefonia: propaga
   la confianza del validador de IA (ya existe en el item)." Functionally harmless; the
   code now derives confianza from `es_valido` for all three channels.

---

## Adversarial Checks

- **Five canonical strings UNCHANGED**: ✅ `App/Backend/app/constants.py` `SECTORES_CANONICOS`
  is byte-identical (`Seguridad Informatica`, `Soporte Tecnico Hardware`,
  `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`). The c-72 commit added only
  `CANAL_TELEFONIA = "llamada telefónica"` and `es_canal_telefonia()`; it did not touch the
  sector tuple.
- **`evaluation/corpus.py::_a_float` UNCHANGED**: ✅ `git diff 771b392..HEAD -- evaluation/corpus.py`
  is empty; last modification predates c-72 (`c73fde4`). `_a_float` present at line 138.
- **No telephony AI Agent in the workflow**: ✅ zero occurrences of `AI Agent`,
  `@n8n/n8n-nodes-langchain.*`, `Google Gemini Chat Model`, `n8n_gemini`. Verified by test
  `test_2_4_*` and by direct grep.
- **Handoff carries no precalculated classification**: ✅ payload key set is exactly
  `{descripcion_pseudonimizada, call_sid, caller_number, ingresado_en}`.
- **`_result_from_precalculated` still reachable only for correo/web**: ✅ guarded by
  `not es_telefonia`; triangulated by `test_1_4_correo_con_precalculada_conserva_el_atajo`
  and `test_1_4_web_con_precalculada_conserva_el_atajo`.

---

## Residual Warnings (summary)

- W1: normalization invalid-channel scenario lacks a dedicated test (PARTIAL).
- W2: main specs still carry the AI Agent requirements pending archive sync.
- W3: no standalone TDD-evidence artifact for strict-TDD cross-check.
- S1-S3: cosmetic/methodological suggestions above.

The change is complete and internally consistent; it is ready to proceed to archive once
the main-spec sync (which is the archive's job) is executed. No CRITICAL blockers.
