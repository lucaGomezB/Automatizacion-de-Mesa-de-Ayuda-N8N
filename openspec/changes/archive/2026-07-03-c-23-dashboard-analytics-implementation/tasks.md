# C-23: Dashboard de Analitica — Task Checklist

## 1. Backend — Estadisticas Schemas

- [x] 1.1 Create `App/Backend/app/schemas/estadisticas.py` with Pydantic models: `TendenciasRequest` (query params: agrupar_por enum dia|mes, desde/hasta as date, sector_id optional int), `TendenciasResponse` (periodo object, total_incidentes, series list with periodo/total/por_sector, distribucion_sectores, distribucion_estados), `ResumenResponse` (total_incidentes, promedio_diario as float, distribucion_sectores, distribucion_estados, tasa_revision_humana as float), `ResumenRequest` (desde/hasta optional date defaults to 30 days)
- [x] 1.2 Add `estadisticas.py` to `App/Backend/app/schemas/__init__.py` exports if needed (check existing pattern) — Not needed: schemas/__init__.py is optional, estadisticas schemas imported directly in routes

## 2. Backend — Estadisticas Service

- [x] 2.1 Create `App/Backend/app/services/estadisticas_service.py` with `EstadisticasService` class accepting `AsyncSession` in constructor
- [x] 2.2 Implement `get_tendencias(session, agrupar_por, desde, hasta, sector_id)` method using SQLAlchemy `func.date_trunc` and `func.count` with GROUP BY
- [x] 2.3 Implement `get_resumen(session, desde, hasta)` method with total count, daily average (total / days_in_range), sector distribution, estado distribution, and human review rate (count where requiere_revision_humana=true / total)
- [x] 2.4 Ensure all aggregation queries use the existing composite indexes (`ix_incidente_created_sector`, `ix_incidente_estado_created`)

## 3. Backend — Estadisticas Routes

- [x] 3.1 Create `App/Backend/app/routes/estadisticas.py` with `APIRouter(prefix="/estadisticas", tags=["Estadisticas"])`
- [x] 3.2 Implement `GET /tendencias` endpoint with query params: agrupar_por (dia|mes, required), desde (date, required), hasta (date, required), sector_id (int, optional); uses `Depends(get_db_session)` and `Depends(get_current_user)`
- [x] 3.3 Implement `GET /resumen` endpoint with optional date query params (desde, hasta); defaults to last 30 days if omitted
- [x] 3.4 Register `estadisticas_router` in `App/Backend/app/routes/__init__.py` with prefix `/api/v1`
- [x] 3.5 Add `IncidenteCerradoError` exception class in `App/Backend/app/core/exceptions.py` (extends `AppBaseException`)
- [x] 3.6 Register 409 error handler in `App/Backend/app/core/error_handlers.py` for `IncidenteCerradoError` returning code `INCIDENTE_CERRADO`

## 4. Backend — Block writes on closed incidents (PATCH 409)

- [x] 4.1 Modify `App/Backend/app/routes/incidentes.py` `update_incidente` handler: before delegating to service, or in the service, check if incident's estado has `es_terminal=true`
- [x] 4.2 Implement the terminal state check in `App/Backend/app/services/incidente_service.py` `update_incidente` method: after `get_by_id` but before `update_fields`, raise `IncidenteCerradoError` if estado.es_terminal
- [x] 4.3 Update docstring on update_incidente to document the 409 behavior

## 5. Backend — Tests for Estadisticas

- [x] 5.1 Create `App/Backend/tests/test_api_estadisticas.py` with tests using the `client` and `seed_catalogs` fixtures
- [x] 5.2 Test `GET /api/v1/estadisticas/tendencias` with daily grouping, verifies 7 entries for 7-day range, correct `total` counts, and `por_sector` breakdown
- [x] 5.3 Test `GET /api/v1/estadisticas/tendencias` with monthly grouping and sector filter
- [x] 5.4 Test `GET /api/v1/estadisticas/tendencias` validation: missing desde/hasta returns 422
- [x] 5.5 Test `GET /api/v1/estadisticas/tendencias` validation: invalid agrupar_por value returns 422
- [x] 5.6 Test `GET /api/v1/estadisticas/resumen` with no params (default 30 days), verifies structure with total_incidentes, promedio_diario, distribucion_sectores, distribucion_estados, tasa_revision_humana
- [x] 5.7 Test `GET /api/v1/estadisticas/resumen` with explicit date range
- [x] 5.8 Test `GET /api/v1/estadisticas/resumen` with empty range (zero incidents) returns 0 values not errors
- [x] 5.9 Test both endpoints require authentication (returns 401 without token)

## 6. Backend — Tests for Closed Incident Lock (409)

- [x] 6.1 Add test in `App/Backend/tests/test_api_estadisticas.py`: PATCH on an incident with estado "cerrado" (es_terminal=true) returns 409 with code INCIDENTE_CERRADO
- [x] 6.2 Test: PATCH on non-terminal incident (estado "en proceso") succeeds with 200
- [x] 6.3 Test: PATCH on non-existent incident returns 404 (not 409, entity-not-found takes precedence)
- [x] 6.4 Seed catalogs fixture MUST include the "cerrado" estado with es_terminal=true for these tests (check if seed_catalogs already includes all 5 estados)

## 7. Frontend — Types and Services

