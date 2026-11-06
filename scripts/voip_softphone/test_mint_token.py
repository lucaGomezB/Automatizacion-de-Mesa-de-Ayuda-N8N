"""Offline unit tests for the local Twilio Access Token minting utility.

No network, no real credentials, no real Twilio account. Every secret used
here is a synthetic placeholder. The tests decode the minted JWT with the
API Key Secret and assert the claim shape required by the spec
(``telephony-test-softphone``).
"""

from __future__ import annotations

import io
import json
import time
import urllib.error
import urllib.request

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


def _decode(token: str) -> dict:
    return jwt.decode(token, API_KEY_SECRET, algorithms=["HS256"])


# ── 2.1 RED: token shape ────────────────────────────────────────────────────


def test_token_header_is_hs256():
    config = mt.load_config(ENV)
    token = mt.mint_access_token(config, "operator-1")  # gitleaks:allow
    assert jwt.get_unverified_header(token)["alg"] == "HS256"


def test_token_declares_issuer_and_subject():
    config = mt.load_config(ENV)
    token = mt.mint_access_token(config, "operator-1")  # gitleaks:allow
    claims = _decode(token)
    assert claims["iss"] == API_KEY_SID
    assert claims["sub"] == ACCOUNT_SID


def test_token_voice_grant_declares_application_and_identity():
    config = mt.load_config(ENV)
    token = mt.mint_access_token(config, "operator-1")  # gitleaks:allow
    claims = _decode(token)
    assert claims["grants"]["identity"] == "operator-1"
    assert (
        claims["grants"]["voice"]["outgoing"]["application_sid"] == TWIML_APP_SID
    )


def test_token_expiry_is_future_and_bounded():
    config = mt.load_config(ENV)
    now = int(time.time())
    token = mt.mint_access_token(config, "operator-1")  # gitleaks:allow
    claims = _decode(token)
    assert claims["exp"] > now
    assert claims["exp"] <= now + mt.DEFAULT_TTL_SECONDS + 5


# ── 2.3 TRIANGULATE: identity, TTL, CLI ─────────────────────────────────────


def test_default_identity_is_unique_per_session():
    first = mt.generate_identity()
    second = mt.generate_identity()
    assert first.startswith("softphone-dev-")
    assert second.startswith("softphone-dev-")
    assert first != second


def test_explicit_identity_is_reflected_in_grant():
    config = mt.load_config(ENV)
    token = mt.mint_access_token(config, "explicit-operator")  # gitleaks:allow
    assert _decode(token)["grants"]["identity"] == "explicit-operator"


def test_configured_ttl_bounds_the_token_lifetime():
    config = mt.load_config(ENV)
    token = mt.mint_access_token(config, "operator-1", ttl_seconds=120)  # gitleaks:allow
    claims = _decode(token)
    assert claims["exp"] - claims["nbf"] == 120


def test_cli_token_mode_prints_a_decodable_token():
    out, err = io.StringIO(), io.StringIO()
    code = mt.run(
        ["token", "--identity", "cli-operator", "--ttl", "120"],
        environ=ENV,
        out=out,
        err=err,
    )
    assert code == 0
    token = out.getvalue().strip()
    claims = _decode(token)
    assert claims["grants"]["identity"] == "cli-operator"
    assert claims["exp"] - claims["nbf"] == 120


def test_cli_token_mode_defaults_identity_to_unique_session_value():
    out, err = io.StringIO(), io.StringIO()
    assert mt.run(["token"], environ=ENV, out=out, err=err) == 0
    identity = _decode(out.getvalue().strip())["grants"]["identity"]
    assert identity.startswith("softphone-dev-")


# ── 2.4 RED: environment validation ─────────────────────────────────────────


def test_load_config_missing_env_raises_config_error():
    with pytest.raises(mt.ConfigError) as excinfo:
        mt.load_config({})
    message = str(excinfo.value)
    for variable in mt.REQUIRED_ENV_VARS:
        assert variable in message


def test_load_config_reports_only_the_missing_variable():
    partial = dict(ENV)
    del partial["TWILIO_TWIML_APP_SID"]
    with pytest.raises(mt.ConfigError) as excinfo:
        mt.load_config(partial)
    assert "TWILIO_TWIML_APP_SID" in str(excinfo.value)
    assert "TWILIO_ACCOUNT_SID" not in str(excinfo.value)


def test_cli_aborts_with_nonzero_exit_when_env_is_missing():
    out, err = io.StringIO(), io.StringIO()
    code = mt.run(["token"], environ={}, out=out, err=err)
    assert code != 0
    assert out.getvalue() == ""
    assert "TWILIO_ACCOUNT_SID" in err.getvalue()


def test_load_config_reads_only_from_supplied_environ():
    # Real process environment must not leak into an explicit empty mapping.
    config = mt.load_config(ENV)
    assert config.account_sid == ACCOUNT_SID
    assert config.api_key_secret == API_KEY_SECRET


# ── 1.x: pure case-status decision (c-174, design.md D2/D3) ─────────────────


