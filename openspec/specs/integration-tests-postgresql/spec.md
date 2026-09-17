# integration-tests-postgresql Specification

## Purpose
TBD - created by archiving change c-19-integration-tests-postgresql. Update Purpose after archive.

## Requirements

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

### Requirement: PostgreSQL unavailability fails loudly

Si PostgreSQL no es alcanzable, la suite de tests marcados como `integration` SHALL fallar con un mensaje accionable y exit code distinto de cero, y NO SHALL saltar ningún test. El mensaje SHALL nombrar el destino de conexión (la URL efectiva) y la acción concreta de remediación (levantar el servicio de PostgreSQL del proyecto). Los tests sin el marker `integration` NO SHALL verse afectados por la ausencia de PostgreSQL.

#### Scenario: PostgreSQL ausente falla con mensaje accionable

- **WHEN** se ejecuta la suite de integración y PostgreSQL no es alcanzable en la URL configurada
- **THEN** la ejecución falla con exit code distinto de cero
- **AND** ningún test marcado como `integration` queda skipped
- **AND** el mensaje nombra la URL de conexión efectiva y el comando de remediación

#### Scenario: La ausencia de PostgreSQL no afecta a la suite SQLite

- **WHEN** se ejecuta la suite sin el marker `integration` y PostgreSQL no está disponible
- **THEN** los tests SQLite se ejecutan normalmente
- **AND** la ausencia de PostgreSQL no produce fallos en esa suite

#### Scenario: Configurable connection string

- **WHEN** la variable de entorno `TEST_PG_URL` está definida
- **THEN** los fixtures de PostgreSQL usan esa URL en lugar de la cadena por defecto de docker-compose
- **AND** el mensaje de fallo, si la conexión falla, nombra la URL efectiva provista por la variable

### Requirement: Endpoints de estadísticas operan sobre PostgreSQL

La suite de integración SHALL verificar que `GET /api/v1/estadisticas/tendencias` y `GET /api/v1/estadisticas/resumen` responden HTTP 200 contra PostgreSQL real, con al menos un incidente creado en la base de datos. La verificación SHALL ejercitar tanto la agrupación por día como por mes en tendencias. La suite NO SHALL aceptar un error 500 del servidor como resultado válido.

#### Scenario: Tendencias responde 200 en PostgreSQL

- **WHEN** existe al menos un incidente en PostgreSQL y se consulta `GET /api/v1/estadisticas/tendencias`
- **THEN** la respuesta es HTTP 200
- **AND** el cuerpo expone la estructura de series temporales con los periodos del rango solicitado

#### Scenario: Tendencias agrupa por mes en PostgreSQL

- **WHEN** se consulta `GET /api/v1/estadisticas/tendencias?agrupar_por=mes`
- **THEN** la respuesta es HTTP 200
- **AND** cada periodo de la serie tiene formato de mes

#### Scenario: Resumen responde 200 en PostgreSQL

- **WHEN** existe al menos un incidente en PostgreSQL y se consulta `GET /api/v1/estadisticas/resumen`
- **THEN** la respuesta es HTTP 200
- **AND** el cuerpo expone los KPIs agregados (total de incidentes, promedio diario y distribuciones)

### Requirement: PATCH con FK inexistente devuelve error de cliente en PostgreSQL

La suite de integración SHALL verificar que `PATCH /api/v1/incidentes/{id}` sobre un incidente existente, con un `estado_id` o `sector_id` que NO existe en el catálogo, responde con un código de error de cliente (4xx) y NO con HTTP 500. El incidente NO SHALL quedar modificado con una referencia inválida.

#### Scenario: FK inexistente en PATCH produce 4xx

- **WHEN** se envía un PATCH a un incidente existente indicando un `estado_id` inexistente
- **THEN** la respuesta es un código 4xx con cuerpo de error estructurado
- **AND** la respuesta NO es HTTP 500

#### Scenario: El incidente no queda con referencia inválida

- **WHEN** un PATCH con FK inexistente es rechazado
- **THEN** el incidente conserva su `estado_id` y `sector_id` previos
- **AND** no se persiste ninguna referencia a una fila inexistente del catálogo

### Requirement: La costura SQLite de los tests aplica integridad referencial

La suite de tests del backend que usa SQLite in-memory SHALL habilitar la verificacion de claves foraneas (`PRAGMA foreign_keys=ON`) en cada conexion, de modo que las violaciones de integridad referencial se detecten tambien en el entorno rapido, igual que en PostgreSQL. La suite MUST NOT dar verde ante una violacion de FK que PostgreSQL rechazaria.

#### Scenario: Una FK invalida falla en SQLite

- **WHEN** una prueba persiste una entidad referenciando una clave foranea inexistente bajo SQLite in-memory
- **THEN** la operacion falla con un error de integridad referencial, igual que en PostgreSQL

#### Scenario: Los datos validos siguen persistiendo

- **WHEN** una prueba persiste entidades con claves foraneas existentes
- **THEN** la operacion se completa normalmente y las filas quedan disponibles para la prueba

### Requirement: La suite PostgreSQL corre en verde de forma aislada

Las pruebas de integracion de PostgreSQL SHALL ejecutarse en verde contra una instancia real, con fixtures cuyo ciclo de vida este aislado entre pruebas y con un alcance de event loop coherente entre fixtures y tests. La suite MUST NOT fallar por un problema de infraestructura de test (por ejemplo, un event loop de alcance incorrecto) presentado como si fuera un fallo de producto.

#### Scenario: La suite PG pasa contra PostgreSQL

- **WHEN** se ejecuta la suite marcada como integracion contra una instancia PostgreSQL healthy
- **THEN** todas las pruebas de integracion pasan y ninguna falla por infraestructura de test

#### Scenario: El aislamiento entre pruebas se mantiene

- **WHEN** se ejecutan pruebas de integracion consecutivas
- **THEN** los datos de una prueba no filtran a la siguiente y no se producen errores de event loop

### Requirement: La suite de integración se ejecuta contra una base descartable

Las fixtures PostgreSQL de la suite de integración SHALL operar sobre la base de datos descartable definida por la capability `disposable-test-database`, y NO SHALL aplicar DDL destructivo sobre la base de datos de la aplicación. El fallo ruidoso ante PostgreSQL ausente (sin skip silencioso) SHALL conservarse, la ausencia de PostgreSQL NO SHALL afectar a la suite SQLite, y los tests de integración PostgreSQL existentes SHALL permanecer en verde.

#### Scenario: La suite de integración usa el destino descartable

- **WHEN** se ejecuta la suite marcada como integración
- **THEN** las fixtures provisionan y usan la base descartable como destino
- **AND** no se ejecuta DDL destructivo sobre la base de datos de la aplicación

#### Scenario: PostgreSQL ausente sigue fallando ruidosamente

- **WHEN** se ejecuta la suite de integración y PostgreSQL no es alcanzable
- **THEN** la ejecución falla con exit code distinto de cero y un mensaje que nombra la URL efectiva
- **AND** ningún test marcado como integración queda skipped

#### Scenario: La suite SQLite no se ve afectada

- **WHEN** se ejecuta la suite sin el marker de integración
- **THEN** los tests SQLite se ejecutan normalmente con el enforcement de claves foráneas habilitado
- **AND** la ausencia o presencia de PostgreSQL no altera su resultado

#### Scenario: Los tests de integración existentes siguen pasando

- **WHEN** se ejecuta la suite de integración contra un PostgreSQL saludable
- **THEN** los tests PostgreSQL existentes pasan contra la base descartable
