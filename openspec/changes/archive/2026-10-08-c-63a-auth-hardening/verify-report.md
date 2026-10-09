# Verify Report: c-63a-auth-hardening

**Change**: c-63a-auth-hardening
**Version**: N/A (delta spec `identity-access-hardening`)
**Governance**: CRITICO (authentication / security / credentials)
**Mode**: Strict TDD (orchestrator-enabled); verification executed independently from repo state and real commands
**Verifier**: sdd-verify (independent re-execution, no reliance on apply summaries)
**Date**: 2026-10-08

---

## 1. Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 30 |
| Tasks complete `[x]` | 30 |
| Tasks incomplete `[ ]` | 0 |

Source: `openspec list --json` -> `{completedTasks: 30, totalTasks: 30, status: complete}` and `openspec status --change c-63a-auth-hardening --json` -> `isPlanningComplete: true`, `isComplete: true`. All six task groups (1-6) fully checked in `tasks.md`.

---

## 2. Build & Tests Execution

### Backend — SQLite unit subset (no PostgreSQL required)
Command: `cd App/Backend; pytest -m "not integration" -q`

```
1136 passed, 42 deselected, 1 xfailed, 283 warnings in 185.28s (0:03:05)
```

### Backend — PostgreSQL integration subset
Prerequisite: `docker compose -p mesa_local up -d postgres` (loopback `127.0.0.1:5433`, health `healthy`).
Command: `cd App/Backend; pytest -m integration -q`

```
42 passed, 1137 deselected, 6 warnings in 30.42s
```

Teardown: `docker compose -p mesa_local stop postgres` executed.

### Dedicated c-63a test files (independent re-run)
Command: `pytest tests/test_password_policy.py tests/test_lockout.py tests/test_auth_tokens.py tests/test_c63a_auth_hardening.py tests/test_migration_013_user_lockout.py tests/test_migration_014_refresh_tokens.py -q`

```
46 passed, 33 warnings in 40.30s
```

### Lint / static
- `cd App/Backend; ruff check .` -> `All checks passed!` (exit 0).
- `openspec validate c-63a-auth-hardening --strict` -> `Change 'c-63a-auth-hardening' is valid` (exit 0).
- OpenAPI sync: `pytest tests/test_openapi_sync.py -q` -> `5 passed`.

### Frontend
- `cd App/Frontend; npm run lint` -> `0 errors, 2 warnings` (both pre-existing in `src/components/ui/input.tsx` and `textarea.tsx`, unrelated to c-63a).
- `cd App/Frontend; npm run test` -> `Test Files 26 passed (26)`, `Tests 124 passed (124)`.

### Migrations (independent PostgreSQL verification, disposable DB)
Created disposable database `c63a_mig_test` on the compose PostgreSQL and ran Alembic directly (not via the SQLite test suite):

- `alembic upgrade head` -> applied 001..014 without error (`013 -> 014` lockout + refresh).
- Schema verified via `psql \d`:
  - `users.failed_attempts` integer NOT NULL DEFAULT 0
  - `users.locked_until` timestamptz NULL
  - `users.token_version` integer NOT NULL DEFAULT 0
  - `refresh_token` table with `user_id`, `token_hash varchar(64)`, `expires_at`, `revoked_at`, `rotated_from`; unique constraint `uq_refresh_token_token_hash`; FK `refresh_token_user_id_fkey REFERENCES users(id) ON DELETE CASCADE`; FK `refresh_token_rotated_from_fkey REFERENCES refresh_token(id) ON DELETE SET NULL`; indexes on user_id, token_hash, revoked_at.
- `alembic downgrade 012` -> ran `014 -> 013` and `013 -> 012`; post-check confirmed the three columns absent and `to_regclass('refresh_token')` NULL; `alembic current` = `012`.
- Disposable database dropped afterwards.

**Coverage**: not executed in this phase. The task's required commands did not include coverage and no cached threshold exists in `openspec/config.yaml`. Marked as SUGGESTION S4.

