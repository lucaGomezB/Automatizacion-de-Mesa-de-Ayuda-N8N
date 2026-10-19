#!/usr/bin/env bash
# ==============================================================================
# Test harness for the security-scan CI job (c-64, group 5).
#
# Structural verification of the `security-scan` job in
# .github/workflows/ci.yml. Parses the workflow with an embedded python3
# parser (PyYAML is available in the dev environment) and asserts the job
# exists, runs in parallel with the existing jobs and executes the three
# scans required by the ci-pipeline delta spec:
#
#   1. backend dependency audit   -> pip-audit over App/Backend/requirements.txt
#   2. backend SAST               -> bandit over App/Backend/app
#   3. frontend dependency audit  -> npm audit over App/Frontend
#
# Covered behavior (5.1 RED / 5.3 TRIANGULATE):
#   - a job named `security-scan` exists alongside backend-tests,
#     frontend-tests and secret-scan (no `needs` coupling: runs in parallel)
#   - its steps run the three scans above
#   - it targets Python 3.12 and Node 20
#   - it pins its scanning tools (pip-audit==, bandit==)
#   - it declares its blocking policy explicitly (SAST `-lll`, backend audit
#     fails on NON-BREAKING fixable vulns, frontend audit report-only
#     `--audit-level=high`)
#   - it uses NO `secrets.*` references
#   - it does not mutate the test jobs' dependency trees (own env / no
#     writes to App/Backend/requirements.txt or App/Frontend/package*.json)
#
# Usage:
#   bash scripts/tests/test_security_scan_job.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — at least one assertion failed (also when the file is absent)
# ==============================================================================

set -uo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${TEST_DIR}/../.." && pwd)"
WORKFLOW="${REPO_ROOT}/.github/workflows/ci.yml"

python3 - "$WORKFLOW" <<'PY'
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
    fail(f"ci.yml exists at {path}")
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
    fail(f"ci.yml parses as YAML ({exc})")
    summary()

ok("ci.yml exists and parses as YAML")

jobs = data.get("jobs") if isinstance(data, dict) else None
if not isinstance(jobs, dict) or not jobs:
    fail("top-level `jobs` mapping is present and non-empty")
    summary()

ok(f"`jobs` mapping present ({len(jobs)} jobs)")

# ---------------------------------------------------------------------------
# 5.1 — the security-scan job exists alongside the pre-existing jobs.
# ---------------------------------------------------------------------------
expected_jobs = ["backend-tests", "frontend-tests", "secret-scan", "security-scan"]
for name in expected_jobs:
    if name in jobs:
        ok(f"job '{name}' present")
    else:
        fail(f"job '{name}' must be present")

job = jobs.get("security-scan")
if not isinstance(job, dict):
    fail("job 'security-scan' is a mapping")
    summary()

# Parallel execution: the scan job must not depend on the test jobs.
if "needs" in job:
    fail(f"security-scan must run in parallel (found `needs: {job['needs']}`)")
else:
    ok("security-scan declares no `needs` (runs in parallel)")

# Gather every `run` step command as a single searchable text blob, plus the
# per-step breakdown so we can attribute each scan to a step.
steps = job.get("steps")
if not isinstance(steps, list) or not steps:
    fail("security-scan declares a non-empty `steps` list")
    summary()

ok(f"security-scan declares steps ({len(steps)} steps)")

step_runs = []
for step in steps:
    if isinstance(step, dict):
        run = step.get("run")
        if isinstance(run, str):
            step_runs.append(run)
run_blob = "\n".join(step_runs)

# (1) backend dependency audit
if re.search(r"pip-audit", run_blob):
    ok("backend dependency audit runs (pip-audit)")
else:
    fail("backend dependency audit missing (no `pip-audit` in run steps)")

if re.search(r"requirements\.txt", run_blob):
    ok("backend audit targets App/Backend/requirements.txt")
else:
    fail("backend audit must target App/Backend/requirements.txt")

# (2) backend SAST
if re.search(r"\bbandit\b", run_blob):
    ok("backend SAST runs (bandit)")
else:
    fail("backend SAST missing (no `bandit` in run steps)")

if re.search(r"App/Backend/app\b", run_blob):
    ok("SAST targets App/Backend/app")
else:
    fail("SAST must target App/Backend/app")

# (3) frontend dependency audit
if re.search(r"npm\s+audit", run_blob):
    ok("frontend dependency audit runs (npm audit)")
else:
    fail("frontend dependency audit missing (no `npm audit` in run steps)")

# ---------------------------------------------------------------------------
# 5.2 — pinned toolchain and target runtimes (Python 3.12 + Node 20).
# ---------------------------------------------------------------------------
setups = {}
for step in steps:
    if not isinstance(step, dict):
        continue
    uses = step.get("uses")
    if isinstance(uses, str) and "setup-python" in uses:
        setups["python"] = step.get("with", {})
    if isinstance(uses, str) and "setup-node" in uses:
        setups["node"] = step.get("with", {})

