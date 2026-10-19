#!/usr/bin/env bash
# ==============================================================================
# Test harness for scripts/backup.sh (dump encryption at rest, BACKUP-005).
#
# Uses plain bash assertions so it runs anywhere without a bats dependency.
# The harness runs OFFLINE: it installs a fake `docker` on PATH that emulates
# the subset backup.sh uses (inspect -> true, exec pg_dump -> sample SQL) and
# uses the REAL openssl for the encryption/decryption assertions.
#
# Isolation: each case copies scripts/backup.sh into a throwaway repo layout
# (<tmp>/repo/scripts/backup.sh) so BACKUP_DIR resolves inside the temp tree and
# the real backups/ directory is never touched.
#
# Covered behavior:
#   - with the passphrase set    -> an encrypted artifact (.sql.enc) is produced
#   - no plaintext SQL artifact remains in backups/ and no .sql dump is left
#   - without the passphrase     -> non-zero exit, names the variable, no dump
#   - triangulation: correct passphrase decrypts to the original dump; a wrong
#     passphrase fails loudly; rotation keeps exactly 7 encrypted files; the
#     PowerShell pair declares the same cipher and the same variable
#
# Usage:
#   bash scripts/tests/test_backup.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
BACKUP_SH="${REPO_ROOT}/scripts/backup.sh"
BACKUP_PS1="${REPO_ROOT}/scripts/backup.ps1"

FAILURES=0
ASSERTIONS=0

pass() { ASSERTIONS=$((ASSERTIONS + 1)); printf '  ok   - %s\n' "$1"; }
fail() { ASSERTIONS=$((ASSERTIONS + 1)); FAILURES=$((FAILURES + 1)); printf '  FAIL - %s\n' "$1"; }

assert_contains() {
    case "$1" in
        *"$2"*) pass "$3" ;;
        *) fail "$3 (expected to contain: $2)" ;;
    esac
}

assert_not_contains() {
    case "$1" in
        *"$2"*) fail "$3 (must NOT contain: $2)" ;;
        *) pass "$3" ;;
    esac
}

assert_nonzero() {
    if [ "$1" -ne 0 ]; then pass "$2"; else fail "$2 (exit code was 0)"; fi
}

assert_zero() {
    if [ "$1" -eq 0 ]; then pass "$2"; else fail "$2 (exit code was $1)"; fi
}

# Fails when the ERE in $2 matches anywhere in file $1 (used for negative grep).
assert_grep_absent() {
    if grep -Eq "$2" "$1"; then
        fail "$3 (matched: $2)"
    else
        pass "$3"
    fi
}

if [ ! -f "$BACKUP_SH" ]; then
    printf 'FAIL - scripts/backup.sh not found at %s\n' "$BACKUP_SH"
    exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─ Fake docker ───────────────────────────────────────────────────────────────
# Emulates the subset of docker used by backup.sh. `inspect` reports the
# container running; `exec ... pg_dump` emits the sample SQL dump on stdout.
FAKE_BIN="${WORK}/fake-bin"
mkdir -p "$FAKE_BIN"

# Sample dump emitted by the fake pg_dump and used as the decryption reference.
SAMPLE_DUMP="${WORK}/sample_dump.sql"
cat > "$SAMPLE_DUMP" <<'SQL'
--
-- PostgreSQL database dump
--
CREATE TABLE incidente (id integer, descripcion text);
INSERT INTO incidente VALUES (1, 'muestra pseudonimizada');
SQL
export FAKE_DUMP_FILE="$SAMPLE_DUMP"

cat > "$FAKE_BIN/docker" <<'EOF'
#!/usr/bin/env bash
sub="${1-}"
case "$sub" in
    inspect) printf 'true\n'; exit 0 ;;
    exec) cat "${FAKE_DUMP_FILE:?}"; exit 0 ;;
    *) exit 0 ;;
esac
EOF
chmod +x "$FAKE_BIN/docker"

# ─ Helpers ───────────────────────────────────────────────────────────────────
PASSPHRASE="correct-horse-battery-staple-9f3a2b"

# Builds a throwaway repo layout with a copy of the real backup.sh, so
# BACKUP_DIR resolves inside the temp tree. Echoes the repo path.
new_repo() {
    local d
    d="$(mktemp -d "${WORK}/repo.XXXXXX")"
    mkdir -p "$d/scripts" "$d/backups"
    cp "$BACKUP_SH" "$d/scripts/backup.sh"
    chmod +x "$d/scripts/backup.sh"
    printf '%s' "$d"
}

# Runs the copied backup.sh with the fake docker on PATH. $1 = repo, $2 =
# passphrase (empty means the variable is unset).
run_backup() {
    local repo="$1" pass="$2"
    if [ -n "$pass" ]; then
        PATH="$FAKE_BIN:$PATH" BACKUP_ENCRYPTION_PASSPHRASE="$pass" \
            bash "$repo/scripts/backup.sh" 2>&1
    else
        PATH="$FAKE_BIN:$PATH" env -u BACKUP_ENCRYPTION_PASSPHRASE \
            bash "$repo/scripts/backup.sh" 2>&1
    fi
}

