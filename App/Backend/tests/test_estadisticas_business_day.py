"""
Tests de servicio: el rango por defecto del resumen respeta el dia de negocio.

Bug latente: entre las 21:00 y las 24:00 de Buenos Aires (UTC-3), la fecha UTC
ya pertenece al dia siguiente. Un incidente creado en esa ventana debe seguir
contando dentro del dia de negocio anterior. El servicio inyecta el reloj via
`now` para que el comportamiento sea determinista, independiente de la zona
horaria del servidor y del momento en que se ejecuta la suite.

Estrategia TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.

B5 (c-35): Grouping-label tests.
    The periodo label produced by _period_expression must reflect the
    Argentina business day (UTC-3), not the UTC date.  The three scenarios
    exercise:
      - Late-night Argentina (23:30 BA = 02:30 UTC next day) -> BA date, NOT UTC+1
      - Early UTC (01:00 UTC = 22:00 BA prev day) -> previous BA date
      - Midnight boundary in Argentina (00:00 BA = 03:00 UTC) -> NEW BA date
"""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select

from app.models.incidente import Incidente
from app.repositories.estadisticas_repository import EstadisticasRepository
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


# ═══════════════════════════════════════════════════════════════════════════════
# B5 (c-35): el rotulo de periodo sigue el dia de negocio argentino (UTC-3)
# ═══════════════════════════════════════════════════════════════════════════════


async def _add_incidente(
    db_session, estado_id: int, created_at: datetime
) -> int:
    """Inserta un incidente con fecha UTC explicita y devuelve su id."""
    incidente = _incidente(estado_id, created_at)
    db_session.add(incidente)
    await db_session.flush()
    return incidente.id


async def _periodo_label(
    db_session,
    incidente_id: int,
    *,
    agrupar_por: str = "dia",
    tz_offset_hours: int | None = None,
) -> str:
    """
    Evalua `_period_expression` contra SQLite para un incidente concreto.

    `tz_offset_hours` es la costura inyectable (D2): si es None se usa el
    default del repositorio; si se pasa, ejercita explicitamente el limite.
    """
    repo = EstadisticasRepository(db_session)
    if tz_offset_hours is None:
        expr = repo._period_expression(agrupar_por)
    else:
        expr = repo._period_expression(agrupar_por, tz_offset_hours=tz_offset_hours)
    result = await db_session.execute(
        select(expr).select_from(Incidente).where(Incidente.id == incidente_id)
    )
    return result.scalar_one()


@pytest.mark.asyncio
async def test_period_label_uses_argentina_date_for_late_night_utc(
    seed_catalogs, db_session
):
    """
    RED (B5): un incidente creado a las 23:30 BA del 16-09-2026 (02:30 UTC
    del 17-09) debe etiquetarse como 2026-09-16, NO como 2026-09-17 (fecha
    UTC).
    """
    incidente_id = await _add_incidente(
        db_session,
        seed_catalogs["estado_nuevo"].id,
        datetime(2026, 9, 17, 2, 30, tzinfo=timezone.utc),
    )

    label = await _periodo_label(db_session, incidente_id)

    assert label == "2026-09-16"


@pytest.mark.asyncio
async def test_period_label_midnight_argentina_is_day_D(
    seed_catalogs, db_session
):
    """
    TRIANGULATE (B5): la medianoche argentina exacta (00:00 BA = 03:00 UTC)
    del 16-09-2026 debe etiquetarse como 2026-09-16, de modo que el limite
    quede cerrado del lado correcto (no se corre al dia anterior). Se pasa
    `tz_offset_hours=-3` explicito para ejercitar la costura inyectable (D2).
    """
    incidente_id = await _add_incidente(
        db_session,
        seed_catalogs["estado_nuevo"].id,
        datetime(2026, 9, 16, 3, 0, tzinfo=timezone.utc),
    )

    label = await _periodo_label(db_session, incidente_id, tz_offset_hours=-3)

    assert label == "2026-09-16"


@pytest.mark.asyncio
async def test_period_label_groups_01utc_under_previous_argentina_date(
    seed_catalogs, db_session
):
    """
    RED (B5): un incidente creado a las 22:00 BA del 16-09-2026 (01:00 UTC
    del 17-09) debe etiquetarse como 2026-09-16 (dia de negocio argentino).
    """
    incidente_id = await _add_incidente(
        db_session,
        seed_catalogs["estado_nuevo"].id,
        datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc),
    )

    label = await _periodo_label(db_session, incidente_id)

    assert label == "2026-09-16"
