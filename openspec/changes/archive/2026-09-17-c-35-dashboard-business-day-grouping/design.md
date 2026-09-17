## Context

`EstadisticasRepository._period_expression` (lines 74-89 of
`App/Backend/app/repositories/estadisticas_repository.py`) currently passes
`Incidente.created_at` directly to `to_char` (PostgreSQL) or `strftime`
(SQLite). Because `created_at` is stored in UTC, incidents created in the
21:00-23:59 Argentina window — which belong to the current business day — are
bucketed into the next UTC day. The date-range filter (fixed in c-30) already
uses `business_range_to_utc` to build correct bounds; the grouping label must
follow the same business-timezone logic.

See `proposal.md` for motivation. See the delta spec in
`specs/dashboard-analytics/spec.md` for the formal requirement.

## Goals / Non-Goals

**Goals:**

- Align the period label produced by `_period_expression` with the
  Argentina business day (UTC-3) for both PostgreSQL and SQLite.
- Keep `period_format` a pure helper function (no DB access) — it stays
  as-is, returning only format strings.
- Provide a testable seam (`tz_offset_hours` parameter on
  `_period_expression`) so the SQLite path can be verified in unit tests
  without a PostgreSQL instance.
- Update existing test assertions that depend on date-label strings.
- Fix the unbalanced trailing code fence in `docs/operational-guide.md` (B7).
- Verify the full repository test against PostgreSQL via
  `@pytest.mark.integration` (B6).

**Non-Goals:**

- No changes to the date-range filter (c-30 already fixed it).
- No frontend changes.
- No database migration (pure SQL expression change; schema is untouched).
- No change to the five category strings or the evaluation corpus.

## Decisions

### D1 — PostgreSQL timezone conversion: `func.timezone()` vs. `AT TIME ZONE` chain

**Decision**: use `func.timezone('America/Argentina/Buenos_Aires', Incidente.created_at)`.

**Rationale**: SQLAlchemy renders `func.timezone(zone, col)` as the standard
`timezone(zone, col)` PostgreSQL function, which is equivalent to
`col AT TIME ZONE zone` for a `timestamptz` column. The single-argument form
is cleaner in Python and produces the same SQL plan. The double-AT-TIME-ZONE
chain (`col AT TIME ZONE 'UTC' AT TIME ZONE zone`) is only needed when the
source column has no timezone information; `created_at` is
`DateTime(timezone=True)` so it carries its zone. Using `func.timezone` also
makes the intent explicit in code and is the canonical SQLAlchemy approach.

**Alternatives considered**:
- `Incidente.created_at.op('AT TIME ZONE')('America/Argentina/Buenos_Aires')`:
  also valid but uses a raw string operator, which is harder to lint and test.
- Casting to a local timestamp in Python before the query: not viable for a
  SQL grouping expression — it must run inside the database.

### D2 — SQLite approximation: fixed offset vs. injectable seam

**Decision**: add an optional `tz_offset_hours: int = -3` parameter to
`_period_expression`. The SQLite branch applies
`func.datetime(Incidente.created_at, f'{tz_offset_hours:+d} hours')`.

**Rationale**: SQLite has no timezone support. Subtracting 3 hours is the
correct approximation for `America/Argentina/Buenos_Aires` (which does not
observe DST, so UTC-3 is constant). Making the offset injectable — rather than
hardcoding it — means unit tests can pass boundary timestamps and verify the
bucketing behavior deterministically without relying on wall-clock time.
The limitation (fixed offset, not a real timezone conversion) is documented
in the docstring.

The `BUSINESS_TZ` constant from `app.utils.business_time` is still the
canonical reference; `_period_expression` does NOT import it directly because
it needs an integer offset for the SQL expression, not a `ZoneInfo` object.
A comment in the code notes the semantic equivalence.

**Alternatives considered**:
- Hardcoding `-3` without injection: simpler but leaves boundary tests
  non-deterministic and harder to read.
- Adding a `timezone_name` parameter and using `pytz`/`dateutil` to derive
  the offset at runtime: overkill for a test seam; SQLite will never run in
  production.

### D3 — Impact on existing test assertions

**Decision**: update every test that asserts on a `periodo` date string to
use UTC-3-correct values.

**Affected files**:
- `App/Backend/tests/test_estadisticas_business_day.py` — add new unit tests
  for the grouping-label fix; existing tests (for default date-range bounds)
  are not affected because they assert on `total_incidentes`, not on `periodo`
  strings.
- `App/Backend/tests/test_api_estadisticas.py` — HTTP-level tests that assert
  on `periodo` values must be reviewed; incidents created in the UTC time range
  of the test will now label by their Argentina date. For tests that create
  incidents with explicit UTC timestamps, the assertions must shift if the
  UTC timestamp crosses a business-day boundary.

The apply agent MUST run the full SQLite unit suite (`pytest -m "not integration"`)
after each TDD step to catch any broken assertion immediately.

### D4 — `period_format` stays as-is

**Decision**: `period_format` is not modified.

**Rationale**: it is a pure function returning format strings only. The TZ
conversion wraps the `created_at` column BEFORE the format function is applied.
The function signature and return values remain identical.

## Risks / Trade-offs

- **SQLite fixed-offset approximation**: if the project ever introduces a
  second timezone or DST-aware testing, the `-3` hardcode will need revisiting.
  Documented in the code as a known limitation.
  Mitigation: the injectable `tz_offset_hours` parameter makes future changes
  localized to one call site.

- **Test regression on `periodo` labels**: any test that asserts on a date
  string AND creates incidents with timestamps in the UTC-midnight window
  (21:00-00:00 BA) will fail after the fix. This is expected and correct —
  the old assertion was wrong.
  Mitigation: TDD cycle's Safety Net step catches pre-existing failures before
  any production code is touched.

- **PostgreSQL `timezone()` function availability**: available since PostgreSQL 8.0;
  no risk for supported versions.

## Migration Plan

1. No database schema changes. No Alembic migration required.
2. Apply the fix to `_period_expression` (GREEN step in TDD).
3. Run `pytest -m "not integration"` — must be green before proceeding.
4. Run `pytest -m integration` against the disposable DB to verify PostgreSQL
   behavior (B6).
5. Remove the trailing code fence in `docs/operational-guide.md` (B7).
6. Rollback: revert the single method change in `estadisticas_repository.py`
   (git revert or manual restore). No data migration needed.
