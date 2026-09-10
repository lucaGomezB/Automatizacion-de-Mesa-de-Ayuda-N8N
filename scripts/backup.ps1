<#
.SYNOPSIS
    PostgreSQL backup script for Automatizacion-Mesa-de-Ayuda-N8N (Windows/PowerShell)

.DESCRIPTION
    Runs pg_dump from the postgres Docker container (project name: mesa_local).
    Saves timestamped SQL dumps to backups/ and keeps the last 7 daily backups.

.PARAMETER None
    All configuration is hardcoded at the top of this script.

.EXAMPLE
    .\scripts\backup.ps1

.NOTES
    Prerequisites:
      - Docker Desktop installed and running
      - The postgres container is running (docker compose up -d postgres)

    Exit codes:
      0 — backup completed successfully
      1 — error (container not running, dump failed, etc.)
#>

#requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Configuration ────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackupDir = Join-Path $RepoRoot "backups"
$RetentionCount = 7

$ComposeProjectName = "mesa_local"
$ServiceName = "postgres"
$DbUser = "mesa"
$DbName = "mesa_de_ayuda"

# ── Idempotent: ensure backup directory exists ──────────────────────────────
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "Created backup directory: $BackupDir"
}

# ── Verify container is running ──────────────────────────────────────────────
$ContainerId = $null
$CandidateNames = @(
    "${ComposeProjectName}-${ServiceName}-1",
    "${ComposeProjectName}_${ServiceName}_1",
    "mesa_local-postgres-1",
    "mesa_local_postgres_1"
)

foreach ($candidate in $CandidateNames) {
    $state = docker inspect --format '{{.State.Running}}' $candidate 2>$null
    if ($LASTEXITCODE -eq 0 -and $state -eq "true") {
        $ContainerId = $candidate
        break
    }
}

if (-not $ContainerId) {
    Write-Host "ERROR: PostgreSQL container not running." -ForegroundColor Red
    Write-Host "Ensure the stack is up:  docker compose up -d postgres"
    exit 1
}

Write-Host "Found running container: $ContainerId"

# ── Generate timestamped filename ────────────────────────────────────────────
$Timestamp = Get-Date -Format "yyyy-MM-dd"
$BackupFile = Join-Path $BackupDir "backup_${Timestamp}.sql"

# ── Run pg_dump ──────────────────────────────────────────────────────────────
Write-Host "Backing up PostgreSQL to: $BackupFile"

$tempErrorFile = Join-Path $env:TEMP "backup_error_$(Get-Date -Format 'yyyyMMddHHmmss').txt"

try {
    docker exec $ContainerId pg_dump -U $DbUser $DbName 2>$tempErrorFile | Out-File -FilePath $BackupFile -Encoding utf8NoBOM

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pg_dump failed." -ForegroundColor Red
        if (Test-Path $tempErrorFile) {
            Get-Content $tempErrorFile | Write-Host -ForegroundColor Red
            Remove-Item $tempErrorFile -Force
        }
        exit 1
    }
} finally {
    if (Test-Path $tempErrorFile) {
        Remove-Item $tempErrorFile -Force -ErrorAction SilentlyContinue
    }
}

$backupSize = (Get-Item $BackupFile).Length
$backupSizeKB = [math]::Round($backupSize / 1KB, 2)
Write-Host "Backup completed: $BackupFile (${backupSizeKB} KB)"

# ── Rotate: keep only the $RetentionCount most recent backups ────────────────
$existingBackups = Get-ChildItem -Path $BackupDir -Filter "backup_*.sql" |
    Sort-Object LastWriteTime -Descending

$totalBackups = $existingBackups.Count
Write-Host "Found $totalBackups backup(s). Retention: $RetentionCount."

if ($totalBackups -gt $RetentionCount) {
    $oldBackups = $existingBackups | Select-Object -Skip $RetentionCount
    Write-Host "Rotating: removing $($oldBackups.Count) old backup(s)..."
    foreach ($oldFile in $oldBackups) {
        Write-Host "  Deleting: $($oldFile.Name)"
        Remove-Item $oldFile.FullName -Force
    }
    Write-Host "Rotation complete. Kept $RetentionCount most recent backups."
} else {
    Write-Host "No rotation needed."
}

Write-Host "Done."
exit 0