---

## 3. Spec Compliance Matrix (IAH-001..IAH-004)

A scenario is COMPLIANT only when a test covering it passed at runtime. All tests below were executed in the 1136-passed SQLite subset (and the 46-passed dedicated re-run).

| Requirement | Scenario | Test (file > name) | Result |
|-------------|----------|--------------------|--------|
| IAH-001 Politica de contrasenas | Contrasena debil rechazada | `test_password_policy.py > test_short_password_is_rejected`, `test_common_password_is_rejected`, `test_get_password_hash_enforces_policy_by_default` | ✅ COMPLIANT |
| IAH-001 | Passphrase valida aceptada | `test_password_policy.py > test_passphrase_with_spaces_is_accepted`, `test_get_password_hash_accepts_compliant_password_and_verifies` | ✅ COMPLIANT |
| IAH-001 | Contrasena derivable del username rechazada | `test_password_policy.py > test_password_containing_username_is_rejected`, `test_password_trivial_variation_of_username_is_rejected` | ✅ COMPLIANT |
| IAH-001 | Reutilizacion reciente rechazada | `test_password_policy.py > test_reused_password_is_rejected` (validator-only) | ⚠️ PARTIAL |
| IAH-001 | Credenciales sembradas grandfathered | `test_password_policy.py > test_get_password_hash_can_grandfather_dev_credentials`, `test_seed_directorio.py > test_seed_enlaza_users_y_empleado_y_deja_admin_operativo`, `test_auth.py` (admin/admin123) | ✅ COMPLIANT |
| IAH-002 Bloqueo por intentos | Bloqueo al alcanzar el umbral | `test_lockout.py > test_reaching_threshold_locks_account`, `test_login_returns_account_locked_code_after_threshold` | ✅ COMPLIANT |
| IAH-002 | Cuenta bloqueada rechaza credenciales validas | `test_lockout.py > test_locked_account_rejects_valid_credentials` | ✅ COMPLIANT |
| IAH-002 | Login exitoso resetea el contador | `test_lockout.py > test_successful_login_resets_counter` | ✅ COMPLIANT |
| IAH-002 | El bloqueo expira | `test_lockout.py > test_lock_expires_and_valid_login_succeeds` | ✅ COMPLIANT |
| IAH-002 | Flag apagado preserva el flujo de desarrollo | `test_lockout.py > test_flag_off_preserves_development_flow` | ✅ COMPLIANT |
| IAH-003 Expiracion/refresco | El access token expira | `test_auth_tokens.py > test_expired_access_token_is_rejected` | ✅ COMPLIANT |
| IAH-003 | El login conserva los campos existentes | `test_auth_tokens.py > test_login_contract_is_additive` | ✅ COMPLIANT |
| IAH-003 | El refresco rota el par de tokens | `test_auth_tokens.py > test_refresh_rotates_and_invalidates_previous` | ✅ COMPLIANT |
| IAH-003 | Token de refresco reutilizado es rechazado | `test_auth_tokens.py > test_refresh_reuse_of_rotated_token_is_rejected` | ✅ COMPLIANT |
| IAH-003 | El refresh se persiste hasheado | `test_auth_tokens.py > test_refresh_token_is_persisted_hashed`, `test_lockout.py > test_issue_refresh_token_persists_only_hash` | ✅ COMPLIANT |
| IAH-004 Revocacion/tasa | Logout revoca el token de refresco | `test_auth_tokens.py > test_logout_revokes_refresh` | ✅ COMPLIANT |
| IAH-004 | Token de refresco revocado es rechazado | `test_auth_tokens.py > test_logout_revokes_refresh` (refresh post-logout = 401) | ✅ COMPLIANT |
| IAH-004 | Revocacion administrativa masiva | `test_auth_tokens.py > test_token_version_invalidates_previous_access`, `test_new_access_after_admin_revocation_is_accepted` | ✅ COMPLIANT |
| IAH-004 | Ventana residual declarada | `test_auth_tokens.py > test_residual_window_access_survives_logout` | ✅ COMPLIANT |
| IAH-004 | El limite de tasa no enmascara el bloqueo | `test_c63a_auth_hardening.py > test_nginx_login_burst_exceeds_lockout_threshold` | ✅ COMPLIANT |

