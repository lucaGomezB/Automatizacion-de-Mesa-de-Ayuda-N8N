"""
Tests de los endpoints del canal de telefonia (c-52).

TDD: se escriben ANTES del router.

Cubren:
    - `POST /api/v1/telefonia/recording-status` con firma fail-closed:
      valida procesa, ausente/invalida 401, token no configurado 401.
    - El callback no requiere `From`.
    - `CallSid` repetido responde de forma idempotente (no re-descarga).
    - Un fallo de descarga/STT no devuelve 500 ni pierde el ingreso.
    - Los schemas de request/response se consumen sin AttributeError.
    - `POST /api/v1/telefonia/record-complete` devuelve el TwiML de cierre.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_db_session
from app.cost_guard.clock import FrozenClock
from app.cost_guard.decision import GuardDecision
from app.cost_guard.twilio_signature import compute_signature

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_TOKEN = "test-auth-token"  # gitleaks:allow
_NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
_PATH = "/api/v1/telefonia/recording-status"
_ACTION_PATH = "/api/v1/telefonia/record-complete"
_URL = f"http://test{_PATH}"
_ACTION_URL = f"http://test{_ACTION_PATH}"
_RECORDING = "https://api.twilio.com/2010-04-01/Accounts/ACtest/Recordings/RE1"


@pytest.fixture(autouse=True)
def override_encryption_key(monkeypatch):
    from app.config.settings import get_settings

    mock_settings = MagicMock()
    mock_settings.pseudonymization_encryption_key = _TEST_FERNET_KEY

    get_settings.cache_clear()
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)

    import app.utils.encryption as enc_module

    enc_module._fernet_instance = None
    yield
    enc_module._fernet_instance = None
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def clean_telefonia(engine):
    from app.models.telefonia_ingreso import TelefoniaIngreso

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _clean():
        async with factory() as session:
            await session.execute(delete(TelefoniaIngreso))
            await session.commit()

    await _clean()
    yield
    await _clean()


def _settings(token: str = _TOKEN):
    settings = MagicMock()
    settings.twilio_auth_token = token
    settings.pseudonymization_internal_domains = ["empresa.local"]
    settings.pseudonymization_encryption_key = _TEST_FERNET_KEY
    settings.twilio_account_sid = "ACtest"
    settings.n8n_telefonia_webhook_url = ""
    settings.n8n_webhook_secret = ""
    return settings


def _form(**overrides):
    base = dict(
        AccountSid="ACtest",
        CallSid="CA-1",
        RecordingSid="RE-1",
        RecordingUrl=_RECORDING,
        RecordingStatus="completed",
        RecordingDuration="30",
        RecordingChannels="1",
        RecordingSource="RecordVerb",
    )
    base.update(overrides)
    return base


class _FakeMedia:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls: list[str] = []

    async def download(self, recording_url: str, extension: str = "wav") -> bytes:
        self.calls.append(recording_url)
        if self.error is not None:
            raise self.error
        return b"WAVDATA"


class _FakeStt:
    model = "gemini-3.5-transcribe"

    def __init__(self, texto: str = "Hola, soy Juan Perez", error: Exception | None = None):
        self.texto = texto
        self.error = error
        self.calls: list[bytes] = []

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        self.calls.append(audio_bytes)
        if self.error is not None:
            raise self.error
        return self.texto


class _DenyingGuard:
    """Doble de la guarda que deniega la reserva (para el mapeo HTTP de W5)."""

    async def reserve(self, provider, caller=None, amount=None) -> GuardDecision:
        return GuardDecision(allowed=False, cause="budget")


class _Notifier:
    def __init__(self):
        self.payloads: list[dict] = []

    async def __call__(self, payload: dict) -> None:
        self.payloads.append(payload)


def _build_service_override(media, stt, notifier, cost_guard=None):
    async def _override(session: AsyncSession = Depends(get_db_session)):
        from app.services.telefonia_service import TelefoniaService

        return TelefoniaService(
            session,
            cost_guard=cost_guard,
            media_client=media,
            stt_client=stt,
            notifier=notifier,
            clock=FrozenClock(_NOW),
            settings=_settings(),
        )

    return _override


@asynccontextmanager
async def _client(
    engine, *, token=_TOKEN, media=None, stt=None, notifier=None, cost_guard=None
):
    from app.main import create_app
    from app.routes.telefonia import get_telefonia_service

    app = create_app()
    media = media or _FakeMedia()
    stt = stt or _FakeStt()
    notifier = notifier if notifier is not None else _Notifier()

    async def override_db():
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_telefonia_service] = _build_service_override(
        media, stt, notifier, cost_guard
    )

    with patch("app.routes.telefonia.get_settings", return_value=_settings(token)):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
            await asyncio.sleep(0)


def _signed_headers(params: dict, token: str = _TOKEN, url: str = _URL) -> dict:
    return {"X-Twilio-Signature": compute_signature(token, url, params)}


# ── 6.1 RED — Firma fail-closed ─────────────────────────────────────────────


async def test_firma_valida_acepta_el_callback(engine):
    params = _form()
    async with _client(engine) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 200, resp.text


async def test_firma_ausente_rechaza_401(engine):
    async with _client(engine) as client:
        resp = await client.post(_PATH, data=_form())
    assert resp.status_code == 401, resp.text


async def test_firma_invalida_rechaza_401(engine):
    params = _form()
    async with _client(engine) as client:
        resp = await client.post(
            _PATH, data=params, headers={"X-Twilio-Signature": "firma-falsa"}
        )
    assert resp.status_code == 401, resp.text


async def test_firma_ausente_con_campos_faltantes_rechaza_401(engine):
    """La firma se valida ANTES que los campos de formulario (fail-closed).

    Una peticion sin firma y sin `CallSid`/`RecordingUrl` debe responder 401, no
    422: el rechazo por firma precede a la validacion del formulario.
    """
    async with _client(engine) as client:
        resp = await client.post(_PATH, data={"AccountSid": "ACtest"})
    assert resp.status_code == 401, resp.text


async def test_token_no_configurado_rechaza_401(engine):
    params = _form()
    async with _client(engine, token="") as client:
        resp = await client.post(
            _PATH,
            data=params,
            headers={"X-Twilio-Signature": compute_signature(_TOKEN, _URL, params)},
        )
    assert resp.status_code == 401, resp.text


# ── 6.3 TRIANGULATE ─────────────────────────────────────────────────────────


async def test_firma_invalida_con_campos_faltantes_rechaza_401(engine):
    """Con campos faltantes, una firma invalida tambien gana con 401."""
    async with _client(engine) as client:
        resp = await client.post(
            _PATH,
            data={"AccountSid": "ACtest"},
            headers={"X-Twilio-Signature": "firma-falsa"},
        )
    assert resp.status_code == 401, resp.text


async def test_firma_valida_con_campos_faltantes_devuelve_422(engine):
    """Superada la firma, los campos requeridos siguen siendo obligatorios.

    Demuestra que el orden es firma -> formulario: una peticion bien firmada pero
    incompleta llega a la validacion del formulario (422), no se rechaza por 401.
    """
    params = {"AccountSid": "ACtest"}
    async with _client(engine) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 422, resp.text


async def test_callback_no_requiere_from(engine):
    params = _form()
    assert "From" not in params
    media = _FakeMedia()
    async with _client(engine, media=media) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 200, resp.text
    assert media.calls == [_RECORDING]


async def test_callsid_repetido_es_idempotente(engine):
    media = _FakeMedia()
    params = _form(CallSid="CA-API-DUP")
    async with _client(engine, media=media) as client:
        primera = await client.post(
            _PATH, data=params, headers=_signed_headers(params)
        )
        segunda = await client.post(
            _PATH, data=params, headers=_signed_headers(params)
        )
    assert primera.status_code == 200, primera.text
    assert segunda.status_code == 200, segunda.text
    assert primera.json()["transcripcion_estado"] == "transcrito"
    assert segunda.json()["transcripcion_estado"] == "transcrito"
    assert media.calls == [_RECORDING]


async def test_callback_repetido_sobre_pendiente_responde_200(engine):
    """W-PEND: un ingreso en vuelo (`pendiente`) responde 200 sin reprocesar.

    El callback repetido de Twilio sobre un ingreso ya `pendiente` es un no-op
    idempotente: el endpoint no re-descarga, no re-transcribe ni re-reserva y
    mapea el estado no transitorio a HTTP 200 con `status == "accepted"`.
    """
    from app.models.telefonia_ingreso import TelefoniaIngreso

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(
            TelefoniaIngreso(
                call_sid="CA-API-PEND",
                transcripcion_estado="pendiente",
                ingresado_en=_NOW,
            )
        )
        await session.commit()

    media = _FakeMedia()
    params = _form(CallSid="CA-API-PEND")
    async with _client(engine, media=media) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "accepted"
    assert body["transcripcion_estado"] == "pendiente"
    assert media.calls == []


async def test_fallo_descarga_devuelve_503(engine):
    from app.utils.twilio_media import TwilioMediaDownloadError

    media = _FakeMedia(error=TwilioMediaDownloadError("fallo"))
    params = _form(CallSid="CA-API-FAIL")
    async with _client(engine, media=media) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 503, resp.text
    assert "error" in resp.json()


async def test_fallo_stt_devuelve_503(engine):
    from app.clients.gemini_stt import SttTranscriptionError

    stt = _FakeStt(error=SttTranscriptionError("fallo"))
    params = _form(CallSid="CA-API-STT-FAIL")
    async with _client(engine, stt=stt) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 503, resp.text
    assert "error" in resp.json()


async def test_guarda_denegada_devuelve_200(engine):
    params = _form(CallSid="CA-API-GUARD")
    async with _client(engine, cost_guard=_DenyingGuard()) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 200, resp.text
    assert resp.json()["transcripcion_estado"] == "guarda_denegada"


async def test_transcrito_devuelve_200(engine):
    params = _form(CallSid="CA-API-OK")
    async with _client(engine) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 200, resp.text
    assert resp.json()["transcripcion_estado"] == "transcrito"


async def test_fallo_descarga_persiste_el_ingreso_tras_503(engine):
    """El 503 invita el reintento de Twilio: el estado de error debe persistir.

    La dependency `get_db_session` revierte la transaccion ante una excepcion;
    el servicio confirma el estado terminal antes de que el 503 la alcance.
    """
    from sqlalchemy import select

    from app.models.telefonia_ingreso import TelefoniaIngreso
    from app.utils.twilio_media import TwilioMediaDownloadError

    media = _FakeMedia(error=TwilioMediaDownloadError("fallo"))
    params = _form(CallSid="CA-API-PERSIST")
    async with _client(engine, media=media) as client:
        resp = await client.post(_PATH, data=params, headers=_signed_headers(params))
    assert resp.status_code == 503, resp.text

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        fila = (
            await session.execute(
                select(TelefoniaIngreso).where(
                    TelefoniaIngreso.call_sid == "CA-API-PERSIST"
                )
            )
        ).scalar_one_or_none()

    assert fila is not None
    assert fila.transcripcion_estado == "error_descarga"


# ── 6.4 Schemas consumidos ──────────────────────────────────────────────────


def test_recording_status_callback_schema_parsea_los_campos():
    from app.schemas.telefonia import RecordingStatusCallback

    callback = RecordingStatusCallback(
        account_sid="ACtest",
        call_sid="CA-SCHEMA",
        recording_sid="RE-1",
        recording_url=_RECORDING,
        recording_status="completed",
        recording_duration=45,
        recording_channels=1,
        recording_source="RecordVerb",
    )
    assert callback.call_sid == "CA-SCHEMA"
    assert callback.recording_duration == 45
    assert callback.caller is None


def test_respuesta_usa_el_schema():
    from app.schemas.telefonia import TelefoniaRecordingResponse

    respuesta = TelefoniaRecordingResponse(
        status="accepted",
        call_sid="CA-SCHEMA",
        transcripcion_estado="transcrito",
    )
    assert set(respuesta.model_dump().keys()) == {
        "status",
        "call_sid",
        "transcripcion_estado",
    }


# ── 6.2 GREEN — Accion posterior a la grabacion ─────────────────────────────


async def test_record_complete_devuelve_twiml(engine):
    async with _client(engine) as client:
        resp = await client.post(
            _ACTION_PATH, headers=_signed_headers({}, url=_ACTION_URL)
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")
    assert "<Say" in resp.text
    assert "<Record" not in resp.text


async def test_record_complete_exige_firma(engine):
    async with _client(engine) as client:
        resp = await client.post(_ACTION_PATH)
    assert resp.status_code == 401, resp.text