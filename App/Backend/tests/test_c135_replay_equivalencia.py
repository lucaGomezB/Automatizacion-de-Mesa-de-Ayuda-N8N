"""
Equivalencia observable de la respuesta de replay (c-140, tarea 2.4/2.6).

Un replay idempotente por `origen_message_id` debe ser observablemente
equivalente al alta original. En particular, si el incidente requiere revision
humana, la respuesta del replay debe re-resolver `destinatarios_revision` con la
misma lectura del alta original (hoy llega vacia y N8N cae al respaldo
`OPERATOR_EMAIL`).

Sin PII real: los emails usan el dominio reservado `example.test`.

Marcador del change: incident-origin-correlation (ADDED "Equivalencia
observable de la respuesta de replay").
"""

from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.empleado import Empleado, RolEmpleado
from app.schemas.clasificacion import ClasificacionResult

_DESCRIPCION = "Falla en el servidor de base de datos principal del sector contable."
_PAYLOAD = {"descripcion": _DESCRIPCION, "prioridad": "alta"}


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


@pytest_asyncio.fixture
async def mesas_de_ayuda(engine, seed_catalogs):
    """Siembra mesa_de_ayuda ACTIVOS y un reportante identificado por correo.

    El fixture replica el patron de `test_notification_recipients.py`: crea los
    destinatarios con el engine compartido (visible al cliente ASGI) y los limpia
    al finalizar.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    sector = seed_catalogs["sector_sistemas"]
    legajos = ["MDA-1", "MDA-2", "REP-ID"]
    async with factory() as session:
        session.add_all(
            [
                Empleado(
                    legajo="MDA-1", nombre="Mesa Uno", email="mda1@example.test",
                    sector_id=sector.id, rol=RolEmpleado.mesa_de_ayuda, activo=True,
                ),
                Empleado(
                    legajo="MDA-2", nombre="Mesa Dos", email="mda2@example.test",
                    sector_id=None, rol=RolEmpleado.mesa_de_ayuda, activo=True,
                ),
                Empleado(
                    legajo="REP-ID", nombre="Reportante Identificado",
                    email="rep-ident@example.test", sector_id=None,
                    rol=RolEmpleado.usuario_final, activo=True,
                ),
            ]
        )
        await session.commit()
    yield {"sector_sistemas": sector, "canal_correo": seed_catalogs["canal_correo"].id}
    async with factory() as session:
        await session.execute(delete(Empleado).where(Empleado.legajo.in_(legajos)))
        await session.commit()


# ── 2.4 RED: el replay re-resuelve los destinatarios de revision ─────────────


@pytest.mark.asyncio
async def test_c135_replay_con_revision_mismos_destinatarios(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """RED: la respuesta del replay trae los MISMOS destinatarios que el alta.

    Hoy el replay devuelve `destinatarios_revision = []`; el replay debe
    re-resolverlos igual que el alta original.
    """
    result = _result(confianza=0.5, requiere_revision_humana=True)
    payload = {**_PAYLOAD, "origen_message_id": "c135-replay-revision"}

    async with make_client_with_classifier(result) as client:
        alta = await client.post("/api/v1/incidentes/", json=payload)
        replay = await client.post("/api/v1/incidentes/", json=payload)

    assert alta.status_code == 201, alta.text
    assert replay.status_code == 201, replay.text
    assert alta.json()["id"] == replay.json()["id"]
    assert alta.json()["requiere_revision_humana"] is True
    assert sorted(alta.json()["destinatarios_revision"]) == [
        "mda1@example.test",
        "mda2@example.test",
    ]
    assert sorted(replay.json()["destinatarios_revision"]) == [
        "mda1@example.test",
        "mda2@example.test",
    ], "El replay no re-resolvio los destinatarios de revision"


# ── 2.6 TRIANGULATE ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_c135_replay_sin_revision_lista_vacia(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """TRIANGULATE (a): replay de un incidente sin revision -> lista vacia.

    Un incidente que no requiere revision (reportante identificado y clasificador
    sin revision) devuelve `destinatarios_revision` vacio tanto en el alta como en
    el replay, igual que el alta original.
    """
    result = _result(confianza=0.95, requiere_revision_humana=False)
    payload = {
        **_PAYLOAD,
        "origen_message_id": "c135-replay-sin-revision",
        "canal_origen_id": mesas_de_ayuda["canal_correo"],
        "reportante_email": "rep-ident@example.test",
    }

    async with make_client_with_classifier(result) as client:
        alta = await client.post("/api/v1/incidentes/", json=payload)
        replay = await client.post("/api/v1/incidentes/", json=payload)

    assert alta.status_code == 201, alta.text
    assert replay.status_code == 201, replay.text
    assert alta.json()["requiere_revision_humana"] is False
    assert alta.json()["destinatarios_revision"] == []
    assert replay.json()["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_c135_replay_directorio_vacio_lista_vacia_sin_excepcion(
    seed_catalogs, make_client_with_classifier
):
    """TRIANGULATE (b): replay con directorio vacio -> lista vacia, sin excepcion."""
    result = _result(confianza=0.5, requiere_revision_humana=True)
    payload = {**_PAYLOAD, "origen_message_id": "c135-replay-directorio-vacio"}

    async with make_client_with_classifier(result) as client:
        alta = await client.post("/api/v1/incidentes/", json=payload)
        replay = await client.post("/api/v1/incidentes/", json=payload)

    assert alta.status_code == 201, alta.text
    assert replay.status_code == 201, replay.text
    assert alta.json()["destinatarios_revision"] == []
    assert replay.json()["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_c135_replay_sin_efectos_laterales(
    seed_catalogs, mesas_de_ayuda, make_client_with_spy_classifier
):
    """TRIANGULATE (c): el replay no reclasifica ni re-despacha la notificacion."""
    result = _result(confianza=0.5, requiere_revision_humana=True)
    payload = {**_PAYLOAD, "origen_message_id": "c135-replay-sin-efectos"}

    async with make_client_with_spy_classifier(result) as (client, spy):
        alta = await client.post("/api/v1/incidentes/", json=payload)
        await asyncio.sleep(0)
        replay = await client.post("/api/v1/incidentes/", json=payload)
        await asyncio.sleep(0)

    assert alta.status_code == 201, alta.text
    assert replay.status_code == 201, replay.text
    assert spy.classify.await_count == 1, (
        "El replay no debe reclasificar (costo pago)"
    )
    assert spy.notify.await_count == 1, (
        "El replay no debe re-despachar la notificacion a N8N"
    )
