"""Tests del servicio de borrado logico de incidentes (c-87, SD-001/SD-002).

Cubren, en RED -> GREEN -> TRIANGULATE:
    - Un incidente visible y activo se marca con el actor y un instante no nulo.
    - Un incidente inexistente, ya borrado o fuera de alcance lanza
      `EntityNotFoundError` (semantica 404), sin modificar filas.
    - La operacion NO borra fisicamente; un segundo borrado se comporta como no
      encontrado.
"""

from datetime import datetime, timezone

import pytest

from app.core.exceptions import EntityNotFoundError
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.incidente_repository import IncidenteRepository
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance
from app.services.incidente_service import IncidenteService


async def _seed(db_session):
    activo = Estado(nombre="nuevo", descripcion="activo", es_terminal=False)
    sector = Sector(nombre="Sistemas", descripcion="A")
    db_session.add_all([activo, sector])
    await db_session.flush()

    actor = Empleado(
        legajo="C87-S1",
        nombre="Actor",
        email="actor.svc.c87@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.administrador_directorio,
    )
    otro = Empleado(
        legajo="C87-S2",
        nombre="Otro",
        email="otro.svc.c87@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.usuario_final,
    )
    db_session.add_all([actor, otro])
    await db_session.flush()
    return {"activo": activo, "sector": sector, "actor": actor, "otro": otro}


async def _crear_incidente(db_session, env, **kwargs) -> Incidente:
    repo = IncidenteRepository(db_session)
    return await repo.create(
        estado_id=env["activo"].id,
        descripcion_original="incidente",
        descripcion_pseudonimizada="incidente",
        prioridad=PrioridadEnum.media,
        **kwargs,
    )


@pytest.mark.asyncio
async def test_soft_delete_marca_fila_y_atribuye_actor(db_session):
    """Un incidente visible se marca con `deleted_at` no nulo y el actor."""
    env = await _seed(db_session)
    inc = await _crear_incidente(db_session, env)
    service = IncidenteService(db_session)

    await service.soft_delete_incidente(
        inc.id,
        actor_empleado_id=env["actor"].id,
        alcance=AlcanceIncidentes(ModoAlcance.GLOBAL),
    )

    fila = await db_session.get(Incidente, inc.id)
    assert fila is not None
    assert fila.deleted_at is not None
    assert fila.deleted_by == env["actor"].id


@pytest.mark.asyncio
async def test_soft_delete_inexistente_lanza_not_found(db_session):
    """Un incidente inexistente lanza `EntityNotFoundError`."""
    env = await _seed(db_session)
    service = IncidenteService(db_session)

    with pytest.raises(EntityNotFoundError):
        await service.soft_delete_incidente(
            999_999,
            actor_empleado_id=env["actor"].id,
            alcance=AlcanceIncidentes(ModoAlcance.GLOBAL),
        )


@pytest.mark.asyncio
async def test_soft_delete_fuera_de_alcance_lanza_not_found(db_session):
    """Un incidente fuera del alcance del llamante se comporta como no encontrado."""
    env = await _seed(db_session)
    # Incidente reportado por OTRO empleado: fuera del alcance PROPIO del actor.
    inc = await _crear_incidente(
        db_session, env, reportante_empleado_id=env["otro"].id
    )
    service = IncidenteService(db_session)
    alcance_propio = AlcanceIncidentes(
        ModoAlcance.PROPIO, reportante_empleado_id=env["actor"].id
    )

    with pytest.raises(EntityNotFoundError):
        await service.soft_delete_incidente(
            inc.id, actor_empleado_id=env["actor"].id, alcance=alcance_propio
        )

    fila = await db_session.get(Incidente, inc.id)
    assert fila.deleted_at is None  # no se modifico


@pytest.mark.asyncio
async def test_soft_delete_no_borra_fisicamente(db_session):
    """La fila persiste con `deleted_at` no nulo (no es borrado fisico)."""
    env = await _seed(db_session)
    inc = await _crear_incidente(db_session, env)
    service = IncidenteService(db_session)

    await service.soft_delete_incidente(
        inc.id,
        actor_empleado_id=env["actor"].id,
        alcance=AlcanceIncidentes(ModoAlcance.GLOBAL),
    )

    assert await db_session.get(Incidente, inc.id) is not None


@pytest.mark.asyncio
async def test_segundo_borrado_se_comporta_como_no_encontrado(db_session):
    """Tras borrar, un segundo borrado lanza `EntityNotFoundError`."""
    env = await _seed(db_session)
    inc = await _crear_incidente(db_session, env)
    service = IncidenteService(db_session)
    alcance = AlcanceIncidentes(ModoAlcance.GLOBAL)

    await service.soft_delete_incidente(
        inc.id, actor_empleado_id=env["actor"].id, alcance=alcance
    )
    marca_original = (await db_session.get(Incidente, inc.id)).deleted_at

    with pytest.raises(EntityNotFoundError):
        await service.soft_delete_incidente(
            inc.id, actor_empleado_id=env["actor"].id, alcance=alcance
        )

    # El marcador existente no se altera.
    fila = await db_session.get(Incidente, inc.id)
    assert fila.deleted_at == marca_original
    assert datetime is not None and timezone is not None
