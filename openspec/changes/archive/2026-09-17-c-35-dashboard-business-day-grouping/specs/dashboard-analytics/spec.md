## ADDED Requirements

### Requirement: Period grouping uses the business day in Argentina time (UTC-3)

The system SHALL group incidents by their calendar day in
`America/Argentina/Buenos_Aires` (UTC-3) when producing period labels for the
trend aggregation endpoint. The `periodo` field in the `series` array MUST
reflect the local business date, NOT the UTC date, of the incident's creation
timestamp.

This applies to both supported SQL engines:
- PostgreSQL (production): convert `created_at` to
  `America/Argentina/Buenos_Aires` before truncating to a date.
- SQLite (test seam): apply a -3-hour offset to `created_at` before calling
  `strftime`. The offset MUST be injectable (via a `tz_offset_hours` parameter
  defaulting to -3) so unit tests can verify boundary behavior deterministically.

#### Scenario: Incident at 23:30 Argentina time groups under its local date

- **WHEN** an incident is created at 23:30 Argentina time on day D (which equals
  02:30 UTC on day D+1) and the trend endpoint is queried with `agrupar_por=dia`
- **THEN** the `periodo` label for that incident SHALL be the YYYY-MM-DD string
  for day D in Argentina, not day D+1 (the UTC date)

#### Scenario: Incident at 01:00 UTC groups under the previous Argentina date

- **WHEN** an incident is created at 01:00 UTC on day D+1 (which equals 22:00
  Argentina time on day D) and the trend endpoint is queried with
  `agrupar_por=dia`
- **THEN** the `periodo` label for that incident SHALL be the YYYY-MM-DD string
  for day D (the Argentina business date), not day D+1

#### Scenario: Midnight boundary in Argentina falls on the correct day

- **WHEN** an incident is created at exactly 00:00 Argentina time on day D
  (= 03:00 UTC on day D) and the trend endpoint is queried with `agrupar_por=dia`
- **THEN** the `periodo` label SHALL be the YYYY-MM-DD string for day D
