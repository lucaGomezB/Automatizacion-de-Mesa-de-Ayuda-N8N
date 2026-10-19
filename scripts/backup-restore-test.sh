#!/usr/bin/env bash
# ==============================================================================
# Reproducible restore test for Automatizacion-Mesa-de-Ayuda-N8N (BACKUP-007).
#
# Decrypts the most recent encrypted dump produced by scripts/backup.sh,
# restores it into a DISPOSABLE PostgreSQL database and verifies that the
# expected tables exist with a plausible row count. The application database is
# NEVER a valid target: the name guard aborts before any destructive operation.
#
# Usage:
#   BACKUP_ENCRYPTION_PASSPHRASE=... bash scripts/backup-restore-test.sh
#
# Environment:
#   BACKUP_ENCRYPTION_PASSPHRASE  (required) decryption secret; same as backup.sh
#   DATABASE_URL                  application URL; the database NAME is the value
#                                 the guard protects (if unset, the guard has no
#                                 reference and cannot compare)
#   RESTORE_BACKUP_DIR            directory holding backup_*.sql.enc (default: <repo>/backups)
#   RESTORE_DB_NAME               disposable target database (default: mesa_de_ayuda_restore_test)
#   RESTORE_CONTAINER             postgres container name (default: mesa_local-postgres-1)
#   RESTORE_DB_USER               database user (default: mesa)
#   RESTORE_EXPECTED_TABLES       space-separated tables to verify
#   RESTORE_MIN_ROWS              minimum rows per expected table (default: 1)
#   TEST_PG_ALLOW_APP_DB=1        the ONLY escape hatch for an app-named target;
#                                 reserved for dedicated, ephemeral environments
#
# Exit codes:
#   0 — dump decrypted, restored and verified successfully
#   1 — any failure (unsafe target, missing/unreadable/undecryptable dump,
#       restore error, verification failure)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

BACKUP_DIR="${RESTORE_BACKUP_DIR:-${REPO_ROOT}/backups}"
CONTAINER="${RESTORE_CONTAINER:-mesa_local-postgres-1}"
DB_USER="${RESTORE_DB_USER:-mesa}"
RESTORE_DB="${RESTORE_DB_NAME:-mesa_de_ayuda_restore_test}"
EXPECTED_TABLES="${RESTORE_EXPECTED_TABLES:-incidente estado sector canal_origen users clasificacion_log}"

PLAINTEXT_DUMP=""
RESTORE_CREATED_DB=0

log() { printf '%s\n' "$*"; }
err() { printf 'ERROR: %s\n' "$*" >&2; }

# ── Name guard (mirrors the c-32 integration-suite guard) ────────────────────
# Extracts the database name from a SQLAlchemy-style URL, e.g.
# postgresql+asyncpg://user:pw@host:5432/mesa_de_ayuda -> mesa_de_ayuda.
app_db_name() {
    local url="${DATABASE_URL:-}"
    [ -n "$url" ] || return 0
    printf '%s' "$url" | sed -E 's#^[^/]*//[^/]*/##; s#\?.*$##'
}

# Aborts (non-zero) when the destination database NAME equals the application
# database named by DATABASE_URL. TEST_PG_ALLOW_APP_DB=1 is the only escape.
assert_safe_restore_target() {
    local target="$1"
    if [ "${TEST_PG_ALLOW_APP_DB:-}" = "1" ]; then
        return 0
    fi
    local app_db
    app_db="$(app_db_name)"
    if [ -n "$app_db" ] && [ "$target" = "$app_db" ]; then
        err "Unsafe restore target: '$target' is the application database declared by DATABASE_URL."
        err "Refusing to restore over it. Use a disposable database name or, only for"
        err "dedicated ephemeral environments, set TEST_PG_ALLOW_APP_DB=1 to acknowledge the risk."
        exit 1
    fi
    return 0
}

require_passphrase() {
    if [ -z "${BACKUP_ENCRYPTION_PASSPHRASE:-}" ]; then
        err "BACKUP_ENCRYPTION_PASSPHRASE is not set; cannot decrypt the dump."
        exit 1
    fi
}

# Emits the most recent encrypted dump, or nothing when none exists.
latest_dump() {
    local dir="$1" files
    files="$(ls -1t "${dir}"/backup_*.sql.enc 2>/dev/null || true)"
    printf '%s\n' "$files" | head -n 1
}

