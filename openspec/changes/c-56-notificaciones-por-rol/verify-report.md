# Verification Report

**Change**: c-56-notificaciones-por-rol
**Version**: N/A (delta specs, unarchived)
**Mode**: Strict TDD (orchestrator-injected) — `openspec/config.yaml` has no `strict_tdd` key; mode applied per injected instruction.
**Verifier**: independent sdd-verify executor (deepseek/deepseek-v4.1-flash)
**Date**: 2026-10-07
**Governance**: HIGH

Independent verification. Nothing below is taken from the apply summary: every claim is proven from source code, the workflow JSON, git diffs, or a command executed in this session.

---

## 1. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 27 |
| Tasks complete `[x]` | 26 |
| Tasks incomplete `[ ]` | 1 |

Incomplete task:

- **7.5 — Smoke manual (PENDIENTE, manual, no automatizable):** requires the c-55 Gmail mailbox and an operator loaded in the directory. It is the only end-to-end runtime proof that an incident requiring review notifies the resolved operator (or the fallback) and produces an audit entry.

Task-count note: tasks 1.1–1.3, 2.1–2.4, 3.1–3.3, 4.1–4.5, 5.1–5.3, 6.1–6.3, 7.1–7.4 and 7.6 are checked and were re-verified below. Task 7.5 is the sole open item.

---

## 2. Build & Tests Execution (exact results)

**Build / type check**: `ruff check .` is the project's quality gate (no separate Python build step; `AGENTS.md` "Never build after changes").

```
$ cd App/Backend; ruff check .
All checks passed!
RUFF_EXIT=0
```

**Offline unit subset** (SQLite, no external services):

```
$ cd App/Backend; pytest -m "not integration" -q
1059 passed, 42 deselected, 1 xfailed, 251 warnings in 122.07s (0:02:02)
```

**PostgreSQL integration subset** (disposable DB `mesa_de_ayuda_test`, PostgreSQL 15.5 healthy on :5433):

```
$ cd App/Backend; pytest -m integration -q
42 passed, 1060 deselected, 6 warnings in 26.06s
```

This matches the tasks.md claims (2.4 / 7.2: "42 passed"). It also resolves a stale statement in the apply-progress memory (`#1208`) that said the integration file was UNRUN — it is written AND was executed green in this session.

**Targeted c-56 suites**:

```
$ pytest tests/test_notification_recipients.py -q          → 16 passed
$ pytest tests/integration/test_notification_recipients_postgres.py -v → 3 passed
$ pytest tests/test_n8n_workflow.py -q                     → 162 passed, 1 xfailed
$ pytest tests/test_api_incidentes.py -q                   → 34 passed
$ pytest tests/test_openapi_sync.py -v                     → 5 passed
```

**OpenSpec strict validation**:

```
$ openspec validate c-56-notificaciones-por-rol --strict
Change 'c-56-notificaciones-por-rol' is valid
OPENSPEC_EXIT=0
```

**Coverage**: not run for this change (no coverage threshold configured in `openspec/config.yaml`; informational only, not a blocker).

---

## 3. Spec Compliance Matrix

