"""
Tests del modulo `app.services.intervencion_estado` (c-165, ASG-005 y ECM-003).

Hoy cubren `a_utc` (tarea 2.5: el inicio declarado se normaliza a UTC antes de
persistir, porque SQLite descarta la zona de `DateTime(timezone=True)`). La tarea 2.9
agrega aca la funcion pura de estado y los predicados SQL.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.intervencion_estado import a_utc

ARGENTINA = timezone(timedelta(hours=-3))


def test_a_utc_convierte_un_instante_con_otra_zona():
    instante = datetime(2026, 10, 30, 12, 0, tzinfo=ARGENTINA)

    resultado = a_utc(instante)

    assert resultado == datetime(2026, 10, 30, 15, 0, tzinfo=timezone.utc)
    assert resultado.utcoffset() == timedelta(0)


def test_a_utc_conserva_un_instante_que_ya_esta_en_utc():
    instante = datetime(2026, 10, 30, 15, 0, tzinfo=timezone.utc)

    assert a_utc(instante) == instante
    assert a_utc(instante).utcoffset() == timedelta(0)


def test_a_utc_interpreta_un_instante_sin_zona_como_utc():
    """Las columnas almacenan UTC: un valor leido de SQLite (sin zona) ya es UTC."""
    assert a_utc(datetime(2026, 10, 30, 15, 0)) == datetime(
        2026, 10, 30, 15, 0, tzinfo=timezone.utc
    )


def test_a_utc_deja_pasar_none():
    assert a_utc(None) is None


@pytest.mark.parametrize("valor", ["2026-10-30T15:00:00Z", 1761836400])
def test_a_utc_rechaza_lo_que_no_es_un_instante(valor):
    with pytest.raises(TypeError):
        a_utc(valor)
