"""Offline TDD tests for the pure TLS evaluators (c-140 section 7).

Pure, side-effect-free evaluators consumed by ``dry_run.py``'s ``tls:*`` group.
No network, no Docker, no socket: every case feeds an already-observed status,
header map, fingerprint or ``docker compose config`` service tree and asserts the
resulting ``Check``.

Run with:
    python -m pytest scripts/dry_run/test_tls_checks.py -q
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tls_checks
from checks import STATUS_FAIL, STATUS_PASS, STATUS_PENDING

HSTS = "max-age=31536000; includeSubDomains"
SECURITY_HEADERS = {
    "Strict-Transport-Security": HSTS,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
}
LOCATION = "https://localhost/api/v1/health?origen=smoke"


# ── version negotiated ───────────────────────────────────────────────────────


def test_version_expected_passes():
    check = tls_checks.evaluate_version("tls:handshake-1.3", "TLSv1.3", "TLSv1.3")
    assert check.status == STATUS_PASS
    assert check.name == "tls:handshake-1.3"


def test_version_mismatch_fails():
    check = tls_checks.evaluate_version("tls:handshake-1.2", "TLSv1.3", "TLSv1.2")
    assert check.status == STATUS_FAIL
    assert "TLSv1.3" in check.detail


def test_version_absent_fails():
    assert tls_checks.evaluate_version("tls:handshake-1.3", None, "TLSv1.3").status == STATUS_FAIL


# ── identity by SHA-256 ──────────────────────────────────────────────────────


def test_identity_match_passes():
    check = tls_checks.evaluate_identity("aabbcc", "aabbcc")
    assert check.status == STATUS_PASS
    assert check.name == "tls:identity"


def test_identity_mismatch_fails():
    check = tls_checks.evaluate_identity("aabbcc", "ddeeff")
    assert check.status == STATUS_FAIL


def test_identity_absent_fails():
    assert tls_checks.evaluate_identity(None, "aabbcc").status == STATUS_FAIL


# ── redirect 301 ─────────────────────────────────────────────────────────────


def test_redirect_preserving_path_and_query_without_hsts_passes():
    check = tls_checks.evaluate_redirect(301, {"Location": LOCATION}, LOCATION)
    assert check.status == STATUS_PASS
    assert check.name == "tls:redirect"


def test_redirect_with_hsts_fails():
    check = tls_checks.evaluate_redirect(301, {"Location": LOCATION, "Strict-Transport-Security": HSTS}, LOCATION)
    assert check.status == STATUS_FAIL


def test_redirect_wrong_status_fails():
    assert tls_checks.evaluate_redirect(200, {"Location": LOCATION}, LOCATION).status == STATUS_FAIL


def test_redirect_without_query_fails():
    check = tls_checks.evaluate_redirect(
        301, {"Location": "https://localhost/api/v1/health"}, LOCATION
    )
    assert check.status == STATUS_FAIL


# ── security headers ─────────────────────────────────────────────────────────


def test_security_headers_complete_pass():
    check = tls_checks.evaluate_security_headers(SECURITY_HEADERS)
    assert check.status == STATUS_PASS
    assert check.name == "tls:headers"


def test_security_headers_wrong_max_age_fails():
    headers = dict(SECURITY_HEADERS)
    headers["Strict-Transport-Security"] = "max-age=60"
    assert tls_checks.evaluate_security_headers(headers).status == STATUS_FAIL


def test_security_headers_missing_permissions_policy_fails():
    headers = dict(SECURITY_HEADERS)
    del headers["Permissions-Policy"]
    check = tls_checks.evaluate_security_headers(headers)
    assert check.status == STATUS_FAIL
    assert "Permissions-Policy" in check.detail


# ── Server header ────────────────────────────────────────────────────────────


def test_server_header_without_version_passes():
    check = tls_checks.evaluate_server_header({"Server": "nginx"})
    assert check.status == STATUS_PASS
    assert check.name == "tls:server-header"


def test_server_header_with_version_fails():
    check = tls_checks.evaluate_server_header({"Server": "nginx/1.31.7"})
    assert check.status == STATUS_FAIL
    assert "1.31.7" in check.detail


# ── unknown Host ─────────────────────────────────────────────────────────────


def test_unknown_host_closed_without_response_passes():
    check = tls_checks.evaluate_unknown_host(None)
    assert check.status == STATUS_PASS
    assert check.name == "tls:unknown-host"


def test_unknown_host_answered_fails():
    assert tls_checks.evaluate_unknown_host(200).status == STATUS_FAIL


# ── TLS 1.1 rejection ────────────────────────────────────────────────────────


def test_tls11_rejected_passes():
    check = tls_checks.evaluate_tls11_rejection(True, "TLSV1_ALERT_PROTOCOL_VERSION")
    assert check.status == STATUS_PASS
    assert check.name == "tls:reject-1.1"


def test_tls11_not_offerable_is_pending():
    check = tls_checks.evaluate_tls11_rejection(False, None)
    assert check.status == STATUS_PENDING


def test_tls11_accepted_fails():
    assert tls_checks.evaluate_tls11_rejection(True, None).status == STATUS_FAIL


# ── edge exposure from `docker compose config` ───────────────────────────────


def test_edge_exposure_string_form_only_nginx_outside_loopback_passes():
    services = {
        "nginx": {"ports": ["80:80", "443:443"]},
        "postgres": {"ports": ["127.0.0.1:5433:5432"]},
        "n8n": {"ports": ["127.0.0.1:5678:5678"]},
    }
    assert tls_checks.evaluate_edge_exposure(services).status == STATUS_PASS


def test_edge_exposure_dict_form_passes():
    services = {
        "nginx": {"ports": [{"target": 80, "published": "80"}, {"target": 443, "published": "443"}]},
        "postgres": {"ports": [{"target": 5432, "published": "5433", "host_ip": "127.0.0.1"}]},
    }
    assert tls_checks.evaluate_edge_exposure(services).status == STATUS_PASS


def test_edge_exposure_bare_n8n_fails():
    services = {
        "nginx": {"ports": ["80:80", "443:443"]},
        "n8n": {"ports": ["5678:5678"]},
    }
    check = tls_checks.evaluate_edge_exposure(services)
    assert check.status == STATUS_FAIL
    assert "n8n" in check.detail