decrypt_dump() {
    local in="$1" out="$2"
    if ! openssl enc -d -aes-256-cbc -pbkdf2 \
            -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
            -in "$in" -out "$out" 2>/dev/null; then
        err "Failed to decrypt dump: $in (wrong passphrase or corrupted file?)"
        return 1
    fi
}

# A dump must exist, be readable, be non-empty and carry the pg_dump banner.
validate_dump() {
    local dump="$1"
    if [ ! -s "$dump" ]; then
        err "Dump is missing, empty or unreadable: $dump"
        return 1
    fi
    if ! head -n 20 "$dump" | grep -q "PostgreSQL database dump"; then
        err "Dump does not look like a PostgreSQL dump (missing pg_dump banner): $dump"
        return 1
    fi
    return 0
}

# ── Database operations (via the postgres container, like backup.sh) ─────────
restore_psql() {
    docker exec -i "$CONTAINER" psql -U "$DB_USER" "$@"
}

recreate_disposable_db() {
    restore_psql -d postgres -v ON_ERROR_STOP=1 -c \
        "DROP DATABASE IF EXISTS \"$RESTORE_DB\" WITH (FORCE)" >/dev/null
    restore_psql -d postgres -v ON_ERROR_STOP=1 -c \
        "CREATE DATABASE \"$RESTORE_DB\"" >/dev/null
    RESTORE_CREATED_DB=1
}

restore_dump() {
    restore_psql -d "$RESTORE_DB" -v ON_ERROR_STOP=1 < "$1" >/dev/null
}

# ── Verification ─────────────────────────────────────────────────────────────
# Every expected table must exist and hold at least RESTORE_MIN_ROWS rows; a
# truncated dump drops the table or leaves it short, which this catches.
verify_tables_and_rows() {
    local table count min_rows failed=0
    min_rows="${RESTORE_MIN_ROWS:-1}"
    for table in $EXPECTED_TABLES; do
        if [ "$(restore_psql -d "$RESTORE_DB" -tAc \
                "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='$table'")" != "1" ]; then
            err "Restored database is missing expected table: $table"
            failed=1
            continue
        fi
        count="$(restore_psql -d "$RESTORE_DB" -tAc "SELECT count(*) FROM \"$table\"" | tr -d '[:space:]')"
        case "$count" in
            ''|*[!0-9]*)
                err "Could not read the row count for table: $table"
                failed=1
                continue
                ;;
        esac
        if [ "$count" -lt "$min_rows" ]; then
            err "Table '$table' has $count row(s) below the expected minimum of $min_rows (truncated dump?)."
            failed=1
        fi
    done
    return "$failed"
}

cleanup() {
    if [ -n "$PLAINTEXT_DUMP" ]; then
        rm -f "$PLAINTEXT_DUMP"
    fi
    if [ "$RESTORE_CREATED_DB" = "1" ]; then
        restore_psql -d postgres -v ON_ERROR_STOP=1 -c \
            "DROP DATABASE IF EXISTS \"$RESTORE_DB\" WITH (FORCE)" >/dev/null 2>&1 || true
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
    assert_safe_restore_target "$RESTORE_DB"
    require_passphrase

    local enc
    enc="$(latest_dump "$BACKUP_DIR")"
    if [ -z "$enc" ]; then
        err "No encrypted backup dump (backup_*.sql.enc) found in: $BACKUP_DIR"
        exit 1
    fi

    PLAINTEXT_DUMP="$(mktemp "${TMPDIR:-/tmp}/restore_plain.XXXXXX")"
    trap cleanup EXIT

    decrypt_dump "$enc" "$PLAINTEXT_DUMP" || exit 1
    validate_dump "$PLAINTEXT_DUMP" || exit 1

    log "Restoring $(basename "$enc") into disposable database '$RESTORE_DB' ..."
    recreate_disposable_db
    if ! restore_dump "$PLAINTEXT_DUMP"; then
        err "Restore failed for '$RESTORE_DB'."
        exit 1
    fi

    if ! verify_tables_and_rows; then
        err "Restore verification failed for '$RESTORE_DB'."
        exit 1
    fi

    log "Restore verified: expected tables present and row counts OK in '$RESTORE_DB'."
    log "Done."
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
