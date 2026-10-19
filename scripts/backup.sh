#!/usr/bin/env bash
# ==============================================================================
# PostgreSQL backup script for Automatizacion-Mesa-de-Ayuda-N8N
#
# Runs pg_dump from the postgres Docker container (project name: mesa_local).
# Encrypts the dump at rest (AES-256-CBC, pbkdf2) and saves it to backups/ as
# backup_YYYY-MM-DD.sql.enc, keeping the last 7 daily encrypted backups.
#
# Usage:
#   BACKUP_ENCRYPTION_PASSPHRASE=... bash scripts/backup.sh
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - The postgres container is running (docker compose up -d postgres)
#   - BACKUP_ENCRYPTION_PASSPHRASE set to the deployment secret
#
# Exit codes:
#   0 — backup completed successfully
#   1 — error (missing passphrase, container not running, dump failed, etc.)
# ==============================================================================

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${REPO_ROOT}/backups"
RETENTION_COUNT=7

COMPOSE_PROJECT_NAME="mesa_local"
SERVICE_NAME="postgres"
DB_USER="mesa"
DB_NAME="mesa_de_ayuda"

# ── Helpers ─────────────────────────────────────────────────────────────────
# The dump MUST NOT be persisted in plaintext. Abort before pg_dump if the
# deployment secret is missing, so no clear-text dump is ever written.
require_passphrase() {
    if [ -z "${BACKUP_ENCRYPTION_PASSPHRASE:-}" ]; then
        echo "ERROR: BACKUP_ENCRYPTION_PASSPHRASE is not set."
        echo "Set it to a deployment secret before running the backup."
        exit 1
    fi
}

encrypt_dump() {
    local plaintext="$1"
    local out="$2"
    if ! openssl enc -aes-256-cbc -pbkdf2 -salt \
            -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
            -in "$plaintext" -out "$out"; then
        echo "ERROR: backup encryption failed."
        rm -f "$out"
        exit 1
    fi
}

rotate_backups() {
    cd "$BACKUP_DIR"
    local backup_files total
    backup_files=($(ls -1t backup_*.sql.enc 2>/dev/null || true))
    total=${#backup_files[@]}
    if [ "$total" -gt "$RETENTION_COUNT" ]; then
        local old_backups=("${backup_files[@]:$RETENTION_COUNT}")
        echo "Rotating: removing ${#old_backups[@]} old backup(s)..."
        for old_file in "${old_backups[@]}"; do
            echo "  Deleting: $old_file"
            rm -f "$old_file"
        done
        echo "Rotation complete. Kept $RETENTION_COUNT most recent backups."
    else
        echo "No rotation needed ($total backups, retention=$RETENTION_COUNT)."
    fi
}

require_passphrase

# ── Idempotent: ensure backup directory exists ───────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── Verify container is running ──────────────────────────────────────────────
CONTAINER_ID=""
# Docker Compose v2 uses compose project name; the container is named
# <project>-<service>-<instance>. Try project-service-1 first.
for candidate in \
    "${COMPOSE_PROJECT_NAME}-${SERVICE_NAME}-1" \
    "${COMPOSE_PROJECT_NAME}_${SERVICE_NAME}_1" \
    "mesa_local-postgres-1" \
    "mesa_local_postgres_1"; do
    if docker inspect --format='{{.State.Running}}' "$candidate" 2>/dev/null | grep -q true; then
        CONTAINER_ID="$candidate"
        break
    fi
done

if [ -z "$CONTAINER_ID" ]; then
    echo "ERROR: PostgreSQL container not running."
    echo "Ensure the stack is up:  docker compose up -d postgres"
    exit 1
fi

# ── Generate timestamped filename ────────────────────────────────────────────
# Uses local date. For cron, this will be the date the backup runs.
if date --version >/dev/null 2>&1; then
    # GNU date (Linux)
    TIMESTAMP=$(date +%Y-%m-%d)
else
    # BSD date (macOS) fallback
    TIMESTAMP=$(date "+%Y-%m-%d")
fi
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.enc"
PLAINTEXT_DUMP="$(mktemp "${TMPDIR:-/tmp}/backup_plain.XXXXXX")"
remove_plaintext_dump() { rm -f "$PLAINTEXT_DUMP" 2>/dev/null || true; }
trap remove_plaintext_dump EXIT

# ── Run pg_dump ──────────────────────────────────────────────────────────────
echo "Backing up PostgreSQL to: $BACKUP_FILE"

if ! docker exec "$CONTAINER_ID" pg_dump -U "$DB_USER" "$DB_NAME" > "$PLAINTEXT_DUMP" 2>/tmp/backup_error.log; then
    echo "ERROR: pg_dump failed."
    cat /tmp/backup_error.log
    rm -f /tmp/backup_error.log
    exit 1
fi

rm -f /tmp/backup_error.log 2>/dev/null || true

# ── Encrypt the dump at rest ─────────────────────────────────────────────────
encrypt_dump "$PLAINTEXT_DUMP" "$BACKUP_FILE"

remove_plaintext_dump

SIZE=$(du -h "$BACKUP_FILE" 2>/dev/null | cut -f1 || echo "unknown")
echo "Backup completed: $BACKUP_FILE ($SIZE)"

# ── Rotate: keep only the $RETENTION_COUNT most recent backups ────────────────
rotate_backups

echo "Done."
exit 0
