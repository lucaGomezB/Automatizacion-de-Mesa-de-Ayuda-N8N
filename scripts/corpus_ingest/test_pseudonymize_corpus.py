"""Offline unit tests for the corpus pseudonymization tool.

No network, no real corpus file, no mutation of ``data/``. Every filesystem
touch happens inside ``tmp_path``. All descriptions here are synthetic and
public; no real PII is embedded.
"""

from __future__ import annotations

import csv

import pseudonymize_corpus as pc

SECTORES = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

HEADER = [
    "ID",
    "Descripcion",
    "Canal de Origen",
    "Sector Asignado",
    "Sectores Adicionales",
    "Tiempo de Registro Manual (segundos)",
    "TIempo de Registro Automatico (Segundos)",
]
TITLE = ["Casos de incidentes registrados:", "", "", "", "", "", ""]


def _write_fixture(path, descriptions):
    """Write a title + header + one row per description, corpus-style CRLF."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(TITLE)
        writer.writerow(HEADER)
        for index, desc in enumerate(descriptions, start=1):
            writer.writerow([f"R{index:03d}", desc, "Correo", "Sistemas", "", "50", ""])


def _read_rows(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


# ── Masking via the production pseudonymizer ────────────────────────────────


def test_masks_email_phone_and_persona():
    rows = [TITLE, HEADER, [
        "R001",
        "El usuario Juan Perez reporta fallas. Escribir a juan.perez@example.com "
        "o llamar al 261 555 1234.",
        "Correo",
        "Sistemas",
        "",
        "50",
        "",
    ]]
    outcome = pc.pseudonymize_rows(rows, [])
    masked = outcome.rows[2][1]
    assert "[PERSONA]" in masked
    assert "[EMAIL]" in masked
    assert "[TELEFONO]" in masked
    assert "Juan" not in masked
    assert "juan.perez@example.com" not in masked
    assert outcome.conteos["email"] >= 1
    assert outcome.conteos["telefono"] >= 1
    assert outcome.conteos["persona"] >= 1


def test_masks_host_when_internal_domains_provided():
    rows = [TITLE, HEADER, [
        "R001",
        "El servidor srv-correo01.corp.empresa.com no responde.",
        "Correo",
        "Sistemas",
        "",
        "50",
        "",
    ]]
    outcome = pc.pseudonymize_rows(rows, ["corp.empresa.com"])
    masked = outcome.rows[2][1]
    assert "[HOST]" in masked
    assert "srv-correo01.corp.empresa.com" not in masked
    assert outcome.conteos["host"] >= 1


def test_no_pii_produces_zero_counts_and_unchanged_text():
    rows = [TITLE, HEADER, [
        "R001",
        "No abre el explorador de archivos",
        "Correo",
        "Sistemas",
        "",
        "50",
        "",
    ]]
    outcome = pc.pseudonymize_rows(rows, [])
    assert outcome.rows[2][1] == "No abre el explorador de archivos"
    assert outcome.conteos == {
        "email": 0,
        "telefono": 0,
        "host": 0,
        "persona": 0,
        "tarjeta": 0,
    }


def test_preserves_canonical_sectors_and_technical_terms():
    description = (
        "Incidente en Seguridad Informatica, Soporte Tecnico Hardware, "
        "Soporte Tecnico Software, Bases de Datos y Sistemas; "
        "el servidor con Windows Server 2019 no responde."
    )
    rows = [TITLE, HEADER, ["R001", description, "Correo", "Sistemas", "", "50", ""]]
    outcome = pc.pseudonymize_rows(rows, [])
    masked = outcome.rows[2][1]
    for sector in SECTORES:
        assert sector in masked
    assert "Windows Server 2019" in masked
    assert "[PERSONA]" not in masked


# ── Structure preservation ──────────────────────────────────────────────────


def test_preserves_title_header_rowcount_and_non_desc_columns():
    descriptions = [f"Caso sintetico numero {i} sin PII" for i in range(1, 201)]
    rows = [TITLE, HEADER] + [
        [f"R{i:03d}", d, "Telefono", "Bases de Datos", "Sistemas", str(i), ""]
        for i, d in enumerate(descriptions, start=1)
    ]
    outcome = pc.pseudonymize_rows(rows, [])
    assert len(outcome.rows) == 202
    assert outcome.rows[0] == TITLE
    assert outcome.rows[1] == HEADER
    for original, masked in zip(rows[2:], outcome.rows[2:]):
        assert masked[1] == original[1]  # no PII -> unchanged
        for col in range(len(HEADER)):
            if col == 1:
                continue
            assert masked[col] == original[col]


def test_write_preserves_crlf_and_quoting(tmp_path):
    rows = [TITLE, HEADER, [
        "R001",
        "Descripcion con coma, y texto",
        "Correo",
        "Seguridad Informatica, Bases de Datos",
        "",
        "75",
        "",
    ]]
    out = tmp_path / "out.csv"
    pc.write_rows(out, rows)
    raw = out.read_bytes()
    assert b"\r\n" in raw
    assert raw.count(b"\n") == raw.count(b"\r\n")
    parsed = _read_rows(out)
    assert parsed[2][3] == "Seguridad Informatica, Bases de Datos"


# ── CLI behavior ────────────────────────────────────────────────────────────


def test_dry_run_writes_nothing(tmp_path):
    csv_path = tmp_path / "corpus.csv"
    out_path = tmp_path / "out.csv"
    _write_fixture(csv_path, ["Texto sin PII"])
    code = pc.run(["--csv", str(csv_path), "--out", str(out_path), "--dry-run"])
    assert code == 0
    assert not out_path.exists()


def test_never_overwrites_raw_input(tmp_path):
    csv_path = tmp_path / "corpus.csv"
    _write_fixture(csv_path, ["Texto sin PII"])
    before = csv_path.read_bytes()
    code = pc.run(["--csv", str(csv_path), "--out", str(csv_path)])
    assert code == 2
    assert csv_path.read_bytes() == before


def test_run_writes_pseudonymized_output(tmp_path):
    csv_path = tmp_path / "corpus.csv"
    out_path = tmp_path / "out.csv"
    _write_fixture(csv_path, [
        "El usuario Juan Perez escribe a juan@example.com o llama al 261 555 1234"
    ])
    code = pc.run(["--csv", str(csv_path), "--out", str(out_path)])
    assert code == 0
    assert out_path.exists()
    raw = out_path.read_bytes()
    assert b"[EMAIL]" in raw
    assert b"[TELEFONO]" in raw
    assert b"[PERSONA]" in raw


# ── Residual PII verification ───────────────────────────────────────────────


def test_residual_scan_flags_dirty_input():
    dirty = "Contacto: juan@example.com / 261 555 1234"
    assert pc.count_residual_pii(dirty) == {"email": 1, "telefono": 1}
    assert pc.count_residual_pii("texto limpio sin datos") == {"email": 0, "telefono": 0}
    # A year range is not a phone.
    assert pc.count_residual_pii("periodo 2015-2022") == {"email": 0, "telefono": 0}


def test_run_exits_nonzero_when_residual_pii_remains(tmp_path, monkeypatch):
    csv_path = tmp_path / "corpus.csv"
    out_path = tmp_path / "out.csv"
    _write_fixture(csv_path, ["Escribir a juan@example.com o llamar al 261 555 1234"])

    class _Noop:
        def __init__(self, texto, conteos):
            self.texto = texto
            self.conteos = conteos

    monkeypatch.setattr(
        pc,
        "pseudonymize",
        lambda text, domains: _Noop(text, {"email": 0, "telefono": 0, "host": 0, "persona": 0}),
    )
    code = pc.run(["--csv", str(csv_path), "--out", str(out_path)])
    assert code == 1


def test_parse_internal_domains():
    assert pc.parse_internal_domains("") == []
    assert pc.parse_internal_domains("corp.empresa.com, empresa.local") == [
        "corp.empresa.com",
        "empresa.local",
    ]
    assert pc.parse_internal_domains('["a.local", "b.local"]') == ["a.local", "b.local"]
