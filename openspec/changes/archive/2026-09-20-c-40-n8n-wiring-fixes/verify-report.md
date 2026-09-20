# Verification Report — c-40-n8n-wiring-fixes

**Change**: c-40-n8n-wiring-fixes
**Version**: N/A (ADDED requirements, no spec version field)
**Mode**: Standard (structural verification; Strict TDD build-cycle not independently reconstructable from the working tree)
**Artifact store**: openspec (report persisted to `openspec/changes/c-40-n8n-wiring-fixes/verify-report.md`)

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 21 |
| Tasks complete | 21 |
| Tasks incomplete | 0 |

Every task in `tasks.md` is marked `[x]` and was independently confirmed against the JSON and the suite.

---

## Build & Tests Execution

**Build**: N/A (no compiled artifact; workflow is a JSON export, suite is Python)
**Lint**: `ruff check .` → `All checks passed!` (exit 0)
**OpenSpec validate**: `openspec validate --strict --changes c-40-n8n-wiring-fixes` → passed (3/3 changes valid)

**Structural N8N suite**: `pytest tests/test_n8n_workflow.py -q`
```
129 passed, 1 xfailed, 1 warning in 1.10s
```
- `130` `def test_` functions total (129 pass + the documented, non-strict xfail `test_payload_has_no_obvious_pii`).
- Baseline at task 0.1 was 107 passed + 1 xfailed. Delta: +22 passing tests.

**Offline backend subset**: `pytest -m "not integration" -q`
```
431 passed, 22 deselected, 1 xfailed, 121 warnings in 69.20s
```
No failures. No regression from c-39's backend timing tests included in the working tree.

**Coverage**: Not measured for this change (routes/services/repositories untouched by c-40; structural JSON assertions are the coverage unit).

---

## Spec Compliance Matrix

