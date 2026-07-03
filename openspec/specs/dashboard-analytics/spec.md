# dashboard-analytics Specification

## Purpose
TBD - created by archiving change c-23-dashboard-analytics-implementation. Update Purpose after archive.
## Requirements
### Requirement: Time-based trend aggregation endpoint
The system SHALL provide `GET /api/v1/estadisticas/tendencias` that returns incident counts grouped by time period (day or month), filtered by optional date range and sector.

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

### Requirement: Summary statistics endpoint
The system SHALL provide `GET /api/v1/estadisticas/resumen` that returns aggregate KPIs including total incidents, daily average, sector distribution, estado distribution, and human review rate for a configurable date range.

#### Scenario: Summary for default 30-day window
- **WHEN** a GET request is sent to `/api/v1/estadisticas/resumen` without date parameters
- **THEN** the response SHALL contain `total_incidentes`, `promedio_diario`, `distribucion_sectores`, `distribucion_estados`, and `tasa_revision_humana` for the last 30 days

#### Scenario: Summary with explicit date range
- **WHEN** a GET request is sent to `/api/v1/estadisticas/resumen?desde=2026-01-01&hasta=2026-12-31`
- **THEN** the response SHALL report metrics for the full year 2026

#### Scenario: Summary for empty date range
- **WHEN** a GET request is sent to `/api/v1/estadisticas/resumen?desde=2026-07-01&hasta=2026-07-01` and no incidents exist in that range
- **THEN** the response SHALL return `total_incidentes: 0`, `promedio_diario: 0.0`, and empty distribution objects

### Requirement: Authentication required for statistics endpoints
The system SHALL require a valid JWT Bearer token for both `/api/v1/estadisticas/tendencias` and `/api/v1/estadisticas/resumen`.

