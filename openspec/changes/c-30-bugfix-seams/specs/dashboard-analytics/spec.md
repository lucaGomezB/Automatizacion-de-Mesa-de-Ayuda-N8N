## MODIFIED Requirements

### Requirement: Time-based trend aggregation endpoint
The system SHALL provide `GET /api/v1/estadisticas/tendencias` that returns incident counts grouped by time period (day or month), filtered by optional date range and sector. The time-period grouping MUST be expressed with SQL portable across the supported engines (PostgreSQL in production and SQLite in the test seam); it MUST NOT depend on SQLite-only functions such as `strftime`.

#### Scenario: Daily aggregation for a 7-day window
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias?agrupar_por=dia&desde=2026-06-01&hasta=2026-06-07`
- **THEN** the response SHALL contain a `series` array with 7 entries, each with `periodo` (YYYY-MM-DD), `total`, and `por_sector` breakdown

#### Scenario: Monthly aggregation with sector filter
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias?agrupar_por=mes&desde=2026-01-01&hasta=2026-06-30&sector_id=1`
- **THEN** the response SHALL contain `series` entries filtered to only sector_id=1, and `total_incidentes` SHALL reflect only that sector

#### Scenario: Missing required date range
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias?agrupar_por=mes` without `desde` or `hasta`
- **THEN** the system SHALL return HTTP 422 with a validation error indicating missing required parameters

#### Scenario: Invalid aggregation parameter
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias?agrupar_por=semana&desde=2026-01-01&hasta=2026-01-31`
- **THEN** the system SHALL return HTTP 422 with a validation error indicating `agrupar_por` must be `dia` or `mes`

#### Scenario: Aggregation runs on PostgreSQL
- **WHEN** the aggregation endpoint runs against PostgreSQL (the production engine)
- **THEN** it returns HTTP 200 with the same `series` shape, and the SQL used for grouping does not reference SQLite-only functions
