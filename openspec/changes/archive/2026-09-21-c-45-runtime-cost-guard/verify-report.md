# Verification Report — c-45-runtime-cost-guard (independent re-verification #4, post W1/W2 fix)

**Change**: c-45-runtime-cost-guard
**Version**: N/A (delta spec `runtime-cost-guard`)
**Mode**: Standard (post-apply independent re-verification; no `strict_tdd` key in `openspec/config.yaml`)
**Date**: 2026-09-21
**Verifier**: SDD verify phase (READ-ONLY; only this report was overwritten)
**Baseline**: previous report in this same file (verdict PASS WITH WARNINGS, residual W1/W2)
**Scope of this pass**: close-out of warnings W1 (Twilio signature behind Nginx) and W2 (OpenAPI
inaccuracy), plus a no-regression sweep over the whole change.

---

## Verdict

**READY TO ARCHIVE** (equivalent to PASS WITH WARNINGS — no blockers remain)

W1 and W2 are both **resolved with independent evidence**. The proxy trust mechanism is real and
verified against the installed Uvicorn 0.30.6 (`FORWARDED_ALLOW_IPS` is read by `uvicorn.Config`;
`proxy_headers=True` by default; `ProxyHeadersMiddleware` rewrites the ASGI scheme from
`X-Forwarded-Proto`). `docker compose config` confirms the backend publishes **no** host port and
only Nginx publishes 80/443. The OpenAPI artifact now documents `text/xml` for the Twilio 200 and
`401` for both guard endpoints. Every claimed command reproduces exactly (offline **545 passed**,
guard **72 passed**, OpenAPI sync **5 passed**, `ruff` clean, `openspec validate --strict` green).
All previous warnings 1-5 remain resolved or documented; B1/B2 remain resolved; no spec scenario
regressed. The only remaining items are non-blocking warnings (R6/R8 partial coverage, integration
suite not re-run) and documented operational caveats.

---

## W1 / W2 Resolution Status (explicit)

### W1 — Twilio signature behind Nginx reconstructs the public `https://` URL — **RESOLVED**

**Claim under test:** the backend now trusts forwarded headers so `str(request.url)` reconstructs
the public `https://` URL behind the shipped Nginx; mechanism is
`FORWARDED_ALLOW_IPS: ${FORWARDED_ALLOW_IPS:-*}` in the backend service of `docker-compose.yml`,
honored by Uvicorn's `ProxyHeadersMiddleware`; the trust assumption is that the backend publishes
no port and Nginx overwrites `X-Forwarded-Proto`; Uvicorn honors `X-Forwarded-Proto` but not
`X-Forwarded-Host` (host comes from Nginx `Host: $host`).

**Independent evidence — config wiring:**
- `docker-compose.yml:100` → `FORWARDED_ALLOW_IPS: ${FORWARDED_ALLOW_IPS:-*}` inside `backend.environment`.
- `docker-compose.yml` backend service has **no `ports:` block** (the file's own header comment says
  "The internal port 8000 is NOT published to the host", line 101-102).
- `docker compose config` (resolved model, not the raw YAML):
  ```
  backend ports= None
  frontend ports= None
  nginx ports= [{'mode': 'ingress', 'target': 80, 'published': '80', 'protocol': 'tcp'},
                {'mode': 'ingress', 'target': 443, 'published': '443', 'protocol': 'tcp'}]
  n8n ports= [{'mode': 'ingress', 'target': 5678, 'published': '5678', 'protocol': 'tcp'}]
  backend FORWARDED_ALLOW_IPS= '*'
  ```
  Only Nginx exposes 80/443 to the host; the backend is reachable solely over the compose network.
- `nginx/nginx.conf:52-57` (`location /api/`): `proxy_set_header Host $host;` and
  `proxy_set_header X-Forwarded-Proto $scheme;` — Nginx **overwrites** the forwarded scheme, so an
  external client cannot inject a forged value.

