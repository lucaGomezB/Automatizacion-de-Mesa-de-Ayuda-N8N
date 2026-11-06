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
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence, TextIO

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

# Pseudonymized corpus read by the case selector (c-70, design.md D3). The
# path is configurable via ``--corpus-json``; this is only the default.
DEFAULT_CORPUS_JSON = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "corpus_evaluacion_pseudonimizado.json"
)

# Channel labels tolerated for the telephone channel, normalized (accents
# stripped, lowercased, trimmed). "llamada telefonica" collapses the JSON
# ("llamada telefónica") and CSV spellings; "telefono" covers the short label.
TELEPHONE_CHANNEL_ALIASES = frozenset({"llamada telefonica", "telefono"})

# ── Case-status probe (c-174, design.md D1/D2/D3/D4/D5) ─────────────────────

# Backend endpoints consumed by the probe. The ingest endpoint already exists
# and is NOT modified; the probe only reads it.
AUTH_LOGIN_PATH = "/api/v1/auth/login"
INGRESO_PATH = "/api/v1/telefonia/ingresos"

# Default backend origin (autosigned cert -> ``--insecure``).
DEFAULT_BACKEND_BASE_URL = "https://localhost"

# Bounded timeout for the two server-side HTTP calls.
PROBE_TIMEOUT_SECONDS = 15.0

# Operator credentials for the probe (read EXCLUSIVELY from the environment).
ENV_OPERATOR_USERNAME = "INGEST_OPERATOR_USERNAME"
ENV_OPERATOR_PASSWORD = "INGEST_OPERATOR_PASSWORD"  # gitleaks:allow (env var name)


class ConfigError(RuntimeError):
    """Raised when required environment variables are absent or empty."""


class CorpusError(RuntimeError):
    """Raised when the pseudonymized corpus cannot be read or parsed."""


class ProbeError(RuntimeError):
    """Raised when the backend probe fails (login, network or HTTP 5xx)."""


@dataclass(frozen=True)
class ProbeConfig:
    """Validated operator credentials plus the probe transport options.

    ``password`` is excluded from ``repr``/``str`` so it never reaches a log
    line or an error message (design.md D8).
    """

    backend_base_url: str
    username: str
    password: str = field(repr=False)
    insecure: bool = False


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


# ── Case-status probe: pure decision + transport (c-174) ────────────────────


def _parse_iso_to_epoch_ms(value: Any) -> Optional[int]:
    """Parse an ISO-8601 timestamp into epoch milliseconds (or ``None``).

    ``datetime.fromisoformat`` accepts a trailing ``Z`` from Python 3.11 on,
    but the explicit normalization keeps the helper robust to the backend
    spelling the instant with ``Z``.
    """

    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def _case_status(
    listo: bool,
    estado: Optional[str],
    incidente_id: Optional[Any],
    latencia_e2e_ms: Optional[Any],
) -> dict[str, Any]:
    """Build the probe response envelope with a single field ordering."""

    return {
        "listo": listo,
        "transcripcion_estado": estado,
        "incidente_id": incidente_id,
        "latencia_e2e_ms": latencia_e2e_ms,
    }


def evaluate_case_status(
    payload: Optional[Mapping[str, Any]], since_ms: Optional[int] = None
) -> dict[str, Any]:
    """Decide whether the case is fully processed (design.md D2/D3).

    ``payload`` is the ``TelefoniaIngresoRead`` body (or ``None`` for a 404).
    ``listo`` is true only when an ingreso exists, its ``incidente_id`` is not
    null AND, when ``since_ms`` is provided, its ``ingresado_en`` is not older
    than ``since_ms`` (so a retry of the same ``corpus_case_id`` is not
    reported from the previous run's ingreso).
    """

    if payload is None:
        return _case_status(False, None, None, None)

    estado = payload.get("transcripcion_estado")
    incidente_id = payload.get("incidente_id")
    latencia = payload.get("latencia_e2e_ms")

    if incidente_id is None:
        return _case_status(False, estado, None, None)

    if since_ms is not None:
        ingresado_ms = _parse_iso_to_epoch_ms(payload.get("ingresado_en"))
        if ingresado_ms is None or ingresado_ms < since_ms:
            return _case_status(False, estado, None, None)

    return _case_status(True, estado, incidente_id, latencia)


