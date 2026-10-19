#!/usr/bin/env bash
# ==============================================================================
# Test harness for the frontend pinning decision (c-64, task 4.4).
#
# Decision (design D6): `package.json` keeps caret (`^`) ranges and the effective
# tree is frozen by the tracked `package-lock.json`; CI installs with `npm ci`,
# which is lockfile-exact. This harness verifies that the mechanism the decision
# relies on is actually in place.
#
# Covered behavior:
#   - App/Frontend/package.json exists and uses `^` ranges
#   - App/Frontend/package-lock.json exists and is tracked by git
#   - .github/workflows/ci.yml installs the frontend with `npm ci`
#   - the workflow does not fall back to a non-lockfile install
#
# Usage:
#   bash scripts/tests/test_frontend_pinning.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed
#
# Note: this harness is OFFLINE.
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
PACKAGE_JSON="${REPO_ROOT}/App/Frontend/package.json"
PACKAGE_LOCK="${REPO_ROOT}/App/Frontend/package-lock.json"
CI="${REPO_ROOT}/.github/workflows/ci.yml"

python3 - "$REPO_ROOT" "$PACKAGE_JSON" "$PACKAGE_LOCK" "$CI" <<'PY'
import json
import os
import subprocess
import sys

repo_root, package_json, package_lock, ci = sys.argv[1:5]
failures = 0
assertions = 0


def ok(msg):
    global assertions
    assertions += 1
    print(f"  ok   - {msg}")


def fail(msg):
    global assertions, failures
    assertions += 1
    failures += 1
    print(f"  FAIL - {msg}")


def summary():
    print(f"\n{assertions} assertions, {failures} failures")
    if failures:
        print("  Result: FAIL")
        sys.exit(1)
    print("  Result: PASS")
    sys.exit(0)


if not os.path.isfile(package_json):
    fail(f"package.json exists at {package_json}")
    summary()

with open(package_json, encoding="utf-8") as handle:
    data = json.load(handle)

ok("package.json exists and parses as JSON")

deps = {}
deps.update(data.get("dependencies", {}) or {})
deps.update(data.get("devDependencies", {}) or {})
carets = [name for name, spec in deps.items() if isinstance(spec, str) and spec.startswith("^")]
if carets:
    ok(f"package.json keeps caret ranges ({len(carets)} of {len(deps)} dependencies)")
else:
    fail("package.json must keep caret ranges as per the documented decision")

if os.path.isfile(package_lock):
    ok("package-lock.json exists")
else:
    fail(f"package-lock.json exists at {package_lock}")
    summary()

tracked = subprocess.run(
    ["git", "-C", repo_root, "ls-files", "--error-unmatch", "App/Frontend/package-lock.json"],
    capture_output=True,
    text=True,
)
if tracked.returncode == 0:
    ok("package-lock.json is tracked by git")
else:
    fail("package-lock.json must be tracked by git")

if os.path.isfile(ci):
    with open(ci, encoding="utf-8") as handle:
        workflow = handle.read()
else:
    workflow = ""

if "npm ci" in workflow:
    ok(".github/workflows/ci.yml installs with `npm ci`")
else:
    fail(".github/workflows/ci.yml must install the frontend with `npm ci`")

if "npm install" not in workflow:
    ok(".github/workflows/ci.yml does not fall back to `npm install`")
else:
    fail(".github/workflows/ci.yml must not use a non-lockfile install")

summary()
PY
