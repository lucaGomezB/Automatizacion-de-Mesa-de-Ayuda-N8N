#!/usr/bin/env bash
# ==============================================================================
# Test harness for scripts/up.sh preflight logic.
#
# Uses plain bash assertions so it runs anywhere without a bats dependency.
#
# Covered behavior:
#   - App/Backend/.env missing      -> non-zero exit, no secret value printed
#   - placeholder GEMINI_API_KEY    -> non-zero exit, variable named, no secret
#   - placeholder PSEUDONYMIZATION_ENCRYPTION_KEY -> non-zero exit, no secret
#   - empty required variable       -> non-zero exit, variable named
#   - valid values                  -> preflight passes, no secret value printed
#   - custom placeholder defined in .env.example is detected (triangulation)
#
# The harness never invokes docker. Failing cases exit during preflight; the
# passing case is exercised through the extracted check_env_file function so the
# harness does not try to build or start the stack.
#
# Usage:
#   bash scripts/tests/test_up_preflight.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
UP_SH="${REPO_ROOT}/scripts/up.sh"

FAILURES=0
ASSERTIONS=0

# Unique sentinel used to prove that secret values never reach stdout/stderr.
SECRET_SENTINEL="SUPER_SECRET_SENTINEL_9f3a2b"

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

if [ ! -f "$UP_SH" ]; then
    printf 'FAIL - scripts/up.sh not found at %s\n' "$UP_SH"
    exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─ Fixtures ─────────────────────────────────────────────────────────────────
EXAMPLE="${WORK}/env.example"
cat > "$EXAMPLE" <<'EOF'
# Template placeholder values
GEMINI_API_KEY=your-gemini-api-key-here
PSEUDONYMIZATION_ENCRYPTION_KEY=your-fernet-key-here
EOF

VALID="${WORK}/valid.env"
cat > "$VALID" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
EOF

PLACEHOLDER_GEMINI="${WORK}/placeholder-gemini.env"
cat > "$PLACEHOLDER_GEMINI" <<EOF
GEMINI_API_KEY=your-gemini-api-key-here
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
EOF

PLACEHOLDER_FERNET="${WORK}/placeholder-fernet.env"
cat > "$PLACEHOLDER_FERNET" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=your-fernet-key-here
EOF

EMPTY_GEMINI="${WORK}/empty-gemini.env"
cat > "$EMPTY_GEMINI" <<EOF
GEMINI_API_KEY=
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
EOF

MISSING="${WORK}/does-not-exist.env"

CUSTOM_EXAMPLE="${WORK}/custom.example"
cat > "$CUSTOM_EXAMPLE" <<'EOF'
GEMINI_API_KEY=custom-gemini-placeholder-xyz
PSEUDONYMIZATION_ENCRYPTION_KEY=custom-fernet-placeholder-xyz
EOF

CUSTOM_ENV="${WORK}/custom.env"
cp "$CUSTOM_EXAMPLE" "$CUSTOM_ENV"
CUSTOM_PLACEHOLDER="custom-gemini-placeholder-xyz"

QUOTED_VALID="${WORK}/quoted-valid.env"
cat > "$QUOTED_VALID" <<EOF
GEMINI_API_KEY="real-gemini-$SECRET_SENTINEL"
PSEUDONYMIZATION_ENCRYPTION_KEY='real-fernet-$SECRET_SENTINEL'
EOF

COMMENTED="${WORK}/commented.env"
cat > "$COMMENTED" <<EOF
# GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
EOF

# ── Helpers ─────────────────────────────────────────────────────────────────
# Runs the real script as a subprocess with the fixture overrides. Used for
# cases that fail during preflight (so docker is never reached).
run_script_subprocess() {
    UP_ENV_FILE="$1" UP_ENV_EXAMPLE="$2" bash "$UP_SH" 2>&1
}

# Sources the script and calls the extracted preflight function in a subshell
# with errexit disabled, so the check result is observable without exiting.
run_check_function() {
    (
        set +e
        # shellcheck disable=SC1090
        source "$UP_SH"
        set +e
        check_env_file "$1" "$2"
    ) 2>&1
}

assert_preflight_fails() {
    local env_file="$1" example_file="$2" label="$3" expected_token="$4"
    local out status
    if out="$(run_script_subprocess "$env_file" "$example_file")"; then
        status=0
    else
        status=$?
    fi
    assert_nonzero "$status" "${label}: exits non-zero"
    assert_contains "$out" "$expected_token" "${label}: names the offending prerequisite"
    assert_not_contains "$out" "$SECRET_SENTINEL" "${label}: never prints a secret value"
}

# ─ Tests ────────────────────────────────────────────────────────────────────
printf 'Preflight: missing .env\n'
assert_preflight_fails "$MISSING" "$EXAMPLE" "missing .env" ".env"

printf 'Preflight: placeholder secrets\n'
assert_preflight_fails "$PLACEHOLDER_GEMINI" "$EXAMPLE" "gemini placeholder" "GEMINI_API_KEY"
assert_preflight_fails "$PLACEHOLDER_FERNET" "$EXAMPLE" "fernet placeholder" "PSEUDONYMIZATION_ENCRYPTION_KEY"

printf 'Preflight: empty secret\n'
assert_preflight_fails "$EMPTY_GEMINI" "$EXAMPLE" "empty gemini key" "GEMINI_API_KEY"

printf 'Preflight: valid values pass\n'
out=""
status=0
if out="$(run_check_function "$VALID" "$EXAMPLE")"; then
    status=0
else
    status=$?
fi
assert_zero "$status" "valid env: preflight passes"
assert_not_contains "$out" "$SECRET_SENTINEL" "valid env: secret value never printed"

printf 'Preflight: template-driven placeholder detection\n'
status=0
if out="$(run_check_function "$CUSTOM_ENV" "$CUSTOM_EXAMPLE")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "custom template placeholder: detected as non-zero"
assert_not_contains "$out" "$CUSTOM_PLACEHOLDER" "custom template placeholder: value not printed"

printf 'Preflight: parser robustness\n'
status=0
if out="$(run_check_function "$QUOTED_VALID" "$EXAMPLE")"; then
    status=0
else
    status=$?
fi
assert_zero "$status" "quoted values: preflight passes"
assert_not_contains "$out" "$SECRET_SENTINEL" "quoted values: secret value never printed"

status=0
if out="$(run_check_function "$COMMENTED" "$EXAMPLE")"; then
    status=0
else
    status=$?
fi
assert_zero "$status" "commented placeholder line ignored: preflight passes"
assert_not_contains "$out" "$SECRET_SENTINEL" "commented line: secret value never printed"

printf '\n%s assertions, %s failure(s)\n' "$ASSERTIONS" "$FAILURES"
if [ "$FAILURES" -ne 0 ]; then
    exit 1
fi
printf 'All preflight tests passed.\n'
exit 0