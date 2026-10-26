"""Offline TDD tests for the c-140 E2E smoke evaluators (section 5).

Pure, side-effect-free evaluators consumed by ``dry_run.py`` (``run_e2e`` and the
new harness groups). No network, no Docker, no external service: every case feeds
simulated API payloads (the exact shape of the real endpoints) and asserts the
resulting ``Check``.

Endpoints modelled:
    GET /api/v1/clasificaciones/incidente/{id} -> list[ClasificacionLogRead]
    GET /api/v1/incidentes/?origen_message_id=... -> list[IncidenteListItem]

Run with:
    python -m pytest scripts/dry_run/test_checks_c135.py -q
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dry_run
import e2e_checks
from checks import STATUS_FAIL, STATUS_PASS, failing, passing

_DRY_RUN_DIR = Path(dry_run.__file__).resolve().parent


# ── e2e:etapa (5.2 / 5.3) ─────────────────────────────────────────────────────


def test_etapa_deterministic_passes():
    check = e2e_checks.evaluate_etapa([{"etapa": "deterministic", "incidente_id": 7}])
    assert check.status == STATUS_PASS
    assert check.name == "e2e:etapa"


def test_etapa_gemini_fails_naming_the_stage():
    check = e2e_checks.evaluate_etapa([{"etapa": "gemini"}])
    assert check.status == STATUS_FAIL
    assert "gemini" in check.detail


def test_etapa_fallback_fails_naming_the_stage():
    check = e2e_checks.evaluate_etapa([{"etapa": "fallback"}])
    assert check.status == STATUS_FAIL
    assert "fallback" in check.detail


def test_etapa_two_records_fail():
    check = e2e_checks.evaluate_etapa(
        [{"etapa": "deterministic"}, {"etapa": "deterministic"}]
    )
    assert check.status == STATUS_FAIL
    assert "2" in check.detail


def test_etapa_empty_list_fails_actionable():
    check = e2e_checks.evaluate_etapa([])
    assert check.status == STATUS_FAIL
    assert check.action


def test_etapa_non_json_fails_actionable():
    check = e2e_checks.evaluate_etapa("<html>502 Bad Gateway</html>")
    assert check.status == STATUS_FAIL
    assert check.action


# ── e2e:idempotencia (5.4) ────────────────────────────────────────────────────


def test_idempotency_same_id_and_single_listing_passes():
    check = e2e_checks.evaluate_idempotency(
        {"incidente_id": 7}, {"incidente_id": 7}, [{"id": 7}], "smoke-abc"
    )
    assert check.status == STATUS_PASS
    assert check.name == "e2e:idempotencia"


def test_idempotency_distinct_ids_fail():
    check = e2e_checks.evaluate_idempotency(
        {"incidente_id": 7}, {"incidente_id": 8}, [{"id": 7}], "smoke-abc"
    )
    assert check.status == STATUS_FAIL
    assert "7" in check.detail and "8" in check.detail


def test_idempotency_two_listing_rows_fail():
    check = e2e_checks.evaluate_idempotency(
        {"incidente_id": 7}, {"incidente_id": 7}, [{"id": 7}, {"id": 8}], "smoke-abc"
    )
    assert check.status == STATUS_FAIL
    assert "2" in check.detail


def test_idempotency_missing_id_fails():
    check = e2e_checks.evaluate_idempotency(
        {"mensaje": "sin id"}, {"incidente_id": 7}, [{"id": 7}], "smoke-abc"
    )
    assert check.status == STATUS_FAIL


# ── guardrail:cost-guard-budget (5.5) ─────────────────────────────────────────


def test_cost_guard_budget_zero_passes():
    check = e2e_checks.evaluate_cost_guard_budget("0")
    assert check.status == STATUS_PASS
    assert check.name == "guardrail:cost-guard-budget"


def test_cost_guard_budget_nonzero_aborts():
    check = e2e_checks.evaluate_cost_guard_budget("10")
    assert check.status == STATUS_FAIL
    assert check.action


def test_cost_guard_budget_missing_aborts():
    assert e2e_checks.evaluate_cost_guard_budget(None).status == STATUS_FAIL
    assert e2e_checks.evaluate_cost_guard_budget("").status == STATUS_FAIL


def test_cost_guard_budget_non_numeric_aborts():
    assert e2e_checks.evaluate_cost_guard_budget("abc").status == STATUS_FAIL


def test_dry_run_overlay_sets_zero_budget():
    import yaml

    overlay = yaml.safe_load(
        (_DRY_RUN_DIR / "compose.dry-run.yml").read_text(encoding="utf-8")
    )
    environment = overlay["services"]["backend"]["environment"]
    assert str(environment.get("COST_GUARD_BUDGET_USD")) == "0"


# ── e2e:reintento (5.6, opt-in --with-retry-fault) ───────────────────────────


def _retry_args(with_retry_fault=True):
    return SimpleNamespace(
        with_retry_fault=with_retry_fault,
        n8n_host="localhost",
        n8n_port=5678,
        e2e_timeout=60,
        poll_timeout=5,
        timeout=15,
    )


def test_retry_recovery_passes_with_incident_and_single_row():
    check = e2e_checks.evaluate_retry_recovery({"incidente_id": 7}, [{"id": 7}], "smoke-abc")
    assert check.status == STATUS_PASS
    assert check.name == "e2e:reintento"


def test_retry_recovery_fails_without_incident():
    assert e2e_checks.evaluate_retry_recovery(None, [{"id": 7}], "smoke-abc").status == STATUS_FAIL


def test_retry_recovery_fails_with_two_rows():
    check = e2e_checks.evaluate_retry_recovery({"incidente_id": 7}, [{"id": 7}, {"id": 8}], "smoke-abc")
    assert check.status == STATUS_FAIL
    assert "2" in check.detail


def test_retry_fault_disconnects_before_send_and_reconnects(monkeypatch):
    calls: list[list] = []
    sleeps: list[float] = []

    def fake_docker(args, timeout=120):
        calls.append(list(args))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def fake_http(method, url, body=None, headers=None, timeout=15):
        calls.append(["HTTP", method])
        return 200, {}, json.dumps({"incidente_id": 7})

    monkeypatch.setattr(dry_run, "docker", fake_docker)
    monkeypatch.setattr(dry_run, "http_request", fake_http)
    monkeypatch.setattr(
        dry_run, "_fetch_incidentes_por_origen", lambda *a, **k: [{"id": 7}]
    )
    monkeypatch.setattr(dry_run.time, "sleep", lambda seconds: sleeps.append(seconds))

    results = dry_run.run_retry_fault(
        _retry_args(), "https://localhost", {"n8n_scheme": "http", "token": "t"}
    )

    disconnect = ["network", "disconnect", "mesa_local_automation", dry_run.BACKEND_CONTAINER]
    reconnect = [
        "network",
        "connect",
        "--alias",
        dry_run.BACKEND_CONTAINER,
        "--alias",
        dry_run.BACKEND_SERVICE_ALIAS,
        "mesa_local_automation",
        dry_run.BACKEND_CONTAINER,
    ]
    assert disconnect in calls
    assert reconnect in calls
    assert calls.index(disconnect) < calls.index(reconnect)
    assert ["HTTP", "POST"] in calls
    assert sleeps == [dry_run.RETRY_FAULT_RECONNECT_DELAY_S]
    assert results[0].status == STATUS_PASS


def test_retry_fault_reconnects_even_when_the_send_raises(monkeypatch):
    calls: list[list] = []

    def fake_docker(args, timeout=120):
        calls.append(list(args))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def boom(*args, **kwargs):
        raise RuntimeError("send exploded")

    monkeypatch.setattr(dry_run, "docker", fake_docker)
    monkeypatch.setattr(dry_run, "http_request", boom)
    monkeypatch.setattr(dry_run.time, "sleep", lambda seconds: None)

    results = dry_run.run_retry_fault(
        _retry_args(), "https://localhost", {"n8n_scheme": "http", "token": "t"}
    )

    reconnect = [
        "network",
        "connect",
        "--alias",
        dry_run.BACKEND_CONTAINER,
        "--alias",
        dry_run.BACKEND_SERVICE_ALIAS,
        "mesa_local_automation",
        dry_run.BACKEND_CONTAINER,
    ]
    assert reconnect in calls
    assert results[0].status == STATUS_FAIL


def test_retry_fault_is_absent_without_the_flag(monkeypatch):
    calls: list = []
    monkeypatch.setattr(
        dry_run, "docker", lambda *a, **k: calls.append(a) or SimpleNamespace(returncode=0)
    )
    results = dry_run.run_retry_fault(
        _retry_args(with_retry_fault=False),
        "https://localhost",
        {"n8n_scheme": "http", "token": "t"},
    )
    assert results == []
    assert calls == []


# ── Evidence report (5.7) ────────────────────────────────────────────────────


def test_evidence_report_includes_traceability():
    results = [passing("e2e:etapa", "ok"), failing("tls:x", "boom", "fix")]
    report = e2e_checks.build_evidence_report(
        commit="abc123",
        timestamp_utc="2026-10-26T12:00:00+00:00",
        n8n_version="2.11.2",
        groups=["e2e", "tls"],
        results=results,
    )
    assert report["commit"] == "abc123"
    assert report["timestamp_utc"].startswith("2026-10-26")
    assert report["n8n_version"] == "2.11.2"
    assert report["groups"] == ["e2e", "tls"]
    assert report["summary"]["total"] == 2
    assert {c["name"] for c in report["checks"]} == {"e2e:etapa", "tls:x"}


def test_evidence_report_omits_secrets():
    password = "admin123"
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.c2lnbmF0dXJl"  # gitleaks:allow
    results = [passing("preflight:login", f"token={token} password={password}")]
    report = e2e_checks.build_evidence_report(
        commit="abc",
        timestamp_utc="2026-10-26T12:00:00+00:00",
        n8n_version="2.11.2",
        groups=["preflight"],
        results=results,
        secrets=[password, token],
    )
    blob = json.dumps(report)
    assert password not in blob
    assert token not in blob


def test_groups_from_checks_preserves_order_without_duplicates():
    results = [passing("e2e:a"), passing("guardrail:b"), passing("e2e:c")]
    assert e2e_checks.groups_from_checks(results) == ["e2e", "guardrail"]
