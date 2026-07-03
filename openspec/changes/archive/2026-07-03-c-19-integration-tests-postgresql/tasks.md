# C-19: Integration Tests with Real PostgreSQL — Tasks

## 1. Test Infrastructure: Marker + Skip Mechanism

- [x] 1.1 Register `integration` marker in `pytest.ini`
- [x] 1.2 Add PostgreSQL health-check via skip in `pg_engine` fixture (pytest.skip if unreachable)
- [x] 1.3 `pytest -m "not integration"` excludes integration tests; `-m integration` runs only them

## 2. PostgreSQL Fixtures (conftest.py)

- [x] 2.1 Add `pg_engine` fixture (session scope) — creates async engine to PostgreSQL, runs `Base.metadata.create_all`, drops at teardown, disposes engine
- [x] 2.2 Add `pg_session` fixture (function scope) — starts transaction, yields session, rolls back after test
- [x] 2.3 Add `pg_client` fixture (function scope) — ASGI client with `get_db_session` overridden to use PostgreSQL engine, auth bypassed, N8N mocked
- [x] 2.4 Add `seed_pg_catalogs` fixture — mirrors seed_catalogs pattern for PostgreSQL

## 3. Integration Tests: Foreign Key Integrity

- [x] 3.1 Test: crear incidente con todas las FKs válidas → incidente persistido (test_create_incidente_valid_fks)
- [x] 3.2 Test: crear incidente con sector_id inválido → IntegrityError (test_create_incidente_invalid_fk)
- [x] 3.3 Test: crear clasificacion_log con FK a sector e incidente → log persistido (test_clasificacion_log_valid_fks)
- [x] 3.4 Extra: clasificacion_log con incidente_id inválido → IntegrityError (test_clasificacion_log_invalid_incidente_fk)

## 4. Integration Tests: Cascade and SET NULL Behavior

- [x] 4.1 Test: eliminar incidente con clasificaciones → cascade delete de clasificacion_log (test_cascade_delete_incidente_removes_logs)
- [x] 4.2 Test: eliminar sector referenciado → incidente.sector_id = NULL (test_set_null_on_sector_delete)

## 5. Integration Tests: Type Constraints and Catalog Uniqueness

- [x] 5.1 Test: validar constraint UNIQUE en sector.nombre (test_unique_constraint_sector_nombre)
- [x] 5.2 Extra: validar UNIQUE en estado.nombre (test_unique_constraint_estado_nombre)
- [x] 5.3 Extra: validar UNIQUE en canal_origen.nombre (test_unique_constraint_canal_nombre)
- [x] 5.4 Test: validar tipo Numeric(5,4) en clasificacion_log.confianza (test_numeric_precision_confianza)
- [x] 5.5 Test: validar created_at con timezone UTC (test_created_at_is_timezone_aware)

## 6. Integration Tests: Indices and Schema Coexistence

- [x] 6.1 Test: verificar índices compuestos ix_incidente_created_sector + ix_incidente_estado_created (test_composite_indices_exist)
- [x] 6.2 Test: verificar que users e incidentes coexisten en mismo schema (test_users_and_incidentes_same_schema)

## 7. Integration Tests: API Operations via PostgreSQL

- [x] 7.1 Test: PATCH actualiza estado de incidente → cambio persistido + GET verifica (test_patch_updates_estado)

## 8. CI Workflow Update

- [x] 8.1 Add PostgreSQL 15.5-alpine service container to `backend-tests` job in `.github/workflows/ci.yml`
- [x] 8.2 Add separate step: `pytest -m integration -v` with `TEST_PG_URL` env var pointing to service container
- [x] 8.3 Add `JWT_SECRET_KEY` dummy env var (required by pydantic-settings) to CI job env
- [x] 8.4 Add `-m "not integration"` to main pytest step to exclude integration tests from SQLite run

## Summary

- **16 integration tests** written (proposal asked for 10-15 minimum)
- **4 new fixtures**: pg_engine, pg_session, pg_client, seed_pg_catalogs
- **3 files modified**: pytest.ini, conftest.py, ci.yml
- **1 new test file**: test_integration_postgresql.py
- **Skip mechanism**: automatically skips when PostgreSQL unavailable
- **Zero regression**: all 208 existing SQLite tests pass unchanged