#### Scenario: Unauthenticated request
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias` without an Authorization header
- **THEN** the system SHALL return HTTP 401 Unauthorized

#### Scenario: Authenticated request
- **WHEN** a GET request is sent to `/api/v1/estadisticas/tendencias` with a valid JWT token
- **THEN** the system SHALL process the request normally and return data

### Requirement: Block write operations on closed incidents
The system SHALL reject PATCH requests to incidents whose estado has `es_terminal=true` with HTTP 409 Conflict.

#### Scenario: Attempt to update a closed incident
- **WHEN** a PATCH request is sent to `/api/v1/incidentes/{id}` where the incident's estado is "cerrado" (es_terminal=true)
- **THEN** the system SHALL return HTTP 409 with error code `INCIDENTE_CERRADO` and message "Los incidentes cerrados son de solo lectura"

#### Scenario: Update a non-terminal incident succeeds
- **WHEN** a PATCH request is sent to `/api/v1/incidentes/{id}` where the incident's estado has es_terminal=false
- **THEN** the system SHALL process the update normally and return HTTP 200

#### Scenario: Update a non-existent incident
- **WHEN** a PATCH request is sent to `/api/v1/incidentes/99999` with a non-existent ID
- **THEN** the system SHALL return HTTP 404 (entity not found check happens before terminal state check)

### Requirement: Dashboard page with trend chart
The frontend SHALL render a line or bar chart (`TendenciaChart`) that displays incident counts over time, grouped by day or month, with a toggle to switch granularity.

#### Scenario: Day-mode chart renders with daily data points
- **WHEN** the user selects "Dia" toggle and the date range covers 7 days
- **THEN** the chart SHALL display 7 data points on the X axis with incident counts on the Y axis

#### Scenario: Month-mode chart renders with monthly data points
- **WHEN** the user selects "Mes" toggle and the date range covers 6 months
- **THEN** the chart SHALL display 6 data points on the X axis representing each month

#### Scenario: Chart loading state
- **WHEN** the dashboard data is being fetched from the API
- **THEN** the `TendenciaChart` SHALL display a skeleton or loading spinner

#### Scenario: Chart error state
- **WHEN** the API returns an error for the trend data
- **THEN** the `TendenciaChart` SHALL display an error message with a retry button

### Requirement: Dashboard page with sector distribution chart
The frontend SHALL render a pie or donut chart (`SectorPieChart`) that shows the distribution of incidents across the three sectors: Sistemas, Operaciones, and Soporte Tecnico.

#### Scenario: Pie chart renders with three sectors
- **WHEN** the summary data is loaded and contains non-zero counts for all three sectors
- **THEN** the `SectorPieChart` SHALL display three slices with proper proportions and sector labels

#### Scenario: Pie chart with zero-value sector
- **WHEN** one sector has zero incidents in the selected range
- **THEN** the `SectorPieChart` SHALL still display the sector with a zero-value slice or omit it gracefully

### Requirement: Dashboard page with estado distribution chart
The frontend SHALL render a bar chart (`EstadoBarChart`) that shows incident counts grouped by estado (nuevo, en proceso, en espera, resuelto, cerrado).

#### Scenario: Bar chart renders with all five estados
- **WHEN** the summary data is loaded
- **THEN** the `EstadoBarChart` SHALL display five bars, one per estado, with heights proportional to incident counts

### Requirement: Dashboard date range filter
The frontend SHALL provide date range filter controls (`FiltrosDashboard`) with two date inputs (desde/hasta) and an agrupar_por toggle (dia/mes).

#### Scenario: Changing the date range refreshes all charts
- **WHEN** the user modifies the "desde" date input and clicks "Aplicar" or presses Enter
- **THEN** all three charts (TendenciaChart, SectorPieChart, EstadoBarChart) SHALL refetch data with the new date range

#### Scenario: Toggle from daily to monthly aggregation
- **WHEN** the user switches the agrupar_por toggle from "Dia" to "Mes"
- **THEN** the TendenciaChart SHALL refetch with agrupar_por=mes

### Requirement: Chart export to PNG
The frontend SHALL allow users to export individual charts as PNG images via html2canvas.

#### Scenario: Export trend chart as PNG
- **WHEN** the user clicks the "Exportar" button on the TendenciaChart
- **THEN** the browser SHALL trigger a download of a PNG file containing the chart image

#### Scenario: Export fails gracefully
- **WHEN** html2canvas fails to capture the chart DOM node
- **THEN** the system SHALL display an error toast: "No se pudo exportar el grafico. Intente de nuevo."

### Requirement: Read-only UI for closed incidents
The frontend SHALL disable edit and delete actions for incidents whose estado is "cerrado" (terminal) in both TicketsTable and TicketDetailDialog.

#### Scenario: Closed incident in TicketsTable has no action buttons
- **WHEN** the TicketsTable renders a row for an incident with estado "cerrado" (es_terminal=true)
- **THEN** the row SHALL NOT display edit or delete action buttons, and SHALL show a read-only indicator

#### Scenario: Closed incident in TicketDetailDialog shows read-only badge
- **WHEN** the TicketDetailDialog renders an incident with estado "cerrado"
- **THEN** the dialog SHALL display a "Solo lectura — Cerrado" badge and SHALL hide edit form controls

#### Scenario: Non-closed incident retains full edit capability
- **WHEN** an incident has estado "en proceso" or any non-terminal state
- **THEN** the TicketsTable and TicketDetailDialog SHALL display normal edit and delete actions

### Requirement: Dashboard navigation link
The Header component SHALL include a "Dashboard" navigation link visible to authenticated users, routing to `/dashboard`.

#### Scenario: Authenticated user sees Dashboard link
- **WHEN** a user is logged in
- **THEN** the Header SHALL display "Dashboard" as a NavLink alongside "Portal" and "Administracion"

#### Scenario: Unauthenticated user does not see Dashboard link
- **WHEN** a user is not logged in
- **THEN** the Header SHALL NOT display any navigation links (the login page header is minimal)

### Requirement: Dashboard route is protected
The `/dashboard` route SHALL be wrapped in ProtectedRoute, requiring JWT authentication. Unauthenticated access SHALL redirect to `/login`.

#### Scenario: Unauthenticated user redirected
- **WHEN** an unauthenticated user navigates to `/dashboard`
- **THEN** the browser SHALL redirect to `/login`

#### Scenario: Authenticated user accesses dashboard
- **WHEN** an authenticated user navigates to `/dashboard`
- **THEN** the Dashboard page SHALL render with all chart components

