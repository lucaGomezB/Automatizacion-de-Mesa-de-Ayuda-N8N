"""Local Twilio Access Token minting for the development softphone.

This is DEV TOOLING, not production code. It reads every credential
exclusively from environment variables, mints a short-lived Twilio Access
Token locally (no network) and, in ``serve`` mode, serves the static
softphone page plus a fresh token from loopback.

Secrets are never hardcoded and never written to a versioned file. See
``README.md`` for the operating guide.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping, Optional, Sequence, TextIO

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

# Default bounded lifetime for a minted token (design.md D7).
DEFAULT_TTL_SECONDS = 1800

# Identity prefix; a per-session timestamp suffix keeps the cost-guard
# per-origin rate key (``client:<identity>``) from exhausting repeated tests.
IDENTITY_PREFIX = "softphone-dev-"

# Credentials are read ONLY from these variables.
REQUIRED_ENV_VARS = (
    "TWILIO_ACCOUNT_SID",
    "TWILIO_API_KEY_SID",
    "TWILIO_API_KEY_SECRET",
    "TWILIO_TWIML_APP_SID",
)

# The server MUST listen only on loopback; anything else is refused.
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

# Static page served by ``serve`` mode (same origin as ``/token``).
HTML_FILENAME = "softphone.html"
DEFAULT_SERVE_HOST = "127.0.0.1"
DEFAULT_SERVE_PORT = 8765


class ConfigError(RuntimeError):
    """Raised when required environment variables are absent or empty."""


@dataclass(frozen=True)
class TokenConfig:
    """Validated Twilio credential set for minting a token."""

    account_sid: str
    api_key_sid: str
    api_key_secret: str
    twiml_app_sid: str


def load_config(environ: Optional[Mapping[str, str]] = None) -> TokenConfig:
    """Validate and load credentials from ``environ`` (default: process env).

    Raises ``ConfigError`` naming exactly the missing variables instead of
    silently operating with empty or default values.
    """

    env = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV_VARS if not env.get(name)]
    if missing:
        raise ConfigError(
            "Faltan variables de entorno requeridas: " + ", ".join(missing)
        )
    return TokenConfig(
        account_sid=env["TWILIO_ACCOUNT_SID"],
        api_key_sid=env["TWILIO_API_KEY_SID"],
        api_key_secret=env["TWILIO_API_KEY_SECRET"],
        twiml_app_sid=env["TWILIO_TWIML_APP_SID"],
    )


def generate_identity(now_ns: Optional[int] = None) -> str:
    """Return a session-unique caller identity ``softphone-dev-<timestamp>``."""

    stamp = time.time_ns() if now_ns is None else now_ns
    return f"{IDENTITY_PREFIX}{stamp}"


def mint_access_token(
    config: TokenConfig,
    identity: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> str:
    """Mint a Twilio Access Token as an HS256 JWT with a VoiceGrant.

    The token is built entirely from local values; no network is touched.
    """

    if ttl_seconds <= 0:
        raise ValueError("El TTL debe ser un entero de segundos positivo")

    token = AccessToken(
        config.account_sid,
        config.api_key_sid,
        config.api_key_secret,
        identity=identity,
        ttl=int(ttl_seconds),
    )
    token.add_grant(VoiceGrant(outgoing_application_sid=config.twiml_app_sid))

    jwt_value = token.to_jwt()
    if isinstance(jwt_value, bytes):  # defensive: SDK returns str today
        jwt_value = jwt_value.decode("utf-8")
    return jwt_value


# ── Local loopback server (serves the page and a fresh token) ───────────────


def load_softphone_html(path: Optional[Path] = None) -> bytes:
    """Read the static softphone page that ``serve`` mode will deliver."""

    html_path = Path(path) if path is not None else Path(__file__).with_name(
        HTML_FILENAME
    )
    return html_path.read_bytes()


def make_handler(
    html_bytes: bytes,
    config: TokenConfig,
    identity: str,
    ttl_seconds: int,
) -> type[BaseHTTPRequestHandler]:
    """Build a request handler bound to the page bytes and token settings."""

    class SoftphoneHandler(BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:  # silence per-request logging
            return

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib hook name
            if self.path == "/":
                self._send(200, html_bytes, "text/html; charset=utf-8")
            elif self.path == "/token":
                token = mint_access_token(config, identity, ttl_seconds=ttl_seconds)
                body = json.dumps({"token": token}).encode("utf-8")
                self._send(200, body, "application/json")
            else:
                self._send(404, b"Not Found", "text/plain; charset=utf-8")

    return SoftphoneHandler


def build_server(
    host: str,
    port: int,
    config: TokenConfig,
    identity: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    html_path: Optional[Path] = None,
) -> ThreadingHTTPServer:
    """Create (but do not start) the loopback server.

    Refuses any binding other than loopback so the short-lived tokens never
    leave the local machine.
    """

    if host not in LOOPBACK_HOSTS:
        raise ValueError(
            f"El servidor solo puede escuchar en loopback, no en '{host}'"
        )

    html_bytes = load_softphone_html(html_path)
    handler = make_handler(html_bytes, config, identity, ttl_seconds)
    server = ThreadingHTTPServer((host, port), handler)
    # Expose state for handlers/tests; each attribute has a single owner.
    server.softphone_html = html_bytes  # type: ignore[attr-defined]
    server.token_config = config  # type: ignore[attr-defined]
    server.identity = identity  # type: ignore[attr-defined]
    server.ttl_seconds = ttl_seconds  # type: ignore[attr-defined]
    return server


def _add_token_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--identity",
        default=None,
        help="Identidad del llamante (default: unica por sesion).",
    )
    parser.add_argument(
        "--ttl",
        type=int,
        default=DEFAULT_TTL_SECONDS,
        help=f"TTL del token en segundos (default: {DEFAULT_TTL_SECONDS}).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mint_token.py",
        description="Acuna Access Tokens de Twilio y sirve el softphone dev.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    token_cmd = subcommands.add_parser(
        "token", help="Imprime un Access Token para inspeccion."
    )
    _add_token_options(token_cmd)

    serve_cmd = subcommands.add_parser(
        "serve", help="Sirve el softphone y un token fresco por loopback."
    )
    serve_cmd.add_argument(
        "--host",
        default=DEFAULT_SERVE_HOST,
        help=f"Interfaz de escucha (solo loopback; default {DEFAULT_SERVE_HOST}).",
    )
    serve_cmd.add_argument(
        "--port",
        type=int,
        default=DEFAULT_SERVE_PORT,
        help=f"Puerto local (default {DEFAULT_SERVE_PORT}).",
    )
    _add_token_options(serve_cmd)

    return parser


def run(
    argv: Optional[Sequence[str]] = None,
    environ: Optional[Mapping[str, str]] = None,
    out: Optional[TextIO] = None,
    err: Optional[TextIO] = None,
) -> int:
    """CLI entry point. Returns a process exit code (0 on success)."""

    stdout = sys.stdout if out is None else out
    stderr = sys.stderr if err is None else err
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(environ)
    except ConfigError as exc:
        print(f"Error: {exc}", file=stderr)
        return 2

    identity = args.identity or generate_identity()

    if args.command == "serve":
        if args.host not in LOOPBACK_HOSTS:
            print(
                f"Error: el servidor solo puede escuchar en loopback, no en '{args.host}'",
                file=stderr,
            )
            return 2
        httpd = build_server(
            args.host, args.port, config, identity, ttl_seconds=args.ttl
        )
        print(
            f"Softphone disponible en http://{args.host}:{args.port}/",
            file=stdout,
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:  # pragma: no cover - interactive stop
            pass
        finally:
            httpd.server_close()
        return 0

    try:
        token = mint_access_token(config, identity, ttl_seconds=args.ttl)
    except ValueError as exc:
        print(f"Error: {exc}", file=stderr)
        return 2

    print(token, file=stdout)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI wiring
    raise SystemExit(run())
