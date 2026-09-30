# Verification Report (Post-Verify Fix Pass): c-52-telefonia-transcripcion-async

**Date**: 2026-09-23
**Verifier**: independent adversarial verification (sdd-verify) — re-ran all commands, did not trust apply summaries
**Mode**: Standard (Strict TDD not declared as a change gate; TDD evidence inspected where asserted)
**Governance**: CRITICAL (Twilio signature fail-closed, encrypted transcript, PII boundary)
**Scope**: the WHOLE current working-tree delta on top of commit `63c45ae`, addressing warnings W1-W6 from `verify-report.md`.

---

## Verdict

**PASS WITH WARNINGS** — the fix pass is behaviorally correct, security-critical paths remain sound, and the offline suite is fully green. W3, W4, W6 and W5 are implemented and covered by passing tests. No CRITICAL issues.

Two warnings remain: (1) a NEW documentation drift — the untracked runbook `docs/runbook-verificacion-telefonia-c52.md` §7.5 still documents W5 recovery as **manual**, directly contradicting the new automatic retry; (2) the concurrent-claim scenario is only simulated (monkeypatched no-op / SQLite rowcount), not exercised under real PostgreSQL row locking.

Note on process: W1/W2 were reported as fixed in an "uncommitted post-verify pass", but `git status` shows `n8n/twilio/README.md` and `docs/operational-guide.md` are **clean** — their corrections are already part of commit `63c45ae` (verified via `git show 63c45ae`). The current state is consistent; only the narrative about *where* the fix lives is inaccurate.

---

## Method

1. Read the change artifacts (`proposal.md`, `design.md`, `tasks.md`, `verify-report.md`) and every delta spec under `specs/**`.
2. Read the full current code (not diffs alone) for `routes/telefonia.py`, `services/telefonia_service.py`, `repositories/telefonia_ingreso_repository.py`, `cost_guard/twiml.py`, `utils/n8n_webhook.py`, `core/database.py`, the model enum, and the new/changed tests.
3. Inspected `git diff` of the uncommitted working tree and `git log -1`.
4. Re-ran every required command plus targeted telefonia/TwiML/migration suites and mapped each passing test to its spec scenario.

---

## Commands and Exact Results

| Command | Result |
|---------|--------|
| `cd App/Backend; pytest -m "not integration" -q` | **670 passed, 25 deselected, 1 xfailed** (62.25s) — up from 649 pre-fix |
| `cd App/Backend; ruff check .` | **All checks passed!** (exit 0) |
| `cd App/Backend; pytest tests/test_openapi_sync.py -v` | **5 passed** |
| `openspec validate --strict --changes c-52-telefonia-transcripcion-async` | **1 passed, 0 failed** |
| `pytest tests/test_migration_008_telefonia.py -v` | **4 passed** (chain, upgrade-table, unique index, downgrade+re-upgrade) |
| `pytest tests/test_api_telefonia.py tests/test_telefonia_service.py tests/test_telefonia_ingreso_repository.py tests/test_twiml_record.py tests/test_migration_008_telefonia.py tests/test_cost_guard_backend_stt.py -v` | **62 passed** |
| `pytest tests/test_n8n_workflow.py --collect-only -q` | **150 tests collected** (guide/structural count still consistent) |

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 44 |
| Tasks complete | 43 |
| Tasks incomplete | 1 (8.4 — live call, human blocker, unchanged) |

---

## W1-W6 Disposition

| Warn | Fix claimed | Verified state | Verdict |
|------|-------------|----------------|---------|
| W1 | `n8n/twilio/README.md` stale | Current file says `SIN transcribe`, `<Record> mono`; no `twilioTrigger`/`call-summary`/`no lo consume` markers remain. Fixed **in `63c45ae`**, not uncommitted. | RESOLVED |
| W2 | `docs/operational-guide.md` §11.2 stale | Line 563 now reads `<Record> mono (SIN transcribe)`; §11.7 consistent. Fixed in `63c45ae`. | RESOLVED |
| W3 | Signature gate as FastAPI dependency | Confirmed: `require_twilio_signature` is `SignatureDep` resolved before form validation. Tests prove ordering both ways (missing fields + no/bad sig → 401; valid sig + missing fields → 422). | RESOLVED |
| W4 | Migration test for 008 | `tests/test_migration_008_telefonia.py` genuinely runs Alembic upgrade head, inspects the table/indexes, and downgrades back to 007 and re-upgrades. | RESOLVED |
| W6 | Explicit mono | `channels="mono"` added to `app/cost_guard/twiml.py` and `n8n/twilio/twiml.xml`, and both `test_twiml_record.py` and `test_runtime_cost_guard.py` assert it. | RESOLVED |
| W5 | State-gated retry | Implemented (service + repo + route + delta spec). Details below. | RESOLVED (test-strength caveat) |

