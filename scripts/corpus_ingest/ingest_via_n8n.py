"""Corpus ingest harness via the REAL N8N flow (c-68).

Purpose
-------
Load the thesis corpus through the real N8N flow for the ``web`` and
``correo`` channels (``telefono`` is measured manually by the author, out of
scope) and derive the hybrid latency metric per case:

    t_pipeline_s = latencia_e2e_ms / 1000 = persistido_en - ingresado_en
    t_espera_s   = ingresado_en - t_envio
    t_e2e_s      = persistido_en - t_envio = t_espera_s + t_pipeline_s

``tiempo_automatizado_s`` is ``t_e2e_s`` for BOTH channels (for correo it
includes the IMAP poller wait). The decomposition is written back to the XLSX,
the CSV twin and a description-free sidecar; the numeric time is merged into
the evaluation JSON without weakening ``evaluation/corpus.py::_a_float``.

Privacy
-------
Corpus descriptions are REAL internal text. This module NEVER logs, prints or
persists a description. On error only a short label is emitted (status code or
exception type), never a response body. The sidecar is description-free by
construction.

No secrets live in this file. Credentials are read from the environment:
``INGEST_OPERATOR_USERNAME`` / ``INGEST_OPERATOR_PASSWORD`` (login), SMTP and
confirmation-IMAP variables (see README.md).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.parse import urlencode

import ingest_corpus as ic

# ── Canonical contract ──────────────────────────────────────────────────────

UTC = timezone.utc

HEADER_ID = "ID"
HEADER_DESCRIPCION = "Descripcion"
HEADER_CANAL = "Canal de Origen"
HEADER_AUTO_TIME = "TIempo de Registro Automatico (Segundos)"
LATENCIA_COL = "Latencia e2e (ms)"
PIPELINE_COL = "Tiempo pipeline (s)"
ESPERA_COL = "Tiempo espera (s)"

MESSAGE_ID_PREFIX = "corpus-"
DEFAULT_MAIL_DOMAIN = "corpus.local"

CANAL_CORREO = "correo"
CANAL_WEB = "web"
CANAL_TELEFONO = "telefono"
INGESTABLE_CHANNELS = (CANAL_CORREO, CANAL_WEB)

DEFAULT_BASE_URL = "https://localhost"
DEFAULT_WEBHOOK_URL = "http://localhost:5678/webhook/incidente-web"
DEFAULT_JSON = "data/corpus_evaluacion_pseudonimizado.json"
DEFAULT_CSV = "data/Corpus Tesis - Hoja 1.csv"
DEFAULT_XLSX = "data/Corpus Tesis.xlsx"
DEFAULT_SIDECAR = "data/corpus_resultados_n8n.json"

LOGIN_PATH = "/api/v1/auth/login"
INCIDENTES_PATH = "/api/v1/incidentes/"
DEFAULT_LIST_LIMIT = 200

POLL_TIMEOUT_S = 90.0
POLL_INTERVAL_S = 5.0
CONFIRMATION_TIMEOUT_S = 60.0
CONFIRMATION_INTERVAL_S = 5.0
CLOCK_SKEW_MARGIN_S = 2.0

# Confirmation receive path (D14) — names must match scripts/corpus_ingest/ingest.env.
ENV_CONFIRMATION_IMAP_HOST = "INGEST_CONFIRMATION_IMAP_HOST"
ENV_CONFIRMATION_IMAP_PORT = "INGEST_CONFIRMATION_IMAP_PORT"
ENV_CONFIRMATION_IMAP_USER = "INGEST_CONFIRMATION_IMAP_USER"
ENV_CONFIRMATION_IMAP_PASSWORD = "INGEST_CONFIRMATION_IMAP_PASSWORD"  # gitleaks:allow (nombre de variable de entorno, no un secreto)
ENV_CONFIRMATION_IMAP_FOLDER = "INGEST_CONFIRMATION_IMAP_FOLDER"
ENV_INGEST_IMAP_HOST = "INGEST_INGEST_IMAP_HOST"
ENV_INGEST_IMAP_USER = "INGEST_INGEST_IMAP_USER"
ENV_INGEST_IMAP_FOLDER = "INGEST_INGEST_IMAP_FOLDER"
DEFAULT_IMAP_PORT = 993
DEFAULT_IMAP_FOLDER = "INBOX"

# ── Pure helpers (unit tested offline) ──────────────────────────────────────


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _norm(value: Any) -> str:
    if value is None:
        return ""
    return _strip_accents(str(value)).strip().lower()


def _to_utc(value: Any) -> datetime | None:
    """Normalize a datetime/ISO-8601 string to an aware UTC instant."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        value = datetime.fromisoformat(text)
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def map_canal(canal: str | None) -> str | None:
    """Map a corpus channel label (JSON or CSV) to a canonical channel.

    Tolerant to accents, case and surrounding whitespace. Unknown or empty
    labels return ``None``.
    """
    key = _norm(canal)
    aliases = {
        "correo": CANAL_CORREO,
        "correo electronico": CANAL_CORREO,
        "formulario web": CANAL_WEB,
        "web": CANAL_WEB,
        "telefono": CANAL_TELEFONO,
        "llamada telefonica": CANAL_TELEFONO,
    }
    return aliases.get(key)


