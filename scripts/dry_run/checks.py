"""Pure, side-effect-free logic for the zero-cost dry-run harness.

Everything in this module is deterministic and unit-testable: the check result
model, the exit-code contract, the summary formatter (which must never leak
secrets) and the small parsers used by the orchestration in ``dry_run.py``.

No network, no Docker, no filesystem access happens here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ── Exit-code contract ───────────────────────────────────────────────────────

EXIT_OK = 0
EXIT_BROKEN = 1

# ── Check statuses ───────────────────────────────────────────────────────────

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_PENDING = "PENDING"

# ── Cost-zero guardrail ──────────────────────────────────────────────────────

# The exact value injected by scripts/dry_run/compose.dry-run.yml.
DUMMY_GEMINI_API_KEY = "dry-run-dummy-gemini-key-not-real"  # gitleaks:allow

# Markers that identify a deliberately fictitious key.
_DUMMY_MARKERS = (
    "dummy",
    "fake",
    "test",
    "dry-run",
    "dryrun",
    "placeholder",
    "not-real",
    "your-",
    "example",
)

# Known real-key prefixes (Google API keys use AIza...). Anything that looks
# real is treated as NOT a dummy, so the harness fails safe and aborts.
_REAL_KEY_PREFIXES = ("AIza", "sk-", "sk_")

# Patterns scrubbed from any output line so a token can never be echoed.
_SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_\-]{10,}"),
    re.compile(r"eyJ[0-9A-Za-z_\-]+\.[0-9A-Za-z_\-]+\.[0-9A-Za-z_\-]+"),
)


@dataclass
class Check:
    """Outcome of a single harness verification."""

    name: str
    status: str
    detail: str = ""
    action: str = ""

    @property
    def ok(self) -> bool:
        return self.status == STATUS_PASS


def passing(name: str, detail: str = "") -> Check:
    return Check(name=name, status=STATUS_PASS, detail=detail)


def failing(name: str, detail: str, action: str) -> Check:
    return Check(name=name, status=STATUS_FAIL, detail=detail, action=action)


def pending(name: str, detail: str, action: str) -> Check:
    return Check(name=name, status=STATUS_PENDING, detail=detail, action=action)


def redact(text: str) -> str:
    """Remove anything that looks like a credential from an output string."""
    if not text:
        return text
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def format_check(result: Check) -> str:
    """Render one check. Failures and pending checks carry a concrete next step."""
    line = f"[{result.status}] {result.name}"
    if result.detail:
        line += f" - {result.detail}"
    if result.status != STATUS_PASS and result.action:
        line += f"\n         next: {result.action}"
    return redact(line)


def exit_code(results: list[Check]) -> int:
    """Zero only when at least one check ran and every check passed.

    An empty result set, any failure and any pending (incomplete) check all
    yield a non-zero exit code so a partial run can never be reported green.
    """
    if not results:
        return EXIT_BROKEN
    if all(result.ok for result in results):
        return EXIT_OK
    return EXIT_BROKEN


def format_summary(results: list[Check]) -> str:
    """Render every check plus the final tally."""
    lines = [format_check(result) for result in results]
    passed = sum(1 for result in results if result.ok)
    total = len(results)
    lines.append("")
    if total and passed == total:
        lines.append(f"RESULT: {passed}/{total} checks passed. Harness GREEN.")
    else:
        failed = sum(1 for r in results if r.status == STATUS_FAIL)
        pending_count = sum(1 for r in results if r.status == STATUS_PENDING)
        lines.append(
            f"RESULT: {passed}/{total} checks passed "
            f"({failed} failed, {pending_count} pending). Harness RED."
        )
    return "\n".join(lines)


def is_dummy_gemini_key(key: str | None) -> bool:
    """Classify the effective GEMINI_API_KEY as fictitious.

    Fail-safe: an empty or clearly-dummy key is accepted; a Google-looking or
    otherwise unknown key is rejected so the harness aborts rather than risk a
    paid call.
    """
    if key is None:
        return True
    value = key.strip()
    if not value:
        return True
    if value == DUMMY_GEMINI_API_KEY:
        return True
    lowered = value.lower()
    if any(marker in lowered for marker in _DUMMY_MARKERS):
        return True
    if value.startswith(_REAL_KEY_PREFIXES):
        return False
    return False


def pick_working_scheme(probes: list[tuple[str, bool]]) -> str | None:
    """Return the first scheme whose probe succeeded, or None."""
    for scheme, worked in probes:
        if worked:
            return scheme
    return None


def extract_incidente_id(payload: object) -> int | None:
    """Pull the incident id from a webhook response body."""
    if not isinstance(payload, dict):
        return None
    for key in ("incidente_id", "id"):
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().isdigit():
            return int(value)
    return None


def extract_canal_origen_id(incidente: object) -> int | None:
    """Pull canal_origen_id from an incident read payload.

    The canonical response nests it as ``canal_origen.id``; a flat
    ``canal_origen_id`` is accepted as a fallback for tolerance.
    """
    if not isinstance(incidente, dict):
        return None
    canal = incidente.get("canal_origen")
    if isinstance(canal, dict) and isinstance(canal.get("id"), int):
        return canal["id"]
    flat = incidente.get("canal_origen_id")
    if isinstance(flat, int) and not isinstance(flat, bool):
        return flat
    return None
