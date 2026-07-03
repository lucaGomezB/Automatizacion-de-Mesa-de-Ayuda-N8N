# C-23: Dashboard de Analitica — Technical Design

## Context

The current system has full CRUD for incidents, automatic classification via a hybrid pipeline (deterministic + Gemini), and a human review queue. However, there is no aggregated visibility into trends. Operators cannot answer questions like "how many Soporte Tecnico incidents this month?" or "what category grew the most this quarter?"

C-23 adds a statistics dashboard (backend aggregation endpoints + frontend ReCharts visualization), locks write operations on closed incidents (409 Conflict), and cancels C-21's planned auto-deletion in favor of indefinite retention.

All prior changes (C-01 through C-10, C-14 through C-17) are archived. C-15 (JWT Auth) is a hard dependency — the dashboard requires authentication.

## Goals / Non-Goals

**Goals:**
- Add `GET /api/v1/estadisticas/tendencias` endpoint with time-based aggregation (daily/monthly) and filterable by sector and date range
- Add `GET /api/v1/estadisticas/resumen` endpoint with summary KPIs (totals, daily average, top sectors, human review rate)
- Block PATCH operations on incidents in terminal state (`es_terminal=true`) with 409 Conflict
- Build a `/dashboard` frontend page with ReCharts (line/bar for trends, pie/donut for sector distribution, stacked bar for estados) and date range filters
- Add chart export to PNG via html2canvas
- Make closed incidents read-only in the UI (hide edit/delete actions in TicketsTable and TicketDetailDialog)
- Add "Dashboard" navigation link in Header, visible only to authenticated users

**Non-Goals:**
- No database schema changes (indefinite retention is already the default behavior, C-21 is cancelled)
- No new N8N workflow modifications
- No changes to the classification pipeline
- No real-time WebSocket streaming (polling via React Query refetch is sufficient for v1)
- No user-customizable dashboard layouts (fixed layout for initial release)

## Decisions

### Decision 1: Aggregation via SQL GROUP BY queries (not in-memory processing)

**What**: Trend and summary data is computed via SQL aggregate queries using `func.date_trunc` and `GROUP BY`, executed directly against the `incidente` table.

**Why**: The incident volume in this system is bounded (a few thousand per month at most per the thesis scope). SQL aggregation with indexed timestamp columns (`ix_incidente_created_sector`) is fast enough without materialized views or caching. In-memory aggregation would load all rows into the service layer and nullify the benefit of database indexes.

**Alternatives considered**:
- Materialized views: Overkill for the expected data volume. Adds PostgreSQL-specific complexity not testable with SQLite in-memory.
- Redis-cached results: Adds infrastructure dependency not justified for this scale. Can be added later if performance requires it.
- ORM-level aggregation in Python: Fetches too many rows, wasting memory and network for a task the database does faster.

### Decision 2: Single estadisticas_service.py with raw SQL (not repository pattern for aggregates)

**What**: `EstadisticasService` executes `func.date_trunc` and `func.count` via SQLAlchemy core-like expressions directly, rather than delegating to a repository class.

**Why**: The repository pattern (CRUD per entity) maps cleanly to single-entity operations. Aggregate queries span multiple tables and produce result shapes that do not map to a single ORM entity. Forcing this through a repository would create a leaky abstraction (a repository that returns dicts instead of ORM instances). The service layer owning read-only aggregate queries is a well-established pattern for reporting endpoints.

**Alternatives considered**:
- `EstadisticasRepository`: Would return non-ORM results, breaking the repository contract. Unclear what entity it "owns."
- SQL views in the database: Schema change avoided by the proposal. Can be added later as an optimization.

### Decision 3: ReCharts as the charting library

**What**: Use ReCharts (^2.12.0) for all chart components on the dashboard.

**Why**: ReCharts is the most popular React charting library built on top of D3 and SVG. It provides composable components (`<LineChart>`, `<BarChart>`, `<PieChart>`) that align with the React declarative model. It has excellent TypeScript support, responsive containers out of the box, and tooltip/render customization. The alternative (Nivo, Victory, Chart.js) either have heavier bundles or less React-idiomatic APIs.

**Alternatives considered**:
- **Nivo**: Powerful but heavier bundle (~200KB gzipped vs ReCharts ~120KB). More complex API for simple charts.
- **Chart.js with react-chartjs-2**: Canvas-based (harder to export as PNG with custom styling), imperative API.
- **Apache ECharts**: Very powerful but not React-native; requires a wrapper that adds complexity.

