#!/usr/bin/env bash
# ==============================================================================
# Test harness for scripts/backup-restore-test.sh (BACKUP-007).
#
# Uses plain bash assertions so it runs anywhere without a bats dependency.
#
# Covered behavior:
#   - scripts/backup-restore-test.sh exists and is executable
#   - the name guard aborts when the destination DB equals the application DB,
#     and performs no destructive work when it refuses
#   - a missing/unreadable dump fails with a non-zero exit code
#   - triangulation: the guard is active without TEST_PG_ALLOW_APP_DB and the
#     escape hatch is the only way past it; a decrypted-but-invalid SQL dump
#     fails clearly; row-count verification detects a truncated dump
#   - live case: restores a real encrypted dump into a DISPOSABLE database and
#     verifies tables/rows. SKIPPED (with a clear message) when no PostgreSQL
#     container is reachable, so the suite still runs OFFLINE.
#
# Usage:
#   bash scripts/tests/test_backup_restore.sh
#
# Exit codes:
#   0 — all assertions passed (skips do not fail the suite)
#   1 — at least one assertion failed
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
RESTORE_SH="${REPO_ROOT}/scripts/backup-restore-test.sh"

PASSPHRASE="correct-horse-battery-staple-9f3a2b"
APP_URL="postgresql+asyncpg://mesa:mesa@postgres:5432/mesa_de_ayuda"
DISPOSABLE_DB="mesa_de_ayuda_restore_test"
CONTAINER="mesa_local-postgres-1"

FAILURES=0
ASSERTIONS=0
SKIPPED=0

pass() { ASSERTIONS=$((ASSERTIONS + 1)); printf '  ok   - %s\n' "$1"; }
fail() { ASSERTIONS=$((ASSERTIONS + 1)); FAILURES=$((FAILURES + 1)); printf '  FAIL - %s\n' "$1"; }
skip() { SKIPPED=$((SKIPPED + 1)); printf '  skip - %s\n' "$1"; }

assert_contains() {
    case "$1" in
        *"$2"*) pass "$3" ;;
        *) fail "$3 (expected to contain: $2)" ;;
    esac
}

assert_nonzero() {
    if [ "$1" -ne 0 ]; then pass "$2"; else fail "$2 (exit code was 0)"; fi
}

assert_zero() {
    if [ "$1" -eq 0 ]; then pass "$2"; else fail "$2 (exit code was $1)"; fi
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Fake docker that records any invocation: proves the guard refuses BEFORE any
# destructive step, and keeps the offline cases free of real Docker.
FAKE_BIN="${WORK}/fake-bin"
mkdir -p "$FAKE_BIN"
DOCKER_SENTINEL="${WORK}/docker-called.sentinel"
cat > "$FAKE_BIN/docker" <<'EOF'
#!/usr/bin/env bash
printf 'docker invoked: %s\n' "$*" >> "${DOCKER_SENTINEL}"
exit 0
EOF
chmod +x "$FAKE_BIN/docker"

# ─ Fixtures ──────────────────────────────────────────────────────────────────
VALID_DUMP="${WORK}/valid_dump.sql"
cat > "$VALID_DUMP" <<'SQL'
--
-- PostgreSQL database dump
--
CREATE TABLE incidente (id integer, descripcion text);
INSERT INTO incidente VALUES (1, 'muestra pseudonimizada');
SQL

INVALID_DUMP="${WORK}/invalid_dump.sql"
printf 'this is not a postgres dump\n' > "$INVALID_DUMP"

EMPTY_DIR="$(mktemp -d "${WORK}/empty.XXXXXX")"

UNREADABLE_DIR="$(mktemp -d "${WORK}/unreadable.XXXXXX")"
UNREADABLE_ENC="${UNREADABLE_DIR}/backup_2026-10-19.sql.enc"
printf 'not really encrypted\n' > "$UNREADABLE_ENC"
chmod 000 "$UNREADABLE_ENC"

# ─ Source helpers (unit-level triangulation) ─────────────────────────────────
# Sources the script and calls a function inside a subshell with errexit off, so
# the result is observable without exiting the harness.
run_sourced() {
    local func="$1"
    shift
    (
        set +e
        # shellcheck disable=SC1090
        source "$RESTORE_SH"
        set +e
        "$func" "$@"
    ) 2>&1
}

# Runs the guard for a given target and (optional) escape-hatch value.
run_guard() {
    local target="$1" allow="${2-}"
    (
        set +e
        export DATABASE_URL="$APP_URL"
        if [ -n "$allow" ]; then
            export TEST_PG_ALLOW_APP_DB="$allow"
        else
            unset TEST_PG_ALLOW_APP_DB
        fi
        # shellcheck disable=SC1090
        source "$RESTORE_SH"
        set +e
        assert_safe_restore_target "$target"
    ) 2>&1
}

# Runs verify_tables_and_rows with a stubbed psql: every expected table exists,
# and the row count is whatever "$1" says (0 models a truncated dump).
run_verify_with_count() {
    local count="$1"
    (
        set +e
        # shellcheck disable=SC1090
        source "$RESTORE_SH"
        set +e
        RESTORE_DB="stub_db"
        EXPECTED_TABLES="incidente"
        RESTORE_MIN_ROWS=1
        STUB_COUNT="$count"
        restore_psql() {
            case "$*" in
                *information_schema.tables*) printf '1\n' ;;
                *count*) printf '%s\n' "$STUB_COUNT" ;;
                *) printf '\n' ;;
            esac
        }
        verify_tables_and_rows
    ) 2>&1
}

