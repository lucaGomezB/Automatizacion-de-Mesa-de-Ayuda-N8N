#!/usr/bin/env bash
# ==============================================================================
# One-command local bootstrap for Automatizacion-Mesa-de-Ayuda-N8N
#
# Runs the full happy path: environment preflight, TLS certificate generation
# when missing, stack startup, bounded health wait, and health verification.
#
# Usage:
#   bash scripts/up.sh
#
# Prerequisites:
#   - Docker Engine and Docker Compose v2 installed
#   - App/Backend/.env created from App/Backend/.env.example with real values
#   - OpenSSL available (used by openssl/generate-certs.sh)
#   - curl available (used for the HTTPS health checks)
#
# Exit codes:
#   0 — stack started, both health endpoints responded
#   1 — error (missing/placeholder env, certificate generation failed,
#       startup failed, health timeout, or health check failed)
#
# Test-only overrides (operators should not set these):
#   UP_ENV_FILE       — path to the .env file under verification
#   UP_ENV_EXAMPLE    — path to the template used for placeholder comparison
#   UP_HEALTH_TIMEOUT — health wait timeout in seconds (default: 600)
#   UP_HEALTH_INTERVAL— health poll interval in seconds (default: 5)
#   UP_COST_PREFLIGHT — path to the cost readiness checker (default: scripts/preflight/cost_readiness.py)
#   UP_PYTHON         — Python interpreter used for the cost preflight
#
# Operator bypass (deliberately loud, never silent):
#   UP_SKIP_COST_PREFLIGHT=1 — skip the cost readiness gate and print a warning
# ==============================================================================

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

ENV_FILE="${UP_ENV_FILE:-${REPO_ROOT}/App/Backend/.env}"
ENV_EXAMPLE="${UP_ENV_EXAMPLE:-${REPO_ROOT}/App/Backend/.env.example}"
CERT_FILE="${REPO_ROOT}/openssl/mesa.crt"
KEY_FILE="${REPO_ROOT}/openssl/mesa.key"
CERT_GENERATOR="${REPO_ROOT}/openssl/generate-certs.sh"
COST_PREFLIGHT_SCRIPT="${REPO_ROOT}/scripts/preflight/cost_readiness.py"
PREFLIGHT_REQUIREMENTS="scripts/preflight/requirements.txt"

HEALTH_TIMEOUT="${UP_HEALTH_TIMEOUT:-600}"
HEALTH_INTERVAL="${UP_HEALTH_INTERVAL:-5}"

# Services declared in docker-compose.yml (project name: mesa_local).
EXPECTED_SERVICE_COUNT=6

# Required secret variables. The values listed here are the placeholders from
# App/Backend/.env.example; the template file is also parsed at runtime so this
# remains a single named source of truth that tolerates template changes.
REQUIRED_SECRETS=("GEMINI_API_KEY" "PSEUDONYMIZATION_ENCRYPTION_KEY" "JWT_SECRET_KEY")
PLACEHOLDER_VALUES=(
    "your-gemini-api-key-here"
    "your-fernet-key-here"
    "your-jwt-secret-key-here"
    "your-key-here"
    "changeme"
)

# ── Logging ──────────────────────────────────────────────────────────────────
log_info() { printf '[up] %s\n' "$*"; }
log_error() { printf '[up] ERROR: %s\n' "$*" >&2; }
log_warn() { printf '[up] WARNING: %s\n' "$*" >&2; }