---

## Spec Compliance Matrix — `specs/telefonia-stt-intake/spec.md` (touched spec)

| Requirement | Scenario | Executing test | Result |
|-------------|----------|----------------|--------|
| Firma fail-closed | Firma válida admite | `test_api_telefonia.py > test_firma_valida_acepta_el_callback` | COMPLIANT |
| Firma fail-closed | Firma ausente/inválida → 401 | `test_firma_ausente_rechaza_401`, `test_firma_invalida_rechaza_401`, `test_firma_ausente_con_campos_faltantes_rechaza_401`, `test_firma_invalida_con_campos_faltantes_rechaza_401` | COMPLIANT (W3 closed) |
| Firma fail-closed | Token no configurado → 401 | `test_token_no_configurado_rechaza_401` | COMPLIANT |
| Firma fail-closed | No requiere `From` | `test_callback_no_requiere_from` | COMPLIANT |
| Sellado del ingreso | Sella antes de descarga/STT | `test_telefonia_service.py > test_latencia_incluye_stt_entre_sello_y_persistencia` | COMPLIANT |
| Sellado del ingreso | Latencia incluye el backend | same (delta sello↔persistencia) | COMPLIANT |
| Sellado del ingreso | Sello se propaga a n8n | `test_telefonia_handoff.py > test_build_payload_tiene_exactamente_las_cuatro_claves` | COMPLIANT |
| Idempotencia + reintento | Repetido `transcrito` no reprocesa | `test_telefonia_service.py > test_callsid_transcrito_no_reprocesa` | COMPLIANT |
| Idempotencia + reintento | Repetido `pendiente` no reprocesa | `test_callsid_pendiente_no_reprocesa` | COMPLIANT |
| Idempotencia + reintento | Repetido en error lo reprocesa | `test_reintento_reprocesa_desde_estado_terminal_de_error[guarda_denegada/error_descarga/error_stt]` | COMPLIANT |
| Idempotencia + reintento | Reintento preserva el sello | `test_reintento_preserva_ingresado_en` | COMPLIANT |
| Idempotencia + reintento | Solo un reintento concurrente reclama | `test_claim_de_cero_filas_no_reprocesa` (monkeypatched claim=False) + `test_claim_for_retry_no_reclama_estados_no_terminales` | **PARTIAL** (see W-CONC) |
| Idempotencia + reintento | `CallSid` nuevo inicia | `test_flujo_feliz_respeta_el_orden_y_persiste` | COMPLIANT |
| Idempotencia + reintento | Idempotencia precede reserva paga | `test_callsid_repetido_no_reserva_ni_descarga`, `test_callsid_transcrito_no_reprocesa` (`guard.calls == []`) | COMPLIANT |
| Respuesta HTTP por estado | Fallo transitorio → 503 | `test_fallo_descarga_devuelve_503`, `test_fallo_stt_devuelve_503` | COMPLIANT |
| Respuesta HTTP por estado | No transitorios → 200 | `test_transcrito_devuelve_200`, `test_guarda_denegada_devuelve_200` | **PARTIAL** (`pendiente` leg not directly asserted) |
| Descarga autenticada | Descarga con Basic auth | `test_twilio_media.py > test_descarga_usa_basic_auth_y_devuelve_contenido` | COMPLIANT |
| Descarga autenticada | Fallo de descarga no invoca STT | `test_fallo_descarga_persiste_estado_sin_abortar` (`stt.calls == []`) | COMPLIANT |
| Descarga autenticada | No descarga sin reserva | `test_guarda_denegada_persiste_estado_y_no_descarga` | COMPLIANT |
| STT dedicado | Produce texto | `test_flujo_feliz_respeta_el_orden_y_persiste` | COMPLIANT |
| STT dedicado | Verbatim + `es-419` | `test_gemini_stt.py > test_transcription_config_va_por_generation_config_en_verbatim` | COMPLIANT |
| STT dedicado | Independiente de Twilio | `test_twiml_record.py > test_ningun_documento_solicita_transcribe[allowed/record-complete/denied]` | COMPLIANT |
| Pseudonimización / doble representación | Pseudonimiza antes del handoff | `test_telefonia_service.py > test_pseudonimiza_antes_del_handoff` | COMPLIANT |
| Pseudonimización / doble representación | Crudo persistido cifrado | `test_telefonia_ingreso_model.py > test_transcript_crudo_se_cifra_y_se_descifra_por_el_orm` | COMPLIANT |
| Pseudonimización / doble representación | Ambas representaciones pobladas | `test_flujo_feliz_respeta_el_orden_y_persiste` | COMPLIANT |
| Persistencia / vínculo | Ingreso trazable | model + service tests | COMPLIANT |
| Persistencia / vínculo | Unicidad de `CallSid` efectiva | `test_telefonia_ingreso_model.py > test_call_sid_duplicado_colisiona` | COMPLIANT |
| Persistencia / vínculo | Vínculo con incidente | `test_link_incidente_registra_el_vinculo` | COMPLIANT |
| Handoff autenticado | Solo texto pseudonimizado | `test_build_payload_tiene_exactamente_las_cuatro_claves`, `test_payload_pseudonimizado_no_contiene_pii_cruda`, `test_notify_envia_payload_exacto_con_secreto` (`b"transcript" not in body`) | COMPLIANT |
| Handoff autenticado | Se autentica (secreto) | `test_notify_envia_payload_exacto_con_secreto` | COMPLIANT |
| Handoff autenticado | `CallSid` identifica el origen | `test_n8n_workflow.py > test_c52_post_persistencia_envia_callsid_como_origen` | COMPLIANT |
| Recuperación fallo/denegación | Guarda denegada conserva | `test_guarda_denegada_persiste_estado_y_no_descarga` | COMPLIANT |
| Recuperación fallo/denegación | Fallo de STT registrado | `test_fallo_stt_persiste_estado_sin_abortar` | COMPLIANT |
| Recuperación fallo/denegación | Fallo no descarta el ingreso | `test_api_telefonia.py > test_fallo_descarga_persiste_el_ingreso_tras_503` | COMPLIANT |
| Recuperación fallo/denegación | El reintento es automático | `test_reintento_reprocesa_desde_estado_terminal_de_error[...]` + 503 tests | COMPLIANT |
| Grabación mono | Mono y declara callbacks | `test_allowed_record_es_mono_con_callbacks_y_sin_transcribe`, `test_solo_el_record_admitido_declara_canales_mono`, `test_runtime_cost_guard.py > test_twiml_xml_es_valido_y_graba_mono_con_callbacks` | COMPLIANT (W6 closed) |
| Grabación mono | No solicita transcribe embebido | `test_ningun_documento_solicita_transcribe` | COMPLIANT |
| Grabación mono | Mensaje posterior alcanzable | `test_record_complete_expone_un_say_alcanzable` | COMPLIANT |

