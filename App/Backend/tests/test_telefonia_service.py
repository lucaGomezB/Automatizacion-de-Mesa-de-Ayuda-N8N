"""
Tests del servicio de ingreso asincronico de telefonia (c-52).

TDD: se escriben ANTES del servicio.

Cubren:
    - Orden del flujo: idempotencia -> sellado -> reserva -> descarga -> STT ->
      pseudonimizacion -> persistencia -> handoff.
    - Idempotencia por CallSid (no reserva ni descarga de nuevo).
    - Guarda denegada: persiste estado explicito y no descarga.
    - Fallo de descarga / STT: persiste estado de error sin abortar.
    - Pseudonimizacion ANTES del handoff (el crudo nunca cruza el borde).
    - Reserva de `backend_stt` estimada por duracion con cap de 45 s.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.config.settings import Settings
from app.cost_guard.clock import FrozenClock
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.decision import GuardDecision, window_start
from app.cost_guard.guard import CostGuard
from app.cost_guard.protocols import CounterKey
from app.cost_guard.store_fake import InMemoryCounterStore

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
_URL = "https://api.twilio.com/2010-04-01/Accounts/ACtest/Recordings/RE1"


@pytest.fixture(autouse=True)
def override_encryption_key(monkeypatch):
    """Inyecta la clave Fernet de prueba y resetea el cache lazy."""
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


def _service_module():
    from app.services import telefonia_service

    return telefonia_service


def _settings():
    settings = MagicMock()
    settings.pseudonymization_internal_domains = ["empresa.local"]
    settings.pseudonymization_encryption_key = _TEST_FERNET_KEY
    settings.twilio_account_sid = "ACtest"
    settings.twilio_auth_token = "token"
    settings.n8n_telefonia_webhook_url = "http://n8n/telefonia"
    settings.n8n_webhook_secret = "handoff-secret"
    return settings


def _real_settings(**overrides) -> Settings:
    base = dict(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="test-key",
        pseudonymization_encryption_key=_TEST_FERNET_KEY,
        jwt_secret_key="test-jwt-secret",
        _env_file=None,
    )
    base.update(overrides)
    return Settings(**base)


def _callback(**overrides):
    from app.schemas.telefonia import RecordingStatusCallback

    base = dict(
        account_sid="ACtest",
        call_sid="CA-1",
        recording_sid="RE-1",
        recording_url=_URL,
        recording_status="completed",
        recording_duration=30,
        recording_channels=1,
        recording_source="RecordVerb",
    )
    base.update(overrides)
    return RecordingStatusCallback(**base)


class RecordingGuard:
    """Doble de la guarda que registra cada reserva."""

    def __init__(self, allowed: bool = True, cause: str | None = None) -> None:
        self.allowed = allowed
        self.cause = cause
        self.calls: list[dict] = []
        self.events: list = []

    async def reserve(self, provider, caller=None, amount=Decimal("1")):
        self.events.append("guard")
        self.calls.append({"provider": provider, "caller": caller, "amount": amount})
        if self.allowed:
            return GuardDecision(allowed=True, cause=None)
        return GuardDecision(allowed=False, cause=self.cause or "budget")


class RecordingMedia:
    """Doble de la descarga de media que registra la URL y simula fallos."""

    def __init__(self, audio: bytes = b"WAVDATA", error: Exception | None = None):
        self.audio = audio
        self.error = error
        self.calls: list[str] = []
        self.events: list = []

    async def download(self, recording_url: str, extension: str = "wav") -> bytes:
        self.events.append("media")
        self.calls.append(recording_url)
        if self.error is not None:
            raise self.error
        return self.audio


class RecordingStt:
    """Doble del STT que registra el audio y simula fallos."""

    model = "gemini-3.5-transcribe"

    def __init__(self, texto: str = "Hola, soy Juan Perez", error: Exception | None = None):
        self.texto = texto
        self.error = error
        self.calls: list[bytes] = []
        self.events: list = []

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        self.events.append("stt")
        self.calls.append(audio_bytes)
        if self.error is not None:
            raise self.error
        return self.texto


class RecordingNotifier:
    """Doble del notificador del handoff."""

    def __init__(self) -> None:
        self.payloads: list[dict] = []
        self.events: list = []

    async def __call__(self, payload: dict) -> None:
        self.events.append("handoff")
        self.payloads.append(payload)


def _service(session, guard, media, stt, notifier, settings=None):
    from app.services.telefonia_service import TelefoniaService

    return TelefoniaService(
        session,
        cost_guard=guard,
        media_client=media,
        stt_client=stt,
        notifier=notifier,
        clock=FrozenClock(_NOW),
        settings=settings if settings is not None else _settings(),
    )


# ── 5.1 RED — Orden del flujo ───────────────────────────────────────────────


async def test_flujo_feliz_respeta_el_orden_y_persiste(db_session):
    events: list = []
    guard = RecordingGuard()
    media = RecordingMedia()
    stt = RecordingStt(texto="Hola, soy Juan Perez")
    notifier = RecordingNotifier()
    for dep in (guard, media, stt, notifier):
        dep.events = events

    service = _service(db_session, guard, media, stt, notifier)
    ingreso = await service.process_recording(_callback())

    assert events[:3] == ["guard", "media", "stt"]
    await asyncio.sleep(0)
    assert events == ["guard", "media", "stt", "handoff"]

    assert guard.calls[0]["provider"] == "backend_stt"
    assert media.calls == [_URL]
    assert stt.calls == [b"WAVDATA"]
    assert ingreso.transcripcion_estado == "transcrito"
    assert ingreso.transcript_original == "Hola, soy Juan Perez"
    assert ingreso.descripcion_pseudonimizada == "Hola, soy [PERSONA]"
    assert ingreso.ingresado_en is not None
    assert ingreso.persistido_en is not None
    assert len(notifier.payloads) == 1


# ── 5.3 TRIANGULATE ─────────────────────────────────────────────────────────


async def test_callsid_repetido_no_reserva_ni_descarga(db_session):
    guard = RecordingGuard()
    media = RecordingMedia()
    stt = RecordingStt()
    notifier = RecordingNotifier()
    service = _service(db_session, guard, media, stt, notifier)

    primero = await service.process_recording(_callback(call_sid="CA-DUP"))
    await asyncio.sleep(0)

    guard.calls.clear()
    media.calls.clear()
    stt.calls.clear()
    notifier.payloads.clear()

    segundo = await service.process_recording(_callback(call_sid="CA-DUP"))
    await asyncio.sleep(0)

    assert segundo.id == primero.id
    assert guard.calls == []
    assert media.calls == []
    assert stt.calls == []
    assert notifier.payloads == []


async def test_guarda_denegada_persiste_estado_y_no_descarga(db_session):
    guard = RecordingGuard(allowed=False, cause="budget")
    media = RecordingMedia()
    stt = RecordingStt()
    notifier = RecordingNotifier()
    service = _service(db_session, guard, media, stt, notifier)

    ingreso = await service.process_recording(_callback(call_sid="CA-DENIED"))
    await asyncio.sleep(0)

    assert ingreso.transcripcion_estado == "guarda_denegada"
    assert ingreso.error_detalle == "budget"
    assert media.calls == []
    assert stt.calls == []
    assert notifier.payloads == []


async def test_fallo_descarga_persiste_estado_sin_abortar(db_session):
    from app.utils.twilio_media import TwilioMediaDownloadError

    guard = RecordingGuard()
    media = RecordingMedia(error=TwilioMediaDownloadError("fallo"))
    stt = RecordingStt()
    notifier = RecordingNotifier()
    service = _service(db_session, guard, media, stt, notifier)

    ingreso = await service.process_recording(_callback(call_sid="CA-DL"))

    assert ingreso.transcripcion_estado == "error_descarga"
    assert ingreso.error_detalle
    assert stt.calls == []
    assert notifier.payloads == []


async def test_fallo_stt_persiste_estado_sin_abortar(db_session):
    from app.clients.gemini_stt import SttTranscriptionError

    guard = RecordingGuard()
    media = RecordingMedia()
    stt = RecordingStt(error=SttTranscriptionError("fallo"))
    notifier = RecordingNotifier()
    service = _service(db_session, guard, media, stt, notifier)

    ingreso = await service.process_recording(_callback(call_sid="CA-STT"))

    assert ingreso.transcripcion_estado == "error_stt"
    assert ingreso.error_detalle
    assert media.calls == [_URL]
    assert notifier.payloads == []


async def test_pseudonimiza_antes_del_handoff(db_session):
    guard = RecordingGuard()
    media = RecordingMedia()
    stt = RecordingStt(texto="Hola, soy Juan Perez y mi correo es juan.perez@empresa.local")
    notifier = RecordingNotifier()
    service = _service(db_session, guard, media, stt, notifier)

    await service.process_recording(_callback(call_sid="CA-PII"))
    await asyncio.sleep(0)

    payload = notifier.payloads[0]
    assert "[PERSONA]" in payload["descripcion_pseudonimizada"]
    assert "[EMAIL]" in payload["descripcion_pseudonimizada"]
    assert "Juan Perez" not in payload["descripcion_pseudonimizada"]
    assert "juan.perez" not in payload["descripcion_pseudonimizada"]


async def test_reserva_backend_stt_estimada_por_duracion(db_session):
    """La reserva escala el costo unitario por la duracion / cap 45 s."""
    store = InMemoryCounterStore()
    config = CostGuardConfig.from_settings(_real_settings())
    guard = CostGuard(store=store, clock=FrozenClock(_NOW), config=config)
    from app.services.cost_guard_service import CostGuardService

    media = RecordingMedia()
    stt = RecordingStt()
    notifier = RecordingNotifier()
    service = _service(
        db_session,
        CostGuardService(guard),
        media,
        stt,
        notifier,
        settings=_real_settings(),
    )

    await service.process_recording(
        _callback(call_sid="CA-AMT-30", recording_duration=30)
    )

    from app.cost_guard import constants

    key = CounterKey(
        ambito=constants.AMBITO_GLOBAL,
        clave="budget",
        ventana_inicio=window_start(_NOW, config.budget_window_seconds),
    )
    unit = config.unit_costs_usd[constants.PROVIDER_BACKEND_STT]
    esperado = unit * Decimal(30) / Decimal(45)
    assert store.snapshot(key).costo_usd == esperado


async def test_reserva_backend_stt_acotada_por_el_cap(db_session):
    store = InMemoryCounterStore()
    config = CostGuardConfig.from_settings(_real_settings())
    guard = CostGuard(store=store, clock=FrozenClock(_NOW), config=config)
    from app.services.cost_guard_service import CostGuardService

    service = _service(
        db_session,
        CostGuardService(guard),
        RecordingMedia(),
        RecordingStt(),
        RecordingNotifier(),
        settings=_real_settings(),
    )

    await service.process_recording(
        _callback(call_sid="CA-AMT-100", recording_duration=100)
    )

    from app.cost_guard import constants

    unit = config.unit_costs_usd[constants.PROVIDER_BACKEND_STT]
    # 100 s se acota a 45 s => una unidad completa.
    total = Decimal("0")
    for key, snap in store.committed.items():
        if key.ambito == constants.AMBITO_GLOBAL and key.clave == "budget":
            total += snap.costo_usd
    assert total == unit


# ── 8.1 TRIANGULATE — la latencia incluye el trabajo de STT ─────────────────


async def test_latencia_incluye_stt_entre_sello_y_persistencia(db_session):
    """
    C-52 (e2e-timing-instrumentation): `ingresado_en` se sella en la recepcion
    del callback (ANTES de descargar/transcribir) y `persistido_en` se fija
    DESPUES de la transcripcion. La latencia derivada incluye, por construccion,
    el trabajo de descarga/STT/pseudonimizacion/handoff del backend.
    """
    from app.services.telefonia_service import TelefoniaService

    clock = FrozenClock(_NOW)

    class AvanzandoStt(RecordingStt):
        async def transcribe(self, audio_bytes, mime_type="audio/wav"):
            clock.advance(7)
            return await super().transcribe(audio_bytes, mime_type)

    service = TelefoniaService(
        db_session,
        cost_guard=RecordingGuard(),
        media_client=RecordingMedia(),
        stt_client=AvanzandoStt(texto="Hola, soy Juan Perez"),
        notifier=RecordingNotifier(),
        clock=clock,
        settings=_settings(),
    )

    ingreso = await service.process_recording(_callback(call_sid="CA-LAT"))
    await asyncio.sleep(0)

    # SQLite devuelve los TIMESTAMPTZ sin zona; la semantica se verifica por el
    # delta entre sellado (antes de la STT) y persistencia (despues de la STT).
    assert ingreso.ingresado_en is not None, (
        "El sello debe fijarse en la recepcion del callback"
    )
    assert ingreso.persistido_en is not None, (
        "La persistencia debe fijarse despues de la STT"
    )

    def _naive(value):
        return value.replace(tzinfo=None) if value.tzinfo else value

    latencia = _naive(ingreso.persistido_en) - _naive(ingreso.ingresado_en)
    assert latencia == timedelta(seconds=7), (
        "La latencia end-to-end debe incluir el tiempo de transcripcion del backend "
        f"(esperado 7 s, obtenido {latencia})"
    )