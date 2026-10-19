#!/usr/bin/env bash
# ==============================================================================
# Test harness for Python dependency pinning in App/Backend/requirements.txt
# (c-64, group 4).
#
# Rule enforced (design D6): every dependency expressed with a `>=` floor must
# also declare an UPPER bound (`<...`), OR carry an explicit, registered
# justification on the same line.
#
# Justification marker convention:
#   no-upper-bound-ok: <motivo>
# An inline comment on the requirement line with a non-empty reason after that
# token is accepted as a documented exception.
#
# Covered behavior:
#   - requirements.txt exists
#   - every `>=`-style requirement declares an upper bound
#   - the only line left without an upper bound is a documented exception
#     (the allowlist below keeps that exception from silently growing)
#   - the three bounded packages carry their intended compatibility ceilings
#
# Usage:
#   bash scripts/tests/test_python_dependency_pins.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed (also when the file is absent)
#
# Note: this harness is OFFLINE. `pip install --dry-run` (task 4.3) is the
# separate resolution check and is not run here.
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
REQUIREMENTS="${REPO_ROOT}/App/Backend/requirements.txt"

python3 - "$REQUIREMENTS" <<'PY'
import os
import re
import sys

path = sys.argv[1]
failures = 0
assertions = 0

# Packages intentionally left without an upper bound, each requiring an inline
# `no-upper-bound-ok:` justification. Kept explicit so the exception set cannot
# grow unnoticed.
EXPECTED_UNBOUNDED = {"cryptography"}

MARKER = "no-upper-bound-ok:"
REQUIREMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(\[[^\]]+\])?\s*(.*)$")


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


if not os.path.isfile(path):
    fail(f"requirements.txt exists at {path}")
    summary()

with open(path, encoding="utf-8") as handle:
    lines = handle.read().splitlines()

ok("requirements.txt exists")

# Collect effective requirement lines: (line_no, raw_line, spec, name, comment).
requirements = []
for index, raw in enumerate(lines, start=1):
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        continue
    body, sep, comment = raw.partition("#")
    body = body.strip()
    match = REQUIREMENT.match(body)
    if not match:
        continue
    name = body.split("[", 1)[0].split("=", 1)[0].split(">", 1)[0].split("<", 1)[0].strip()
    requirements.append((index, raw, body, name, comment.strip() if sep else ""))

if requirements:
    ok(f"parsed {len(requirements)} requirement lines")
else:
    fail("at least one requirement line is present")
    summary()

bounded_floor = [
    (no, name, body, comment)
    for no, raw, body, name, comment in requirements
    if ">=" in body
]
if bounded_floor:
    ok(f"found {len(bounded_floor)} `>=` style requirements")
else:
    fail("expected `>=` style requirements in requirements.txt")

# A `>=` requirement without `<` is unbounded.
unbounded = []
for no, name, body, comment in bounded_floor:
    if "<" not in body:
        justified = MARKER in comment and bool(
            comment.split(MARKER, 1)[1].strip()
        )
        unbounded.append((no, name, justified))

unjustified = [(no, name) for no, name, just in unbounded if not just]
if unjustified:
    fail(
        "every `>=` requirement declares an upper bound or a registered "
        f"justification (unjustified: {unjustified})"
    )
else:
    ok("every `>=` requirement is bounded or justified")

unbounded_names = {name for _, name, _ in unbounded}
if unbounded_names == EXPECTED_UNBOUNDED:
    ok(f"the unbounded exception set is exactly {sorted(EXPECTED_UNBOUNDED)}")
else:
    fail(
        f"unbounded exception set must be {sorted(EXPECTED_UNBOUNDED)}, "
        f"got {sorted(unbounded_names)}"
    )

# The intended compatibility ceilings for the bounded packages.
intended = {
    "google-genai": ">=2.20.0,<3",
    "bcrypt": ">=4.0.0,<5",
    "python-jose": ">=3.3.0,<4",
}
by_name = {name: body for _, _, body, name, _ in requirements}
for name, expected in intended.items():
    body = by_name.get(name)
    if body is not None and expected in body.replace(" ", ""):
        ok(f"'{name}' declares '{expected}'")
    else:
        fail(f"'{name}' must declare '{expected}' (got {body!r})")

summary()
PY
