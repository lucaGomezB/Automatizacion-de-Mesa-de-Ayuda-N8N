# C-19: Design — Integration Tests with Real PostgreSQL

## Context

The backend test suite (`App/Backend/tests/`) uses SQLite in-memory exclusively. The thesis (Chapter 6, §6.7) claims integration tests run against real PostgreSQL, but they do not. SQLite cannot validate:

- PostgreSQL-specific types (`Numeric(5,4)`, `TIMESTAMPTZ`, arrays)
- Sequence/identity behavior (`autoincrement`)
- PostgreSQL-specific constraint enforcement (FK with `SET NULL` / `CASCADE`)
- PostgreSQL-specific SQL syntax
- Composite index behavior under real query plans

The production database is PostgreSQL 15.5 (via `docker-compose.yml` on port 5433). The CI pipeline runs on GitHub Actions with Ubuntu runners.

Existing test infrastructure:
- `conftest.py` defines `engine` (SQLite, session scope), `db_session` (function scope, rollback), `client` (ASGI), `seed_catalogs`, and `make_client_with_classifier`
- 190+ unit tests, all green, all using SQLite
- `pytest.ini` configures `asyncio_mode = auto` and `testpaths = tests`

## Goals / Non-Goals

**Goals:**
1. Add a `pytest.mark.integration` marker for tests requiring real PostgreSQL
2. Provide PostgreSQL-aware fixtures (`pg_engine`, `pg_session`, `pg_client`) that mirror the existing SQLite fixture pattern
3. Write 10-15 integration tests validating PostgreSQL-specific behaviors (FK integrity, cascade delete, UNIQUE constraints, Numeric precision, timezone, indices, schema coexistence)
4. Integration tests skip automatically when PostgreSQL is unavailable (safe for devs without Docker)
5. CI runs integration tests as an optional step when PostgreSQL service is present

**Non-Goals:**
- Do NOT replace or modify existing SQLite tests
- Do NOT run integration tests by default (opt-in via marker)
- Do NOT add Docker testcontainers dependency (uses already-available docker-compose PostgreSQL)
- Do NOT test Gemini or N8N integration (those remain mocked)

## Decisions

### D1: Connection Strategy — Environment Variable + Health Check

**Decision**: Use environment variable `TEST_PG_URL` with fallback to docker-compose defaults (`postgresql+asyncpg://mesa:mesa@localhost:5433/mesa_de_ayuda`). A session-scoped autouse fixture probes the connection and sets a module-level skip flag.

**Alternatives considered**:
- `testcontainers-python[postgres]`: Adds Docker SDK dependency. Overkill when docker-compose already provides PostgreSQL. Rejected.
- `pytest-postgresql`: Requires pg binaries on the host. Complex on Windows. Rejected.
- Hardcoded connection string: Inflexible for CI vs local. Rejected.

**Rationale**: The docker-compose PostgreSQL is already part of the development workflow. An env var override allows CI to point at a GitHub Actions service container. The health check fixture ensures graceful degradation.

### D2: Fixture Architecture — Mirror Existing SQLite Pattern

**Decision**: Create `pg_engine` (session scope), `pg_session` (function scope with rollback), and `pg_client` (function scope) fixtures that mirror the existing SQLite fixtures in structure. The `pg_client` overrides `get_db_session` to use the PostgreSQL engine.

**Alternatives considered**:
- Reuse existing fixtures with a toggle: Would make `conftest.py` complex and risk breaking existing tests. Rejected.
- Separate conftest file: Adds module discovery complexity. Rejected — use one conftest with `skipif` guards inside the fixtures.

**Rationale**: Same fixture structure = same test writing patterns. Tests that need PostgreSQL just import `pg_client` instead of `client`.

### D3: Test Isolation — Transaction Rollback per Test

**Decision**: Each `pg_session` fixture begins a transaction, yields the session, and rolls back after the test. This mirrors the SQLite `db_session` pattern. Catalog seeding uses the same pattern as `seed_catalogs` but against PostgreSQL.

**Rationale**: Rollback is faster than `CREATE/DROP DATABASE` per test. The PostgreSQL `SAVEPOINT` mechanism supports nested transactions if needed. All 190+ existing tests already use this pattern — no new isolation concept to learn.

### D4: CI Integration — Optional Service Container + Separate Step

**Decision**: Add a PostgreSQL service container to the `backend-tests` job in `.github/workflows/ci.yml`. Integration tests run as a separate step: `pytest -m integration`. If the service is unavailable (or omitted), the skip mechanism prevents failure.

**Rationale**: Integration tests are opt-in. The CI job structure stays clean — the main `pytest` step runs SQLite tests as before (excluding `integration` marker). The integration step is additive.

### D5: Marker Registration — pytest.ini

**Decision**: Add `markers = integration: tests that require a real PostgreSQL database` to `pytest.ini`.

**Rationale**: Without registration, pytest emits warnings. The marker control via `-m integration` / `-m "not integration"` is standard pytest.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Integration tests slow down CI | Run as separate step, only when PostgreSQL service is present. SQLite tests remain fast. |
| PostgreSQL unavailable = tests silently skip | CI ensures PostgreSQL service is present. Local devs see a warning at collection time. |
| Port 5433 collision with other projects | Configurable via `TEST_PG_URL` env var. Default matches docker-compose. |
| Fixture leakage between integration and unit tests | Integration markers act as gate; `-m "not integration"` excludes them from unit test runs. |
| `EncryptedText` TypeDecorator requires Fernet key in env | Integration tests must set `PSEUDONYMIZATION_ENCRYPTION_KEY` env var. CI already sets a dummy key. |

## Open Questions

None — the proposal is concrete and the existing codebase provides clear patterns to follow.
