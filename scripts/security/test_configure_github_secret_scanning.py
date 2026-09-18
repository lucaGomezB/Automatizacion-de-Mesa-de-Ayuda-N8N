"""Tests del script `scripts/security/configure_github_secret_scanning.sh` (C-37).

El script es bash y habla con GitHub via `gh`. Para testearlo sin red se inyecta
un stub de `gh` por la variable `GH_BIN`: el stub registra cada invocacion en un
log JSON-lines y responde JSON configurable desde un archivo de estado.

Capas:
- Los tests verifican el contrato observable del script (salida y llamadas a
  `gh api`), no su implementacion interna.
- Sin red, sin credenciales, sin tocar GitHub.

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/security/test_configure_github_secret_scanning.py -q

Strict TDD: RED (script ausente) -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from types import SimpleNamespace

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "security" / "configure_github_secret_scanning.sh"
DEFAULT_REPO = "owner/repo"


# ---------------------------------------------------------------------------
# Stub de gh
# ---------------------------------------------------------------------------
# Se escribe en tmp_path y se ejecuta como `$GH_BIN`. Lee su estado de las
# variables de entorno STUB_GH_* inyectadas por el harness y registra cada
# invocacion como una linea JSON en STUB_GH_LOG.
GH_STUB = r'''#!/usr/bin/env python3
"""Stub de `gh` para tests sin red. No forma parte del producto."""
import json
import os
import sys

argv = sys.argv[1:]
method = "GET"
for i, arg in enumerate(argv):
    if arg in ("--method", "-X") and i + 1 < len(argv):
        method = argv[i + 1].upper()

fields = []
for i, arg in enumerate(argv):
    if arg in ("-f", "--raw-field", "-F", "--field") and i + 1 < len(argv):
        fields.append(argv[i + 1])

subcommand = argv[0] if argv else ""
endpoint = argv[1] if len(argv) > 1 and subcommand == "api" else subcommand

log_path = os.environ.get("STUB_GH_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "argv": argv,
            "method": method,
            "endpoint": endpoint,
            "fields": fields,
        }) + "\n")


def emit(payload):
    print(json.dumps(payload))
    sys.exit(0)


state = {}
state_path = os.environ.get("STUB_GH_STATE")
if state_path and os.path.exists(state_path):
    with open(state_path, encoding="utf-8") as handle:
        state = json.load(handle)

if endpoint == "repo":
    emit({"nameWithOwner": os.environ.get("STUB_GH_REPO", "owner/repo")})

if endpoint.startswith("repos/"):
    if "/secret-scanning/alerts" in endpoint:
        tail = endpoint.rstrip("/").split("/")[-1]
        if method == "PATCH" and tail.isdigit():
            emit({
                "number": int(tail),
                "state": "resolved",
                "resolution": state.get("resolution", "revoked"),
            })
        emit(state.get("alerts", []))
    if method == "PATCH":
        emit({})
    emit({
        "security_and_analysis": {
            "secret_scanning": {"status": state.get("secret_scanning", "enabled")},
            "secret_scanning_push_protection": {
                "status": state.get("push_protection", "enabled")
            },
            "secret_scanning_non_provider_patterns": {"status": "disabled"},
            "secret_scanning_validity_checks": {"status": "disabled"},
        }
    })

print(json.dumps({"error": "unhandled stub invocation", "argv": argv}), file=sys.stderr)
sys.exit(1)
'''


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------
@pytest.fixture
def harness(tmp_path):
    stub = tmp_path / "gh_stub.py"
    stub.write_text(GH_STUB, encoding="utf-8")
    stub.chmod(0o755)
    log = tmp_path / "gh-invocations.log"
    state_file = tmp_path / "gh-state.json"

    def run(args, state=None, gh_bin=None, repo=DEFAULT_REPO):
        assert SCRIPT.exists(), f"script not implemented yet: {SCRIPT}"
        if state is not None:
            state_file.write_text(json.dumps(state), encoding="utf-8")
        env = os.environ.copy()
        env["STUB_GH_LOG"] = str(log)
        env["STUB_GH_STATE"] = str(state_file)
        env["STUB_GH_REPO"] = repo
        env["GH_BIN"] = str(gh_bin) if gh_bin is not None else str(stub)
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def invocations():
        if not log.exists():
            return []
        return [
            json.loads(line)
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    return SimpleNamespace(
        run=run,
        invocations=invocations,
        log=log,
        stub=stub,
        state_file=state_file,
        tmp_path=tmp_path,
    )


def _output(result):
    return result.stdout + result.stderr


def _patches(invocations, endpoint=None):
    return [
        call
        for call in invocations
        if call["method"] == "PATCH" and (endpoint is None or call["endpoint"] == endpoint)
    ]


# ---------------------------------------------------------------------------
# 2.1 --dry-run
# ---------------------------------------------------------------------------
def test_dry_run_prints_api_ops_and_ui_steps_without_writing(harness):
    result = harness.run(
        ["--dry-run"],
        state={"secret_scanning": "disabled", "push_protection": "disabled"},
    )

    assert result.returncode == 0, _output(result)
    out = _output(result).lower()
    assert "secret_scanning_push_protection" in out
    assert "secret_scanning_non_provider_patterns" in out
    assert "secret_scanning_validity_checks" in out
    assert "dry-run" in out
    assert _patches(harness.invocations()) == []


# ---------------------------------------------------------------------------
# 2.2 Habilitacion
# ---------------------------------------------------------------------------
def test_enables_both_protections_when_disabled(harness):
    result = harness.run(
        [],
        state={"secret_scanning": "disabled", "push_protection": "disabled"},
    )

    assert result.returncode == 0, _output(result)
    patches = _patches(harness.invocations(), endpoint=f"repos/{DEFAULT_REPO}")
    assert len(patches) == 1
    fields = " ".join(patches[0]["fields"])
    assert "security_and_analysis[secret_scanning][status]=enabled" in fields
    assert (
        "security_and_analysis[secret_scanning_push_protection][status]=enabled" in fields
    )


# ---------------------------------------------------------------------------
# 2.3 Idempotencia
# ---------------------------------------------------------------------------
def test_idempotent_when_both_already_enabled(harness):
    result = harness.run(
        [],
        state={"secret_scanning": "enabled", "push_protection": "enabled"},
    )

    assert result.returncode == 0, _output(result)
    assert _patches(harness.invocations()) == []
    assert "habilitad" in _output(result).lower()


# ---------------------------------------------------------------------------
# 2.4 Funciones no disponibles (requieren plan pago)
# ---------------------------------------------------------------------------
def test_unavailable_features_are_reported(harness):
    result = harness.run(
        [],
        state={"secret_scanning": "enabled", "push_protection": "enabled"},
    )

    assert result.returncode == 0, _output(result)
    out = _output(result)
    assert "secret_scanning_non_provider_patterns" in out
    assert "secret_scanning_validity_checks" in out
    lowered = out.lower()
    assert "no disponibles" in lowered
    assert "plan pago" in lowered
    assert "no son configurables por api" in lowered


# ---------------------------------------------------------------------------
# 2.5 Entorno incompleto
# ---------------------------------------------------------------------------
def test_missing_gh_binary_fails_loudly(harness):
    result = harness.run(["--dry-run"], gh_bin=harness.tmp_path / "gh-does-not-exist")

    assert result.returncode != 0
    out = _output(result).lower()
    assert "gh" in out
    assert "error" in out
    assert "no se encontro" in out or "instal" in out


# ---------------------------------------------------------------------------
# 2.6 Resolucion opt-in
# ---------------------------------------------------------------------------
def test_resolution_without_confirm_does_not_patch_alert(harness):
    result = harness.run(
        ["--resolve-alert", "1", "--resolution", "revoked"],
        state={"secret_scanning": "enabled", "push_protection": "enabled"},
    )

    alert_patches = [
        call
        for call in harness.invocations()
        if call["method"] == "PATCH" and "secret-scanning/alerts" in call["endpoint"]
    ]
    assert alert_patches == []
    assert "--confirm" in _output(result)


def test_resolution_with_confirm_patches_alert(harness):
    result = harness.run(
        ["--resolve-alert", "1", "--resolution", "revoked", "--confirm"],
        state={"secret_scanning": "enabled", "push_protection": "enabled"},
    )

    assert result.returncode == 0, _output(result)
    alert_patches = _patches(
        harness.invocations(), endpoint=f"repos/{DEFAULT_REPO}/secret-scanning/alerts/1"
    )
    assert len(alert_patches) == 1
    fields = " ".join(alert_patches[0]["fields"])
    assert "state=resolved" in fields
    assert "resolution=revoked" in fields


# ---------------------------------------------------------------------------
# 4.1 TRIANGULATE — estado parcial
# ---------------------------------------------------------------------------
def test_partial_state_patches_only_the_missing_protection(harness):
    result = harness.run(
        [],
        state={"secret_scanning": "enabled", "push_protection": "disabled"},
    )

    assert result.returncode == 0, _output(result)
    patches = _patches(harness.invocations(), endpoint=f"repos/{DEFAULT_REPO}")
    assert len(patches) == 1
    fields = " ".join(patches[0]["fields"])
    assert (
        "security_and_analysis[secret_scanning_push_protection][status]=enabled" in fields
    )
    assert "security_and_analysis[secret_scanning][status]=enabled" not in fields


# ---------------------------------------------------------------------------
# 4.2 TRIANGULATE — repo explicito
# ---------------------------------------------------------------------------
def test_explicit_repo_is_used_in_endpoints(harness):
    result = harness.run(
        ["--repo", "acme/widgets"],
        state={"secret_scanning": "disabled", "push_protection": "disabled"},
    )

    assert result.returncode == 0, _output(result)
    endpoints = [call["endpoint"] for call in harness.invocations()]
    assert "repos/acme/widgets" in endpoints
    assert all(DEFAULT_REPO not in endpoint for endpoint in endpoints)
