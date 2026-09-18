<#
.SYNOPSIS
    One-command local bootstrap for Automatizacion-Mesa-de-Ayuda-N8N (Windows/PowerShell)

.DESCRIPTION
    Runs the full happy path: environment preflight, TLS certificate generation
    when missing, stack startup, bounded health wait, and health verification.

.PARAMETER None
    All configuration is defined at the top of this script.

.EXAMPLE
    .\scripts\up.ps1

.NOTES
    Prerequisites:
      - Docker Desktop installed and running (with the Compose v2 plugin)
      - App\Backend\.env created from App\Backend\.env.example with real values
      - OpenSSL available (used by openssl\generate-certs.ps1)
      - curl.exe available (used for the HTTPS health checks)

    Exit codes:
      0 - stack started, both health endpoints responded
      1 - error (missing/placeholder env, certificate generation failed,
          startup failed, health timeout, or health check failed)

    Test-only overrides (operators should not set these):
      UP_ENV_FILE        - path to the .env file under verification
      UP_ENV_EXAMPLE     - path to the template used for placeholder comparison
      UP_HEALTH_TIMEOUT  - health wait timeout in seconds (default: 600)
      UP_HEALTH_INTERVAL - health poll interval in seconds (default: 5)
#>

#requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Configuration -----------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

if ($env:UP_ENV_FILE) { $EnvFile = $env:UP_ENV_FILE } else { $EnvFile = Join-Path $RepoRoot "App/Backend/.env" }
if ($env:UP_ENV_EXAMPLE) { $EnvExample = $env:UP_ENV_EXAMPLE } else { $EnvExample = Join-Path $RepoRoot "App/Backend/.env.example" }
$CertFile = Join-Path $RepoRoot "openssl/mesa.crt"
$KeyFile = Join-Path $RepoRoot "openssl/mesa.key"
$CertGenerator = Join-Path $RepoRoot "openssl/generate-certs.ps1"

if ($env:UP_HEALTH_TIMEOUT) { $HealthTimeout = [int]$env:UP_HEALTH_TIMEOUT } else { $HealthTimeout = 600 }
if ($env:UP_HEALTH_INTERVAL) { $HealthInterval = [int]$env:UP_HEALTH_INTERVAL } else { $HealthInterval = 5 }

# Services declared in docker-compose.yml (project name: mesa_local).
$ExpectedServiceCount = 6

# Required secret variables. The values listed here are the placeholders from
# App\Backend\.env.example; the template file is also parsed at runtime so this
# remains a single named source of truth that tolerates template changes.
$RequiredSecrets = @("GEMINI_API_KEY", "PSEUDONYMIZATION_ENCRYPTION_KEY")
$PlaceholderValues = @(
    "your-gemini-api-key-here",
    "your-fernet-key-here",
    "your-key-here",
    "changeme"
)

# -- Logging -----------------------------------------------------------------
function Write-Info {
    param([string]$Message)
    Write-Host "[up] $Message"
}

function Write-Err {
    param([string]$Message)
    Write-Host "[up] ERROR: $Message" -ForegroundColor Red
}

# -- .env parsing ------------------------------------------------------------
# Reads the last assignment of KEY=... from a dotenv-style file. Returns $null
# when the key is absent, or the parsed value (possibly empty) otherwise. Never
# logs a value.
function Read-EnvValue {
    param([string]$Key, [string]$File)
    if (-not (Test-Path -LiteralPath $File)) { return $null }
    $line = $null
    foreach ($candidate in Get-Content -LiteralPath $File) {
        if ($candidate -match "^\s*$([regex]::Escape($Key))\s*=") {
            $line = $candidate
        }
    }
    if ($null -eq $line) { return $null }
    $value = $line.Substring($line.IndexOf("=") + 1).Trim()
    if ($value.Length -ge 2) {
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
    }
    return $value
}

# Returns the effective placeholder set: the named constants plus any non-empty
# placeholder values found in the template file.
function Get-Placeholders {
    param([string]$ExampleFile)
    $result = New-Object System.Collections.Generic.List[string]
    foreach ($placeholder in $PlaceholderValues) { $result.Add($placeholder) }
    if (Test-Path -LiteralPath $ExampleFile) {
        foreach ($key in $RequiredSecrets) {
            $value = Read-EnvValue -Key $key -File $ExampleFile
            if ($null -ne $value -and $value -ne "") { $result.Add($value) }
        }
    }
    return $result
}