def load_probe_config(
    environ: Optional[Mapping[str, str]] = None,
    backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
    insecure: bool = False,
) -> Optional[ProbeConfig]:
    """Load the operator credentials used by the probe.

    Returns ``None`` when BOTH credentials are absent (fail-open, design.md
    D5). A partially configured pair is a misconfiguration and raises
    ``ConfigError`` naming the missing variable (never the value).
    """

    env = os.environ if environ is None else environ
    username = env.get(ENV_OPERATOR_USERNAME)
    password = env.get(ENV_OPERATOR_PASSWORD)
    if not username and not password:
        return None
    if not username or not password:
        missing = (
            ENV_OPERATOR_USERNAME if not username else ENV_OPERATOR_PASSWORD
        )
        raise ConfigError(
            "Credenciales de sonda incompletas: falta " + missing
        )
    return ProbeConfig(
        backend_base_url=backend_base_url,
        username=username,
        password=password,
        insecure=insecure,
    )


def _ssl_context(config: ProbeConfig) -> Optional[ssl.SSLContext]:
    """Return the TLS context for the probe (unverified when ``insecure``)."""

    if not config.insecure:
        return None
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def _default_opener(
    request: urllib.request.Request, config: ProbeConfig
) -> tuple[int, bytes]:
    """Open ``request`` with stdlib ``urllib`` and return ``(status, body)``.

    HTTP error statuses (4xx/5xx) are returned as data, not raised, so the
    caller can map 404 (no ingreso) and 401 (expired JWT) explicitly.
    """

    try:
        with urllib.request.urlopen(
            request,
            context=_ssl_context(config),
            timeout=PROBE_TIMEOUT_SECONDS,
        ) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        # Network/TLS failure: surface as a probe error so the route answers
        # 502 and the page degrades fail-open (design.md D7).
        raise ProbeError(
            f"No se pudo contactar el backend: {exc.reason}"
        ) from exc


