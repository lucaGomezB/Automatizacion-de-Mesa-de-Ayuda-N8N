#!/usr/bin/env bash
# ==============================================================================
# Test harness for .github/dependabot.yml (c-64, group 2).
#
# Structural verification of the Dependabot configuration using plain bash
# assertions plus an embedded python3 parser (PyYAML is available in the dev
# environment). No bats dependency; runs OFFLINE.
#
# Covered behavior:
#   - the file exists and parses as YAML with `version: 2`
#   - exactly three update entries: pip @ /App/Backend, npm @ /App/Frontend,
#     github-actions @ /
#   - each entry has a recurring schedule (schedule.interval: weekly)
#   - each entry declares a non-empty `groups` block
#   - no credential/token values are present
#   - no auto-merge or auto-approve directives are present
#
# Usage:
#   bash scripts/tests/test_dependabot_config.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed (also when the file is absent)
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
DEPENDABOT="${REPO_ROOT}/.github/dependabot.yml"

python3 - "$DEPENDABOT" <<'PY'
import os
import re
import sys

path = sys.argv[1]
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


if not os.path.isfile(path):
    fail(f"dependabot.yml exists at {path}")
    summary()

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    fail(f"PyYAML available ({exc})")
    summary()

with open(path, encoding="utf-8") as handle:
    raw = handle.read()

try:
    data = yaml.safe_load(raw)
except Exception as exc:
    fail(f"dependabot.yml parses as YAML ({exc})")
    summary()

ok("dependabot.yml exists")

if isinstance(data, dict):
    ok("top-level document is a mapping")
else:
    fail("top-level document must be a mapping")
    summary()

if data.get("version") == 2:
    ok("version == 2")
else:
    fail(f"version must be 2, got {data.get('version')!r}")

updates = data.get("updates")
if isinstance(updates, list):
    ok("updates is a list")
else:
    fail("updates must be a list")
    updates = []

expected = [
    ("pip", "/App/Backend"),
    ("npm", "/App/Frontend"),
    ("github-actions", "/"),
]

by_eco = {}
for entry in updates:
    if isinstance(entry, dict):
        by_eco[entry.get("package-ecosystem")] = entry

for eco, directory in expected:
    entry = by_eco.get(eco)
    if entry is None:
        fail(f"entry present for ecosystem '{eco}'")
        continue
    if entry.get("directory") == directory:
        ok(f"'{eco}' directory == {directory}")
    else:
        fail(f"'{eco}' directory must be {directory}, got {entry.get('directory')!r}")

extra = sorted(set(by_eco) - {eco for eco, _ in expected})
if extra:
    fail(f"unexpected ecosystems present: {extra}")
else:
    ok("only the three expected ecosystems are present")

for eco, _ in expected:
    entry = by_eco.get(eco)
    if entry is None:
        continue
    schedule = entry.get("schedule")
    if isinstance(schedule, dict) and schedule.get("interval") == "weekly":
        ok(f"'{eco}' schedule.interval == weekly")
    else:
        fail(f"'{eco}' schedule.interval must be weekly, got {schedule!r}")
    groups = entry.get("groups")
    if isinstance(groups, dict) and groups:
        ok(f"'{eco}' declares a non-empty groups block")
    else:
        fail(f"'{eco}' must declare a non-empty groups block")

def strip_comments(text):
    """Remove trailing YAML comments so checks see effective config, not prose."""
    stripped = []
    for line in text.splitlines():
        out = []
        in_string = False
        quote = ""
        for ch in line:
            if in_string:
                out.append(ch)
                if ch == quote:
                    in_string = False
            elif ch in "\"'":
                in_string = True
                quote = ch
                out.append(ch)
            elif ch == "#":
                break
            else:
                out.append(ch)
        stripped.append("".join(out))
    return "\n".join(stripped)


def walk_keys(node):
    """Yield every mapping key and scalar string in the parsed document."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            yield from walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk_keys(item)
    elif isinstance(node, str):
        yield node


effective = strip_comments(raw)

credential_patterns = [
    r"(?i)\btoken\b",
    r"(?i)\bpassword\b",
    r"(?i)\bsecret\b",
    r"(?i)\bauth\b",
    r"(?i)api[_-]?key",
    r"(?i)\bcredentials?\b",
]
credential_hits = [p for p in credential_patterns if re.search(p, raw)]
if credential_hits:
    fail(f"no credential/token values present (matched: {credential_hits})")
else:
    ok("no credential/token values present")

auto_patterns = [r"(?i)auto[-_ ]?merge", r"(?i)auto[-_ ]?approve"]
auto_hits = [p for p in auto_patterns if re.search(p, effective)]
config_auto = [
    token
    for token in walk_keys(data)
    if any(re.search(p, token) for p in auto_patterns)
]
if auto_hits or config_auto:
    fail(
        "no auto-merge/auto-approve directives "
        f"(text: {auto_hits}, config: {config_auto})"
    )
else:
    ok("no auto-merge/auto-approve directives present")

summary()
PY
