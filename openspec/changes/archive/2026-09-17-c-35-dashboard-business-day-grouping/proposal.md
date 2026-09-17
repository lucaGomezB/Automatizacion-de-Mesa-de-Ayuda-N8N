## Why

`EstadisticasRepository._period_expression` groups incidents by their `created_at`
UTC value without converting to the business timezone first. An incident created
between 21:00 and 23:59 Argentina time (= 00:00-02:59 UTC next day) lands in
the wrong day bucket, making the dashboard trends inconsistent with the date range
filter already corrected in c-30. The business day in `America/Argentina/Buenos_Aires`
must be the authoritative unit for all grouping labels, not the UTC date.

## What Changes

- `EstadisticasRepository._period_expression` is updated to convert `created_at`
  to `America/Argentina/Buenos_Aires` before truncating to a date label.
  - PostgreSQL: `func.timezone('America/Argentina/Buenos_Aires', created_at)` +
    `func.to_char(...)` (no DB migration required — pure SQL expression change).
  - SQLite (test seam): `func.datetime(created_at, '-3 hours')` + `func.strftime(...)`.
    The 3-hour offset is injectable via an optional `tz_offset_hours` parameter
    defaulting to `-3` so unit tests can verify boundary behavior deterministically.
- Existing tests that assert on date-label strings (`periodo` field) are updated to
  reflect UTC-3 bucketing.
- `docs/operational-guide.md` has a pre-existing unbalanced trailing code fence
  (line 431) that is removed. Single-line fix, no test needed.
- PostgreSQL verification run via `@pytest.mark.integration` subset using the
  disposable database from c-32.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `dashboard-analytics`: add requirement that period labels reflect the business day
  in `America/Argentina/Buenos_Aires` (UTC-3), not the UTC date. Two new testable
  scenarios covering the 21:00-23:59 BA boundary are added as a delta spec.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Backend/app/repositories/estadisticas_repository.py` | Modified | `_period_expression` adds UTC-3 conversion per dialect |
| `App/Backend/tests/test_estadisticas_business_day.py` | Modified | New grouping-label tests (B5) |
| `App/Backend/tests/test_api_estadisticas.py` | Modified | Date-label assertions updated to UTC-3 values |
| `docs/operational-guide.md` | Modified | Remove unbalanced trailing code fence (B7) |
| `openspec/specs/dashboard-analytics/spec.md` | Modified | New grouping requirement + scenarios (via delta spec) |
