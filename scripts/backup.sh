#!/usr/bin/env bash
# ==============================================================================
# PostgreSQL backup script for Automatizacion-Mesa-de-Ayuda-N8N
#
# Runs pg_dump from the postgres Docker container (project name: mesa_local).
# Saves timestamped SQL dumps to backups/ and keeps the last 7 daily backups.
#
# Usage:
#   bash scripts/backup.sh
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - The postgres container is running (docker compose up -d postgres)
#
# Exit codes:
#   0 — backup completed successfully
#   1 — error (container not running, dump failed, etc.)
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
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"

# ── Run pg_dump ──────────────────────────────────────────────────────────────
echo "Backing up PostgreSQL to: $BACKUP_FILE"

if ! docker exec "$CONTAINER_ID" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE" 2>/tmp/backup_error.log; then
    echo "ERROR: pg_dump failed."
    cat /tmp/backup_error.log
    rm -f /tmp/backup_error.log
    exit 1
fi

rm -f /tmp/backup_error.log 2>/dev/null || true

SIZE=$(du -h "$BACKUP_FILE" 2>/dev/null | cut -f1 || echo "unknown")
echo "Backup completed: $BACKUP_FILE ($SIZE)"

# ── Rotate: keep only the $RETENTION_COUNT most recent backups ────────────────
cd "$BACKUP_DIR"
BACKUP_FILES=($(ls -1t backup_*.sql 2>/dev/null || true))
TOTAL_BACKUPS=${#BACKUP_FILES[@]}

if [ "$TOTAL_BACKUPS" -gt "$RETENTION_COUNT" ]; then
    OLD_BACKUPS=("${BACKUP_FILES[@]:$RETENTION_COUNT}")
    echo "Rotating: removing ${#OLD_BACKUPS[@]} old backup(s)..."
    for old_file in "${OLD_BACKUPS[@]}"; do
        echo "  Deleting: $old_file"
        rm -f "$old_file"
    done
    echo "Rotation complete. Kept $RETENTION_COUNT most recent backups."
else
    echo "No rotation needed ($TOTAL_BACKUPS backups, retention=$RETENTION_COUNT)."
fi

echo "Done."
exit 0