def _ingreso(**overrides) -> dict:
    """A ``TelefoniaIngresoRead``-shaped payload with synthetic values."""

    payload = {
        "id": 8,
        "call_sid": "CA" + "3" * 32,
        "corpus_case_id": "T1",
        "transcripcion_estado": "transcrito",
        "ingresado_en": "2026-11-06T12:00:00+00:00",
        "persistido_en": "2026-11-06T12:00:07+00:00",
        "incidente_id": 20,
        "latencia_e2e_ms": 6800,
        "duracion_segundos": 18,
    }
    payload.update(overrides)
    return payload


def test_evaluate_case_status_ready_when_ingreso_has_incidente():
    result = mt.evaluate_case_status(_ingreso())
    assert result == {
        "listo": True,
        "transcripcion_estado": "transcrito",
        "incidente_id": 20,
        "latencia_e2e_ms": 6800,
    }


def test_evaluate_case_status_without_ingreso_is_not_ready():
    result = mt.evaluate_case_status(None)
    assert result == {
        "listo": False,
        "transcripcion_estado": None,
        "incidente_id": None,
        "latencia_e2e_ms": None,
    }


def test_evaluate_case_status_without_incidente_is_not_ready():
    result = mt.evaluate_case_status(
        _ingreso(incidente_id=None, latencia_e2e_ms=None)
    )
    assert result["listo"] is False
    assert result["incidente_id"] is None


def test_evaluate_case_status_terminal_error_exposes_estado_and_stays_not_ready():
    result = mt.evaluate_case_status(
        _ingreso(
            incidente_id=None,
            latencia_e2e_ms=None,
            transcripcion_estado="error_stt",
        )
    )
    assert result["listo"] is False
    assert result["transcripcion_estado"] == "error_stt"


def test_evaluate_case_status_discards_ingreso_older_than_since():
    # Retry (D3): a fresh ``since`` (epoch ms) invalidates the previous run.
    since_ms = mt._parse_iso_to_epoch_ms("2026-11-06T12:00:30+00:00")
    result = mt.evaluate_case_status(_ingreso(), since_ms=since_ms)
    assert result["listo"] is False


def test_evaluate_case_status_accepts_ingreso_at_or_after_since():
    since_ms = mt._parse_iso_to_epoch_ms("2026-11-06T12:00:00+00:00")
    result = mt.evaluate_case_status(_ingreso(), since_ms=since_ms)
    assert result["listo"] is True


def test_parse_iso_to_epoch_ms_accepts_zulu_timestamps():
    assert mt._parse_iso_to_epoch_ms("1970-01-01T00:00:01Z") == 1000


def test_parse_iso_to_epoch_ms_returns_none_for_missing_value():
    assert mt._parse_iso_to_epoch_ms(None) is None
    assert mt._parse_iso_to_epoch_ms("no-es-fecha") is None


# ── 2.x: probe config + transport (c-174, design.md D4/D5/D8) ───────────────


PROBE_ENV = {
    "INGEST_OPERATOR_USERNAME": "operador-sonda",
    "INGEST_OPERATOR_PASSWORD": "placeholder-sonda-pw",
}