@dataclass(frozen=True)
class MetricResult:
    """Hybrid latency decomposition (D1)."""

    t_pipeline_s: float | None
    t_espera_s: float | None
    t_e2e_s: float | None
    anomalo: bool


def derive_metric(
    *,
    t_envio: Any,
    ingresado_en: Any,
    persistido_en: Any,
    latencia_e2e_ms: int | None = None,
    latencia_anomala: bool = False,
    skew_margin_s: float = CLOCK_SKEW_MARGIN_S,
) -> MetricResult:
    """Derive ``t_pipeline_s``, ``t_espera_s`` and ``t_e2e_s`` for one case.

    A case is anomalous (excluded from the corpus and analysis) when the
    derived latency is missing, explicitly flagged, non-positive, or when the
    wait is negative beyond the clock-skew margin. Anomalies are reported, not
    clamped to zero.
    """
    envio = _to_utc(t_envio)
    ingreso = _to_utc(ingresado_en)
    persistido = _to_utc(persistido_en)
    if envio is None or ingreso is None or persistido is None:
        return MetricResult(None, None, None, True)

    t_espera_s = (ingreso - envio).total_seconds()
    if latencia_e2e_ms is None:
        t_pipeline_s = (persistido - ingreso).total_seconds()
    else:
        t_pipeline_s = float(latencia_e2e_ms) / 1000.0
    t_e2e_s = (persistido - envio).total_seconds()

    anomalo = (
        bool(latencia_anomala)
        or latencia_e2e_ms is None
        or t_pipeline_s < 0
        or t_e2e_s <= 0
        or t_espera_s < -abs(skew_margin_s)
    )
    return MetricResult(t_pipeline_s, t_espera_s, t_e2e_s, anomalo)


def tiempo_automatizado_s(canal: str, metric: MetricResult) -> float | None:
    """Canonical ``tiempo_automatizado_s`` = ``t_e2e_s`` (both channels)."""
    if metric.anomalo or metric.t_e2e_s is None:
        return None
    return metric.t_e2e_s


def build_web_payload(
    *, descripcion: str, case_id: str, prioridad: str = "media"
) -> dict[str, Any]:
    """Build the web-channel POST body for the N8N webhook.

    Carries a deterministic ``origen_message_id`` (``corpus-<ID>``) so c-69's
    server-side dedup makes a re-run idempotent.
    """
    return {
        "descripcion": descripcion,
        "prioridad": prioridad,
        "origen_message_id": f"{MESSAGE_ID_PREFIX}{case_id}",
    }


