"""Tests del borrado logico y la exclusion en el repositorio (c-87, SD-001/VIS-009).

Cubren, en RED -> GREEN -> TRIANGULATE:
    - `soft_delete` marca la fila (`deleted_at`/`deleted_by`), no la elimina y
      devuelve 1 fila afectada.
    - La condicion por defecto `deleted_at IS NULL` excluye los borrados de
      `get_with_relations`, `list_filtered` y la consulta de historial (c-86).
    - Casos borde: incidente inexistente devuelve 0; un borrado no aparece en
      ningun filtro; un activo si aparece.
"""

from datetime import datetime, timezone

import pytest

from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.incidente_repository import IncidenteRepository


async def _seed(db_session):
    """Siembra un estado activo, uno terminal, un sector y un empleado actor."""
    activo = Estado(nombre="nuevo", descripcion="activo", es_terminal=False)
    cerrado = Estado(nombre="cerrado", descripcion="terminal", es_terminal=True)
    sector = Sector(nombre="Sistemas", descripcion="A")
    db_session.add_all([activo, cerrado, sector])
    await db_session.flush()

    actor = Empleado(
        legajo="C87-1",
        nombre="Actor",
        email="actor.c87@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.administrador_directorio,
    )
    db_session.add(actor)
    await db_session.flush()
    return {"activo": activo, "cerrado": cerrado, "sector": sector, "actor": actor}


def _base(**kwargs) -> dict:
    base = {
        "descripcion_original": "incidente",
        "descripcion_pseudonimizada": "incidente",
        "prioridad": PrioridadEnum.media,
    }
    base.update(kwargs)
    return base


# ── soft_delete ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_soft_delete_marca_fila_con_actor_y_no_la_elimina(db_session):
    """`soft_delete` setea los marcadores, devuelve 1 y conserva la fila."""
    env = await _seed(db_session)
    repo = IncidenteRepository(db_session)
    inc = await repo.create(estado_id=env["activo"].id, **_base())

    ahora = datetime.now(timezone.utc)
    afectadas = await repo.soft_delete(
        inc.id, deleted_by=env["actor"].id, deleted_at=ahora
    )

    assert afectadas == 1
    fila = await db_session.get(Incidente, inc.id)
    assert fila is not None  # la fila persiste (no es borrado fisico)
    assert fila.deleted_at is not None
    assert fila.deleted_by == env["actor"].id


@pytest.mark.asyncio
async def test_soft_delete_inexistente_devuelve_cero(db_session):
    """`soft_delete` sobre un id inexistente no afecta filas (devuelve 0)."""
    await _seed(db_session)
    repo = IncidenteRepository(db_session)

    afectadas = await repo.soft_delete(
        999_999, deleted_by=None, deleted_at=datetime.now(timezone.utc)
    )

    assert afectadas == 0


# ── Exclusion en las superficies de lectura ───────────────────────────────────


@pytest.mark.asyncio
async def test_get_with_relations_excluye_borrado(db_session):
    """`get_with_relations` no devuelve un incidente borrado."""
    env = await _seed(db_session)
    repo = IncidenteRepository(db_session)
    activo = await repo.create(estado_id=env["activo"].id, **_base())
    borrado = await repo.create(estado_id=env["activo"].id, **_base())

    await repo.soft_delete(
        borrado.id, deleted_by=env["actor"].id, deleted_at=datetime.now(timezone.utc)
    )

    assert await repo.get_with_relations(borrado.id) is None
    assert await repo.get_with_relations(activo.id) is not None


@pytest.mark.asyncio
async def test_list_filtered_excluye_borrado(db_session):
    """`list_filtered` no incluye el incidente borrado, si el activo."""
    env = await _seed(db_session)
    repo = IncidenteRepository(db_session)
    activo = await repo.create(estado_id=env["activo"].id, **_base())
    borrado = await repo.create(estado_id=env["activo"].id, **_base())

    await repo.soft_delete(
        borrado.id, deleted_by=env["actor"].id, deleted_at=datetime.now(timezone.utc)
    )

    ids = {i.id for i in await repo.list_filtered(limit=100)}
    assert borrado.id not in ids
    assert activo.id in ids


@pytest.mark.asyncio
async def test_list_filtered_excluye_borrado_en_cualquier_filtro(db_session):
    """Un borrado no aparece aun aplicando filtros combinados (sector/estado)."""
    env = await _seed(db_session)
    repo = IncidenteRepository(db_session)
    borrado = await repo.create(
        estado_id=env["activo"].id, sector_id=env["sector"].id, **_base()
    )
    await repo.soft_delete(
        borrado.id, deleted_by=env["actor"].id, deleted_at=datetime.now(timezone.utc)
    )

    por_sector = await repo.list_filtered(sector_id=env["sector"].id, limit=100)
    por_estado = await repo.list_filtered(estado_id=env["activo"].id, limit=100)

    assert borrado.id not in {i.id for i in por_sector}
    assert borrado.id not in {i.id for i in por_estado}


@pytest.mark.asyncio
async def test_list_historial_excluye_borrado(db_session):
    """La consulta de historial (c-86) no muestra un cerrado borrado."""
    env = await _seed(db_session)
    repo = IncidenteRepository(db_session)
    cerrado_activo = await repo.create(estado_id=env["cerrado"].id, **_base())
    cerrado_borrado = await repo.create(estado_id=env["cerrado"].id, **_base())

    await repo.soft_delete(
        cerrado_borrado.id,
        deleted_by=env["actor"].id,
        deleted_at=datetime.now(timezone.utc),
    )

    ids = {i.id for i in await repo.list_historial(limit=100)}
    assert cerrado_borrado.id not in ids
    assert cerrado_activo.id in ids
