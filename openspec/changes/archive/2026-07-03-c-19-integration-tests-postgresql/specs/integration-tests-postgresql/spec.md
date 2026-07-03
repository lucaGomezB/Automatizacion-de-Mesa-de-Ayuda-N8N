# C-19: Integration Tests with Real PostgreSQL — Delta Specs

## ADDED Requirements

### Requirement: Integration test marker is registered
The test suite SHALL define a `pytest.mark.integration` marker for tests that require a real PostgreSQL database. Tests without this marker SHALL continue using SQLite in-memory as before.

#### Scenario: Marker registration
- **WHEN** pytest collects tests without the `-m integration` flag
- **THEN** integration-marked tests are excluded from the run
- **AND** all 190+ existing SQLite tests execute normally

#### Scenario: Opt-in execution
- **WHEN** pytest is invoked with `-m integration`
- **THEN** only tests marked with `@pytest.mark.integration` are collected and executed

### Requirement: PostgreSQL fixtures mirror existing SQLite fixture pattern
The test suite SHALL provide `pg_engine`, `pg_session`, and `pg_client` fixtures that connect to a real PostgreSQL database with the same lifecycle semantics as the existing SQLite fixtures.

#### Scenario: pg_engine session scope
- **WHEN** the test session starts and PostgreSQL is reachable
- **THEN** a single async engine is created and all tables are created via `Base.metadata.create_all`
- **AND** the engine is disposed at session end

#### Scenario: pg_session rollback isolation
- **WHEN** a test uses the `pg_session` fixture
- **THEN** the session starts a transaction at setup
- **AND** rolls back the transaction at teardown
- **AND** no test data persists between tests

#### Scenario: pg_client uses PostgreSQL
- **WHEN** a test uses the `pg_client` fixture
- **THEN** the ASGI client's `get_db_session` dependency is overridden to use the PostgreSQL engine
- **AND** authentication is bypassed with the same mock user as the SQLite `client` fixture

### Requirement: PostgreSQL unavailability triggers skip
If PostgreSQL is not reachable at test collection time, all integration tests SHALL be skipped automatically without causing test failures.

#### Scenario: Skip when PostgreSQL unreachable
- **WHEN** the health check fixture cannot connect to the configured PostgreSQL instance
- **THEN** all `pytest.mark.integration` tests are skipped with reason "PostgreSQL unavailable"
- **AND** the overall test suite exit code is 0 (success)

#### Scenario: Configurable connection string
- **WHEN** the `TEST_PG_URL` environment variable is set
- **THEN** the PostgreSQL fixtures use that URL instead of the default docker-compose connection string

### Requirement: Foreign key integrity is validated against PostgreSQL
Integration tests SHALL verify that PostgreSQL enforces foreign key constraints, rejecting inserts with invalid references and cascading deletes as defined in the schema.

#### Scenario: Valid FK insert succeeds
- **WHEN** an incidente is created with valid `estado_id`, `sector_id`, and `canal_origen_id` referencing existing catalog rows
- **THEN** the incidente is persisted successfully with all FKs resolved

#### Scenario: Invalid FK insert raises IntegrityError
- **WHEN** an incidente is created with a `sector_id` that does not exist in the `sector` table
- **THEN** PostgreSQL raises an `IntegrityError` (foreign key violation)

#### Scenario: Cascade delete removes classification logs
- **WHEN** an incidente with associated `ClasificacionLog` rows is deleted
- **THEN** all related `ClasificacionLog` rows are deleted automatically via `ON DELETE CASCADE`

#### Scenario: SET NULL on sector deletion
- **WHEN** a `Sector` referenced by an incidente is deleted
- **THEN** the incidente's `sector_id` is set to NULL via `ON DELETE SET NULL`

### Requirement: PostgreSQL type constraints are validated
Integration tests SHALL verify that PostgreSQL enforces column type constraints, including `Numeric(5,4)` precision and `TIMESTAMPTZ` timezone awareness.

#### Scenario: Numeric(5,4) precision enforced
- **WHEN** a `ClasificacionLog` is inserted with `confianza = 0.12345` (5 decimal digits)
- **THEN** PostgreSQL rounds or rejects the value according to `Numeric(5,4)` precision

#### Scenario: created_at stores timezone-aware timestamps
- **WHEN** an incidente is created
- **THEN** its `created_at` value is stored with UTC timezone information (`TIMESTAMPTZ`)

### Requirement: UNIQUE constraints on catalog tables are enforced
Integration tests SHALL verify that catalog tables (`sector`, `estado`, `canal_origen`) enforce uniqueness on the `nombre` column.

#### Scenario: Duplicate sector name rejected
- **WHEN** an attempt is made to insert a `Sector` with a `nombre` that already exists
- **THEN** PostgreSQL raises an `IntegrityError` (unique constraint violation)

### Requirement: Composite indices exist on incidente table
Integration tests SHALL verify that the composite indices `ix_incidente_created_sector` and `ix_incidente_estado_created` exist in the PostgreSQL schema.

#### Scenario: Composite indices exist in schema
- **WHEN** the schema is inspected after table creation
- **THEN** index `ix_incidente_created_sector` on `(created_at, sector_id)` exists
- **AND** index `ix_incidente_estado_created` on `(estado_id, created_at)` exists

### Requirement: User and incidente tables coexist in same schema
Integration tests SHALL verify that `users` and `incidente` tables coexist in the same PostgreSQL schema without conflicts.

#### Scenario: Tables coexist without conflict
- **WHEN** both `users` and `incidente` tables are queried in the same session
- **THEN** both tables exist and are queryable
- **AND** no name collision or constraint conflict occurs

### Requirement: Incidente state transitions via PATCH are persisted
Integration tests SHALL verify that updating an incidente's estado via PATCH is correctly persisted in PostgreSQL.

#### Scenario: PATCH updates estado
- **WHEN** an incidente with `estado = "nuevo"` receives a PATCH request with `estado_id` pointing to "en proceso"
- **THEN** the incidente's `estado_id` is updated in PostgreSQL
- **AND** a subsequent GET returns the updated estado

### Requirement: CI runs integration tests when PostgreSQL service is present
The GitHub Actions CI workflow SHALL include an optional PostgreSQL service container and a separate step that runs integration-marked tests.

#### Scenario: CI integration test step
- **WHEN** the CI workflow runs on a push to `main` or a pull request
- **THEN** a PostgreSQL 15.5 service container is available
- **AND** the integration tests execute against that container
- **AND** test results are reported in the CI output