A scenario is PROVEN only when a test that exercises it passed on execution. `PARTIAL` means the behavior is proven structurally or statically but the workflow runtime itself is not executed in this environment (N8N is a declarative JSON artifact; the project's N8N layer is structural by design — design D10). There are **no MISSING** scenarios.

### 3.1 `notification-routing` (NEW capability) — 21 scenarios

| Requirement | Scenario | Test / Evidence | Result |
|-------------|----------|-----------------|--------|
| NR-001 directorio = fuente de verdad | Los destinatarios provienen del directorio | `test_notification_recipients.py::test_4_1_alta_con_revision_incluye_operadores_del_sector` (POST 201 returns `op1/op2@example.test` from `directorio_empleado`) | ✅ PROVEN |
| NR-001 | Sin directorio no hay lista embebida | Static: `grep` for emails in `App/Backend/app/**` → none; no fixed recipient list exists (`NotificationRecipientService` composes `EmpleadoRepository`). No dedicated test. | ⚠️ PARTIAL (static) |
| NR-002 resolución por rol y sector | Operador del sector resuelto | `test_2_1_listar_operadores_por_sector_solo_activos_operador`, `test_4_1_alta_con_revision_incluye_operadores_del_sector` | ✅ PROVEN |
| NR-002 | Varios operadores del sector | `test_2_3_varios_operadores_sin_duplicados`, `test_3_3_varios_destinatarios`, `test_4_1` (2 op.) | ✅ PROVEN |
| NR-002 | Empleados de otros roles excluidos | `test_2_3_excluye_inactivos_y_otros_roles` (UF-1, ADM-1) + fixture `operadores_sector` (UF-SIS excluded in `test_4_1`) | ✅ PROVEN |
| NR-002 | Operador inactivo excluido | `test_2_3_excluye_inactivos_y_otros_roles` (OP-INACT) + fixture `OP-INACT` excluded in `test_4_1` | ✅ PROVEN |
| NR-002 | Sin sector no es fatal | `test_2_3_sector_nulo_o_inexistente_devuelve_vacio`, `test_3_3_sector_nulo_o_sin_operadores_devuelve_vacio_sin_excepcion`, `test_4_3_alta_revision_sector_nulo_lista_vacia` (HTTP 201, `sector=null`, `[]`) | ✅ PROVEN |
| NR-003 precedencia y respaldo | El directorio toma precedencia | `test_4_1` (non-empty list from directory) + preparer JS `lista.length > 0 ? lista : [$env.OPERATOR_EMAIL]` | ✅ PROVEN |
| NR-003 | Fallback al destinatario único | `test_4_3_alta_revision_sin_operadores_lista_vacia` (backend emits `[]`) + `test_c56_preparar_lee_destinatarios_y_respaldo` (structural). N8N fallback not executed. | ⚠️ PARTIAL (structural) |
| NR-003 | Compatibilidad con un backend previo | Preparer JS guards with `Array.isArray(...)` → absent field ⇒ `[]` ⇒ fallback; `test_c56_preparar_lee_destinatarios_y_respaldo`. Not executed. | ⚠️ PARTIAL (structural) |
| NR-004 contrato backend→N8N | La lista llega con la marca de revisión | `test_4_1` asserts both `requiere_revision_humana is True` and the list in the 201 body | ✅ PROVEN |
| NR-004 | Lista vacía representable | `test_4_4_alta_sin_revision_no_incluye_destinatarios`, `test_4_3_alta_revision_sin_operadores_lista_vacia` (field present, `[]`, HTTP 201) | ✅ PROVEN |
| NR-004 | Sin round-trip adicional | Static: `git diff` of `n8n/workflow.json` adds no `httpRequest`; no new contact-resolving route (`routes/incidentes.py` diff limits to `response_model`). No dedicated test. | ⚠️ PARTIAL (static) |
| NR-005 un envío por destinatario | Un correo por operador | `test_c56_preparar_emite_un_item_por_destinatario` (`.map` one item each) + `test_c56_gate_rutea_por_preparar` (preparer → send). Structural. | ⚠️ PARTIAL (structural) |
| NR-005 | La lista no se expone entre destinatarios | `test_c56_notificar_usa_destinatario_por_item`: `toEmail === "={{ $json.destinatario }}"`, no `destinatarios_revision` and no `$env.OPERATOR_EMAIL` in the send node. Structural. | ⚠️ PARTIAL (structural) |
| NR-006 privacidad | Sin emails en la trazabilidad | `test_3_3_trazabilidad_sin_emails_en_claro` (`capture_logs`: event + `sector_id` + `cantidad`, asserts email string absent) | ✅ PROVEN |
| NR-006 | Reutilización del directorio | Static: `NotificationRecipientService.__init__` builds `EmpleadoRepository`; no second source, no HTTP. No dedicated test. | ⚠️ PARTIAL (static) |
| NR-006 | El payload acotado a la notificación | `test_4_1_get_no_expone_destinatarios_revision` (GET detail and GET list omit the field) | ✅ PROVEN |
| NR-007 no-bloqueo | El alta no depende de la notificación | `test_4_3_*` returns HTTP 201 with empty list; send remains `asyncio.create_task` fire-and-forget in `_apply_classification` | ✅ PROVEN |
| NR-007 | Directorio no dispone de contacto | `test_4_3_alta_revision_sin_operadores_lista_vacia`, `test_4_3_alta_revision_sector_nulo_lista_vacia` | ✅ PROVEN |
| NR-007 | Fallo de envío auditado | `test_c56_auditoria_en_paralelo_al_envio` (audit is a direct successor of the gate, and NOT reachable through preparer/send) + `onError: continueRegularOutput` on the send node. Structural. | ⚠️ PARTIAL (structural) |

### 3.2 `n8n-workflow` (MODIFIED) — 11 scenarios

| Requirement | Scenario | Test / Evidence | Result |
|-------------|----------|-----------------|--------|
| Notificación al operador designado | Se notifica al operador cuando el backend pide revisión | `test_revision_humana_true_branch_notifies_operator`, `test_c56_gate_rutea_por_preparar`, `test_c56_auditoria_en_paralelo_al_envio`. Structural. | ⚠️ PARTIAL (structural) |
| Notificación al operador designado | Fallback cuando no hay destinatarios resueltos | `test_c56_preparar_lee_destinatarios_y_respaldo` (JS reads `destinatarios_revision` + `$env.OPERATOR_EMAIL`). Structural. | ⚠️ PARTIAL (structural) |
| Notificación al operador designado | No se notifica cuando no hace falta revisión | `test_revision_humana_false_branch_routes_and_audits` (false branch → canal switch + audit). Structural. | ⚠️ PARTIAL (structural) |
| Notificación al operador designado | Un correo por destinatario sin exponer la lista | `test_c56_notificar_usa_destinatario_por_item`, `test_c56_preparar_emite_un_item_por_destinatario`. Structural. | ⚠️ PARTIAL (structural) |
| Notificación al operador designado | La rama de revisión marca el correo como leído | `test_revision_branch_requires_no_mark_read_node` (IMAP trigger, c-55 invariant). Structural. | ✅ PROVEN |
| Notificación al operador designado | La notificación no antecede a la auditoría | `test_notificar_operador_reaches_audit`, `test_c56_auditoria_en_paralelo_al_envio`. Structural. | ✅ PROVEN |
| Notificación al operador designado | La notificación no depende de Entra OAuth2 | `test_c55_no_outlook_artifacts_and_node_count` (node is `emailSend`, credential `smtp`). Structural. | ✅ PROVEN |
| URLs del backend configurables por entorno | Los nodos HTTP usan la variable de entorno | `test_..._uses_backend_url_env` / `$env.BACKEND_URL` structural tests pass | ✅ PROVEN |
| URLs del backend configurables por entorno | No hay host hardcodeado | host-literal structural test passes | ✅ PROVEN |
| URLs del backend configurables por entorno | Las variables se exponen desde el compose | Static: `docker-compose.yml` n8n service declares `BACKEND_URL` and `OPERATOR_EMAIL` (parsed YAML). No dedicated assertion found. | ⚠️ PARTIAL (static) |
| URLs del backend configurables por entorno | OPERATOR_EMAIL es el respaldo, no la fuente principal | `test_c56_notificar_usa_destinatario_por_item`, `test_c56_respaldo_solo_en_el_nodo_de_preparacion` (fallback literal appears in exactly one node) | ✅ PROVEN |

**Compliance summary**: **19/32 PROVEN, 13/32 PARTIAL, 0/32 MISSING.** All PARTIAL entries are either (a) static-only evidence, or (b) N8N declarative-topology assertions — neither is a functional gap. The residual N8N runtime behavior is exactly what task 7.5's manual smoke covers.

---

## 4. Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| NR-001 source of truth | ✅ Implemented | `NotificationRecipientService` composes `EmpleadoRepository.listar_operadores_por_sector`; no embedded list anywhere in `app/`. |
| NR-002 role/sector filter | ✅ Implemented | Repo query: `sector_id == ?`, `rol == RolEmpleado.operador.value`, `activo.is_(True)`, `order_by(Empleado.id)`; `None` ⇒ `[]`. |
| NR-003 precedence/fallback | ✅ Implemented | Backend emits `[]` when no operator; N8N preparer chooses list vs `$env.OPERATOR_EMAIL`. |
| NR-004 create-only contract | ✅ Implemented | `IncidenteCreateResponse(IncidenteRead)` adds `destinatarios_revision`; POST `response_model` updated; `IncidenteRead`/`IncidenteListItem` untouched. |
| NR-005 one email per recipient | ✅ Implemented | Preparer `.map` yields one item; send uses `$json.destinatario`; no shared To/Cc/Bcc. |
| NR-006 privacy | ✅ Implemented | Service logs only `sector_id`/`cantidad`; invalid-email warning logs no address; audit node contains no email/`destinatarios` reference; docs use only `example.com`/`example.test`. |
| NR-007 non-blocking | ✅ Implemented | Resolution only when `requiere_revision_humana`; repository failure swallowed (`except Exception` → `[]`); send stays fire-and-forget. |
| No schema migration | ✅ Implemented | No new/untracked Alembic file; `destinatarios_revision` is a transient attribute, never persisted or serialized in GET. |

### Adversarial checks (all independently confirmed)

1. **`destinatarios_revision` only in the CREATE response.** `grep` in `App/Backend/app/` shows the field is declared only on `IncidenteCreateResponse`; `IncidenteRead` and `IncidenteListItem` do not define it. In `docs/openapi.json` the key appears only at `/components/schemas/IncidenteCreateResponse/properties`, referenced solely by the `POST /api/v1/incidentes/` 201 response. Behavioral proof: `test_4_1_get_no_expone_destinatarios_revision` passed (GET detail and GET list payloads omit the key).
2. **Populated ONLY when `requiere_revision_humana=true`.** `incidente_service._apply_classification`: `destinatarios_revision = []` unless `result.requiere_revision_humana`, else resolves. Proven empty with review-off (`test_4_4_alta_sin_revision...`), null sector (`test_4_3_alta_revision_sector_nulo_lista_vacia`), and no operator (`test_4_3_alta_revision_sin_operadores_lista_vacia`) — all HTTP 201. **A resolution failure does not raise:** `test_3_3_fallo_del_repositorio_no_propaga` (repo `RuntimeError` → `[]`).
3. **Only ACTIVE `rol=operador` of the sector.** `test_2_3_excluye_inactivos_y_otros_roles` excludes inactive, `usuario_final`, `administrador_directorio`; `test_4_1` fixture proves the same through the API; `test_2_3_sector_nulo_o_inexistente_devuelve_vacio` proves `None`/inexistent → `[]` with no exception.
4. **No real emails leaked.** Service logs carry only `sector_id`/`cantidad` (verified); `test_3_3_trazabilidad_sin_emails_en_claro` asserts the address is absent from captured logs. The audit node's `jsCode` references neither `destinatarios` nor `email`. A regex scan of `docs/n8n-workflow-guide.md`, `n8n/workflow.json`, `.env.example`, `docker-compose.yml`, `docs/openapi.json` finds only `example.com`/`example.test` placeholders.
5. **N8N wiring.** Independent JSON parse: the only node whose serialized content contains `$env.OPERATOR_EMAIL` is `Preparar destinatarios de revision`; `Notificar operador designado` uses `toEmail = "={{ $json.destinatario }}"` and has `onError: continueRegularOutput`. The gate's true branch (`main[0]`) fans out to `Preparar destinatarios de revision`, `Registro de auditoria`, `Es correo?` and `Confirmar correo en revision?` as siblings, so audit is reachable independently of a failed send. Preparer → send is the only edge into the send node.
6. **No regression of c-38/c-40/c-53/c-55.** `test_c56_no_regresion_c38_c40_c53_c55` passed; targeted selection of c40/c53/c55/c56/revision tests: 66 passed, 108 deselected. The c-72 topology test was updated to the new preparer hop and passes. `docker-compose.yml` still sets `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`, so `$env` access remains valid.
7. **Hard constraints unchanged.** `git diff` is empty for `App/Backend/app/constants.py` (five canonical strings), `App/Backend/app/classifiers/keywords.py` (`KEYWORD_MAP`), `docs/prompt_gemini.txt`, and `evaluation/corpus.py` (`_a_float`). No Alembic migration added.

---

## 5. Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 directory as source of truth | ✅ Yes | Repo query on `directorio_empleado`; roles from `RolEmpleado`. |
| D2 contract = create response (option A) | ✅ Yes | `IncidenteCreateResponse`; no webhook move; no query endpoint. |
| D3 directory precedence + env fallback | ✅ Yes | Backend `[]` → N8N `$env.OPERATOR_EMAIL`. |
| D4 one email per recipient, audit parallel | ✅ Yes | Preparer `.map`, per-item `toEmail`, audit sibling of the gate. |
| D5 reuse c-54 seam, no duplicate resolver | ✅ Yes | Service composes `EmpleadoRepository`; no second identity resolver. |
| D6 resolve only with review, fire-and-forget | ✅ Yes | `if result.requiere_revision_humana`; `_dispatch_notification` unchanged. |
| D7 route by MAIN sector only | ✅ Yes | `sector_id` from `result.sector_predicho`; additional sectors untouched. |
| D8 PII boundary | ✅ Yes | Field only in authenticated POST; not in logs/audit/GET; human review task 7.6 checked. |
| D9 no schema migration | ✅ Yes | None added. |
| D10 test strategy (unit/integration/structural) | ✅ Yes | All layers present and green. |
| D11 archive order | n/a | Not an archive-phase concern here. |
| D12 docs and counts | ⚠️ Partial | The **guide** was corrected to 29 nodes / 163 structural props and the doc-sync tests pass, but **`design.md` still states "37 → 38"** (D12, line 92) — stale versus the real 28 → 29. Documentation drift only. |

File-change table in the proposal/impact list is accurate except that `App/Backend/tests/test_c72_n8n_workflow.py` was also modified (topology update: gate true → preparer → send). This is a legitimate, low-risk collateral change not listed in the impact table.

---

## 6. TDD Compliance (Strict TDD)

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ | Apply-progress (Engram `#1208`) describes RED/GREEN/TRIANGULATE and records baseline (`1035 passed`) and final (`1059 passed`) counts, but contains **no formal "TDD Cycle Evidence" table**. Repo precedent (c-70/c-72/c-73 verify reports) classifies this as WARNING, not CRITICAL, because the OPSX repo-local workflow emits no apply-progress artifact and `tasks.md` encodes per-task RED/GREEN/TRIANGULATE. |
| All tasks have tests | ✅ | 16 unit + 3 integration + 8 new structural tests exist for the changed behavior. |
| RED confirmed (tests exist) | ✅ | `tests/test_notification_recipients.py` and the c-56 group in `test_n8n_workflow.py` exist and reference production symbols. |
| GREEN confirmed (tests pass) | ✅ | Executed: 16 + 3 + 162 passed (offline full suite 1059 passed). |
| Triangulation adequate | ✅ | Multiple distinct expected values per behavior: 0/1/N recipients, null/inexistent sector, inactive/other roles, invalid email, repo failure, sector with operators vs empty, another sector (D7). |
| Safety Net for modified files | ✅ | Apply-progress records the offline baseline (1035 passed, 1 xfailed) before modification; no pre-existing failure reported. |

**TDD Compliance**: functionally satisfied; the only gap is the missing formal table (process/traceability, tracked as W2).

### Assertion Quality (Step 5f)

| File | Location | Pattern | Issue | Severity |
|------|----------|---------|-------|----------|
| `tests/test_notification_recipients.py` | `test_4_1_get_no_expone_destinatarios_revision` | `for item in listado.json(): assert ...` | The loop is vacuous if `listado.json()` were empty; the sibling `detalle` assertion is independent and valid. | SUGGESTION |

No tautologies, no ghost-loop-only tests, no type-only standalone assertions, no implementation-detail coupling. Empty-list assertions all have companion non-empty tests in the same file.

**Assertion quality**: 0 CRITICAL, 0 WARNING, 1 SUGGESTION.

---

## 7. Issues Found

**CRITICAL** (must fix before archive): **None.**

**WARNING** (should fix):
- **W1 — Task 7.5 manual smoke PENDING.** The only end-to-end proof that N8N actually sends one email per resolved recipient (or the fallback) and writes the audit entry has not been executed. All automated N8N evidence is structural (declarative topology). This does NOT block archiving the code (the change is reversible, adds no migration, and — by design — does not activate real operator data until the directory is populated), but it **MUST** be completed before enabling real PII/operators per governance HIGH / design D9.
- **W2 — No formal "TDD Cycle Evidence" table** in the apply-progress artifact (`#1208`); only inline RED/GREEN/TRIANGULATE in `tasks.md`. Functional TDD substance was independently verified (tests exist, are triangulated, pass). Process/traceability gap only, consistent with repo precedent.
- **W3 — `design.md` D12 node count is stale**: states "37 → 38"; the real workflow went 28 → 29. The guide and doc-sync tests use the correct value; only the design artifact was not refreshed.

**SUGGESTION** (nice to have):
- **S1 —** Add a non-empty assertion for the list endpoint in `test_4_1_get_no_expone_destinatarios_revision` so the loop cannot be vacuous.
- **S2 —** Update `design.md` D12/Migration Plan to 28 → 29 (or remove the absolute counts from the design, since the guide is the doc-sync source of truth).
- **S3 —** `apply-progress #1208` says the integration file was UNRUN; it is now executed green (42 passed). Refresh the artifact to avoid stale audit trail.

---

## 8. Verdict

**PASS WITH WARNINGS**

- **CRITICAL count: 0.**
- Every executable command is green: offline 1059 passed, integration 42 passed, ruff clean, `openspec validate --strict` valid, OpenAPI in sync.
- 19/32 spec scenarios PROVEN, 13/32 PARTIAL (static/structural only, inherent to the declarative N8N layer), 0 MISSING.
- All adversarial checks pass: contract surface (CREATE only), conditional population, role/active/sector filtering, no PII leakage, correct N8N fallback/per-item/audit topology, no c-38/c-40/c-53/c-55 regression, and hard constraints untouched.
- Residual risk is confined to the **manual smoke (task 7.5)**, which is pending by nature and does not block code archive but must be completed before activating real operators in the directory.
