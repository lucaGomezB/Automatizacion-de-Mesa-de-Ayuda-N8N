"""
Tests de la descarga autenticada de la grabacion de Twilio (c-52).

TDD: se escriben ANTES del modulo.

Cubren:
    - Descarga con HTTP Basic (`AccountSid:AuthToken`).
    - Construccion de la URL `.wav` / `.mp3` sin duplicar la extension.
    - Error de descarga (estado no exitoso), timeout y credenciales faltantes.
"""

from __future__ import annotations

import base64

import httpx
import pytest

_SID = "ACtest0000000000000000000000000"  # gitleaks:allow
_TOKEN = "token-de-prueba"  # gitleaks:allow
_RECORDING = "https://api.twilio.com/2010-04-01/Accounts/ACtest/Recordings/RE123"


def _module():
    from app.utils import twilio_media

    return twilio_media


def _http(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def _expected_basic(sid: str = _SID, token: str = _TOKEN) -> str:
    raw = f"{sid}:{token}".encode()
    return "Basic " + base64.b64encode(raw).decode()


# ── 4.4 RED — URL .wav / .mp3 ───────────────────────────────────────────────


def test_build_url_agrega_wav_por_defecto():
    build = _module().build_recording_url
    assert build(_RECORDING) == f"{_RECORDING}.wav"


def test_build_url_agrega_mp3():
    build = _module().build_recording_url
    assert build(_RECORDING, extension="mp3") == f"{_RECORDING}.mp3"


def test_build_url_no_duplica_la_extension():
    build = _module().build_recording_url
    assert build(f"{_RECORDING}.wav") == f"{_RECORDING}.wav"
    assert build(f"{_RECORDING}.wav", extension="mp3") == f"{_RECORDING}.mp3"


def test_build_url_rechaza_extension_desconocida():
    build = _module().build_recording_url
    with pytest.raises(ValueError):
        build(_RECORDING, extension="ogg")


# ── 4.5 GREEN — Descarga con Basic auth ─────────────────────────────────────


async def test_descarga_usa_basic_auth_y_devuelve_contenido():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        return httpx.Response(200, content=b"WAVDATA")

    media_cls = _module().TwilioMediaClient
    async with _http(handler) as http:
        media = media_cls(account_sid=_SID, auth_token=_TOKEN, http_client=http)
        data = await media.download(_RECORDING)

    assert data == b"WAVDATA"
    assert captured["auth"] == _expected_basic()
    assert captured["url"] == f"{_RECORDING}.wav"


async def test_descarga_mp3():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, content=b"MP3DATA")

    media_cls = _module().TwilioMediaClient
    async with _http(handler) as http:
        media = media_cls(account_sid=_SID, auth_token=_TOKEN, http_client=http)
        data = await media.download(_RECORDING, extension="mp3")

    assert data == b"MP3DATA"
    assert captured["url"] == f"{_RECORDING}.mp3"


# ── 4.6 TRIANGULATE — Estado no exitoso, timeout y credenciales faltantes ───


async def test_estado_no_exitoso_lanza_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, content=b"not found")

    error_cls = _module().TwilioMediaError
    media_cls = _module().TwilioMediaClient
    async with _http(handler) as http:
        media = media_cls(account_sid=_SID, auth_token=_TOKEN, http_client=http)
        with pytest.raises(error_cls):
            await media.download(_RECORDING)


async def test_timeout_lanza_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    error_cls = _module().TwilioMediaError
    media_cls = _module().TwilioMediaClient
    async with _http(handler) as http:
        media = media_cls(account_sid=_SID, auth_token=_TOKEN, http_client=http)
        with pytest.raises(error_cls):
            await media.download(_RECORDING)


async def test_credenciales_faltantes_lanza_error():
    error_cls = _module().TwilioMediaError
    media_cls = _module().TwilioMediaClient
    with pytest.raises(error_cls):
        await media_cls(account_sid="", auth_token="").download(_RECORDING)