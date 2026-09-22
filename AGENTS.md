# AGENTS.md

Project guidance for OpenCode sessions. Every line answers: "Would an agent likely miss this without help?"

## Project State

This project is **NOT in maintenance mode**. Several OPSX changes are active at any given time (for example `c-28` through `c-33` at the time of writing), and some are complete but NOT yet archived. Never assume a change is archived — always ask the CLI first:

```bash
openspec list --json
```

`status: complete` means the tasks are done, but the change only becomes archived once it is moved under `openspec/changes/archive/`. Treat `openspec list --json` as the single source of truth for what exists; this file can and will go stale.

Primary sources of truth:
- `openspec/config.yaml` — authoritative stack, conventions, thresholds, category strings
- `CHANGES.md` — dependency tree, governance levels, and "Leer antes" pointers per change
- `knowledge-base/` — 11 canonical files covering vision, domain model, architecture, flows
- `CLAUDE.md` — legacy reference (this file supersedes it for agent-specific guidance)

## Quick Start for New Sessions

```bash
# 1. Activate pre-commit hook (blocks secrets in commits — MANDATORY after clone)
git config core.hooksPath .githooks

# 2. Restore shared project memory
engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"

# 3. Confirm state
openspec list --json
```

## Component Map

```
.
├── App/Backend/       # FastAPI backend (Python 3.12)
│   ├── app/
│   │   ├── routes/           # API endpoints → delegates to services
│   │   ├── services/         # Business logic (IncidenteService, ClasificacionService)
│   │   ├── repositories/     # Data access pattern
│   │   ├── models/           # SQLAlchemy ORM (5 tables + catalogs)
│   │   ├── classifiers/      # Deterministic + Gemini + Hybrid (F1 se re-mide con el corpus real)
│   │   ├── schemas/          # Pydantic v2 request/response models
│   │   ├── utils/            # n8n_webhook, pseudonymizer, business_time (UTC-3 day boundaries)
│   │   ├── core/             # Database, error_handlers, logging (structlog)
│   │   └── config/           # pydantic-settings (.env)
│   ├── alembic/              # Migrations (seed catalogs in 001)
│   └── tests/                # SQLite unit suite + PostgreSQL integration subset (disposable DB)
│
├── App/Frontend/                 # React 18 + TypeScript + Vite
│   └── src/
│       ├── components/       # Domain components (exclude ui/ and layout/ from coverage)
│       ├── hooks/            # React Query wrappers
│       ├── services/         # Axios API clients
│       └── test/setup.ts     # Testing Library setup
│
├── .agents/skills/    # Vendored domain skills (see .agents/SKILLS.md)
├── .opencode/skills/  # OPSX workflow skills (explore/propose/apply/archive/sync)
├── n8n/workflow.json  # N8N workflow (import into N8N UI)
├── evaluation/               # Self-contained eval framework (own pytest.ini + requirements.txt)
├── data/                     # Evaluation corpus (NOT tracked in git)
└── docs/                     # Design docs, guides, OpenAPI spec, prompt
```

## Skills (Domain Knowledge)

The project VENDORS its domain skills into the repo, so every collaborator gets them on
clone — no global install and no per-machine setup required. The canonical registry is
`.agents/SKILLS.md`: read it before writing code during an apply.

- `.agents/skills/<name>/SKILL.md` — vendored domain skills (SQLAlchemy/PostgreSQL, pytest,
  TDD, Python design patterns, Tailwind). Origin and version tracked in `skills-lock.json`.
- `.opencode/skills/` — OPSX workflow skills (explore / propose / apply / archive / sync).

Rules:
- During apply, load the FULL `SKILL.md` of every skill that matches the change's tasks
  BEFORE writing code. Skill patterns win over general agent knowledge, but a hard project
  rule (`AGENTS.md`, `openspec/config.yaml`) wins over the skill.
- Known caveat: `tailwind-design-system` targets Tailwind v4 while this project is on
  v3.4.11 — use only its transferable concepts, never its v4 syntax.
- Update or reinstall: `npx skills check`, `npx skills update`,
  `npx skills experimental_install` (restores exactly what `skills-lock.json` declares).

## Exact Developer Commands

All commands run from the repo root unless noted.

### Backend (App/Backend/)

The backend suite has TWO subsets:

- **SQLite unit subset** (unmarked tests): fully offline, no Docker, no external services (Gemini/N8N mocked).
- **PostgreSQL integration subset** (`@pytest.mark.integration`): REQUIRES a reachable PostgreSQL. PostgreSQL is a mandatory prerequisite — the suite fails loudly and never skips. Its fixtures run destructive DDL ONLY against a DISPOSABLE database, never the application database.

```bash
# Run the whole backend suite. Requires a reachable PostgreSQL for the integration subset.
cd App/Backend; pytest

# Run only the fast SQLite subset (no PostgreSQL required, fully offline)
cd App/Backend; pytest -m "not integration"

# Run only the PostgreSQL integration subset (uses the disposable database)
cd App/Backend; pytest -m integration

# Run a single test file
cd App/Backend; pytest tests/test_api_incidentes.py

# Run a single test function
cd App/Backend; pytest tests/test_api_incidentes.py::test_create_incidente

# Run with coverage (routes, services, repositories only)
cd App/Backend; pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing

# Lint (ruff — currently only pycodestyle E rules, no F rules)
cd App/Backend; ruff check .

# Verify OpenAPI spec is synchronized with code
cd App/Backend; pytest tests/test_openapi_sync.py -v

# Regenerate alembic migration after model changes
cd App/Backend; alembic revision --autogenerate -m "description"
```

#### Safe local workflow for the PostgreSQL integration subset

The integration fixtures are destructive, so they run against a DISPOSABLE database (`mesa_de_ayuda_test`), created and dropped automatically by the session fixture. The application database (`mesa_de_ayuda`, the compose one) is NEVER targeted by default.

```bash
# 1. Start the compose PostgreSQL (from the repo root)
docker compose up -d postgres

# 2. Run the integration subset. Without TEST_PG_URL the fixtures provision
#    `mesa_de_ayuda_test` via the `postgres` maintenance connection on the same
#    server and DROP it at session teardown.
cd App/Backend; pytest -m integration

# 3. Point at your own dedicated database when needed (e.g. CI). When
#    TEST_PG_URL is set, that database is used as-is (never created/dropped).
cd App/Backend; TEST_PG_URL=postgresql+asyncpg://user:pw@host:5432/my_test_db pytest -m integration
```

**Safety guard**: before any destructive DDL the fixtures compare the target database NAME against the application database name (derived from `DATABASE_URL`). If they match, the run ABORTS with a non-zero exit code. The only exception is the explicit escape hatch `TEST_PG_ALLOW_APP_DB=1`, reserved for dedicated, ephemeral environments (e.g. a CI service container). Never set it against a database whose data you care about.

### Frontend (App/Frontend/)

```bash
cd App/Frontend; npm run dev           # Dev server on :3000
cd App/Frontend; npm run test          # Vitest (run mode)
cd App/Frontend; npm run test:watch    # Vitest (watch mode)
cd App/Frontend; npm run test:coverage # Vitest with coverage
cd App/Frontend; npm run lint          # ESLint flat config
cd App/Frontend; npm run build         # tsc + vite build (typecheck FIRST)
```

### Evaluation (evaluation/)

```bash
cd evaluation; pytest              # Self-contained suite (FakeClassifier, no Gemini)
```

### Full Stack (Docker)

```bash
# Start everything (PostgreSQL :5433, Redis :6379, backend :8000, N8N :5678)
docker compose up -d

# Verify all healthy
docker compose ps

# The compose name is FIXED to mesa_local — docker compose up always targets the right stack.
# Do NOT use docker compose -p or omit the name.
```

## Env Vars and Secrets

- **`.env` location**: `App/Backend/.env` (NOT root `.env`)
- **Template**: `App/Backend/.env.example`
- **Pre-commit hook**: `.githooks/pre-commit` blocks commits containing API keys, PEM keys, or `.env` files. Use `gitleaks:allow` comment to whitelist false positives.
- **CI dummies**: backend tests in CI need these env vars even though the SQLite subset is offline (pydantic-settings requires them without defaults). The integration subset additionally gets `TEST_PG_URL` pointed at its dedicated service container:

```
DATABASE_URL=postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy
GEMINI_API_KEY=ci-dummy-key
PSEUDONYMIZATION_ENCRYPTION_KEY=MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA= # gitleaks:allow
```