**Compliance summary**: 19/20 scenarios COMPLIANT, 1/20 PARTIAL, 0 UNTESTED, 0 FAILING.

---

## 4. Adversarial Security Checks (prove, do not trust)

### 4.1 Password policy (IAH-001)
- Weak rejected: `validate_password("short11char")` raises `PASSWORD_TOO_SHORT`; `"administrator"` raises `PASSWORD_TOO_COMMON`. Enforced at the single provisioning point `get_password_hash` (default `enforce_policy=True`). `app/utils/password_policy.py:165-197`, `app/services/auth_service.py:82-90`.
- Strong passphrases accepted: `"correct horse battery staple"` passes with and without an unrelated username; exact boundary 12 chars passes. No composition/rotation requirement (NIST 800-63B).
- Derivable rejected: containment/substring normalization in both directions (`_is_derivable_from_username`, `password_policy.py:124-138`).
- Grandfather path: `get_password_hash("admin123", enforce_policy=False)` verifies with bcrypt; migration `003` seeds an INLINE hash (no `get_password_hash` call), so fresh installs are unaffected. `scripts/seed_directorio.py:152` calls `get_password_hash(persona["password"])` WITHOUT `enforce_policy=False`; the three seed passwords (`cambiar-esta-clave-{admin,operador,usuario}`) are >= 12 chars, not in the common list, and not derivable, so they pass and dev flow is preserved (confirmed by `test_seed_directorio.py`).
- Error envelope: `PasswordPolicyViolation` handler returns `{"error": {"code", "message", "details?"}}` with HTTP 422 (`core/error_handlers.py:273-281`, `build_policy_envelope`).

### 4.2 Lockout (IAH-002)
- Valid credential rejected once locked: `authenticate_user` checks `locked_until` BEFORE `verify_password` (`auth_service.py:207-215`); route returns 401 `ACCOUNT_LOCKED` and no `access_token` (test asserts absence).
- Code `ACCOUNT_LOCKED`: route catches `AccountLockedError` and emits the distinguished code (`routes/auth.py:103-112`). Note: the handler in `error_handlers.py` also maps it, but the route handles it first — see 4.7.
- Resets on success: `failed_attempts`/`locked_until` cleared on success (`auth_service.py:223-228`).
- Expires: expired lock is cleared before verification (`auth_service.py:212-214`); proven by `test_lock_expires_and_valid_login_succeeds`.
- Flag off by default: `account_lockout_enabled: bool = False` (`settings.py:271`); with the flag off no counter increments and valid credentials log in.
- Not bypassable: the lock check precedes password verification; `_register_failed_attempt` raises at `failed_attempts >= threshold`. Unknown users never lock and return `None` (no existence leak via counter). Window reset uses `updated_at` (`test_window_resets_stale_failures`).
- Persistence of the counter across real HTTP: `get_db_session` commits on normal return even for a 401 JSONResponse (`core/database.py:93-96`), so failed attempts and the lock persist. This also validates the route-level catch of `AccountLockedError` (see 4.7).

