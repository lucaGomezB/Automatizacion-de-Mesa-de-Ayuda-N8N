# AGENTS.md

Project guidance for OpenCode sessions. Every line answers: "Would an agent likely miss this without help?"

## Project State

All 10 OPSX changes are **complete and archived**. The project is in maintenance mode. Before touching anything, check:

```bash
openspec list --json
```

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
│   │   ├── classifiers/      # Deterministic + Gemini + Hybrid (F1 ~0.88)
│   │   ├── schemas/          # Pydantic v2 request/response models
│   │   ├── utils/            # n8n_webhook, pseudonymizer
│   │   ├── core/             # Database, error_handlers, logging (structlog)
│   │   └── config/           # pydantic-settings (.env)
│   ├── alembic/              # Migrations (seed catalogs in 001)
│   └── tests/                # 190+ tests, SQLite in-memory (NOT PostgreSQL)
│
├── App/Frontend/                 # React 18 + TypeScript + Vite
│   └── src/
│       ├── components/       # Domain components (exclude ui/ and layout/ from coverage)
│       ├── hooks/            # React Query wrappers
│       ├── services/         # Axios API clients
│       └── test/setup.ts     # Testing Library setup
│
├── Automatizacion_Mesa_de_Ayuda.json  # N8N workflow (import into N8N UI)
├── evaluation/               # Self-contained eval framework (own pytest.ini + requirements.txt)
├── data/                     # Evaluation corpus (NOT tracked in git)
└── docs/                     # Design docs, guides, OpenAPI spec, prompt
```

## Exact Developer Commands

All commands run from the repo root unless noted.

### Backend (App/Backend/)

```bash
# Run all backend tests (SQLite in-memory — NO Docker required)
cd App/Backend; pytest

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
- **CI dummies**: backend tests in CI need these env vars even though tests are offline (pydantic-settings requires them without defaults):

```
DATABASE_URL=postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy
GEMINI_API_KEY=ci-dummy-key
PSEUDONYMIZATION_ENCRYPTION_KEY=MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA= # gitleaks:allow
```

- **Backend tests run OFFLINE** — the conftest forces SQLite in-memory and mocks Gemini/N8N. No real service connections needed.

## Architecture Rules (Non-Obvious)

- **Layer discipline**: routes → services → repositories → models. NEVER skip a layer in implementation.
- **Async SQLAlchemy**: always use `selectinload()` for relationships being serialized. Lazy-loading will fail in async context.
- **Category strings**: `["Sistemas", "Operaciones", "Soporte Técnico"]` — EXACT, case-sensitive, with accents. Any deviation breaks classifier comparison.
- **Domain identifiers in Spanish**: model fields, route paths (`/incidentes`), schema keys. Code identifiers (functions, variables) may be English or Spanish — keep consistent per file.
- **Error response body**: standard envelope `{"error": {"code": "...", "message": "...", "details?": "..."}}` via `core/error_handlers.py`.
- **N8N webhook notification**: fire-and-forget via `asyncio.create_task`. Do NOT block HTTP response on webhook completion. The mock in `conftest.py` patches this out globally.

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

- Do NOT commit `.env` files. The pre-commit hook blocks them.
- Do NOT write production code that lazy-loads SQLAlchemy relationships in async context.
- Do NOT change the three category strings — they are locked by domain spec and the evaluation corpus.
- Do NOT remove or rename `CLAUDE.md` — it contains the Skill routing table used by other tooling.
- Do NOT run `docker compose` without the fixed project name `mesa_local` — duplicate stacks will collide on ports 8000/5678/6379/5433.
- Do NOT run tests from repo root expecting all suites to execute — backend, frontend, and evaluation each require their own working directory.
