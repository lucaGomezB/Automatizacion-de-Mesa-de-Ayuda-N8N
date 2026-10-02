"""Offline tests for the loopback token/page server of the dev softphone.

No network beyond an ephemeral loopback socket bound to 127.0.0.1. Every
credential is a synthetic placeholder.
"""

from __future__ import annotations

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
