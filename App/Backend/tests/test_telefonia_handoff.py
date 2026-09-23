"""
Tests del handoff autenticado backend -> n8n del canal de telefonia (c-52).

TDD: se escriben ANTES de la variante dedicada en `app/utils/n8n_webhook.py`.

Cubren:
    - Payload EXACTO {descripcion_pseudonimizada, call_sid, caller, ingresado_en}.
    - Secreto compartido en la invocacion (header `X-N8N-Secret`).
    - El payload NO expone el transcript crudo ni PII en claro.
    - La falta de URL o de secreto NO produce un handoff silencioso.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import httpx
import pytest

_NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)


def _module():
    from app.utils import n8n_webhook

    return n8n_webhook


def _settings(url: str = "http://n8n/telefonia", secret: str = "handoff-secret"):
    settings = MagicMock()
    settings.n8n_telefonia_webhook_url = url
    settings.n8n_webhook_secret = secret
    return settings


def _payload():
    return _module().build_telefonia_handoff_payload(
        descripcion_pseudonimizada="Hola, soy [PERSONA]",
        call_sid="CA-HANDOFF-1",
        caller="+5492615551234",
        ingresado_en=_NOW,
    )


# ── 5.4 RED — Payload exacto ────────────────────────────────────────────────


def test_build_payload_tiene_exactamente_las_cuatro_claves():
    payload = _payload()
    assert set(payload.keys()) == {
        "descripcion_pseudonimizada",
        "call_sid",
        "caller",
        "ingresado_en",
    }
    assert payload["call_sid"] == "CA-HANDOFF-1"
    assert payload["caller"] == "+5492615551234"
    assert payload["ingresado_en"] == _NOW.isoformat()


def test_build_payload_no_incluye_transcript_crudo():
    payload = _payload()
    for prohibido in ("transcript", "transcript_original", "texto", "audio"):
        assert prohibido not in payload


# ── 5.5 GREEN — Handoff autenticado ─────────────────────────────────────────


async def test_notify_envia_payload_exacto_con_secreto(monkeypatch):
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["secret"] = request.headers.get("x-n8n-secret")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(
        "app.utils.n8n_webhook.get_settings", lambda: _settings()
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        outcome = await _module().notify_telefonia_handoff(_payload(), http_client=http)

    assert outcome == _module().HANDOFF_SENT
    assert captured["url"] == "http://n8n/telefonia"
    assert captured["secret"] == "handoff-secret"
    assert b"CA-HANDOFF-1" in captured["body"]
    assert b"transcript" not in captured["body"]


# ── 5.6 TRIANGULATE — Sin fuga y sin handoff silencioso ─────────────────────


async def test_falta_de_secreto_no_envia_handoff(monkeypatch):
    called = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        called["n"] += 1
        return httpx.Response(200)

    monkeypatch.setattr(
        "app.utils.n8n_webhook.get_settings", lambda: _settings(secret="")
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        outcome = await _module().notify_telefonia_handoff(_payload(), http_client=http)

    assert outcome == _module().HANDOFF_SKIPPED_NO_SECRET
    assert called["n"] == 0


async def test_url_no_configurada_no_envia_handoff(monkeypatch):
    called = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        called["n"] += 1
        return httpx.Response(200)

    monkeypatch.setattr(
        "app.utils.n8n_webhook.get_settings", lambda: _settings(url="")
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        outcome = await _module().notify_telefonia_handoff(_payload(), http_client=http)

    assert outcome == _module().HANDOFF_SKIPPED_NO_URL
    assert called["n"] == 0


def test_payload_pseudonimizado_no_contiene_pii_cruda():
    crudo = "Juan Perez juan.perez@empresa.local 2615551234"
    from app.utils.pseudonymizer import pseudonymize

    pseudonimizado = pseudonymize(crudo, ["empresa.local"]).texto
    payload = _module().build_telefonia_handoff_payload(
        descripcion_pseudonimizada=pseudonimizado,
        call_sid="CA-PII-2",
        caller=None,
        ingresado_en=_NOW,
    )
    serializado = str(payload)
    assert "Juan Perez" not in serializado
    assert "juan.perez@empresa.local" not in serializado
    assert "2615551234" not in serializado