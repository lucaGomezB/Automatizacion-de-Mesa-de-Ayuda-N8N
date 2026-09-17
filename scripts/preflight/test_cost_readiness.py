"""Tests del preflight de preparacion de costo (C-36).

Logica pura: se verifica `scripts/preflight/cost_readiness.py` leyendo los
artefactos reales del repo (`n8n/workflow.json` y `docker-compose.yml`) y
fixtures mutados en `tmp_path`. Sin red, sin Docker, sin credenciales.

Ejecucion (desde la raiz del repo):
    python -m pytest scripts/preflight/test_cost_readiness.py -q

Strict TDD: RED (modulo ausente) -> GREEN -> TRIANGULATE (mutaciones) -> REFACTOR.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402
import yaml  # noqa: E402

import cost_readiness  # noqa: E402
from cost_readiness import (  # noqa: E402
    Check,
    check_compose,
    check_workflow,
    exit_code,
    format_summary,
    run_preflight,
)


# ---------------------------------------------------------------------------
# Helpers de fixtures
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REAL_WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"
REAL_COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"


def _load_workflow() -> dict:
    return json.loads(REAL_WORKFLOW_PATH.read_text(encoding="utf-8"))


def _node(workflow: dict, name: str) -> dict:
    return next(n for n in workflow["nodes"] if n["name"] == name)


def _write_workflow(tmp_path, mutate) -> pathlib.Path:
    data = _load_workflow()
    mutate(data)
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def _valid_compose_data() -> dict:
    """Compose fixture con las dos cotas ya aprobadas (estado final del change)."""
    data = yaml.safe_load(REAL_COMPOSE_PATH.read_text(encoding="utf-8"))
    env = data["services"]["n8n"].setdefault("environment", {})
    env.setdefault("EXECUTIONS_TIMEOUT", "300")
    env.setdefault("EXECUTIONS_TIMEOUT_MAX", "600")
    return data


def _write_compose(tmp_path, mutate) -> pathlib.Path:
    data = _valid_compose_data()
    mutate(data)
    path = tmp_path / "docker-compose.yml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def _fails(checks) -> list:
    return [c for c in checks if c.status == "FAIL"]


def _summary(checks) -> str:
    return " || ".join(f"{c.status}:{c.name}:{c.detail}" for c in checks)


def _assert_single_named_fail(checks, needle: str) -> None:
    fails = _fails(checks)
    assert len(fails) == 1, f"Se esperaba exactamente un FAIL, got: {_summary(checks)}"
    assert needle in fails[0].name or needle in fails[0].detail, (
        f"El FAIL no nombra la guarda {needle!r}: {fails[0]!r}"
    )


# ===========================================================================
# 1.1 Tope del agente pago
# ===========================================================================
def test_valid_workflow_all_guards_pass(tmp_path):
    """El workflow real satisface todas las guardas verificadas."""
    checks = check_workflow(REAL_WORKFLOW_PATH)
    assert checks, "check_workflow debe devolver al menos un check"
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_missing_agent_max_iterations_fails_named(tmp_path):
    """Un workflow sin options.maxIterations produce FAIL nombrando la guarda."""
    def mutate(wf):
        _node(wf, "AI Agent")["parameters"]["options"].pop("maxIterations", None)

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "maxIterations")


# ===========================================================================
# 1.2 Lookback del trigger de Outlook
# ===========================================================================
def test_outlook_missing_lookback_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "Llega un email a Mesa de Ayuda")["parameters"]["filters"].pop(
            "custom", None
        )

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "Outlook")


def test_outlook_missing_unread_filter_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "Llega un email a Mesa de Ayuda")["parameters"]["filters"][
            "readStatus"
        ] = "all"

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "Outlook")


# ===========================================================================
# 1.3 Alcanzabilidad de "Marcar correo como leido"
# ===========================================================================
def test_mark_read_guard_passes_on_real_workflow():
    checks = check_workflow(REAL_WORKFLOW_PATH)
    assert any("Marcar correo como leido" in c.name for c in checks)
    assert all(
        c.status == "PASS"
        for c in checks
        if "Marcar correo como leido" in c.name
    ), _summary(checks)


def test_mark_read_unreachable_from_reject_branch_fails(tmp_path):
    def mutate(wf):
        outs = wf["connections"]["La informacion esta OK"]["main"][1]
        wf["connections"]["La informacion esta OK"]["main"][1] = [
            e for e in outs if e["node"] != "Es correo?"
        ]

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "Marcar correo como leido")


def test_mark_read_unreachable_from_error_branch_fails(tmp_path):
    def mutate(wf):
        outs = wf["connections"]["HTTP POST a MTM-SRU"]["main"][1]
        wf["connections"]["HTTP POST a MTM-SRU"]["main"][1] = [
            e for e in outs if e["node"] != "Es correo?"
        ]

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "Marcar correo como leido")


def test_mark_read_unreachable_from_success_branch_fails(tmp_path):
    def mutate(wf):
        outs = wf["connections"]["Rutear por canal de origen"]["main"][1]
        wf["connections"]["Rutear por canal de origen"]["main"][1] = [
            e for e in outs if e["node"] != "Marcar correo como leido"
        ]

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "Marcar correo como leido")


# ===========================================================================
# 1.4 Body enriquecido del HTTP POST
# ===========================================================================
def test_body_missing_origen_message_id_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "HTTP POST a MTM-SRU")["parameters"]["body"].pop(
            "origen_message_id", None
        )

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "origen_message_id")


def test_body_missing_classification_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "HTTP POST a MTM-SRU")["parameters"]["body"].pop(
            "clasificacion", None
        )

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "clasificacion")


def test_body_missing_origen_evento_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "HTTP POST a MTM-SRU")["parameters"]["body"].pop(
            "origen_evento", None
        )

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "origen_evento")


# ===========================================================================
# 1.5 Webhook dedicado de notificacion
# ===========================================================================
def test_missing_notification_webhook_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "notificacion-clasificacion")["parameters"]["path"] = "otra-ruta"

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "notificacion-clasificacion")


def test_notification_webhook_connected_to_creation_fails(tmp_path):
    def mutate(wf):
        wf["connections"]["notificacion-clasificacion"]["main"] = [
            [{"node": "HTTP POST a MTM-SRU", "type": "main", "index": 0}]
        ]

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "notificacion-clasificacion")


# ===========================================================================
# 1.6 Guarda de reintentos pagos
# ===========================================================================
def test_paid_agent_retry_on_fail_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "AI Agent")["retryOnFail"] = True

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "retryOnFail")


def test_paid_language_model_max_tries_fails_named(tmp_path):
    def mutate(wf):
        _node(wf, "Google Gemini Chat Model")["maxTries"] = 3

    checks = check_workflow(_write_workflow(tmp_path, mutate))
    _assert_single_named_fail(checks, "maxTries")


# ===========================================================================
# 1.7 Guardas del compose
# ===========================================================================
def test_valid_compose_all_guards_pass(tmp_path):
    checks = check_compose(_write_compose(tmp_path, lambda data: None))
    assert checks
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_compose_latest_image_fails_named(tmp_path):
    def mutate(data):
        data["services"]["n8n"]["image"] = "n8nio/n8n:latest"

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "imagen")


def test_compose_webhook_url_other_route_fails_named(tmp_path):
    def mutate(data):
        data["services"]["backend"]["environment"]["N8N_WEBHOOK_URL"] = (
            "http://n8n:5678/webhook/incidente-web"
        )

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "N8N_WEBHOOK_URL")


def test_compose_missing_executions_timeout_fails_named(tmp_path):
    def mutate(data):
        data["services"]["n8n"]["environment"].pop("EXECUTIONS_TIMEOUT", None)

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "EXECUTIONS_TIMEOUT")


def test_compose_incoherent_timeouts_fails_named(tmp_path):
    def mutate(data):
        data["services"]["n8n"]["environment"]["EXECUTIONS_TIMEOUT_MAX"] = "100"

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "EXECUTIONS_TIMEOUT_MAX")


# ===========================================================================
# W-1 (fix post-verificacion): el techo ausente debe FAIL, nunca PASS
# ===========================================================================
def test_compose_missing_executions_timeout_max_fails_named(tmp_path):
    """W-1: sin EXECUTIONS_TIMEOUT_MAX el preflight debe FAIL y salir 1."""
    def mutate(data):
        data["services"]["n8n"]["environment"].pop("EXECUTIONS_TIMEOUT_MAX", None)

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "EXECUTIONS_TIMEOUT_MAX")
    assert exit_code(checks) == 1


def test_compose_missing_both_timeouts_fails_without_false_pass(tmp_path):
    """W-1 triangulacion: sin ambas cotas hay un unico FAIL y exit 1."""
    def mutate(data):
        env = data["services"]["n8n"]["environment"]
        env.pop("EXECUTIONS_TIMEOUT", None)
        env.pop("EXECUTIONS_TIMEOUT_MAX", None)

    checks = check_compose(_write_compose(tmp_path, mutate))
    _assert_single_named_fail(checks, "EXECUTIONS_TIMEOUT")
    assert exit_code(checks) == 1


# ===========================================================================
# 1.8 Contrato de salida
# ===========================================================================
def test_exit_code_zero_only_when_all_pass():
    assert exit_code([Check("a", "PASS"), Check("b", "PASS")]) == 0
    assert exit_code([Check("a", "PASS"), Check("b", "FAIL", "falta")]) == 1
    assert exit_code([]) == 1


def test_format_summary_names_each_check():
    checks = [Check("guarda-uno", "PASS"), Check("guarda-dos", "FAIL", "ausente")]
    summary = format_summary(checks)
    assert "guarda-uno" in summary
    assert "guarda-dos" in summary


def test_run_preflight_combines_workflow_and_compose(tmp_path):
    compose = _write_compose(tmp_path, lambda data: None)
    checks = run_preflight(REAL_WORKFLOW_PATH, compose)
    assert any("AI Agent" in c.name for c in checks)
    assert any("EXECUTIONS_TIMEOUT" in c.name for c in checks)
    assert exit_code(checks) == 0


# ===========================================================================
# 2.3 Dependencia PyYAML ausente nunca produce falso PASS
# ===========================================================================
def test_yaml_missing_produces_actionable_fail(monkeypatch):
    monkeypatch.setattr(cost_readiness, "yaml", None)
    checks = check_compose(REAL_COMPOSE_PATH)
    fails = _fails(checks)
    assert fails, "La ausencia de PyYAML debe producir un FAIL, no un falso PASS"
    assert any("PyYAML" in (c.name + c.detail) for c in fails), _summary(checks)
    assert exit_code(checks) == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))