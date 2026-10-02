"""Scriptable Twilio setup for the development softphone (Twilio CLI).

Creates an API Key and a TwiML App whose Voice URL reuses the existing
backend voice endpoint, printing the resulting identifiers. The API Key
Secret is a ONE-TIME value: it is printed once and NEVER written to a
versioned file.

Authentication: the Twilio **Keys API requires account credentials**
(Account SID + Auth Token). A CLI *profile* stores an API Key, and an API Key
cannot manage the Keys resource (Twilio error ``70004``). The script therefore
reads ``TWILIO_ACCOUNT_SID`` and ``TWILIO_AUTH_TOKEN`` from the environment and
runs the CLI without ``--profile``, which is the supported path. An optional
``--profile`` is available for advanced users, but it will fail on the Keys
API unless the profile carries account credentials.

DEV TOOLING — not part of the production backend.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Callable, Mapping, Optional, Sequence, TextIO

# design.md D5/D7: default TwiML App voice URL reuses the existing endpoint on
# the reserved ngrok domain; overridable with an explicit flag.
DEFAULT_VOICE_URL = (
    "https://tameness-trilogy-unrefined.ngrok-free.dev"
    "/api/v1/cost-guard/twilio/voice"
)
DEFAULT_VOICE_METHOD = "POST"
DEFAULT_KEY_FRIENDLY_NAME = "mesa-dev-softphone"
DEFAULT_APP_FRIENDLY_NAME = "mesa-dev-softphone-twiML"

# design.md D8: the Keys API needs account credentials; a CLI profile storing an
# API Key would be rejected with error 70004. These are read from the env.
REQUIRED_ACCOUNT_ENV_VARS = ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")

CommandRunner = Callable[[Sequence[str]], "subprocess.CompletedProcess[str]"]


def default_runner(command: Sequence[str]) -> "subprocess.CompletedProcess[str]":
    """Run the Twilio CLI, capturing stdout/stderr as text."""

    return subprocess.run(list(command), capture_output=True, text=True)


def build_create_key_command(
    profile: Optional[str] = None,
    friendly_name: str = DEFAULT_KEY_FRIENDLY_NAME,
) -> list[str]:
    """Build the ``keys:create`` command.

    Without an explicit ``profile`` the CLI authenticates from the environment
    account credentials, which is the only path the Keys API accepts.
    """

    command = [
        "twilio",
        "api:core:keys:create",
        "--friendly-name",
        friendly_name,
    ]
    if profile is not None:
        command += ["--profile", profile]
    command += ["-o", "json"]
    return command


def build_create_app_command(
    voice_url: str = DEFAULT_VOICE_URL,
    profile: Optional[str] = None,
    voice_method: str = DEFAULT_VOICE_METHOD,
    friendly_name: str = DEFAULT_APP_FRIENDLY_NAME,
) -> list[str]:
    """Build the ``applications:create`` command (same auth path as the key)."""

    command = [
        "twilio",
        "api:core:applications:create",
        "--friendly-name",
        friendly_name,
        "--voice-url",
        voice_url,
        "--voice-method",
        voice_method,
    ]
    if profile is not None:
        command += ["--profile", profile]
    command += ["-o", "json"]
    return command


def parse_json_output(stdout: str) -> dict:
    """Parse the CLI JSON object, tolerating leading/trailing log lines."""

    text = stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
        raise


def describe_failure(result: "subprocess.CompletedProcess[str]") -> str:
    """Build an actionable detail from a failed CLI run.

    The Twilio CLI can exit non-zero while writing its structured error JSON to
    STDOUT and leaving STDERR empty. Prefer stderr when present, otherwise fall
    back to stdout, and include both streams when both carry content.
    """

    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    streams = [stream for stream in (stderr, stdout) if stream]
    if not streams:
        return "sin detalle del CLI (stderr y stdout vacios)"
    return " | ".join(streams)


def missing_account_credentials(
    environ: Optional[Mapping[str, str]] = None,
) -> list[str]:
    """Return the required account env vars that are absent or empty."""

    env = os.environ if environ is None else environ
    return [name for name in REQUIRED_ACCOUNT_ENV_VARS if not env.get(name)]


def run_setup(
    profile: Optional[str],
    voice_url: str,
    runner: CommandRunner,
    out: TextIO,
    err: TextIO,
    environ: Optional[Mapping[str, str]] = None,
) -> int:
    """Create the API Key then the TwiML App, printing identifiers.

    When ``profile`` is ``None`` the CLI uses the account credentials from the
    environment. If those are missing the run aborts (exit 2) with an
    actionable message, mirroring ``mint_token.py``'s ``ConfigError`` style.
    """

    if profile is None:
        missing = missing_account_credentials(environ)
        if missing:
            print(
                "Error: faltan credenciales de cuenta para autenticar el Twilio "
                "CLI: " + ", ".join(missing) + ". La Keys API exige Account SID + "
                "Auth Token; un perfil guarda un API Key y falla con 70004. "
                "Exporta TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN, o pasa --profile "
                "con credenciales de cuenta.",
                file=err,
            )
            return 2

    key_result = runner(build_create_key_command(profile=profile))
    if key_result.returncode != 0:
        print(
            f"Error: fallo al crear el API Key: {describe_failure(key_result)}",
            file=err,
        )
        return 1
    key_data = parse_json_output(key_result.stdout)
    print(f"API Key SID: {key_data.get('sid', '')}", file=out)
    print(
        "API Key Secret (se muestra una sola vez, capturalo en el entorno): "
        f"{key_data.get('secret', '')}",
        file=out,
    )

    app_result = runner(build_create_app_command(voice_url=voice_url, profile=profile))
    if app_result.returncode != 0:
        print(
            f"Error: fallo al crear el TwiML App: {describe_failure(app_result)}",
            file=err,
        )
        return 1
    app_data = parse_json_output(app_result.stdout)
    print(f"TwiML App SID: {app_data.get('sid', '')}", file=out)
    print(
        "Carga estos valores en variables de entorno; NO escribas el secret a "
        "ningun archivo versionado.",
        file=out,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="setup_twilio.py",
        description="Crea el API Key y el TwiML App para el softphone dev.",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help=(
            "Perfil OPCIONAL del Twilio CLI. Advertencia: un perfil guarda un "
            "API Key, que no puede gestionar la Keys API (error 70004); el "
            "default sin --profile usa TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN del "
            "entorno, que es el camino soportado."
        ),
    )
    parser.add_argument(
        "--voice-url",
        default=DEFAULT_VOICE_URL,
        help="Voice URL del TwiML App (default: endpoint de voz en ngrok).",
    )
    return parser


def run(
    argv: Optional[Sequence[str]] = None,
    runner: Optional[CommandRunner] = None,
    out: Optional[TextIO] = None,
    err: Optional[TextIO] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> int:
    """CLI entry point. Returns a process exit code (0 on success)."""

    stdout = sys.stdout if out is None else out
    stderr = sys.stderr if err is None else err
    active_runner = default_runner if runner is None else runner

    args = build_parser().parse_args(argv)
    return run_setup(
        profile=args.profile,
        voice_url=args.voice_url,
        runner=active_runner,
        out=stdout,
        err=stderr,
        environ=environ,
    )


if __name__ == "__main__":  # pragma: no cover - CLI wiring
    raise SystemExit(run())