- **SQLite subset runs OFFLINE** — the conftest forces SQLite in-memory and mocks Gemini/N8N; no real service connections are needed. The **PostgreSQL integration subset is NOT offline**: it requires a reachable PostgreSQL and runs destructive DDL against a disposable database only (see the safe local workflow above).
- **`TEST_PG_URL` / `TEST_PG_ALLOW_APP_DB`**: `TEST_PG_URL` selects the integration target; without it the fixtures provision and drop the disposable `mesa_de_ayuda_test`. `TEST_PG_ALLOW_APP_DB=1` is the ONLY way to allow a target whose database name equals the application database (dedicated ephemeral environments only).

## Architecture Rules (Non-Obvious)

- **Layer discipline**: routes → services → repositories → models. NEVER skip a layer in implementation.
- **Async SQLAlchemy**: always use `selectinload()` for relationships being serialized. Lazy-loading will fail in async context.
- **Category strings**: `["Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"]` — EXACT, case-sensitive, WITHOUT accents. `Operaciones` was removed. Any accent or casing deviation breaks classifier comparison.
- **Domain identifiers in Spanish**: model fields, route paths (`/incidentes`), schema keys. Code identifiers (functions, variables) may be English or Spanish — keep consistent per file.
- **Error response body**: standard envelope `{"error": {"code": "...", "message": "...", "details?": "..."}}` via `core/error_handlers.py`.
- **N8N webhook notification**: fire-and-forget via `asyncio.create_task`. Do NOT block HTTP response on webhook completion. The mock in `conftest.py` patches this out globally.
- **Business day is UTC-3**: dashboard date ranges and calendar days are resolved in `America/Argentina/Buenos_Aires` via `app/utils/business_time.py`, then converted to UTC-aware instants (half-open bounds) before querying. Do NOT use `date.today()` (server-local) against `created_at` UTC columns — near midnight it shifts the business day and excludes recent incidents.

## Testing Quirks

- **Backend conftest fixture hierarchy**: `engine` (session scope) → `db_session` (function scope, rollback) → `client` (ASGI client). For classifier-override tests, use `make_client_with_classifier`.
- **seed_catalogs fixture**: creates Estado/Sector/CanalOrigen rows via engine directly (NOT via db_session), because the ASGI client opens its own session per request. Tears down in correct FK order.
- **Frontend coverage exclusions**: `src/components/ui/**` and `src/components/layout/**` are shadcn primitives — excluded from coverage.
- **Frontend test setup**: `globalThis.jest = null` in `src/test/setup.ts` prevents jest-dom from conflicting with vitest's `expect`.
- **evaluation/ has its own pytest.ini** — running `pytest` from repo root will NOT pick it up. Must run from `evaluation/` directory.
- **Flaky tests**: none are known flaky. If something fails in CI but passes locally, check Python/pip version skew (the project pins exact versions in requirements.txt).

## CI Pipeline (.github/workflows/ci.yml)

Triggers: push to `main`, all pull requests. Two parallel jobs:

| Job | What it does |
|-----|-------------|
| `backend-tests` | ruff lint → pytest with coverage → verify OpenAPI sync → evaluation tests |
| `frontend-tests` | ESLint → Vitest with coverage |

The OpenAPI sync check (`test_openapi_sync.py`) regenerates the spec in-memory and compares against `docs/openapi.json`. If you add/change endpoints, regenerate the static file:

```bash
cd App/Backend; python -c "from app.main import app; import json; open('../docs/openapi.json','w').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False))"
```

## Engram Memory

Shared project memory in `.engram/`. Before pushing:

```bash
engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"
git add .engram && git commit -m "chore(engram): sync project memory"
```

Never use `engram sync --all` — it exports ALL projects to this repo.

## What NOT to Do

- Do NOT use emojis under any circumstance — not in code, not in comments, not in commit messages, not in chat responses, not in documentation. They degrade readability and professionalism.
- Do NOT commit `.env` files. The pre-commit hook blocks them.
- Do NOT write production code that lazy-loads SQLAlchemy relationships in async context.
- Do NOT change the five category strings — they are locked by domain spec and the evaluation corpus.
- Do NOT remove or rename `CLAUDE.md` — it contains the Skill routing table used by other tooling.
- Do NOT run `docker compose` without the fixed project name `mesa_local` — duplicate stacks will collide on ports 8000/5678/6379/5433.
- Do NOT run tests from repo root expecting all suites to execute — backend, frontend, and evaluation each require their own working directory.