**Independent evidence — Uvicorn actually honors it (installed version, not docs):**
- `uvicorn==0.30.6`. `uvicorn/config.py:204` `proxy_headers: bool = True` (default);
  `config.py:249` `self.proxy_headers = proxy_headers`; `config.py:469-470`:
  `if self.proxy_headers: self.loaded_app = ProxyHeadersMiddleware(self.loaded_app, trusted_hosts=self.forwarded_allow_ips)`.
- `config.py`: `if forwarded_allow_ips is None: self.forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")`.
  Runtime proof:
  ```
  FORWARDED_ALLOW_IPS='*' python3 -c "...Config('app.main:app')..."  -> forwarded_allow_ips= '*' proxy_headers= True
  python3 -c "...Config('app.main:app')..."                          -> forwarded_allow_ips= '127.0.0.1' proxy_headers= True
  ```
  So without the compose line the trusted set is `127.0.0.1` (Nginx's bridge IP is NOT trusted →
  `http://`), and with it the set is `*` (trusted → `https`).
- `uvicorn/middleware/proxy_headers.py`: handles `x-forwarded-proto` (sets `scope["scheme"]`) and
  `x-forwarded-for` (sets `scope["client"]`); it does **NOT** touch `x-forwarded-host`. Host is taken
  from the `Host` header, which Nginx sets to `$host`. This confirms the claimed nuance.

**Independent evidence — the code uses the request URL (no manual reconstruction):**
- `App/Backend/app/routes/cost_guard.py:123`:
  `verify_signature(auth_token, signature, str(request.url), form)` — the URL is derived from the
  request scope, so the trusted scheme is what determines the signed string.

**Independent evidence — the new tests exercise the real middleware and derive the value from compose:**
- `tests/test_runtime_cost_guard.py:41` imports the real
  `uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware`.
- `_backend_forwarded_allow_ips()` (lines 1305-1319) parses `docker-compose.yml` and resolves
  `${FORWARDED_ALLOW_IPS:-*}` → `*`; `_client_with_guard(..., proxy_trusted_hosts=...)` wraps the
  ASGI app in the real `ProxyHeadersMiddleware` (lines 1274-1277).
- The five W1/W2 tests pass in isolation:
  ```
  tests/test_runtime_cost_guard.py::test_compose_backend_confia_en_los_headers_del_proxy PASSED
  tests/test_runtime_cost_guard.py::test_twilio_firma_https_valida_con_headers_del_proxy PASSED
  tests/test_runtime_cost_guard.py::test_twilio_firma_http_no_valida_cuando_el_proxy_declara_https PASSED
  tests/test_runtime_cost_guard.py::test_openapi_twilio_voice_200_declara_text_xml PASSED
  tests/test_runtime_cost_guard.py::test_openapi_endpoints_de_guarda_declaran_401 PASSED
  ================= 5 passed, 67 deselected, 1 warning in 0.81s =================
  ```
- `test_twilio_firma_https_valida_con_headers_del_proxy` computes the signature over
  `https://test/api/v1/cost-guard/twilio/voice`, sends `X-Forwarded-Proto: https` through the real
  middleware, and gets **200 + text/xml**. Its triangulation sends a signature computed over
  `http://…` and gets **401** — proving the reconstructed scheme (not luck) is what validates.

**Documentation of the trust assumption:**
- `docs/operational-guide.md` §11.6 (lines 632-650): explains `FORWARDED_ALLOW_IPS`, that `*` is safe
  because port 8000 is unpublished and Nginx overwrites `X-Forwarded-Proto`, and states the operator
  action — if the backend is published or deployed outside this compose, pin `FORWARDED_ALLOW_IPS`
  to the proxy subnet (never empty). It also states the Twilio console URL must match the
  reconstructed URL exactly.
- `README.md:125-131`, root `.env.example:55-61` (`FORWARDED_ALLOW_IPS=*` with the same rationale),
  and `docker-compose.yml:91-100` (inline comment).

