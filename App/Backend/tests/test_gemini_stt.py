"""
Tests del cliente de speech-to-text `GeminiSttClient` (c-52).

TDD: se escriben ANTES del cliente.

Cubren:
    - Modelo configurable (`gemini-3.5-transcribe` por defecto, override).
    - `transcription_config` pasado por `generation_config`, en modo verbatim
      con granularidad de palabra y `language_codes=["es-419"]`.
    - `store=False`.
    - El audio se sube con `files.upload` y se referencia por `uri`.
    - Triangulacion: fallo del cliente y respuesta vacia NO abortan en silencio.
"""

from __future__ import annotations

import pytest

# ── Dobles de prueba del SDK de Gemini ──────────────────────────────────────


class _FakeFile:
    def __init__(self, uri: str, mime_type: str) -> None:
        self.uri = uri
        self.mime_type = mime_type


class _FakeInteraction:
    def __init__(self, output_text: str | None) -> None:
        self.output_text = output_text


class _FakeFiles:
    def __init__(self) -> None:
        self.uploaded: list[bytes] = []
        self.uri = "https://files.example/audio-1"

    async def upload(self, *, file, config=None):
        data = file.read() if hasattr(file, "read") else file
        self.uploaded.append(data)
        return _FakeFile(uri=self.uri, mime_type="audio/wav")


class _FakeInteractions:
    def __init__(self, output_text: str | None = "texto transcripto") -> None:
        self.output_text = output_text
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.output_text, Exception):
            raise self.output_text
        return _FakeInteraction(self.output_text)


class _FakeAio:
    def __init__(self, output_text: str | None = "texto transcripto") -> None:
        self.files = _FakeFiles()
        self.interactions = _FakeInteractions(output_text)


class _FakeClient:
    def __init__(self, output_text: str | None = "texto transcripto") -> None:
        self.aio = _FakeAio(output_text)


def _client_cls():
    from app.clients.gemini_stt import GeminiSttClient

    return GeminiSttClient


def _error_cls():
    from app.clients.gemini_stt import SttTranscriptionError

    return SttTranscriptionError


_AUDIO = b"RIFF....WAVEfmt "


# ── 4.1 RED — Configuracion de la llamada ───────────────────────────────────


async def test_usa_el_modelo_configurado_por_defecto():
    fake = _FakeClient()
    client = _client_cls()(client=fake)

    texto = await client.transcribe(_AUDIO, mime_type="audio/wav")

    kwargs = fake.aio.interactions.calls[0]
    assert kwargs["model"] == "gemini-3.5-transcribe"
    assert texto == "texto transcripto"


async def test_acepta_un_modelo_alternativo():
    fake = _FakeClient()
    client = _client_cls()(client=fake, model="gemini-3.5-transcribe-experimental")

    await client.transcribe(_AUDIO)

    assert (
        fake.aio.interactions.calls[0]["model"]
        == "gemini-3.5-transcribe-experimental"
    )


async def test_transcription_config_va_por_generation_config_en_verbatim():
    fake = _FakeClient()
    client = _client_cls()(client=fake)

    await client.transcribe(_AUDIO)

    generation_config = fake.aio.interactions.calls[0]["generation_config"]
    transcription = generation_config.transcription_config
    assert transcription is not None
    assert transcription.mode.type == "verbatim"
    assert transcription.mode.timestamp_granularities == ["word"]
    assert transcription.language_codes == ["es-419"]


async def test_store_es_false():
    fake = _FakeClient()
    client = _client_cls()(client=fake)

    await client.transcribe(_AUDIO)

    assert fake.aio.interactions.calls[0]["store"] is False


async def test_el_audio_se_sube_y_se_referencia_por_uri():
    fake = _FakeClient()
    client = _client_cls()(client=fake)

    await client.transcribe(_AUDIO, mime_type="audio/wav")

    assert fake.aio.files.uploaded == [_AUDIO]
    entrada = fake.aio.interactions.calls[0]["input"]
    assert entrada[0]["type"] == "audio"
    assert entrada[0]["uri"] == fake.aio.files.uri
    assert entrada[0]["mime_type"] == "audio/wav"


# ── 4.3 TRIANGULATE — Fallo y respuesta vacia no silenciosos ────────────────


async def test_fallo_del_cliente_propaga_error_de_dominio():
    fake = _FakeClient(output_text=RuntimeError("api caida"))
    client = _client_cls()(client=fake)

    with pytest.raises(_error_cls()):
        await client.transcribe(_AUDIO)


async def test_respuesta_vacia_no_se_devuelve_en_silencio():
    fake = _FakeClient(output_text="")
    client = _client_cls()(client=fake)

    with pytest.raises(_error_cls()):
        await client.transcribe(_AUDIO)


async def test_respuesta_none_no_se_devuelve_en_silencio():
    fake = _FakeClient(output_text=None)
    client = _client_cls()(client=fake)

    with pytest.raises(_error_cls()):
        await client.transcribe(_AUDIO)