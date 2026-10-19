#!/usr/bin/env bash
# ==============================================================================
# Test harness for docker image pins in docker-compose.yml (c-64, group 3).
#
# Structural verification that every service in the compose file references a
# Docker image pinned to an EXPLICIT version tag. Floating tags (`latest`) and
# tag-less references are rejected. A tag such as `alpine` is NOT an explicit
# version pin: it is a mutable channel that can silently change the image.
#
# Covered behavior:
#   - docker-compose.yml exists and parses as YAML
#   - the file declares services with image references
#   - every image reference carries a tag
#   - no image tag is `latest`
#   - every image tag is an explicit version (`<major>[.<minor>[.<patch>]][-suffix]`)
#   - the already-pinned images stay pinned (regression guard)
#
# Usage:
#   bash scripts/tests/test_docker_image_pins.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed (also when the file is absent)
#
# Note: this harness is OFFLINE. It does not contact the registry; registry
# resolution of the concrete tag used for the pin happens during the apply.
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
COMPOSE="${REPO_ROOT}/docker-compose.yml"

python3 - "$COMPOSE" <<'PY'
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
    fail(f"docker-compose.yml exists at {path}")
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
    fail(f"docker-compose.yml parses as YAML ({exc})")
    summary()

ok("docker-compose.yml exists and parses as YAML")

services = data.get("services") if isinstance(data, dict) else None
if not isinstance(services, dict) or not services:
    fail("top-level `services` mapping is present and non-empty")
    summary()

ok(f"`services` mapping present ({len(services)} services)")

# An explicit version tag: starts with a digit (optionally `v`), then optional
# dot-separated numeric segments and an optional `-suffix` (e.g. `15.5-alpine`).
VERSION_TAG = re.compile(r"^v?\d+(\.\d+)*(-[A-Za-z0-9._-]+)?$")


def split_tag(image):
    """Return the tag portion of an image reference, or None when untagged."""
    if not isinstance(image, str) or not image:
        return None
    last = image.rsplit("/", 1)[-1]
    if "@" in image:
        return None
    if ":" not in last:
        return None
    return last.rsplit(":", 1)[1]


references = []
for name, spec in services.items():
    if isinstance(spec, dict) and "image" in spec:
        references.append((name, spec.get("image")))

if references:
    ok(f"image references declared ({len(references)} services)")
else:
    fail("at least one service declares an `image`")

untagged = [(n, i) for n, i in references if split_tag(i) is None]
if untagged:
    fail(f"every image carries a tag (untagged: {untagged})")
else:
    ok("every image reference carries a tag")

latest = [(n, i) for n, i in references if split_tag(i) == "latest"]
if latest:
    fail(f"no image tag is `latest` (found: {latest})")
else:
    ok("no image tag is `latest`")

floating = [
    (n, i)
    for n, i in references
    if split_tag(i) is not None and not VERSION_TAG.match(split_tag(i))
]
if floating:
    fail(f"every image tag is an explicit version (floating channels: {floating})")
else:
    ok("every image tag is an explicit version")

# Regression guard: images that were already pinned must remain pinned.
pinned_before = [
    (n, i) for n, i in references if isinstance(i, str) and i.startswith("postgres")
]
if pinned_before and all(VERSION_TAG.match(split_tag(i)) for _, i in pinned_before):
    ok("existing postgres image stays on an explicit version tag")
else:
    fail(f"existing postgres image must stay pinned (found: {pinned_before})")

summary()
PY
