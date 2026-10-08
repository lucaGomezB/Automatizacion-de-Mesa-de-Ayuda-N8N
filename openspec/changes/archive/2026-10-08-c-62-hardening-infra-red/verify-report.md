# Verification Report: c-62-hardening-infra-red

**Change**: c-62-hardening-infra-red
**Date**: 2026-10-08
**Verifier**: sdd-verify (independent, from repo state + executed commands)
**Mode**: Strict TDD (environment-declared) — config-only change; TDD behavioral evidence is the new structural suite `App/Backend/tests/test_c62_infra_hardening.py`
**Governance**: ALTO (infra access boundary)
**Resolved OQs verified against**: OQ-1=A loopback, OQ-2=A Redis retired, OQ-3=three networks, OQ-4=A loopback UI, OQ-5=B `docker-compose.dev.yml`, OQ-6=nginx hardened (CSP deferred), OQ-7=corpus loopback, OQ-8=no documented-command changes

---

## 1. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 33 |
| Tasks complete `[x]` | 33 |
| Tasks incomplete `[ ]` | 0 |
| N/A tasks | 2 (2.3, 3.3) |

Both N/A tasks carry a correct conditional rationale given the resolved OQs:

- **2.3** ("Si OQ-1 elige el retiro, crear el mecanismo de acceso de desarrollo opt-in"): OQ-1=A keeps loopback publication (does NOT retire). Condition false -> N/A. The dev opt-in shipped anyway under OQ-5=B (`docker-compose.dev.yml`, no port re-exposure).
- **3.3** ("Si Redis se conserva, agregar REDIS_PASSWORD"): OQ-2=A retires Redis. Condition false -> N/A. `.env.example` correctly documents "no hay REDIS_PASSWORD que configurar".

Group 8 (preflight/c-72 realignment) is fully complete (8.1-8.4).

---

## 2. Build & Tests Execution

### 2.1 Compose configuration (effective)

`docker compose -p mesa_local config` -> exit 0. `docker compose -p mesa_local --profile corpus config` -> exit 0.

Base stack services: `backend, frontend, n8n, nginx, postgres` (no `redis`).

| Service | Published port (effective) | Loopback? |
|---------|---------------------------|-----------|
| postgres | `127.0.0.1:5433 -> 5432` | YES |
| n8n | `127.0.0.1:5678 -> 5678` | YES |
| nginx | `80 -> 80`, `443 -> 443` | NO (0.0.0.0, intended) |
| backend | none | n/a |
| frontend | none | n/a |

Corpus profile adds: `postgres-corpus 127.0.0.1:5434`, `backend-corpus 127.0.0.1:8001`, `n8n-corpus 127.0.0.1:5679` (all loopback). No `redis` in either rendering.

Declared networks (both renderings): `edge`, `data` (`internal: true`), `automation`, `host_access` (not internal).

### 2.2 Network membership (computed from compose config)

Base:
- `edge` = {backend, frontend, nginx}
- `data` = {backend, postgres}
- `automation` = {backend, n8n}
- `host_access` = {postgres}

Corpus:
- `edge` = {backend, backend-corpus, frontend, nginx}
- `data` = {backend, backend-corpus, postgres, postgres-corpus}
- `automation` = {backend, backend-corpus, n8n, n8n-corpus}
- `host_access` = {postgres, postgres-corpus}

Assertions:
- `n8n` & `postgres` share a network: **NONE** (base).
- `n8n-corpus` & `postgres-corpus` share a network: **NONE** (corpus).
- support network `host_access` membership is bounded to `{postgres, postgres-corpus}`: **holds** (no n8n/nginx/frontend).

### 2.3 Test executions (exact counts)

| Command | Result |
|---------|--------|
| `python3 -m pytest tests/test_c62_infra_hardening.py -q` | **31 passed** |
| `python3 -m pytest -m "not integration" -q` | **1090 passed, 42 deselected, 1 xfailed**, exit 0 (133.27s) |
| `python3 -m pytest scripts/preflight -q` | **48 passed** |
| `python3 -m pytest scripts/corpus_ingest/test_corpus_compose_isolation.py -q` | **8 passed** |
| `python3 scripts/preflight/cost_readiness.py` | **10/10 PASS, GREEN**, exit 0 |
| `python3 scripts/preflight/gemini_readiness.py` | **2/2 PASS, GREEN**, exit 0 |
| `openspec validate c-62-hardening-infra-red --strict` | **valid**, exit 0 |

