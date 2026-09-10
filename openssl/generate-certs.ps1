<#
.SYNOPSIS
    Generate self-signed TLS certificate for local development (Windows).

.DESCRIPTION
    Detects OpenSSL from common installation paths (Git for Windows, Chocolatey,
    standalone OpenSSL), generates a self-signed X.509 certificate with SANs for
    localhost, 127.0.0.1, and mesa.local, and writes the output to:
      openssl\mesa.crt  (certificate, 365 days, RSA 2048-bit)
      openssl\mesa.key  (private key)

    This script is idempotent: re-running overwrites existing certificates.

.EXAMPLE
    .\openssl\generate-certs.ps1
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = $ScriptDir

# Ensure output directory exists
if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Locate OpenSSL executable
$opensslPath = $null
$searchPaths = @(
    "openssl",
    "C:\Program Files\Git\usr\bin\openssl.exe",
    "C:\Program Files\Git\mingw64\bin\openssl.exe",
    "C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
    "C:\Program Files (x86)\GnuWin32\bin\openssl.exe",
    "C:\tools\openssl\bin\openssl.exe"
)

foreach ($candidate in $searchPaths) {
    # Try as a command first (e.g., if it is in PATH)
    try {
        $cmd = Get-Command $candidate -ErrorAction Stop
        $opensslPath = $cmd.Source
        break
    }
    catch {
        # Not in PATH — try as a literal file path
        if (Test-Path -LiteralPath $candidate) {
            $opensslPath = $candidate
            break
        }
    }
}

if (-not $opensslPath) {
    Write-Host "ERROR: OpenSSL was not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install OpenSSL via one of:" -ForegroundColor Yellow
    Write-Host "  1. Git for Windows (recommended — includes OpenSSL in Git Bash)"
    Write-Host "     https://git-scm.com/download/win"
    Write-Host "  2. Chocolatey:  choco install openssl"
    Write-Host "  3. Standalone:   https://slproweb.com/products/Win32OpenSSL.html"
    Write-Host ""
    Write-Host "After installing, verify with:  openssl version"
    exit 1
}

Write-Host "Using OpenSSL: $opensslPath" -ForegroundColor Cyan
$opensslVersion = & $opensslPath version 2>&1
Write-Host "Version: $opensslVersion"

# Build a temporary OpenSSL config with SANs
$configContent = @"
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = localhost

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = localhost
DNS.2 = mesa.local
IP.1 = 127.0.0.1
"@

$configPath = Join-Path $env:TEMP "openssl-mesa-config-$PID.cnf"
$configContent | Set-Content -LiteralPath $configPath -Encoding ASCII

$certPath = Join-Path $OutputDir "mesa.crt"
$keyPath  = Join-Path $OutputDir "mesa.key"

try {
    Write-Host "Generating self-signed TLS certificate (RSA 2048-bit, valid for 365 days)..."

    # Use the call operator to handle paths with spaces in the executable
    $process = Start-Process -FilePath $opensslPath -ArgumentList @(
        "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048",
        "-keyout", $keyPath,
        "-out", $certPath,
        "-config", $configPath,
        "-extensions", "v3_req"
    ) -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -ne 0) {
        Write-Host "ERROR: OpenSSL exited with code $($process.ExitCode)" -ForegroundColor Red
        exit $process.ExitCode
    }

    Write-Host ""
    Write-Host "Certificate generated successfully." -ForegroundColor Green
    Write-Host "  Certificate : $certPath"
    Write-Host "  Private key : $keyPath"
    Write-Host ""
    Write-Host "You can verify with:"
    Write-Host "  openssl x509 -in '$certPath' -text -noout | Select-Object -First 20"
}
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
finally {
    Remove-Item -LiteralPath $configPath -Force -ErrorAction SilentlyContinue
}
