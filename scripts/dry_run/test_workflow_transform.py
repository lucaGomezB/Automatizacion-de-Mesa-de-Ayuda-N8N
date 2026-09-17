"""Unit tests for the cost-zero workflow transformation in dry_run.py.

``_workflow_for_dry_run`` rewrites ``n8n/workflow.json`` into a credential-free
copy that a fresh N8N can activate. The most failure-prone part is inlining the
login node: HTTP Request v4.4 sends a JSON body ONLY when ``specifyBody='json'``
and ``jsonBody`` are set. Setting a bare ``body`` field is silently ignored and
N8N falls back to the default ``keypair`` body (a single empty ``{"": ""}``
pair), which the backend rejects with HTTP 422.

Run with:
    cd scripts/dry_run && python -m pytest test_workflow_transform.py -q
or from the repo root:
    python -m pytest scripts/dry_run/test_workflow_transform.py -q
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dry_run


USERNAME = "admin"
PASSWORD = "admin123"


def _login_node() -> dict:
    workflow, _ = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    nodes = {node["name"]: node for node in workflow["nodes"]}
    return nodes["Login operador"]


def test_login_node_sends_json_body_via_specify_body():
    parameters = _login_node()["parameters"]
    assert parameters["sendBody"] is True
    assert parameters["contentType"] == "json"
    assert parameters["specifyBody"] == "json"


def test_login_node_json_body_carries_operator_credentials():
    parameters = _login_node()["parameters"]
    parsed = json.loads(parameters["jsonBody"])
    assert parsed == {"username": USERNAME, "password": PASSWORD}


def test_login_node_has_no_empty_keypair_body():
    parameters = _login_node()["parameters"]
    assert "bodyParameters" not in parameters
    assert "body" not in parameters


def test_login_node_has_no_credential_reference():
    node = _login_node()
    assert "credentials" not in node
    assert "authentication" not in node
    assert "genericAuthType" not in node


def test_removed_nodes_have_no_inbound_edges():
    workflow, removed = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    for value in workflow["connections"].values():
        for branch in value.get("main", []):
            for edge in branch or []:
                assert edge["node"] not in removed


def test_http_post_node_has_no_credential_authentication():
    workflow, _ = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    nodes = {node["name"]: node for node in workflow["nodes"]}
    node = nodes["HTTP POST a MTM-SRU"]
    assert "credentials" not in node
    assert node["parameters"].get("authentication") != "genericCredentialType"
    assert "genericAuthType" not in node["parameters"]


def test_http_post_node_keeps_explicit_authorization_header():
    workflow, _ = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    nodes = {node["name"]: node for node in workflow["nodes"]}
    header = nodes["HTTP POST a MTM-SRU"]["parameters"]["headerParameters"]["parameters"]
    assert any(
        entry["name"] == "Authorization" and "access_token" in entry["value"]
        for entry in header
    )


def test_http_post_node_sends_payload_as_json_expression():
    workflow, _ = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    nodes = {node["name"]: node for node in workflow["nodes"]}
    parameters = nodes["HTTP POST a MTM-SRU"]["parameters"]
    assert parameters["specifyBody"] == "json"
    assert "body" not in parameters
    json_body = parameters["jsonBody"]
    assert json_body.startswith("={{")
    assert "JSON.stringify" in json_body
    for expression in (
        "$('Normalizar entrada del incidente').item.json.descripcion",
        "$('Normalizar entrada del incidente').item.json.prioridad || 'media'",
        "$('Normalizar entrada del incidente').item.json.canal_origen_id",
    ):
        assert expression in json_body


def test_web_channel_path_is_preserved():
    workflow, _ = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    names = {node["name"] for node in workflow["nodes"]}
    assert "Confirmacion web al usuario" in names
    assert "Rutear por canal de origen" in names
    assert "Webhook formulario web" in names


# ── Twilio guardrail (§8.2) ──────────────────────────────────────────────────


def test_twilio_trigger_is_removed_from_the_dry_run_workflow():
    workflow, removed = dry_run._workflow_for_dry_run(USERNAME, PASSWORD)
    assert "Llamada telefonica" in removed
    remaining = {node.get("type", "").lower() for node in workflow["nodes"]}
    assert not any("twilio" in node_type for node_type in remaining)
    assert not any("llamada" in node.get("name", "").lower() for node in workflow["nodes"])


def test_harness_source_never_invokes_the_twilio_api():
    source = (Path(dry_run.__file__).read_text(encoding="utf-8")).lower()
    for forbidden in ("import twilio", "from twilio", "twilio.rest", "api.twilio.com", "twilioclient"):
        assert forbidden not in source