### 2.4 Live stack (started and torn down)

`docker compose -p mesa_local up -d` -> exit 0. `docker compose ps`:

```
mesa_local-backend-1    backend    Up (healthy)   8000/tcp
mesa_local-frontend-1   frontend   Up (healthy)   80/tcp, 3000/tcp
mesa_local-n8n-1        n8n        Up             127.0.0.1:5678->5678/tcp
mesa_local-nginx-1      nginx      Up             0.0.0.0:80->80, 0.0.0.0:443->443
mesa_local-postgres-1   postgres   Up (healthy)   127.0.0.1:5433->5432/tcp
```

- No Redis service; all required services healthy.
- `curl -k -fsS https://localhost/api/v1/health` -> `{"status":"ok","version":"1.0.0"}` (exit 0).
- nginx headers: `server: nginx` (no version), `referrer-policy: strict-origin-when-cross-origin`, `permissions-policy: geolocation=(), microphone=(), camera=(), payment=()` (plus HSTS, X-Content-Type-Options, X-Frame-Options).
- HTTP->HTTPS: `http://localhost/` -> `301`, `location: https://localhost/`.
- Unknown Host/SNI (resolved to 127.0.0.1): empty reply => **444**.
- Rate limit login: 50 rapid POSTs -> `44 x 429`, `6 x 422` (burst passes, excess 429).
- Host listeners: `127.0.0.1:5678` and `127.0.0.1:5433` only.
- n8n auth: `/rest/workflows` -> 401, `/rest/login` -> 401 (root `/` serves the 200 login SPA).
- `docker compose -p mesa_local down` -> exit 0, no containers/ports left.

---

## 3. Spec Compliance Matrix

| Requirement | Scenario | Test / Evidence | Result |
|-------------|----------|-----------------|--------|
| INFRA-001 | PostgreSQL y N8N publican solo en loopback | `test_c62_infra_hardening.py::test_postgres_is_bound_to_loopback_only`, `::test_n8n_ui_is_bound_to_loopback_only`, `::test_no_published_port_is_exposed_on_all_interfaces`; live `config host_ip: 127.0.0.1` + `ss` 127.0.0.1:5433/5678 | PROVEN |
| INFRA-001 | Backend alcanza N8N por la red interna | Structural: backend+n8n share `automation`; `N8N_WEBHOOK_URL=http://n8n:5678/...`; n8n depends_on backend healthy. No end-to-end delivery assertion executed | PARTIAL |
| INFRA-002 | Tests de integracion alcanzan PostgreSQL por loopback | `test_postgres_is_bound_to_loopback_only`; `conftest.py:85` default `localhost:5433`; port loopback-published. Integration subset NOT executed in this verify | PARTIAL |
| INFRA-002 | PostgreSQL no expuesto a la LAN | live `ss` shows `127.0.0.1:5433` only | PROVEN |
| INFRA-003 | Redis sin consumidores (retiro documentado) | `test_redis_service_was_retired`, `::test_no_service_depends_on_the_retired_redis`, `::test_no_queue_bull_redis_variables_remain`; proposal/design OQ-2=A; compose renders no `redis` | PROVEN |
| INFRA-003 | Redis con autenticacion / acceso sin credenciales rechazado | Not applicable — service retired (applicable branch = "sin consumidores") | N/A |
| INFRA-004 | N8N y PostgreSQL no comparten red | `::test_no_network_contains_an_automation_and_a_data_service` (+ corpus pair); computed membership = NONE | PROVEN |
| INFRA-004 | Red de soporte no incluye N8N ni proxy/frontend | `::test_host_access_network_exists_only_to_publish_data_ports`; membership `{postgres, postgres-corpus}` | PROVEN |
| INFRA-004 | Arranque sano con segmentacion | live `up -d` -> all healthy (`docker compose ps`); health 200 | PROVEN |
| INFRA-005 | UI no expuesta sin auth en 0.0.0.0 | `::test_n8n_ui_is_bound_to_loopback_only`; live 127.0.0.1:5678 only | PROVEN |
| INFRA-005 | Canal habilitado exige autenticacion | live `/rest/workflows` -> 401, `/rest/login` -> 401 | PROVEN |
| INFRA-006 | Version de nginx no expuesta | `::test_nginx_hides_its_version`; live `server: nginx` | PROVEN |
| INFRA-006 | Limite de tasa sobre endpoint publico | `::test_nginx_rate_limits_login_and_webhooks`; live 44x429 | PROVEN |
| INFRA-006 | Host desconocido rechazado (444) | `::test_nginx_keeps_catchall_and_http_to_https_redirect`; live empty reply (444) | PROVEN |
| INFRA-007 | Modo por defecto endurecido | `::test_default_compose_does_not_enable_development_app_posture`; live default hardened | PROVEN |
| INFRA-007 | Acceso de desarrollo opt-in | `::test_dev_override_exists`, `::test_dev_override_declares_development_environment`, `::test_dev_override_is_not_a_port_reexposer` | PROVEN |
| INFRA-008 | Preflight de costo pasa con compose modificado | `python3 scripts/preflight/cost_readiness.py` 10/10 GREEN exit 0; `::test_n8n_image_stays_pinned`, `::test_n8n_webhook_url_keeps_the_dedicated_route`, `::test_n8n_execution_timeouts_are_preserved` | PROVEN |
| INFRA-008 | CI no depende del compose | `.github/workflows/ci.yml:87` `TEST_PG_URL=...localhost:5432` service container; compose not used for integration | PROVEN |
| INFRA-009 | Documentacion vigente sin accesos rotos | README/AGENTS/operational-guide updated to loopback; consumers still use `localhost:5433`/`localhost:5678`; both loopback-published | PROVEN |
| INFRA-009 | Dry-run alcanza N8N | `dry_run.py` defaults `--n8n-host localhost --n8n-port 5678`; port loopback-bound. Harness NOT executed live | PARTIAL |
| ENV-001 | Variables de retencion presentes | `::test_n8n_execution_timeouts_are_preserved` (`EXECUTIONS_DATA_PRUNE=true`, `EXECUTIONS_DATA_MAX_AGE=720`) | PROVEN |
| ENV-001 | Resto de config N8N sin cambios | compose diff: only Redis vars/ports/networks changed; `BACKEND_URL`, `N8N_BASIC_AUTH_ACTIVE`, `COST_GUARD_SHARED_SECRET`, volumes intact; `N8N_WEBHOOK_URL` route unchanged | PROVEN |
| ENV-001 | Exposicion puede cambiar sin afectar retencion | retention vars present in hardened service (live up) | PROVEN |