**Assessment of `*` safety and the documented caveat:** Acceptable **within this compose**. The
backend has no published port, so no external client can reach `backend:8000`; the only path is
through Nginx, which overwrites `X-Forwarded-Proto` (and `Host`), so an external attacker cannot
forge the scheme. The caveat is sufficient and correctly actionable: it tells the operator to pin
the proxy subnet if the backend is ever exposed outside this compose, and warns never to leave the
value empty. One benign side effect worth recording (see SUGGESTION): `*` also trusts
`X-Forwarded-For`, making `request.client` attacker-influenced — but a full-repo search shows **no
app code uses `request.client` or `X-Forwarded-For`** (`grep -rn "request.client\|X-Forwarded-For" app/`
returns nothing), and the guard's rate limiting keys on the phone `From`, not the client IP. So the
side effect is inert here.

### W2 — OpenAPI documents the Twilio media type and both 401s — **RESOLVED**

Inspected the committed `docs/openapi.json` (generated by `App/Backend/scripts/export_openapi.py`):
```
/api/v1/cost-guard/twilio/voice POST responses:
  200.content = { "text/xml": { "schema": { "type": "string" } } }     <- was application/json
  401.description = "Firma `X-Twilio-Signature` ausente o invalida, o `TWILIO_AUTH_TOKEN` ..."
  parameters = ['X-Twilio-Signature']
/api/v1/cost-guard/reserve POST responses:
  200.content = application/json (CostGuardReserveResponse)
  401.description = "Header `X-Cost-Guard-Secret` ausente o distinto, o `COST_GUARD_SHARED_SECRET` ..."
  parameters = ['X-Cost-Guard-Secret']
```
- Route wiring: `cost_guard.py:68-77` declares `TwimlResponse(Response)` with
  `media_type = TWIML_MEDIA_TYPE` and passes `response_class=TwimlResponse` (line 178); both routes
  declare `responses={401: {...}}` (lines 144-151, 179-186).
- Guarding tests `test_openapi_twilio_voice_200_declara_text_xml` and
  `test_openapi_endpoints_de_guarda_declaran_401` pass (see above), and the sync test
  `test_openapi_in_sync_with_app` confirms the committed file equals the live schema.

---

## Warning 1-5 Status (carried from the previous reports)

| # | Warning | Status | Evidence |
|---|---------|--------|----------|
| 1 | Guard endpoints unauthenticated by default; secret optional; query allowed | **RESOLVED** | `/reserve`: mandatory header `X-Cost-Guard-Secret`, `hmac.compare_digest`, 401 when unconfigured (`routes/cost_guard.py:80-100,166`); query rejected (`test_endpoint_twilio_no_acepta_secreto_por_query`). `/twilio/voice`: signature-only, 401 fail-closed without token (`:103-127,207`). |
| 2 | `fail_open` + `COST_GUARD_ALERT_ENABLED` documented but dead | **RESOLVED** | `test_store_caido_fail_open_permite_la_llamada`, `test_store_caido_fail_closed_sigue_siendo_el_default`, `test_alert_enabled_controla_la_notificacion_externa`, `test_alert_disabled_no_emite_notificacion_externa`, `test_notificacion_externa_no_altera_la_decision_si_falla` — all pass. |
| 3 | `X-Twilio-Signature` not validated; artifacts disagree | **RESOLVED** | `twilio_signature.py` + route wiring + SDK vector test; `design.md:115,199` reconciled; `docs/openapi.json` lists `X-Twilio-Signature` for the Twilio endpoint. |
| 4 | Transcript field uncertainty not repeated in operational docs | **DOCUMENTED** | `docs/operational-guide.md` §11.7 (line 651) and `docs/n8n-workflow-guide.md:91-96`. |
| 5 | Integration suite not reproducible (volume password drift) | **DOCUMENTED** (not re-run here) | `docs/operational-guide.md` §11.8 (line 670). Not required by this re-verification; the offline subset was used. |

