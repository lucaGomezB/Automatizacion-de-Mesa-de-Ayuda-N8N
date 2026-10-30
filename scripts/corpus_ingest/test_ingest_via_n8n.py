"""Offline unit tests for the N8N corpus ingest harness (c-68).

No network, no real corpus, no mutation of ``data/``. Every filesystem touch
happens inside ``tmp_path``. Descriptions here are synthetic and public text;
the real corpus descriptions are never loaded.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict, fields, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Los tests de campana arman planes con el paquete `evaluation` de la raiz del repo;
# se agrega la raiz a sys.path de forma relativa al archivo (mismo patron que
# test_ingest_telefonia_corpus.py) para correr tanto desde la raiz como desde este directorio.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ingest_via_n8n as ivn  # noqa: E402
from evaluation import plan_campana as pc  # noqa: E402

UTC = timezone.utc


def _dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2026, 9, 29, hour, minute, second, tzinfo=UTC)


# ── Fakes ───────────────────────────────────────────────────────────────────


class FakeResponse:
    def __init__(self, status_code: int = 200, body: dict | None = None) -> None:
        self.status_code = status_code
        self._body = body or {}

    def json(self) -> dict:
        return self._body


class FakeSession:
    """Minimal ``requests.Session`` stand-in; records calls."""

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.calls: list[tuple] = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _webhook_body(incidente_id: int | None, numero: str | None = "INC-000001") -> dict:
    return {"incidente_id": incidente_id, "numero_incidente": numero}


def _detail_body(**overrides) -> dict:
    body = {
        "id": 11,
        "numero_incidente": "INC-000011",
        "sector": {"nombre": "Sistemas"},
        "requiere_revision_humana": False,
        "ingresado_en": _dt(12, 0, 5).isoformat(),
        "persistido_en": _dt(12, 0, 7).isoformat(),
        "latencia_e2e_ms": 2000,
        "latencia_anomala": False,
    }
    body.update(overrides)
    return body


# ── Metric derivation (tasks 1.1-1.3) ───────────────────────────────────────


def test_derive_metric_pipeline_espera_e2e_sum():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=_dt(12, 0, 5),
        persistido_en=_dt(12, 0, 7),
        latencia_e2e_ms=2000,
    )
    assert metric.t_pipeline_s == pytest.approx(2.0)
    assert metric.t_espera_s == pytest.approx(5.0)
    assert metric.t_e2e_s == pytest.approx(7.0)
    assert metric.t_espera_s + metric.t_pipeline_s == pytest.approx(metric.t_e2e_s)
    assert metric.anomalo is False


def test_tiempo_automatizado_is_e2e_for_web_and_correo():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=_dt(12, 0, 5),
        persistido_en=_dt(12, 0, 7),
        latencia_e2e_ms=2000,
    )
    assert ivn.tiempo_automatizado_s("web", metric) == pytest.approx(7.0)
    assert ivn.tiempo_automatizado_s("correo", metric) == pytest.approx(7.0)


def test_derive_metric_email_includes_poller_wait():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=_dt(12, 0, 50),
        persistido_en=_dt(12, 0, 52),
        latencia_e2e_ms=2000,
    )
    assert metric.t_espera_s == pytest.approx(50.0)
    assert metric.t_pipeline_s == pytest.approx(2.0)
    assert metric.t_e2e_s == pytest.approx(52.0)
    assert metric.anomalo is False


def test_derive_metric_null_latency_is_anomalous():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=_dt(12, 0, 5),
        persistido_en=_dt(12, 0, 7),
        latencia_e2e_ms=None,
    )
    assert metric.anomalo is True
    assert ivn.tiempo_automatizado_s("web", metric) is None


def test_derive_metric_non_positive_e2e_is_anomalous():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 10),
        ingresado_en=_dt(12, 0, 3),
        persistido_en=_dt(12, 0, 5),
        latencia_e2e_ms=2000,
    )
    assert metric.t_e2e_s <= 0
    assert metric.anomalo is True


def test_derive_metric_negative_espera_beyond_skew_is_anomalous():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 10),
        ingresado_en=_dt(12, 0, 5),
        persistido_en=_dt(12, 0, 30),
        latencia_e2e_ms=25000,
    )
    assert metric.t_espera_s < 0
    assert metric.anomalo is True


def test_derive_metric_explicit_anomaly_flag_is_anomalous():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=_dt(12, 0, 5),
        persistido_en=_dt(12, 0, 7),
        latencia_e2e_ms=2000,
        latencia_anomala=True,
    )
    assert metric.anomalo is True


def test_derive_metric_missing_instant_is_anomalous():
    metric = ivn.derive_metric(
        t_envio=_dt(12, 0, 0),
        ingresado_en=None,
        persistido_en=_dt(12, 0, 7),
        latencia_e2e_ms=2000,
    )
    assert metric.anomalo is True
    assert metric.t_e2e_s is None


# ── Web payload (tasks 1.4-1.6) ─────────────────────────────────────────────


def test_build_web_payload_shape_and_determinism():
    payload = ivn.build_web_payload(descripcion="d" * 20, case_id="R007")
    assert payload["descripcion"] == "d" * 20
    assert payload["prioridad"] == "media"
    assert payload["origen_message_id"] == "corpus-R007"
    again = ivn.build_web_payload(descripcion="x" * 30, case_id="R007")
    assert again["origen_message_id"] == payload["origen_message_id"]


def test_build_web_payload_custom_priority_and_special_chars():
    payload = ivn.build_web_payload(
        descripcion="a, b; c <d>", case_id="R008", prioridad="alta"
    )
    assert payload["prioridad"] == "alta"
    assert payload["descripcion"] == "a, b; c <d>"


def test_build_web_payload_has_no_backend_rejected_fields():
    payload = ivn.build_web_payload(descripcion="d" * 20, case_id="R009")
    assert set(payload) == {"descripcion", "prioridad", "origen_message_id"}


# ── Message-ID (tasks 1.7-1.9) ──────────────────────────────────────────────


def test_build_message_id_and_normalize():
    header = ivn.build_message_id("R001", "corpus.local")
    assert header == "<corpus-R001@corpus.local>"
    assert ivn.normalize_message_id(header) == "corpus-R001@corpus.local"
    assert ivn.normalize_message_id("corpus-R001@corpus.local") == "corpus-R001@corpus.local"


def test_correlation_keys_cover_bracketed_and_plain():
    keys = ivn.correlation_keys("R002", "corpus.local")
    assert "<corpus-R002@corpus.local>" in keys
    assert "corpus-R002@corpus.local" in keys


def test_resolve_mail_domain_from_env(monkeypatch):
    monkeypatch.setenv("INGEST_CORPUS_MAIL_DOMAIN", "example.test")
    assert ivn.resolve_mail_domain() == "example.test"
    monkeypatch.delenv("INGEST_CORPUS_MAIL_DOMAIN", raising=False)
    assert ivn.resolve_mail_domain() == ivn.DEFAULT_MAIL_DOMAIN


def test_normalize_message_id_repeated_and_whitespace():
    assert ivn.normalize_message_id("  <corpus-R001@corpus.local>  ") == "corpus-R001@corpus.local"
    assert ivn.normalize_message_id("corpus-R001@corpus.local") == "corpus-R001@corpus.local"


# ── Channel mapping / selection (tasks 1.10-1.12) ────────────────────────────


def test_map_canal_json_labels_with_accents():
    assert ivn.map_canal("correo electrónico") == "correo"
    assert ivn.map_canal("formulario web") == "web"
    assert ivn.map_canal("llamada telefónica") == "telefono"


def test_map_canal_csv_labels_and_case_insensitive():
    assert ivn.map_canal("Correo") == "correo"
    assert ivn.map_canal("Formulario Web") == "web"
    assert ivn.map_canal("Telefono") == "telefono"
    assert ivn.map_canal("CORREO") == "correo"


def test_map_canal_unknown_empty_spaces():
    assert ivn.map_canal("  ") is None
    assert ivn.map_canal("fax") is None
    assert ivn.map_canal(None) is None


def test_select_cases_filters_channel_and_limit():
    cases = [
        ivn.Case("R001", "d1", "correo electrónico"),
        ivn.Case("R002", "d2", "llamada telefónica"),
        ivn.Case("R003", "d3", "formulario web"),
    ]
    only_correo = ivn.select_cases(cases, "correo", None)
    assert [c.case_id for c in only_correo] == ["R001"]
    limited = ivn.select_cases(cases, None, 2)
    assert [c.case_id for c in limited] == ["R001", "R002"]


# ── Confirmation secondary check (tasks 1.13-1.14) ──────────────────────────


def test_confirmation_subject_matches_workflow():
    assert ivn.confirmation_subject("INC-000011") == (
        "Incidente registrado - Numero INC-000011"
    )


def test_derive_confirmation_present():
    recibida, delta = ivn.derive_confirmation(
        t_envio=_dt(12, 0, 0), t_confirmacion=_dt(12, 0, 30)
    )
    assert recibida is True
    assert delta == pytest.approx(30.0)


def test_derive_confirmation_absent_returns_false_and_none():
    recibida, delta = ivn.derive_confirmation(t_envio=_dt(12, 0, 0), t_confirmacion=None)
    assert recibida is False
    assert delta is None


def test_confirmation_path_must_be_separate():
    assert ivn.confirmation_path_is_separate(
        ingest_host="mail.local",
        confirmation_host="mail.local",
        ingest_mailbox="INBOX",
        confirmation_folder="Confirmaciones",
        ingest_user="ingesta@local",
        confirmation_user="ingesta@local",
    ) is True
    assert ivn.confirmation_path_is_separate(
        ingest_host="mail.local",
        confirmation_host="mail.local",
        ingest_mailbox="INBOX",
        confirmation_folder="INBOX",
        ingest_user="ingesta@local",
        confirmation_user="ingesta@local",
    ) is False


# ── Exact correlation selector (task 3.3) ───────────────────────────────────


def test_select_correlated_incident_skips_stale_and_picks_fresh():
    items = [
        {"id": 1, "ingresado_en": _dt(11, 0, 0).isoformat()},
        {"id": 2, "ingresado_en": _dt(12, 0, 5).isoformat()},
    ]
    chosen = ivn.select_correlated_incident(items, _dt(12, 0, 0))
    assert chosen["id"] == 2


def test_select_correlated_incident_none_when_all_stale():
    items = [{"id": 1, "ingresado_en": _dt(11, 0, 0).isoformat()}]
    assert ivn.select_correlated_incident(items, _dt(12, 0, 0)) is None


def test_select_incident_by_window_documented_fallback():
    items = [
        {"id": 1, "ingresado_en": _dt(12, 0, 30).isoformat()},
        {"id": 2, "ingresado_en": _dt(12, 0, 40).isoformat()},
    ]
    chosen = ivn.select_incident_by_window(
        items, t_envio=_dt(12, 0, 30), claimed_ids={1}
    )
    assert chosen["id"] == 2


def test_select_incident_by_window_excludes_unrelated_old_and_claimed():
    items = [
        {"id": 1, "ingresado_en": _dt(10, 0, 0).isoformat()},
        {"id": 2, "ingresado_en": _dt(12, 0, 30).isoformat()},
    ]
    chosen = ivn.select_incident_by_window(
        items, t_envio=_dt(12, 0, 30), claimed_ids={2}, margin_s=60
    )
    assert chosen is None


# ── CSV writer (tasks 4.1-4.3) ──────────────────────────────────────────────


def _write_fixture_csv(path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["Casos de incidentes registrados:", "", "", "", "", "", ""])
        writer.writerow(
            [
                "ID",
                "Descripcion",
                "Canal de Origen",
                "Sector Asignado",
                "Sectores Adicionales",
                "Tiempo de Registro Manual (segundos)",
                "TIempo de Registro Automatico (Segundos)",
            ]
        )
        writer.writerow(["R001", "No puede ingresar", "Correo", "Sistemas", "", "75", ""])
        writer.writerow(["R002", "No puede abrir", "Telefono", "Sistemas", "", "110", ""])


def _ok_result(case_id: str = "R001") -> ivn.CaseResult:
    return ivn.CaseResult(
        case_id=case_id,
        canal="correo",
        incidente_id=11,
        numero_incidente="INC-000011",
        sector="Sistemas",
        revision=False,
        t_envio=_dt(12, 0, 0).isoformat(),
        ingresado_en=_dt(12, 0, 5).isoformat(),
        persistido_en=_dt(12, 0, 7).isoformat(),
        latencia_e2e_ms=2000,
        t_pipeline_s=2.0,
        t_espera_s=5.0,
        t_e2e_s=7.0,
        origen_message_id="corpus-R001@corpus.local",
        confirmacion_recibida=True,
        t_confirmacion=_dt(12, 0, 30).isoformat(),
        t_confirmacion_s=30.0,
        anomalo=False,
        error=None,
    )


def _anomalo_result(case_id: str = "R001") -> ivn.CaseResult:
    """Replay-shaped result: negative e2e, flagged anomalous, error None."""
    return replace(
        _ok_result(case_id),
        t_pipeline_s=-1005.0,
        t_espera_s=5.0,
        t_e2e_s=-1000.0,
        anomalo=True,
    )


def _error_with_metrics_result(case_id: str = "R001") -> ivn.CaseResult:
    """Error case that nonetheless carries numeric metric fields."""
    return replace(_ok_result(case_id), error="timeout_correlacion")


def _read_csv_rows(path) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def _csv_metric_indexes(header: list[str]) -> dict[str, int]:
    return {
        "auto": header.index(ivn.HEADER_AUTO_TIME),
        "latencia": header.index(ivn.LATENCIA_COL),
        "pipeline": header.index(ivn.PIPELINE_COL),
        "espera": header.index(ivn.ESPERA_COL),
    }


_CSV_SENTINELS = {"auto": "4", "latencia": "4000", "pipeline": "99", "espera": "88"}


def _seed_csv_metric_sentinels(path) -> dict[str, int]:
    """Write valid metrics first, then stamp distinct sentinels in every cell."""
    ivn.write_csv_results(path, {"R001": _ok_result()})
    rows = _read_csv_rows(path)
    idx = _csv_metric_indexes(rows[1])
    for key, sentinel in _CSV_SENTINELS.items():
        rows[2][idx[key]] = sentinel
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(rows)
    return idx


def test_write_csv_fills_auto_latency_and_decomposition_columns(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    ivn.write_csv_results(path, {"R001": _ok_result()})
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header.count(ivn.PIPELINE_COL) == 1
    assert header.count(ivn.ESPERA_COL) == 1
    assert header.count(ivn.LATENCIA_COL) == 1
    auto = header.index(ivn.HEADER_AUTO_TIME)
    lat = header.index(ivn.LATENCIA_COL)
    pipe = header.index(ivn.PIPELINE_COL)
    wait = header.index(ivn.ESPERA_COL)
    assert rows[2][auto] == "7"
    assert rows[2][lat] == "2000"
    assert rows[2][pipe] == "2"
    assert rows[2][wait] == "5"
    # Originals preserved.
    assert rows[2][0] == "R001"
    assert rows[2][5] == "75"


def test_write_csv_error_leaves_cells_and_preserves_prior_value(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    failed = ivn.CaseResult(
        case_id="R001",
        canal="correo",
        incidente_id=None,
        numero_incidente=None,
        sector=None,
        revision=None,
        t_envio=None,
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
        error="timeout",
    )
    ivn.write_csv_results(path, {"R001": failed})
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert rows[2][header.index(ivn.HEADER_AUTO_TIME)] == ""
    # A prior numeric value is never overwritten with blank.
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    rows[2][header.index(ivn.HEADER_AUTO_TIME)] = "4"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(rows)
    ivn.write_csv_results(path, {"R001": failed})
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[2][header.index(ivn.HEADER_AUTO_TIME)] == "4"


def test_write_csv_is_idempotent(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    results = {"R001": _ok_result()}
    ivn.write_csv_results(path, results)
    ivn.write_csv_results(path, results)
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header.count(ivn.PIPELINE_COL) == 1
    assert header.count(ivn.ESPERA_COL) == 1
    assert len({len(r) for r in rows}) == 1


def test_write_csv_anomalous_result_preserves_prior_values(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    idx = _seed_csv_metric_sentinels(path)
    ivn.write_csv_results(path, {"R001": _anomalo_result()})
    row = _read_csv_rows(path)[2]
    for key, sentinel in _CSV_SENTINELS.items():
        assert row[idx[key]] == sentinel
    # The negative value of the anomalous replay never lands in the corpus.
    assert float(row[idx["auto"]]) > 0


def test_write_csv_error_result_preserves_prior_values(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    idx = _seed_csv_metric_sentinels(path)
    ivn.write_csv_results(path, {"R001": _error_with_metrics_result()})
    row = _read_csv_rows(path)[2]
    for key, sentinel in _CSV_SENTINELS.items():
        assert row[idx[key]] == sentinel


def test_write_csv_valid_result_overwrites_prior_values(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    idx = _seed_csv_metric_sentinels(path)
    ivn.write_csv_results(path, {"R001": _ok_result()})
    row = _read_csv_rows(path)[2]
    assert row[idx["auto"]] == "7"
    assert row[idx["latencia"]] == "2000"
    assert row[idx["pipeline"]] == "2"
    assert row[idx["espera"]] == "5"


def test_write_csv_anomalous_result_leaves_blank_cell_blank(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    ivn.write_csv_results(path, {"R001": _ok_result()})
    rows = _read_csv_rows(path)
    idx = _csv_metric_indexes(rows[1])
    for key in idx:
        rows[2][idx[key]] = ""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(rows)
    ivn.write_csv_results(path, {"R001": _anomalo_result()})
    row = _read_csv_rows(path)[2]
    for key in idx:
        assert row[idx[key]] == ""


# ── XLSX writer (tasks 4.1-4.3) ─────────────────────────────────────────────


def test_write_xlsx_fills_columns_and_is_idempotent(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Casos de incidentes registrados:"])
    ws.append(
        [
            "ID",
            "Descripcion",
            "Canal de Origen",
            "Sector Asignado",
            "Sectores Adicionales",
            "Tiempo de Registro Manual (segundos)",
            "TIempo de Registro Automatico (Segundos)",
        ]
    )
    ws.append(["R001", "Text", "Correo", "Sistemas", "", 75, None])
    wb.save(path)

    results = {"R001": _ok_result()}
    ivn.write_xlsx_results(path, results)
    ivn.write_xlsx_results(path, results)

    wb2 = openpyxl.load_workbook(path)
    ws2 = wb2[wb2.sheetnames[0]]
    header = [ws2.cell(row=2, column=c).value for c in range(1, ws2.max_column + 1)]
    assert header.count(ivn.PIPELINE_COL) == 1
    assert header.count(ivn.ESPERA_COL) == 1
    assert header.count(ivn.LATENCIA_COL) == 1
    auto = header.index(ivn.HEADER_AUTO_TIME) + 1
    lat = header.index(ivn.LATENCIA_COL) + 1
    pipe = header.index(ivn.PIPELINE_COL) + 1
    wait = header.index(ivn.ESPERA_COL) + 1
    assert ws2.cell(row=3, column=auto).value == pytest.approx(7.0)
    assert ws2.cell(row=3, column=lat).value == 2000
    assert ws2.cell(row=3, column=pipe).value == pytest.approx(2.0)
    assert ws2.cell(row=3, column=wait).value == pytest.approx(5.0)
    assert ws2.cell(row=3, column=1).value == "R001"


def _write_fixture_xlsx(path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Casos de incidentes registrados:"])
    ws.append(
        [
            "ID",
            "Descripcion",
            "Canal de Origen",
            "Sector Asignado",
            "Sectores Adicionales",
            "Tiempo de Registro Manual (segundos)",
            "TIempo de Registro Automatico (Segundos)",
        ]
    )
    ws.append(["R001", "Text", "Correo", "Sistemas", "", 75, None])
    wb.save(path)


_XLSX_SENTINELS = {"auto": 4, "latencia": 4000, "pipeline": 99, "espera": 88}


def _xlsx_metric_columns(path) -> dict[str, int]:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    header = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    return {
        "auto": header.index(ivn.HEADER_AUTO_TIME) + 1,
        "latencia": header.index(ivn.LATENCIA_COL) + 1,
        "pipeline": header.index(ivn.PIPELINE_COL) + 1,
        "espera": header.index(ivn.ESPERA_COL) + 1,
    }


def _seed_xlsx_metric_sentinels(path) -> dict[str, int]:
    openpyxl = pytest.importorskip("openpyxl")
    ivn.write_xlsx_results(path, {"R001": _ok_result()})
    cols = _xlsx_metric_columns(path)
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    for key, sentinel in _XLSX_SENTINELS.items():
        ws.cell(row=3, column=cols[key], value=sentinel)
    wb.save(path)
    return cols


def test_write_xlsx_anomalous_result_preserves_prior_values(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    _write_fixture_xlsx(path)
    cols = _seed_xlsx_metric_sentinels(path)
    ivn.write_xlsx_results(path, {"R001": _anomalo_result()})
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    for key, sentinel in _XLSX_SENTINELS.items():
        assert ws.cell(row=3, column=cols[key]).value == sentinel


def test_write_xlsx_error_result_preserves_prior_values(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    _write_fixture_xlsx(path)
    cols = _seed_xlsx_metric_sentinels(path)
    ivn.write_xlsx_results(path, {"R001": _error_with_metrics_result()})
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    for key, sentinel in _XLSX_SENTINELS.items():
        assert ws.cell(row=3, column=cols[key]).value == sentinel


def test_write_xlsx_valid_result_overwrites_prior_values(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    _write_fixture_xlsx(path)
    cols = _seed_xlsx_metric_sentinels(path)
    ivn.write_xlsx_results(path, {"R001": _ok_result()})
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    assert ws.cell(row=3, column=cols["auto"]).value == pytest.approx(7.0)
    assert ws.cell(row=3, column=cols["latencia"]).value == 2000
    assert ws.cell(row=3, column=cols["pipeline"]).value == pytest.approx(2.0)
    assert ws.cell(row=3, column=cols["espera"]).value == pytest.approx(5.0)


# ── Sidecar (tasks 4.4-4.5) ─────────────────────────────────────────────────


def test_sidecar_json_has_no_description_and_has_trace_fields(tmp_path):
    path = tmp_path / "resultados.json"
    ivn.write_sidecar_json(path, [_ok_result()])
    raw = path.read_text(encoding="utf-8")
    assert "descripcion" not in raw.lower()
    data = json.loads(raw)
    assert data[0]["case_id"] == "R001"
    assert data[0]["confirmacion_recibida"] is True
    assert data[0]["t_confirmacion_s"] == pytest.approx(30.0)
    assert data[0]["t_e2e_s"] == pytest.approx(7.0)


# ── Sidecar merge across runs (keyed by case_id) ────────────────────────────


def _seed_sidecar(path, results: list[ivn.CaseResult]) -> None:
    path.write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_write_sidecar_missing_file_writes_current_results(tmp_path):
    path = tmp_path / "missing.json"
    ivn.write_sidecar_json(path, [_ok_result("R001")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001"]
    assert data[0]["t_e2e_s"] == pytest.approx(7.0)


def test_write_sidecar_corrupt_file_falls_back_to_current_results(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json", encoding="utf-8")
    ivn.write_sidecar_json(path, [_ok_result("R002")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R002"]


def test_write_sidecar_preserves_valid_entry_when_replay_is_anomalous(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    ivn.write_sidecar_json(path, [_anomalo_result("R001")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001"]
    assert data[0]["t_e2e_s"] == pytest.approx(7.0)
    assert data[0]["anomalo"] is False


def test_write_sidecar_preserves_valid_entry_when_replay_has_error(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    ivn.write_sidecar_json(path, [_error_with_metrics_result("R001")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["error"] is None
    assert data[0]["t_e2e_s"] == pytest.approx(7.0)


def test_write_sidecar_replaces_entry_on_valid_remeasure(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    remeasured = replace(_ok_result("R001"), t_pipeline_s=4.0, t_e2e_s=9.0)
    ivn.write_sidecar_json(path, [remeasured])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001"]
    assert data[0]["t_e2e_s"] == pytest.approx(9.0)
    assert data[0]["t_pipeline_s"] == pytest.approx(4.0)


def test_write_sidecar_appends_new_case_and_keeps_existing_in_order(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    ivn.write_sidecar_json(path, [_ok_result("R002")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001", "R002"]
    assert data[0]["t_e2e_s"] == pytest.approx(7.0)


def test_write_sidecar_updates_existing_in_place_and_appends_new(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001"), _ok_result("R002"), _ok_result("R003")])
    remeasured = replace(_ok_result("R002"), t_e2e_s=8.5)
    ivn.write_sidecar_json(path, [remeasured, _ok_result("R004")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001", "R002", "R003", "R004"]
    assert data[1]["t_e2e_s"] == pytest.approx(8.5)


def test_write_sidecar_stores_new_invalid_case_regardless(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    ivn.write_sidecar_json(path, [_anomalo_result("R002")])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [d["case_id"] for d in data] == ["R001", "R002"]
    assert data[1]["anomalo"] is True


def test_write_sidecar_merge_never_adds_description(tmp_path):
    path = tmp_path / "sidecar.json"
    _seed_sidecar(path, [_ok_result("R001")])
    ivn.write_sidecar_json(path, [_anomalo_result("R001"), _ok_result("R002")])
    raw = path.read_text(encoding="utf-8")
    assert "descripcion" not in raw.lower()


# ── Evaluation JSON merge (tasks 4.6-4.8) ───────────────────────────────────


def _write_fixture_json(path) -> None:
    doc = {
        "schema_version": 1,
        "metadata": {"descripcion": "synthetic", "total_casos": 3},
        "casos": [
            {
                "id": "R001",
                "descripcion": "d1",
                "canal_origen": "correo electrónico",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 50,
                "tiempo_automatizado_s": None,
            },
            {
                "id": "R002",
                "descripcion": "d2",
                "canal_origen": "formulario web",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 60,
                "tiempo_automatizado_s": 9.0,
            },
            {
                "id": "R003",
                "descripcion": "d3",
                "canal_origen": "llamada telefónica",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 70,
                "tiempo_automatizado_s": None,
            },
        ],
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def test_merge_json_writes_numeric_and_counts_pending(tmp_path):
    path = tmp_path / "corpus.json"
    _write_fixture_json(path)
    pending = ivn.merge_evaluation_json(path, {"R001": 7.0})
    doc = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R001"]["tiempo_automatizado_s"] == pytest.approx(7.0)
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(9.0)
    assert by_id["R003"]["tiempo_automatizado_s"] is None
    assert pending == 1  # R003 (telefono) still null


def test_merge_json_does_not_overwrite_non_null_with_null(tmp_path):
    path = tmp_path / "corpus.json"
    _write_fixture_json(path)
    ivn.merge_evaluation_json(path, {"R002": None})
    doc = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(9.0)


def test_merge_json_is_idempotent(tmp_path):
    path = tmp_path / "corpus.json"
    _write_fixture_json(path)
    first = ivn.merge_evaluation_json(path, {"R001": 7.0})
    second = ivn.merge_evaluation_json(path, {"R001": 7.0})
    assert first == second == 1


# ── Web path (tasks 2.1-2.3) ────────────────────────────────────────────────


def test_ingest_web_posts_to_webhook_and_reads_detail():
    session = FakeSession(
        [
            FakeResponse(200, _webhook_body(11)),
            FakeResponse(200, _detail_body()),
        ]
    )
    result = ivn.ingest_web_case(
        session=session,
        token="t",
        base_url="https://api.local",
        webhook_url="http://n8n.local/webhook/incidente-web",
        case_id="R001",
        descripcion="d" * 20,
        verify=True,
        timeout=10,
        t_envio=_dt(12, 0, 0),
    )
    assert result.error is None
    assert result.incidente_id == 11
    assert result.t_e2e_s == pytest.approx(7.0)
    assert result.canal == "web"
    # POST to webhook then GET the detail.
    assert session.calls[0][0] == "POST"
    assert session.calls[0][1].endswith("/incidente-web")
    assert session.calls[1][1].endswith("/api/v1/incidentes/11")


def test_ingest_web_4xx_is_not_retried():
    session = FakeSession([FakeResponse(422, {"error": {"code": "validation_error"}})])
    result = ivn.ingest_web_case(
        session=session,
        token="t",
        base_url="https://api.local",
        webhook_url="http://n8n.local/webhook/incidente-web",
        case_id="R001",
        descripcion="d" * 20,
        verify=True,
        timeout=10,
        retry_backoff=0,
    )
    assert result.error is not None
    assert result.error.startswith("http422")
    assert len(session.calls) == 1


def test_ingest_web_5xx_is_retried():
    session = FakeSession(
        [
            FakeResponse(503, {}),
            FakeResponse(200, _webhook_body(11)),
            FakeResponse(200, _detail_body()),
        ]
    )
    result = ivn.ingest_web_case(
        session=session,
        token="t",
        base_url="https://api.local",
        webhook_url="http://n8n.local/webhook/incidente-web",
        case_id="R001",
        descripcion="d" * 20,
        verify=True,
        timeout=10,
        retry_backoff=0,
    )
    assert result.error is None
    assert result.incidente_id == 11
    assert len(session.calls) == 3


def test_ingest_web_timeout_reports_short_label():
    import requests

    session = FakeSession(
        [requests.Timeout(), requests.Timeout(), requests.Timeout()]
    )
    result = ivn.ingest_web_case(
        session=session,
        token="t",
        base_url="https://api.local",
        webhook_url="http://n8n.local/webhook/incidente-web",
        case_id="R001",
        descripcion="d" * 20,
        verify=True,
        timeout=10,
        retry_backoff=0,
    )
    assert result.error == "Timeout"


def test_ingest_web_missing_incidente_id_is_error():
    session = FakeSession([FakeResponse(200, _webhook_body(None))])
    result = ivn.ingest_web_case(
        session=session,
        token="t",
        base_url="https://api.local",
        webhook_url="http://n8n.local/webhook/incidente-web",
        case_id="R001",
        descripcion="d" * 20,
        verify=True,
        timeout=10,
        retry_backoff=0,
    )
    assert result.error == "sin_incidente_id"


# ── Email path (tasks 3.1-3.4) ──────────────────────────────────────────────


def test_build_email_message_sets_deterministic_message_id():
    msg = ivn.build_email_message(
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
    )
    assert msg["Message-ID"] == "<corpus-R001@corpus.local>"
    assert msg["To"] == "ingesta@corpus.local"


def test_ingest_email_correlates_exact_and_derives_metric():
    session = FakeSession(
        [
            FakeResponse(
                200,
                [
                    {"id": 11, "ingresado_en": _dt(12, 0, 50).isoformat()},
                ],
            ),
            FakeResponse(200, _detail_body(ingresado_en=_dt(12, 0, 50).isoformat(), persistido_en=_dt(12, 0, 52).isoformat(), latencia_e2e_ms=2000)),
        ]
    )
    sent: list = []

    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=sent.append,
        t_envio=_dt(12, 0, 0),
    )
    assert result.error is None
    assert result.incidente_id == 11
    assert result.t_espera_s == pytest.approx(50.0)
    assert result.t_e2e_s == pytest.approx(52.0)
    assert len(sent) == 1
    assert sent[0]["Message-ID"] == "<corpus-R001@corpus.local>"
    assert "origen_message_id=corpus-R001%40corpus.local" in session.calls[0][1] or (
        "origen_message_id=" in session.calls[0][1]
    )


def test_ingest_email_timeout_when_no_correlated_incident():
    session = FakeSession([FakeResponse(200, []), FakeResponse(200, [])])
    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=lambda m: None,
        t_envio=_dt(12, 0, 0),
    )
    assert result.error == "timeout_correlacion"


def test_ingest_email_replay_same_message_id_is_deterministic():
    first = ivn.build_message_id("R001", "corpus.local")
    second = ivn.build_message_id("R001", "corpus.local")
    assert first == second


def test_ingest_email_confirmation_observed_separately():
    session = FakeSession(
        [
            FakeResponse(200, [{"id": 11, "ingresado_en": _dt(12, 0, 5).isoformat()}]),
            FakeResponse(200, _detail_body()),
        ]
    )
    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=lambda m: None,
        t_envio=_dt(12, 0, 0),
        confirmation_observer=lambda numero: _dt(12, 0, 30),
    )
    assert result.confirmacion_recibida is True
    assert result.t_confirmacion_s == pytest.approx(30.0)
    # Primary measurement preserved.
    assert result.t_e2e_s == pytest.approx(7.0)


def test_ingest_email_confirmation_absent_keeps_primary():
    session = FakeSession(
        [
            FakeResponse(200, [{"id": 11, "ingresado_en": _dt(12, 0, 5).isoformat()}]),
            FakeResponse(200, _detail_body()),
        ]
    )
    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=lambda m: None,
        t_envio=_dt(12, 0, 0),
        confirmation_observer=lambda numero: None,
    )
    assert result.confirmacion_recibida is False
    assert result.t_confirmacion_s is None
    assert result.t_e2e_s == pytest.approx(7.0)


def test_ingest_email_confirmation_observer_raises_is_non_blocking():
    """D14: a raising confirmation observer must NOT abort the primary run."""
    session = FakeSession(
        [
            FakeResponse(200, [{"id": 11, "ingresado_en": _dt(12, 0, 5).isoformat()}]),
            FakeResponse(200, _detail_body()),
        ]
    )

    def _boom(numero: str) -> datetime:
        raise RuntimeError("boom")

    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=lambda m: None,
        t_envio=_dt(12, 0, 0),
        confirmation_observer=_boom,
    )
    # Absent secondary check, never an error.
    assert result.error is None
    assert result.confirmacion_recibida is False
    assert result.t_confirmacion is None
    assert result.t_confirmacion_s is None
    # Primary measurement derived normally from the API instants.
    assert result.t_pipeline_s == pytest.approx(2.0)
    assert result.t_espera_s == pytest.approx(5.0)
    assert result.t_e2e_s == pytest.approx(7.0)


def test_confirmation_observer_exception_does_not_leak_message(capsys):
    """The swallowed exception body (which may echo a secret) never hits output."""
    session = FakeSession(
        [
            FakeResponse(200, [{"id": 11, "ingresado_en": _dt(12, 0, 5).isoformat()}]),
            FakeResponse(200, _detail_body()),
        ]
    )

    def _boom(numero: str) -> datetime:
        raise RuntimeError("IMAP login failed for TOP_SECRET_PW")

    result = ivn.ingest_email_case(
        session=session,
        token="t",
        base_url="https://api.local",
        case_id="R001",
        descripcion="d" * 20,
        domain="corpus.local",
        sender="ingesta@corpus.local",
        recipient="ingesta@corpus.local",
        verify=True,
        timeout=10,
        poll_timeout=0,
        poll_interval=0,
        send_func=lambda m: None,
        t_envio=_dt(12, 0, 0),
        confirmation_observer=_boom,
    )
    assert result.confirmacion_recibida is False
    assert result.error is None
    captured = capsys.readouterr()
    assert "TOP_SECRET_PW" not in captured.out
    assert "TOP_SECRET_PW" not in captured.err


def _write_two_email_cases_json(path) -> None:
    doc = {
        "schema_version": 1,
        "metadata": {"descripcion": "synthetic", "total_casos": 2},
        "casos": [
            {
                "id": "R001",
                "descripcion": "d1",
                "canal_origen": "correo electrónico",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 50,
                "tiempo_automatizado_s": None,
            },
            {
                "id": "R002",
                "descripcion": "d2",
                "canal_origen": "correo electrónico",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 60,
                "tiempo_automatizado_s": None,
            },
        ],
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def test_run_per_case_exception_is_reported_and_does_not_abort(tmp_path, monkeypatch):
    """One unexpected per-case exception is reported as a case error, not fatal."""
    json_path = tmp_path / "corpus.json"
    _write_two_email_cases_json(json_path)
    _set_operator_creds(monkeypatch)
    _clear_confirmation_env(monkeypatch)

    calls: list[str] = []

    def flaky_ingest_email_case(**kwargs):
        calls.append(kwargs["case_id"])
        if len(calls) == 1:
            raise RuntimeError("boom")
        return _ok_result(case_id=kwargs["case_id"])

    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(ivn, "ingest_email_case", flaky_ingest_email_case)
    monkeypatch.setattr(ivn, "write_csv_results", lambda *a, **k: None)
    monkeypatch.setattr(ivn, "write_xlsx_results", lambda *a, **k: None)

    sidecar = tmp_path / "sidecar.json"
    code = ivn.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--sidecar",
            str(sidecar),
            "--csv",
            str(tmp_path / "c.csv"),
            "--xlsx",
            str(tmp_path / "c.xlsx"),
            "--only-channel",
            "correo",
        ]
    )
    # The second case still ran despite the first one raising.
    assert calls == ["R001", "R002"]
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data[0]["case_id"] == "R001"
    assert data[0]["error"] == "RuntimeError"
    assert data[0]["t_e2e_s"] is None
    assert data[1]["case_id"] == "R002"
    assert data[1]["error"] is None
    assert code == 1  # one failed case reported, run completed normally


# ── Dry-run and privacy (task 6.1) ──────────────────────────────────────────


def test_dry_run_reports_counts_without_writing(tmp_path, capsys):
    path = tmp_path / "corpus.json"
    _write_fixture_json(path)
    exit_code = ivn.run(
        ["--dry-run", "--source", "json", "--json", str(path), "--sidecar", str(tmp_path / "sidecar.json")]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "correo" in out
    assert "web" in out
    assert "telefono" in out
    # Privacy: the synthetic descriptions never leak to stdout.
    assert "d1" not in out
    assert not (tmp_path / "sidecar.json").exists()


def test_dry_run_does_not_touch_data_files(tmp_path):
    json_path = tmp_path / "corpus.json"
    csv_path = tmp_path / "corpus.csv"
    _write_fixture_json(json_path)
    _write_fixture_csv(csv_path)
    before = csv_path.read_bytes()
    exit_code = ivn.run(
        [
            "--dry-run",
            "--source",
            "csv",
            "--csv",
            str(csv_path),
            "--json",
            str(json_path),
            "--sidecar",
            str(tmp_path / "corpus_resultados_n8n.json"),
        ]
    )
    assert exit_code == 0
    assert csv_path.read_bytes() == before
    assert not (tmp_path / "corpus_resultados_n8n.json").exists()


# ── Confirmation IMAP observer + separation guard (D14 wiring) ───────────────


def test_select_confirmation_instant_picks_matching_message():
    messages = [
        {"subject": "Otro asunto", "received": _dt(12, 0, 10).isoformat()},
        {
            "subject": ivn.confirmation_subject("INC-000011"),
            "received": _dt(12, 0, 30).isoformat(),
        },
        {
            "subject": ivn.confirmation_subject("INC-000011"),
            "received": _dt(12, 0, 31).isoformat(),
        },
    ]
    instant = ivn.select_confirmation_instant(messages, "INC-000011")
    assert instant == _dt(12, 0, 30)


def test_select_confirmation_instant_absent_returns_none():
    messages = [
        {"subject": "Otro asunto", "received": _dt(12, 0, 10).isoformat()},
        {
            "subject": ivn.confirmation_subject("INC-000099"),
            "received": _dt(12, 0, 30).isoformat(),
        },
    ]
    assert ivn.select_confirmation_instant(messages, "INC-000011") is None


def test_select_confirmation_instant_normalizes_received_to_utc():
    messages = [
        {
            "subject": ivn.confirmation_subject("INC-000011"),
            "received": "2026-09-29T09:00:30-03:00",
        }
    ]
    instant = ivn.select_confirmation_instant(messages, "INC-000011")
    assert instant == _dt(12, 0, 30)
    assert instant.tzinfo is not None


def test_select_confirmation_instant_ignores_non_datetime_received():
    messages = [
        {
            "subject": ivn.confirmation_subject("INC-000011"),
            "received": None,
        }
    ]
    assert ivn.select_confirmation_instant(messages, "INC-000011") is None


def test_build_confirmation_observer_disabled_without_host_or_user():
    assert ivn.build_confirmation_observer(env={}) is None
    assert (
        ivn.build_confirmation_observer(
            env={"INGEST_CONFIRMATION_IMAP_HOST": "imap.local"}
        )
        is None
    )
    assert (
        ivn.build_confirmation_observer(
            env={"INGEST_CONFIRMATION_IMAP_USER": "confirm@local"}
        )
        is None
    )


def test_build_confirmation_observer_enabled_calls_injected_fetch():
    seen: list[dict] = []

    def fake_fetch(**kwargs):
        seen.append(kwargs)
        return [
            {
                "subject": ivn.confirmation_subject("INC-000011"),
                "received": "2026-09-29T09:00:30-03:00",
            }
        ]

    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.conf.local",
        "INGEST_CONFIRMATION_IMAP_USER": "confirm@local",
        "INGEST_CONFIRMATION_IMAP_PASSWORD": "pw",
        "INGEST_CONFIRMATION_IMAP_FOLDER": "Confirmaciones",
    }
    observer = ivn.build_confirmation_observer(env=env, fetch_messages=fake_fetch)
    assert observer is not None
    assert observer("INC-000011") == _dt(12, 0, 30)
    assert seen[0]["host"] == "imap.conf.local"
    assert seen[0]["user"] == "confirm@local"
    assert seen[0]["folder"] == "Confirmaciones"
    # Default port when the companion env file omits it.
    assert seen[0]["port"] == 993


def test_build_confirmation_observer_honors_custom_port_and_default_folder():
    seen: list[dict] = []

    def fake_fetch(**kwargs):
        seen.append(kwargs)
        return []

    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.conf.local",
        "INGEST_CONFIRMATION_IMAP_USER": "confirm@local",
        "INGEST_CONFIRMATION_IMAP_PORT": "1430",
    }
    observer = ivn.build_confirmation_observer(env=env, fetch_messages=fake_fetch)
    assert observer is not None
    assert observer("INC-000011") is None
    assert seen[0]["port"] == 1430
    assert seen[0]["folder"] == "INBOX"


def test_confirmation_observer_has_no_description_or_secret_leak(capsys):
    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.conf.local",
        "INGEST_CONFIRMATION_IMAP_USER": "confirm@local",
        "INGEST_CONFIRMATION_IMAP_PASSWORD": "TOP_SECRET_PW",
    }

    def fake_fetch(**kwargs):
        return []

    observer = ivn.build_confirmation_observer(env=env, fetch_messages=fake_fetch)
    assert observer is not None
    assert observer("INC-000011") is None
    captured = capsys.readouterr()
    assert "TOP_SECRET_PW" not in captured.out
    assert "TOP_SECRET_PW" not in captured.err


def test_confirmation_separation_error_none_when_unconfigured():
    assert ivn.confirmation_separation_error(env={}) is None


def test_confirmation_separation_error_detects_same_folder_same_account():
    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.local",
        "INGEST_CONFIRMATION_IMAP_USER": "ingesta@local",
        "INGEST_CONFIRMATION_IMAP_FOLDER": "INBOX",
        "INGEST_INGEST_IMAP_HOST": "imap.local",
        "INGEST_INGEST_IMAP_USER": "ingesta@local",
        "INGEST_INGEST_IMAP_FOLDER": "INBOX",
    }
    error = ivn.confirmation_separation_error(env=env)
    assert error is not None
    assert "separado" in error.lower()


def test_confirmation_separation_error_accepts_different_folder():
    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.local",
        "INGEST_CONFIRMATION_IMAP_USER": "ingesta@local",
        "INGEST_CONFIRMATION_IMAP_FOLDER": "Confirmaciones",
        "INGEST_INGEST_IMAP_HOST": "imap.local",
        "INGEST_INGEST_IMAP_USER": "ingesta@local",
        "INGEST_INGEST_IMAP_FOLDER": "INBOX",
    }
    assert ivn.confirmation_separation_error(env=env) is None


def _set_operator_creds(monkeypatch) -> None:
    monkeypatch.setenv("INGEST_OPERATOR_USERNAME", "operador")
    monkeypatch.setenv("INGEST_OPERATOR_PASSWORD", "pw")


def _clear_confirmation_env(monkeypatch) -> None:
    for key in (
        "INGEST_CONFIRMATION_IMAP_HOST",
        "INGEST_CONFIRMATION_IMAP_PORT",
        "INGEST_CONFIRMATION_IMAP_USER",
        "INGEST_CONFIRMATION_IMAP_PASSWORD",
        "INGEST_CONFIRMATION_IMAP_FOLDER",
        "INGEST_INGEST_IMAP_HOST",
        "INGEST_INGEST_IMAP_USER",
        "INGEST_INGEST_IMAP_FOLDER",
    ):
        monkeypatch.delenv(key, raising=False)


def test_run_missing_credentials_aborts_without_network(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_fixture_json(json_path)
    monkeypatch.delenv("INGEST_OPERATOR_USERNAME", raising=False)
    monkeypatch.delenv("INGEST_OPERATOR_PASSWORD", raising=False)

    def _boom(*args, **kwargs):
        raise AssertionError("login must not run without credentials")

    monkeypatch.setattr(ivn, "login", _boom)
    code = ivn.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "ERROR" in err
    # The missing env values resolve to None; the guard must never echo a
    # credential value (there is none, but a naive print would leak it).
    assert "None" not in err


def test_run_aborts_when_confirmation_path_equals_ingestion(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "corpus.json"
    _write_fixture_json(json_path)
    _set_operator_creds(monkeypatch)
    for key, value in {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.local",
        "INGEST_CONFIRMATION_IMAP_USER": "ingesta@local",
        "INGEST_CONFIRMATION_IMAP_PASSWORD": "SUPER_SECRET_PW",
        "INGEST_CONFIRMATION_IMAP_FOLDER": "INBOX",
        "INGEST_INGEST_IMAP_HOST": "imap.local",
        "INGEST_INGEST_IMAP_USER": "ingesta@local",
        "INGEST_INGEST_IMAP_FOLDER": "INBOX",
    }.items():
        monkeypatch.setenv(key, value)

    def _boom(*args, **kwargs):  # login must never run when the guard aborts
        raise AssertionError("login should not be reached")

    monkeypatch.setattr(ivn, "login", _boom)
    code = ivn.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
            "--only-channel",
            "correo",
        ]
    )
    assert code != 0
    err = capsys.readouterr().err
    assert "separado" in err.lower()
    assert "SUPER_SECRET_PW" not in err


def test_run_wires_confirmation_observer_when_configured(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_fixture_json(json_path)
    _set_operator_creds(monkeypatch)
    for key, value in {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.conf.local",
        "INGEST_CONFIRMATION_IMAP_USER": "confirm@local",
        "INGEST_CONFIRMATION_IMAP_FOLDER": "Confirmaciones",
        "INGEST_INGEST_IMAP_HOST": "imap.ingest.local",
        "INGEST_INGEST_IMAP_USER": "ingest@local",
        "INGEST_INGEST_IMAP_FOLDER": "INBOX",
    }.items():
        monkeypatch.setenv(key, value)

    captured: dict = {}

    def fake_ingest_email_case(**kwargs):
        captured["observer"] = kwargs.get("confirmation_observer")
        captured["timeout"] = kwargs.get("confirmation_timeout")
        captured["interval"] = kwargs.get("confirmation_interval")
        return _ok_result()

    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(ivn, "ingest_email_case", fake_ingest_email_case)
    monkeypatch.setattr(ivn, "write_csv_results", lambda *a, **k: None)
    monkeypatch.setattr(ivn, "write_xlsx_results", lambda *a, **k: None)
    code = ivn.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
            "--csv",
            str(tmp_path / "c.csv"),
            "--xlsx",
            str(tmp_path / "c.xlsx"),
            "--only-channel",
            "correo",
        ]
    )
    assert code == 0
    assert callable(captured["observer"])
    assert captured["timeout"] == ivn.CONFIRMATION_TIMEOUT_S
    assert captured["interval"] == ivn.CONFIRMATION_INTERVAL_S


def test_run_leaves_observer_none_when_unconfigured(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_fixture_json(json_path)
    _set_operator_creds(monkeypatch)
    _clear_confirmation_env(monkeypatch)

    captured: dict = {}

    def fake_ingest_email_case(**kwargs):
        captured["observer"] = kwargs.get("confirmation_observer")
        return _ok_result()

    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(ivn, "ingest_email_case", fake_ingest_email_case)
    monkeypatch.setattr(ivn, "write_csv_results", lambda *a, **k: None)
    monkeypatch.setattr(ivn, "write_xlsx_results", lambda *a, **k: None)
    code = ivn.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
            "--csv",
            str(tmp_path / "c.csv"),
            "--xlsx",
            str(tmp_path / "c.xlsx"),
            "--only-channel",
            "correo",
        ]
    )
    assert code == 0
    assert captured["observer"] is None


# ── Bounded confirmation IMAP fetch (timeout + SUBJECT criterion) ────────────


class FakeIMAPClient:
    """Context-manager IMAP stand-in; records ctor kwargs and search args."""

    def __init__(
        self,
        *,
        host: str = "",
        port: int = 993,
        ssl_context=None,
        timeout: float | None = None,
        search_status: str = "OK",
        uids: bytes = b"",
        messages: dict | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.timeout = timeout
        self.search_status = search_status
        self.uids = uids
        self.messages = messages or {}
        self.search_calls: list[tuple] = []
        self.logged_in: tuple | None = None
        self.selected: tuple | None = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def login(self, user, password):
        self.logged_in = (user, password)
        return ("OK", [b"LOGIN completed"])

    def select(self, folder, readonly=False):
        self.selected = (folder, readonly)
        return ("OK", [b"1"])

    def search(self, *args):
        self.search_calls.append(args)
        return (self.search_status, [self.uids])

    def fetch(self, number, spec):
        return ("OK", [self.messages[number]])


def _capturing_factory(client: FakeIMAPClient) -> tuple:
    """Return (factory, captured) recording the IMAP constructor kwargs."""
    captured: dict = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return client

    return factory, captured


def _raw_message(subject: str, internaldate: str) -> tuple:
    prefix = f'1 (INTERNALDATE "{internaldate}" BODY[HEADER.FIELDS (SUBJECT)] {{0}}'.encode()
    header = f"Subject: {subject}\r\n\r\n".encode()
    return (prefix, header)


def test_fetch_confirmation_messages_uses_timeout_and_bounded_search():
    client = FakeIMAPClient(
        uids=b"1",
        messages={
            b"1": _raw_message(
                ivn.confirmation_subject("INC-000011"),
                "29-Sep-2026 12:00:30 +0000",
            )
        },
    )
    factory, captured = _capturing_factory(client)
    found = ivn._fetch_confirmation_messages(
        host="imap.conf.local",
        port=993,
        user="confirm@local",
        password="pw",
        folder="Confirmaciones",
        client_factory=factory,
    )
    # (a) The IMAP client is built with a positive timeout.
    assert captured["timeout"] == ivn.DEFAULT_IMAP_TIMEOUT_S
    assert captured["timeout"] > 0
    assert captured["host"] == "imap.conf.local"
    assert captured["port"] == 993
    # (b) The search is bounded by SUBJECT, never a full-mailbox ALL scan.
    assert client.search_calls
    args = client.search_calls[0]
    assert "SUBJECT" in args
    assert "ALL" not in args
    assert any(ivn.CONFIRMATION_SUBJECT_FILTER in str(a) for a in args)
    # (c) The parsed messages are still returned and selectable.
    assert found[0]["subject"] == ivn.confirmation_subject("INC-000011")
    assert ivn.select_confirmation_instant(found, "INC-000011") == _dt(12, 0, 30)


def test_fetch_confirmation_messages_empty_search_returns_empty():
    client = FakeIMAPClient(uids=b"")
    factory, _ = _capturing_factory(client)
    found = ivn._fetch_confirmation_messages(
        host="imap.conf.local",
        port=993,
        user="confirm@local",
        password="pw",
        folder="Confirmaciones",
        client_factory=factory,
    )
    assert found == []
    assert ivn.select_confirmation_instant(found, "INC-000011") is None


def test_fetch_confirmation_messages_selects_only_matching_subject():
    client = FakeIMAPClient(
        uids=b"1 2",
        messages={
            b"1": _raw_message("Otro asunto", "29-Sep-2026 12:00:10 +0000"),
            b"2": _raw_message(
                ivn.confirmation_subject("INC-000011"),
                "29-Sep-2026 12:00:30 +0000",
            ),
        },
    )
    factory, _ = _capturing_factory(client)
    found = ivn._fetch_confirmation_messages(
        host="imap.conf.local",
        port=993,
        user="confirm@local",
        password="pw",
        folder="Confirmaciones",
        client_factory=factory,
    )
    assert len(found) == 2
    assert ivn.select_confirmation_instant(found, "INC-000011") == _dt(12, 0, 30)


def test_fetch_confirmation_messages_search_not_ok_returns_empty():
    client = FakeIMAPClient(
        search_status="NO",
        uids=b"1",
        messages={
            b"1": _raw_message(
                ivn.confirmation_subject("INC-000011"),
                "29-Sep-2026 12:00:30 +0000",
            )
        },
    )
    factory, _ = _capturing_factory(client)
    found = ivn._fetch_confirmation_messages(
        host="imap.conf.local",
        port=993,
        user="confirm@local",
        password="pw",
        folder="Confirmaciones",
        client_factory=factory,
    )
    assert found == []


def test_build_confirmation_observer_plumbs_client_factory():
    captured: dict = {}
    sentinel = object()

    def fake_fetch(**kwargs):
        captured.update(kwargs)
        return []

    env = {
        "INGEST_CONFIRMATION_IMAP_HOST": "imap.conf.local",
        "INGEST_CONFIRMATION_IMAP_USER": "confirm@local",
    }
    observer = ivn.build_confirmation_observer(
        env=env, fetch_messages=fake_fetch, client_factory=sentinel
    )
    assert observer is not None
    assert observer("INC-000011") is None
    assert captured["client_factory"] is sentinel


# ── Modo campana (c-166): campos nuevos de CaseResult (task 2.1) ────────────

CAMPOS_CAMPANA = ["orden", "posicion", "mitad", "brazo_primero", "id_corrida"]


def test_case_result_acepta_los_campos_de_campana_al_final_con_default_none():
    resultado = _ok_result()  # constructor existente: no pasa ningun campo de campana

    assert [getattr(resultado, campo) for campo in CAMPOS_CAMPANA] == [None] * 5
    assert [f.name for f in fields(ivn.CaseResult)][-5:] == CAMPOS_CAMPANA
    assert list(asdict(resultado))[-5:] == CAMPOS_CAMPANA


def test_case_result_guarda_los_campos_de_campana_cuando_se_los_pasa():
    resultado = replace(
        _ok_result(),
        orden="aleatorio",
        posicion=7,
        mitad=1,
        brazo_primero="automatizado",
        id_corrida="corrida-1",
    )

    assert asdict(resultado)["orden"] == "aleatorio"
    assert asdict(resultado)["posicion"] == 7
    assert asdict(resultado)["mitad"] == 1
    assert asdict(resultado)["brazo_primero"] == "automatizado"
    assert asdict(resultado)["id_corrida"] == "corrida-1"


def test_los_builders_existentes_dejan_los_campos_de_campana_en_none():
    desde_detalle = ivn._result_from_detail(
        case_id="R001",
        canal="web",
        detail=_detail_body(),
        t_envio=_dt(12, 0, 0),
        origen_message_id=None,
    )
    desde_error = ivn._error_result("R001", "web", _dt(12, 0, 0), "http500")

    for resultado in (desde_detalle, desde_error):
        assert [getattr(resultado, campo) for campo in CAMPOS_CAMPANA] == [None] * 5


# ── Modo campana (c-166): sidecars historicos (task 2.4) ────────────────────


def _entrada_historica(resultado: ivn.CaseResult) -> dict:
    """Entrada de sidecar tal como la escribia la version previa (sin claves de campana)."""
    return {k: v for k, v in asdict(resultado).items() if k not in CAMPOS_CAMPANA}


def test_sidecar_historico_sin_claves_de_campana_se_sigue_leyendo_y_mergeando(tmp_path):
    path = tmp_path / "sidecar.json"
    historicas = [_entrada_historica(_ok_result("R001")), _entrada_historica(_ok_result("R002"))]
    path.write_text(json.dumps(historicas), encoding="utf-8")
    nueva = replace(
        _ok_result("R002"),
        t_e2e_s=9.0,
        orden="inverso",
        posicion=2,
        mitad=1,
        brazo_primero="automatizado",
        id_corrida="corrida-1",
    )

    ivn.write_sidecar_json(path, [nueva, _ok_result("R003")])

    data = json.loads(path.read_text(encoding="utf-8"))
    assert [entrada["case_id"] for entrada in data] == ["R001", "R002", "R003"]
    assert data[0] == historicas[0]  # intacta: no se le agregan claves
    assert data[1]["t_e2e_s"] == 9.0
    assert (data[1]["posicion"], data[1]["mitad"], data[1]["id_corrida"]) == (2, 1, "corrida-1")
    assert [data[2][campo] for campo in CAMPOS_CAMPANA] == [None] * 5


def test_las_claves_de_campana_ausentes_de_un_sidecar_historico_equivalen_a_none():
    entrada = _entrada_historica(_ok_result())

    resultado = ivn.CaseResult(**entrada)

    assert not set(CAMPOS_CAMPANA) & set(entrada)
    assert [getattr(resultado, campo) for campo in CAMPOS_CAMPANA] == [None] * 5


# ── Modo campana (c-166): --limit antes del orden (task 2.5) ────────────────

CANAL_CORREO_JSON = "correo electrónico"
CANAL_TELEFONO_JSON = "llamada telefónica"


def _write_cases_json(path, canales) -> None:
    """Corpus sintetico con un caso por canal indicado (ids R001, R002, ...)."""
    casos = [
        {
            "id": f"R{numero:03d}",
            "descripcion": f"d{numero}",
            "canal_origen": canal,
            "sector_asignado": "Sistemas",
            "sectores_adicionales": [],
            "tiempo_manual_s": 50,
            "tiempo_automatizado_s": None,
        }
        for numero, canal in enumerate(canales, start=1)
    ]
    doc = {
        "schema_version": 1,
        "metadata": {"descripcion": "synthetic", "total_casos": len(casos)},
        "casos": casos,
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def _escribir_plan(path, ids, modo="directo", seed=None):
    pc.escribir_plan_csv(pc.generar_plan_campana(ids, modo, seed), path)
    return path


def _ingesta_falsa(monkeypatch, vistos: list[str]) -> list[str]:
    """Cliente falso: registra los case_id enviados, en orden, y cada resultado es valido.

    Devuelve la lista donde se anotan las llamadas a los writers de CSV/XLSX (que no
    escriben nada), para poder afirmar si el modo campana los invoca.
    """
    escrituras: list[str] = []

    def falsa(**kwargs):
        vistos.append(kwargs["case_id"])
        return _ok_result(case_id=kwargs["case_id"])

    _set_operator_creds(monkeypatch)
    _clear_confirmation_env(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(ivn, "ingest_email_case", falsa)
    monkeypatch.setattr(ivn, "ingest_web_case", falsa)
    monkeypatch.setattr(ivn, "write_csv_results", lambda *a, **k: escrituras.append("csv"))
    monkeypatch.setattr(ivn, "write_xlsx_results", lambda *a, **k: escrituras.append("xlsx"))
    return escrituras


def _argv_campana(tmp_path, json_path, *extra) -> list[str]:
    return [
        "--source",
        "json",
        "--json",
        str(json_path),
        "--sidecar",
        str(tmp_path / "corrida.json"),
        "--id-corrida",
        "corrida-1",
        "--sleep",
        "0",
        *extra,
    ]


def test_orden_inverso_con_limit_procesa_el_reverso_de_los_tres_primeros(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 5)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "inverso", "--limit", "3"))

    assert codigo == 0
    assert vistos == ["R003", "R002", "R001"]  # NO los tres ultimos (R005, R004, R003)


def test_orden_alternado_con_limit_ordena_solo_los_casos_seleccionados(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 6)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "alternado", "--limit", "4"))

    assert codigo == 0
    assert vistos == ["R001", "R003", "R002", "R004"]


def test_plan_con_limit_se_rechaza_con_error_accionable_y_no_envia_nada(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 4)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003", "R004"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan), "--limit", "2"))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--limit" in err and "--plan" in err
    assert vistos == []


# ── Modo campana (c-166): --plan (task 2.6) ─────────────────────────────────

CANAL_WEB_JSON = "formulario web"
IDS_5 = ["R001", "R002", "R003", "R004", "R005"]


def _leer_sidecar(tmp_path) -> list[dict]:
    return json.loads((tmp_path / "corrida.json").read_text(encoding="utf-8"))


def test_plan_envia_los_casos_ingestables_en_orden_de_posicion_y_omite_telefono(
    tmp_path, monkeypatch
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(
        json_path,
        [CANAL_CORREO_JSON, CANAL_TELEFONO_JSON, CANAL_WEB_JSON, CANAL_CORREO_JSON, CANAL_CORREO_JSON],
    )
    plan = _escribir_plan(tmp_path / "plan.csv", IDS_5, "inverso")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan)))

    assert codigo == 0
    assert vistos == ["R005", "R004", "R003", "R001"]  # R002 es telefono: se omite


def test_plan_registra_la_asignacion_del_plan_en_cada_entrada_del_sidecar(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 5)
    plan = _escribir_plan(tmp_path / "plan.csv", IDS_5, "aleatorio", seed=7)
    esperado = {fila.id_caso: fila for fila in pc.leer_plan_csv(plan)}
    _ingesta_falsa(monkeypatch, [])

    ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan)))

    entradas = _leer_sidecar(tmp_path)
    assert sorted(entrada["case_id"] for entrada in entradas) == IDS_5
    for entrada in entradas:
        fila = esperado[entrada["case_id"]]
        assert entrada["posicion"] == fila.posicion
        assert entrada["mitad"] == fila.mitad
        assert entrada["brazo_primero"] == fila.brazo_primero
        assert entrada["orden"] == "aleatorio"
        assert entrada["id_corrida"] == "corrida-1"


def test_plan_acepta_un_subplan_con_posiciones_globales_no_contiguas(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 5)
    completo = pc.generar_plan_campana(IDS_5, "directo")
    subplan = tmp_path / "subplan.csv"
    pc.escribir_plan_csv(pc.subplan(completo, mitad=2, brazo="manual", turno=1), subplan)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(subplan)))

    assert codigo == 0
    assert vistos == ["R003", "R005"]  # mitad 2, manual primero: posiciones 3 y 5
    assert [entrada["posicion"] for entrada in _leer_sidecar(tmp_path)] == [3, 5]


def test_plan_respeta_only_channel_sobre_los_casos_del_plan(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(
        json_path, [CANAL_CORREO_JSON, CANAL_WEB_JSON, CANAL_CORREO_JSON, CANAL_WEB_JSON]
    )
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003", "R004"], "inverso")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan), "--only-channel", "web"))

    assert vistos == ["R004", "R002"]


def test_plan_con_un_id_caso_ausente_del_corpus_aborta_antes_de_enviar(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R999"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan)))

    assert codigo == 2
    assert "R999" in capsys.readouterr().err
    assert vistos == []
    assert not (tmp_path / "corrida.json").exists()


def test_plan_inexistente_aborta_con_error_accionable(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 2)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(tmp_path / "no_existe.csv")))

    assert codigo == 2
    assert "no_existe.csv" in capsys.readouterr().err
    assert vistos == []


def test_plan_y_orden_juntos_se_rechazan_y_no_envian_nada(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(
        _argv_campana(tmp_path, json_path, "--plan", str(plan), "--orden", "inverso")
    )

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--plan" in err and "--orden" in err
    assert vistos == []


@pytest.mark.parametrize("modo", ["plan", "orden"])
def test_la_falta_de_id_corrida_se_rechaza_con_plan_y_con_orden(
    tmp_path, monkeypatch, capsys, modo
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    modo_argv = ["--plan", str(plan)] if modo == "plan" else ["--orden", "inverso"]

    codigo = ivn.run(
        [
            "--source", "json", "--json", str(json_path),
            "--sidecar", str(tmp_path / "corrida.json"), "--sleep", "0",
            *modo_argv,
        ]
    )  # fmt: skip

    assert codigo == 2
    assert "--id-corrida" in capsys.readouterr().err
    assert vistos == []


def test_dry_run_con_plan_cuenta_los_casos_sin_red_ni_escritura(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON, CANAL_TELEFONO_JSON, CANAL_WEB_JSON])
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--plan", str(plan), "--dry-run"))

    assert codigo == 0
    assert "DRY-RUN" in capsys.readouterr().out
    assert vistos == []
    assert not (tmp_path / "corrida.json").exists()


# ── Modo campana (c-166): --orden/--seed como atajo (task 2.7) ──────────────


def test_orden_genera_el_plan_lo_escribe_junto_al_sidecar_y_procesa_en_ese_orden(
    tmp_path, monkeypatch
):
    ids = [f"R{numero:03d}" for numero in range(1, 7)]
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 6)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    plan_esperado = pc.generar_plan_campana(ids, "aleatorio", 11)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "aleatorio", "--seed", "11"))

    plan_escrito = pc.leer_plan_csv(tmp_path / "corrida.json.plan.csv")
    assert codigo == 0
    assert plan_escrito == plan_esperado
    assert vistos == [fila.id_caso for fila in plan_esperado]
    assert [entrada["posicion"] for entrada in _leer_sidecar(tmp_path)] == [1, 2, 3, 4, 5, 6]
    assert {entrada["orden"] for entrada in _leer_sidecar(tmp_path)} == {"aleatorio"}


def test_orden_sin_semilla_deja_la_celda_seed_vacia_en_el_plan_escrito(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 4)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "alternado"))

    assert codigo == 0
    assert vistos == ["R001", "R003", "R002", "R004"]
    assert {fila.seed for fila in pc.leer_plan_csv(tmp_path / "corrida.json.plan.csv")} == {None}


def test_orden_aleatorio_sin_seed_termina_con_error_que_pide_seed_y_no_envia_nada(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "aleatorio"))

    assert codigo == 2
    assert "--seed" in capsys.readouterr().err
    assert vistos == []
    assert not (tmp_path / "corrida.json").exists()
    assert not (tmp_path / "corrida.json.plan.csv").exists()


def test_orden_no_pisa_un_plan_previo_distinto_de_la_misma_corrida(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 4)
    previo = _escribir_plan(tmp_path / "corrida.json.plan.csv", IDS_5[:4], "inverso")
    antes = previo.read_bytes()
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "directo"))

    assert codigo == 2
    assert "corrida.json.plan.csv" in capsys.readouterr().err
    assert previo.read_bytes() == antes
    assert vistos == []


def test_orden_acepta_un_plan_previo_identico_para_reanudar_la_corrida(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 4)
    _escribir_plan(tmp_path / "corrida.json.plan.csv", IDS_5[:4], "inverso")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "inverso"))

    assert codigo == 0
    assert vistos == ["R004", "R003", "R002", "R001"]


def test_dry_run_con_orden_no_escribe_el_plan(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    _ingesta_falsa(monkeypatch, [])

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "inverso", "--dry-run"))

    assert codigo == 0
    assert "DRY-RUN" in capsys.readouterr().out
    assert not (tmp_path / "corrida.json.plan.csv").exists()


# ── Modo campana (c-166): proteccion de archivos versionados (task 2.8) ─────

JSON_CANONICO = "data/corpus_evaluacion_pseudonimizado.json"
COPIA_DE_CAMPANA = "evaluation/data/campana/corpus_campana.json"


def _argv_con_modo(modo_argv, **opciones) -> list[str]:
    """argv de campana donde cada opcion es un flag explicito (None = no se pasa)."""
    argv = ["--source", "json", "--id-corrida", "corrida-1", "--sleep", "0", *modo_argv]
    for flag, valor in opciones.items():
        if valor is not None:
            argv += [f"--{flag}", valor]
    return argv


@pytest.mark.parametrize("modo", ["orden", "plan"])
@pytest.mark.parametrize(
    ("json_arg", "sidecar_arg", "ofensor"),
    [
        pytest.param(None, "corrida.json", JSON_CANONICO, id="json_en_su_default"),
        pytest.param(JSON_CANONICO, "corrida.json", JSON_CANONICO, id="json_canonico"),
        pytest.param("data/corpus_resultados.json", "corrida.json", "data/corpus_resultados.json", id="json_resultados"),
        pytest.param("campana.json", "data/corpus_resultados.json", "data/corpus_resultados.json", id="sidecar_resultados"),
        pytest.param("campana.json", "data/corpus_resultados_telefonia.json", "data/corpus_resultados_telefonia.json", id="sidecar_telefonia"),
        pytest.param("campana.json", "data/corpus_resultados_n8n.json", "data/corpus_resultados_n8n.json", id="sidecar_n8n_por_defecto"),
        pytest.param("campana.json", "data/corpus_resultados_otra.json", "data/corpus_resultados_otra.json", id="sidecar_patron"),
    ],
)  # fmt: skip
def test_con_plan_u_orden_aborta_si_json_o_sidecar_apuntan_a_un_archivo_versionado(
    tmp_path, monkeypatch, capsys, modo, json_arg, sidecar_arg, ofensor
):
    monkeypatch.chdir(tmp_path)  # cualquier escritura indebida caeria aca, no en el repo
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    for variable in ("INGEST_OPERATOR_USERNAME", "INGEST_OPERATOR_PASSWORD"):
        monkeypatch.delenv(variable)  # la proteccion se evalua antes de leer credenciales
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ivn.run(_argv_con_modo(modo_argv, json=json_arg, sidecar=sidecar_arg))

    err = capsys.readouterr().err
    assert codigo == 2
    assert ofensor in err
    assert "evaluation/data/campana/" in err  # la ruta de campana sugerida
    assert "INGEST_OPERATOR" not in err
    assert vistos == []
    assert not (tmp_path / "data").exists()  # no se escribio nada en data/
    assert not list(tmp_path.glob("*.plan.csv"))


def test_con_plan_la_ruta_absoluta_a_un_archivo_versionado_del_repo_tambien_se_rechaza(
    tmp_path, monkeypatch, capsys
):
    versionado = _REPO_ROOT / "data" / "corpus_resultados.json"
    antes = versionado.read_bytes() if versionado.exists() else None
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 2)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    # Red de seguridad: aun si la proteccion fallara, ningun escritor toca el repo real.
    intentos_de_escritura: list[str] = []
    monkeypatch.setattr(
        ivn, "write_sidecar_json", lambda ruta, *a, **k: intentos_de_escritura.append(str(ruta))
    )
    monkeypatch.setattr(
        ivn, "merge_evaluation_json", lambda ruta, *a, **k: intentos_de_escritura.append(str(ruta))
    )

    codigo = ivn.run(
        _argv_con_modo(["--plan", str(plan)], json=str(json_path), sidecar=str(versionado))
    )

    assert codigo == 2
    assert "corpus_resultados.json" in capsys.readouterr().err
    assert vistos == []
    assert intentos_de_escritura == []
    assert (versionado.read_bytes() if versionado.exists() else None) == antes


def test_sin_plan_ni_orden_los_defaults_versionados_no_se_bloquean(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 2)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    monkeypatch.chdir(tmp_path)

    # Sin --plan/--orden la conducta no cambia: el sidecar toma su default (data/...).
    codigo = ivn.run(["--source", "json", "--json", str(json_path), "--sleep", "0"])

    assert codigo == 0
    assert vistos == ["R001", "R002"]
    assert (tmp_path / ivn.DEFAULT_SIDECAR).exists()


# ── Modo campana (c-166): sidecar propio de la corrida (task 2.9) ───────────


@pytest.mark.parametrize("modo", ["orden", "plan"])
def test_con_plan_u_orden_el_sidecar_es_obligatorio(tmp_path, monkeypatch, capsys, modo):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)
    monkeypatch.chdir(tmp_path)
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ivn.run(_argv_con_modo(modo_argv, json=str(json_path)))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "--sidecar" in err and "obligatorio" in err
    assert vistos == []
    assert not (tmp_path / "data").exists()  # el default NO rige en modo campana


def _sembrar_sidecar(tmp_path, id_corrida) -> bytes:
    entrada = replace(_ok_result("R001"), id_corrida=id_corrida, t_e2e_s=99.0)
    ruta = tmp_path / "corrida.json"
    ruta.write_text(json.dumps([asdict(entrada)]), encoding="utf-8")
    return ruta.read_bytes()


def test_un_sidecar_existente_de_otra_corrida_aborta_sin_enviar_ni_tocarlo(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    antes = _sembrar_sidecar(tmp_path, "corrida-previa")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "directo"))

    err = capsys.readouterr().err
    assert codigo == 2
    assert "corrida-previa" in err and "corrida-1" in err
    assert vistos == []
    assert (tmp_path / "corrida.json").read_bytes() == antes


def test_un_sidecar_historico_sin_id_corrida_se_trata_como_de_otra_corrida(
    tmp_path, monkeypatch, capsys
):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    _sembrar_sidecar(tmp_path, None)
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "directo"))

    assert codigo == 2
    assert "sin id_corrida" in capsys.readouterr().err
    assert vistos == []


def test_un_sidecar_existente_con_el_mismo_id_corrida_se_reanuda(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    _sembrar_sidecar(tmp_path, "corrida-1")
    vistos: list[str] = []
    _ingesta_falsa(monkeypatch, vistos)

    codigo = ivn.run(_argv_campana(tmp_path, json_path, "--orden", "directo"))

    entradas = _leer_sidecar(tmp_path)
    assert codigo == 0
    assert vistos == ["R001", "R002", "R003"]
    assert [entrada["case_id"] for entrada in entradas] == ["R001", "R002", "R003"]
    assert {entrada["id_corrida"] for entrada in entradas} == {"corrida-1"}
    assert entradas[0]["t_e2e_s"] == 7.0  # el re-envio valido reemplaza al previo (merge)


# ── Modo campana (c-166): sin write-back a CSV/XLSX (task 2.10) ─────────────


@pytest.mark.parametrize("modo", ["orden", "plan"])
def test_con_plan_u_orden_no_se_escriben_ni_el_csv_ni_el_xlsx(tmp_path, monkeypatch, modo):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 3)
    plan = _escribir_plan(tmp_path / "plan.csv", ["R001", "R002", "R003"])
    vistos: list[str] = []
    escrituras = _ingesta_falsa(monkeypatch, vistos)
    modo_argv = ["--orden", "inverso"] if modo == "orden" else ["--plan", str(plan)]

    codigo = ivn.run(_argv_campana(tmp_path, json_path, *modo_argv))

    assert codigo == 0
    assert len(vistos) == 3  # la corrida se hizo
    assert escrituras == []  # los datos de campana viven solo en el sidecar y en la copia de campana


def test_sin_plan_ni_orden_se_siguen_escribiendo_el_csv_y_el_xlsx(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 2)
    escrituras = _ingesta_falsa(monkeypatch, [])

    codigo = ivn.run(
        [
            "--source", "json", "--json", str(json_path),
            "--sidecar", str(tmp_path / "sidecar.json"), "--sleep", "0",
        ]
    )  # fmt: skip

    assert codigo == 0
    assert escrituras == ["csv", "xlsx"]


def test_con_plan_el_json_de_campana_si_recibe_las_mediciones(tmp_path, monkeypatch):
    json_path = tmp_path / "campana.json"
    _write_cases_json(json_path, [CANAL_CORREO_JSON] * 2)
    _ingesta_falsa(monkeypatch, [])

    ivn.run(_argv_campana(tmp_path, json_path, "--orden", "directo"))

    casos = json.loads(json_path.read_text(encoding="utf-8"))["casos"]
    assert [caso["tiempo_automatizado_s"] for caso in casos] == [7.0, 7.0]
