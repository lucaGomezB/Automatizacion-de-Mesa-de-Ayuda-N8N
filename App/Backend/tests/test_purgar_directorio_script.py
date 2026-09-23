"""
Tests del script CLI de purga por retencion (c-54, W2 / DIR-007).

El script `scripts/purgar_directorio.py` expone `purgar_directorio`, una funcion
testeable que delega en `DirectorioService.purgar_vencidos` y puede commitear.
Se ejecuta como `python -m scripts.purgar_directorio`.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.catalog import Sector
from app.repositories.empleado_repository import EmpleadoRepository
from app.services.directorio_service import DirectorioService
from scripts.purgar_directorio import purgar_directorio

_AHORA = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_purgar_directorio_borra_vencidos_y_conserva_activos(db_session):
    """El script elimina las bajas > 1 año y deja intactas las activas."""
    sector = Sector(nombre="Sistemas", descripcion="d")
    db_session.add(sector)
    await db_session.flush()

    svc = DirectorioService(db_session)
    activo = await svc.crear_empleado(
        legajo="CLI-ACT", nombre="N", email="cli.act@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    viejo = await svc.crear_empleado(
        legajo="CLI-VIE", nombre="N", email="cli.vie@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    await svc.desactivar_empleado(viejo.id)
    viejo.fecha_baja = _AHORA - timedelta(days=400)
    db_session.add(viejo)
    await db_session.flush()

    purgados = await purgar_directorio(db_session, ahora=_AHORA)

    assert purgados == 1
    assert (await svc.obtener(activo.id)).legajo == "CLI-ACT"
    assert await EmpleadoRepository(db_session).get_or_none(viejo.id) is None
