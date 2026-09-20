"""
Tests de servicio del sello temporal end-to-end (C-39, tareas 3.1-3.4).

Cubre `IncidenteService`:
    - `create_and_classify` sella `persistido_en` (no nulo) y persiste el
      `ingresado_en` provisto por el payload, normalizado a UTC.
    - Un PATCH posterior (`update_incidente`) recalcula `updated_at` pero NO
      modifica `persistido_en` (inmutabilidad de la persistencia confirmada).
    - Un replay idempotente por `origen_message_id` devuelve la fila existente
      con sus instantes ORIGINALES y no crea una segunda fila.

Estrategia: `db_session` (SQLite in-memory con rollback por test) + catalogo
sembrado en la misma sesion + clasificador doble (sin llamadas a Gemini). La
notificacion fire-and-forget a N8N se parchea con AsyncMock.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import func, select

from app.models.catalog import Estado, Sector
from app.models.incidente import Incidente
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import IncidenteCreate, IncidenteUpdate
from app.services.incidente_service import IncidenteService

_DESCRIPCION = "El servidor de base de datos principal no responde desde la manana."


def _as_utc(value: datetime) -> datetime:
    """Interpreta un datetime como UTC (SQLite devuelve naive tras el round-trip)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


async def _seed(session) -> None:
    """Siembra el catalogo minimo: estado 'nuevo' y sector 'Sistemas'."""
    session.add_all(
        [
            Estado(nombre="nuevo", descripcion="Incidente recibido", es_terminal=False),
            Estado(nombre="cerrado", descripcion="Finalizado", es_terminal=True),
            Sector(nombre="Sistemas", descripcion="Infraestructura y redes"),
        ]
    )
    await session.flush()


def _result() -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho="Sistemas",
        confianza=0.95,
        etapa="deterministic",
        requiere_revision_humana=False,
        respuesta_raw=None,
    )


def _service(session) -> IncidenteService:
    classifier = AsyncMock()
    classifier.classify = AsyncMock(return_value=_result())
    return IncidenteService(session, classifier=classifier)


async def _count_incidentes(session) -> int:
    return await session.scalar(select(func.count()).select_from(Incidente))


# ---------------------------------------------------------------------------
# Tarea 3.1 / 3.2 — sellado de persistido_en
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_classify_sella_persistido_en(db_session):
    """RED (3.1): tras el alta, `persistido_en` queda con un valor no nulo."""
    await _seed(db_session)
    service = _service(db_session)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        incidente = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION)
        )

    assert incidente.persistido_en is not None, (
        "create_and_classify debe sellar persistido_en (instante de persistencia)"
    )
    assert isinstance(incidente.persistido_en, datetime)


@pytest.mark.asyncio
async def test_create_and_classify_persiste_ingresado_en_normalizado(db_session):
    """El `ingresado_en` del payload se persiste normalizado a UTC."""
    await _seed(db_session)
    service = _service(db_session)
    ingresado = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        incidente = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION, ingresado_en=ingresado)
        )

    assert _as_utc(incidente.ingresado_en) == ingresado


@pytest.mark.asyncio
async def test_create_and_classify_sin_ingresado_deja_nulo(db_session):
    """Un alta sin `ingresado_en` persiste el instante nulo sin bloquearse."""
    await _seed(db_session)
    service = _service(db_session)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        incidente = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION)
        )

    assert incidente.ingresado_en is None
    assert incidente.persistido_en is not None


# ---------------------------------------------------------------------------
# Tarea 3.3 — inmutabilidad ante PATCH
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_modifica_updated_at_pero_no_persistido_en(db_session):
    """RED (3.3): un PATCH recalcula `updated_at` pero conserva `persistido_en`."""
    await _seed(db_session)
    service = _service(db_session)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        incidente = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION)
        )

    persistido_original = incidente.persistido_en
    updated_original = incidente.updated_at
    assert persistido_original is not None

    # Pequena espera para garantizar un `updated_at` posterior observable.
    import asyncio

    await asyncio.sleep(0.01)

    actualizado = await service.update_incidente(
        incidente.id, IncidenteUpdate(prioridad="critica")
    )

    assert _as_utc(actualizado.updated_at) > _as_utc(updated_original), (
        "El PATCH debe recalcular updated_at"
    )
    assert _as_utc(actualizado.persistido_en) == _as_utc(persistido_original), (
        "persistido_en debe ser inmutable: un PATCH no puede sobrescribirlo"
    )


# ---------------------------------------------------------------------------
# Tarea 3.4 — replay idempotente conserva la medicion
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replay_idempotente_conserva_instantes_y_no_crea_fila(db_session):
    """RED (3.4): un segundo alta con el mismo origen_message_id no re-mide."""
    await _seed(db_session)
    service = _service(db_session)
    ingresado = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)
    payload = IncidenteCreate(
        descripcion=_DESCRIPCION,
        ingresado_en=ingresado,
        origen_message_id="outlook-msg-timing-001",
    )

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        primera = await service.create_and_classify(payload)
        segunda = await service.create_and_classify(payload)

    assert primera.id == segunda.id, "El replay debe devolver el mismo incidente"
    assert segunda.ingresado_en == primera.ingresado_en, (
        "El replay no debe re-medir el ingreso"
    )
    assert segunda.persistido_en == primera.persistido_en, (
        "El replay no debe re-sellar la persistencia"
    )
    assert await _count_incidentes(db_session) == 1, (
        "El replay idempotente no debe crear una segunda fila"
    )


@pytest.mark.asyncio
async def test_alta_con_identificadores_distintos_crea_dos_filas(db_session):
    """TRIANGULATE (3.4): dos identificadores distintos producen dos filas."""
    await _seed(db_session)
    service = _service(db_session)

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        a = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION, origen_message_id="msg-a")
        )
        b = await service.create_and_classify(
            IncidenteCreate(descripcion=_DESCRIPCION, origen_message_id="msg-b")
        )

    assert a.id != b.id
    assert await _count_incidentes(db_session) == 2
