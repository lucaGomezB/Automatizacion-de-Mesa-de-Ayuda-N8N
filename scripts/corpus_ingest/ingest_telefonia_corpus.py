"""Telephony corpus recovery and write-back (c-70, section 5).

Purpose
-------
Recover the measurement of each telephony corpus case by ``corpus_case_id`` from
the dedicated read endpoint ``GET /api/v1/telefonia/ingresos`` (D5) and write it
back to the corpus with the SAME harness guarantees as ``ingest_via_n8n`` (D6):

    t_pipeline_s = t_e2e_s = latencia_e2e_ms / 1000
    t_espera_s   = None   (empty/N-A: there is no client wait in telephony, D4)

The canonical ``tiempo_automatizado_s`` is ``t_e2e_s`` and matches the other
channels (single source of truth: the linked incident's ``latencia_e2e_ms``).

``--replace`` (D7) removes the PRIOR rows of a case, keeping only the latest
ingreso. It is destructive (governance ALTO): ``--replace`` alone is a dry-run
that neither deletes nor writes; the destructive run requires the explicit
``--confirm-replace`` approval.

Privacy
-------
Corpus descriptions are REAL internal text. This module NEVER logs, prints or
persists a description. On error only a short label is emitted (status code or
exception type). The sidecar is description-free by construction.

No secrets live in this file. Credentials are read from the environment:
``INGEST_OPERATOR_USERNAME`` / ``INGEST_OPERATOR_PASSWORD`` (D5).
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlencode

import ingest_corpus as ic
import ingest_via_n8n as ivn

# ── Canonical contract ──────────────────────────────────────────────────────

CANAL_TELEFONO = ivn.CANAL_TELEFONO  # "telefono"

HEADER_AUTO_TIME = ivn.HEADER_AUTO_TIME
LATENCIA_COL = ivn.LATENCIA_COL
PIPELINE_COL = ivn.PIPELINE_COL
ESPERA_COL = ivn.ESPERA_COL

TELEFONIA_INGRESOS_PATH = "/api/v1/telefonia/ingresos"

# A case with no ingreso is a normal pending state, not a failure.
PENDING_LABEL = "sin_ingreso"

ENV_OPERATOR_USERNAME = "INGEST_OPERATOR_USERNAME"
ENV_OPERATOR_PASSWORD = "INGEST_OPERATOR_PASSWORD"  # gitleaks:allow (nombre de variable de entorno, no un secreto)

DEFAULT_BASE_URL = ivn.DEFAULT_BASE_URL
DEFAULT_JSON = ivn.DEFAULT_JSON
DEFAULT_CSV = ivn.DEFAULT_CSV
DEFAULT_XLSX = ivn.DEFAULT_XLSX
DEFAULT_SIDECAR = "data/corpus_resultados_telefonia.json"


# ── Pure metric logic (tasks 5.1-5.3) ───────────────────────────────────────


@dataclass(frozen=True)
class TelefoniaMetric:
    """Telephony latency decomposition (D4).

    In telephony ``ingresado_en`` is sealed when the backend receives the
    recording-status callback, so there is no client wait: ``t_espera_s`` is
    always ``None`` (empty/N-A, never fabricated as zero).
    """

    t_pipeline_s: float | None
    t_espera_s: float | None
    t_e2e_s: float | None
    anomalo: bool


def derive_telefonia_metric(
    latencia_e2e_ms: int | None, *, latencia_anomala: bool = False
) -> TelefoniaMetric:
    """Derive ``t_pipeline_s = t_e2e_s = latencia_e2e_ms / 1000`` for one case.

    A case is anomalous (excluded from the corpus and analysis) when the latency
    is missing, non-positive or explicitly flagged. Anomalies are reported, NOT
    clamped to zero (a clamp would fabricate a value that does not exist).
    """
    if latencia_anomala or latencia_e2e_ms is None or latencia_e2e_ms <= 0:
        return TelefoniaMetric(None, None, None, True)
    seconds = round(float(latencia_e2e_ms) / 1000.0, 3)
    return TelefoniaMetric(seconds, None, seconds, False)


def build_telefonia_result(
    *, case_id: str, detail: Mapping[str, Any]
) -> ivn.CaseResult:
    """Build a description-free ``CaseResult`` from the endpoint payload.

    ``t_espera_s`` is always ``None`` so the existing writers omit the wait cell
    without touching it (D4).
    """
    latencia = detail.get("latencia_e2e_ms")
    metric = derive_telefonia_metric(
        latencia, latencia_anomala=bool(detail.get("latencia_anomala", False))
    )
    ingresado_en = ivn._to_utc(detail.get("ingresado_en"))
    persistido_en = ivn._to_utc(detail.get("persistido_en"))
    return ivn.CaseResult(
        case_id=case_id,
        canal=CANAL_TELEFONO,
        incidente_id=detail.get("incidente_id"),
        numero_incidente=None,
        sector=None,
        revision=None,
        t_envio=None,
        ingresado_en=ingresado_en.isoformat() if ingresado_en else None,
        persistido_en=persistido_en.isoformat() if persistido_en else None,
        latencia_e2e_ms=latencia if isinstance(latencia, int) else None,
        t_pipeline_s=metric.t_pipeline_s,
        t_espera_s=metric.t_espera_s,
        t_e2e_s=metric.t_e2e_s,
        origen_message_id=None,
        confirmacion_recibida=False,
        t_confirmacion=None,
        t_confirmacion_s=None,
        anomalo=metric.anomalo,
        error=None,
    )


# ── HTTP layer ──────────────────────────────────────────────────────────────


def recover_telefonia_case(
    *,
    session: Any,
    base_url: str,
    token: str,
    case_id: str,
    verify: Any,
    timeout: float,
    backoff: float = ic.BACKOFF_BASE_S,
) -> ivn.CaseResult:
    """Recover the latest ingreso of ``case_id`` and derive its metric.

    A ``404`` means the case has no ingreso yet: it is reported as pending and
    nothing is written. Any other non-2xx becomes a short error label.
    """
    query = urlencode({"corpus_case_id": case_id, "latest": "true"})
    url = f"{base_url}{TELEFONIA_INGRESOS_PATH}?{query}"
    response = ic._request_with_retry(
        session,
        "GET",
        url,
        headers=ivn._headers(token),
        verify=verify,
        timeout=timeout,
        backoff_base=backoff,
    )
    if response.status_code == 404:
        return ivn._error_result(case_id, CANAL_TELEFONO, None, PENDING_LABEL)
    if response.status_code >= 400:
        return ivn._error_result(case_id, CANAL_TELEFONO, None, ivn._error_label(response))
    return build_telefonia_result(case_id=case_id, detail=response.json())


def delete_previos(
    *,
    session: Any,
    base_url: str,
    token: str,
    case_id: str,
    verify: Any,
    timeout: float,
    dry_run: bool,
    backoff: float = ic.BACKOFF_BASE_S,
) -> dict[str, Any] | None:
    """Call the scoped delete endpoint for ``--replace`` (dry-run by default).

    The endpoint keeps the latest ingreso and removes the prior ones, scoped to
    the ``corpus_case_id`` (never other cases). Returns ``None`` on error.
    """
    query = urlencode(
        {"corpus_case_id": case_id, "dry_run": "true" if dry_run else "false"}
    )
    url = f"{base_url}{TELEFONIA_INGRESOS_PATH}?{query}"
    response = ic._request_with_retry(
        session,
        "DELETE",
        url,
        headers=ivn._headers(token),
        verify=verify,
        timeout=timeout,
        backoff_base=backoff,
    )
    if response.status_code >= 400:
        return None
    return response.json()


# ── Write-back (tasks 5.4-5.6) ──────────────────────────────────────────────


def write_back(
    *,
    csv_path: str | Path,
    xlsx_path: str | Path,
    sidecar_path: str | Path,
    json_path: str | Path,
    results: Iterable[ivn.CaseResult],
) -> int:
    """Write telephony results to both registration files and the eval JSON.

    Reuses the harness writers (D6): idempotent columns, no ``null`` over an
    existing value, no description in the sidecar, and a numeric-only JSON merge
    that never weakens ``evaluation/corpus.py::_a_float``. Returns the count of
    cases still null in the evaluation JSON.
    """
    results = list(results)
    by_id = {result.case_id: result for result in results}
    ivn.write_sidecar_json(sidecar_path, results)
    ivn.write_csv_results(csv_path, by_id)
    ivn.write_xlsx_results(xlsx_path, by_id)
    measurements = {
        result.case_id: result.t_e2e_s
        for result in results
        if ivn._should_write_metric(result) and result.t_e2e_s is not None
    }
    return ivn.merge_evaluation_json(json_path, measurements)


# ── CLI / orchestration ─────────────────────────────────────────────────────


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recupera las mediciones de telefonia del corpus por corpus_case_id "
            "desde el endpoint dedicado y las escribe de vuelta al XLSX, al CSV "
            "y al JSON de evaluacion. Nunca imprime descripciones."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--source", choices=("json", "csv", "xlsx"), default="json")
    parser.add_argument("--json", default=DEFAULT_JSON)
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--xlsx", default=DEFAULT_XLSX)
    parser.add_argument("--sidecar", default=DEFAULT_SIDECAR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Reemplaza las filas previas del caso (dry-run por defecto).",
    )
    parser.add_argument(
        "--confirm-replace",
        action="store_true",
        help="Aprobacion explicita para el borrado destructivo de --replace.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _source_path(args: argparse.Namespace) -> str:
    if args.source == "json":
        return args.json
    if args.source == "xlsx":
        return args.xlsx
    return args.csv


def _print_counts(all_cases: Sequence[ivn.Case], selected: Sequence[ivn.Case]) -> None:
    total = sum(
        1 for case in all_cases if ivn.map_canal(case.canal) == CANAL_TELEFONO
    )
    print(f"Casos en el corpus: {len(all_cases)} | telefonia: {total} | seleccionados: {len(selected)}")


def _case_label(result: ivn.CaseResult) -> str:
    if result.error == PENDING_LABEL:
        return "pendiente"
    if result.error:
        return f"error {result.error}"
    return f"e2e={result.t_e2e_s} anomalo={result.anomalo}"


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    if args.confirm_replace and not args.replace:
        print(
            "ERROR: --confirm-replace requiere --replace (no hay nada que reemplazar).",
            file=sys.stderr,
        )
        return 2

    cases = ivn.read_cases(_source_path(args), args.source)
    selected = ivn.select_cases(cases, CANAL_TELEFONO, args.limit)
    _print_counts(cases, selected)

    if args.dry_run:
        print(
            f"DRY-RUN: telefonia={len(selected)}. No se ejecuto red ni escritura."
        )
        return 0

    username = os.environ.get(ENV_OPERATOR_USERNAME)
    password = os.environ.get(ENV_OPERATOR_PASSWORD)
    if not username or not password:
        print(
            "ERROR: faltan INGEST_OPERATOR_USERNAME / INGEST_OPERATOR_PASSWORD.\n"
            "Exportar credenciales de un operador administrador_directorio antes "
            "de correr. Ver README.md (no hay secretos hardcodeados).",
            file=sys.stderr,
        )
        return 2

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

    token = ivn.login(session, base_url, username, password, verify)
    print("Login OK. Recuperando mediciones de telefonia...")

    results: list[ivn.CaseResult] = []
    for index, case in enumerate(selected, start=1):
        try:
            result = recover_telefonia_case(
                session=session,
                base_url=base_url,
                token=token,
                case_id=case.case_id,
                verify=verify,
                timeout=args.timeout,
            )
        except Exception as exc:  # noqa: BLE001 - one case must not abort the run
            result = ivn._error_result(
                case.case_id, CANAL_TELEFONO, None, type(exc).__name__
            )
        results.append(result)
        print(f"[{index}/{len(selected)}] {case.case_id}: {_case_label(result)}")

    if args.replace:
        for case in selected:
            try:
                counts = delete_previos(
                    session=session,
                    base_url=base_url,
                    token=token,
                    case_id=case.case_id,
                    verify=verify,
                    timeout=args.timeout,
                    dry_run=not args.confirm_replace,
                )
            except Exception:  # noqa: BLE001 - never leak body/description
                counts = None
            if args.confirm_replace:
                print(f"replace {case.case_id}: {counts}")
            else:
                print(f"replace {case.case_id}: dry-run {counts}")
        if not args.confirm_replace:
            print(
                "DRY-RUN --replace: no se borro ni se escribio nada. "
                "Usar --confirm-replace para ejecutar el reemplazo."
            )
            return 0

    pending_nulls = write_back(
        csv_path=args.csv,
        xlsx_path=args.xlsx,
        sidecar_path=args.sidecar,
        json_path=args.json,
        results=results,
    )

    medidos = sum(
        1 for r in results if r.error is None and not r.anomalo
    )
    anomalos = sum(1 for r in results if r.error is None and r.anomalo)
    pendientes = sum(1 for r in results if r.error == PENDING_LABEL)
    fallidos = sum(
        1 for r in results if r.error is not None and r.error != PENDING_LABEL
    )
    print(
        f"Listo: medidos={medidos} anomalos={anomalos} pendientes={pendientes} "
        f"fallidos={fallidos} telefono_pendiente={pending_nulls} "
        f"sidecar={args.sidecar}"
    )
    return 1 if fallidos else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