### 4.3 Tokens (IAH-003 / IAH-004)
- Access TTL: `create_access_token` defaults to `jwt_access_expire_minutes=15` (`auth_service.py:117-118`); `expires_in == 900` asserted; expired token -> 401.
- Refresh rotation + reuse: `rotate_refresh_token` revokes the presented token and issues a new one (`auth_service.py:343-352`); a revoked/rotated token hits `stored.revoked_at is not None` -> rejected (`auth_service.py:331-333`). Tests cover both rotation and explicit reuse.
- Only the hash is stored: `_hash_refresh_value` = SHA-256 hex (`auth_service.py:275-277`); DB column `token_hash` length 64; tests assert the clear value is neither stored nor a substring. High-entropy opaque value (`secrets.token_urlsafe(48)`), so unsalted SHA-256 is appropriate.
- `token_version` invalidates prior access immediately: `get_current_user` compares the embedded `ver` claim to `user.token_version` (`core/security.py:89-92, 121-132`); non-numeric `ver` normalized to `-1` -> rejected with 401 (not 500). Mass revocation increments the version and revokes active refresh tokens (`auth_service.py:372-397`).
- Residual access window: logout only revokes refresh; the already-issued access survives until its TTL — documented in `routes/auth.py:14-18` and proven by `test_residual_window_access_survives_logout`. Matches IAH-004.

### 4.4 nginx rate limit vs lockout (D7 / IAH-004)
- `nginx/nginx.conf:99-100`: `location /api/v1/auth/login { limit_req zone=login_limit burst=10 nodelay; }`, zone `rate=10r/m` (`line 16`).
- Structural test `test_nginx_login_burst_exceeds_lockout_threshold` asserts `burst (10) >= threshold (5) * 2`, so a client reaches the 5-failure lockout before nginx returns 429. Verified.

### 4.5 Dev flow with flags off
- `admin`/`admin123`: `test_auth.py` seeds with `enforce_policy=False` and all auth tests pass; migration `003` inline hash unchanged.
- `directorio.admin`: `scripts/seed_directorio.py` passwords satisfy the policy (verified above) and the seed suite passes.
- Dry-run telefonía: `test_api_telefonia_corpus.py > test_delete_dry_run_por_defecto_no_borra` remains green.
- `docs/openapi.json` in sync: `test_openapi_sync.py` 5 passed; added paths `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`; `TokenResponse` preserves `access_token` (required) and `token_type` with added optional `refresh_token`/`expires_in`; only descriptive strings were removed.

### 4.6 Scope containment
`git status --porcelain` lists exactly the c-63a backend/frontend/nginx/openapi files, the c-63a artifacts, and the `c-63a`/`c-63b`/`c-63c` change folders. Confirmed ABSENT: `n8n/workflow.json`, `docker-compose.yml`, `CHANGES.md`, and any other change folders. No `.env` staged. Secrets scanner `python3 scripts/security/scan_engram_secrets.py .engram` -> `Total: 0 hallazgo(s)`.

### 4.7 Apply-deviation review
| Deviation | Justified? | Evidence |
|-----------|------------|----------|
| `docs/openapi.json` regenerated (+161 lines) | YES | New endpoints require the spec file to stay in sync; `test_openapi_sync.py` regenerates in-memory and compares — 5 passed. Diff is additive (only docstrings removed). |
| `test_migration_012` downgrade target `-1` -> explicit `011` | YES | Head advanced to 014, so `-1` would revert 014 rather than 012. The test now pins `_DOWN_REVISION = "011"`. Correct and safe; independent downgrade `alembic downgrade 012` verified 014->013->012. |
| `AccountLockedError` caught in `routes/auth.py` instead of propagating to the exception handler | YES | `get_db_session` commits on normal return but ROLLS BACK on any exception (`core/database.py:93-106`). Letting it propagate would discard the freshly-persisted lock state and the account would never actually lock on the triggering request. Catching and returning a JSONResponse preserves the commit. Safe. |

---

## 5. Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| IAH-001 Politica de contrasenas | ✅ Implemented | `password_policy.py` validator + wired into `get_password_hash`; settings exposed; standard envelope handler. |
| IAH-002 Bloqueo por intentos | ✅ Implemented | `failed_attempts`/`locked_until` columns (migration 013), service logic, flag, injectable clock/settings. |
| IAH-003 Expiracion/refresco | ✅ Implemented | Short access, `refresh_token` model/repo (migration 014), `/auth/refresh`, hash-only persistence. |
| IAH-004 Revocacion/tasa | ✅ Implemented | `/auth/logout`, `token_version` check, `revoke_all_sessions`, nginx burst. |
| IAH-001 reutilizacion | ⚠️ Partial | Validator supports `history_hashes`, but no persisted history nor enforcement path in c-63a (documented OQ-1=A, deferred to c-63b). |