# ─ Tests ─────────────────────────────────────────────────────────────────────
printf 'Restore script: exists and is executable\n'
if [ -f "$RESTORE_SH" ]; then
    pass "restore: scripts/backup-restore-test.sh exists"
else
    fail "restore: scripts/backup-restore-test.sh exists"
fi
if [ -x "$RESTORE_SH" ]; then
    pass "restore: scripts/backup-restore-test.sh is executable"
else
    fail "restore: scripts/backup-restore-test.sh is executable"
fi

printf 'Restore guard: aborts on the application database\n'
rm -f "$DOCKER_SENTINEL"
out=""
status=0
if out="$(PATH="$FAKE_BIN:$PATH" DOCKER_SENTINEL="$DOCKER_SENTINEL" \
        DATABASE_URL="$APP_URL" RESTORE_DB_NAME="mesa_de_ayuda" \
        BACKUP_ENCRYPTION_PASSPHRASE="$PASSPHRASE" \
        bash "$RESTORE_SH" 2>&1)"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "guard: exits non-zero on the application database"
assert_contains "$out" "application database" "guard: explains the refusal"
if [ -f "$DOCKER_SENTINEL" ]; then
    fail "guard: no destructive work happens before the guard"
else
    pass "guard: no destructive work happens before the guard"
fi

printf 'Restore: missing dump fails loudly\n'
out=""
status=0
if out="$(DATABASE_URL="$APP_URL" RESTORE_DB_NAME="$DISPOSABLE_DB" \
        RESTORE_BACKUP_DIR="$EMPTY_DIR" BACKUP_ENCRYPTION_PASSPHRASE="$PASSPHRASE" \
        bash "$RESTORE_SH" 2>&1)"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "missing dump: exits non-zero"
assert_contains "$out" "dump" "missing dump: names the cause"

printf 'Restore: unreadable dump fails loudly\n'
out=""
status=0
if out="$(DATABASE_URL="$APP_URL" RESTORE_DB_NAME="$DISPOSABLE_DB" \
        RESTORE_BACKUP_DIR="$UNREADABLE_DIR" BACKUP_ENCRYPTION_PASSPHRASE="$PASSPHRASE" \
        bash "$RESTORE_SH" 2>&1)"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "unreadable dump: exits non-zero"
assert_contains "$out" "dump" "unreadable dump: names the cause"

# ─ Triangulation ─────────────────────────────────────────────────────────────
printf 'Triangulation: the guard is the only gate and TEST_PG_ALLOW_APP_DB is the escape hatch\n'
out="$(run_guard "mesa_de_ayuda" "")"
status=$?
assert_nonzero "$status" "guard active: app DB target is refused without the escape hatch"
assert_contains "$out" "application database" "guard active: explains the refusal"

out="$(run_guard "mesa_de_ayuda" "1")"
status=$?
assert_zero "$status" "escape hatch: TEST_PG_ALLOW_APP_DB=1 allows the app DB target"

