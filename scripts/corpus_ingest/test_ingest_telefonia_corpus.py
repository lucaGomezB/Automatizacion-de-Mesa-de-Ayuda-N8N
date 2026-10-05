"""Offline unit tests for the telephony corpus recovery/write-back script (c-70).

No network, no real corpus, no mutation of ``data/``. Every filesystem touch
happens inside ``tmp_path``. Descriptions here are synthetic and public text;
the real corpus descriptions are never loaded. The script is exercised through
monkeypatched network entry points so the suite stays fully offline.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# El test importa el paquete `evaluation` de la raiz del repo; agregamos la raiz
# a sys.path de forma relativa al archivo (mismo patron que pseudonymize_corpus.py)
# para que la suite corra tanto desde la raiz como desde este directorio.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ingest_corpus as ic
import ingest_telefonia_corpus as itc
import ingest_via_n8n as ivn

UTC = timezone.utc


def _dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2026, 10, 2, hour, minute, second, tzinfo=UTC)


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


def _detail(latencia: int | None = 2000, **overrides) -> dict:
    body = {
        "id": 7,
        "call_sid": "CA0123456789",
        "corpus_case_id": "R002",
        "transcripcion_estado": "completada",
        "ingresado_en": _dt(12, 0, 5).isoformat(),
        "persistido_en": _dt(12, 0, 7).isoformat(),
        "incidente_id": 11,
        "latencia_e2e_ms": latencia,
    }
    body.update(overrides)
    return body


# ── Metric derivation (tasks 5.1-5.3) ───────────────────────────────────────


def test_derive_telefonia_metric_valid_equals_pipeline_and_e2e():
    metric = itc.derive_telefonia_metric(2000)
    assert metric.t_pipeline_s == pytest.approx(2.0)
    assert metric.t_e2e_s == pytest.approx(2.0)
    assert metric.t_pipeline_s == metric.t_e2e_s
    assert metric.t_espera_s is None
    assert metric.anomalo is False


def test_derive_telefonia_metric_rounds_to_three_decimals():
    metric = itc.derive_telefonia_metric(12345)
    assert metric.t_e2e_s == pytest.approx(12.345)
    assert metric.t_pipeline_s == pytest.approx(12.345)


def test_derive_telefonia_metric_null_is_anomalous():
    metric = itc.derive_telefonia_metric(None)
    assert metric.t_e2e_s is None
    assert metric.t_pipeline_s is None
    assert metric.t_espera_s is None
    assert metric.anomalo is True


def test_derive_telefonia_metric_zero_is_anomalous():
    metric = itc.derive_telefonia_metric(0)
    assert metric.t_e2e_s is None
    assert metric.anomalo is True


def test_derive_telefonia_metric_negative_is_anomalous_without_clamping():
    metric = itc.derive_telefonia_metric(-500)
    # Excluded, never clamped to zero.
    assert metric.t_e2e_s is None
    assert metric.t_pipeline_s is None
    assert metric.anomalo is True


def test_derive_telefonia_metric_explicit_anomaly_flag():
    metric = itc.derive_telefonia_metric(2000, latencia_anomala=True)
    assert metric.t_e2e_s is None
    assert metric.anomalo is True


# ── Result construction (tasks 5.1-5.3) ─────────────────────────────────────


def test_build_telefonia_result_shape_and_no_wait():
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    assert isinstance(result, ivn.CaseResult)
    assert result.case_id == "R002"
    assert result.canal == "telefono"
    assert result.incidente_id == 11
    assert result.latencia_e2e_ms == 2000
    assert result.t_e2e_s == pytest.approx(2.0)
    assert result.t_pipeline_s == pytest.approx(2.0)
    assert result.t_espera_s is None
    assert result.anomalo is False
    assert result.error is None
    assert result.ingresado_en == _dt(12, 0, 5).isoformat()
    assert result.persistido_en == _dt(12, 0, 7).isoformat()


def test_build_telefonia_result_null_latency_is_anomalous():
    result = itc.build_telefonia_result(case_id="R002", detail=_detail(None))
    assert result.anomalo is True
    assert result.t_e2e_s is None
    assert ivn._should_write_metric(result) is False


def test_build_telefonia_result_is_description_free():
    result = itc.build_telefonia_result(
        case_id="R002", detail=_detail(descripcion="SECRET-CASE-TEXT")
    )
    assert "descripcion" not in {f for f in vars(result)}


# ── Recovery over the dedicated endpoint (tasks 5.5-5.6) ────────────────────


def test_recover_telefonia_case_ok_builds_metric():
    session = FakeSession([FakeResponse(200, _detail())])
    result = itc.recover_telefonia_case(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
    )
    method, url, _ = session.calls[0]
    assert method == "GET"
    assert itc.TELEFONIA_INGRESOS_PATH in url
    assert "corpus_case_id=R002" in url
    assert "latest=true" in url
    assert result.t_e2e_s == pytest.approx(2.0)
    assert result.error is None


def test_recover_telefonia_case_404_is_pending():
    session = FakeSession([FakeResponse(404, {})])
    result = itc.recover_telefonia_case(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
    )
    assert result.error == itc.PENDING_LABEL
    assert result.t_e2e_s is None
    assert ivn._should_write_metric(result) is False


def test_recover_telefonia_case_http_error_reports_short_label():
    # A 4xx is deterministic (never retried); the label carries the code.
    session = FakeSession([FakeResponse(403, {"error": {"code": "forbidden"}})])
    result = itc.recover_telefonia_case(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
    )
    assert result.error == "http403/forbidden"
    assert result.t_e2e_s is None


# ── Delete endpoint (tasks 5.7-5.9) ─────────────────────────────────────────


def test_delete_previos_dry_run_uses_dry_run_true():
    session = FakeSession(
        [FakeResponse(200, {"ingresos_eliminados": 2, "incidentes_eliminados": 2})]
    )
    counts = itc.delete_previos(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
        dry_run=True,
    )
    method, url, _ = session.calls[0]
    assert method == "DELETE"
    assert "corpus_case_id=R002" in url
    assert "dry_run=true" in url
    assert counts["ingresos_eliminados"] == 2


def test_delete_previos_destructive_uses_dry_run_false():
    session = FakeSession(
        [FakeResponse(200, {"ingresos_eliminados": 2, "incidentes_eliminados": 2})]
    )
    itc.delete_previos(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
        dry_run=False,
    )
    _, url, _ = session.calls[0]
    assert "dry_run=false" in url


# ── Write-back fixtures ─────────────────────────────────────────────────────


def _write_telephony_json(path) -> None:
    doc = {
        "schema_version": 1,
        "metadata": {"descripcion": "synthetic", "total_casos": 3},
        "casos": [
            {
                "id": "R001",
                "descripcion": "synthetic-d1",
                "canal_origen": "correo electrónico",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 50,
                "tiempo_automatizado_s": None,
            },
            {
                "id": "R002",
                "descripcion": "synthetic-d2",
                "canal_origen": "llamada telefónica",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 60,
                "tiempo_automatizado_s": None,
            },
            {
                "id": "R003",
                "descripcion": "synthetic-d3",
                "canal_origen": "llamada telefonica",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 70,
                "tiempo_automatizado_s": None,
            },
        ],
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


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
    # A distinct second telephony row so replacement scope is observable.
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    rows.append(["R003", "No puede llamar", "Telefono", "Sistemas", "", "90", ""])
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(rows)


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
    ws.append(["R002", "Text", "Telefono", "Sistemas", "", 110, None])
    wb.save(path)


def _write_registration_fixtures(tmp_path) -> tuple:
    """Create a valid CSV + XLSX pair (the writers require both to exist)."""
    csv_path = tmp_path / "corpus.csv"
    xlsx_path = tmp_path / "corpus.xlsx"
    _write_fixture_csv(csv_path)
    _write_fixture_xlsx(xlsx_path)
    return csv_path, xlsx_path


def _read_csv_rows(path) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


# ── Write-back (tasks 5.4-5.6) ──────────────────────────────────────────────


def test_write_back_fills_csv_columns_and_wait_blank(tmp_path):
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[result],
    )
    rows = _read_csv_rows(csv_path)
    header = rows[1]
    assert header.count(ivn.PIPELINE_COL) == 1
    assert header.count(ivn.ESPERA_COL) == 1
    assert header.count(ivn.LATENCIA_COL) == 1
    row = next(r for r in rows if r and r[0] == "R002")
    assert row[header.index(ivn.HEADER_AUTO_TIME)] == "2"
    assert row[header.index(ivn.LATENCIA_COL)] == "2000"
    assert row[header.index(ivn.PIPELINE_COL)] == "2"
    assert row[header.index(ivn.ESPERA_COL)] == ""
    # Other rows untouched.
    r001 = next(r for r in rows if r and r[0] == "R001")
    assert r001[header.index(ivn.HEADER_AUTO_TIME)] == ""


def test_write_back_is_idempotent_and_no_duplicate_columns(tmp_path):
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    for _ in range(2):
        itc.write_back(
            csv_path=csv_path,
            xlsx_path=xlsx_path,
            sidecar_path=tmp_path / "sidecar.json",
            json_path=json_path,
            results=[result],
        )
    rows = _read_csv_rows(csv_path)
    header = rows[1]
    assert header.count(ivn.PIPELINE_COL) == 1
    assert header.count(ivn.ESPERA_COL) == 1
    assert len({len(r) for r in rows}) == 1


def test_write_back_fills_xlsx_columns_and_wait_blank(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[result],
    )
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb[wb.sheetnames[0]]
    header = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    row = next(
        r for r in range(3, ws.max_row + 1) if ws.cell(row=r, column=1).value == "R002"
    )
    assert ws.cell(row=row, column=header.index(ivn.HEADER_AUTO_TIME) + 1).value == pytest.approx(2.0)
    assert ws.cell(row=row, column=header.index(ivn.LATENCIA_COL) + 1).value == 2000
    assert ws.cell(row=row, column=header.index(ivn.PIPELINE_COL) + 1).value == pytest.approx(2.0)
    assert ws.cell(row=row, column=header.index(ivn.ESPERA_COL) + 1).value is None


def test_write_back_merges_eval_json_numeric(tmp_path):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    pending = itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[result],
    )
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(2.0)
    assert by_id["R001"]["tiempo_automatizado_s"] is None
    assert by_id["R003"]["tiempo_automatizado_s"] is None
    assert pending == 2  # R001 (correo) + R003 (telefono sin medir)


def test_write_back_pending_case_writes_nothing(tmp_path):
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    pending_result = itc.recover_telefonia_case(
        session=FakeSession([FakeResponse(404, {})]),
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
    )
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[pending_result],
    )
    row = next(r for r in _read_csv_rows(csv_path) if r and r[0] == "R002")
    header = _read_csv_rows(csv_path)[1]
    assert row[header.index(ivn.HEADER_AUTO_TIME)] == ""
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] is None


def test_write_back_never_writes_null_over_existing(tmp_path):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    for case in doc["casos"]:
        if case["id"] == "R002":
            case["tiempo_automatizado_s"] = 9.0
    json_path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    anomalous = itc.build_telefonia_result(case_id="R002", detail=_detail(-500))
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[anomalous],
    )
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(9.0)


def test_write_back_sidecar_is_description_free(tmp_path):
    sidecar = tmp_path / "sidecar.json"
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    result = itc.build_telefonia_result(case_id="R002", detail=_detail())
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=sidecar,
        json_path=json_path,
        results=[result],
    )
    raw = sidecar.read_text(encoding="utf-8")
    assert "descripcion" not in raw.lower()
    data = json.loads(raw)
    assert data[0]["case_id"] == "R002"
    assert data[0]["t_espera_s"] is None


def test_merge_does_not_coerce_non_numeric_or_bool(tmp_path):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    ivn.merge_evaluation_json(json_path, {"R002": "not-a-number"})
    ivn.merge_evaluation_json(json_path, {"R002": True})
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] is None


def test_evaluation_a_float_still_rejects_non_numeric(tmp_path):
    from evaluation.corpus import CorpusError, cargar_corpus

    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    for case in doc["casos"]:
        if case["id"] == "R002":
            case["tiempo_automatizado_s"] = "not-a-number"
    json_path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(CorpusError):
        cargar_corpus(json_path)


# ── run(): replace / dry-run / creds / privacy (tasks 5.5-5.9) ──────────────


def _set_operator_creds(monkeypatch) -> None:
    monkeypatch.setenv("INGEST_OPERATOR_USERNAME", "operador")
    monkeypatch.setenv("INGEST_OPERATOR_PASSWORD", "pw")


def _fake_recover(valid_ids=("R002",), pending_ids=()):
    def recover(*, case_id, **kwargs):
        if case_id in pending_ids:
            return ivn._error_result(case_id, itc.CANAL_TELEFONO, None, itc.PENDING_LABEL)
        if case_id in valid_ids:
            return itc.build_telefonia_result(case_id=case_id, detail=_detail())
        return ivn._error_result(case_id, itc.CANAL_TELEFONO, None, itc.PENDING_LABEL)

    return recover


def test_run_missing_credentials_aborts_without_network(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    monkeypatch.delenv("INGEST_OPERATOR_USERNAME", raising=False)
    monkeypatch.delenv("INGEST_OPERATOR_PASSWORD", raising=False)

    def _boom(*a, **k):
        raise AssertionError("login must not run without credentials")

    monkeypatch.setattr(ivn, "login", _boom)
    code = itc.run(["--source", "json", "--json", str(json_path)])
    assert code == 2
    err = capsys.readouterr().err
    assert "ERROR" in err
    assert "pw" not in err


def test_run_writes_only_telephony_results(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002",)))

    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    assert code == 0
    rows = _read_csv_rows(csv_path)
    header = rows[1]
    r002 = next(r for r in rows if r and r[0] == "R002")
    r001 = next(r for r in rows if r and r[0] == "R001")
    assert r002[header.index(ivn.HEADER_AUTO_TIME)] == "2"
    assert r001[header.index(ivn.HEADER_AUTO_TIME)] == ""
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(2.0)
    assert by_id["R003"]["tiempo_automatizado_s"] is None


def test_run_pending_case_reported_and_not_written(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(
        itc, "recover_telefonia_case", _fake_recover(valid_ids=(), pending_ids=("R002",))
    )
    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "pendiente" in out.lower() or "sin_ingreso" in out.lower()
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] is None


def test_run_dry_run_no_network_no_write(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)

    def _boom(*a, **k):
        raise AssertionError("dry-run must not touch the network")

    monkeypatch.setattr(ivn, "login", _boom)
    monkeypatch.setattr(itc, "recover_telefonia_case", _boom)
    code = itc.run(["--dry-run", "--source", "json", "--json", str(json_path)])
    assert code == 0
    assert "DRY-RUN" in capsys.readouterr().out


def test_run_does_not_log_descriptions(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002",)))
    itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    out = capsys.readouterr().out
    assert "synthetic-d1" not in out
    assert "synthetic-d2" not in out
    assert "synthetic-d3" not in out


def test_run_replace_dry_run_neither_deletes_nor_writes(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002",)))

    deletes: list[dict] = []
    writes: list[dict] = []

    def fake_delete(**kwargs):
        deletes.append(kwargs)
        return {"ingresos_eliminados": 1, "incidentes_eliminados": 1}

    def fake_write_back(**kwargs):
        writes.append(kwargs)
        return 0

    monkeypatch.setattr(itc, "delete_previos", fake_delete)
    monkeypatch.setattr(itc, "write_back", fake_write_back)
    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--replace",
        ]
    )
    assert code == 0
    assert deletes and all(d["dry_run"] is True for d in deletes)
    assert writes == []
    assert "DRY-RUN" in capsys.readouterr().out


def test_run_replace_confirmed_deletes_and_writes(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002",)))

    deletes: list[dict] = []
    writes: list[dict] = []

    def fake_delete(**kwargs):
        deletes.append(kwargs)
        return {"ingresos_eliminados": 1, "incidentes_eliminados": 1}

    def fake_write_back(**kwargs):
        writes.append(kwargs)
        return 0

    monkeypatch.setattr(itc, "delete_previos", fake_delete)
    monkeypatch.setattr(itc, "write_back", fake_write_back)
    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--replace",
            "--confirm-replace",
        ]
    )
    assert code == 0
    assert deletes and all(d["dry_run"] is False for d in deletes)
    assert len(writes) == 1


def test_run_without_replace_never_deletes(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002",)))

    deletes: list[dict] = []

    def fake_delete(**kwargs):
        deletes.append(kwargs)
        return {}

    monkeypatch.setattr(itc, "delete_previos", fake_delete)
    monkeypatch.setattr(itc, "write_back", lambda **k: 0)
    code = itc.run(["--source", "json", "--json", str(json_path)])
    assert code == 0
    assert deletes == []


def test_run_replace_is_scoped_to_each_selected_case(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(
        itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002", "R003"))
    )
    seen: list[str] = []

    def fake_delete(**kwargs):
        seen.append(kwargs["case_id"])
        return {"ingresos_eliminados": 0, "incidentes_eliminados": 0}

    monkeypatch.setattr(itc, "delete_previos", fake_delete)
    monkeypatch.setattr(itc, "write_back", lambda **k: 0)
    itc.run(["--source", "json", "--json", str(json_path), "--replace"])
    # Only telephony cases (R002, R003), never the correo case R001.
    assert sorted(seen) == ["R002", "R003"]


def test_confirm_replace_without_replace_is_rejected(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    code = itc.run(["--source", "json", "--json", str(json_path), "--confirm-replace"])
    assert code == 2
    assert "confirm-replace" in capsys.readouterr().err.lower()


# ── Triangulation (tasks 5.3, 5.6, 5.9) ─────────────────────────────────────


def test_derive_telefonia_metric_rounding_variants():
    assert itc.derive_telefonia_metric(1000).t_e2e_s == pytest.approx(1.0)
    assert itc.derive_telefonia_metric(1999).t_e2e_s == pytest.approx(1.999)
    assert itc.derive_telefonia_metric(2500).t_e2e_s == pytest.approx(2.5)


def test_build_telefonia_result_explicit_anomaly_flag():
    result = itc.build_telefonia_result(
        case_id="R002", detail=_detail(2000, latencia_anomala=True)
    )
    assert result.anomalo is True
    assert result.t_e2e_s is None
    assert ivn._should_write_metric(result) is False


def test_delete_previos_error_returns_none():
    session = FakeSession([FakeResponse(403, {"error": {"code": "forbidden"}})])
    counts = itc.delete_previos(
        session=session,
        base_url="https://localhost",
        token="tok",
        case_id="R002",
        verify=False,
        timeout=5.0,
        dry_run=True,
    )
    assert counts is None


def test_write_back_mixed_results_only_valid_merged(tmp_path):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    valid = itc.build_telefonia_result(case_id="R002", detail=_detail(3000))
    anomalous = itc.build_telefonia_result(case_id="R003", detail=_detail(-1000))
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[valid, anomalous],
    )
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["casos"]}
    assert by_id["R002"]["tiempo_automatizado_s"] == pytest.approx(3.0)
    assert by_id["R003"]["tiempo_automatizado_s"] is None
    # The anomalous telephony row keeps its prior (blank) CSV cell.
    rows = _read_csv_rows(csv_path)
    header = rows[1]
    r003 = next(r for r in rows if r and r[0] == "R003")
    assert r003[header.index(ivn.HEADER_AUTO_TIME)] == ""


def test_write_back_anomalous_preserves_csv_prior_value(tmp_path):
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    # Seed a prior valid value for R002 first.
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[itc.build_telefonia_result(case_id="R002", detail=_detail(2000))],
    )
    # An anomalous replay must not overwrite it.
    itc.write_back(
        csv_path=csv_path,
        xlsx_path=xlsx_path,
        sidecar_path=tmp_path / "sidecar.json",
        json_path=json_path,
        results=[itc.build_telefonia_result(case_id="R002", detail=_detail(-500))],
    )
    rows = _read_csv_rows(csv_path)
    header = rows[1]
    r002 = next(r for r in rows if r and r[0] == "R002")
    assert r002[header.index(ivn.HEADER_AUTO_TIME)] == "2"
    assert r002[header.index(ivn.LATENCIA_COL)] == "2000"


def test_run_replace_dry_run_reports_counts_multiple_and_none(tmp_path, monkeypatch, capsys):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")
    monkeypatch.setattr(
        itc, "recover_telefonia_case", _fake_recover(valid_ids=("R002", "R003"))
    )
    counts = {"R002": 2, "R003": 0}

    def fake_delete(**kwargs):
        return {
            "ingresos_eliminados": counts[kwargs["case_id"]],
            "incidentes_eliminados": counts[kwargs["case_id"]],
        }

    monkeypatch.setattr(itc, "delete_previos", fake_delete)
    monkeypatch.setattr(itc, "write_back", lambda **k: 0)
    code = itc.run(["--source", "json", "--json", str(json_path), "--replace"])
    out = capsys.readouterr().out
    assert code == 0
    assert "replace R002" in out
    assert "replace R003" in out


def test_run_hard_error_returns_nonzero(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")

    def failing_recover(**kwargs):
        return ivn._error_result(
            kwargs["case_id"], itc.CANAL_TELEFONO, None, "http403/forbidden"
        )

    monkeypatch.setattr(itc, "recover_telefonia_case", failing_recover)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    assert code == 1


def test_run_recover_exception_is_reported_and_does_not_abort(tmp_path, monkeypatch):
    json_path = tmp_path / "corpus.json"
    _write_telephony_json(json_path)
    _set_operator_creds(monkeypatch)
    monkeypatch.setattr(ivn, "login", lambda *a, **k: "tok")

    def exploding_recover(**kwargs):
        if kwargs["case_id"] == "R002":
            raise RuntimeError("boom")
        return itc.build_telefonia_result(case_id=kwargs["case_id"], detail=_detail(2000))

    monkeypatch.setattr(itc, "recover_telefonia_case", exploding_recover)
    csv_path, xlsx_path = _write_registration_fixtures(tmp_path)
    code = itc.run(
        [
            "--source",
            "json",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--xlsx",
            str(xlsx_path),
            "--sidecar",
            str(tmp_path / "sidecar.json"),
        ]
    )
    # The exception is a per-case hard error; the run completes.
    assert code == 1
    sidecar = json.loads((tmp_path / "sidecar.json").read_text(encoding="utf-8"))
    by_id = {entry["case_id"]: entry for entry in sidecar}
    assert by_id["R002"]["error"] == "RuntimeError"
    assert by_id["R003"]["error"] is None