**Artifacts reconciled:** `design.md` D7/risk no longer mandates the header for Twilio (line 115
"EXCLUSIVAMENTE con la firma"); `docs/operational-guide.md` §11.2/§11.6, `docs/n8n-workflow-guide.md`
§2, `README.md:100,120-131`, `App/Backend/.env.example`, root `.env.example`, `n8n/twilio/README.md`
and `n8n/twilio/twiml.xml` describe the achievable setup.

---

## B1 / B2 Status (previously resolved — re-confirmed)

- **B1 RESOLVED** — `twilio_voice_webhook` (`cost_guard.py:188-210`) calls only
  `_require_twilio_signature`, never `_require_secret`; `_require_secret` is used only by `/reserve`
  (line 166). Twilio's auth is exclusively `X-Twilio-Signature` (HMAC-SHA1 over URL + sorted params,
  constant-time compare, with/without-port tolerance in `twilio_signature.py`).
- **B2 RESOLVED** — `docker-compose.yml:90` (backend) and `:136` (n8n) both use
  `COST_GUARD_SHARED_SECRET: ${COST_GUARD_SHARED_SECRET:-}`; `docker compose config` shows the same
  value in both services:
  ```
  backend COST_GUARD_SHARED_SECRET= ''
  n8n     COST_GUARD_SHARED_SECRET= ''
  ```
  `n8n/workflow.json` node `Guard de costo` references `$env.COST_GUARD_SHARED_SECRET` and sends
  header `X-Cost-Guard-Secret` (verified by parsing the JSON).

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 81 |
| Tasks complete | 81 |
| Tasks incomplete | 0 |

`openspec status --change c-45-runtime-cost-guard` → `Progress: 4/4 artifacts complete`. Section 18
(W1/W2 close-out, 18.1-18.5) present and all `[x]`. `openspec validate --strict` passes.

---

## Build & Tests Execution

**Lint**: `cd App/Backend; ruff check .` → ✅ `All checks passed!` (exit 0)

**Tests (change-specific)**: ✅ **72 passed**
```
cd App/Backend; pytest tests/test_runtime_cost_guard.py -q
72 passed, 1 warning in 3.27s
```

**Tests (offline suite)**: ✅ **545 passed** / 0 failed / 25 deselected / 1 xfailed
```
cd App/Backend; pytest -m "not integration" -q
545 passed, 25 deselected, 1 xfailed, 145 warnings in 80.13s (0:01:20)
```

**Tests (W1/W2 targeted)**: ✅ 5 passed
```
cd App/Backend; pytest tests/test_runtime_cost_guard.py -v -k "proxy or forwarded or openapi_twilio or openapi_endpoints"
5 passed, 67 deselected, 1 warning in 0.81s
```

**OpenAPI sync**: ✅ 5 passed
```
cd App/Backend; pytest tests/test_openapi_sync.py -q
5 passed, 1 warning in 0.22s
```

**openspec validate**: ✅
```
openspec validate --strict --changes c-45-runtime-cost-guard
✓ change/c-45-runtime-cost-guard
Totals: 1 passed, 0 failed (1 items)
```

**Structural (compose)**: ✅ backend has no published port; Nginx owns 80/443;
`FORWARDED_ALLOW_IPS` resolves to `*`; `COST_GUARD_SHARED_SECRET` identical on backend and n8n.

**Structural (n8n)**: ✅ `n8n/workflow.json` parses (34 nodes, guard + IF present, secret + header
present); `n8n/twilio/twiml.xml` is valid XML.

**PostgreSQL integration subset**: ➖ not re-run in this pass (warning 5 remains an environment
drift, documented in §11.8). The offline suite fully covers the change; nothing in the W1/W2 fix
touches the PostgreSQL path.

**Coverage**: not run (no threshold configured for this change).

---

## Spec Compliance Matrix

Legend: ✅ COMPLIANT (real passing test) · ⚠️ PARTIAL (test passes but scenario not fully
demonstrated end-to-end) · ❌ UNTESTED/FAILING.
Delta spec has **14 requirements / 37 scenarios**; all map to tests in the passing
`test_runtime_cost_guard.py`.