class _FakeOpener:
    """Deterministic opener: replays canned ``(status, body)`` tuples."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []

    def __call__(self, request, config):
        self.requests.append(request)
        return self._responses.pop(0)

    def methods(self):
        return [request.get_method() for request in self.requests]


def _probe_config(**overrides):
    values = {
        "backend_base_url": "https://backend.test",
        "username": "operador-sonda",
        "password": "placeholder-sonda-pw",
        "insecure": True,
    }
    values.update(overrides)
    return mt.ProbeConfig(**values)


def test_load_probe_config_reads_credentials_and_flags():
    config = mt.load_probe_config(PROBE_ENV, "https://backend.test", True)
    assert config is not None
    assert config.username == "operador-sonda"
    assert config.password == "placeholder-sonda-pw"
    assert config.backend_base_url == "https://backend.test"
    assert config.insecure is True


def test_load_probe_config_absent_credentials_returns_none():
    assert mt.load_probe_config({}, "https://localhost", False) is None


def test_load_probe_config_partial_credentials_raises_config_error():
    with pytest.raises(mt.ConfigError) as excinfo:
        mt.load_probe_config(
            {"INGEST_OPERATOR_USERNAME": "operador-sonda"},
            "https://localhost",
            False,
        )
    assert "INGEST_OPERATOR_PASSWORD" in str(excinfo.value)
    assert "placeholder" not in str(excinfo.value)


def test_probe_config_repr_and_str_never_expose_password():
    config = _probe_config(password="secreto-muy-secreto")
    assert "secreto-muy-secreto" not in repr(config)
    assert "secreto-muy-secreto" not in str(config)


def test_login_backend_extracts_access_token():
    opener = _FakeOpener(
        [(200, json.dumps({"access_token": "jwt-1"}).encode("utf-8"))]
    )
    assert mt.login_backend(_probe_config(), opener) == "jwt-1"
    assert opener.methods() == ["POST"]


def test_fetch_ingreso_returns_status_and_payload():
    opener = _FakeOpener([(200, json.dumps(_ingreso()).encode("utf-8"))])
    status, payload = mt.fetch_ingreso(_probe_config(), "jwt-1", "T1", opener)
    assert status == 200
    assert payload["incidente_id"] == 20
    assert opener.methods() == ["GET"]


def test_fetch_ingreso_404_returns_none_payload():
    opener = _FakeOpener([(404, b"")])
    status, payload = mt.fetch_ingreso(_probe_config(), "jwt-1", "T1", opener)
    assert status == 404
    assert payload is None


def test_probe_client_relogins_once_on_401_and_retries():
    opener = _FakeOpener(
        [
            (200, json.dumps({"access_token": "jwt-1"}).encode("utf-8")),
            (401, b""),
            (200, json.dumps({"access_token": "jwt-2"}).encode("utf-8")),
            (200, json.dumps(_ingreso()).encode("utf-8")),
        ]
    )
    client = mt.ProbeClient(_probe_config(), opener)
    result = client.status("T1", None)
    assert result["listo"] is True
    assert opener.methods() == ["POST", "GET", "POST", "GET"]


def test_probe_client_propagates_5xx_as_probe_error():
    opener = _FakeOpener(
        [
            (200, json.dumps({"access_token": "jwt-1"}).encode("utf-8")),
            (503, b""),
        ]
    )
    client = mt.ProbeClient(_probe_config(), opener)
    with pytest.raises(mt.ProbeError):
        client.status("T1", None)


def test_probe_client_caches_token_across_calls():
    opener = _FakeOpener(
        [
            (200, json.dumps({"access_token": "jwt-1"}).encode("utf-8")),
            (200, json.dumps(_ingreso()).encode("utf-8")),
            (200, json.dumps(_ingreso()).encode("utf-8")),
        ]
    )
    client = mt.ProbeClient(_probe_config(), opener)
    client.status("T1", None)
    client.status("T1", None)
    assert opener.methods() == ["POST", "GET", "GET"]


def test_default_opener_wraps_network_errors_as_probe_error(monkeypatch):
    def boom(*args, **kwargs):
        raise urllib.error.URLError("sin red")

    monkeypatch.setattr(mt.urllib.request, "urlopen", boom)
    request = urllib.request.Request("https://backend.test/algo")
    with pytest.raises(mt.ProbeError):
        mt._default_opener(request, _probe_config())


def test_probe_client_surfaces_network_errors_as_probe_error():
    def boom(request, config):
        raise mt.ProbeError("No se pudo contactar el backend")

    client = mt.ProbeClient(_probe_config(), boom)
    with pytest.raises(mt.ProbeError):
        client.status("T1", None)



# ── 6.x: `serve` CLI probe flags (c-174, design.md D1/D5) ───────────────────


def test_serve_parser_defaults_for_probe_options():
    args = mt.build_parser().parse_args(["serve"])
    assert args.backend_base_url == "https://localhost"
    assert args.insecure is False


def test_serve_parser_accepts_probe_options():
    args = mt.build_parser().parse_args(
        ["serve", "--backend-base-url", "https://backend.test", "--insecure"]
    )
    assert args.backend_base_url == "https://backend.test"
    assert args.insecure is True


def _stub_build_server(monkeypatch, captured):
    class FakeServer:
        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            pass

    def fake_build_server(host, port, config, identity, **kwargs):
        captured.update(kwargs)
        captured["host"] = host
        return FakeServer()

    monkeypatch.setattr(mt, "build_server", fake_build_server)


def test_serve_propagates_probe_config_from_environment(monkeypatch):
    captured = {}
    _stub_build_server(monkeypatch, captured)
    env = dict(ENV)
    env.update(PROBE_ENV)
    out, err = io.StringIO(), io.StringIO()
    assert mt.run(["serve", "--insecure"], environ=env, out=out, err=err) == 0
    probe = captured["probe_config"]
    assert isinstance(probe, mt.ProbeConfig)
    assert probe.username == "operador-sonda"
    assert probe.insecure is True
    assert probe.backend_base_url == "https://localhost"


def test_serve_without_probe_credentials_stays_operational(monkeypatch):
    captured = {}
    _stub_build_server(monkeypatch, captured)
    out, err = io.StringIO(), io.StringIO()
    assert mt.run(["serve"], environ=dict(ENV), out=out, err=err) == 0
    assert captured["probe_config"] is None


def test_serve_partial_probe_credentials_warn_and_disable_probe(monkeypatch):
    captured = {}
    _stub_build_server(monkeypatch, captured)
    env = dict(ENV)
    env["INGEST_OPERATOR_USERNAME"] = "operador-sonda"
    out, err = io.StringIO(), io.StringIO()
    assert mt.run(["serve"], environ=env, out=out, err=err) == 0
    assert captured["probe_config"] is None
    assert "INGEST_OPERATOR" in err.getvalue()