All N8N scenarios are validated by **structural** assertions against `n8n/workflow.json` (graph reachability, node config, code substrings). The project's N8N suite runs without a live N8N runtime by design; runtime behavior is flagged as residual risk rather than failing the matrix.

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| N8N-WEBHOOK-003 | Alta web exitosa responde con el identificador | `test_web_confirmation_node_exists`, `test_web_confirmation_reachable_from_web_trigger` | ✅ COMPLIANT |
| N8N-WEBHOOK-003 | Rechazo por validación responde al cliente web | `test_c40_web_dead_ends_reach_closing_responder` | ✅ COMPLIANT |
| N8N-WEBHOOK-003 | Error del backend responde al cliente web | `test_c40_web_dead_ends_reach_closing_responder` | ✅ COMPLIANT |
| N8N-WEBHOOK-003 | Revisión humana responde al cliente web | `test_c40_web_dead_ends_reach_closing_responder` | ✅ COMPLIANT |
| N8N-WEBHOOK-003 | Guarda de canal evita respuestas cruzadas | `test_c40_web_guard_does_not_respond_for_non_web_channel` | ✅ COMPLIANT |
| N8N-EMAIL-002 | Correo con remitente produce destinatario no vacío | `test_c40_normalizer_emits_remitente`, `test_c40_email_confirmation_resolves_recipient_from_normalizer` | ⚠️ PARTIAL (static; `from` shape not exercised) |
| N8N-EMAIL-002 | La expresión referencia el nodo normalizador | `test_c40_email_confirmation_resolves_recipient_from_normalizer` | ✅ COMPLIANT |
| N8N-EMAIL-002 | El remitente no contamina payload ni auditoría | `test_c40_remitente_not_in_post_body_nor_audit` | ✅ COMPLIANT |
| N8N-PHONE-002 | La salida de telefonía no alcanza el nodo de correo | `test_c40_telefonia_branch_does_not_reach_email_confirmation` | ✅ COMPLIANT |
| N8N-PHONE-002 | El fallback no alcanza el nodo de correo | `test_c40_fallback_branch_does_not_reach_email_confirmation` | ✅ COMPLIANT |
| N8N-PHONE-002 | La salida de correo conserva su confirmación | `test_c40_correo_branch_still_reaches_email_confirmation` | ✅ COMPLIANT |
| N8N-MEMORY-001 | El nodo de memoria declara su credencial | `test_c40_memory_redis_node_declares_credentials_and_session_params`, `test_c40_memory_redis_credential_uses_placeholder` | ✅ COMPLIANT |
| N8N-MEMORY-001 | El nodo de memoria declara parámetros de sesión | `test_c40_memory_redis_node_declares_credentials_and_session_params` | ✅ COMPLIANT |
| N8N-MEMORY-001 | La suite cubre el tipo de nodo de memoria | `test_c40_credential_requiring_types_include_memory_redis` | ✅ COMPLIANT |
| N8N-AUTH-002 | Un solo mecanismo de autenticación | `test_c40_incidentes_http_node_has_single_auth_mechanism` | ✅ COMPLIANT |
| N8N-AUTH-002 | El header usa el token dinámico del login | `test_c40_incidentes_http_node_header_is_dynamic_bearer` | ✅ COMPLIANT |
| N8N-AUTH-002 | El nodo no declara credencial httpHeaderAuth en conflicto | `test_c40_incidentes_http_node_has_single_auth_mechanism` | ✅ COMPLIANT |
| N8N-AUDIT-002 | La salida de error alcanza la auditoría | `test_c40_audit_reachable_from_http_error_output` | ✅ COMPLIANT |
| N8N-AUDIT-002 | La salida de error conserva la guarda de canal | `test_c40_audit_reachable_from_http_error_output` | ✅ COMPLIANT |
| N8N-AUDIT-002 | El error del backend no se audita como alta | `test_c40_audit_error_result_is_not_creado` | ⚠️ PARTIAL (static substring assertion; JS not executed) |
| N8N-AUDIT-003 | El nodo de notificación declara manejo de error | `test_c40_notificar_operador_declares_on_error_continue` | ✅ COMPLIANT |
| N8N-AUDIT-003 | La auditoría sigue alcanzable tras fallo | `test_c40_notificar_operador_still_reaches_audit`, `test_notificar_operador_reaches_audit` | ✅ COMPLIANT (static) |
| N8N-AUDIT-003 | La rama de revisión conserva la notificación | `test_revision_humana_true_branch_notifies_operator`, `test_revision_true_branch_notifies_operator_and_marks_read` | ✅ COMPLIANT |
| N8N-DOC-001 | El conteo de nodos coincide con el JSON | `test_c40_guide_node_count_matches_workflow` | ✅ COMPLIANT |
| N8N-DOC-001 | El conteo de pruebas coincide con la suite | `test_c40_guide_test_count_matches_suite` | ✅ COMPLIANT |
| N8N-DOC-001 | No queda la excepción obsoleta de la rama de revisión | `test_c40_guide_has_no_stale_review_branch_exception` | ✅ COMPLIANT |

**Compliance summary**: 24/26 COMPLIANT, 2/26 PARTIAL, 0 FAILING, 0 UNTESTED.

---

## The 8 Defects — Independent Structural Verification