# Emits any backup artifact (first match) in the repo's backups dir.
first_artifact() {
    find "$1/backups" -maxdepth 1 -type f -name 'backup_*' 2>/dev/null | head -n 1
}

# Emits the first plaintext-SQL artifact (contains the pg_dump banner), if any.
plaintext_artifact() {
    grep -l 'PostgreSQL database dump' "$1"/backups/backup_* 2>/dev/null | head -n 1
}

# ─ Tests ─────────────────────────────────────────────────────────────────────
printf 'Encryption: dump is encrypted at rest\n'
repo="$(new_repo)"
out=""
status=0
if out="$(run_backup "$repo" "$PASSPHRASE")"; then status=0; else status=$?; fi
assert_zero "$status" "encrypt: backup exits 0 with the passphrase set"

enc_file="$(find "$repo/backups" -maxdepth 1 -type f -name 'backup_*.enc' 2>/dev/null | head -n 1)"
if [ -n "$enc_file" ]; then
    pass "encrypt: an encrypted artifact (.enc) exists"
else
    fail "encrypt: an encrypted artifact (.enc) exists"
fi

plain="$(plaintext_artifact "$repo")"
if [ -z "$plain" ]; then
    pass "encrypt: no backup artifact is readable as plain SQL"
else
    fail "encrypt: no backup artifact is readable as plain SQL ($plain)"
fi

sql_leftover="$(find "$repo/backups" -maxdepth 1 -type f -name 'backup_*.sql' 2>/dev/null | head -n 1)"
if [ -z "$sql_leftover" ]; then
    pass "encrypt: no plaintext .sql dump left in backups/"
else
    fail "encrypt: no plaintext .sql dump left in backups/ ($sql_leftover)"
fi

printf 'Encryption: missing passphrase aborts before persisting\n'
repo="$(new_repo)"
out=""
status=0
if out="$(run_backup "$repo" "")"; then status=0; else status=$?; fi
assert_nonzero "$status" "no passphrase: backup exits non-zero"
assert_contains "$out" "BACKUP_ENCRYPTION_PASSPHRASE" "no passphrase: names the offending variable"

leftover="$(first_artifact "$repo")"
if [ -z "$leftover" ]; then
    pass "no passphrase: no dump persisted in backups/"
else
    fail "no passphrase: no dump persisted in backups/ ($leftover)"
fi

# ─ Triangulation ─────────────────────────────────────────────────────────────
printf 'Triangulation: correct passphrase decrypts to the original dump\n'
repo="$(new_repo)"
status=0
if run_backup "$repo" "$PASSPHRASE" >/dev/null 2>&1; then status=0; else status=$?; fi
assert_zero "$status" "decrypt: backup exits 0"
enc_file="$(find "$repo/backups" -maxdepth 1 -type f -name 'backup_*.enc' 2>/dev/null | head -n 1)"
if [ -n "$enc_file" ]; then
    decrypted="${WORK}/decrypted_correct.sql"
    if openssl enc -d -aes-256-cbc -pbkdf2 -pass "pass:$PASSPHRASE" \
            -in "$enc_file" -out "$decrypted" 2>/dev/null; then
        pass "decrypt: correct passphrase decrypts the artifact"
    else
        fail "decrypt: correct passphrase decrypts the artifact"
    fi
    if [ -f "$decrypted" ] && cmp -s "$decrypted" "$SAMPLE_DUMP"; then
        pass "decrypt: decrypted content matches the original dump"
    else
        fail "decrypt: decrypted content matches the original dump"
    fi
else
    fail "decrypt: correct passphrase decrypts the artifact (no .enc artifact)"
    fail "decrypt: decrypted content matches the original dump (no .enc artifact)"
fi

printf 'Triangulation: wrong passphrase fails loudly\n'
repo="$(new_repo)"
status=0
if run_backup "$repo" "$PASSPHRASE" >/dev/null 2>&1; then status=0; else status=$?; fi
enc_file="$(find "$repo/backups" -maxdepth 1 -type f -name 'backup_*.enc' 2>/dev/null | head -n 1)"
wrong_out=""
wrong_status=0
if wrong_out="$(openssl enc -d -aes-256-cbc -pbkdf2 -pass "pass:definitely-not-the-passphrase" \
        -in "$enc_file" -out "${WORK}/decrypted_wrong.sql" 2>&1)"; then
    wrong_status=0
else
    wrong_status=$?
fi
assert_nonzero "$wrong_status" "wrong passphrase: decryption exits non-zero"
if [ -f "${WORK}/decrypted_wrong.sql" ] && cmp -s "${WORK}/decrypted_wrong.sql" "$SAMPLE_DUMP"; then
    fail "wrong passphrase: does not reproduce the original dump"
else
    pass "wrong passphrase: does not reproduce the original dump"
fi

printf 'Triangulation: rotation over encrypted files keeps exactly 7\n'
repo="$(new_repo)"
for i in $(seq 1 10); do
    f="$repo/backups/backup_2026-09-$(printf '%02d' "$i").sql.enc"
    printf 'dummy-%s\n' "$i" > "$f"
    touch -d "2026-09-$(printf '%02d' "$i") 00:00:00" "$f"