def login_backend(
    config: ProbeConfig,
    opener: Optional[Callable[..., tuple[int, bytes]]] = None,
) -> str:
    """Authenticate against the backend and return the access token."""

    open_fn = opener or _default_opener
    body = json.dumps(
        {"username": config.username, "password": config.password}
    ).encode("utf-8")
    request = urllib.request.Request(
        config.backend_base_url + AUTH_LOGIN_PATH,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    status, raw = open_fn(request, config)
    if status != 200:
        raise ProbeError(f"Login del operador fallido: HTTP {status}")
    return json.loads(raw.decode("utf-8"))["access_token"]


def fetch_ingreso(
    config: ProbeConfig,
    token: str,
    case_id: str,
    opener: Optional[Callable[..., tuple[int, bytes]]] = None,
) -> tuple[int, Optional[dict[str, Any]]]:
    """Read the latest ingreso for ``case_id``.

    Returns ``(404, None)`` when the case has no ingreso yet. A 5xx is
    surfaced as ``ProbeError`` (the probe cannot answer); any other non-200
    status is returned without a payload so the caller can react (401).
    """

    open_fn = opener or _default_opener
    query = urllib.parse.urlencode(
        {"corpus_case_id": case_id, "latest": "true"}
    )
    request = urllib.request.Request(
        f"{config.backend_base_url}{INGRESO_PATH}?{query}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    status, raw = open_fn(request, config)
    if status == 404:
        return 404, None
    if status >= 500:
        raise ProbeError(f"Backend respondio HTTP {status}")
    if status != 200:
        return status, None
    payload = json.loads(raw.decode("utf-8")) if raw else None
    return status, payload


class ProbeClient:
    """Stateful probe: caches the JWT and re-logs on a single 401 (D8)."""

    def __init__(
        self,
        config: ProbeConfig,
        opener: Optional[Callable[..., tuple[int, bytes]]] = None,
    ) -> None:
        self._config = config
        self._opener = opener
        self._token: Optional[str] = None

    def _login(self) -> str:
        self._token = login_backend(self._config, self._opener)
        return self._token

    def status(
        self, case_id: str, since_ms: Optional[int] = None
    ) -> dict[str, Any]:
        token = self._token if self._token else self._login()
        status_code, payload = fetch_ingreso(
            self._config, token, case_id, self._opener
        )
        if status_code == 401:
            token = self._login()
            _, payload = fetch_ingreso(
                self._config, token, case_id, self._opener
            )
        return evaluate_case_status(payload, since_ms)


# ── Corpus case listing (c-70, design.md D3) ────────────────────────────────


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _norm_channel(value: Any) -> str:
    if value is None:
        return ""
    return _strip_accents(str(value)).strip().lower()


def load_telephone_cases(corpus_json_path: Any) -> list[dict]:
    """Return ``[{id, descripcion}]`` for the telephone cases of the corpus.

    The corpus is read from ``corpus_json_path`` (pseudonymized copy) and the
    channel label is matched tolerantly (accents, case and surrounding
    whitespace). A missing or malformed corpus raises ``CorpusError`` with the
    offending path so the failure is actionable. Descriptions are returned for
    the operator to RECITE and MUST NOT be logged by callers.
    """

    path = Path(corpus_json_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CorpusError(
            f"No se encontro el corpus pseudonimizado en '{path}'"
        ) from exc
    except OSError as exc:
        raise CorpusError(f"No se pudo leer el corpus '{path}': {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CorpusError(f"El corpus '{path}' no es JSON valido: {exc}") from exc

    casos = data.get("casos") if isinstance(data, dict) else None
    if not isinstance(casos, list):
        raise CorpusError(f"El corpus '{path}' no contiene una lista 'casos'")

    cases: list[dict] = []
    for caso in casos:
        if not isinstance(caso, dict):
            continue
        if _norm_channel(caso.get("canal_origen")) not in TELEPHONE_CHANNEL_ALIASES:
            continue
        case_id = caso.get("id")
        if not case_id:
            continue
        cases.append(
            {
                "id": str(case_id),
                "descripcion": str(caso.get("descripcion") or ""),
            }
        )
    return cases


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
    corpus_json_path: Optional[Path] = None,
    probe: Optional[Callable[[str, Optional[int]], dict[str, Any]]] = None,
) -> type[BaseHTTPRequestHandler]:
    """Build a request handler bound to the page bytes and token settings.

    ``probe`` is the callable backing ``GET /case-status``. It is injected so
    the route is unit-testable offline; ``build_server`` derives it from a
    ``ProbeConfig``. When it is ``None`` the route reports
    ``probe_unconfigured`` (fail-open, design.md D5).
    """

    resolved_corpus = (
        Path(corpus_json_path)
        if corpus_json_path is not None
        else DEFAULT_CORPUS_JSON
    )

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

        def _send_json(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(status, body, "application/json")

        def _send_corpus_cases(self) -> None:
            # Never log the descriptions: they are pseudonymized but still
            # case content. Only the error path is surfaced, without cases.
            try:
                cases = load_telephone_cases(resolved_corpus)
            except CorpusError as exc:
                self._send_json(
                    500, {"error": {"code": "corpus_unavailable", "message": str(exc)}}
                )
                return
            self._send_json(200, cases)

        def _send_case_status(self) -> None:
            # Only identifiers/estados travel here; never case content (D8).
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            case_id = (params.get("case_id") or [""])[0].strip()
            if not case_id:
                self._send_json(
                    400,
                    {
                        "error": {
                            "code": "missing_case_id",
                            "message": "Falta el parametro case_id",
                        }
                    },
                )
                return
            if probe is None:
                self._send_json(
                    503,
                    {
                        "error": {
                            "code": "probe_unconfigured",
                            "message": (
                                "La sonda no esta configurada: exportar "
                                f"{ENV_OPERATOR_USERNAME}/{ENV_OPERATOR_PASSWORD}"
                            ),
                        }
                    },
                )
                return
            since_raw = (params.get("since") or [None])[0]
            since_ms: Optional[int] = None
            if since_raw is not None:
                try:
                    since_ms = int(since_raw)
                except (TypeError, ValueError):
                    since_ms = None
            try:
                result = probe(case_id, since_ms)
            except ProbeError as exc:
                self._send_json(
                    502,
                    {"error": {"code": "probe_error", "message": str(exc)}},
                )
                return
            self._send_json(200, result)

        def do_GET(self) -> None:  # noqa: N802 - stdlib hook name
            route = urllib.parse.urlparse(self.path).path
            if route == "/":
                self._send(200, html_bytes, "text/html; charset=utf-8")
            elif route == "/token":
                token = mint_access_token(config, identity, ttl_seconds=ttl_seconds)
                self._send_json(200, {"token": token})
            elif route == "/corpus-cases":
                self._send_corpus_cases()
            elif route == "/case-status":
                self._send_case_status()
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
    corpus_json_path: Optional[Path] = None,
    probe_config: Optional[ProbeConfig] = None,
    probe: Optional[Callable[[str, Optional[int]], dict[str, Any]]] = None,
) -> ThreadingHTTPServer:
    """Create (but do not start) the loopback server.

    Refuses any binding other than loopback so the short-lived tokens never
    leave the local machine. An explicit ``probe`` wins over ``probe_config``
    (tests inject a fake); otherwise a ``ProbeClient`` is built from the
    config and its ``status`` method backs ``GET /case-status``.
    """

    if host not in LOOPBACK_HOSTS:
        raise ValueError(
            f"El servidor solo puede escuchar en loopback, no en '{host}'"
        )

    html_bytes = load_softphone_html(html_path)
    resolved_corpus = (
        Path(corpus_json_path)
        if corpus_json_path is not None
        else DEFAULT_CORPUS_JSON
    )
    resolved_probe = probe
    if resolved_probe is None and probe_config is not None:
        resolved_probe = ProbeClient(probe_config).status
    handler = make_handler(
        html_bytes,
        config,
        identity,
        ttl_seconds,
        corpus_json_path=resolved_corpus,
        probe=resolved_probe,
    )
    server = ThreadingHTTPServer((host, port), handler)
    # Expose state for handlers/tests; each attribute has a single owner.
    server.softphone_html = html_bytes  # type: ignore[attr-defined]
    server.token_config = config  # type: ignore[attr-defined]
    server.identity = identity  # type: ignore[attr-defined]
    server.ttl_seconds = ttl_seconds  # type: ignore[attr-defined]
    server.corpus_json_path = resolved_corpus  # type: ignore[attr-defined]
    server.probe_config = probe_config  # type: ignore[attr-defined]
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
    serve_cmd.add_argument(
        "--corpus-json",
        default=None,
        help=(
            "Ruta al corpus pseudonimizado para el selector de casos "
            f"(default: {DEFAULT_CORPUS_JSON})."
        ),
    )
    serve_cmd.add_argument(
        "--backend-base-url",
        default=DEFAULT_BACKEND_BASE_URL,
        help=(
            "URL base del backend para la sonda /case-status "
            f"(default: {DEFAULT_BACKEND_BASE_URL})."
        ),
    )
    serve_cmd.add_argument(
        "--insecure",
        action="store_true",
        help="No verificar el certificado TLS del backend (autofirmado).",
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
        # Fail-open (design.md D5): a missing/incomplete probe config never
        # blocks the softphone; /case-status degrades to a clear error.
        try:
            probe_config = load_probe_config(
                environ, args.backend_base_url, args.insecure
            )
        except ConfigError as exc:
            print(
                f"Advertencia: {exc}; la sonda /case-status queda deshabilitada.",
                file=stderr,
            )
            probe_config = None
        httpd = build_server(
            args.host,
            args.port,
            config,
            identity,
            ttl_seconds=args.ttl,
            corpus_json_path=args.corpus_json,
            probe_config=probe_config,
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