**Compliance summary**: 22/25 scenarios PROVEN, 3/25 PARTIAL (all PARTIAL are "not executed end-to-end" gaps, not failures), 0 FAILING, 0 UNTESTED (the INFRA-003 auth scenarios are legitimately N/A by resolution).

---

## 4. Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| INFRA-001 | Implemented | `docker-compose.yml:62,138` loopback bindings |
| INFRA-002 | Implemented | `docker-compose.yml:62`; `conftest.py:85` unchanged, still valid |
| INFRA-003 | Implemented | Redis service/depends_on/QUEUE_BULL_REDIS_* removed (compose diff) |
| INFRA-004 | Implemented | `docker-compose.yml:426-443` four networks; `data` internal; `host_access` bounded |
| INFRA-005 | Implemented | n8n loopback only (`docker-compose.yml:138`); basic auth active |
| INFRA-006 | Implemented | `nginx/nginx.conf:11,16-17,80-81,84,96-135` |
| INFRA-007 | Implemented | `docker-compose.dev.yml` (ENVIRONMENT=development, no ports) |
| INFRA-008 | Implemented | `scripts/preflight/*` realigned; CI contracts preserved |
| INFRA-009 | Implemented | docs updated; consumers still valid |
| ENV-001 | Implemented | retention vars intact |

---

## 5. Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 / OQ-1=A loopback | Yes | all base ports 127.0.0.1 |
| D2 / OQ-2=A Redis retired | Yes | no service, no vars, no depends_on |
| D3 / OQ-3 three networks | Yes (extended) | `edge`/`data`/`automation` + `host_access` support network, explicitly permitted by INFRA-004 |
| D4 / OQ-4=A loopback UI | Yes | 127.0.0.1:5678 |
| D5 / OQ-5=B dev override file | Yes | `docker-compose.dev.yml`, no port re-exposure |
| D6 / OQ-6 nginx hardened, CSP deferred | Yes | `server_tokens off`, both headers, rate limits; no CSP directive (test asserts) |
| D3 corpus mirror (OQ-7) | Yes | corpus ports loopback; corpus test literals updated |
| OQ-8 no command changes | Yes | `TEST_PG_URL`/`localhost:5678` unchanged |