**Compliance summary**: 36 COMPLIANT / 2 PARTIAL / 0 FAILING / 0 UNTESTED (telefonia-stt-intake). The other four delta specs (`n8n-workflow`, `runtime-cost-guard`, `e2e-timing-instrumentation`, `data-pseudonymization`) are unchanged by this fix pass and remained green in the full run; their original matrix stands.

---

## Security Re-verification (adversarial, read the code not just tests)

| Check | Evidence | Result |
|-------|----------|--------|
| Signature fail-closed after dependency refactor | `routes/telefonia.py:89-117` — token missing → 401; `verify_signature` over `str(request.url)` + `await request.form()`. Exposed as `SignatureDep`, resolved before form validation (`test_firma_ausente_con_campos_faltantes_rechaza_401` = 401, `test_firma_valida_con_campos_faltantes_devuelve_422` = 422). `/record-complete` also requires it (`test_record_complete_exige_firma`). | PASS |
| Dependency runs before form validation | FastAPI solves sub-dependencies before body/form params; empirically proven by the two ordering tests above (401 wins over 422 only when signature is the failing gate; valid signature falls through to 422). | PASS |
| Pseudonymization before handoff | `telefonia_service.py:321-339` — `pseudonymize(...)` then payload built from `resultado.texto` only. | PASS |
| Raw transcript never crosses to n8n | `n8n_webhook.py:113-142` exact 4-key payload; `test_build_payload_no_incluye_transcript_crudo`; `grep transcript` in `n8n/workflow.json` = 0. | PASS |
| Encryption at rest | `transcript_original`/`caller_cifrado` are `EncryptedText`; model round-trip test proves ciphertext at column level. | PASS |
| Reserve-before-download order | `test_flujo_feliz_respeta_el_orden_y_persiste` asserts `events[:3] == ["guard","media","stt"]`. | PASS |
| 503 persists the error row before raising | `routes/telefonia.py:177-186` calls `service.commit_error_state()` (commits) then raises 503; `get_db_session` rollback after commit is a no-op. `test_fallo_descarga_persiste_el_ingreso_tras_503` re-reads the row in a new session and asserts `error_descarga`. | PASS |
| Atomic claim + no double processing | `repositories/telefonia_ingreso_repository.py:47-83` single `UPDATE ... WHERE call_sid AND estado IN (...)`, `rowcount == 1` gate; claim and pipeline share the request transaction. | PASS (design); PARTIAL (test strength) |
| `ingresado_en` not overwritten on retry | `_apply_callback_fields` touches only `recording_sid`/`caller_cifrado`/`duracion_segundos`; `test_reintento_preserva_ingresado_en` (clock advanced 120s) asserts equality. | PASS |
| Per-attempt reserve is intended | `_run_pipeline` reserves on every invocation; `test_reintento_reprocesa_desde_estado_terminal_de_error` asserts exactly one new reserve after clearing. | PASS |