out="$(run_guard "$DISPOSABLE_DB" "")"
status=$?
assert_zero "$status" "guard active: a disposable target is allowed"

printf 'Triangulation: a decrypted-but-invalid SQL dump fails clearly\n'
out="$(run_sourced validate_dump "$INVALID_DUMP")"
status=$?
assert_nonzero "$status" "invalid dump: validate_dump exits non-zero"
assert_contains "$out" "dump" "invalid dump: names the cause"

out="$(run_sourced validate_dump "$VALID_DUMP")"
status=$?
assert_zero "$status" "valid dump: validate_dump accepts a pg_dump banner"

printf 'Triangulation: row-count verification detects a truncated dump\n'
out="$(run_verify_with_count 0)"
status=$?
assert_nonzero "$status" "truncated dump: verify_tables_and_rows exits non-zero"
assert_contains "$out" "row" "truncated dump: reports the row-count problem"

out="$(run_verify_with_count 5)"
status=$?
assert_zero "$status" "healthy dump: verify_tables_and_rows accepts sufficient rows"

# ─ Live restore (skips when no PostgreSQL is reachable) ──────────────────────
printf 'Restore (live): decrypts and restores into a disposable database\n'
if ! command -v docker >/dev/null 2>&1 || \
        ! docker exec "$CONTAINER" pg_isready -U mesa -d mesa_de_ayuda >/dev/null 2>&1; then
    skip "live restore: no reachable PostgreSQL container '$CONTAINER'; guard/verification covered offline"
else
    LIVE_DIR="$(mktemp -d "${WORK}/live.XXXXXX")"
    PLAIN="${LIVE_DIR}/source.sql"
    if docker exec "$CONTAINER" pg_dump -U mesa mesa_de_ayuda > "$PLAIN" 2>/dev/null; then
        export BACKUP_ENCRYPTION_PASSPHRASE="$PASSPHRASE"
        if openssl enc -aes-256-cbc -pbkdf2 -salt \
                -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
                -in "$PLAIN" -out "${LIVE_DIR}/backup_live.sql.enc" 2>/dev/null; then
            before="$(docker exec "$CONTAINER" psql -U mesa -d mesa_de_ayuda -tAc "SELECT count(*) FROM incidente" | tr -d '[:space:]')"
            out=""
            status=0
            if out="$(DATABASE_URL="$APP_URL" RESTORE_BACKUP_DIR="$LIVE_DIR" \
                    RESTORE_DB_NAME="$DISPOSABLE_DB" RESTORE_CONTAINER="$CONTAINER" \
                    BACKUP_ENCRYPTION_PASSPHRASE="$PASSPHRASE" \
                    bash "$RESTORE_SH" 2>&1)"; then
                status=0
            else
                status=$?
            fi
            assert_zero "$status" "live restore: exits 0"
            assert_contains "$out" "verified" "live restore: reports table/row verification"
            remaining="$(docker exec "$CONTAINER" psql -U mesa -d postgres -tAc \
                "SELECT 1 FROM pg_database WHERE datname='${DISPOSABLE_DB}'" | tr -d '[:space:]')"
            if [ -z "$remaining" ]; then
                pass "live restore: disposable database is cleaned up"
            else
                fail "live restore: disposable database is cleaned up ($DISPOSABLE_DB still exists)"
            fi
            after="$(docker exec "$CONTAINER" psql -U mesa -d mesa_de_ayuda -tAc "SELECT count(*) FROM incidente" | tr -d '[:space:]')"
            if [ "$before" = "$after" ]; then
                pass "live restore: the application database is untouched"
            else
                fail "live restore: the application database is untouched ($before -> $after)"
            fi
        else
            skip "live restore: could not encrypt the generated dump (openssl unavailable)"
        fi
    else
        skip "live restore: could not generate a dump from '$CONTAINER'"
    fi
fi

printf '\n%s assertions, %s failure(s), %s skipped\n' "$ASSERTIONS" "$FAILURES" "$SKIPPED"
if [ "$FAILURES" -ne 0 ]; then
    exit 1
fi
printf 'All backup restore tests passed.\n'
exit 0