### Decision 4: html2canvas for PNG export (not recharts-to-png or chart-specific solutions)

**What**: Use html2canvas (^1.4.1) to capture chart DOM elements and download them as PNG.

**Why**: html2canvas captures any DOM node including the chart container with its legends, titles, and tooltips. It works regardless of the chart type (line, bar, pie) with a single implementation. Chart-specific solutions like recharts-to-png require per-chart-type configuration and are less maintained.

**Alternatives considered**:
- recharts-to-png: Unmaintained (last commit 2022), does not support all ReCharts components.
- Chart.js built-in `toBase64Image()`: Not applicable since we chose ReCharts.

### Decision 5: 409 Conflict for closed incident writes (not 403 Forbidden or 422 Unprocessable)

**What**: PATCH on an incident in terminal state (`estado.es_terminal=true`) returns HTTP 409 Conflict with code `INCIDENTE_CERRADO`.

**Why**: 409 is semantically correct: the resource is in a state that conflicts with the requested operation. 403 implies authorization, which is misleading (the user is authenticated, the operation is just not allowed on this resource state). 422 implies validation failure, which is also misleading (the payload is valid, the state prevents it).

**Alternatives considered**:
- 403 Forbidden: Wrong semantics. The user has permission; the resource state prohibits the operation.
- 422 Unprocessable: Payload is well-formed; the issue is resource state, not input validation.
- 405 Method Not Allowed: The method IS allowed (PATCH works for non-closed incidents); just not for this particular resource.

### Decision 6: Date range as required query params on /tendencias, optional on /resumen

**What**: `GET /api/v1/estadisticas/tendencias` requires `desde` and `hasta` (ISO 8601 date strings). `GET /api/v1/estadisticas/resumen` makes them optional (defaults to last 30 days if omitted).

**Why**: Trend data is meaningless without a bounded range (line charts with unbounded ranges would be confusing). Summary KPIs can reasonably default to a recent window and allow optional extension.

**Alternatives considered**:
- Both endpoints always require date range: More consistent but less ergonomic for the summary widget.
- Neither requires date range: Trend endpoint would return potentially thousands of data points, degrading performance.

### Decision 7: Frontend component structure follows existing page pattern

**What**: The dashboard page lives at `pages/Dashboard/` with index.tsx as the entry point and sub-components (`TendenciaChart.tsx`, `SectorPieChart.tsx`, `EstadoBarChart.tsx`, `FiltrosDashboard.tsx`) in the same directory. It uses `PageWrapper` for consistent layout, `useQuery` for data fetching, and shadcn/ui primitives.

**Why**: This mirrors the existing `pages/Administracion/` pattern exactly. Consistency reduces cognitive load for future contributors.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SQLite (test) vs PostgreSQL (prod) GROUP BY date_trunc behavior differences | Tests use SQLite in-memory; acceptance criteria validated against known seed data. PostgreSQL `date_trunc('month', ...)` has direct SQLite equivalent via `strftime`. If gaps emerge, add a test-only compatibility layer in the service. |
| ReCharts bundle size impact on frontend load time | ReCharts v2 is tree-shakeable. Only import `<LineChart>`, `<BarChart>`, `<PieChart>` and their required sub-components. Verify bundle size with `npm run build` before merging. |
| html2canvas fails on complex SVG charts with custom CSS | Wrap the export in a try/catch. If capture fails, show a toast error "No se pudo exportar el grafico. Intente de nuevo." Fallback: user can screenshot manually. |
| Dashboard query performance under high incident volume | The `ix_incidente_created_sector` composite index already exists on `(created_at, sector_id)`. The `agrupar_por=dia` query with a 90-day range returns at most 90 rows. Even with 100k incidents, PostgreSQL aggregates this in milliseconds. |
| 409 Conflict may surprise existing API consumers (N8N, scripts) | The blocqueo is documented in the OpenAPI spec and the proposal. Existing consumers that PATCH closed incidents will need to handle 409. The error code `INCIDENTE_CERRADO` is machine-readable. |

## Open Questions

None. All design decisions made above. The proposal resolves ambiguities about what endpoints return, what the frontend should display, and what the read-only lock looks like.
