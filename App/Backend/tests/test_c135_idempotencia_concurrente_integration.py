"""
Idempotencia del alta bajo reintentos concurrentes (c-140, tarea 2.2/2.3).

Verifica contra PostgreSQL (la espera por bloqueo del indice UNIQUE no es
observable en SQLite) que un mismo `origen_message_id` produce, ante cualquier
entrelazado de intentos, exactamente una fila de `incidente` y exactamente un
registro de `clasificacion_log`, con el clasificador invocado una sola vez.

Requiere PostgreSQL alcanzable (subset `-m integration`). La base es la
descartable provisionada por la sesion; los identificadores de origen usan un
prefijo propio para no colisionar con otras corridas.

Marcadores del change: incident-origin-correlation (ADDED "Idempotencia del
alta bajo reintentos concurrentes" y "Trazabilidad de los replays del alta").
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog.testing import capture_logs

from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente
from app.schemas.clasificacion import ClasificacionResult

pytestmark = pytest.mark.integration

_DESCRIPCION = "Falla del servidor de base de datos principal del area contable."
_BASE_PAYLOAD = {"descripcion": _DESCRIPCION, "prioridad": "alta"}


def _result(
    sector_predicho: str = "Sistemas",
    confianza: float = 0.95,
    requiere_revision_humana: bool = False,
) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=requiere_revision_humana,
    )


def _slow_spy(result: ClasificacionResult, delay: float = 0.3) -> AsyncMock:
    """Doble del clasificador COMPARTIDO con una demora que fuerza el entrelazado.

    La demora ocurre DESPUES del flush del incidente (Paso 4) y antes del commit,
    de modo que la segunda insercion concurrente espera el lock del indice UNIQUE.
    """
    spy = AsyncMock()

    async def _classify(_texto: str):
        await asyncio.sleep(delay)
        return result

    spy.classify = AsyncMock(side_effect=_classify)
    return spy


async def _count_rows(engine, stmt) -> int:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return int((await session.scalar(stmt)) or 0)


async def _incidente_id(engine, origen_message_id: str) -> int | None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        return await session.scalar(
            select(Incidente.id).where(
                Incidente.origen_message_id == origen_message_id
            )
        )


# ── 2.2 CARACTERIZACION: dos altas concurrentes, mismo identificador ─────────


@pytest.mark.asyncio
async def test_c135_dos_altas_concurrentes_mismo_origen(
    seed_pg_catalogs, make_pg_client_with_classifier, pg_engine
):
    """Dos POST concurrentes con el mismo `origen_message_id`: una fila, un log.

    Ambas responden 201 con el mismo `id`, existe una sola fila de incidente y un
    solo registro de clasificacion, y el clasificador se invoca UNA sola vez.
    """
    result = _result()
    spy = _slow_spy(result)
    oid = "c135-carrera-dos"
    payload = {**_BASE_PAYLOAD, "origen_message_id": oid}

    async with make_pg_client_with_classifier(result, classifier=spy) as client:
        primera, segunda = await asyncio.gather(
            client.post("/api/v1/incidentes/", json=payload),
            client.post("/api/v1/incidentes/", json=payload),
        )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 201, segunda.text
    assert primera.json()["id"] == segunda.json()["id"], (
        "Las altas concurrentes con el mismo origen_message_id crearon incidentes "
        "distintos"
    )
    assert spy.classify.await_count == 1, (
        f"El clasificador se invoco {spy.classify.await_count} veces; la carrera "
        "debe clasificar una sola vez (costo pago)"
    )

    incidente_id = primera.json()["id"]
    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(Incidente)
            .where(Incidente.origen_message_id == oid),
        )
        == 1
    ), "Se duplico la fila de incidente"
    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(ClasificacionLog)
            .where(ClasificacionLog.incidente_id == incidente_id),
        )
        == 1
    ), "Se duplico el registro de clasificacion_log"


# ── 2.3 TRIANGULATE ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_c135_cinco_altas_concurrentes_una_fila(
    seed_pg_catalogs, make_pg_client_with_classifier, pg_engine
):
    """N=5 altas concurrentes con el mismo identificador -> exactamente una fila."""
    result = _result()
    spy = _slow_spy(result, delay=0.4)
    oid = "c135-carrera-cinco"
    payload = {**_BASE_PAYLOAD, "origen_message_id": oid}

    async with make_pg_client_with_classifier(result, classifier=spy) as client:
        respuestas = await asyncio.gather(
            *(client.post("/api/v1/incidentes/", json=payload) for _ in range(5))
        )

    for r in respuestas:
        assert r.status_code == 201, r.text
    ids = {r.json()["id"] for r in respuestas}
    assert len(ids) == 1, f"Se crearon varios incidentes: {ids}"
    assert spy.classify.await_count == 1
    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(Incidente)
            .where(Incidente.origen_message_id == oid),
        )
        == 1
    )


@pytest.mark.asyncio
async def test_c135_primer_intento_abortado_luego_reintento(
    seed_pg_catalogs, pg_engine
):
    """Un primer intento que revierte (el clasificador falla) se reintenta UNA vez.

    El primer intento aborta su transaccion (rollback por la excepcion del
    clasificador); el reintento posterior con el mismo identificador crea el
    incidente una sola vez. Se ejercita el servicio directamente para provocar el
    rollback de forma determinista (el transporte ASGI re-lanza excepciones).
    """
    from app.schemas.incidente import IncidenteCreate
    from app.services.incidente_service import IncidenteService

    result = _result()
    oid = "c135-carrera-abortado"

    class _SpyQueFalla:
        async def classify(self, _texto: str):
            raise RuntimeError("fallo transitorio del clasificador")

    class _SpyOk:
        async def classify(self, _texto: str):
            return result

    factory = async_sessionmaker(pg_engine, expire_on_commit=False)

    # Primer intento: inserta (flush) y luego falla al clasificar -> rollback.
    async with factory() as session:
        servicio = IncidenteService(session, classifier=_SpyQueFalla())
        with pytest.raises(RuntimeError):
            await servicio.create_and_classify(
                IncidenteCreate(
                    descripcion=_DESCRIPCION,
                    prioridad="alta",
                    origen_message_id=oid,
                )
            )
        await session.rollback()

    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(Incidente)
            .where(Incidente.origen_message_id == oid),
        )
        == 0
    ), "El intento abortado no debe dejar fila"

    # Reintento: crea el incidente una sola vez y lo clasifica.
    async with factory() as session:
        servicio = IncidenteService(session, classifier=_SpyOk())
        creado = await servicio.create_and_classify(
            IncidenteCreate(
                descripcion=_DESCRIPCION,
                prioridad="alta",
                origen_message_id=oid,
            )
        )
        await session.commit()
        creado_id = creado.id

    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(Incidente)
            .where(Incidente.origen_message_id == oid),
        )
        == 1
    ), "El reintento debe crear el incidente una sola vez"
    assert (
        await _count_rows(
            pg_engine,
            select(func.count())
            .select_from(ClasificacionLog)
            .where(ClasificacionLog.incidente_id == creado_id),
        )
        == 1
    )


@pytest.mark.asyncio
async def test_c135_replay_secuencial_mismo_id(
    seed_pg_catalogs, make_pg_client_with_classifier, pg_engine
):
    """Replay secuencial tras commit: mismo `id`, sin reclasificar."""
    result = _result()
    spy = _slow_spy(result, delay=0.0)
    oid = "c135-replay-secuencial"
    payload = {**_BASE_PAYLOAD, "origen_message_id": oid}

    async with make_pg_client_with_classifier(result, classifier=spy) as client:
        primera = await client.post("/api/v1/incidentes/", json=payload)
        segunda = await client.post("/api/v1/incidentes/", json=payload)

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 201, segunda.text
    assert primera.json()["id"] == segunda.json()["id"]
    assert spy.classify.await_count == 1


@pytest.mark.asyncio
async def test_c135_eventos_replay_sin_pii(
    seed_pg_catalogs, make_pg_client_with_classifier, pg_engine
):
    """Los dos caminos de replay emiten su evento con id, sin la descripcion."""
    result = _result()
    spy = _slow_spy(result, delay=0.3)
    oid_carrera = "c135-evento-carrera"
    oid_replay = "c135-evento-replay"
    payload_carrera = {**_BASE_PAYLOAD, "origen_message_id": oid_carrera}
    payload_replay = {**_BASE_PAYLOAD, "origen_message_id": oid_replay}

    async with make_pg_client_with_classifier(result, classifier=spy) as client:
        with capture_logs() as logs_carrera:
            await asyncio.gather(
                client.post("/api/v1/incidentes/", json=payload_carrera),
                client.post("/api/v1/incidentes/", json=payload_carrera),
            )
        # Alta + replay secuencial para el cortocircuito.
        await client.post("/api/v1/incidentes/", json=payload_replay)
        with capture_logs() as logs_replay:
            await client.post("/api/v1/incidentes/", json=payload_replay)

    eventos_carrera = [
        e for e in logs_carrera if e.get("event") == "incidente_idempotente_carrera"
    ]
    eventos_replay = [
        e for e in logs_replay if e.get("event") == "incidente_idempotente"
    ]
    assert eventos_carrera, "No se emitio incidente_idempotente_carrera en la carrera"
    assert eventos_replay, "No se emitio incidente_idempotente en el replay secuencial"

    evento = eventos_replay[-1]
    assert evento.get("origen_message_id") == oid_replay
    assert evento.get("incidente_id") is not None
    for logs in (logs_carrera, logs_replay):
        assert _DESCRIPCION not in repr(logs), "El evento de replay filtro PII"


# ── 2.6(d) TRIANGULATE: carrera CON revision -> mismos destinatarios ─────────


@pytest_asyncio.fixture
async def mesas_de_ayuda_pg(pg_engine, seed_pg_catalogs):
    """Siembra dos mesa_de_ayuda activos para resolver destinatarios en PG."""
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    legajos = ["C135-MDA-1", "C135-MDA-2"]
    async with factory() as session:
        session.add_all(
            [
                Empleado(
                    legajo="C135-MDA-1",
                    nombre="Mesa C135 Uno",
                    email="c135-mda-1@example.test",
                    rol=RolEmpleado.mesa_de_ayuda,
                    activo=True,
                ),
                Empleado(
                    legajo="C135-MDA-2",
                    nombre="Mesa C135 Dos",
                    email="c135-mda-2@example.test",
                    rol=RolEmpleado.mesa_de_ayuda,
                    activo=True,
                ),
            ]
        )
        await session.commit()
    yield
    async with factory() as session:
        await session.execute(delete(Empleado).where(Empleado.legajo.in_(legajos)))
        await session.commit()


@pytest.mark.asyncio
async def test_c135_carrera_con_revision_mismos_destinatarios(
    seed_pg_catalogs, mesas_de_ayuda_pg, make_pg_client_with_classifier, pg_engine
):
    """Carrera con revision: ambas respuestas traen los MISMOS destinatarios.

    El ganador resuelve los destinatarios al clasificar; el perdedor (rama
    IntegrityError) los re-resuelve por el camino de replay (c-140, D7), de modo
    que ambas respuestas son equivalentes para el orquestador.
    """
    result = _result(confianza=0.5, requiere_revision_humana=True)
    spy = _slow_spy(result)
    oid = "c135-carrera-revision"
    payload = {**_BASE_PAYLOAD, "origen_message_id": oid}

    async with make_pg_client_with_classifier(result, classifier=spy) as client:
        primera, segunda = await asyncio.gather(
            client.post("/api/v1/incidentes/", json=payload),
            client.post("/api/v1/incidentes/", json=payload),
        )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 201, segunda.text
    assert primera.json()["id"] == segunda.json()["id"]
    d1 = sorted(primera.json()["destinatarios_revision"])
    d2 = sorted(segunda.json()["destinatarios_revision"])
    assert d1 == d2, (
        f"Las respuestas de la carrera no coinciden en destinatarios: {d1} vs {d2}"
    )
    assert set(d1) >= {"c135-mda-1@example.test", "c135-mda-2@example.test"}
    assert spy.classify.await_count == 1