---

## 6. Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 Fase A reversible | ✅ Yes | Only auth core; MFA/rotation untouched (c-63b/c folders separate). |
| D2 Policy (own validator, no new deps, NIST) | ✅ Yes | Local common list, no composition, passphrases accepted. |
| D3 Lockout per account, injectable clock, flag default false | ✅ Yes | `LockoutSettings` value object + `now` injection. |
| D4 Short access + persisted opaque refresh (hash) + token_version | ✅ Yes | SQLite-compatible model; hash-only storage. |
| D5 Revocation + residual window declared | ✅ Yes | Logout revokes refresh only; token_version immediate; spec + code document residual TTL. |
| D6 Additive login contract + refresh/logout endpoints | ✅ Yes | `access_token`/`token_type` preserved; new fields optional. |
| D7 nginx burst above lockout threshold | ✅ Yes | burst 5 -> 10 (>= 2x threshold). |
| D8 Dev/test/CI compatibility | ✅ Yes | Flags off by default; dev seeds grandfathered; tests deterministic. |

Open Question OQ-1 = A (policy enforcement at provisioning only; history deferred) is reflected in code comments, `.env.example`, and `design.md`.

---

## 7. Issues Found

**CRITICAL** (must fix before archive): None.

**WARNING** (should fix):
- W1 — IAH-001 "Reutilizacion reciente" is only validator-level. The system has no persisted password history and no call site passes `history_hashes`; the scenario is not realized end-to-end. This is an explicit, author-approved scope decision (OQ-1=A, deferred to c-63b), NOT an open defect. Status: ACCEPTED DEFERRAL (see section 10). Evidence: `password_policy.py:18-22`, `auth_service.py:82-90` (no history arg passed), `test_reused_password_is_rejected` (unit only).
- W2 — RESOLVED (see section 10). Row lock + dedicated `lockout_window_start` column (migration 015), independently re-verified.
- W3 — RESOLVED (see section 10). Coverage measurement executed (aggregate 85%) and TDD cycle evidence recorded.

**SUGGESTION** (nice to have):
- S1 — `ACCOUNT_LOCKED` can reveal that a username exists (only real accounts can reach the locked state). `design.md:45` claims it does not reveal existence. Consider a uniform response or pair with per-IP throttling.
- S2 — Refresh reuse detection rejects the reused token but does not revoke the token family/descendants (`rotate_refresh_token`, `auth_service.py:331-333`). Family revocation would harden against stolen-token replay.
- S3 — `revoke_all_sessions` (administrative mass revocation) has no HTTP endpoint; it is only a service function used in tests. Wiring it belongs to c-63b (privileged role), consistent with scope.
- S4 — Add coverage measurement for the changed auth modules and, if Strict TDD evidence is required for archive, attach the apply-phase TDD cycle table.

---

## 8. Verdict

**PASS** — CRITICAL count: 0, open WARNING count: 0 (W2 and W3 RESOLVED; W1 reclassified as an accepted, author-approved deferral to c-63b).

Tasks 30/30 complete; backend SQLite subset 1145 passed / 1 xfailed, integration 42 passed, frontend 124 passed, ruff and `openspec validate --strict` all green; migrations 013, 014 and 015 independently apply and downgrade on PostgreSQL; all 20 spec scenarios covered (19 COMPLIANT, 1 documented deferral). No blocking security defect. The three apply deviations are each justified and safe. Final independent re-verification recorded in section 10.

---

## 9. Post-verify fixes (W2/W3)

**Date**: 2026-10-08
**Scope**: c-63a only (governance CRITICO). No c-63b/c work started.

### W2 — lockout counter race + window criterion (FIXED)

Two changes address W2:

