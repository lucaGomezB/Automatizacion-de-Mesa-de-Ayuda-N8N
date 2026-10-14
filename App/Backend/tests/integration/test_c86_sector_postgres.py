"""Integracion PostgreSQL del filtrado SECTOR (c-86, VIS-007/D3).

Requiere un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Verifica en el motor real el filtro server-side del alcance SECTOR con varios
sectores y cierres, incluido que un cierre por sector retira el incidente de la
vista activa de ESE sector sin afectar a los demas.
"""

from datetime import datetime, timezone

import pytest

from app.models.asociaciones import incidente_sector_adicional
from app.models.catalog import Estado
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import (
    Incidente,
    IncidenteCierreSector,
    PrioridadEnum,
)
from app.repositories.incidente_repository import IncidenteRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_filtro_sector_multisector_y_cierres_postgres(
    pg_session, seed_pg_catalogs
):
    """Con multiples sectores y cierres, la vista activa por sector es correcta."""
    cat = seed_pg_catalogs
    a = cat["sector_seguridad"]
    b = cat["sector_hardware"]
    c = cat["sector_sistemas"]
    estado_activo = cat["estado_nuevo"]

    estado_cerrado = Estado(
        nombre="cerrado-sec", descripcion="terminal", es_terminal=True
    )
    pg_session.add(estado_cerrado)
    await pg_session.flush()

    actor = Empleado(
        legajo="SEC-G",
        nombre="Gestion",
        email="sec.g@example.test",
        sector_id=a.id,
        rol=RolEmpleado.gestion_incidentes,
    )
    pg_session.add(actor)
    await pg_session.flush()

    base = dict(
        descripcion_original="incidente",
        descripcion_pseudonimizada="incidente",
        prioridad=PrioridadEnum.media,
    )
    ia = Incidente(**base, estado_id=estado_activo.id, sector_id=a.id)
    ib = Incidente(**base, estado_id=estado_activo.id, sector_id=b.id)
    iab = Incidente(**base, estado_id=estado_activo.id, sector_id=b.id)
    ic = Incidente(**base, estado_id=estado_activo.id, sector_id=c.id)
    i_closed = Incidente(**base, estado_id=estado_cerrado.id, sector_id=a.id)
    i_cierre_a = Incidente(**base, estado_id=estado_activo.id, sector_id=a.id)
    pg_session.add_all([ia, ib, iab, ic, i_closed, i_cierre_a])
    await pg_session.flush()

    # A como sector adicional de iab: se inserta la asociacion con Core para no
    # re-vincular el objeto `Sector` del fixture de catalogo (otra sesion).
    await pg_session.execute(
        incidente_sector_adicional.insert().values(
            incidente_id=iab.id, sector_id=a.id
        )
    )
    pg_session.add(
        IncidenteCierreSector(
            incidente_id=i_cierre_a.id,
            sector_id=a.id,
            cerrado_por=actor.id,
            cerrado_en=datetime.now(timezone.utc),
        )
    )
    await pg_session.flush()

    repo = IncidenteRepository(pg_session)

    vista_a = {i.id for i in await repo.list_filtered(sector_scope_id=a.id, limit=100)}
    assert vista_a == {ia.id, iab.id}

    vista_b = {i.id for i in await repo.list_filtered(sector_scope_id=b.id, limit=100)}
    assert vista_b == {ib.id, iab.id}

    vista_c = {i.id for i in await repo.list_filtered(sector_scope_id=c.id, limit=100)}
    assert vista_c == {ic.id}

    # El cierre por A retira i_cierre_a de la vista de A pero no afecta a nadie mas.
    assert i_cierre_a.id not in vista_a
    assert i_closed.id not in vista_a
    assert i_closed.id not in vista_b

    await pg_session.rollback()