# ── .env parsing ─────────────────────────────────────────────────────────────
# Reads the last assignment of KEY=... from a dotenv-style file. Prints only the
# parsed value, never a log line. Returns 1 when the key is not present.
read_env_value() {
    local key="$1" file="$2"
    local line value
    line="$(grep -E "^[[:space:]]*${key}[[:space:]]*=" "$file" 2>/dev/null | tail -n 1 || true)"
    [ -z "$line" ] && return 1
    value="${line#*=}"
    value="${value%$'\r'}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    if [[ "$value" == \"*\" ]]; then value="${value:1:${#value}-2}"; fi
    if [[ "$value" == \'*\' ]]; then value="${value:1:${#value}-2}"; fi
    printf '%s' "$value"
}

# Prints the effective placeholder set: the named constant plus any non-empty
# placeholder values found in the template file, so a template change propagates
# automatically.
collect_placeholders() {
    local file="$1" key value
    printf '%s\n' "${PLACEHOLDER_VALUES[@]}"
    [ -f "$file" ] || return 0
    for key in "${REQUIRED_SECRETS[@]}"; do
        if value="$(read_env_value "$key" "$file")" && [ -n "$value" ]; then
            printf '%s\n' "$value"
        fi
    done
}

is_placeholder() {
    local value="$1" candidate
    shift
    for candidate in "$@"; do
        if [ "$value" = "$candidate" ]; then
            return 0
        fi
    done
    return 1
}

# Preflight: validates the environment file without ever printing values.
# Returns 0 when the file exists and both required secrets are real values.
check_env_file() {
    local env_file="$1"
    local example_file="${2:-$ENV_EXAMPLE}"
    local key value placeholder
    local -a placeholders=()

    if [ ! -f "$env_file" ]; then
        log_error "Missing environment file: ${env_file}"
        log_error "Create it from the template and fill in real values:"
        log_error "  cp App/Backend/.env.example App/Backend/.env"
        return 1
    fi

    while IFS= read -r placeholder; do
        [ -n "$placeholder" ] && placeholders+=("$placeholder")
    done < <(collect_placeholders "$example_file")

    for key in "${REQUIRED_SECRETS[@]}"; do
        if ! value="$(read_env_value "$key" "$env_file")"; then
            log_error "Missing required variable in ${env_file}: ${key}"
            log_error "Set ${key} to a real value before starting the stack."
            return 1
        fi
        if [ -z "$value" ]; then
            log_error "Empty required variable in ${env_file}: ${key}"
            log_error "Set ${key} to a real value before starting the stack."
            return 1
        fi
        if is_placeholder "$value" "${placeholders[@]}"; then
            log_error "Placeholder value detected for ${key} in ${env_file}"
            log_error "Replace the placeholder with a real value before starting the stack."
            return 1
        fi
    done

    return 0
}

# ── Cost readiness preflight ─────────────────────────────────────────────────
# Resolves the Python interpreter lazily (inside the function, never at source
# time) so `source up.sh` under `set -e` stays safe: UP_PYTHON -> python3 ->
# python.
detect_cost_preflight_python() {
    local candidate
    if [ -n "${UP_PYTHON:-}" ]; then
        candidate="$UP_PYTHON"
        if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
            printf '%s' "$candidate"
            return 0
        fi
        return 1
    fi
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

# Single source of truth for the actionable install hint, so every cost-gate
# failure points the operator at the same dependency file.
log_preflight_install_hint() {
    log_error "Install the preflight dependencies and retry:"
    log_error "  pip install -r ${PREFLIGHT_REQUIREMENTS}"
}

# Runs the static cost readiness preflight and returns non-zero when the gate
# must block startup. The checker output is printed verbatim because it already
# names the FAIL guards. UP_SKIP_COST_PREFLIGHT=1 is the only bypass and it is
# deliberately loud: it never skips silently.
check_cost_preflight() {
    local script python output status

    if [ "${UP_SKIP_COST_PREFLIGHT:-}" = "1" ]; then
        log_warn "UP_SKIP_COST_PREFLIGHT=1: COST READINESS PREFLIGHT SKIPPED."
        log_warn "The stack may start with broken cost guards. Unset the variable to re-enable the gate."
        return 0
    fi

    script="${UP_COST_PREFLIGHT:-$COST_PREFLIGHT_SCRIPT}"
    if [ ! -f "$script" ]; then
        log_error "Cost preflight script not found: ${script}"
        log_preflight_install_hint
        return 1
    fi

    if ! python="$(detect_cost_preflight_python)"; then
        log_error "No Python interpreter found for the cost preflight (tried UP_PYTHON, python3, python)."
        log_preflight_install_hint
        return 1
    fi

    if output="$("$python" "$script" 2>&1)"; then
        status=0
    else
        status=$?
    fi
    printf '%s\n' "$output"

    if [ "$status" -ne 0 ]; then
        log_error "Cost readiness preflight FAILED (exit ${status}). The stack was NOT started."
        log_error "Resolve the FAIL guards above before starting paid services."
        log_error "If a dependency is missing, install: pip install -r ${PREFLIGHT_REQUIREMENTS}"
        return 1
    fi

    return 0
}

# ── TLS certificates ─────────────────────────────────────────────────────────
ensure_certificates() {
    if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
        log_info "TLS certificates already present; skipping generation."
        return 0
    fi

    log_info "TLS certificates missing; generating..."
    if [ ! -f "$CERT_GENERATOR" ]; then
        log_error "Certificate generator not found: openssl/generate-certs.sh"
        return 1
    fi
    if ! bash "$CERT_GENERATOR"; then
        log_error "TLS certificate generation failed. Aborting."
        return 1
    fi
}

# ── Stack startup ────────────────────────────────────────────────────────────
# The compose project name is fixed to mesa_local in docker-compose.yml, so the
# -p flag is intentionally omitted.
start_stack() {
    log_info "Starting stack: docker compose up -d --build"
    if ! docker compose up -d --build; then
        log_error "docker compose up failed. Aborting."
        return 1
    fi
}

services_are_healthy() {
    local output line service state health seen=0
    output="$(docker compose ps --format '{{.Service}} {{.State}} {{.Health}}' 2>/dev/null)" || return 1
    [ -z "$output" ] && return 1

    while IFS=' ' read -r service state health; do
        [ -z "$service" ] && continue
        seen=$((seen + 1))
        if [ "$state" != "running" ]; then
            return 1
        fi
        if [ -n "$health" ] && [ "$health" != "healthy" ]; then
            return 1
        fi
    done <<< "$output"

    [ "$seen" -ge "$EXPECTED_SERVICE_COUNT" ]
}

wait_for_healthy() {
    local waited=0
    log_info "Waiting up to ${HEALTH_TIMEOUT}s for services to become healthy..."
    while [ "$waited" -lt "$HEALTH_TIMEOUT" ]; do
        if services_are_healthy; then
            log_info "All services are running and healthy."
            return 0
        fi
        sleep "$HEALTH_INTERVAL"
        waited=$((waited + HEALTH_INTERVAL))
    done

    log_error "Timeout after ${HEALTH_TIMEOUT}s: services did not become healthy."
    log_error "Current status:"
    docker compose ps || true
    return 1
}

# ─ Health verification and output ───────────────────────────────────────────
verify_health() {
    local base="https://localhost" path
    for path in "/api/v1/health" "/api/v1/health/db"; do
        if ! curl -k -fsS "${base}${path}" >/dev/null; then
            log_error "Health check failed: ${base}${path}"
            return 1
        fi
        log_info "Health OK: ${base}${path}"
    done
}

print_access_info() {
    printf '\n'
    log_info "Stack is up and healthy."
    printf 'Access URLs:\n'
    printf '  Web UI : https://localhost/\n'
    printf '  N8N    : http://localhost:5678  (admin / n8n_local_dev, default local)\n'
    printf '\n'
    printf 'Manual N8N setup (required, not automated):\n'
    printf '  1. Open N8N and import n8n/workflow.json via Workflows -> Import from file.\n'
    printf '  2. Configure the Outlook, Twilio, and Gemini credentials in N8N.\n'
    printf '  3. Activate the workflow.\n'
    printf '\n'
    printf 'Note: the workflow is NOT imported automatically; do it manually.\n'
}

# ── Entry point ──────────────────────────────────────────────────────────────
main() {
    check_env_file "$ENV_FILE" "$ENV_EXAMPLE" || exit 1
    check_cost_preflight || exit 1
    ensure_certificates || exit 1
    start_stack || exit 1
    wait_for_healthy || exit 1
    verify_health || exit 1
    print_access_info
}

# Only run when executed directly; sourcing (used by the test harness) must not
# start docker or trigger any side effect.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi