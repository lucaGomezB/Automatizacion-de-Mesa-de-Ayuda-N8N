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
#   - missing/empty/placeholder JWT_SECRET_KEY -> non-zero exit, variable named
#   - empty required variable       -> non-zero exit, variable named
#   - valid values                  -> preflight passes, no secret value printed
#   - custom placeholder defined in .env.example is detected (triangulation)
#   - cost readiness gate: a failing preflight aborts before Docker; a passing
#     preflight continues; UP_SKIP_COST_PREFLIGHT=1 skips it with a loud warning
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
JWT_SECRET_KEY=your-jwt-secret-key-here
EOF

VALID="${WORK}/valid.env"
cat > "$VALID" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=real-jwt-$SECRET_SENTINEL
EOF

PLACEHOLDER_GEMINI="${WORK}/placeholder-gemini.env"
cat > "$PLACEHOLDER_GEMINI" <<EOF
GEMINI_API_KEY=your-gemini-api-key-here
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=real-jwt-$SECRET_SENTINEL
EOF

PLACEHOLDER_FERNET="${WORK}/placeholder-fernet.env"
cat > "$PLACEHOLDER_FERNET" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET_KEY=real-jwt-$SECRET_SENTINEL
EOF

EMPTY_GEMINI="${WORK}/empty-gemini.env"
cat > "$EMPTY_GEMINI" <<EOF
GEMINI_API_KEY=
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=real-jwt-$SECRET_SENTINEL
EOF

MISSING_JWT="${WORK}/missing-jwt.env"
cat > "$MISSING_JWT" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
EOF

EMPTY_JWT="${WORK}/empty-jwt.env"
cat > "$EMPTY_JWT" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=
EOF

PLACEHOLDER_JWT="${WORK}/placeholder-jwt.env"
cat > "$PLACEHOLDER_JWT" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=your-jwt-secret-key-here
EOF

# Template without the JWT placeholder: proves the static placeholder list still
# catches it when the template is unavailable or has been changed.
NO_JWT_EXAMPLE="${WORK}/no-jwt.example"
cat > "$NO_JWT_EXAMPLE" <<'EOF'
GEMINI_API_KEY=your-gemini-api-key-here
PSEUDONYMIZATION_ENCRYPTION_KEY=your-fernet-key-here
EOF

MISSING="${WORK}/does-not-exist.env"

CUSTOM_EXAMPLE="${WORK}/custom.example"
cat > "$CUSTOM_EXAMPLE" <<'EOF'
GEMINI_API_KEY=custom-gemini-placeholder-xyz
PSEUDONYMIZATION_ENCRYPTION_KEY=custom-fernet-placeholder-xyz
JWT_SECRET_KEY=custom-jwt-placeholder-xyz
EOF

CUSTOM_ENV="${WORK}/custom.env"
cp "$CUSTOM_EXAMPLE" "$CUSTOM_ENV"
CUSTOM_PLACEHOLDER="custom-gemini-placeholder-xyz"

# Template where ONLY the JWT placeholder is custom, so the JWT path of the
# template-driven detection is exercised in isolation.
CUSTOM_JWT_EXAMPLE="${WORK}/custom-jwt.example"
cat > "$CUSTOM_JWT_EXAMPLE" <<'EOF'
GEMINI_API_KEY=your-gemini-api-key-here
PSEUDONYMIZATION_ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET_KEY=custom-jwt-placeholder-xyz
EOF

CUSTOM_JWT_ENV="${WORK}/custom-jwt.env"
cat > "$CUSTOM_JWT_ENV" <<EOF
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=custom-jwt-placeholder-xyz
EOF

CUSTOM_JWT_PLACEHOLDER="custom-jwt-placeholder-xyz"

QUOTED_VALID="${WORK}/quoted-valid.env"
cat > "$QUOTED_VALID" <<EOF
GEMINI_API_KEY="real-gemini-$SECRET_SENTINEL"
PSEUDONYMIZATION_ENCRYPTION_KEY='real-fernet-$SECRET_SENTINEL'
JWT_SECRET_KEY="real-jwt-$SECRET_SENTINEL"
EOF

COMMENTED="${WORK}/commented.env"
cat > "$COMMENTED" <<EOF
# GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_API_KEY=real-gemini-$SECRET_SENTINEL
PSEUDONYMIZATION_ENCRYPTION_KEY=real-fernet-$SECRET_SENTINEL
JWT_SECRET_KEY=real-jwt-$SECRET_SENTINEL
EOF

# ─ Cost readiness gate fixtures ─────────────────────────────────────────────
# Stubs injected through UP_COST_PREFLIGHT (the interpreter override is unused
# here because the stubs are real Python scripts).
STUB_FAIL="${WORK}/stub_fail.py"
cat > "$STUB_FAIL" <<'EOF'
import sys

