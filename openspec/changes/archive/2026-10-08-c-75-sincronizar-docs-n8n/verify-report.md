## Verification Report

**Change**: c-75-sincronizar-docs-n8n
**Version**: N/A (delta spec `n8n-workflow`, N8N-DOC-004/005/006)
**Mode**: Standard verify (Strict TDD not applicable — see below)
**Verifier**: Independent (evidence from repo state, not the apply summary)
**Re-verify**: 2026-10-08 — after the CRITICAL-01 fix (guide:405 `BACKEND_URL` example). Result updated to PASS.

### TDD Mode Rationale

The system prompt has Strict TDD enabled, but the orchestrator launch prompt did NOT inject
"STRICT TDD MODE IS ACTIVE". This change is DOCUMENTATION-ONLY (design Decision 3: "Sin pruebas
nuevas"): no production code is written, so there is no RED/GREEN cycle to verify. I applied the
**Standard verify** protocol and used the existing doc-sync suites as the TDD **safety net**
(regression baseline). No `strict-tdd-verify.md` steps (5a/5e, layer validation, changed-file
coverage) apply because no code artifact changed.

---

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 14 |
| Tasks complete | 14 |
| Tasks incomplete | 0 |

All tasks `[x]`. Task 2.2's explicit acceptance sub-check ("cambiar el ejemplo
`https://localhost/api/v1` por un origen sin `/api/v1`") was initially NOT satisfied (CRITICAL-01
in the first verify pass); it is now RESOLVED after the fix (see CRITICAL-01 status and the
re-verify note below). Task mark and artifact now agree.

---

### Build & Tests Execution

**Build**: ➖ Not applicable (documentation change; no build target)

**Tests**: PASS — `202 passed, 1 xfailed, 1 warning` (exit 0)
```
cd App/Backend; pytest tests/test_n8n_workflow.py tests/test_c33_cost_guard_wiring.py \
  tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py \
  tests/test_docs_evaluation_sync.py -q
=> 202 passed, 1 xfailed, 1 warning in 13.31s   (re-run after the fix)
```

**OpenSpec validation**: PASS (exit 0)
```
openspec validate c-75-sincronizar-docs-n8n --strict
=> Change 'c-75-sincronizar-docs-n8n' is valid
```

**Coverage**: ➖ Not applicable (no changed source lines)

Targeted spec-scenario tests (all PASSED):
```
test_c40_guide_node_count_matches_workflow              PASSED
test_c40_guide_test_count_matches_suite                 PASSED
test_c40_guide_has_no_stale_review_branch_exception     PASSED
test_c53_guia_no_afirma_confirmacion_telefonica_por_twiml PASSED
test_c33_cost_guard_wiring.py (2 tests)                 PASSED
```

---

### Spec Compliance Matrix

