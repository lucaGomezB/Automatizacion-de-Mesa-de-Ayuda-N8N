## 1. Safety Net

- [x] 1.1 Run `cd App/Backend; pytest -m "not integration"` and record the baseline passing count; verify the run exits 0 before any production code is touched

## 2. RED — Failing tests for B5 grouping scenarios

- [x] 2.1 In `App/Backend/tests/test_estadisticas_business_day.py`, write a test `test_period_label_uses_argentina_date_for_late_night_utc` that creates an incident at 02:30 UTC (= 23:30 BA on the previous day) and asserts that `_period_expression` (via the service or a direct repository call) produces the BA date, not the UTC date; run `pytest tests/test_estadisticas_business_day.py -k test_period_label` and confirm it FAILS (RED)
- [x] 2.2 Write a second test `test_period_label_groups_01utc_under_previous_argentina_date` that creates an incident at 01:00 UTC (= 22:00 BA on day D) and asserts the `periodo` label equals day D; confirm it FAILS (RED)

## 3. GREEN — Fix `_period_expression`

- [x] 3.1 Update `EstadisticasRepository._period_expression` in `App/Backend/app/repositories/estadisticas_repository.py`: add optional `tz_offset_hours: int = -3` parameter; for the PostgreSQL branch wrap `Incidente.created_at` with `func.timezone('America/Argentina/Buenos_Aires', Incidente.created_at)` before passing to `func.to_char`; for the SQLite branch wrap with `func.datetime(Incidente.created_at, f'{tz_offset_hours:+d} hours')` before passing to `func.strftime`; add a docstring note about the SQLite fixed-offset limitation
- [x] 3.2 Run `pytest tests/test_estadisticas_business_day.py -k test_period_label` and confirm both tests from step 2 now PASS (GREEN)
- [x] 3.3 Run full SQLite suite `pytest -m "not integration"` and confirm it exits 0; if any pre-existing assertion on `periodo` date strings breaks, update those assertions to the correct UTC-3 values and confirm the suite is green before continuing

## 4. TRIANGULATE — Midnight boundary edge case

- [x] 4.1 Write a third test `test_period_label_midnight_argentina_is_day_D` that creates an incident at 03:00 UTC (= 00:00 BA on day D, exactly midnight Argentina time) and asserts the label equals day D; pass `tz_offset_hours=-3` explicitly to exercise the injectable seam; confirm the test PASSES immediately (this verifies the boundary is closed on the correct side)
- [x] 4.2 Run the full SQLite suite again and confirm it exits 0

## 5. REFACTOR

- [x] 5.1 Review `_period_expression` for clarity: ensure the `tz_offset_hours` parameter is documented in the docstring, the SQLite limitation comment references `BUSINESS_TZ` equivalence, and no dead code remains; run `cd App/Backend; ruff check .` and confirm 0 lint errors
- [x] 5.2 Run `pytest -m "not integration"` once more to confirm refactoring did not break anything

## 6. Integration verification — B6

- [x] 6.1 Start the compose PostgreSQL with `docker compose up -d postgres` from the repo root
- [x] 6.2 Run `cd App/Backend; pytest -m integration` against the disposable database and confirm all integration tests pass, including the grouping-label behavior on real PostgreSQL

## 7. Documentation fix — B7

- [x] 7.1 Remove the unbalanced trailing code fence on line 431 of `docs/operational-guide.md` (the lone triple-backtick at the very end of the file with no opening fence); open the file visually and confirm the section ends cleanly with the bullet point referencing `dry-run-harness.md`

## 8. Final validation

- [x] 8.1 Run `openspec validate c-35-dashboard-business-day-grouping --strict` and confirm it exits 0 with no errors
- [x] 8.2 Run `cd App/Backend; pytest -m "not integration"` one final time and confirm the full SQLite suite is green