if setups.get("python", {}).get("python-version") == "3.12":
    ok("job sets up Python 3.12")
else:
    fail(f"job must set up Python 3.12 (got {setups.get('python')!r})")

if setups.get("node", {}).get("node-version") == "20":
    ok("job sets up Node 20")
else:
    fail(f"job must set up Node 20 (got {setups.get('node')!r})")

# Scanning tools are pinned like the existing `ruff==0.8.4`.
for tool in ("pip-audit", "bandit"):
    if re.search(rf"\b{tool}==\d", run_blob):
        ok(f"scanning tool pinned: {tool}==<version>")
    else:
        fail(f"scanning tool must be pinned: {tool}==<version>")

# ---------------------------------------------------------------------------
# 5.3 — blocking policy, no secrets, no test-dependency-tree mutation.
# ---------------------------------------------------------------------------
# (a) blocking policy is explicit AND attributed to the right step.
sast_runs = [r for r in step_runs if re.search(r"\bbandit\s+-r\b", r)]
if sast_runs and all(re.search(r"-lll\b", r) for r in sast_runs):
    ok("SAST step blocks HIGH severity only (bandit -lll)")
else:
    fail(f"SAST step must pass -lll (bandit runs: {sast_runs!r})")

audit_runs = [r for r in step_runs if re.search(r"\bpip-audit\s+-r\b", r)]
audit_blob = "\n".join(audit_runs)
if audit_runs and re.search(r"non-breaking|no rompiente", audit_blob, re.I):
    ok("backend audit step documents the blocks-on-non-breaking-fixable policy")
else:
    fail("backend audit step must document the blocks-on-non-breaking-fixable policy")

if audit_runs and re.search(r"pip_audit_exceptions\.txt", audit_blob):
    ok("backend audit step references the versioned exceptions file")
else:
    fail("backend audit step must reference scripts/security/pip_audit_exceptions.txt")

if (
    audit_runs
    and re.search(r"--ignore-vuln", audit_blob)
    and re.search(r"continue-on-error", audit_blob, re.I)
):
    ok("backend audit excepts explicitly per-ID, not via a global continue-on-error")
else:
    fail("backend audit must use explicit --ignore-vuln (no global continue-on-error)")

npm_runs = [r for r in step_runs if re.search(r"npm\s+audit", r)]
npm_blob = "\n".join(npm_runs)
if npm_runs and re.search(r"--audit-level=high", npm_blob):
    ok("frontend audit targets --audit-level=high")
else:
    fail("frontend audit must pass --audit-level=high")

if npm_runs and re.search(r"\|\|\s*true\b", npm_blob):
    ok("frontend audit is non-blocking (report-only: `|| true`)")
else:
    fail("frontend audit must be non-blocking in this iteration")

# (b) no repository secrets are referenced. `secrets.` must be the GitHub
# Actions context, not an identifier such as `scan_engram_secrets.py`.
if re.search(r"(?<![A-Za-z0-9_])secrets\.", raw):
    fail("workflow must not reference `secrets.*`")
else:
    ok("no `secrets.*` references in the workflow")

# (c) the job does not mutate the test jobs' dependency trees.
mutating = re.search(
    r"(pip install -r\s+App/Backend/requirements\.txt|"
    r"npm (ci|install)\b[^\n]*App/Frontend|"
    r"(>>|>)\s*App/Backend/requirements\.txt|"
    r"(>>|>)\s*App/Frontend/package[^\s]*)",
    run_blob,
)
if mutating:
    fail(f"job must not mutate test dependency trees (matched {mutating.group(0)!r})")
else:
    ok("job does not mutate the test jobs' dependency trees")

# (d) the versioned exception list is well-formed: every entry is a valid
# vulnerability ID with a non-empty per-line reason, so exceptions stay
# auditable (never a bare mute).
exc_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(path))),
    "scripts/security/pip_audit_exceptions.txt",
)
if os.path.isfile(exc_path):
    ok("pip-audit exceptions file exists")
    bad = []
    entries = 0
    with open(exc_path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            entries += 1
            code, _sep, reason = stripped.partition("#")
            if not re.match(r"^(PYSEC|CVE|GHSA)-\S+$", code.strip()):
                bad.append(lineno)
            elif not reason.strip():
                bad.append(lineno)
    if entries and not bad:
        ok(f"every exception entry carries a valid ID and a reason ({entries} entries)")
    elif not entries:
        fail("exceptions file has no entries despite pre-existing findings")
    else:
        fail(f"exception entries missing a valid ID or reason (lines: {bad})")
else:
    fail(f"pip-audit exceptions file exists at {exc_path}")

summary()
PY