| Requirement | Scenario | Evidence | Result |
|-------------|----------|----------|--------|
| N8N-DOC-004 | Conserva conteo de nodos y propiedades estructurales | `test_n8n_workflow.py::test_c40_guide_node_count_matches_workflow` + `test_c40_guide_test_count_matches_suite` PASSED; guide:42 `Estado: 29 nodos (26 operativos + 3 sticky notes)`, guide:579 `Verifica 163 propiedades estructurales`; `workflow.json` = 29 nodes | COMPLIANT |
| N8N-DOC-004 | Tabla del canal telefonía refleja el flujo vigente | guide:202-215 lists `Llamada telefonica -> Sellar ingreso telefonia -> Normalizar entrada del incidente`; all 11 names exist in `workflow.json`; no retired node in the table | PROVEN (structural) |
| N8N-DOC-004 | Documentos que describen el grafo no presentan nodos retirados | grep over guide/por_implementar/runbook: retired tokens appear only with explicit retirement markers ("retirado por C-72", "ya no existe") | PROVEN (structural) |
| N8N-DOC-004 | La excepción obsoleta de la rama de revisión no reaparece | `test_c40_guide_has_no_stale_review_branch_exception` PASSED; grep `queda sin marcar`/`no** pasa por Marcar correo como leido` = none | COMPLIANT |
| N8N-DOC-004 | La guía no reintroduce confirmación por TwiML | `test_c53_guia_no_afirma_confirmacion_telefonica_por_twiml` PASSED; grep `TwiML`/`<Say>` in guide = none | COMPLIANT |
| N8N-DOC-004 | Conserva tokens del webhook dedicado | `test_c33_cost_guard_wiring.py` PASSED; guide:143-146 `notificacion-clasificacion`, `N8N_WEBHOOK_URL`, `incidente-web` | COMPLIANT |
| N8N-DOC-005 | Transporte documentado IMAP/SMTP | ground truth: `workflow.json` trigger `n8n-nodes-base.emailReadImap` (`postProcessAction=read`), creds `imap`; `emailSend` creds `smtp`; docs guide:150-162, por_implementar:36-42, dry-run-harness:126-143 | PROVEN |
| N8N-DOC-005 | No reaparecen Outlook/Twilio/Redis de workflow | grep: `microsoftOutlook*`/`twilioTrigger`/`REDIS_URL` only in historical/negative statements; no `microsoftOutlook*` credential presented live | PROVEN |
| N8N-DOC-005 | Versión N8N = la del compose | guide:433 `n8nio/n8n:2.11.2`, por_implementar:109; `n8nio/n8n:latest` absent (only a historical note at guide:500 clarifying the current pin) | PROVEN |
| N8N-DOC-005 | El ejemplo de `BACKEND_URL` no incluye `/api/v1` | **RESOLVED (re-verify)**: guide:405 now `| BACKEND_URL | URL base del backend FastAPI, **solo el origen** (el workflow agrega `/api/v1`; no incluir el prefijo de versión) | http://backend:8000 |`. Literal `https://localhost/api/v1` absent from the guide; consistent with guide:253 `POST {BACKEND_URL}/api/v1/incidentes` and compose:130 `BACKEND_URL: http://backend:8000` | **PROVEN** |
| N8N-DOC-006 | Guía operativa no describe el agente retirado ni la guarda | `git diff docs/operational-guide.md`: removed "n8n (AI Agent)" + `Guard de costo`; now "n8n: ya NO reserva costo propio" | PROVEN |
| N8N-DOC-006 | Constantes de costo coinciden con el código | operational-guide:86-87 `0.0075` / `0.0038` == `settings.py:182,186`; `COST_GUARD_UNIT_COST_BACKEND_STT_USD` present | PROVEN |
| N8N-DOC-006 | Diagramas reflejan la topología vigente | despliegue.md: OUTLOOK node/edges removed, `Redis (memoria AI Agent)` -> `Redis (cola de trabajos)`, N8N 2.11.2, IMAP/SMTP + handoff; secuencia.md: participant `(Correo IMAP / Web / Telefonía)` | PROVEN |
| N8N-DOC-006 | El runbook no afirma variables inexistentes | runbook:52 corrected: the three vars "YA están declaradas en `App/Backend/.env.example`"; verified `.env.example:29,33,70` defines all three | PROVEN |
| N8N-DOC-006 | Invariantes de bootstrap preservadas | `test_docs_bootstrap_sync.py` + `test_docs_restructure_sync.py` + `test_docs_evaluation_sync.py` all PASSED; no `Gestion_Incidentes`/`generate_corpus.py`/`seed fijo` introduced | COMPLIANT |

**Compliance summary**: 15/15 scenarios proven/compliant (after CRITICAL-01 resolution).

---

### Adversarial Checks (Scope Containment)

`git status --porcelain` working tree:
```
 M AGENTS.md
 M docs/diagrams/despliegue.md
 M docs/diagrams/secuencia.md
 M docs/dry-run-harness.md
 M docs/medicion-latencia-e2e.md
 M docs/n8n-workflow-guide.md
 M docs/operational-guide.md
 M docs/por_implementar.md
 M docs/runbook-verificacion-telefonia-c52.md
 M docs/troubleshooting.md
?? openspec/changes/c-75-sincronizar-docs-n8n/
```

| Forbidden target | Changed? | Note |
|------------------|----------|------|
| `n8n/workflow.json` | NO | untouched |
| `docker-compose.yml` | NO | untouched |
| `App/Backend/**` (incl. `.env.example`, settings, code) | NO | untouched |
| `docs/openapi.json` | NO | untouched |
| `openspec/changes/c-56-notificaciones-por-rol/**` | NO | untouched |
| `docs/Comandos_para_iniciar_proyecto.txt` | NO | untouched |
| `docs/anexo_h_prompt_gemini.md` | NO | untouched |
| `docs/c-72-unificacion-clasificacion-telefonica.md` | NO | untouched |
| `docs/seguridad/**`, `docs/cumplimiento/**` | NO | untouched |

`AGENTS.md` classification: the only diff is a NEW `## External Sources (GitHub and Third-Party
Code)` anti-spoofing section (8 added lines). This is NOT part of c-75 and NOT scope drift; it is
a pre-existing working-tree modification. Correctly excluded from the c-75 diff (c-75 touched only
the 9 docs). One housekeeping note: it remains uncommitted in the working tree alongside the c-75
docs, so a commit that stages `docs/` must avoid accidentally sweeping it in.

**Result**: scope containment is exact. Only the 9 in-scope docs were modified; the new
`openspec/changes/c-75-sincronizar-docs-n8n/` directory is this change's artifacts.

---

### Correctness Spot-Checks (independent)

1. **Telephone node table vs JSON**: the guide's telefonia table names
   (`Llamada telefonica`, `Responder handoff telefonia`, `Sellar ingreso telefonia`,
   `Normalizar entrada del incidente`, `Entrada valida`, `Login operador`,
   `HTTP POST a MESA-AYUDAS`, `Requiere revision humana`, `Preparar destinatarios de revision`,
   `Notificar operador designado`, `Registro de auditoria`) all exist in `workflow.json`; the
   retired set (`AI Agent`, `Guard de costo`, `Guard permite?`, `Restaurar item telefonia`,
   `Tope de refinamiento alcanzado`, `Derivar a revision humana`, `Google Gemini Chat Model`,
   `memoryRedisChat`) is absent from the JSON. CONFIRMED.
