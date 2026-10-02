"""Offline tests for the scriptable Twilio setup helper.

The Twilio CLI is injected as a fake runner: no real process, no network, no
credentials. Assertions cover command construction, the resolved voice URL
and that the one-time secret is never persisted to a file.
"""

from __future__ import annotations

import io
import json
import subprocess

import setup_twilio as st

KEY_JSON = json.dumps(
    {
        "sid": "SK" + "1" * 32,
        "secret": "placeholder-secret-shown-once",
        "friendly_name": "mesa-dev-softphone",
    }
)
APP_JSON = json.dumps(
    {
        "sid": "AP" + "2" * 32,
        "friendly_name": "mesa-dev-softphone-twiML",
    }
)


class FakeRunner:
    """Records commands and replays canned outputs or failures."""

    def __init__(self, results):
        self.commands = []
        self._results = list(results)

    def __call__(self, command):
        self.commands.append(command)
        result = self._results.pop(0)
        if isinstance(result, int):
            return subprocess.CompletedProcess(command, result, stdout="", stderr="boom")
        return subprocess.CompletedProcess(command, 0, stdout=result, stderr="")


# ── 4.1 RED: command construction with profile and POST method ──────────────


def test_create_key_command_uses_profile_and_json_output():
    command = st.build_create_key_command(profile="Luca")
    assert command[0] == "twilio"
    assert "api:core:keys:create" in command
    assert "--profile" in command
    assert command[command.index("--profile") + 1] == "Luca"
    assert command[command.index("-o") + 1] == "json"


# ── RED: account-auth default (the Keys API needs account credentials) ────────
#
# A CLI profile stores an API Key, which cannot manage the Keys resource
# (Twilio error 70004). The supported path is account credentials from the
# environment: no --profile by default, so the CLI resolves them from env.

ACCOUNT_ENV = {
    "TWILIO_ACCOUNT_SID": "AC" + "0" * 32,
    "TWILIO_AUTH_TOKEN": "placeholder-auth-token",
}


def test_create_key_command_has_no_profile_by_default():
    command = st.build_create_key_command()
    assert command[0] == "twilio"
    assert "api:core:keys:create" in command
    assert "--profile" not in command
    assert command[command.index("-o") + 1] == "json"


def test_create_app_command_has_no_profile_by_default():
    command = st.build_create_app_command()
    assert "api:core:applications:create" in command
    assert "--profile" not in command


def test_run_without_profile_and_missing_env_aborts():
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run([], runner=runner, out=out, err=err, environ={})
    assert code != 0
    assert "TWILIO_ACCOUNT_SID" in err.getvalue()
    assert "TWILIO_AUTH_TOKEN" in err.getvalue()
    assert runner.commands == []  # the CLI is never invoked without credentials


def test_run_with_profile_flag_is_passed_through():
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run(
        ["--profile", "mesa-admin"], runner=runner, out=out, err=err, environ={}
    )
    assert code == 0
    key_command = runner.commands[0]
    assert key_command[key_command.index("--profile") + 1] == "mesa-admin"


def test_create_app_command_sets_voice_url_and_post_method():
    command = st.build_create_app_command(
        voice_url="https://example.test/api/v1/cost-guard/twilio/voice",
        profile="Luca",
    )
    assert "api:core:applications:create" in command
    assert command[command.index("--voice-url") + 1] == (
        "https://example.test/api/v1/cost-guard/twilio/voice"
    )
    assert command[command.index("--voice-method") + 1] == "POST"
    assert command[command.index("--profile") + 1] == "Luca"


def test_run_setup_prints_sids_and_secret_once():
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 0
    text = out.getvalue()
    assert "SK" + "1" * 32 in text
    assert "AP" + "2" * 32 in text
    assert text.count("placeholder-secret-shown-once") == 1


# ── 4.3 TRIANGULATE: defaults, override, no secret on disk ──────────────────


def test_default_voice_url_is_the_reserved_ngrok_endpoint():
    assert st.DEFAULT_VOICE_URL == (
        "https://tameness-trilogy-unrefined.ngrok-free.dev"
        "/api/v1/cost-guard/twilio/voice"
    )
    command = st.build_create_app_command()
    assert command[command.index("--voice-url") + 1] == st.DEFAULT_VOICE_URL


def test_voice_url_override_is_reflected_in_the_command():
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    st.run_setup(
        profile="Luca",
        voice_url="https://override.test/voice",
        runner=runner,
        out=out,
        err=err,
    )
    app_command = runner.commands[1]
    assert app_command[app_command.index("--voice-url") + 1] == (
        "https://override.test/voice"
    )


def test_setup_does_not_write_any_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 0
    assert list(tmp_path.iterdir()) == []


