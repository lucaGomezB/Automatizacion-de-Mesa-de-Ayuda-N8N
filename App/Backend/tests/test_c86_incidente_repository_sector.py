"""Tests del filtrado server-side del alcance SECTOR (c-86, VIS-007/D3).

El repositorio debe devolver, para el sector S, los incidentes cuyo CONJUNTO de
sectores incluye S, que NO estan globalmente cerrados y que NO tienen un cierre
por sector para S. El filtro es server-side y reusable por listado, acceso
puntual e historial.
"""

from datetime import datetime, timezone

import pytest

from app.models.catalog import Estado, Sector
from app.models.incidente import (
    Incidente,
    IncidenteCierreSector,
    PrioridadEnum,
)
from app.models.empleado import Empleado, RolEmpleado
from app.repositories.incidente_repository import IncidenteRepository


@pytest.fixture
async def sector_env(db_session):
    """Crea sectores, estados y cinco incidentes que ejercen el filtro SECTOR."""
    a = Sector(nombre="Sistemas", descripcion="A")
    b = Sector(nombre="Bases de Datos", descripcion="B")
    c = Sector(nombre="Soporte Tecnico Software", descripcion="C")
    estado_activo = Estado(nombre="nuevo", descripcion="activo", es_terminal=False)
    estado_cerrado = Estado(nombre="cerrado", descripcion="terminal", es_terminal=True)
    db_session.add_all([a, b, c, estado_activo, estado_cerrado])
    await db_session.flush()

    actor = Empleado(
        legajo="G-1",
        nombre="Gestion",
        email="g1@example.test",
        sector_id=a.id,
        rol=RolEmpleado.gestion_incidentes,
    )
    db_session.add(actor)
    await db_session.flush()

    base = dict(
        descripcion_original="incidente",
        descripcion_pseudonimizada="incidente",
        prioridad=PrioridadEnum.media,
    )

    # i1: sector principal A (activo).
    i1 = Incidente(**base, estado_id=estado_activo.id, sector_id=a.id)
    # i2: sector principal B, A como adicional (activo).
    i2 = Incidente(
        **base, estado_id=estado_activo.id, sector_id=b.id, sectores_adicionales=[a]
    )
    # i3: sector principal C (no incluye A).
    i3 = Incidente(**base, estado_id=estado_activo.id, sector_id=c.id)
    # i4: sector principal A pero globalmente cerrado.
    i4 = Incidente(**base, estado_id=estado_cerrado.id, sector_id=a.id)
    # i5: sector principal A, activo pero con cierre por sector A.
    i5 = Incidente(**base, estado_id=estado_activo.id, sector_id=a.id)
    # i6: sin sector (no pertenece a A).
    i6 = Incidente(**base, estado_id=estado_activo.id, sector_id=None)
    db_session.add_all([i1, i2, i3, i4, i5, i6])
    await db_session.flush()

    db_session.add(
        IncidenteCierreSector(
            incidente_id=i5.id,
            sector_id=a.id,
            cerrado_por=actor.id,
            cerrado_en=datetime.now(timezone.utc),
        )
    )
    await db_session.flush()

    return {
        "sector_a": a.id,
        "sector_b": b.id,
        "sector_c": c.id,
        "i1": i1.id,
        "i2": i2.id,
        "i3": i3.id,
        "i4": i4.id,
        "i5": i5.id,
        "i6": i6.id,
    }


@pytest.mark.asyncio
async def test_filtro_sector_incluye_principal_y_adicional(db_session, sector_env):
    """El sector S ve los incidentes con S en principal o adicionales."""
    repo = IncidenteRepository(db_session)
    visibles = await repo.list_filtered(
        sector_scope_id=sector_env["sector_a"], limit=100
    )
    ids = {i.id for i in visibles}
    assert sector_env["i1"] in ids  # por principal
    assert sector_env["i2"] in ids  # por adicional


@pytest.mark.asyncio
async def test_filtro_sector_excluye_otros_sectores(db_session, sector_env):
    """El sector S no ve incidentes cuyo conjunto no incluye S."""
    repo = IncidenteRepository(db_session)
    visibles = await repo.list_filtered(
        sector_scope_id=sector_env["sector_a"], limit=100
    )
    ids = {i.id for i in visibles}
    assert sector_env["i3"] not in ids
    assert sector_env["i6"] not in ids


@pytest.mark.asyncio
async def test_filtro_sector_excluye_globalmente_cerrados(db_session, sector_env):
    """Un incidente en estado terminal no aparece en la vista activa del sector."""
    repo = IncidenteRepository(db_session)
    visibles = await repo.list_filtered(
        sector_scope_id=sector_env["sector_a"], limit=100
    )
    ids = {i.id for i in visibles}
    assert sector_env["i4"] not in ids


@pytest.mark.asyncio
async def test_filtro_sector_excluye_cerrados_para_el_sector(db_session, sector_env):
    """Un cierre por sector para S retira el incidente de la vista activa de S."""
    repo = IncidenteRepository(db_session)
    visibles = await repo.list_filtered(
        sector_scope_id=sector_env["sector_a"], limit=100
    )
    ids = {i.id for i in visibles}
    assert sector_env["i5"] not in ids
    assert ids == {sector_env["i1"], sector_env["i2"]}


@pytest.mark.asyncio
async def test_sin_filtro_sector_no_acota(db_session, sector_env):
    """Sin `sector_scope_id` no se aplica el filtro (alcances PROPIO/GLOBAL)."""
    repo = IncidenteRepository(db_session)
    visibles = await repo.list_filtered(limit=100)
    ids = {i.id for i in visibles}
    assert {sector_env[k] for k in ("i1", "i2", "i3", "i4", "i5", "i6")} <= ids
