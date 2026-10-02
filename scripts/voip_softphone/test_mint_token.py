"""Offline unit tests for the local Twilio Access Token minting utility.

No network, no real credentials, no real Twilio account. Every secret used
here is a synthetic placeholder. The tests decode the minted JWT with the
API Key Secret and assert the claim shape required by the spec
(``telephony-test-softphone``).
"""

from __future__ import annotations

import io
import time

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
