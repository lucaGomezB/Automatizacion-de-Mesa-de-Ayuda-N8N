"""Tests de auditoria del ciclo de vida (c-86, ILC-006 / D8).

Verifican que cada operacion de ciclo (cierre por sector, cierre global,
reapertura y cambio de estado) registra un `incidente_evento` con tipo, actor y
fecha; que la trazabilidad no contiene PII; que el borrado ARCO de un empleado
(SET NULL) preserva el evento sin PII; y que los reintentos idempotentes no
duplican eventos.
"""

import pytest
import pytest_asyncio
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, IncidenteEvento, PrioridadEnum
from app.services.ciclo_incidente_service import CicloIncidenteService
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance


@pytest_asyncio.fixture
async def auditoria_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        e_nuevo = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        e_proceso = Estado(nombre="en proceso", descripcion="p", es_terminal=False)
        e_espera = Estado(nombre="en espera", descripcion="e", es_terminal=False)
        e_cerrado = Estado(nombre="cerrado", descripcion="c", es_terminal=True)
        s.add_all([a, b, e_nuevo, e_proceso, e_espera, e_cerrado])
        await s.flush()

        gestion = Empleado(
            legajo="GA", nombre="Gestion A", email="ga@example.test",
            sector_id=a.id, rol=RolEmpleado.gestion_incidentes,
        )
        mesa = Empleado(
            legajo="MDA", nombre="Mesa", email="mda@example.test",
            sector_id=None, rol=RolEmpleado.mesa_de_ayuda,
        )
        s.add_all([gestion, mesa])
        await s.flush()

        incidente = Incidente(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
            estado_id=e_nuevo.id,
            sector_id=a.id,
        )
        s.add(incidente)
        await s.commit()

        ids = {
            "incidente": incidente.id,
            "sector_a": a.id,
            "gestion": gestion.id,
            "mesa": mesa.id,
        }

    yield ids

    async with factory() as s:
        await s.execute(delete(IncidenteEvento))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


def _alcance(env):
    return AlcanceIncidentes(ModoAlcance.SECTOR, sector_id=env["sector_a"])


async def _actor(session, empleado_id: int) -> Empleado:
    return await session.get(Empleado, empleado_id)


async def _eventos(session, incidente_id: int, tipo: str) -> list[IncidenteEvento]:
    return list(
        (
            await session.execute(
                select(IncidenteEvento).where(
                    IncidenteEvento.incidente_id == incidente_id,
                    IncidenteEvento.tipo == tipo,
                )
            )
        ).scalars().all()
    )


@pytest.mark.asyncio
async def test_cada_operacion_registra_evento_con_actor_y_fecha(engine, auditoria_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        gestion = await _actor(s, auditoria_env["gestion"])
        mesa = await _actor(s, auditoria_env["mesa"])

        await service.editar_estado(
            auditoria_env["incidente"], "en espera", gestion, _alcance(auditoria_env)
        )
        await service.cerrar_sector(
            auditoria_env["incidente"], gestion, _alcance(auditoria_env)
        )
        await service.rehabilitar(auditoria_env["incidente"], mesa)
        await service.cerrar_global(auditoria_env["incidente"], mesa)

        for tipo, actor_id in (
            ("cambio_estado", auditoria_env["gestion"]),
            ("cierre_sector", auditoria_env["gestion"]),
            ("reapertura", auditoria_env["mesa"]),
            ("cierre_global", auditoria_env["mesa"]),
        ):
            eventos = await _eventos(s, auditoria_env["incidente"], tipo)
            assert len(eventos) == 1, tipo
            assert eventos[0].actor_empleado_id == actor_id, tipo
            assert eventos[0].created_at is not None, tipo
        await s.rollback()


def test_evento_no_tiene_columnas_de_pii():
    """La trazabilidad usa identificadores internos, sin email ni telefono."""
    columnas = {c.name for c in IncidenteEvento.__table__.columns}
    assert columnas == {
        "id",
        "incidente_id",
        "tipo",
        "actor_empleado_id",
        "sector_id",
        "estado_anterior",
        "estado_nuevo",
        "created_at",
    }
    for prohibido in ("email", "telefono", "nombre"):
        assert prohibido not in columnas


@pytest.mark.asyncio
async def test_borrado_arco_preserva_evento_sin_pii(engine, auditoria_env):
    """El borrado ARCO del empleado (SET NULL) preserva el evento, sin PII."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        gestion = await _actor(s, auditoria_env["gestion"])
        await service.cerrar_sector(
            auditoria_env["incidente"], gestion, _alcance(auditoria_env)
        )
        # Borrado ARCO: se elimina fisicamente el empleado actor.
        await s.delete(gestion)
        await s.flush()

        evento = (await _eventos(s, auditoria_env["incidente"], "cierre_sector"))[0]
        assert evento.actor_empleado_id is None
        assert "email" not in repr(evento)
        await s.rollback()


@pytest.mark.asyncio
async def test_reintentos_idempotentes_no_duplican_eventos(engine, auditoria_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        gestion = await _actor(s, auditoria_env["gestion"])
        await service.cerrar_sector(
            auditoria_env["incidente"], gestion, _alcance(auditoria_env)
        )
        await service.cerrar_sector(
            auditoria_env["incidente"], gestion, _alcance(auditoria_env)
        )
        total = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteEvento)
                .where(
                    IncidenteEvento.incidente_id == auditoria_env["incidente"],
                    IncidenteEvento.tipo == "cierre_sector",
                )
            )
        ).scalar_one()
        assert total == 1
        await s.rollback()