def test_cli_reports_cli_failure_with_nonzero_exit():
    runner = FakeRunner([1])
    out, err = io.StringIO(), io.StringIO()
    code = st.run(["--profile", "Luca"], runner=runner, out=out, err=err)
    assert code != 0
    assert "Error" in err.getvalue() or "error" in err.getvalue().lower()


# ── TRIANGULATE: env-auth success and partial-missing env ────────────────────


def test_run_with_env_credentials_succeeds_without_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run([], runner=runner, out=out, err=err, environ=dict(ACCOUNT_ENV))
    assert code == 0
    assert "--profile" not in runner.commands[0]
    assert "--profile" not in runner.commands[1]
    text = out.getvalue()
    assert "SK" + "1" * 32 in text
    assert "AP" + "2" * 32 in text
    assert text.count("placeholder-secret-shown-once") == 1
    assert list(tmp_path.iterdir()) == []


def test_run_with_only_account_sid_missing_auth_token_aborts():
    env = {"TWILIO_ACCOUNT_SID": ACCOUNT_ENV["TWILIO_ACCOUNT_SID"]}
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run([], runner=runner, out=out, err=err, environ=env)
    assert code != 0
    assert "TWILIO_AUTH_TOKEN" in err.getvalue()
    assert runner.commands == []


def test_run_with_only_auth_token_missing_account_sid_aborts():
    env = {"TWILIO_AUTH_TOKEN": ACCOUNT_ENV["TWILIO_AUTH_TOKEN"]}
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run([], runner=runner, out=out, err=err, environ=env)
    assert code != 0
    assert "TWILIO_ACCOUNT_SID" in err.getvalue()
    assert runner.commands == []


def test_run_with_empty_env_values_aborts():
    env = {"TWILIO_ACCOUNT_SID": "", "TWILIO_AUTH_TOKEN": ""}
    runner = FakeRunner([KEY_JSON, APP_JSON])
    out, err = io.StringIO(), io.StringIO()
    code = st.run([], runner=runner, out=out, err=err, environ=env)
    assert code != 0
    assert "TWILIO_ACCOUNT_SID" in err.getvalue()
    assert "TWILIO_AUTH_TOKEN" in err.getvalue()


# ── 5.2 RED/TRIANGULATE: surface structured errors written to stdout ─────────
#
# The Twilio CLI can exit non-zero writing its structured error JSON to STDOUT
# while STDERR stays empty (observed: exit 70, stderr 0 bytes). The failure
# message must surface whichever stream carries the detail.

KEY_ERROR_JSON = json.dumps(
    [
        {
            "code": 70004,
            "message": (
                "The provided key does not have the permissions to access "
                "this endpoint"
            ),
            "more_info": "https://www.twilio.com/docs/errors/70004",
            "status": 401,
        }
    ]
)


def _failure_runner(returncode, stdout, stderr):
    def _run(command):
        return subprocess.CompletedProcess(
            command, returncode, stdout=stdout, stderr=stderr
        )

    return _run


def test_key_failure_surfaces_stdout_when_stderr_is_empty():
    runner = _failure_runner(70, stdout=KEY_ERROR_JSON, stderr="")
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 1
    assert "fallo al crear el API Key" in err.getvalue()
    assert "70004" in err.getvalue()
    assert "permissions" in err.getvalue()


def test_key_failure_surfaces_stderr_when_stdout_is_empty():
    runner = _failure_runner(1, stdout="", stderr="network unreachable")
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 1
    assert "fallo al crear el API Key" in err.getvalue()
    assert "network unreachable" in err.getvalue()


def test_key_failure_includes_both_streams_when_present():
    runner = _failure_runner(1, stdout="stdout detail", stderr="stderr detail")
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 1
    assert "stderr detail" in err.getvalue()
    assert "stdout detail" in err.getvalue()


def test_key_failure_with_empty_streams_reports_placeholder():
    runner = _failure_runner(1, stdout="", stderr="")
    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca", voice_url=st.DEFAULT_VOICE_URL, runner=runner, out=out, err=err
    )
    assert code == 1
    assert "fallo al crear el API Key" in err.getvalue()
    assert "sin detalle" in err.getvalue()


def test_app_failure_surfaces_stdout_when_stderr_is_empty():
    def combined_runner(command):
        if command[1] == "api:core:keys:create":
            return subprocess.CompletedProcess(command, 0, stdout=KEY_JSON, stderr="")
        return subprocess.CompletedProcess(
            command, 70, stdout=KEY_ERROR_JSON, stderr=""
        )

    out, err = io.StringIO(), io.StringIO()
    code = st.run_setup(
        profile="Luca",
        voice_url=st.DEFAULT_VOICE_URL,
        runner=combined_runner,
        out=out,
        err=err,
    )
    assert code == 1
    assert "fallo al crear el TwiML App" in err.getvalue()
    assert "70004" in err.getvalue()