| # | Requirement | Scenario | Test | Result |
|---|-------------|----------|------|--------|
| R1 | Presupuesto global compartido | Gasto por debajo permite | `test_decision_permite_por_debajo_del_presupuesto` | ✅ |
| R1 | | Gasto de una superficie consume la bolsa | `test_superficies_distintas_comparten_bolsa_global`, `test_gasto_de_una_superficie_afecta_la_evaluacion_de_otra` | ✅ |
| R1 | | Presupuesto agotado dispara en cualquier superficie | `test_decision_deniega_presupuesto_agotado`, `test_disparo_emite_evento_estructurado`, `test_fake_rollback_descarta_reserva` | ✅ |
| R1 | | Ventana nueva reinicia el gasto | `test_ventana_de_presupuesto_se_reinicia` | ✅ |
| R2 | Costo unitario por superficie | Reserva usa el costo de la superficie | `test_fake_commit_aplica_reserva` | ✅ |
| R2 | | Superficies distintas, costos distintos | `test_superficies_distintas_comparten_bolsa_global` | ✅ |
| R3 | Límite de tasa | Tasa por debajo permite | `test_decision_permite_por_debajo_del_presupuesto` | ✅ |
| R3 | | Límite alcanzado dispara | `test_decision_deniega_rate_global`, `test_ventana_de_rate_global_se_reinicia` | ✅ |
| R3 | | Reinicio de ventana rehabilita | `test_ventana_de_rate_global_se_reinicia` | ✅ |
| R4 | Tasa por número de origen | Origen por debajo permite | `test_origen_excedido_no_bloquea_a_otros_origenes` | ✅ |
| R4 | | Origen excedido dispara solo para ese origen | `test_origen_excedido_no_bloquea_a_otros_origenes` | ✅ |
| R4 | | Reinicio de ventana del origen | `test_ventana_por_origen_se_reinicia` | ✅ |
| R5 | Evaluación antes de la llamada paga | Solo con guarda permitiendo | `test_guarda_permite_y_gemini_se_invoca`, `test_guarda_disparada_no_invoca_al_proveedor_y_degrada` | ✅ |
| R5 | | Precalculada no consume presupuesto | `test_clasificacion_precalculada_no_consume_presupuesto` | ✅ |
| R5 | | Cortocircuito determinístico no consume | `test_cortocircuito_deterministico_no_consume_presupuesto` | ✅ |
| R6 | Enforcement AI Agent n8n | Guarda permite → AI Agent se invoca | `test_workflow_guarda_de_costo_entrega_al_ai_agent_y_deriva_al_denegar` | ⚠️ PARTIAL (structural JSON only; no runtime n8n test) |
| R6 | | Guarda deniega → AI Agent NO se invoca | `test_workflow_guarda_de_costo_entrega_al_ai_agent_y_deriva_al_denegar` | ⚠️ PARTIAL |
| R7 | Enforcement pre-llamada Twilio | Permite → graba con transcripción | `test_webhook_twilio_permite_devuelve_record_con_transcripcion`, `test_twilio_firma_https_valida_con_headers_del_proxy` (real ProxyHeadersMiddleware + `X-Forwarded-Proto: https`) | ✅ COMPLIANT (W1 closed) |
| R7 | | Deniega → no graba ni transcribe | `test_webhook_twilio_deniega_devuelve_say_y_hangup` | ✅ |
| R7 | | Reserva no depende de la duración | `test_webhook_twilio_reserva_una_unidad_por_llamada` | ✅ |
| R8 | Caller crudo | Se registra crudo en eventos | `test_caller_crudo_aparece_en_eventos_de_guarda` | ✅ |
| R8 | | No entra al corpus de evaluación | `test_corpus_de_evaluacion_no_incorpora_el_caller` | ⚠️ PARTIAL (asserts dataclass field set only) |
| R9 | Degradación segura | Fallback determinístico + revisión | `test_guarda_disparada_no_invoca_al_proveedor_y_degrada` | ✅ |
| R9 | | Bloqueo duro propaga señal | `test_politica_hard_block_no_invoca_al_proveedor_y_propaga_senal` | ✅ |
| R9 | | Ninguna política invoca al proveedor pago | both (`gemini.classify.assert_not_called()`) | ✅ |
| R10 | Fail-closed con notificación | Almacén caído deniega + degrada | `test_store_inalcanzable_fail_closed_y_notificacion` | ✅ |
| R10 | | Emite notificación estructurada | `test_store_inalcanzable_fail_closed_y_notificacion` | ✅ |
| R10 | | Política no implícita / configurable | `test_politica_fail_closed_es_explicita`, `test_settings_defaults_conservadores`, `test_store_caido_fail_open_permite_la_llamada` | ✅ |
| R11 | Default habilitado conservador | Sin config arranca habilitada conservadora | `test_settings_defaults_conservadores` | ✅ |
| R11 | | Override por entorno | `test_settings_override_por_entorno` | ✅ |
| R11 | | Default estable entre arranques | `test_settings_default_es_estable_entre_instanciaciones` | ✅ |
| R12 | Observabilidad | Disparo emite evento estructurado | `test_disparo_emite_evento_estructurado` | ✅ |
| R12 | | Llamada permitida no emite evento | `test_llamada_permitida_no_emite_evento_de_disparo` | ✅ |
| R13 | Postura al arranque | Registra postura efectiva | `test_postura_registra_estado_efectivo`, `test_lifespan_registra_postura_de_la_guarda`, `test_postura_advierte_si_falta_el_secreto_compartido`, `test_postura_advierte_si_falta_el_token_de_twilio` | ✅ |
| R13 | | Config inválida no arranca ambiguo | `test_settings_configuracion_invalida_falla_explicito` | ✅ |
| R14 | Evaluabilidad offline | Almacén y reloj inyectados | `test_fake_commit_aplica_reserva` + all offline guard tests | ✅ |
| R14 | | Reinicio de ventana sin servicios reales | `test_ventana_de_presupuesto_se_reinicia` | ✅ |

