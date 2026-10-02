"""Offline unit tests for the N8N corpus ingest harness (c-68).

No network, no real corpus, no mutation of ``data/``. Every filesystem touch
happens inside ``tmp_path``. Descriptions here are synthetic and public text;
the real corpus descriptions are never loaded.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

import pytest

import ingest_via_n8n as ivn

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