1. **Row lock on the account.** `authenticate_user` now loads the user with a new `UserRepository.get_by_username_for_update()` that emits `SELECT ... FOR UPDATE` (`with_for_update()`). Concurrent failed attempts for the same account are serialized, and the counter increment is committed in the same Unit of Work (`get_db_session` commits on normal return; the route catch of `AccountLockedError` preserves the commit — see apply deviation). The lock is held from the read through commit/rollback. On SQLite the `FOR UPDATE` clause is not emitted (the dialect ignores it), so the offline subset is unaffected — proven by the full SQLite suite staying green.

2. **Dedicated window column.** New column `users.lockout_window_start` (migration **015**) replaces the `updated_at`-derived window. It is anchored on the first failed attempt of a streak, re-anchored when the window expires, and cleared on successful login / lock expiry. An unrelated update (e.g. deactivating the account) no longer resets the counter.

New migration: **015** `015_user_lockout_window_start.py` (`down_revision = "014"`).

PostgreSQL up/down evidence (scratch DB `c63a_w2_mig` on loopback `127.0.0.1:5433`):
- `alembic upgrade head` -> `014 -> 015`, `alembic current` = `015 (head)`.
- `psql \d users` -> `lockout_window_start | timestamp with time zone | | |`.
- `alembic downgrade 014` -> `015 -> 014`; `information_schema` query for the column returned `(0 rows)`.
- `alembic upgrade head` again -> `014 -> 015` (reversible).
- Disposable database dropped afterwards; `docker compose -p mesa_local stop postgres` executed.

Tests added/updated (`tests/test_lockout.py`, `tests/test_migration_015_lockout_window.py`):
- `test_window_uses_dedicated_column_not_updated_at` (moves `updated_at` to 2020, refreshes, asserts the counter still accumulates within the dedicated window) — this test fails against the pre-W2 `updated_at` logic and passes after the fix.
- `test_success_clears_window_start`, `test_lock_expiry_clears_window_start`, updated `test_window_resets_stale_failures` (asserts re-anchoring).
- `test_get_by_username_for_update_returns_user`, `test_for_update_compiles_on_postgres_and_is_ignored_on_sqlite`, `test_authenticate_uses_locking_helper_when_lockout_enabled`.
- Migration 015 chain + upgrade/downgrade.
- `tests/test_migration_014_refresh_tokens.py` downgrade target changed to `014`'s down-revision `013` because head advanced to 015 (same adaptation pattern previously applied to 012).

**Residual (by design, no action):** the row lock guarantees correctness per account; SQLite remains a serialized single-writer engine, so the offline subset does not exercise true concurrency. The lock intent is proven structurally (PostgreSQL compile) and by the FOR UPDATE helper being on the authentication path.

### W3 — Strict TDD per-file coverage (EXECUTED)

Command:
`pytest tests/test_password_policy.py tests/test_lockout.py tests/test_auth_tokens.py tests/test_auth.py tests/test_c63a_auth_hardening.py tests/test_migration_013_user_lockout.py tests/test_migration_014_refresh_tokens.py tests/test_migration_015_lockout_window.py --cov=app.services.auth_service --cov=app.utils.password_policy --cov=app.repositories.token_repository --cov=app.models.refresh_token --cov=app.core.security --cov-report=term-missing -q`

```
Name                                   Stmts   Miss  Cover   Missing
app/core/security.py                      40     11    72%   79, 103-134
app/models/refresh_token.py               14      1    93%   65
app/repositories/token_repository.py      21      1    95%   52
app/services/auth_service.py             136     23    83%   155, 208-209, 343-366, 379-383
app/utils/password_policy.py              52      4    92%   120-121, 129, 137
TOTAL                                    263     40    85%
74 passed
```

Coverage totals per module: `password_policy` 92%, `token_repository` 95%, `refresh_token` 93%, `auth_service` 83%, `security` 72%, aggregate **85%**. No coverage threshold is configured in `openspec/config.yaml`; this is a measurement, not a gate. Uncovered lines are defensive branches (legacy token without `ver`, inactive-user branch, repr) — the IAH-001..004 behaviors are all covered by the scenario matrix above.

### TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 2.1-2.5 password policy | `tests/test_password_policy.py` | Unit | N/A (new) | Written | 14 passed | 6 boundary cases | Clean |
| 3.1 migration 013 | `tests/test_migration_013_user_lockout.py` | Migration (SQLite file) | N/A (new) | Written | 3 passed | downgrade + re-upgrade | Clean |
| 3.2-3.5 lockout | `tests/test_lockout.py` | Unit + Integration (route) | 1090/1090 | Written | 10 passed | window/locked/flag-off/unknown | Clean |
| W2 window + lock | `tests/test_lockout.py` | Unit + Structural | 1136/1136 | Written (failed on pre-W2 logic) | 6 passed | dedicated column vs updated_at | Clean |
| W2 migration 015 | `tests/test_migration_015_lockout_window.py` | Migration (SQLite file) | N/A (new) | Written | 3 passed | downgrade + re-upgrade | Clean |
| 4.1 migration 014 | `tests/test_migration_014_refresh_tokens.py` | Migration (SQLite file) | N/A (new) | Written | 3 passed | downgrade + re-upgrade | Clean |
| 4.2-4.4 tokens | `tests/test_auth_tokens.py` | Integration (route) + Unit | 1090/1090 | Written | 11 passed | reuse/expired/residual/malformed ver | Clean |
| 5.1-5.5 revocation + nginx | `tests/test_auth_tokens.py`, `tests/test_c63a_auth_hardening.py` | Integration + Structural | 1090/1090 | Written | 5 + 6 passed | new access after revoke | Clean |
| Frontend wiring | `src/services/api.test.ts` | Unit | 121/121 | Written | 3 passed | no-token case | Clean |

### Post-fix verification (exact)

- `cd App/Backend; pytest -m "not integration" -q` -> `1145 passed, 42 deselected, 1 xfailed, 299 warnings in 205.11s`.
- `cd App/Backend; pytest -m integration -q` (postgres started then stopped) -> `42 passed, 1146 deselected, 6 warnings in 27.45s`.
- `cd App/Backend; ruff check .` -> `All checks passed!`.
- `openspec validate c-63a-auth-hardening --strict` -> `Change 'c-63a-auth-hardening' is valid`.
- Frontend not touched in this round (no re-run required).

**Updated verdict**: W2 and W3 resolved. W1 (password-history persistence) remains the single author-approved deferral to c-63b. No CRITICAL issues.

---

## 10. Independent re-verification (post W2/W3 fixes)

**Date**: 2026-10-08
**Method**: re-executed from repo state and real commands; not trusting the apply summary. Governance CRITICO.

### W2 — lockout counter race + window criterion: RESOLVED

- **Row lock present on the authentication path.** `authenticate_user` resolves the account through `UserRepository.get_by_username_for_update()` (`app/repositories/user_repository.py:38-59`), which emits `select(User).where(...).with_for_update()`, and uses it at `app/services/auth_service.py:203`. The lock is held from the read until the Unit of Work commit/rollback (`core/database.py:93-106`), and the route's catch of `AccountLockedError` returns a JSONResponse so the transaction commits (`routes/auth.py:103-112`). This closes the read-then-write lost-update window: concurrent failed attempts for the same account serialize.
- **SQLite unaffected.** `FOR UPDATE` is emitted only for PostgreSQL; the SQLite dialect ignores it. Independently confirmed by `test_for_update_compiles_on_postgres_and_is_ignored_on_sqlite` (asserts `FOR UPDATE` in the PostgreSQL-compiled SQL and absent in SQLite) and by the full offline SQLite suite staying green (1145 passed).
- **Dedicated window column.** The window now uses `users.lockout_window_start` (`auth_service.py:253-262`), set on the first failure of a streak, re-anchored when the window expires, and cleared on success/expiry (`auth_service.py:217-219, 231-234`). `updated_at` is no longer consulted.
- **Migration 015** `015_user_lockout_window_start.py`, `down_revision = "014"`. Independently applied AND downgraded on PostgreSQL against a fresh disposable database `c63a_mig15`:

```
Running upgrade 012 -> 013 ... 013 -> 014 ... 014 -> 015, Migracion 015: `lockout_window_start` dedicada en `users` (W2, c-63a).
lockout_window_start | timestamp with time zone | | |
Running downgrade 015 -> 014, Migracion 015 ...
(information_schema query for lockout_window_start -> empty)
alembic current -> 014
```

  Dispose database dropped; `docker compose -p mesa_local stop postgres` executed.

### Adversarial re-check (W2)

- Race meaningfully mitigated: row lock present and exercised on the auth path (`test_authenticate_uses_locking_helper_when_lockout_enabled` spies the helper and asserts it is called). The lock serializes same-account increments until commit — the prior lost-update path is gone.
- Unrelated `updated_at` change cannot reset the window: `test_window_uses_dedicated_column_not_updated_at` forces `updated_at` to 2020, refreshes, and asserts the counter still accumulates within the dedicated window (2, not 1). This test fails against pre-W2 logic and passes now.
- Not bypassable sequentially: `test_reaching_threshold_locks_account`, `test_locked_account_rejects_valid_credentials`, `test_login_returns_account_locked_code_after_threshold` still pass.
- Counter resets on success/expiry: `test_success_clears_window_start`, `test_lock_expiry_clears_window_start` pass; `test_window_resets_stale_failures` asserts re-anchoring.

### W3 — Strict TDD coverage / evidence: RESOLVED

Independently re-ran the coverage command; the aggregate reproduces exactly:

```
Name                                   Stmts   Miss  Cover   Missing
app/core/security.py                      40     11    72%   79, 103-134
app/models/refresh_token.py               14      1    93%   65
app/repositories/token_repository.py      21      1    95%   52
app/services/auth_service.py             136     23    83%   155, 208-209, 343-366, 379-383
app/utils/password_policy.py              52      4    92%   120-121, 129, 137
TOTAL                                    263     40    85%
74 passed
```

Per-module coverage: `password_policy` 92%, `token_repository` 95%, `refresh_token` 93%, `auth_service` 83%, `security` 72%; aggregate 85%. No coverage threshold is configured in `openspec/config.yaml` (measurement, not a gate). TDD cycle evidence is recorded in section 9. Uncovered lines are defensive/legacy branches, not IAH-001..004 behaviors.

### Regression (exact outputs)

- `cd App/Backend; pytest -m "not integration" -q` -> `1145 passed, 42 deselected, 1 xfailed, 299 warnings in 203.89s (0:03:23)`.
- `cd App/Backend; pytest -m integration -q` (postgres at `127.0.0.1:5433`, then stopped) -> `42 passed, 1146 deselected, 6 warnings in 35.43s`.
- `cd App/Backend; ruff check .` -> `All checks passed!` (exit 0).
- `openspec validate c-63a-auth-hardening --strict` -> `Change 'c-63a-auth-hardening' is valid` (exit 0).

### Scope containment (re-checked)

`git status --porcelain` shows only c-63a files plus `alembic/versions/015_*` and `tests/test_migration_015_*`, plus the c-63a/b/c change folders. Confirmed absent: `n8n/workflow.json`, `docker-compose.yml`, `CHANGES.md`, other change folders. `tasks.md` is NOT modified. No `.env` tracked.

### W1 — reclassified

W1 (password-history persistence for IAH-001 "reutilizacion reciente") is NOT an open warning: it is an explicit author-approved scope deferral (OQ-1=A) recorded in `design.md`, deferred to c-63b. No action required for c-63a. Kept visible as a known limitation.

**Final re-verified verdict**: PASS — CRITICAL 0, open WARNING 0.
