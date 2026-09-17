"""Unit tests for the pure logic in scripts/dry_run/checks.py.

Run with:
    cd scripts/dry_run && python -m pytest test_checks.py -q
or from the repo root:
    python -m pytest scripts/dry_run/test_checks.py -q
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import checks
from checks import (
    DUMMY_GEMINI_API_KEY,
    Check,
    exit_code,
    extract_canal_origen_id,
    extract_incidente_id,
    failing,
    format_check,
    format_summary,
    is_dummy_gemini_key,
    passing,
    pending,
    pick_working_scheme,
    redact,
)


# ── exit-code contract (§1.3) ────────────────────────────────────────────────


def test_exit_code_zero_only_when_all_pass():
    assert exit_code([passing("a"), passing("b")]) == 0


def test_exit_code_nonzero_on_any_failure():
    assert exit_code([passing("a"), failing("b", "boom", "fix it")]) != 0


def test_exit_code_nonzero_on_pending():
    assert exit_code([passing("a"), pending("b", "skipped", "run later")]) != 0


def test_exit_code_nonzero_on_empty_results():
    assert exit_code([]) != 0


# ── summary formatting (§1.2) ────────────────────────────────────────────────


def test_failure_includes_name_and_action():
    line = format_check(failing("login", "got 500", "check backend logs"))
    assert "login" in line
    assert "check backend logs" in line
    assert "FAIL" in line


def test_success_does_not_print_secrets():
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.c2lnbmF0dXJl"  # gitleaks:allow
    line = format_check(passing("create", f"token={token}"))
    assert token not in line
    assert "[REDACTED]" in line


def test_google_key_is_redacted():
    line = redact("key=AIzaSyA1234567890abcdefghijklmnop")
    assert "AIzaSyA1234567890abcdefghijklmnop" not in line


def test_summary_reports_green_only_when_all_pass():
    assert "GREEN" in format_summary([passing("a"), passing("b")])


def test_summary_reports_red_when_any_pending():
    summary = format_summary([passing("a"), pending("b", "skipped", "do it")])
    assert "RED" in summary
    assert "1/2" in summary


def test_summary_of_empty_run_is_red():
    assert "RED" in format_summary([])


# ── cost-zero guardrail (§2.2) ───────────────────────────────────────────────


def test_exact_dummy_key_is_dummy():
    assert is_dummy_gemini_key(DUMMY_GEMINI_API_KEY)


def test_real_google_key_is_not_dummy():
    assert not is_dummy_gemini_key("AIzaSyA1234567890abcdefghijklmnop")


def test_empty_key_is_dummy():
    assert is_dummy_gemini_key("")
    assert is_dummy_gemini_key(None)


def test_placeholder_markers_are_dummy():
    assert is_dummy_gemini_key("your-gemini-api-key-here")
    assert is_dummy_gemini_key("not-real")
    assert is_dummy_gemini_key("DRY_RUN_TEST_KEY")


def test_unknown_format_fails_safe():
    assert not is_dummy_gemini_key("some-opaque-value-123")


# ── scheme resolution (§4.5) ─────────────────────────────────────────────────


def test_pick_working_scheme_prefers_http_then_https():
    assert pick_working_scheme([("http", True), ("https", True)]) == "http"
    assert pick_working_scheme([("http", False), ("https", True)]) == "https"
    assert pick_working_scheme([("http", False), ("https", False)]) is None


# ── payload parsers (§4.1, §5.2, §5.3) ───────────────────────────────────────


def test_extract_incidente_id_from_int_and_str():
    assert extract_incidente_id({"incidente_id": 42}) == 42
    assert extract_incidente_id({"incidente_id": "42"}) == 42
    assert extract_incidente_id({}) is None
    assert extract_incidente_id(None) is None


def test_extract_canal_origen_id_nested_and_flat():
    assert extract_canal_origen_id({"canal_origen": {"id": 2}}) == 2
    assert extract_canal_origen_id({"canal_origen_id": 2}) == 2
    assert extract_canal_origen_id({"canal_origen": None}) is None
    assert extract_canal_origen_id({}) is None


def test_check_ok_property():
    assert Check("a", checks.STATUS_PASS).ok
    assert not Check("a", checks.STATUS_FAIL).ok
    assert not Check("a", checks.STATUS_PENDING).ok
