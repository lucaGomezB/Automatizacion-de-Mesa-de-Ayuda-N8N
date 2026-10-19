"""
Tests de calibracion de la confianza (c-77, A6).

Strict TDD:
    RED  -> no existia funcion de calibracion por bandas ni de contingencia
            sobre la confianza del clasificador.
    GREEN -> `evaluation.metrics` expone `calibracion_por_bandas` y
             `contingencia_confianza`.

La calibracion contrasta la confianza declarada por el clasificador con su
exactitud real: un clasificador bien calibrado deberia ser mas exacto en las
bandas de confianza alta. El caso de este corpus es el opuesto (anti-calibrado).
"""

from __future__ import annotations

import pytest

from evaluation.metrics import (
    BANDAS_CALIBRACION_DEFECTO,
    calibracion_por_bandas,
    contingencia_confianza,
)


# ---------------------------------------------------------------------------
# Fixtures sinteticos: verdad simple (Sistemas vs Bases de Datos)
# ---------------------------------------------------------------------------
def _conjunto(confianzas, correctos):
    reales = ["Sistemas"] * len(confianzas)
    predichos = ["Sistemas" if c else "Bases de Datos" for c in correctos]
    return confianzas, reales, predichos


# ---------------------------------------------------------------------------
# Bandas
# ---------------------------------------------------------------------------
def test_bandas_por_defecto_cubren_el_intervalo_unidad():
    assert BANDAS_CALIBRACION_DEFECTO[0][0] == 0.0
    assert BANDAS_CALIBRACION_DEFECTO[-1][1] == 1.0
    for (lo_a, hi_a), (lo_b, hi_b) in zip(
        BANDAS_CALIBRACION_DEFECTO, BANDAS_CALIBRACION_DEFECTO[1:]
    ):
        assert hi_a == lo_b, "las bandas deben ser contiguas y sin solapamiento"


def test_calibracion_por_bandas_cuenta_aciertos_y_exactitud():
    confianzas = [0.2, 0.3, 0.8, 0.9, 0.97]
    correctos = [True, False, False, True, True]
    bandas = calibracion_por_bandas(*_conjunto(confianzas, correctos))

    por_limite = {b.limite_inferior: b for b in bandas}
    assert por_limite[0.0].total == 2 and por_limite[0.0].aciertos == 1
    assert por_limite[0.0].exactitud == pytest.approx(0.5)
    assert por_limite[0.7].total == 1 and por_limite[0.7].aciertos == 0
    assert por_limite[0.85].total == 1 and por_limite[0.85].aciertos == 1
    assert por_limite[0.95].total == 1 and por_limite[0.95].aciertos == 1


def test_calibracion_banda_superior_es_cerrada_en_uno():
    bandas = calibracion_por_bandas(*_conjunto([1.0], [True]))
    superior = bandas[-1]
    assert superior.total == 1 and superior.aciertos == 1


def test_calibracion_banda_vacia_tiene_exactitud_cero_sin_romper():
    bandas = calibracion_por_bandas(*_conjunto([0.1], [True]))
    vacias = [b for b in bandas if b.total == 0]
    assert vacias, "debe haber bandas vacias"
    assert all(b.exactitud == 0.0 for b in vacias)


# ---------------------------------------------------------------------------
# Contingencia en torno al umbral (gate 0,70)
# ---------------------------------------------------------------------------
def test_contingencia_separa_alta_y_baja_por_el_umbral():
    confianzas = [0.70, 0.95, 0.69, 0.2]
    correctos = [False, True, True, False]
    cont = contingencia_confianza(*_conjunto(confianzas, correctos), umbral=0.70)

    assert cont.alta_total == 2 and cont.alta_aciertos == 1
    assert cont.alta_exactitud == pytest.approx(0.5)
    assert cont.baja_total == 2 and cont.baja_aciertos == 1
    assert cont.baja_exactitud == pytest.approx(0.5)


def test_contingencia_umbral_es_inclusivo_en_la_confianza_alta():
    cont = contingencia_confianza(*_conjunto([0.70], [True]), umbral=0.70)
    assert cont.alta_total == 1
    assert cont.baja_total == 0


def test_contingencia_umbral_por_defecto_es_070():
    cont = contingencia_confianza(*_conjunto([0.70], [True]))
    assert cont.umbral == pytest.approx(0.70)
    assert cont.alta_total == 1