# Preflight: validates the environment file without ever printing values.
function Test-EnvPreflight {
    param([string]$EnvPath, [string]$ExamplePath)

    if (-not (Test-Path -LiteralPath $EnvPath)) {
        Write-Err "Missing environment file: $EnvPath"
        Write-Err "Create it from the template and fill in real values:"
        Write-Err "  Copy-Item App\Backend\.env.example App\Backend\.env"
        return $false
    }

    $placeholders = Get-Placeholders -ExampleFile $ExamplePath

    foreach ($key in $RequiredSecrets) {
        $value = Read-EnvValue -Key $key -File $EnvPath
        if ($null -eq $value) {
            Write-Err "Missing required variable in ${EnvPath}: $key"
            Write-Err "Set $key to a real value before starting the stack."
            return $false
        }
        if ($value -eq "") {
            Write-Err "Empty required variable in ${EnvPath}: $key"
            Write-Err "Set $key to a real value before starting the stack."
            return $false
        }
        if ($placeholders -contains $value) {
            Write-Err "Placeholder value detected for $key in ${EnvPath}"
            Write-Err "Replace the placeholder with a real value before starting the stack."
            return $false
        }
    }

    return $true
}

# -- TLS certificates --------------------------------------------------------
function Invoke-EnsureCertificates {
    if ((Test-Path -LiteralPath $CertFile) -and (Test-Path -LiteralPath $KeyFile)) {
        Write-Info "TLS certificates already present; skipping generation."
        return $true
    }

    Write-Info "TLS certificates missing; generating..."
    if (-not (Test-Path -LiteralPath $CertGenerator)) {
        Write-Err "Certificate generator not found: openssl\generate-certs.ps1"
        return $false
    }

    & $CertGenerator
    if (-not ((Test-Path -LiteralPath $CertFile) -and (Test-Path -LiteralPath $KeyFile))) {
        Write-Err "TLS certificate generation failed. Aborting."
        return $false
    }

    return $true
}

# -- Stack startup -----------------------------------------------------------
# The compose project name is fixed to mesa_local in docker-compose.yml, so the
# -p flag is intentionally omitted.
function Invoke-StartStack {
    Write-Info "Starting stack: docker compose up -d --build"
    docker compose up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Err "docker compose up failed. Aborting."
        return $false
    }
    return $true
}

function Test-ServicesHealthy {
    $output = docker compose ps --format "{{.Service}} {{.State}} {{.Health}}" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $output) { return $false }

    $seen = 0
    foreach ($rawLine in $output) {
        $line = $rawLine.Trim()
        if ($line -eq "") { continue }
        $parts = $line -split '\s+'
        $state = if ($parts.Count -gt 1) { $parts[1] } else { "" }
        $health = if ($parts.Count -gt 2) { $parts[2] } else { "" }
        $seen++
        if ($state -ne "running") { return $false }
        if ($health -ne "" -and $health -ne "healthy") { return $false }
    }

    return ($seen -ge $ExpectedServiceCount)
}

function Wait-ForHealthy {
    $waited = 0
    Write-Info "Waiting up to ${HealthTimeout}s for services to become healthy..."
    while ($waited -lt $HealthTimeout) {
        if (Test-ServicesHealthy) {
            Write-Info "All services are running and healthy."
            return $true
        }
        Start-Sleep -Seconds $HealthInterval
        $waited += $HealthInterval
    }

    Write-Err "Timeout after ${HealthTimeout}s: services did not become healthy."
    Write-Err "Current status:"
    docker compose ps
    return $false
}

# -- Health verification and output ------------------------------------------
function Invoke-VerifyHealth {
    $base = "https://localhost"
    foreach ($path in @("/api/v1/health", "/api/v1/health/db")) {
        curl.exe -k -fsS "$base$path" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Health check failed: $base$path"
            return $false
        }
        Write-Info "Health OK: $base$path"
    }
    return $true
}

function Write-AccessInfo {
    Write-Host ""
    Write-Info "Stack is up and healthy."
    Write-Host "Access URLs:"
    Write-Host "  Web UI : https://localhost/"
    Write-Host "  N8N    : http://localhost:5678  (admin / n8n_local_dev, default local)"
    Write-Host ""
    Write-Host "Manual N8N setup (required, not automated):"
    Write-Host "  1. Open N8N and import n8n/workflow.json via Workflows -> Import from file."
    Write-Host "  2. Configure the Outlook, Twilio, and Gemini credentials in N8N."
    Write-Host "  3. Activate the workflow."
    Write-Host ""
    Write-Host "Note: the workflow is NOT imported automatically; do it manually."
}

# -- Entry point -------------------------------------------------------------
if (-not (Test-EnvPreflight -EnvPath $EnvFile -ExamplePath $EnvExample)) { exit 1 }
if (-not (Invoke-EnsureCertificates)) { exit 1 }
if (-not (Invoke-StartStack)) { exit 1 }
if (-not (Wait-ForHealthy)) { exit 1 }
if (-not (Invoke-VerifyHealth)) { exit 1 }

Write-AccessInfo
exit 0