---

## Response Contract

| Estado resultante | HTTP | Evidence |
|-------------------|------|----------|
| `transcrito` | 200 | `test_transcrito_devuelve_200` |
| `guarda_denegada` | 200 | `test_guarda_denegada_devuelve_200` |
| `pendiente` | 200 | by construction (`TRANSIENT_ERROR_STATES` excludes it); **not directly asserted** |
| `error_descarga` | 503 + `{"error": ...}` | `test_fallo_descarga_devuelve_503`, `test_fallo_descarga_persiste_el_ingreso_tras_503` |
| `error_stt` | 503 + `{"error": ...}` | `test_fallo_stt_devuelve_503` |

OpenAPI: `docs/openapi.json` documents the 503 response and the updated description; `test_openapi_in_sync_with_app` passes (regeneration matches the app).

---

## Issues Found

**CRITICAL (must fix before archive):**
None.

**WARNING (should fix):**
- **W-DOC — runbook still documents W5 as manual recovery.** `docs/runbook-verificacion-telefonia-c52.md:265` states: "si el ingreso quedó en `error_descarga`/`error_stt`/`guarda_denegada`, un callback repetido del mismo `CallSid` NO reintenta ... La recuperación es manual". This directly contradicts the new implementation, the updated delta spec, and the fixed route/service. Line 248 ("Recuperación: ... ver §7.5") inherits the same drift. This is the exact documentation drift flagged for this verification.
- **W-CONC — concurrent-claim scenario is only simulated.** The spec scenario "Solo un reintento concurrente reclama el ingreso" is covered by `test_claim_de_cero_filas_no_reprocesa`, which monkeypatches `claim_for_retry` to return `False`, and by the SQLite repository test (rowcount semantics). No test exercises real PostgreSQL `READ COMMITTED` row locking under genuine concurrency. The design is sound, but the atomicity guarantee itself is untested in CI. Marked PARTIAL.
- **W-PEND — `pendiente → 200` not directly asserted** at the HTTP layer. Low risk (structural branch), but the spec scenario explicitly names `pendiente`.

**SUGGESTION (nice to have):**
- Add an integration test (disposable PostgreSQL) firing two concurrent `process_recording` calls on the same error row and asserting exactly one claim wins.
- Persist the handoff outcome as a column/status instead of log-only observability.
- Rename `cost_guard_unit_cost_twilio_transcription_usd` (no longer represents transcription).
- Reconcile the report narrative about W1/W2 living "uncommitted": they are actually resolved in `63c45ae`; no working-tree diff exists for those two files.

---

## Task 8.4 Status

Still legitimately unchecked (43/44): requires a real Twilio call. The runbook `docs/runbook-verificacion-telefonia-c52.md` is the correct vehicle, but its §7.5 must be updated for W5 before it is used — as written it would lead an operator to manual recovery that no longer applies.

---

## Final Verdict

**PASS WITH WARNINGS** — W3, W4, W5 and W6 are implemented and behaviorally covered; the full offline suite (670 passed), ruff, OpenAPI sync, migration 008 and strict OpenSpec validation are all green; security-critical paths remain sound. Archive is blocked only by the W-DOC runbook drift (should fix) and the untested-concurrency caveat (known, non-blocking). No CRITICAL issues.
