"""Offline tests for the loopback token/page server of the dev softphone.

No network beyond an ephemeral loopback socket bound to 127.0.0.1. Every
credential is a synthetic placeholder.
"""

from __future__ import annotations

import contextlib
import http.client
import json
import threading

import jwt
import pytest

import mint_token as mt

ACCOUNT_SID = "AC" + "0" * 32
API_KEY_SID = "SK" + "1" * 32
API_KEY_SECRET = "placeholder-api-key-secret-000000000000"
TWIML_APP_SID = "AP" + "2" * 32

ENV = {
    "TWILIO_ACCOUNT_SID": ACCOUNT_SID,
    "TWILIO_API_KEY_SID": API_KEY_SID,
    "TWILIO_API_KEY_SECRET": API_KEY_SECRET,
    "TWILIO_TWIML_APP_SID": TWIML_APP_SID,
}


@pytest.fixture
def server():
    config = mt.load_config(ENV)
    httpd = mt.build_server(
        "127.0.0.1",
        0,
        config,
        identity="serve-operator",
        ttl_seconds=120,
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def _get(httpd, path):
    host, port = httpd.server_address[0], httpd.server_address[1]
    conn = http.client.HTTPConnection(host, port, timeout=5)
    conn.request("GET", path)
    response = conn.getresponse()
    body = response.read()
    conn.close()
    return response.status, body


# ── 3.1 RED: server serves page + fresh token, loopback only ────────────────


def test_binds_exclusively_to_loopback(server):
    assert server.server_address[0] == "127.0.0.1"


def test_refuses_non_loopback_binding():
    config = mt.load_config(ENV)
    with pytest.raises(ValueError):
        mt.build_server("0.0.0.0", 0, config, identity="op", ttl_seconds=60)


def test_root_returns_the_softphone_page(server):
    status, body = _get(server, "/")
    assert status == 200
    text = body.decode("utf-8")
    assert "<html" in text.lower()
    assert "Call" in text
    assert "Hangup" in text


def test_token_endpoint_returns_json_with_a_decodable_jwt(server):
    status, body = _get(server, "/token")
    assert status == 200
    payload = json.loads(body.decode("utf-8"))
    claims = jwt.decode(payload["token"], API_KEY_SECRET, algorithms=["HS256"])
    assert claims["grants"]["identity"] == "serve-operator"
    assert (
        claims["grants"]["voice"]["outgoing"]["application_sid"] == TWIML_APP_SID
    )


# ── 3.3 TRIANGULATE: fresh token per request + unknown route ────────────────


def test_token_is_minted_per_request_not_a_fixed_value(server, monkeypatch):
    # The SDK's ``jti`` has one-second resolution, so two rapid responses can
    # be byte-identical. The real contract is that a fresh token is MINTED on
    # every request rather than served from a cached constant.
    calls = []
    original = mt.mint_access_token

    def spy(config, identity, ttl_seconds=mt.DEFAULT_TTL_SECONDS):
        calls.append((identity, ttl_seconds))
        return original(config, identity, ttl_seconds=ttl_seconds)

    monkeypatch.setattr(mt, "mint_access_token", spy)
    _get(server, "/token")
    _get(server, "/token")
    assert calls == [("serve-operator", 120), ("serve-operator", 120)]


def test_unknown_route_returns_404(server):
    status, _ = _get(server, "/does-not-exist")
    assert status == 404


# ── 3.x: /case-status probe route (c-174, design.md D1/D5/D7) ───────────────


@contextlib.contextmanager
def _running_server(probe=None, probe_config=None):
    config = mt.load_config(ENV)
    httpd = mt.build_server(
        "127.0.0.1",
        0,
        config,
        identity="probe-operator",
        ttl_seconds=120,
        probe=probe,
        probe_config=probe_config,
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def _ready_probe(calls):
    def probe(case_id, since_ms):
        calls.append((case_id, since_ms))
        return {
            "listo": True,
            "transcripcion_estado": "transcrito",
            "incidente_id": 20,
            "latencia_e2e_ms": 6800,
        }

    return probe


def test_case_status_returns_probe_json_and_forwards_arguments():
    calls = []
    with _running_server(probe=_ready_probe(calls)) as server:
        status, body = _get(
            server, "/case-status?case_id=T1&since=1700000000000"
        )
    assert status == 200
    payload = json.loads(body.decode("utf-8"))
    assert payload == {
        "listo": True,
        "transcripcion_estado": "transcrito",
        "incidente_id": 20,
        "latencia_e2e_ms": 6800,
    }
    assert calls == [("T1", 1700000000000)]


def test_case_status_without_since_forwarded_as_none():
    calls = []
    with _running_server(probe=_ready_probe(calls)) as server:
        status, _ = _get(server, "/case-status?case_id=T1")
    assert status == 200
    assert calls == [("T1", None)]


def test_case_status_without_case_id_returns_400():
    with _running_server(probe=_ready_probe([])) as server:
        status, body = _get(server, "/case-status")
    assert status == 400
    payload = json.loads(body.decode("utf-8"))
    assert payload["error"]["code"] == "missing_case_id"


def test_case_status_without_probe_returns_503_probe_unconfigured():
    with _running_server(probe=None, probe_config=None) as server:
        status, body = _get(server, "/case-status?case_id=T1")
    assert status == 503
    payload = json.loads(body.decode("utf-8"))
    assert payload["error"]["code"] == "probe_unconfigured"


def test_case_status_probe_error_returns_502():
    def failing_probe(case_id, since_ms):
        raise mt.ProbeError("backend no disponible")

    with _running_server(probe=failing_probe) as server:
        status, body = _get(server, "/case-status?case_id=T1")
    assert status == 502
    payload = json.loads(body.decode("utf-8"))
    assert payload["error"]["code"] == "probe_error"
    assert "backend no disponible" in payload["error"]["message"]


def test_unknown_route_still_returns_404_when_probe_is_wired():
    with _running_server(probe=_ready_probe([])) as server:
        status, _ = _get(server, "/does-not-exist")
    assert status == 404


def test_case_status_does_not_log_case_content(capfd):
    with _running_server(probe=_ready_probe([])) as server:
        _get(server, "/case-status?case_id=T1&since=1700000000000")
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_build_server_creates_a_probe_client_from_config(monkeypatch):
    created = {}

    class FakeClient:
        def __init__(self, config, opener=None):
            created["config"] = config

        def status(self, case_id, since_ms=None):
            return {
                "listo": False,
                "transcripcion_estado": None,
                "incidente_id": None,
                "latencia_e2e_ms": None,
            }

    monkeypatch.setattr(mt, "ProbeClient", FakeClient)
    config = mt.load_config(ENV)
    probe_config = mt.ProbeConfig("https://backend.test", "operador", "pw", True)
    httpd = mt.build_server(
        "127.0.0.1",
        0,
        config,
        identity="op",
        ttl_seconds=60,
        probe_config=probe_config,
    )
    try:
        assert created["config"] is probe_config
        assert httpd.probe_config is probe_config
    finally:
        httpd.server_close()

