"""
Tests del TwiML del webhook de voz tras c-52 (TDD: se escriben ANTES de la
implementacion).

Describen el contrato nuevo del documento de llamada admitida:

    - `<Record>` en modo MONO (sin `transcribe`), con `recordingStatusCallback`
      hacia el callback de estado del backend y `action` hacia el documento de
      cierre post-grabacion.
    - El `<Say>` posterior es ALCANZABLE: vive en el documento `action`
      (`render_twiml_record_complete`), no inline tras `<Record>`.
    - El mensaje NO promete la creacion inmediata del ticket (el alta ahora es
      asincrona).
    - La rama denegada conserva `<Say>` + `<Hangup/>` y NO graba.

Estrategia: se parsea el XML devuelto con ElementTree (no se comparan strings
literales) para verificar la estructura real que Twilio consume.
"""

from __future__ import annotations

from xml.etree import ElementTree

import pytest

from app.cost_guard import twiml

_BASE = "https://backend.mesa.local"
_STATUS_URL = f"{_BASE}/api/v1/telefonia/recording-status"
_ACTION_URL = f"{_BASE}/api/v1/telefonia/record-complete"


def _parse(xml: str) -> ElementTree.Element:
    return ElementTree.fromstring(xml)


# ── 2.1 RED — Grabacion mono con callbacks y sin transcripcion ───────────────


def test_allowed_record_es_mono_con_callbacks_y_sin_transcribe():
    """El `<Record>` admitido declara callbacks y NO solicita transcripcion."""
    root = _parse(twiml.render_twiml_allowed(base_url=_BASE))
    assert root.tag == "Response"

    record = root.find("Record")
    assert record is not None, "el documento admitido debe contener un <Record>"
    assert record.attrib.get("maxLength") == "45"
    assert record.attrib.get("finishOnKey") == "#"
    assert record.attrib.get("playBeep") == "true"
    assert record.attrib.get("recordingStatusCallback") == _STATUS_URL
    assert record.attrib.get("action") == _ACTION_URL
    # c-52: la transcripcion embebida de Twilio deja de usarse.
    assert "transcribe" not in record.attrib


def test_allowed_no_promete_ticket_inmediato():
    """El mensaje de la llamada admitida no promete el alta inmediata."""
    xml = twiml.render_twiml_allowed(base_url=_BASE).lower()
    assert "fue registrado" not in xml
    assert "numero de ticket" not in xml


# ── 2.1 RED — Documento `action` de cierre post-grabacion ────────────────────


def test_record_complete_expone_un_say_alcanzable():
    """El documento `action` reproduce un <Say> de cierre y no graba."""
    root = _parse(twiml.render_twiml_record_complete())
    assert root.tag == "Response"
    say = root.find("Say")
    assert say is not None, "el documento action debe tener un <Say> alcanzable"
    assert root.find("Record") is None, "el documento action no debe volver a grabar"


def test_record_complete_no_promete_ticket_inmediato():
    xml = twiml.render_twiml_record_complete().lower()
    assert "fue registrado" not in xml
    assert "numero de ticket" not in xml


# ── 2.3 TRIANGULATE — Rama denegada y ausencia de transcribe en todos ────────


def test_denied_conserva_say_y_hangup_sin_grabar():
    root = _parse(twiml.render_twiml_denied())
    assert root.find("Say") is not None
    assert root.find("Hangup") is not None
    assert root.find("Record") is None


@pytest.mark.parametrize("doc", ["allowed", "record-complete", "denied"])
def test_ningun_documento_solicita_transcribe(doc):
    """Ningun documento TwiML del canal solicita la transcripcion embebida."""
    if doc == "allowed":
        xml = twiml.render_twiml_allowed(base_url=_BASE)
    elif doc == "record-complete":
        xml = twiml.render_twiml_record_complete()
    else:
        xml = twiml.render_twiml_denied()
    root = _parse(xml)
    for element in root.iter():
        assert "transcribe" not in element.attrib
    assert "transcribe" not in xml


def test_allowed_usa_la_base_publica_configurada(monkeypatch):
    """Sin argumento, los callbacks se construyen desde la base publica."""

    class _S:
        backend_public_base_url = _BASE

    monkeypatch.setattr(twiml, "get_settings", lambda: _S())
    root = _parse(twiml.render_twiml_allowed())
    record = root.find("Record")
    assert record is not None
    assert record.attrib.get("recordingStatusCallback") == _STATUS_URL
    assert record.attrib.get("action") == _ACTION_URL