print("[FAIL] workflow: AI Agent declara tope de iteraciones (options.maxIterations)")
print("RESULT: 0/1 guardas en PASS (1 en FAIL). Preflight RED.")
sys.exit(1)
EOF

STUB_PASS="${WORK}/stub_pass.py"
cat > "$STUB_PASS" <<'EOF'
import sys

print("[PASS] workflow: AI Agent declara tope de iteraciones (options.maxIterations)")
print("RESULT: 1/1 guardas en PASS. Preflight GREEN.")
sys.exit(0)
EOF

# Fake docker on PATH: proves the gate aborts before any Docker side effect.
FAKE_BIN="${WORK}/fake-bin"
mkdir -p "$FAKE_BIN"
DOCKER_SENTINEL="${WORK}/docker-called.sentinel"
cat > "$FAKE_BIN/docker" <<'EOF'
#!/usr/bin/env bash
printf 'docker invoked\n' >> "${DOCKER_SENTINEL}"
exit 0
EOF
chmod +x "$FAKE_BIN/docker"

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

# Sources the script and calls the cost gate in a subshell. Overrides:
#   $1 = UP_COST_PREFLIGHT (script path), $2 = UP_PYTHON, $3 = UP_SKIP_COST_PREFLIGHT
run_cost_preflight_function() {
    (
        set +e
        export UP_COST_PREFLIGHT="${1-}"
        export UP_PYTHON="${2-}"
        export UP_SKIP_COST_PREFLIGHT="${3-}"
        # shellcheck disable=SC1090
        source "$UP_SH"
        set +e
        check_cost_preflight
    ) 2>&1
}