**Coherence note (SUGGESTION)**: `design.md` D3 table still describes exactly three networks; the implementation adds `host_access` as a fourth. This is spec-sanctioned (INFRA-004 allows a support network) but the design artifact was not updated to list it. Documentation-only; no behavioral deviation.

---

## 6. Adversarial Checks

### 6.1 CI contracts preserved in `docker-compose.yml`
- n8n image pinned: `n8nio/n8n:2.11.2` (`docker-compose.yml:133`), asserted by preflight PASS.
- `N8N_WEBHOOK_URL` dedicated route: `http://n8n:5678/webhook/notificacion-clasificacion` (`:90`), preflight PASS.
- `EXECUTIONS_TIMEOUT=300` / `EXECUTIONS_TIMEOUT_MAX=600` present (`:186-187`), preflight PASS.
- CI: `.github/workflows/ci.yml:108,112` runs `cost_readiness.py` and `gemini_readiness.py`; integration uses service container `localhost:5432` (`:87`). **Verified.**

### 6.2 Preflight fix is genuine, not a weakened guard
Inspected `scripts/preflight/cost_readiness.py` and `gemini_readiness.py`:
- Neutralized guards PASS only when the node is ABSENT and FAIL (named) if it reappears misconfigured: `_check_agent_iterations` (AI Agent + `options.maxIterations`), `_check_model_pinned`, `_check_agent_retry` — same c-55 pattern as `_check_mark_read_resolved_in_trigger`.
- Body contract `_check_enriched_body` requires `origen_message_id` + `origen_evento` and forbids `clasificacion`, `sector_predicho`, `confianza`.
- Independent inspection of `n8n/workflow.json` (29 nodes): AI Agent absent, Gemini model absent, body has both required keys, none of the forbidden keys.
- Negative tests exist and pass: `test_agent_present_without_max_iterations_fails_named`, `test_body_forbids_clasificacion`/`sector_predicho`/`confianza`, `test_modelo_implicito_falla_nombrado`, `test_reintento_sin_cotas_falla_nombrado`, etc. This is a genuine c-72 alignment, NOT a weakened guard. **Verified.**

### 6.3 Scope containment
`git status --porcelain` contains only: `.env.example`, `AGENTS.md`, `README.md`, `docker-compose.yml`, `docs/operational-guide.md`, `nginx/nginx.conf`, `scripts/corpus_ingest/test_corpus_compose_isolation.py`, `scripts/preflight/{cost_readiness.py,gemini_readiness.py,test_cost_readiness.py,test_gemini_readiness.py}`, `scripts/up.{sh,ps1}`, plus untracked `App/Backend/tests/test_c62_infra_hardening.py`, `docker-compose.dev.yml`, and the change folder. **No `App/Backend/app/**`, no `n8n/workflow.json`, no frontend changes, no other change touched.** **Verified.**

### 6.4 Documented commands still valid (loopback)
`TEST_PG_URL`/`localhost:5433` (`conftest.py:85`) and `localhost:5678` (`dry_run.py:825`, `up.sh:389`) remain valid because both ports are loopback-published and confirmed listening. **Verified by config + live listeners.**

### 6.5 Rollback viability
Config-only change. Reverting the listed compose/nginx/script/doc commits and running `docker compose up -d` restores the prior state; named volumes persist; no data migration, no application code. **Reversible — verified by inspection.**

---

## 7. Issues Found

**CRITICAL** (must fix before archive):
- None.

**WARNING** (should fix):
- None.

**SUGGESTION** (nice to have):
- `design.md` D3 network table does not mention the added `host_access` support network. Update the design artifact for audit coherence (implementation is spec-compliant).
- Three scenarios are verified structurally/at config level but not end-to-end (INFRA-001 backend->n8n internal delivery, INFRA-002 integration suite against loopback, INFRA-009 dry-run harness). An optional smoke run would upgrade them from PARTIAL to PROVEN. None block archive.

---

## 8. Verdict

**PASS**

All 33 tasks complete; `openspec validate --strict` passes; offline suite 1090 passed; new c-62 structural suite 31 passed; preflight 10/10 + 2/2 GREEN with genuine (non-weakened) c-72 realignment; live stack starts healthy without Redis, serves health 200, exposes no version, honors 429/444/301, and publishes postgres/n8n only on loopback; network invariants (n8n never shares a network with postgres) hold in both base and corpus renderings; scope is contained and rollback is config-only. **CRITICAL count: 0.** Three scenarios remain PARTIAL (not executed end-to-end) and are recorded as SUGGESTIONS, not blockers.
