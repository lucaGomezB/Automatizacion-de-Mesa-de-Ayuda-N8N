"""
Tests de servicio: el rango por defecto del resumen respeta el dia de negocio.

Bug latente: entre las 21:00 y las 24:00 de Buenos Aires (UTC-3), la fecha UTC
ya pertenece al dia siguiente. Un incidente creado en esa ventana debe seguir
contando dentro del dia de negocio anterior. El servicio inyecta el reloj via
`now` para que el comportamiento sea determinista, independiente de la zona
horaria del servidor y del momento en que se ejecuta la suite.

Estrategia TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import date, datetime, timezone

import pytest

from app.models.incidente import Incidente
from app.services.estadisticas_service import EstadisticasService

# Instante del 16-09-2026 a las 22:00 en Buenos Aires (01:00 UTC del 17-09).
_MOMENTO = datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc)


def _incidente(estado_id: int, created_at: datetime) -> Incidente:
    """Construye un Incidente con una fecha de creacion UTC explicita."""
    return Incidente(
        descripcion_original="Falla nocturna en el servidor de base de datos.",
        descripcion_pseudonimizada="Falla nocturna en el servidor de base de datos.",
        prioridad="media",
        estado_id=estado_id,
        created_at=created_at,
    )


@pytest.mark.asyncio
async def test_resumen_default_range_includes_incident_from_previous_business_day(
    seed_catalogs, db_session
):
    """
    RED: `get_resumen()` por defecto incluye un incidente creado en la ventana
    21:00-24:00 BA, que en UTC pertenece al dia calendario siguiente.
    """
    db_session.add(_incidente(seed_catalogs["estado_nuevo"].id, _MOMENTO))
    await db_session.flush()

    service = EstadisticasService(db_session)
    data = await service.get_resumen(now=_MOMENTO)

    assert data["total_incidentes"] == 1


@pytest.mark.asyncio
async def test_resumen_explicit_range_uses_business_day_bounds(
    seed_catalogs, db_session
):
    """
    TRIANGULATE: con rango explicito 16-09 .. 16-09, un incidente a las 12:00
    UTC del 16-09 entra, y uno de las 01:00 UTC del 17-09 (01:00 BA del 17)
    queda fuera.
    """
    db_session.add(
        _incidente(
            seed_catalogs["estado_nuevo"].id,
            datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc),
        )
    )
    db_session.add(
        _incidente(
            seed_catalogs["estado_nuevo"].id,
            datetime(2026, 9, 17, 4, 0, tzinfo=timezone.utc),
        )
    )
    await db_session.flush()

    service = EstadisticasService(db_session)
    data = await service.get_resumen(
        desde=date(2026, 9, 16), hasta=date(2026, 9, 16)
    )

    assert data["total_incidentes"] == 1