def resolve_mail_domain(env: dict[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    value = (source.get("INGEST_CORPUS_MAIL_DOMAIN") or "").strip()
    return value or DEFAULT_MAIL_DOMAIN


def build_message_id(case_id: str, domain: str = DEFAULT_MAIL_DOMAIN) -> str:
    """Deterministic RFC-5322 ``Message-ID`` header value (with brackets)."""
    return f"<{MESSAGE_ID_PREFIX}{case_id}@{domain}>"


def normalize_message_id(value: str | None) -> str:
    """Strip whitespace and ``<>`` so correlation is format tolerant (D6)."""
    if value is None:
        return ""
    return value.strip().strip("<>").strip()


def correlation_keys(case_id: str, domain: str = DEFAULT_MAIL_DOMAIN) -> list[str]:
    """Candidate stored forms to query for exact correlation (D6/D3)."""
    bracketed = build_message_id(case_id, domain)
    plain = normalize_message_id(bracketed)
    keys = [bracketed, plain]
    seen: list[str] = []
    for key in keys:
        if key and key not in seen:
            seen.append(key)
    return seen


def select_correlated_incident(
    items: Sequence[dict[str, Any]], min_ingresado_en: Any
) -> dict[str, Any] | None:
    """Pick the first listed incident whose ``ingresado_en`` >= the send instant.

    Guards against claiming a stale incident from a prior run (D3).
    """
    threshold = _to_utc(min_ingresado_en)
    for item in items:
        ingreso = _to_utc(item.get("ingresado_en"))
        if ingreso is None:
            continue
        if threshold is None or ingreso >= threshold:
            return item
    return None


def select_incident_by_window(
    items: Sequence[dict[str, Any]],
    *,
    t_envio: Any,
    claimed_ids: Iterable[Any] = (),
    margin_s: float = 60.0,
) -> dict[str, Any] | None:
    """Documented FALLBACK: pick a new incident by a bounded time window.

    Used only when the exact correlation contract (c-69) is unavailable. A
    dedicated clean mailbox, one case in flight and claimed ids are required.
    Never the primary mechanism.
    """
    threshold = _to_utc(t_envio)
    if threshold is None:
        return None
    claimed = set(claimed_ids)
    lower = threshold - timedelta(seconds=abs(margin_s))
    for item in items:
        if item.get("id") in claimed:
            continue
        ingreso = _to_utc(item.get("ingresado_en"))
        if ingreso is None:
            continue
        if ingreso >= lower:
            return item
    return None


def confirmation_subject(numero_incidente: str) -> str:
    """Deterministic subject of the N8N confirmation email (workflow contract)."""
    return f"Incidente registrado - Numero {numero_incidente}"


def derive_confirmation(
    *, t_envio: Any, t_confirmacion: Any
) -> tuple[bool, float | None]:
    """Secondary end-to-end check: presence and latency of the confirmation.

    Absence never invalidates the primary API-instants measurement.
    """
    confirmacion = _to_utc(t_confirmacion)
    envio = _to_utc(t_envio)
    if confirmacion is None or envio is None:
        return (False, None)
    return (True, (confirmacion - envio).total_seconds())


def confirmation_path_is_separate(
    *,
    ingest_host: str | None,
    confirmation_host: str | None,
    ingest_mailbox: str | None,
    confirmation_folder: str | None,
    ingest_user: str | None,
    confirmation_user: str | None,
) -> bool:
    """True when the confirmation path cannot feed the ingestion IMAP trigger.

    A different mailbox/folder on the same account, or any different host/user,
    is accepted. The same folder on the same account is rejected (D14).
    """
    same_account = _norm(ingest_host) == _norm(confirmation_host) and _norm(
        ingest_user
    ) == _norm(confirmation_user)
    if same_account and _norm(ingest_mailbox) == _norm(confirmation_folder):
        return False
    return True


def select_confirmation_instant(
    messages: Sequence[Mapping[str, Any]], numero_incidente: str
) -> datetime | None:
    """Pure selection: first message whose subject matches, as a UTC instant.

    No IMAP, no network. Each message is a mapping with ``subject`` and
    ``received`` (datetime or ISO-8601 string). Returns ``None`` when no message
    matches the deterministic confirmation subject or the instant is invalid.
    """
    expected = _norm(confirmation_subject(numero_incidente))
    for message in messages:
        if _norm(message.get("subject")) != expected:
            continue
        instant = _to_utc(message.get("received"))
        if instant is not None:
            return instant
    return None


def _fetch_confirmation_messages(  # pragma: no cover - I/O
    *,
    host: str,
    port: int,
    user: str,
    password: str | None,
    folder: str,
) -> list[dict[str, Any]]:
    """Read-only IMAP fetch of ``(subject, received)`` from the separate path.

    Never writes, never deletes and never reads the ingestion mailbox. Kept out
    of unit tests; the observer accepts an injected fetcher instead.
    """
    import email
    import imaplib
    import re
    import ssl
    from email.utils import parsedate_to_datetime

    context = ssl.create_default_context()
    found: list[dict[str, Any]] = []
    with imaplib.IMAP4_SSL(host, port, ssl_context=context) as client:
        client.login(user, password or "")
        client.select(folder, readonly=True)
        status, data = client.search(None, "ALL")
        if status != "OK":
            return found
        for number in (data[0] or b"").split():
            status, message_data = client.fetch(
                number, "(INTERNALDATE BODY.PEEK[HEADER.FIELDS (SUBJECT)])"
            )
            if status != "OK":
                continue
            raw_prefix = b""
            raw_header = b""
            for part in message_data:
                if isinstance(part, tuple):
                    raw_prefix, raw_header = part[0], part[1]
                    break
            else:
                continue
            header = email.message_from_bytes(raw_header)
            match = re.search(rb'INTERNALDATE "([^"]+)"', raw_prefix)
            received = None
            if match:
                received = parsedate_to_datetime(
                    match.group(1).decode("ascii", "ignore")
                )
            found.append({"subject": header.get("Subject", ""), "received": received})
    return found


def build_confirmation_observer(
    env: Mapping[str, str] | None = None,
    fetch_messages: Callable[..., list[dict[str, Any]]] | None = None,
) -> Callable[[str], datetime | None] | None:
    """Build the confirmation observer, or ``None`` when it is not configured.

    Only wired when both the IMAP host and user are present, so the default
    behavior stays non-blocking (``confirmacion_recibida = false``). The IMAP
    client is injectable for offline tests.
    """
    source = os.environ if env is None else env
    host = (source.get(ENV_CONFIRMATION_IMAP_HOST) or "").strip()
    user = (source.get(ENV_CONFIRMATION_IMAP_USER) or "").strip()
    if not host or not user:
        return None
    port_text = (source.get(ENV_CONFIRMATION_IMAP_PORT) or "").strip()
    port = int(port_text) if port_text else DEFAULT_IMAP_PORT
    password = source.get(ENV_CONFIRMATION_IMAP_PASSWORD)
    folder = (
        source.get(ENV_CONFIRMATION_IMAP_FOLDER) or ""
    ).strip() or DEFAULT_IMAP_FOLDER
    fetch = fetch_messages or _fetch_confirmation_messages

    def observer(numero_incidente: str) -> datetime | None:
        messages = fetch(
            host=host, port=port, user=user, password=password, folder=folder
        )
        return select_confirmation_instant(messages, numero_incidente)

    return observer


def confirmation_separation_error(
    env: Mapping[str, str] | None = None,
) -> str | None:
    """Error message when the confirmation path can feed the ingest trigger.

    Returns ``None`` when the observer is not configured or when the path is
    separate (D14). The message never contains a credential.
    """
    source = os.environ if env is None else env
    conf_host = (source.get(ENV_CONFIRMATION_IMAP_HOST) or "").strip()
    conf_user = (source.get(ENV_CONFIRMATION_IMAP_USER) or "").strip()
    if not conf_host or not conf_user:
        return None
    conf_folder = (
        source.get(ENV_CONFIRMATION_IMAP_FOLDER) or ""
    ).strip() or DEFAULT_IMAP_FOLDER
    ingest_host = source.get(ENV_INGEST_IMAP_HOST)
    ingest_user = source.get(ENV_INGEST_IMAP_USER)
    ingest_folder = (
        source.get(ENV_INGEST_IMAP_FOLDER) or ""
    ).strip() or DEFAULT_IMAP_FOLDER
    separate = confirmation_path_is_separate(
        ingest_host=ingest_host,
        confirmation_host=conf_host,
        ingest_mailbox=ingest_folder,
        confirmation_folder=conf_folder,
        ingest_user=ingest_user,
        confirmation_user=conf_user,
    )
    if separate:
        return None
    return (
        "ERROR: el camino de confirmacion NO es separado del de ingesta "
        "(misma cuenta y carpeta). Configurar una carpeta o buzon dedicado "
        "(ver README.md, D14) antes de correr."
    )


# ── Case / result models ────────────────────────────────────────────────────


@dataclass
class Case:
    """One corpus case (description kept in memory only; never logged)."""

    case_id: str
    descripcion: str
    canal: str


@dataclass
class CaseResult:
    """Per-case outcome. Deliberately description-free (D7)."""

    case_id: str
    canal: str
    incidente_id: int | None
    numero_incidente: str | None
    sector: str | None
    revision: bool | None
    t_envio: str | None
    ingresado_en: str | None
    persistido_en: str | None
    latencia_e2e_ms: int | None
    t_pipeline_s: float | None
    t_espera_s: float | None
    t_e2e_s: float | None
    origen_message_id: str | None
    confirmacion_recibida: bool
    t_confirmacion: str | None
    t_confirmacion_s: float | None
    anomalo: bool
    error: str | None


# ── Reading ─────────────────────────────────────────────────────────────────


def read_json_cases(path: str | Path) -> list[Case]:
    """Read cases from the evaluation JSON (the default pseudonymized source)."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    cases: list[Case] = []
    for item in doc.get("casos", []):
        cid = item.get("id")
        if cid is None:
            continue
        cases.append(
            Case(
                case_id=str(cid).strip(),
                descripcion=str(item.get("descripcion", "")),
                canal=str(item.get("canal_origen", "")),
            )
        )
    return cases


def read_cases(path: str | Path, source: str = "json") -> list[Case]:
    """Dispatch to the JSON reader or the CSV/XLSX registration reader."""
    if source == "json":
        return read_json_cases(path)
    return [
        Case(case_id=c.case_id, descripcion=c.descripcion, canal=c.canal)
        for c in ic.read_cases(path, source)
    ]


def select_cases(
    cases: Sequence[Case], only_channel: str | None = None, limit: int | None = None
) -> list[Case]:
    """Filter by canonical channel and apply a limit."""
    selected = list(cases)
    if only_channel is not None:
        target = map_canal(only_channel)
        selected = [c for c in selected if map_canal(c.canal) == target]
    if limit is not None:
        selected = selected[: max(limit, 0)]
    return selected


# ── Writing (idempotent, structure-preserving) ──────────────────────────────


def _write_csv_columns(
    row: list[Any], cols: dict[str, int], result: CaseResult
) -> None:
    if result.t_e2e_s is not None:
        row[cols["auto"]] = ic._format_seconds(result.t_e2e_s)
    if result.latencia_e2e_ms is not None:
        row[cols["latencia"]] = str(result.latencia_e2e_ms)
    if result.t_pipeline_s is not None:
        row[cols["pipeline"]] = ic._format_seconds(result.t_pipeline_s)
    if result.t_espera_s is not None:
        row[cols["espera"]] = ic._format_seconds(result.t_espera_s)


def write_csv_results(path: str | Path, results: dict[str, CaseResult]) -> None:
    """Fill auto/latency and add the decomposition columns to the CSV twin.

    Idempotent: existing columns are reused, never duplicated. A case without
    a measurement leaves the existing cell untouched (a prior value is never
    overwritten with blank).
    """
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header_idx = ic._find_header_row(rows)
    header = rows[header_idx]
    cols = {
        "id": ic._column_index(header, HEADER_ID),
        "auto": ic._auto_time_index(header),
        "latencia": ic._ensure_column(rows, header_idx, LATENCIA_COL),
        "pipeline": ic._ensure_column(rows, header_idx, PIPELINE_COL),
        "espera": ic._ensure_column(rows, header_idx, ESPERA_COL),
    }

    width = len(rows[header_idx])
    for row in rows:
        if len(row) < width:
            row.extend([""] * (width - len(row)))

    for row in rows[header_idx + 1 :]:
        case_id = row[cols["id"]].strip()
        result = results.get(case_id)
        if result is None:
            continue
        _write_csv_columns(row, cols, result)

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


def _ensure_xlsx_column(ws: Any, header_row: int, header_values: list[Any], name: str) -> int:
    """Return the 1-based column index for ``name``, appending it if absent."""
    for idx, cell in enumerate(header_values, start=1):
        if _norm(cell) == _norm(name):
            return idx
    col = len(header_values) + 1
    ws.cell(row=header_row, column=col, value=name)
    header_values.append(name)
    return col


def write_xlsx_results(path: str | Path, results: dict[str, CaseResult]) -> None:
    """Update the XLSX in place with the same columns as the CSV twin.

    Idempotent on re-run; a case without a measurement is left untouched.
    """
    openpyxl = ic._import_openpyxl()
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]

    header_row = None
    header_values: list[Any] = []
    for row_idx in range(1, ws.max_row + 1):
        values = [ws.cell(row=row_idx, column=c).value for c in range(1, ws.max_column + 1)]
        normalized = {_norm(v) for v in values}
        if HEADER_ID.lower() in normalized and HEADER_DESCRIPCION.lower() in normalized:
            header_row = row_idx
            header_values = values
            break
    if header_row is None:
        raise ValueError("No se encontro la fila de encabezados en el XLSX.")

    id_col = ic._column_index(header_values, HEADER_ID) + 1
    auto_col = ic._auto_time_index(header_values) + 1
    lat_col = _ensure_xlsx_column(ws, header_row, header_values, LATENCIA_COL)
    pipe_col = _ensure_xlsx_column(ws, header_row, header_values, PIPELINE_COL)
    wait_col = _ensure_xlsx_column(ws, header_row, header_values, ESPERA_COL)

    for row_idx in range(header_row + 1, ws.max_row + 1):
        case_id = ws.cell(row=row_idx, column=id_col).value
        if case_id is None or not str(case_id).strip():
            continue
        result = results.get(str(case_id).strip())
        if result is None:
            continue
        if result.t_e2e_s is not None:
            ws.cell(row=row_idx, column=auto_col, value=round(float(result.t_e2e_s), 3))
        if result.latencia_e2e_ms is not None:
            ws.cell(row=row_idx, column=lat_col, value=result.latencia_e2e_ms)
        if result.t_pipeline_s is not None:
            ws.cell(row=row_idx, column=pipe_col, value=round(float(result.t_pipeline_s), 3))
        if result.t_espera_s is not None:
            ws.cell(row=row_idx, column=wait_col, value=round(float(result.t_espera_s), 3))

    wb.save(path)


def write_sidecar_json(path: str | Path, results: Iterable[CaseResult]) -> None:
    """Write the description-free traceability sidecar."""
    payload = [asdict(r) for r in results]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def merge_evaluation_json(path: str | Path, measurements: dict[str, float | None]) -> int:
    """Merge numeric ``tiempo_automatizado_s`` by ``id`` into the evaluation JSON.

    Never writes ``null`` over an existing value and never weakens
    ``evaluation/corpus.py::_a_float``. Returns the count of cases still null
    (telephone pending, author fills them manually).
    """
    target = Path(path)
    doc = json.loads(target.read_text(encoding="utf-8"))
    casos = doc.get("casos", [])
    for case in casos:
        cid = case.get("id")
        if cid is None:
            continue
        value = measurements.get(str(cid))
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        case["tiempo_automatizado_s"] = round(float(value), 3)
    target.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return sum(1 for c in casos if c.get("tiempo_automatizado_s") is None)


# ── Result helpers ──────────────────────────────────────────────────────────


def _error_label(response: Any) -> str:
    """Short, body-free error label for a non-2xx response."""
    code = ""
    try:
        body = response.json()
        code = (body.get("error") or {}).get("code") or ""
    except Exception:  # noqa: BLE001 - body is untrusted
        code = ""
    return f"http{response.status_code}" + (f"/{code}" if code else "")


def _error_result(
    case_id: str, canal: str, t_envio: datetime | None, label: str
) -> CaseResult:
    return CaseResult(
        case_id=case_id,
        canal=canal,
        incidente_id=None,
        numero_incidente=None,
        sector=None,
        revision=None,
        t_envio=t_envio.isoformat() if t_envio else None,
        ingresado_en=None,
        persistido_en=None,
        latencia_e2e_ms=None,
        t_pipeline_s=None,
        t_espera_s=None,
        t_e2e_s=None,
        origen_message_id=None,
        confirmacion_recibida=False,
        t_confirmacion=None,
        t_confirmacion_s=None,
        anomalo=False,
        error=label,
    )


def _result_from_detail(
    *,
    case_id: str,
    canal: str,
    detail: dict[str, Any],
    t_envio: datetime,
    origen_message_id: str | None,
    confirmation: tuple[bool, datetime | None, float | None] | None = None,
) -> CaseResult:
    ingresado_en = _to_utc(detail.get("ingresado_en"))
    persistido_en = _to_utc(detail.get("persistido_en"))
    metric = derive_metric(
        t_envio=t_envio,
        ingresado_en=ingresado_en,
        persistido_en=persistido_en,
        latencia_e2e_ms=detail.get("latencia_e2e_ms"),
        latencia_anomala=bool(detail.get("latencia_anomala", False)),
    )
    sector_obj = detail.get("sector") or {}
    conf_recibida, conf_instant, conf_delta = confirmation or (False, None, None)
    return CaseResult(
        case_id=case_id,
        canal=canal,
        incidente_id=detail.get("id"),
        numero_incidente=detail.get("numero_incidente"),
        sector=sector_obj.get("nombre") if isinstance(sector_obj, dict) else None,
        revision=detail.get("requiere_revision_humana"),
        t_envio=t_envio.isoformat(),
        ingresado_en=ingresado_en.isoformat() if ingresado_en else None,
        persistido_en=persistido_en.isoformat() if persistido_en else None,
        latencia_e2e_ms=detail.get("latencia_e2e_ms"),
        t_pipeline_s=metric.t_pipeline_s,
        t_espera_s=metric.t_espera_s,
        t_e2e_s=metric.t_e2e_s,
        origen_message_id=origen_message_id,
        confirmacion_recibida=conf_recibida,
        t_confirmacion=conf_instant.isoformat() if conf_instant else None,
        t_confirmacion_s=conf_delta,
        anomalo=metric.anomalo,
        error=None,
    )


# ── HTTP / transport layer ──────────────────────────────────────────────────


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(session: Any, base_url: str, username: str, password: str, verify: Any) -> str:
    response = ic._request_with_retry(
        session,
        "POST",
        f"{base_url}{LOGIN_PATH}",
        json={"username": username, "password": password},
        verify=verify,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login fallido: HTTP {response.status_code}")
    return response.json()["access_token"]


def _get_detail(
    session: Any,
    base_url: str,
    token: str,
    incidente_id: int,
    verify: Any,
    timeout: float,
    backoff: float,
) -> Any:
    return ic._request_with_retry(
        session,
        "GET",
        f"{base_url}{INCIDENTES_PATH}{incidente_id}",
        headers=_headers(token),
        verify=verify,
        timeout=timeout,
        backoff_base=backoff,
    )


def ingest_web_case(
    *,
    session: Any,
    token: str,
    base_url: str,
    webhook_url: str,
    case_id: str,
    descripcion: str,
    verify: Any,
    timeout: float,
    prioridad: str = "media",
    t_envio: Any = None,
    retry_backoff: float = ic.BACKOFF_BASE_S,
) -> CaseResult:
    """POST one case to the web webhook, then read its persisted instants."""
    envio = _to_utc(t_envio) or datetime.now(UTC)
    payload = build_web_payload(
        descripcion=descripcion, case_id=case_id, prioridad=prioridad
    )
    try:
        response = ic._request_with_retry(
            session,
            "POST",
            webhook_url,
            json=payload,
            verify=verify,
            timeout=timeout,
            backoff_base=retry_backoff,
        )
    except Exception as exc:  # noqa: BLE001 - never leak body/description
        return _error_result(case_id, CANAL_WEB, envio, type(exc).__name__)
    if response.status_code >= 400:
        return _error_result(case_id, CANAL_WEB, envio, _error_label(response))

    body = response.json()
    incidente_id = body.get("incidente_id")
    if incidente_id is None:
        return _error_result(case_id, CANAL_WEB, envio, "sin_incidente_id")

    try:
        detail_response = _get_detail(
            session, base_url, token, int(incidente_id), verify, timeout, retry_backoff
        )
    except Exception as exc:  # noqa: BLE001
        return _error_result(case_id, CANAL_WEB, envio, type(exc).__name__)
    if detail_response.status_code >= 400:
        return _error_result(case_id, CANAL_WEB, envio, _error_label(detail_response))

    return _result_from_detail(
        case_id=case_id,
        canal=CANAL_WEB,
        detail=detail_response.json(),
        t_envio=envio,
        origen_message_id=payload["origen_message_id"],
    )


def build_email_message(
    *,
    case_id: str,
    descripcion: str,
    domain: str,
    sender: str,
    recipient: str,
) -> EmailMessage:
    """Build the ingest email with a deterministic ``Message-ID`` (D6)."""
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = f"Incidente {case_id}"
    msg["Message-ID"] = build_message_id(case_id, domain)
    msg.set_content(descripcion)
    return msg


def find_incidente_by_origen(
    *,
    session: Any,
    base_url: str,
    token: str,
    keys: Sequence[str],
    verify: Any,
    timeout: float,
    poll_timeout: float,
    poll_interval: float,
    min_ingresado_en: Any,
    backoff: float = ic.BACKOFF_BASE_S,
) -> dict[str, Any] | None:
    """Poll the exact-filter list endpoint until the correlated incident appears."""
    deadline = time.monotonic() + max(poll_timeout, 0.0)
    while True:
        for key in keys:
            query = urlencode({"origen_message_id": key, "limit": DEFAULT_LIST_LIMIT})
            url = f"{base_url}{INCIDENTES_PATH}?{query}"
            try:
                response = ic._request_with_retry(
                    session,
                    "GET",
                    url,
                    headers=_headers(token),
                    verify=verify,
                    timeout=timeout,
                    backoff_base=backoff,
                )
            except Exception:  # noqa: BLE001 - transient; retry until deadline
                continue
            if response.status_code >= 400:
                continue
            items = response.json()
            chosen = select_correlated_incident(items, min_ingresado_en)
            if chosen is not None:
                detail_response = _get_detail(
                    session, base_url, token, int(chosen["id"]), verify, timeout, backoff
                )
                if detail_response.status_code < 400:
                    return detail_response.json()
                return None
        if time.monotonic() >= deadline:
            return None
        time.sleep(max(poll_interval, 0.0))


def _observe_confirmation(
    confirmation_observer: Callable[[str], datetime | None] | None,
    numero_incidente: str | None,
    timeout: float,
    interval: float,
) -> tuple[bool, datetime | None, float | None]:
    """Secondary check via a SEPARATE receive path (never the ingest mailbox)."""
    if confirmation_observer is None or numero_incidente is None:
        return (False, None, None)
    deadline = time.monotonic() + max(timeout, 0.0)
    while True:
        instant = confirmation_observer(numero_incidente)
        if instant is not None:
            return (True, _to_utc(instant), None)
        if time.monotonic() >= deadline:
            return (False, None, None)
        time.sleep(max(interval, 0.0))


def ingest_email_case(
    *,
    session: Any,
    token: str,
    base_url: str,
    case_id: str,
    descripcion: str,
    domain: str,
    sender: str,
    recipient: str,
    verify: Any,
    timeout: float,
    poll_timeout: float,
    poll_interval: float,
    send_func: Callable[[EmailMessage], None],
    t_envio: Any = None,
    confirmation_observer: Callable[[str], datetime | None] | None = None,
    confirmation_timeout: float = 0.0,
    confirmation_interval: float = 0.0,
    retry_backoff: float = ic.BACKOFF_BASE_S,
) -> CaseResult:
    """Send one case by email, correlate exactly and derive the metric.

    The confirmation email is checked via a separate receive path and never
    invalidates the primary API-instants measurement.
    """
    envio = _to_utc(t_envio) or datetime.now(UTC)
    message = build_email_message(
        case_id=case_id,
        descripcion=descripcion,
        domain=domain,
        sender=sender,
        recipient=recipient,
    )
    try:
        send_func(message)
    except Exception as exc:  # noqa: BLE001
        return _error_result(
            case_id, CANAL_CORREO, envio, "smtp_" + type(exc).__name__
        )

    keys = correlation_keys(case_id, domain)
    detail = find_incidente_by_origen(
        session=session,
        base_url=base_url,
        token=token,
        keys=keys,
        verify=verify,
        timeout=timeout,
        poll_timeout=poll_timeout,
        poll_interval=poll_interval,
        min_ingresado_en=envio,
        backoff=retry_backoff,
    )
    if detail is None:
        return _error_result(case_id, CANAL_CORREO, envio, "timeout_correlacion")

    recibida, instant, _ = _observe_confirmation(
        confirmation_observer,
        detail.get("numero_incidente"),
        confirmation_timeout,
        confirmation_interval,
    )
    _, delta = derive_confirmation(
        t_envio=envio, t_confirmacion=instant if recibida else None
    )
    return _result_from_detail(
        case_id=case_id,
        canal=CANAL_CORREO,
        detail=detail,
        t_envio=envio,
        origen_message_id=normalize_message_id(build_message_id(case_id, domain)),
        confirmation=(recibida, instant, delta),
    )


# ── CLI / orchestration ─────────────────────────────────────────────────────


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Carga el corpus de la tesis por el flujo N8N real (web y correo), "
            "deriva la metrica hibrida y escribe los tiempos de vuelta al XLSX, "
            "al CSV y al JSON de evaluacion. Nunca imprime descripciones."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--webhook-url", default=DEFAULT_WEBHOOK_URL)
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--source", choices=("json", "csv", "xlsx"), default="json")
    parser.add_argument("--json", default=DEFAULT_JSON)
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--xlsx", default=DEFAULT_XLSX)
    parser.add_argument("--sidecar", default=DEFAULT_SIDECAR)
    parser.add_argument("--only-channel", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--poll-timeout", type=float, default=POLL_TIMEOUT_S)
    parser.add_argument("--poll-interval", type=float, default=POLL_INTERVAL_S)
    parser.add_argument("--confirmation-timeout", type=float, default=CONFIRMATION_TIMEOUT_S)
    parser.add_argument("--confirmation-interval", type=float, default=CONFIRMATION_INTERVAL_S)
    parser.add_argument("--mail-domain", default=None)
    parser.add_argument("--smtp-host", default=os.environ.get("INGEST_SMTP_HOST"))
    parser.add_argument("--smtp-port", type=int, default=int(os.environ.get("INGEST_SMTP_PORT", "465")))
    parser.add_argument("--smtp-from", default=os.environ.get("INGEST_SMTP_FROM"))
    parser.add_argument("--ingest-address", default=os.environ.get("INGEST_MAILBOX_ADDRESS"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _channel_counts(cases: Sequence[Case]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        canal = map_canal(case.canal) or case.canal.strip() or "desconocido"
        counts[canal] = counts.get(canal, 0) + 1
    return counts


def _pending_nulls(path: str | Path) -> int | None:
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return sum(
        1
        for c in doc.get("casos", [])
        if c.get("tiempo_automatizado_s") is None
    )


def _source_path(args: argparse.Namespace) -> str:
    if args.source == "json":
        return args.json
    if args.source == "xlsx":
        return args.xlsx
    return args.csv


def _print_counts(all_cases: Sequence[Case], selected: Sequence[Case]) -> None:
    total = _channel_counts(all_cases)
    print(f"Casos en el corpus: {len(all_cases)} | seleccionados: {len(selected)}")
    for canal, count in sorted(total.items()):
        print(f"  canal {canal!r}: {count}")


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    cases = read_cases(_source_path(args), args.source)
    selected = select_cases(cases, args.only_channel, args.limit)
    _print_counts(cases, selected)

    ingestables = [c for c in selected if map_canal(c.canal) in INGESTABLE_CHANNELS]

    if args.dry_run:
        telefono = sum(1 for c in selected if map_canal(c.canal) == CANAL_TELEFONO)
        no_mapeados = sum(1 for c in selected if map_canal(c.canal) is None)
        pending = _pending_nulls(args.json) if args.source == "json" else None
        pending_txt = "n/a" if pending is None else str(pending)
        print(
            f"DRY-RUN: ingesta={len(ingestables)} telefono_omitido={telefono} "
            f"sin_mapear={no_mapeados} pendientes_nulos={pending_txt}. "
            "No se ejecuto red ni escritura."
        )
        return 0

    username = os.environ.get("INGEST_OPERATOR_USERNAME")
    password = os.environ.get("INGEST_OPERATOR_PASSWORD")
    if not username or not password:
        print(
            "ERROR: faltan INGEST_OPERATOR_USERNAME / INGEST_OPERATOR_PASSWORD.\n"
            "Exportar credenciales de un operador con alcance total antes de correr. "
            "Ver README.md (no hay secretos hardcodeados).",
            file=sys.stderr,
        )
        return 2

    confirmation_observer = build_confirmation_observer()
    if confirmation_observer is not None and any(
        map_canal(c.canal) == CANAL_CORREO for c in ingestables
    ):
        separation_error = confirmation_separation_error()
        if separation_error:
            print(separation_error, file=sys.stderr)
            return 3

    import requests  # local import: keeps module import side-effect free

    base_url = args.base_url.rstrip("/")
    session = requests.Session()
    verify: Any = False if args.insecure else True
    if args.insecure:
        try:
            import urllib3  # noqa: PLC0415

            urllib3.disable_warnings()
        except Exception:  # noqa: BLE001
            pass

    domain = (args.mail_domain or resolve_mail_domain()).strip() or DEFAULT_MAIL_DOMAIN
    sender = args.smtp_from or args.ingest_address
    recipient = args.ingest_address
    token = login(session, base_url, username, password, verify)
    print("Login OK. Iniciando ingesta por el flujo N8N...")

    def _send_email(message: EmailMessage) -> None:
        _send_via_smtp(message, args)

    results: list[CaseResult] = []
    for index, case in enumerate(selected, start=1):
        canal = map_canal(case.canal)
        if canal not in INGESTABLE_CHANNELS:
            continue
        if index > 1 and args.sleep > 0:
            time.sleep(args.sleep)
        t_envio = datetime.now(UTC)
        if canal == CANAL_WEB:
            result = ingest_web_case(
                session=session,
                token=token,
                base_url=base_url,
                webhook_url=args.webhook_url,
                case_id=case.case_id,
                descripcion=case.descripcion,
                verify=verify,
                timeout=args.timeout,
                t_envio=t_envio,
            )
        else:
            result = ingest_email_case(
                session=session,
                token=token,
                base_url=base_url,
                case_id=case.case_id,
                descripcion=case.descripcion,
                domain=domain,
                sender=sender or "",
                recipient=recipient or "",
                verify=verify,
                timeout=args.timeout,
                poll_timeout=args.poll_timeout,
                poll_interval=args.poll_interval,
                send_func=_send_email,
                t_envio=t_envio,
                confirmation_observer=confirmation_observer,
                confirmation_timeout=args.confirmation_timeout,
                confirmation_interval=args.confirmation_interval,
            )
        results.append(result)
        if result.error:
            print(f"[{index}/{len(selected)}] {case.case_id}: error {result.error}")
        else:
            print(
                f"[{index}/{len(selected)}] {case.case_id}: incidente "
                f"{result.incidente_id} e2e={result.t_e2e_s} anomaly={result.anomalo}"
            )

    write_sidecar_json(args.sidecar, results)
    by_id = {r.case_id: r for r in results}
    write_csv_results(args.csv, by_id)
    write_xlsx_results(args.xlsx, by_id)

    measurements = {
        r.case_id: r.t_e2e_s
        for r in results
        if not r.anomalo and r.t_e2e_s is not None and r.error is None
    }
    pending = merge_evaluation_json(args.json, measurements)

    ok = sum(1 for r in results if r.error is None and not r.anomalo)
    anomalos = sum(1 for r in results if r.error is None and r.anomalo)
    fallidos = sum(1 for r in results if r.error is not None)
    print(
        f"Listo: ok={ok} anomalos={anomalos} fallidos={fallidos} "
        f"telefono_pendiente={pending} sidecar={args.sidecar}"
    )
    return 0 if (fallidos == 0 and anomalos == 0) else 1


def _send_via_smtp(message: EmailMessage, args: argparse.Namespace) -> None:  # pragma: no cover - I/O
    """Send via SMTP using env-provided credentials (no secrets in code)."""
    import smtplib
    import ssl

    host = args.smtp_host
    if not host:
        raise RuntimeError("INGEST_SMTP_HOST no configurado")
    smtp_user = os.environ.get("INGEST_SMTP_USER")
    smtp_password = os.environ.get("INGEST_SMTP_PASSWORD")
    context = ssl.create_default_context()
    if args.smtp_port == 465:
        with smtplib.SMTP_SSL(host, args.smtp_port, context=context) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, args.smtp_port) as server:
            server.starttls(context=context)
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