2. **N8N image**: `docker-compose.yml:120,353` = `n8nio/n8n:2.11.2`; guide:433 and
   por_implementar:109 cite `2.11.2`. CONFIRMED.
3. **Cost values**: `settings.py:182` = `0.0075`, `settings.py:186` = `0.0038`;
   operational-guide:86-87 match. CONFIRMED.
4. **Diagram topology**: despliegue.md now routes `TWILIO -> BE` (callback) and
   `BE -> N8N` (handoff), `IMAP -> N8N`; no Outlook, no `Twilio -> N8N`, no Redis-agent-memory
   edge. secuencia.md participant updated. CONFIRMED.
5. **Trigger/credentials/env truth**: `workflow.json` trigger = `emailReadImap`
   (`postProcessAction=read`, cred `imap`), email nodes = `emailSend` (cred `smtp`), env vars
   referenced = exactly `BACKEND_URL`, `OPERATOR_EMAIL`, `SMTP_FROM_EMAIL`. Docs match, including
   the corrected `BACKEND_URL` example (`http://backend:8000`). CONFIRMED (full).

---

### Preserved-Correct Content Check

| Invariant | Present? | Evidence |
|-----------|----------|----------|
| c-55 IMAP/SMTP section | YES | guide:150-162 "Decisión 1 — Canal de correo sobre IMAP/SMTP" |
| c-56 `destinatarios_revision` contract | YES | guide:284-301 + table row 177 |
| `OPERATOR_EMAIL` fallback | YES | guide:177,294,407,612 |
| `active:false` note | YES | guide:54 |
| Audit event shape | YES | guide:638-648 |
| Bootstrap tokens (`scripts/up.sh`/`make up`, `UP_SKIP_COST_PREFLIGHT`, `docker compose up -d`, `openssl/generate-certs.sh`, `JWT_SECRET_KEY`, `App/Backend/`, evaluation runner) | YES | 3 doc-sync suites PASSED |
| c-33/c-56/c-57/c-69 webhook + notification tokens | YES | guide + `test_c33` PASSED |

No correct content was deleted: the removals (Redis Chat Memory §2.4, F3 patch instructions,
"Guard de costo permite" phrasing) all described retired components.

---

### Issues Found

**CRITICAL** (must fix before archive):
- None. **CRITICAL-01 — RESOLVED (re-verify, 2026-10-08).**
  - Was: `docs/n8n-workflow-guide.md:405` showed `| BACKEND_URL | URL base del backend FastAPI | https://localhost/api/v1 |`, violating N8N-DOC-005.
  - Now: `docs/n8n-workflow-guide.md:405` reads
    ``| `BACKEND_URL` | URL base del backend FastAPI, **solo el origen** (el workflow agrega `/api/v1`; no incluir el prefijo de versión) | `http://backend:8000` |``
  - Evidence: grep for the literal `https://localhost/api/v1` in the guide returns nothing;
    the example matches compose:130 (`BACKEND_URL: http://backend:8000`) and is consistent with
    guide:253 (`POST {BACKEND_URL}/api/v1/incidentes`). N8N-DOC-005 scenario now PROVEN.

**WARNING** (should fix):
- None.

**SUGGESTION** (nice to have):
- **SUG-01**: guide:759-762 (historical §7.3, C-05 record) still describes the retired node
  `Se verifica lo que trajo la IA` in present tense ("Solo el canal telefonía lo setea (en
  ...)"). It sits inside an explicitly historical section, so it is acceptable, but a
  `[retirado por C-72]` marker would remove any ambiguity.
- **SUG-02**: the guide's own env table is the only place documenting the `BACKEND_URL` example;
  adding a `(origen, sin /api/v1)` note would prevent the exact drift that caused CRITICAL-01.

---

### Verdict

**PASS** — CRITICAL count: 0

All 15 spec scenarios are proven/compliant after the CRITICAL-01 fix. Regression is clean
(202 passed, 1 xfailed; `openspec validate --strict` green), scope is exact, and no retired node
is presented as current. The change is ready to archive.

---

### Post-archive correction (2026-10-08)

The added requirement IDs were renumbered from `N8N-DOC-001/002/003` to `N8N-DOC-004/005/006`
after archiving, because the original `N8N-DOC-001` collided with a pre-existing requirement
(`N8N-DOC-001 — La guía del workflow refleja el estado real`) already present in
`openspec/specs/n8n-workflow/spec.md`. The main spec and this archive's delta spec, tasks,
proposal, design and this report were updated consistently. No behavior, scope or acceptance
criterion changed; this is an identifier-only correction to keep requirement labels unique.
