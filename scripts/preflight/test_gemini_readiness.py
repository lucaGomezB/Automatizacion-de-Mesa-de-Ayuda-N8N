"""Tests del preflight estatico de la superficie Gemini (c-58).

Logica pura: se verifica `scripts/preflight/gemini_readiness.py` leyendo el
artefacto real (`n8n/workflow.json`) y fixtures mutados en `tmp_path`. Sin red,
sin Docker y sin credenciales.

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/preflight/test_gemini_readiness.py -q

Strict TDD: RED (modulo ausente) -> GREEN -> TRIANGULATE (mutaciones) -> REFACTOR.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import gemini_readiness  # noqa: E402
from gemini_readiness import (  # noqa: E402
    Check,
    exit_code,
    format_summary,
    run_gemini_readiness,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REAL_WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"

GEMINI_MODEL_NODE_NAME = "Google Gemini Chat Model"
AI_AGENT_NODE_NAME = "AI Agent"


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


def _summary(checks) -> str:
    return " || ".join(f"{c.status}:{c.name}:{c.detail}" for c in checks)


def _fails(checks) -> list:
    return [c for c in checks if c.status == "FAIL"]


def _assert_fails_naming(checks, needle: str) -> None:
    fails = _fails(checks)
    assert fails, f"Se esperaba al menos un FAIL: {_summary(checks)}"
    assert any(needle in c.name or needle in c.detail for c in fails), (
        f"Los FAIL no nombran {needle!r}: {_summary(checks)}"
    )


# ===========================================================================
# Superficie pineada y resiliente
# ===========================================================================
def test_workflow_real_pasa_todas_las_guardas():
    checks = run_gemini_readiness(REAL_WORKFLOW_PATH)
    assert checks, "run_gemini_readiness debe devolver al menos un check"
    assert all(c.status == "PASS" for c in checks), _summary(checks)
    assert exit_code(checks) == 0


def test_modelo_implicito_falla_nombrado(tmp_path):
    def mutate(wf):
        _node(wf, GEMINI_MODEL_NODE_NAME)["parameters"].pop("modelName", None)

    checks = run_gemini_readiness(_write_workflow(tmp_path, mutate))
    _assert_fails_naming(checks, "modelName")
    assert exit_code(checks) == 1


def test_modelo_vacio_falla_nombrado(tmp_path):
    def mutate(wf):
        _node(wf, GEMINI_MODEL_NODE_NAME)["parameters"]["modelName"] = ""

    checks = run_gemini_readiness(_write_workflow(tmp_path, mutate))
    _assert_fails_naming(checks, "modelName")


def test_reintento_ausente_falla_nombrado(tmp_path):
    def mutate(wf):
        agent = _node(wf, AI_AGENT_NODE_NAME)
        agent.pop("retryOnFail", None)
        agent.pop("maxTries", None)
        agent.pop("waitBetweenTries", None)

    checks = run_gemini_readiness(_write_workflow(tmp_path, mutate))
    _assert_fails_naming(checks, "retryOnFail")
    assert exit_code(checks) == 1


def test_reintento_sin_cotas_falla_nombrado(tmp_path):
    def mutate(wf):
        agent = _node(wf, AI_AGENT_NODE_NAME)
        agent["retryOnFail"] = True
        agent.pop("maxTries", None)
        agent.pop("waitBetweenTries", None)

    checks = run_gemini_readiness(_write_workflow(tmp_path, mutate))
    _assert_fails_naming(checks, "maxTries")


def test_max_tries_fuera_del_tope_falla_nombrado(tmp_path):
    def mutate(wf):
        agent = _node(wf, AI_AGENT_NODE_NAME)
        agent["retryOnFail"] = True
        agent["maxTries"] = gemini_readiness.AGENT_MAX_TRIES_CAP + 1
        agent["waitBetweenTries"] = gemini_readiness.AGENT_MIN_WAIT_BETWEEN_TRIES_MS

    checks = run_gemini_readiness(_write_workflow(tmp_path, mutate))
    _assert_fails_naming(checks, "tope")


def test_workflow_ilegible_falla_sin_falso_pass(tmp_path):
    missing = tmp_path / "no-existe.json"
    checks = run_gemini_readiness(missing)
    assert exit_code(checks) == 1


# ===========================================================================
# El chequeo no usa red ni clave
# ===========================================================================
def test_el_modulo_no_referencia_la_clave_ni_red():
    source = pathlib.Path(gemini_readiness.__file__).read_text(encoding="utf-8").lower()
    assert "gemini_api_key" not in source, "El chequeo no debe requerir la clave"
    for network_token in ("import requests", "import httpx", "urllib.request"):
        assert network_token not in source, (
            f"El chequeo no debe usar red ({network_token!r})"
        )


def test_corre_sin_variables_de_entorno_de_gemini(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    checks = run_gemini_readiness(REAL_WORKFLOW_PATH)
    assert exit_code(checks) == 0


# ===========================================================================
# Contrato de salida
# ===========================================================================
def test_exit_code_solo_cero_si_todo_pasa():
    assert exit_code([Check("a", "PASS"), Check("b", "PASS")]) == 0
    assert exit_code([Check("a", "PASS"), Check("b", "FAIL", "falta")]) == 1
    assert exit_code([]) == 1


def test_format_summary_nombra_cada_check():
    summary = format_summary([Check("guarda-uno", "PASS"), Check("guarda-dos", "FAIL")])
    assert "guarda-uno" in summary
    assert "guarda-dos" in summary


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
