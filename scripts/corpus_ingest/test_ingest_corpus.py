"""Offline unit tests for the corpus ingest harness.

No network, no real corpus file, no mutation of ``data/``. Every filesystem
touch happens inside ``tmp_path``. Descriptions here are synthetic and public.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

import pytest

import ingest_corpus as ic


# ── Channel mapping ─────────────────────────────────────────────────────────


def test_channel_mapping_canonical_names():
    assert ic.map_canal_origen_id("Correo") == 1
    assert ic.map_canal_origen_id("Formulario Web") == 2
    assert ic.map_canal_origen_id("Telefono") == 3


def test_channel_mapping_is_case_and_space_insensitive():
    assert ic.map_canal_origen_id("  correo ") == 1
    assert ic.map_canal_origen_id("FORMULARIO WEB") == 2


def test_channel_mapping_unknown_returns_none():
    assert ic.map_canal_origen_id("Paloma Mensajera") is None
    assert ic.map_canal_origen_id("") is None
    assert ic.map_canal_origen_id(None) is None


# ── Payload builder ─────────────────────────────────────────────────────────


def test_build_payload_shape_and_determinism():
    fixed = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)
    payload = ic.build_incidente_payload(
        descripcion="Synthetic description long enough",
        canal_origen_id=2,
        case_id="R007",
        ingresado_en=fixed,
    )
    assert payload["descripcion"] == "Synthetic description long enough"
    assert payload["canal_origen_id"] == 2
    assert payload["origen_evento"] == "creacion_incidente"
    assert payload["origen_message_id"] == "corpus-R007"
    assert payload["ingresado_en"].endswith("+00:00")
    # Message id is deterministic: same case -> same id.
    again = ic.build_incidente_payload(
        descripcion="x" * 20, canal_origen_id=1, case_id="R007", ingresado_en=fixed
    )
    assert again["origen_message_id"] == payload["origen_message_id"]


def test_build_payload_ingresado_en_is_tz_aware():
    payload = ic.build_incidente_payload(
        descripcion="y" * 20, canal_origen_id=1, case_id="R001"
    )
    parsed = datetime.fromisoformat(payload["ingresado_en"])
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None


# ── CSV read/write ──────────────────────────────────────────────────────────


def _write_fixture_csv(path):
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
        writer.writerow(
            [
                "R001",
                "No puede ingresar, con coma y todo",
                "Correo",
                "Seguridad Informatica",
                "Soporte Tecnico Software",
                "75",
                "",
            ]
        )
        writer.writerow(
            ["R002", "No puede abrir archivos", "Telefono", "Sistemas", "", "110", ""]
        )


def test_read_cases_csv(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    cases = ic.read_csv_cases(path)
    assert [c.case_id for c in cases] == ["R001", "R002"]
    assert cases[0].canal == "Correo"
    assert cases[0].descripcion.startswith("No puede ingresar")


def test_write_csv_updates_columns_and_preserves_originals(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Seguridad Informatica",
            revision=False,
            wall_s=1.5234,
            latencia_e2e_ms=420,
            error=None,
        ),
        "R002": ic.CorpusResult(
            case_id="R002",
            incidente_id=None,
            numero_incidente=None,
            sector=None,
            revision=None,
            wall_s=None,
            latencia_e2e_ms=None,
            error="timeout",
        ),
    }
    ic.write_csv_results(path, results)

    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header[-1] == ic.LATENCIA_COL
    auto = header.index("TIempo de Registro Automatico (Segundos)")
    lat = header.index(ic.LATENCIA_COL)
    row1 = rows[2]
    row2 = rows[3]
    assert row1[auto] == "1.523"
    assert row1[lat] == "420"
    assert row2[auto] == ""  # error -> left blank
    assert row2[lat] == ""
    # Originals preserved.
    assert row1[0] == "R001"
    assert row1[5] == "75"
    assert rows[0][0] == "Casos de incidentes registrados:"


def test_read_cases_dispatches_csv(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    assert len(ic.read_cases(path, "csv")) == 2


def test_read_csv_cases_skips_blank_rows(tmp_path):
    path = tmp_path / "corpus.csv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["Title:", "", "", "", "", "", ""])
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
        writer.writerow(["R001", "Text", "Correo", "Sistemas", "", "50", ""])
        writer.writerow(["", "", "", "", "", "", ""])
    cases = ic.read_csv_cases(path)
    assert [c.case_id for c in cases] == ["R001"]


def test_select_cases_filters_channel_and_applies_limit():
    cases = [
        ic.CorpusCase("R001", "d1", "Correo"),
        ic.CorpusCase("R002", "d2", "Telefono"),
        ic.CorpusCase("R003", "d3", "correo"),
        ic.CorpusCase("R004", "d4", "Formulario Web"),
    ]
    only_correo = ic._select_cases(cases, "Correo", None)
    assert [c.case_id for c in only_correo] == ["R001", "R003"]
    limited = ic._select_cases(cases, None, 2)
    assert [c.case_id for c in limited] == ["R001", "R002"]
    assert ic._select_cases(cases, "Correo", 1)[0].case_id == "R001"


def test_read_xlsx_cases(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "corpus.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Title:"])
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
    ws.append(["R001", "Text", "Correo", "Sistemas", "", 50, None])
    wb.save(path)
    cases = ic.read_cases(path, "xlsx")
    assert [c.case_id for c in cases] == ["R001"]
    assert cases[0].canal == "Correo"


def test_write_csv_is_idempotent(tmp_path):
    path = tmp_path / "corpus.csv"
    _write_fixture_csv(path)
    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Sistemas",
            revision=True,
            wall_s=2.0,
            latencia_e2e_ms=100,
            error=None,
        )
    }
    ic.write_csv_results(path, results)
    ic.write_csv_results(path, results)
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[1]
    assert header.count(ic.LATENCIA_COL) == 1
    # Every row has the same field count.
    assert len({len(r) for r in rows}) == 1


# ── XLSX read/write ─────────────────────────────────────────────────────────


def test_write_xlsx_updates_columns_and_is_idempotent(tmp_path):
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
    ws.append(["R001", "Text", "Correo", "Seguridad Informatica", "", 75, None])
    ws.append(["R002", "Text2", "Telefono", "Sistemas", "", 110, None])
    wb.save(path)

    results = {
        "R001": ic.CorpusResult(
            case_id="R001",
            incidente_id=11,
            numero_incidente="INC-000011",
            sector="Seguridad Informatica",
            revision=False,
            wall_s=1.5,
            latencia_e2e_ms=420,
            error=None,
        ),
        "R002": ic.CorpusResult(
            case_id="R002",
            incidente_id=None,
            numero_incidente=None,
            sector=None,
            revision=None,
            wall_s=None,
            latencia_e2e_ms=None,
            error="http500",
        ),
    }
    ic.write_xlsx_results(path, results)
    ic.write_xlsx_results(path, results)  # idempotent: no duplicate column

    wb2 = openpyxl.load_workbook(path)
    ws2 = wb2[wb2.sheetnames[0]]
    header = [ws2.cell(row=2, column=c).value for c in range(1, ws2.max_column + 1)]
    assert header.count(ic.LATENCIA_COL) == 1
    assert header[-1] == ic.LATENCIA_COL
    auto_col = header.index("TIempo de Registro Automatico (Segundos)") + 1
    lat_col = header.index(ic.LATENCIA_COL) + 1
    assert ws2.cell(row=3, column=auto_col).value == 1.5
    assert ws2.cell(row=3, column=lat_col).value == 420
    assert ws2.cell(row=4, column=auto_col).value in (None, "")
    assert ws2.cell(row=3, column=1).value == "R001"
    assert ws2.cell(row=3, column=4).value == "Seguridad Informatica"


# ── Sidecar JSON ────────────────────────────────────────────────────────────


def test_sidecar_json_has_no_description(tmp_path):
    path = tmp_path / "resultados.json"
    results = [
        ic.CorpusResult(
            case_id="R001",
            incidente_id=1,
            numero_incidente="INC-000001",
            sector="Sistemas",
            revision=True,
            wall_s=0.9,
            latencia_e2e_ms=300,
            error=None,
        )
    ]
    ic.write_sidecar_json(path, results)
    raw = path.read_text(encoding="utf-8")
    assert "descripcion" not in raw.lower()
    data = json.loads(raw)
    assert data[0]["case_id"] == "R001"
    assert data[0]["latencia_e2e_ms"] == 300