**Compliance summary**: **34/37 COMPLIANT, 3/37 PARTIAL, 0 UNTESTED, 0 FAILING.**
No scenario lost coverage. R7-permit **moved from PARTIAL to COMPLIANT** because the former caveat
(W1) is now closed and backed by a test that exercises the real Uvicorn middleware. The 3 remaining
PARTIALs are unchanged and non-blocking: R6 x2 (structural n8n JSON only) and R8 x1 (corpus check is
a dataclass field-set assertion).

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| R1 shared global budget | ✅ Implemented | `cost_guard/guard.py`, `decision.py`; passing tests. |
| R2 per-surface unit cost | ✅ Implemented | Same pool, per-surface unit costs. |
| R3 global rate limit | ✅ Implemented | `decision.py:91`. |
| R4 per-origin rate limit | ✅ Implemented | `decision.py:95`; caller key. |
| R5 guard before paid call | ✅ Implemented | `incidente_service.py`; precalc/deterministic bypass. |
| R6 n8n AI Agent enforcement | ✅ Implemented (structural) | `workflow.json` guard + IF; no live n8n test. |
| R7 Twilio pre-call webhook | ✅ Implemented | TwiML allow/deny; signature-only; proxy trust wired. |
| R8 raw caller capture/exclusion | ✅ Implemented | Raw in events; not in business tables; corpus field set excludes it. |
| R9 safe degradation | ✅ Implemented | `hybrid.py`; never invokes paid provider. |
| R10 fail-closed + notification | ✅ Implemented | Policy configurable; event always emitted. |
| R11 conservative default | ✅ Implemented | `settings.py:106-137`. |
| R12 observability | ✅ Implemented | `cost_guard_tripped` / `cost_guard_store_unavailable`. |
| R13 startup posture | ✅ Implemented | `posture.py`, `main.py:146`. |
| R14 offline evaluability | ✅ Implemented | Injected store/clock; in-memory fake. |