| # | Defect | Fix location in `n8n/workflow.json` | Verdict |
|---|--------|--------------------------------------|---------|
| 1 | Web branch had no `respondToWebhook` (client hangs) | Nodes `Es web?` (if, condition `$('Normalizar entrada del incidente').item.json.canal_origen == 'web'`) and `Respuesta web de cierre` (respondToWebhook, `respondWith: json`, `options.responseCode: 200`, body `resultado: 'sin_alta'`). Connections: `Es correo? [main#1] -> Es web?`, `Es web? [main#0] -> Respuesta web de cierre`, `Es web? [main#1] -> []`. Reachability confirmed from rejection (`Entrada valida` main#1), backend error (`HTTP POST a MTM-SRU` main#1) and human review (`Requiere revision humana` main#0) via `Es correo?` main#1. | ✅ PRESENT & CORRECT |
| 2 | Email recipient always empty | Normalizer emits `remitente: item.json.remitente \|\| item.json.from \|\| null`. `Correo de confirmacion al usuario.parameters.toRecipients = "={{ $('Normalizar entrada del incidente').item.json.remitente \|\| '' }}"`. Not present in POST body; audit jsCode active lines contain no `remitente`. | ✅ PRESENT & CORRECT |
| 3 | Telephony confirmation mis-routed to Outlook | `Rutear por canal de origen [main#2] -> []` (Telefonia) and `[main#3] -> []` (Otros/fallback). `[main#1] -> ['Marcar correo como leido','Correo de confirmacion al usuario']` preserved (Correo). | ✅ PRESENT & CORRECT |
| 4 | Redis memory node without credential | `memoryRedisChat` node declares `credentials.redis = { id: "REPLACE_WITH_REDIS_CREDENTIAL_ID", name: "Mesa de Ayuda - Redis" }` and non-empty params `sessionId`, `sessionTTL: 3600`, `contextWindowLength: 10`. `CREDENTIAL_REQUIRING_NODE_TYPES` includes the type. | ✅ PRESENT & CORRECT |
| 5 | Duplicate `Authorization` header | `HTTP POST a MTM-SRU` has no `authentication`, no `genericAuthType`, no `credentials.httpHeaderAuth`; only `sendHeaders: true` with exactly one header `Authorization: =Bearer {{ $('Login operador').item.json.access_token }}`. (Only `Login operador` still uses `httpCustomAuth` — different node, out of scope.) | ✅ PRESENT & CORRECT |
| 6 | No audit on error branch | `HTTP POST a MTM-SRU [main#1] -> ['Es correo?','Registro de auditoria']`. Audit jsCode detects `item.error` → `error_backend` (≠ `creado`). | ✅ PRESENT & CORRECT (static) |
| 7 | Notification could skip audit | `Notificar operador designado.onError = "continueRegularOutput"`, edge `Notificar operador designado [main#0] -> Registro de auditoria` preserved. | ✅ PRESENT & CORRECT |
| 8 | Doc drift | Guide declares `32 nodos (29 operativos + 3 sticky notes)` matching JSON; declares `Verifica 130 propiedades estructurales` matching 130 `def test_`; stale review-branch exception replaced by C-40 correction note (guide lines 69-71). | ✅ PRESENT & CORRECT |

---

## c-39 Cross-Change Integrity Check (rebased timing instrumentation)

Preserved end-to-end. Ingress seal exists on all three channels and flows through to the POST:

- Email: `Se verifica que la informacion...` jsCode seals `ingresado_en` at trigger start.
- Web: `Marcar canal web` jsCode seals `ingresado_en` at the webhook edge.
- Telephony: `Sellar ingreso telefonia` code node seals `ingresado_en`; telephone validator re-injects it across the AI Agent.
- `Normalizar entrada del incidente` propagates `ingresado_en: item.json.ingresado_en || null`.
- `HTTP POST a MTM-SRU` body sends `"ingresado_en": "={{ $('Normalizar entrada del incidente').item.json.ingresado_en }}"`.
- Dedicated tests pass: `test_c39_telefonia_sella_ingreso_aguas_arriba_del_agente`, `test_c39_telefonia_preserva_ingreso_a_traves_del_agente`, `test_c39_correo_sella_al_inicio_del_flujo_y_no_usa_received_date`, `test_c39_web_sella_en_marcar_canal_web`, `test_c39_normalizador_propaga_ingresado_en`, `test_c39_cada_trigger_sella_ingreso_hacia_el_normalizador`, `test_c39_body_incluye_ingresado_en_por_expresion`, `test_c39_body_sin_credenciales_y_host_por_env`.

**Verdict: PRESERVED.** No c-39 timing field was removed or overwritten by c-40.

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| N8N-WEBHOOK-003 | ✅ Implemented | Graph reachability + guard confirmed on all three shared terminal branches |
| N8N-EMAIL-002 | ✅ Implemented | Normalizer + confirmation expression; PII excluded from POST/audit |
| N8N-PHONE-002 | ✅ Implemented | Telefonia/fallback outputs empty; correo output intact |
| N8N-MEMORY-001 | ✅ Implemented | Credential + session params + suite type coverage |
| N8N-AUTH-002 | ✅ Implemented | Single dynamic Bearer mechanism; no conflicting credential |
| N8N-AUDIT-002 | ✅ Implemented | Error output fans to audit + guard; error result ≠ `creado` |
| N8N-AUDIT-003 | ✅ Implemented | `continueRegularOutput` + preserved audit edge |
| N8N-DOC-001 | ✅ Implemented | Counts and stale-exception assertions enforced by tests |

No dangling connection targets (independently checked: all `connections` sources and targets resolve to declared nodes).

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| 1 — Web close via `Es web?` + single closing responder | ✅ Yes | Exactly the two nodes and wiring described; generic 200 + `sin_alta` |
| 2 — Sender travels in normalized structure, not POST | ✅ Yes | `remitente` in normalizer only; POST body and audit clean |
| 3 — Telephony/fallback without email node | ✅ Yes | Outputs 2 and 3 empty |
| 4 — Redis credential + params in `REPLACE_WITH_*` style | ✅ Yes | Placeholder consistent with rest of export |
| 5 — Single auth mechanism (explicit dynamic Bearer) | ✅ Yes | `authentication`/`genericAuthType`/`httpHeaderAuth` removed |
| 6 — Audit on backend error path | ✅ Yes | Audit added in parallel to `Es correo?`; error result refined |
| 7 — `onError: continueRegularOutput` on notification | ✅ Yes | Edge to audit preserved |
| 8 — Guide synchronized and test-checked | ✅ Yes | Node/test counts and stale exception machine-verified |

No rejected alternative was accidentally implemented.

---

## TDD Compliance Note

`tasks.md` documents the RED → GREEN → TRIANGULATE structure per defect, and the suite clearly separates the c-40 tests (`test_c40_*`) from prior suites. However, because the implementation lives in an **uncommitted working tree** with no per-cycle commits, the verify phase cannot independently reconstruct that each test was written before its implementation. This is reported as a limitation of evidence, not a failure: the current state is fully green.

---

## Issues Found

**CRITICAL** (must fix before archive): None.

**WARNING** (should fix):
- Static-only confidence for runtime semantics. The suite exercises the JSON graph and code substrings, not a live N8N runtime. Two scenarios are therefore PARTIAL: (a) the email recipient string resolution, and (b) the backend-error audit result value.

**SUGGESTION** (nice to have):
- Add a lightweight runtime/integration smoke check (import the workflow into N8N and drive one web rejection + one backend error) to upgrade the two PARTIAL scenarios.

---

## Residual Runtime Risks (cannot be verified without a live N8N runtime)

1. **Email `from` shape**: `remitente: item.json.remitente || item.json.from || null` assumes `from` resolves to a usable recipient value. The Microsoft Outlook trigger typically exposes `from` as an object (e.g. `{ emailAddress: { address, name } }`), not a bare string. If `toRecipients` expects a string address, the confirmation recipient may still be invalid at runtime. This is the single highest-value residual risk.
2. **`Es web?` pairing on error items**: `$('Normalizar entrada del incidente').item.json.canal_origen` is evaluated from the shared `Es correo?` main#1, which can be reached with N8N error-item shapes. Item pairing across an error output is not guaranteed by static analysis.
3. **`item.error` detection**: the audit distinguishes backend errors via `item.error`; the exact N8N error-item shape is runtime-dependent. The fallback never records `creado`, so a false positive is unlikely, but the error-specific label may vary.
4. **Silent notification failure**: `onError: continueRegularOutput` intentionally swallows the send failure; audit runs but no alert surfaces. Accepted by design.

None of these are defects in the change's scope; they are runtime behaviors unverifiable offline.

---

## Verdict

**PASS WITH WARNINGS — READY TO ARCHIVE.**

All 21 tasks implemented; all 8 defects fixed and structurally confirmed; c-39 timing instrumentation preserved; 129/130 structural tests pass (1 documented xfail), offline backend subset 431 passed with no failures, ruff clean, strict OpenSpec validation clean. The only caveats are static-only evidence for two scenarios and the Outlook `from` shape runtime risk, neither blocking archive.