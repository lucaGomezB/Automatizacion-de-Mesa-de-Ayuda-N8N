"""
Tests unitarios de las utilidades de calendario de negocio (UTC-3).

Cubre app/utils/business_time.py: la resolucion del dia calendario de negocio
(America/Argentina/Buenos_Aires) y su conversion a los limites UTC
inclusivo/exclusivo que consumen las consultas de estadisticas.

Estrategia TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import date, datetime, timezone

from app.utils.business_time import (
    BUSINESS_TZ,
    business_range_to_utc,
    business_today,
)


def test_business_today_early_utc_morning_belongs_to_previous_business_day():
    """
    RED: 01:00 UTC del 17-09 es 22:00 del 16-09 en Buenos Aires (UTC-3).

    El dia de negocio debe ser el 16, no el 17: la fecha UTC ya adelanto un
    dia pero la jornada laboral argentina sigue siendo la del 16.
    """
    now = datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc)
    assert business_today(now=now) == date(2026, 9, 16)


def test_business_today_afternoon_utc_matches_business_day():
    """
    RED (caso coincidente): 15:00 UTC del 17-09 es 12:00 del 17-09 en BA.
    """
    now = datetime(2026, 9, 17, 15, 0, tzinfo=timezone.utc)
    assert business_today(now=now) == date(2026, 9, 17)


def test_business_today_uses_business_timezone():
    """La zona de negocio es explicitamente America/Argentina/Buenos_Aires."""
    assert str(BUSINESS_TZ) == "America/Argentina/Buenos_Aires"


def test_business_range_to_utc_single_day_is_half_open():
    """
    RED: un dia de negocio se traduce a [00:00 BA, 00:00 BA del dia siguiente).

    El limite inferior es inclusivo y el superior es EXCLUSIVO, expresados
    como instantes UTC.
    """
    lower, upper = business_range_to_utc(date(2026, 9, 16), date(2026, 9, 16))

    assert lower == datetime(2026, 9, 16, 3, 0, tzinfo=timezone.utc)
    assert upper == datetime(2026, 9, 17, 3, 0, tzinfo=timezone.utc)

    # Instante de la ventana 21:00-24:00 BA: cae DENTRO del dia 16.
    inside = datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc)
    # Primer instante del dia 17 en BA: queda EXCLUIDO del dia 16.
    boundary = datetime(2026, 9, 17, 3, 0, tzinfo=timezone.utc)

    assert lower <= inside < upper
    assert not (lower <= boundary < upper)


def test_business_range_to_utc_crosses_year_boundary():
    """
    TRIANGULATE: 31-12-2025 (un solo dia) termina en 01-01-2026 03:00 UTC.
    """
    lower, upper = business_range_to_utc(date(2025, 12, 31), date(2025, 12, 31))

    assert lower == datetime(2025, 12, 31, 3, 0, tzinfo=timezone.utc)
    assert upper == datetime(2026, 1, 1, 3, 0, tzinfo=timezone.utc)
