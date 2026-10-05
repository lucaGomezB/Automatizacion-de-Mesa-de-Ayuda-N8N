"""
Tests de API de la correlacion por `corpus_case_id` (c-70, secciones 2 y 3).

Strict TDD: se escriben ANTES de las rutas.

Cubren:
    - El webhook de voz (`/cost-guard/twilio/voice`) persiste `call_sid ->
      corpus_case_id` en la tabla corta cuando el parametro custom llega, y NO
      escribe nada cuando esta ausente (retrocompatible).
    - El callback de grabacion resuelve el `corpus_case_id` por `call_sid`,
      BORRA la fila pendiente, la persiste en el ingreso al sellar, purga las
      vencidas y preserva el valor en el reproceso.
    - El endpoint de lectura `GET /api/v1/telefonia/ingresos` devuelve el ultimo
      ingreso con la latencia del incidente vinculado y exige rol
      `administrador_directorio`.
    - El borrado acotado `DELETE /api/v1/telefonia/ingresos` es dry-run por
      defecto, destructivo con `dry_run=false`, respeta FKs y no toca otros casos.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_db_session
from app.cost_guard.twilio_signature import compute_signature

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_TOKEN = "test-auth-token"  # gitleaks:allow
_NOW = datetime(2026, 10, 5, 12, 0, 0, tzinfo=timezone.utc)
_RECORDING = "https://api.twilio.com/2010-04-01/Accounts/ACtest/Recordings/RE1"
_VOICE_PATH = "/api/v1/cost-guard/twilio/voice"
_VOICE_URL = f"http://test{_VOICE_PATH}"
_CALLBACK_PATH = "/api/v1/telefonia/recording-status"
_CALLBACK_URL = f"http://test{_CALLBACK_PATH}"
_INGRESOS_PATH = "/api/v1/telefonia/ingresos"
_INGRESOS_URL = f"http://test{_INGRESOS_PATH}"


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
async def clean_corpus_tables(engine):
    from app.models.catalog import Estado
    from app.models.clasificacion_log import ClasificacionLog
    from app.models.empleado import Empleado
    from app.models.incidente import Incidente
    from app.models.telefonia_ingreso import TelefoniaIngreso
    from app.models.telefonia_pending_call import TelefoniaPendingCall
    from app.models.user import User

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _clean():
        async with factory() as session:
            await session.execute(delete(TelefoniaIngreso))
            await session.execute(delete(TelefoniaPendingCall))
            await session.execute(delete(ClasificacionLog))
            await session.execute(delete(Incidente))
            # `_seed_incidente` crea (y commitea) un `Estado` de apoyo; se limpia
            # para no romper el `seed_catalogs` de otros modulos (UNIQUE nombre).
            await session.execute(delete(Estado))
            await session.execute(delete(Empleado))
            await session.execute(delete(User))
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


class _FakeMedia:
    async def download(self, recording_url: str, extension: str = "wav") -> bytes:
        return b"WAVDATA"


class _FakeStt:
    model = "gemini-3.5-transcribe"

    async def transcribe(self, audio_bytes, mime_type: str = "audio/wav") -> str:
        return "Hola, soy Juan Perez"


class _Notifier:
    def __init__(self):
        self.payloads: list[dict] = []

    async def __call__(self, payload: dict) -> None:
        self.payloads.append(payload)


def _voice_headers(params: dict, token: str = _TOKEN) -> dict:
    return {"X-Twilio-Signature": compute_signature(token, _VOICE_URL, params)}


def _voice_params(**overrides):
    base = {
        "From": "+5492615551234",
        "To": "+5492615550000",
        "CallSid": "CA-VOICE-1",
        "AccountSid": "ACtest",
        "CallStatus": "ringing",
        "Direction": "inbound",
    }
    base.update(overrides)
    return base


def _callback_form(**overrides):
    base = dict(
        AccountSid="ACtest",
        CallSid="CA-CB-1",
        RecordingSid="RE-1",
        RecordingUrl=_RECORDING,
        RecordingStatus="completed",
        RecordingDuration="30",
        RecordingChannels="1",
        RecordingSource="RecordVerb",
    )
    base.update(overrides)
    return base


def _callback_headers(params: dict, token: str = _TOKEN) -> dict:
    return {"X-Twilio-Signature": compute_signature(token, _CALLBACK_URL, params)}


def _build_service_override(notifier=None):
    notifier = notifier if notifier is not None else _Notifier()

    async def _override(session: AsyncSession = Depends(get_db_session)):
        from app.services.telefonia_service import TelefoniaService

        return TelefoniaService(
            session,
            cost_guard=None,
            media_client=_FakeMedia(),
            stt_client=_FakeStt(),
            notifier=notifier,
            clock=_FrozenClock(_NOW),
            settings=_settings(),
        )

    return _override


class _FrozenClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


@asynccontextmanager
async def _api_client(
    engine,
    *,
    token: str = _TOKEN,
    notifier=None,
    service_override=None,
    seed_empleado_rol: str | None = None,
    seed_user_id: int = 1,
    incidente_result=None,
):
    """Cliente HTTP con DB de test, auth mock y firma Twilio controlada."""
    from unittest.mock import AsyncMock, patch as _patch

    from app.main import create_app
    from app.core.security import get_current_user
    from app.cost_guard.dependencies import get_cost_guard
    from app.models.user import User
    from app.routes.incidentes import get_service as get_incidente_service
    from app.routes.telefonia import get_telefonia_service

    app = create_app()

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
    app.dependency_overrides[get_cost_guard] = lambda: None
    app.dependency_overrides[get_telefonia_service] = (
        service_override or _build_service_override(notifier)
    )

    if incidente_result is not None:
        from app.services.incidente_service import IncidenteService

        def _incidente_service_override(session: AsyncSession = Depends(get_db_session)):
            fake = AsyncMock()
            fake.classify = AsyncMock(return_value=incidente_result)
            return IncidenteService(session, classifier=fake)

        app.dependency_overrides[get_incidente_service] = _incidente_service_override

    async def override_auth():
        return User(id=seed_user_id, username="test_user", hashed_password="", is_active=True)

    app.dependency_overrides[get_current_user] = override_auth

    if seed_empleado_rol is not None:
        from app.models.empleado import Empleado
        from app.models.user import User as UserModel

        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            session.add(
                UserModel(
                    id=seed_user_id,
                    username=f"user-{seed_user_id}",
                    hashed_password="x",
                    is_active=True,
                )
            )
            await session.flush()
            session.add(
                Empleado(
                    legajo="LEG-1",
                    nombre="Admin Test",
                    email="admin@test.local",
                    rol=seed_empleado_rol,
                    user_id=seed_user_id,
                    activo=True,
                )
            )
            await session.commit()

    with patch("app.routes.cost_guard.get_settings", return_value=_settings(token)), patch(
        "app.routes.telefonia.get_settings", return_value=_settings(token)
    ), patch(
        "app.services.incidente_service.notify_n8n", new_callable=AsyncMock
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
            await asyncio.sleep(0)


async def _seed_pending(engine, call_sid: str, corpus_case_id: str, created_at=None):
    from app.models.telefonia_pending_call import TelefoniaPendingCall

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(
            TelefoniaPendingCall(
                call_sid=call_sid,
                corpus_case_id=corpus_case_id,
                created_at=created_at or _NOW,
            )
        )
        await session.commit()


async def _get_pending(engine, call_sid: str):
    from app.models.telefonia_pending_call import TelefoniaPendingCall

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return await session.get(TelefoniaPendingCall, call_sid)


async def _seed_ingreso(engine, **kwargs):
    from app.models.telefonia_ingreso import TelefoniaIngreso

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        fila = TelefoniaIngreso(**kwargs)
        session.add(fila)
        await session.commit()
        await session.refresh(fila)
        return fila


async def _get_ingreso(engine, call_sid: str):
    from app.models.telefonia_ingreso import TelefoniaIngreso

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return (
            await session.execute(
                select(TelefoniaIngreso).where(TelefoniaIngreso.call_sid == call_sid)
            )
        ).scalar_one_or_none()


# ── 2.5 RED — Webhook de voz persiste el mapeo ──────────────────────────────


async def test_voice_con_corpus_case_id_persiste_pendiente(engine):
    params = _voice_params(corpus_case_id="CASO-VOICE-1")
    async with _api_client(engine) as client:
        resp = await client.post(
            _VOICE_PATH, data=params, headers=_voice_headers(params)
        )
    assert resp.status_code == 200, resp.text

    fila = await _get_pending(engine, "CA-VOICE-1")
    assert fila is not None
    assert fila.corpus_case_id == "CASO-VOICE-1"


async def test_voice_sin_corpus_case_id_no_escribe_nada(engine):
    params = _voice_params(CallSid="CA-VOICE-SIN")
    async with _api_client(engine) as client:
        resp = await client.post(
            _VOICE_PATH, data=params, headers=_voice_headers(params)
        )
    assert resp.status_code == 200, resp.text

    assert await _get_pending(engine, "CA-VOICE-SIN") is None


async def test_voice_upsert_idempotente_por_call_sid(engine):
    params_uno = _voice_params(CallSid="CA-VOICE-DUP", corpus_case_id="CASO-A")
    params_dos = _voice_params(CallSid="CA-VOICE-DUP", corpus_case_id="CASO-B")
    async with _api_client(engine) as client:
        await client.post(_VOICE_PATH, data=params_uno, headers=_voice_headers(params_uno))
        await client.post(_VOICE_PATH, data=params_dos, headers=_voice_headers(params_dos))

    fila = await _get_pending(engine, "CA-VOICE-DUP")
    assert fila is not None
    assert fila.corpus_case_id == "CASO-B"


async def test_voice_no_agrega_corpus_case_id_a_la_url_del_callback(engine):
    """No se agrega query a la URL del callback (la firma no cambia)."""
    params = _voice_params(corpus_case_id="CASO-VOICE-URL")
    async with _api_client(engine) as client:
        resp = await client.post(
            _VOICE_PATH, data=params, headers=_voice_headers(params)
        )
    assert "corpus_case_id" not in resp.text


# ── 2.6 / 2.7 RED — Callback resuelve, borra y persiste ─────────────────────


async def test_callback_resuelve_borra_pendiente_y_persiste_en_ingreso(engine):
    await _seed_pending(engine, "CA-CB-1", "CASO-RESOLVER")
    params = _callback_form(CallSid="CA-CB-1")

    async with _api_client(engine) as client:
        resp = await client.post(
            _CALLBACK_PATH, data=params, headers=_callback_headers(params)
        )

    assert resp.status_code == 200, resp.text
    ingreso = await _get_ingreso(engine, "CA-CB-1")
    assert ingreso is not None
    assert ingreso.corpus_case_id == "CASO-RESOLVER"
    # La fila pendiente se borra al resolverla.
    assert await _get_pending(engine, "CA-CB-1") is None


async def test_callback_sin_pendiente_deja_el_ingreso_sin_corpus(engine):
    params = _callback_form(CallSid="CA-CB-SIN-PEND")

    async with _api_client(engine) as client:
        resp = await client.post(
            _CALLBACK_PATH, data=params, headers=_callback_headers(params)
        )

    assert resp.status_code == 200, resp.text
    ingreso = await _get_ingreso(engine, "CA-CB-SIN-PEND")
    assert ingreso is not None
    assert ingreso.corpus_case_id is None


async def test_callback_purga_pendientes_vencidas(engine):
    from app.repositories.telefonia_pending_call_repository import (
        PENDING_CALL_TTL_SECONDS,
    )

    vieja = datetime.now(timezone.utc) - timedelta(seconds=PENDING_CALL_TTL_SECONDS + 600)
    await _seed_pending(engine, "CA-CB-VENCIDA", "CASO-VIEJO", created_at=vieja)
    params = _callback_form(CallSid="CA-CB-PURGA")

    async with _api_client(engine) as client:
        resp = await client.post(
            _CALLBACK_PATH, data=params, headers=_callback_headers(params)
        )

    assert resp.status_code == 200, resp.text
    assert await _get_pending(engine, "CA-CB-VENCIDA") is None


async def test_reproceso_preserva_corpus_case_id(engine):
    """Un ingreso en error con corpus_case_id lo preserva al reprocesar."""
    from app.utils.twilio_media import TwilioMediaDownloadError

    await _seed_ingreso(
        engine,
        call_sid="CA-CB-RETRY",
        transcripcion_estado="error_descarga",
        corpus_case_id="CASO-RETRY",
        ingresado_en=_NOW,
    )
    params = _callback_form(CallSid="CA-CB-RETRY")

    class _MediaFalla:
        async def download(self, recording_url, extension="wav"):
            raise TwilioMediaDownloadError("fallo")

    async def _override(session: AsyncSession = Depends(get_db_session)):
        from app.services.telefonia_service import TelefoniaService

        return TelefoniaService(
            session,
            media_client=_MediaFalla(),
            stt_client=_FakeStt(),
            notifier=_Notifier(),
            clock=_FrozenClock(_NOW),
            settings=_settings(),
        )

    async with _api_client(engine, service_override=_override) as client:
        resp = await client.post(
            _CALLBACK_PATH, data=params, headers=_callback_headers(params)
        )
    assert resp.status_code == 503, resp.text

    ingreso = await _get_ingreso(engine, "CA-CB-RETRY")
    assert ingreso is not None
    assert ingreso.transcripcion_estado == "error_descarga"
    assert ingreso.corpus_case_id == "CASO-RETRY"


# ── Helpers de seccion 3 ─────────────────────────────────────────────────────


async def _seed_incidente(engine, *, ingresado_en, persistido_en, con_log=True):
    from app.models.catalog import Estado
    from app.models.clasificacion_log import ClasificacionLog
    from app.models.incidente import Incidente

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        estado = (
            await session.execute(select(Estado).where(Estado.nombre == "nuevo"))
        ).scalar_one_or_none()
        if estado is None:
            estado = Estado(nombre="nuevo", descripcion="recibido", es_terminal=False)
            session.add(estado)
            await session.flush()
        incidente = Incidente(
            descripcion_original="Juan Perez reporto una falla",
            descripcion_pseudonimizada="[PERSONA] reporto una falla",
            estado_id=estado.id,
            requiere_revision_humana=False,
            ingresado_en=ingresado_en,
            persistido_en=persistido_en,
        )
        session.add(incidente)
        await session.flush()
        if con_log:
            session.add(
                ClasificacionLog(
                    incidente_id=incidente.id,
                    confianza=0.9,
                    etapa="gemini",
                    requiere_revision_humana=False,
                )
            )
        await session.commit()
        await session.refresh(incidente)
        return incidente.id


async def _get_incidente(engine, incidente_id):
    from app.models.incidente import Incidente

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return await session.get(Incidente, incidente_id)


async def _count_logs(engine, incidente_id):
    from app.models.clasificacion_log import ClasificacionLog

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return (
            await session.execute(
                select(ClasificacionLog).where(
                    ClasificacionLog.incidente_id == incidente_id
                )
            )
        ).scalars().all()


# ── 3.2 RED — Endpoint de lectura ───────────────────────────────────────────


async def test_get_ingresos_devuelve_el_ultimo_con_latencia(engine):
    ingresado = _NOW
    persistido = _NOW + timedelta(milliseconds=2500)
    inc_id = await _seed_incidente(
        engine, ingresado_en=ingresado, persistido_en=persistido
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-READ-VIEJO",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-READ",
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-READ-NUEVO",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-READ",
        incidente_id=inc_id,
    )

    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.get(
            _INGRESOS_PATH, params={"corpus_case_id": "CASO-READ", "latest": "true"}
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["call_sid"] == "CA-READ-NUEVO"
    assert body["corpus_case_id"] == "CASO-READ"
    assert body["incidente_id"] == inc_id
    assert body["latencia_e2e_ms"] == 2500


async def test_get_ingresos_404_sin_resultados(engine):
    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.get(
            _INGRESOS_PATH, params={"corpus_case_id": "CASO-NO-EXISTE"}
        )
    assert resp.status_code == 404, resp.text
    assert resp.json()["error"]["code"]


# ── 3.4 TRIANGULATE — Visibilidad por rol ───────────────────────────────────


async def test_get_ingresos_requiere_rol_administrador(engine):
    async with _api_client(engine, seed_empleado_rol="operador") as client:
        resp = await client.get(
            _INGRESOS_PATH, params={"corpus_case_id": "CASO-X"}
        )
    assert resp.status_code == 403, resp.text


async def test_get_ingresos_sin_empleado_vinculado_403(engine):
    async with _api_client(engine) as client:
        resp = await client.get(
            _INGRESOS_PATH, params={"corpus_case_id": "CASO-X"}
        )
    assert resp.status_code == 403, resp.text


# ── 3.5 RED — Borrado acotado ───────────────────────────────────────────────


async def test_delete_dry_run_por_defecto_no_borra(engine):
    primer_inc = await _seed_incidente(
        engine, ingresado_en=_NOW, persistido_en=_NOW + timedelta(seconds=1)
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-DEL-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-DEL",
        incidente_id=primer_inc,
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-DEL-2",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-DEL",
    )

    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.delete(
            _INGRESOS_PATH, params={"corpus_case_id": "CASO-DEL"}
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["dry_run"] is True
    assert body["ingresos_eliminados"] == 1
    # Nada se borro: ambas filas siguen.
    assert await _get_ingreso(engine, "CA-DEL-1") is not None
    assert await _get_ingreso(engine, "CA-DEL-2") is not None
    assert await _get_incidente(engine, primer_inc) is not None


async def test_delete_marca_dry_run_no_dry_run(engine):
    await _seed_ingreso(
        engine,
        call_sid="CA-DEL-ONLY",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-ONLY",
    )
    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.delete(
            _INGRESOS_PATH,
            params={"corpus_case_id": "CASO-ONLY", "dry_run": "false"},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["dry_run"] is False
    # El ultimo (unico) ingreso se conserva.
    assert await _get_ingreso(engine, "CA-DEL-ONLY") is not None


# ── 3.7 TRIANGULATE — Orden FK y aislamiento por caso ───────────────────────


async def test_delete_conserva_el_ultimo_y_borra_previos_con_cascada(engine):
    inc_1 = await _seed_incidente(
        engine, ingresado_en=_NOW, persistido_en=_NOW + timedelta(seconds=1)
    )
    inc_2 = await _seed_incidente(
        engine, ingresado_en=_NOW, persistido_en=_NOW + timedelta(seconds=1)
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-REPL-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-REPL",
        incidente_id=inc_1,
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-REPL-2",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-REPL",
        incidente_id=inc_2,
    )

    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.delete(
            _INGRESOS_PATH,
            params={"corpus_case_id": "CASO-REPL", "dry_run": "false"},
        )

    assert resp.status_code == 200, resp.text
    assert resp.json()["ingresos_eliminados"] == 1
    assert resp.json()["incidentes_eliminados"] == 1
    # Se conserva el ultimo (CA-REPL-2) y su incidente.
    assert await _get_ingreso(engine, "CA-REPL-2") is not None
    assert await _get_incidente(engine, inc_2) is not None
    # Se elimino el previo, su incidente y sus clasificacion_log (CASCADE).
    assert await _get_ingreso(engine, "CA-REPL-1") is None
    assert await _get_incidente(engine, inc_1) is None
    assert await _count_logs(engine, inc_1) == []


async def test_delete_no_afecta_otros_corpus_case_id(engine):
    await _seed_ingreso(
        engine,
        call_sid="CA-OTRO-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-OTRO-DEL",
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-MIO-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-MIO-DEL",
    )
    await _seed_ingreso(
        engine,
        call_sid="CA-MIO-2",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-MIO-DEL",
    )

    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.delete(
            _INGRESOS_PATH,
            params={"corpus_case_id": "CASO-MIO-DEL", "dry_run": "false"},
        )

    assert resp.status_code == 200, resp.text
    assert await _get_ingreso(engine, "CA-OTRO-1") is not None
    assert await _get_ingreso(engine, "CA-MIO-2") is not None
    assert await _get_ingreso(engine, "CA-MIO-1") is None


async def test_delete_caso_inexistente_es_noop(engine):
    async with _api_client(
        engine, seed_empleado_rol="administrador_directorio"
    ) as client:
        resp = await client.delete(
            _INGRESOS_PATH,
            params={"corpus_case_id": "CASO-INEXISTENTE", "dry_run": "false"},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ingresos_eliminados"] == 0
    assert resp.json()["incidentes_eliminados"] == 0


# ── 9.2 RED — El alta del incidente enlaza el ingreso (fix post-smoke) ───────
#
# El smoke real revelo que `telefonia_ingreso.incidente_id` quedaba NULL porque
# `link_incidente` nunca se llamaba; el endpoint de lectura derivaba la latencia
# del incidente vinculado (FK) y devolvia `None`. Estos tests cierran el gap.


def _result_telefonia():
    from app.schemas.clasificacion import ClasificacionResult

    return ClasificacionResult(
        sector_predicho="Sistemas",
        sectores_adicionales=[],
        confianza=0.9,
        etapa="deterministic",
        requiere_revision_humana=False,
        respuesta_raw=None,
    )


def _payload_telefonico(origen_message_id: str) -> dict:
    return {
        "descripcion": "Falla reportada por un cliente durante la llamada telefonica.",
        "prioridad": "media",
        "origen_message_id": origen_message_id,
        "ingresado_en": (
            datetime.now(timezone.utc) - timedelta(seconds=17)
        ).isoformat(),
    }


async def _seed_estado_nuevo(engine):
    from app.models.catalog import Estado

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        existente = (
            await session.execute(select(Estado).where(Estado.nombre == "nuevo"))
        ).scalar_one_or_none()
        if existente is None:
            session.add(
                Estado(nombre="nuevo", descripcion="recibido", es_terminal=False)
            )
            await session.commit()


async def test_alta_incidente_telefonico_enlaza_ingreso_y_endpoint_devuelve_latencia(
    engine,
):
    """Crear el incidente con `origen_message_id = call_sid` enlaza el ingreso y
    la lectura del corpus pasa a devolver `latencia_e2e_ms` no nula."""
    await _seed_estado_nuevo(engine)
    ingreso = await _seed_ingreso(
        engine,
        call_sid="CA-LINK-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-LINK",
    )
    assert ingreso.incidente_id is None

    async with _api_client(
        engine,
        seed_empleado_rol="administrador_directorio",
        incidente_result=_result_telefonia(),
    ) as client:
        resp = await client.post(
            "/api/v1/incidentes/", json=_payload_telefonico("CA-LINK-1")
        )
        assert resp.status_code == 201, resp.text
        inc_id = resp.json()["id"]

        enlazado = await _get_ingreso(engine, "CA-LINK-1")
        assert enlazado.incidente_id == inc_id

        read = await client.get(
            _INGRESOS_PATH,
            params={"corpus_case_id": "CASO-LINK", "latest": "true"},
        )

    assert read.status_code == 200, read.text
    body = read.json()
    assert body["incidente_id"] == inc_id
    assert body["latencia_e2e_ms"] is not None
    assert body["latencia_e2e_ms"] > 0


async def test_alta_sin_ingreso_coincidente_es_noop(engine):
    """El alta generica (o de otro canal) no crea ni modifica ingresos."""
    await _seed_estado_nuevo(engine)
    async with _api_client(engine, incidente_result=_result_telefonia()) as client:
        resp = await client.post(
            "/api/v1/incidentes/", json=_payload_telefonico("CA-NO-INGRESO")
        )
    assert resp.status_code == 201, resp.text
    assert await _get_ingreso(engine, "CA-NO-INGRESO") is None


async def test_alta_no_toca_ingreso_de_otro_call_sid(engine):
    """Un ingreso con otro `call_sid` queda intacto."""
    await _seed_estado_nuevo(engine)
    await _seed_ingreso(
        engine,
        call_sid="CA-OTRO-SID",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-OTRO-SID",
    )
    async with _api_client(engine, incidente_result=_result_telefonia()) as client:
        resp = await client.post(
            "/api/v1/incidentes/", json=_payload_telefonico("CA-DISTINTO")
        )
    assert resp.status_code == 201, resp.text
    otro = await _get_ingreso(engine, "CA-OTRO-SID")
    assert otro.incidente_id is None


async def test_replay_idempotente_enlaza_ingreso_no_enlazado(engine):
    """Auto-sanado: un reintento sobre un ingreso sin enlace lo vincula."""
    await _seed_estado_nuevo(engine)
    payload = _payload_telefonico("CA-HEAL-1")
    async with _api_client(engine, incidente_result=_result_telefonia()) as client:
        primera = await client.post("/api/v1/incidentes/", json=payload)
        assert primera.status_code == 201, primera.text
        inc_id = primera.json()["id"]

        # El ingreso aparece DESPUES del alta y sin enlace (auto-sanado).
        await _seed_ingreso(
            engine,
            call_sid="CA-HEAL-1",
            transcripcion_estado="transcrito",
            corpus_case_id="CASO-HEAL",
        )
        assert (await _get_ingreso(engine, "CA-HEAL-1")).incidente_id is None

        replay = await client.post("/api/v1/incidentes/", json=payload)
        assert replay.status_code == 201, replay.text
        assert replay.json()["id"] == inc_id

    assert (await _get_ingreso(engine, "CA-HEAL-1")).incidente_id == inc_id