---

## Core Invariants — re-check

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Shared GLOBAL budget; per-surface unit cost; same pool | ✅ | `guard.py`, `decision.py`; passing tests. |
| Precalc + deterministic short-circuit never consult guard | ✅ | `test_clasificacion_precalculada_no_consume_presupuesto`, `test_cortocircuito_deterministico_no_consume_presupuesto`. |
| On trip: paid provider NOT invoked; deterministic + human review | ✅ | `hybrid.py`; passing tests. |
| Store unavailable → fail-closed + structured event; fail_open opt-in | ✅ | `guard.py`; `test_store_inalcanzable_fail_closed_y_notificacion`, `test_store_caido_fail_open_permite_la_llamada`. |
| Twilio allow → `<Record transcribe="true">`; deny → `<Say>`+`<Hangup>` | ✅ | `test_webhook_twilio_*`; W1 test over real proxy middleware. |
| Raw caller in guard events; corpus excludes it | ✅ (corpus check ⚠️ PARTIAL) | `guard.py`; `evaluation/corpus.py` has no caller/phone field. |
| Enabled-conservative default; `.env` override; invalid config fails | ✅ | `settings.py:106-137`. |
| Defaults unchanged (USD 10/week, fail_closed, alert on) | ✅ | `settings.py:106-137`. |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 new capability `runtime-cost-guard` | ✅ Yes | No `cost-readiness` change. |
| D2 wrapper + injectable store/clock | ✅ Yes | |
| D3 global pool + per-surface unit cost; pure decision | ✅ Yes | |
| D4 configurable degradation | ✅ Yes | |
| D5 structlog events + startup posture | ✅ Yes | |
| D6 PostgreSQL + migration 007 | ✅ Yes | |
| D7 Twilio pre-call webhook, signature-only auth | ✅ Yes | `design.md:115` reconciled; W1 proxy trust now wired + documented. |
| D8 n8n guard node + IF + wired secret | ✅ Yes | B2 fixed. |
| D9 raw caller captured; excluded from corpus | ✅ Yes | |
| D10 fail_closed default; fail_open supported; alert controllable | ✅ Yes | |

---

## Issues Found

### CRITICAL (must fix before archive)

**None.** No blockers. B1/B2 remain resolved and W1/W2 are now closed.

### WARNING (should fix)

1. **W3 — No behavioral test for n8n enforcement (carried over).** R6 is covered only by structural
   JSON assertions; the real 401/deny path is not exercised. Not a regression and not feasible
   offline without a live n8n; accepted.
2. **R8 corpus check is structural only (carried over).** `test_corpus_de_evaluacion_no_incorpora_el_caller`
   asserts the dataclass field set, not that a generated corpus row cannot carry the caller. Low
   impact: `evaluation/corpus.py` has no caller field at all.
3. **Warning 5 — PostgreSQL integration subset not re-run** in this pass (environment drift,
   documented in §11.8). The offline suite covers the change; the W1/W2 fix does not touch the
   PostgreSQL path.

### SUGGESTION (nice to have)

- `FORWARDED_ALLOW_IPS=*` also makes Uvicorn trust `X-Forwarded-For`, so `request.client` becomes
  attacker-influenced through Nginx. Currently inert: a full-repo search shows no app code reads
  `request.client` or `X-Forwarded-For`, and guard rate limiting keys on the phone `From`. If future
  code ever trusts `request.client`, pin the proxy subnet instead of `*` or sanitize XFF.
- Strict `>` boundary semantics on rolling reservation (unchanged; committed cap respected).
- Recreate the running containers so the B2/W1 wiring takes effect
  (`docker compose up -d --force-recreate backend n8n`); a live container created before the fix
  would not have `COST_GUARD_SHARED_SECRET`/`FORWARDED_ALLOW_IPS`.