# Runs the real script as a subprocess with a fake docker on PATH and the cost
# gate overridden by a stub. Used to prove the failing gate aborts before Docker.
run_script_subprocess_with_cost() {
    PATH="$FAKE_BIN:$PATH" \
        DOCKER_SENTINEL="$DOCKER_SENTINEL" \
        UP_ENV_FILE="$1" \
        UP_ENV_EXAMPLE="$2" \
        UP_COST_PREFLIGHT="$3" \
        UP_HEALTH_TIMEOUT=1 \
        UP_HEALTH_INTERVAL=1 \
        bash "$UP_SH" 2>&1
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

# Same contract as assert_preflight_fails but exercises check_env_file through
# `source` instead of a subprocess, so cases that would otherwise proceed past
# the env preflight (and touch Docker) never reach docker.
assert_check_fails() {
    local env_file="$1" example_file="$2" label="$3" expected_token="$4"
    local out status
    if out="$(run_check_function "$env_file" "$example_file")"; then
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

printf 'Preflight: JWT_SECRET_KEY absent\n'
assert_check_fails "$MISSING_JWT" "$EXAMPLE" "missing jwt key" "JWT_SECRET_KEY"

printf 'Preflight: JWT_SECRET_KEY empty\n'
assert_check_fails "$EMPTY_JWT" "$EXAMPLE" "empty jwt key" "JWT_SECRET_KEY"

printf 'Preflight: JWT_SECRET_KEY placeholder\n'
assert_check_fails "$PLACEHOLDER_JWT" "$EXAMPLE" "jwt placeholder" "JWT_SECRET_KEY"

printf 'Preflight: JWT static placeholder backup (template lacks JWT)\n'
assert_check_fails "$PLACEHOLDER_JWT" "$NO_JWT_EXAMPLE" "jwt static placeholder" "JWT_SECRET_KEY"

printf 'Preflight: JWT placeholder from custom template\n'
out=""
status=0
if out="$(run_check_function "$CUSTOM_JWT_ENV" "$CUSTOM_JWT_EXAMPLE")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "custom jwt template placeholder: detected as non-zero"
assert_contains "$out" "JWT_SECRET_KEY" "custom jwt template placeholder: names JWT_SECRET_KEY"
assert_not_contains "$out" "$CUSTOM_JWT_PLACEHOLDER" "custom jwt template placeholder: value not printed"

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

# ─ Cost readiness gate ──────────────────────────────────────────────────────
printf 'Cost gate: failing preflight aborts before Docker\n'
rm -f "$DOCKER_SENTINEL"
out=""
status=0
if out="$(run_script_subprocess_with_cost "$VALID" "$EXAMPLE" "$STUB_FAIL")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "cost gate fail: up.sh exits non-zero"
assert_contains "$out" "FAIL" "cost gate fail: prints the preflight summary"
assert_contains "$out" "AI Agent declara tope de iteraciones" "cost gate fail: names the failing guard"
assert_not_contains "$out" "Starting stack" "cost gate fail: never reaches start_stack"
if [ -f "$DOCKER_SENTINEL" ]; then
    fail "cost gate fail: docker was not invoked"
else
    pass "cost gate fail: docker was not invoked"
fi

printf 'Cost gate: passing preflight continues\n'
out=""
status=0
if out="$(run_cost_preflight_function "$STUB_PASS")"; then
    status=0
else
    status=$?
fi
assert_zero "$status" "cost gate pass: check_cost_preflight returns 0"
assert_contains "$out" "Preflight GREEN" "cost gate pass: prints the preflight summary"

printf 'Cost gate: missing preflight script\n'
out=""
status=0
if out="$(run_cost_preflight_function "${WORK}/does-not-exist.py")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "missing preflight script: returns non-zero"
assert_contains "$out" "does-not-exist.py" "missing preflight script: names the path"
assert_contains "$out" "requirements.txt" "missing preflight script: actionable message"

printf 'Cost gate: invalid interpreter\n'
out=""
status=0
if out="$(run_cost_preflight_function "$STUB_PASS" "/nonexistent/python")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "invalid interpreter: returns non-zero"
assert_contains "$out" "Python interpreter" "invalid interpreter: actionable message"
assert_contains "$out" "requirements.txt" "invalid interpreter: actionable dependency hint"

printf 'Cost gate: operator bypass is loud\n'
out=""
status=0
if out="$(run_cost_preflight_function "$STUB_FAIL" "" "1")"; then
    status=0
else
    status=$?
fi
assert_zero "$status" "bypass: check_cost_preflight returns 0"
assert_contains "$out" "WARNING" "bypass: prints a loud warning"
assert_contains "$out" "UP_SKIP_COST_PREFLIGHT" "bypass: names the variable"
assert_not_contains "$out" "Preflight RED" "bypass: does not run the preflight"

printf 'Cost gate: bypass only honours the value 1\n'
out=""
status=0
if out="$(run_cost_preflight_function "$STUB_FAIL" "" "0")"; then
    status=0
else
    status=$?
fi
assert_nonzero "$status" "bypass=0: the gate still runs and fails"
assert_contains "$out" "Preflight RED" "bypass=0: the preflight output is printed"

# ─ Windows parity (structural) ──────────────────────────────────────────────
# No pwsh is available in this environment, so up.ps1 is verified structurally:
# the required secret, the placeholder, the gate function, the operator bypass
# and the invocation order (before certificates) must all be present.
UP_PS1="${REPO_ROOT}/scripts/up.ps1"
printf 'Windows parity: up.ps1 structure\n'
if [ -f "$UP_PS1" ]; then
    pass "up.ps1 exists"
else
    fail "up.ps1 exists"
fi
ps1_content="$(<"$UP_PS1")"
assert_contains "$ps1_content" "JWT_SECRET_KEY" "up.ps1 references JWT_SECRET_KEY"
assert_contains "$ps1_content" "your-jwt-secret-key-here" "up.ps1 lists the JWT placeholder"
assert_contains "$ps1_content" "Invoke-CostPreflight" "up.ps1 defines the cost gate"
assert_contains "$ps1_content" "UP_SKIP_COST_PREFLIGHT" "up.ps1 supports the operator bypass"

required_line="$(grep -n -F '$RequiredSecrets' "$UP_PS1" | head -n 1 | cut -d: -f1)"
if [ -n "$required_line" ] && sed -n "${required_line}p" "$UP_PS1" | grep -q -F "JWT_SECRET_KEY"; then
    pass "up.ps1 declares JWT_SECRET_KEY in \$RequiredSecrets"
else
    fail "up.ps1 declares JWT_SECRET_KEY in \$RequiredSecrets"
fi

gate_line="$(grep -n -F 'if (-not (Invoke-CostPreflight))' "$UP_PS1" | head -n 1 | cut -d: -f1)"
cert_line="$(grep -n -F 'if (-not (Invoke-EnsureCertificates))' "$UP_PS1" | head -n 1 | cut -d: -f1)"
if [ -n "$gate_line" ] && [ -n "$cert_line" ] && [ "$gate_line" -lt "$cert_line" ]; then
    pass "up.ps1 invokes the cost gate before certificates"
else
    fail "up.ps1 invokes the cost gate before certificates (gate=${gate_line:-none} cert=${cert_line:-none})"
fi

printf '\n%s assertions, %s failure(s)\n' "$ASSERTIONS" "$FAILURES"
if [ "$FAILURES" -ne 0 ]; then
    exit 1
fi
printf 'All preflight tests passed.\n'
exit 0