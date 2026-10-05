"""Offline tests for the ``GET /corpus-cases`` endpoint and its phone filter.

No network beyond an ephemeral loopback socket bound to 127.0.0.1. The corpus
is a synthetic temp file: no real (even pseudonymized) descriptions are read
or written here. Every credential is a synthetic placeholder.
"""

from __future__ import annotations

import http.client
import json
import threading
from pathlib import Path

import pytest

import mint_token as mt

ACCOUNT_SID = "AC" + "0" * 32
API_KEY_SID = "SK" + "1" * 32
API_KEY_SECRET = "placeholder-api-key-secret-000000000000"
TWIML_APP_SID = "AP" + "2" * 32

ENV = {
    "TWILIO_ACCOUNT_SID": ACCOUNT_SID,
    "TWILIO_API_KEY_SID": API_KEY_SID,
    "TWILIO_API_KEY_SECRET": API_KEY_SECRET,
    "TWILIO_TWIML_APP_SID": TWIML_APP_SID,
}


def _write_corpus(path: Path, casos: list) -> Path:
    path.write_text(
        json.dumps(
            {"schema_version": 1, "metadata": {}, "casos": casos},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _caso(case_id: str, canal: str, descripcion: str = "descripcion sintetica") -> dict:
    return {
        "id": case_id,
        "descripcion": descripcion,
        "canal_origen": canal,
        "sector_asignado": "Sistemas",
        "sectores_adicionales": [],
        "tiempo_manual_s": 60.0,
        "tiempo_automatizado_s": None,
    }


# ── 4.2 RED: tolerant telephone filter ──────────────────────────────────────


def test_load_telephone_cases_returns_only_phone_channel(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [
            _caso("T1", "llamada telefonica"),
            _caso("T2", "llamada telefónica"),
            _caso("T3", "telefono"),
            _caso("W1", "formulario web"),
            _caso("C1", "correo electrónico"),
        ],
    )
    cases = mt.load_telephone_cases(corpus)
    assert [c["id"] for c in cases] == ["T1", "T2", "T3"]


def test_load_telephone_cases_projects_only_id_and_descripcion(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [_caso("T1", "telefono", descripcion="No puede iniciar sesion")],
    )
    cases = mt.load_telephone_cases(corpus)
    assert cases == [{"id": "T1", "descripcion": "No puede iniciar sesion"}]


def test_load_telephone_cases_tolerates_accents_case_and_whitespace(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [
            _caso("T1", "  Llamada Telefónica  "),
            _caso("T2", "TELÉFONO"),
            _caso("T3", "LLAMADA TELEFONICA"),
        ],
    )
    cases = mt.load_telephone_cases(corpus)
    assert [c["id"] for c in cases] == ["T1", "T2", "T3"]


def test_load_telephone_cases_returns_empty_when_no_phone_cases(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [_caso("W1", "formulario web"), _caso("C1", "correo electrónico")],
    )
    assert mt.load_telephone_cases(corpus) == []


def test_load_telephone_cases_missing_file_raises_clear_error(tmp_path):
    missing = tmp_path / "no-existe.json"
    with pytest.raises(mt.CorpusError) as excinfo:
        mt.load_telephone_cases(missing)
    assert str(missing) in str(excinfo.value)


def test_load_telephone_cases_invalid_json_raises_corpus_error(tmp_path):
    bad = tmp_path / "corpus.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(mt.CorpusError):
        mt.load_telephone_cases(bad)


def test_load_telephone_cases_excludes_cases_missing_id(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [
            {"descripcion": "sin id", "canal_origen": "telefono"},
            _caso("T1", "telefono"),
        ],
    )
    assert [c["id"] for c in mt.load_telephone_cases(corpus)] == ["T1"]


def test_load_telephone_cases_excludes_missing_or_unknown_channel(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [
            {"id": "X1", "descripcion": "sin canal"},
            {"id": "X2", "descripcion": "fax", "canal_origen": "fax"},
            _caso("T1", "telefono"),
        ],
    )
    assert [c["id"] for c in mt.load_telephone_cases(corpus)] == ["T1"]


def test_load_telephone_cases_missing_casos_key_raises_corpus_error(tmp_path):
    bad = tmp_path / "corpus.json"
    bad.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    with pytest.raises(mt.CorpusError):
        mt.load_telephone_cases(bad)


# ── 4.3 GREEN: the loopback endpoint ────────────────────────────────────────


@pytest.fixture
def server(tmp_path):
    corpus = _write_corpus(
        tmp_path / "corpus.json",
        [
            _caso("T1", "llamada telefonica", descripcion="Caso telefonico uno"),
            _caso("W1", "formulario web", descripcion="Caso web"),
        ],
    )
    config = mt.load_config(ENV)
    httpd = mt.build_server(
        "127.0.0.1",
        0,
        config,
        identity="corpus-operator",
        ttl_seconds=120,
        corpus_json_path=corpus,
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def _get(httpd, path):
    host, port = httpd.server_address[0], httpd.server_address[1]
    conn = http.client.HTTPConnection(host, port, timeout=5)
    conn.request("GET", path)
    response = conn.getresponse()
    body = response.read()
    conn.close()
    return response.status, body


def test_corpus_cases_endpoint_returns_phone_cases(server):
    status, body = _get(server, "/corpus-cases")
    assert status == 200
    payload = json.loads(body.decode("utf-8"))
    assert payload == [{"id": "T1", "descripcion": "Caso telefonico uno"}]


def test_corpus_cases_endpoint_reports_missing_corpus(tmp_path):
    config = mt.load_config(ENV)
    httpd = mt.build_server(
        "127.0.0.1",
        0,
        config,
        identity="corpus-operator",
        ttl_seconds=120,
        corpus_json_path=tmp_path / "no-existe.json",
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(httpd, "/corpus-cases")
        assert status == 500
        payload = json.loads(body.decode("utf-8"))
        assert "no-existe.json" in payload["error"]["message"]
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def test_corpus_cases_endpoint_does_not_log_descriptions(server, capfd):
    _get(server, "/corpus-cases")
    captured = capfd.readouterr()
    assert "Caso telefonico uno" not in captured.out
    assert "Caso telefonico uno" not in captured.err