---

## Residual Risk

- **Operational (W1 follow-through):** the fix is correct **only** while the backend stays
  unpublished and Nginx keeps overwriting `X-Forwarded-Proto`. If the backend is ever published or
  deployed outside this compose, `FORWARDED_ALLOW_IPS` must be pinned to the proxy subnet. This is
  explicitly documented in `docs/operational-guide.md` §11.6, `README.md`, and root `.env.example`.
  No code-level residual.
- **Twilio reachability:** the shipped compose now reconstructs `https://<host>/...`, so the
  signature can validate once `TWILIO_AUTH_TOKEN` is set and the Twilio console URL matches exactly.
  The remaining requirement is operator configuration (token + console URL), which is documented.
- **R6/R8 partial coverage** — unchanged, non-blocking.

## Exact Reproduction

```bash
# W1 — proxy trust wiring (resolved model)
docker compose config | python3 -c "import sys,yaml; c=yaml.safe_load(sys.stdin); \
  print('backend ports=', c['services']['backend'].get('ports')); \
  print('nginx ports=', c['services']['nginx']['ports']); \
  print('FORWARDED_ALLOW_IPS=', repr(c['services']['backend']['environment'].get('FORWARDED_ALLOW_IPS')))"
# backend ports= None ; nginx ports= 80/443 ; FORWARDED_ALLOW_IPS= '*'
grep -n "X-Forwarded-Proto" nginx/nginx.conf            # :55 proxy_set_header X-Forwarded-Proto $scheme;
grep -n "str(request.url)" App/Backend/app/routes/cost_guard.py   # :123

# W1 — Uvicorn actually honors FORWARDED_ALLOW_IPS / installs the middleware
cd App/Backend
FORWARDED_ALLOW_IPS='*' python3 -c "from uvicorn.config import Config; c=Config('app.main:app'); print(repr(c.forwarded_allow_ips), c.proxy_headers)"
python3 -c "from uvicorn.config import Config; c=Config('app.main:app'); print(repr(c.forwarded_allow_ips), c.proxy_headers)"
grep -n "ProxyHeadersMiddleware" /home/skywalker/.local/lib/python3.12/site-packages/uvicorn/config.py  # :470

# W1/W2 tests
pytest tests/test_runtime_cost_guard.py -v -k "proxy or forwarded or openapi_twilio or openapi_endpoints"   # 5 passed

# W2 — generated OpenAPI
python3 -c "import json; d=json.load(open('../../docs/openapi.json')); \
  print(d['paths']['/api/v1/cost-guard/twilio/voice']['post']['responses']['200']['content']); \
  print('401' in d['paths']['/api/v1/cost-guard/reserve']['post']['responses'])"

# Commands claimed
pytest tests/test_runtime_cost_guard.py -q      # 72 passed
pytest -m "not integration" -q                  # 545 passed, 25 deselected, 1 xfailed
ruff check .                                    # All checks passed!
pytest tests/test_openapi_sync.py -q            # 5 passed
openspec validate --strict --changes c-45-runtime-cost-guard   # 1 passed, 0 failed
```

---

## Verdict

**READY TO ARCHIVE** (no blockers; non-blocking warnings remain)

W1 and W2 are resolved with independent, reproducible evidence: the proxy trust is real at the
Uvicorn level, the backend publishes no port, Nginx overwrites the forwarded scheme, the code
verifies against `str(request.url)`, and the new tests exercise the actual
`ProxyHeadersMiddleware` with the value derived from `docker-compose.yml`; the OpenAPI artifact now
documents `text/xml` and both `401`s. All prior warnings 1-5 remain resolved or documented, B1/B2
remain resolved, and the full offline suite (545), guard tests (72), OpenAPI sync (5), `ruff`, and
`openspec validate --strict` all pass with no regressions. The change is functionally correct and
ready to archive; the remaining R6/R8 partial coverage and the not-re-run PostgreSQL integration
subset are documented, non-blocking residuals.