done
status=0
if run_backup "$repo" "$PASSPHRASE" >/dev/null 2>&1; then status=0; else status=$?; fi
assert_zero "$status" "rotation: backup exits 0"
rot_count="$(find "$repo/backups" -maxdepth 1 -type f -name 'backup_*.sql.enc' 2>/dev/null | wc -l | tr -d ' ')"
if [ "$rot_count" -eq 7 ]; then
    pass "rotation: exactly 7 encrypted files remain (got $rot_count)"
else
    fail "rotation: exactly 7 encrypted files remain (got $rot_count)"
fi
oldest_expected_removed="$repo/backups/backup_2026-09-04.sql.enc"
if [ ! -f "$oldest_expected_removed" ]; then
    pass "rotation: the oldest backups are removed (2026-09-04 gone)"
else
    fail "rotation: the oldest backups are removed (2026-09-04 present)"
fi
newest_kept="$repo/backups/backup_2026-09-10.sql.enc"
if [ -f "$newest_kept" ]; then
    pass "rotation: the most recent backups are kept (2026-09-10 present)"
else
    fail "rotation: the most recent backups are kept (2026-09-10 present)"
fi

printf 'Triangulation: PowerShell parity (structural)\n'
if [ -f "$BACKUP_PS1" ]; then
    pass "backup.ps1 exists"
else
    fail "backup.ps1 exists"
fi
ps1_content="$(<"$BACKUP_PS1")"
assert_contains "$ps1_content" "BACKUP_ENCRYPTION_PASSPHRASE" "backup.ps1 references BACKUP_ENCRYPTION_PASSPHRASE"
assert_contains "$ps1_content" "aes-256-cbc" "backup.ps1 declares the AES-256-CBC cipher"
assert_contains "$ps1_content" "pbkdf2" "backup.ps1 declares pbkdf2"
assert_contains "$ps1_content" ".sql.enc" "backup.ps1 uses the .sql.enc extension"
assert_contains "$ps1_content" "backup_*.sql.enc" "backup.ps1 rotates over encrypted files"

# ─ Versioned scheduler (BACKUP-006) ──────────────────────────────────────────
# The automation MUST be a versioned file under scripts/ (cron primary, systemd
# timer documented as an equivalent alternative), it MUST invoke backup.sh,
# log its output and MUST NOT carry secrets.
printf 'Scheduler: a versioned schedule file exists under scripts/\n'
SCHEDULE_FILE=""
for candidate in \
    "${REPO_ROOT}/scripts/backup-schedule.cron" \
    "${REPO_ROOT}/scripts/backup-schedule.timer"; do
    if [ -f "$candidate" ]; then SCHEDULE_FILE="$candidate"; break; fi
done
if [ -n "$SCHEDULE_FILE" ]; then
    pass "schedule: a versioned schedule file exists (${SCHEDULE_FILE##*/})"
else
    fail "schedule: a versioned schedule file exists (scripts/backup-schedule.cron)"
fi

if [ -n "$SCHEDULE_FILE" ]; then
    schedule_content="$(<"$SCHEDULE_FILE")"
else
    schedule_content=""
fi
schedule_lower="$(printf '%s' "$schedule_content" | tr '[:upper:]' '[:lower:]')"

assert_contains "$schedule_content" "scripts/backup.sh" "schedule: invokes scripts/backup.sh"
assert_contains "$schedule_content" ">>" "schedule: redirects the backup output"
assert_contains "$schedule_content" ".log" "schedule: writes to a log file"
assert_contains "$schedule_lower" "systemd" "schedule: documents the systemd alternative"
assert_contains "$schedule_lower" "timer" "schedule: documents the systemd timer alternative"

if [ -n "$SCHEDULE_FILE" ]; then
    assert_grep_absent "$SCHEDULE_FILE" 'BACKUP_ENCRYPTION_PASSPHRASE=[^[:space:]]' \
        "schedule: carries no passphrase value"
    assert_grep_absent "$SCHEDULE_FILE" '(PASSWORD|PGPASSWORD|SECRET|TOKEN)=[^[:space:]]' \
        "schedule: carries no credential value"
else
    fail "schedule: carries no passphrase value (no schedule file)"
    fail "schedule: carries no credential value (no schedule file)"
fi

printf 'Triangulation: the schedule uses a repo-relative invocation (no secrets)\n'
if [ -n "$SCHEDULE_FILE" ]; then
    assert_grep_absent "$SCHEDULE_FILE" '[^[:space:]]/scripts/backup.sh' \
        "schedule: invokes backup.sh via the repo-relative path"
else
    fail "schedule: invokes backup.sh via the repo-relative path (no schedule file)"
fi

printf '\n%s assertions, %s failure(s)\n' "$ASSERTIONS" "$FAILURES"
if [ "$FAILURES" -ne 0 ]; then
    exit 1
fi
printf 'All backup tests passed.\n'
exit 0