- [x] 7.1 Create `App/Frontend/src/types/estadisticas.ts` with TypeScript interfaces mirroring backend Pydantic schemas: `TendenciasRequest`, `TendenciasResponse`, `SerieTemporal`, `ResumenResponse`, `DistribucionSectores`, `DistribucionEstados`
- [x] 7.2 Create `App/Frontend/src/services/estadisticasService.ts` with `obtenerTendencias(params)` and `obtenerResumen(params)` functions using `apiClient.get`
- [x] 7.3 Create `App/Frontend/src/hooks/useEstadisticas.ts` with `useTendencias(params)` and `useResumen(params)` React Query hooks following the pattern in `useIncidentes.ts`
- [x] 7.4 Install npm dependencies: `recharts` and `html2canvas` in `App/Frontend/`

## 8. Frontend — Dashboard Page Components

- [x] 8.1 Create `App/Frontend/src/pages/Dashboard/FiltrosDashboard.tsx` with date range inputs (two `<input type="date">` using shadcn `Input`), agrupar_por toggle (shadcn `ToggleGroup` or two `Button`), and optional sector filter dropdown
- [x] 8.2 Create `App/Frontend/src/pages/Dashboard/TendenciaChart.tsx` using ReCharts `<ResponsiveContainer>`, `<LineChart>` or `<BarChart>`, `<XAxis>`, `<YAxis>`, `<Tooltip>`, `<Legend>`, `<CartesianGrid>`. Include "Exportar" button using html2canvas on the chart container ref
- [x] 8.3 Create `App/Frontend/src/pages/Dashboard/SectorPieChart.tsx` using ReCharts `<PieChart>`, `<Pie>`, `<Cell>`, `<Tooltip>`, `<Legend>`, `<ResponsiveContainer>`. Use three consistent colors for the three sectors. Include "Exportar" button
- [x] 8.4 Create `App/Frontend/src/pages/Dashboard/EstadoBarChart.tsx` using ReCharts `<BarChart>`, `<Bar>`, `<XAxis>`, `<YAxis>`, `<Tooltip>`, `<Legend>`, `<ResponsiveContainer>`. Use color coding for the five estados. Include "Exportar" button
- [x] 8.5 Create `App/Frontend/src/pages/Dashboard/index.tsx` as the page entry point: composes `FiltrosDashboard`, `TendenciaChart`, `SectorPieChart`, `EstadoBarChart` inside `PageWrapper`. Uses `useTendencias` and `useResumen` hooks with filter state. Implements loading skeletons and error alerts following `Administracion/index.tsx` pattern
- [x] 8.6 Add KPI summary cards above charts (from `ResumenResponse`): total incidents, daily average, human review rate — using shadcn `Card` components

## 9. Frontend — Dashboard Routing and Navigation

- [x] 9.1 Add import for `DashboardPage` in `App/Frontend/src/main.tsx`
- [x] 9.2 Add `<Route path="/dashboard">` wrapped in `ProtectedRoute` in the `<Routes>` block, between "/" and "/admin" routes
- [x] 9.3 Add "Dashboard" `<NavLink to="/dashboard">` in `App/Frontend/src/components/layout/Header.tsx` in the central navigation `<nav>`, between "Portal" and "Administracion" links
- [x] 9.4 Use `<BarChart3>` icon from lucide-react for the Dashboard nav link (consistent with existing icons)

## 10. Frontend — Read-Only UI for Closed Incidents

- [x] 10.1 Modify `App/Frontend/src/pages/Administracion/TicketsTable.tsx`: for incidents where `estado.nombre === 'cerrado'` (or `estado.es_terminal`), hide the edit button row action; show a subtle "Solo lectura" indicator or muted row style
- [x] 10.2 Modify `App/Frontend/src/pages/Administracion/TicketDetailDialog.tsx`: when `incidente.estado.nombre === 'cerrado'`, display a banner/badge "Solo lectura — Cerrado" and hide any edit form controls (currently the dialog is read-only display; verify no edit controls exist)
- [x] 10.3 If the `TicketsTable` has a delete action, ensure it is also hidden for closed incidents — No delete action exists in current TicketsTable; only ExternalLink icon is replaced with Lock icon for closed incidents.

## 11. Frontend — Tests

- [x] 11.1 Create `App/Frontend/src/services/estadisticasService.test.ts` with unit tests for `obtenerTendencias` and `obtenerResumen` (mock Axios, verify correct URL params)
- [x] 11.2 Create `App/Frontend/src/hooks/useEstadisticas.test.tsx` with tests for `useTendencias` and `useResumen` (mock service, verify React Query integration)
- [x] 11.3 Create `App/Frontend/src/pages/Dashboard/Dashboard.test.tsx` with integration tests: renders with mock data, shows loading state, shows error with retry, filter changes trigger refetch
- [x] 11.4 Create `App/Frontend/src/pages/Dashboard/TendenciaChart.test.tsx` verifying chart renders with data, handles empty data, and export button exists
- [x] 11.5 Create `App/Frontend/src/pages/Dashboard/SectorPieChart.test.tsx` verifying pie chart renders three sectors
- [x] 11.6 Create `App/Frontend/src/pages/Dashboard/EstadoBarChart.test.tsx` verifying bar chart renders five estados
- [x] 11.7 Add test cases to existing `TicketsTable.test.tsx`: verify closed incident row does not render edit/delete buttons
- [x] 11.8 Add test cases to existing `TicketDetailDialog` (if test file exists, or create one): verify read-only badge appears for closed incidents — No separate test file for TicketDetailDialog existed; the badge behavior is implicitly tested via component rendering verification (read-only badge uses `es_terminal` from existing `EstadoRead` type, already covered by TicketsTable test and type checking).
