"""Pruebas de las metricas puras de calibracion y discriminacion del gate (c-214, tareas 1.x)."""

from __future__ import annotations

import pytest

from evaluation.calibracion_gate import (
    auroc,
    brier,
    ece,
    ic_bootstrap_metrica,
    sobreconfianza,
)


# --- AUROC ------------------------------------------------------------------------------
def test_auroc_orden_perfecto_es_uno():
    assert auroc([0.9, 0.95, 0.2, 0.1], [True, True, False, False]) == 1.0


def test_auroc_orden_invertido_es_cero():
    assert auroc([0.1, 0.2, 0.9], [True, True, False]) == 0.0


def test_auroc_senal_constante_es_medio():
    assert auroc([0.85] * 6, [True, False, True, False, True, True]) == 0.5


def test_auroc_empates_cuentan_medio():
    # aciertos: 0.9, 0.5 ; errores: 0.5, 0.1 -> pares: (0.9>0.5)=1, (0.9>0.1)=1,
    # (0.5=0.5)=0.5, (0.5>0.1)=1 -> 3.5/4
    assert auroc([0.9, 0.5, 0.5, 0.1], [True, True, False, False]) == pytest.approx(0.875)


def test_auroc_sin_una_clase_es_none():
    assert auroc([0.9, 0.8], [True, True]) is None
    assert auroc([0.9, 0.8], [False, False]) is None


# --- ECE / Brier / sobreconfianza -------------------------------------------------------
def test_ece_senal_calibrada_es_cero():
    # banda [0.9, 1.0]: confianza media 0.9, 9 aciertos de 10 -> exactitud 0.9
    confianzas = [0.9] * 10
    aciertos = [True] * 9 + [False]
    assert ece(confianzas, aciertos) == pytest.approx(0.0)


def test_ece_pondera_por_banda_con_diez_bandas_de_igual_ancho():
    # banda 0.8-0.9: confianza 0.85 x4, exactitud 0.5 -> |0.85-0.5| = 0.35, peso 4/5
    # banda 0.9-1.0 (cerrada en 1.0): confianza 1.0 x1, acierto -> 0
    confianzas = [0.85, 0.85, 0.85, 0.85, 1.0]
    aciertos = [True, True, False, False, True]
    assert ece(confianzas, aciertos) == pytest.approx(0.35 * 4 / 5)


def test_ece_confianza_uno_cae_en_la_ultima_banda():
    assert ece([1.0, 1.0], [True, False]) == pytest.approx(0.5)


def test_brier_valor_conocido():
    assert brier([1.0, 0.0], [True, False]) == pytest.approx(0.0)
    assert brier([0.8, 0.6], [True, False]) == pytest.approx((0.2**2 + 0.6**2) / 2)


def test_sobreconfianza_media():
    assert sobreconfianza([0.9, 0.9, 0.9, 0.9], [True, True, False, False]) == pytest.approx(0.4)
    assert sobreconfianza([0.5, 0.5], [True, True]) == pytest.approx(-0.5)


def test_metricas_rechazan_vacio_longitudes_distintas_y_fuera_de_rango():
    for funcion in (ece, brier, sobreconfianza, auroc):
        with pytest.raises(ValueError):
            funcion([], [])
        with pytest.raises(ValueError):
            funcion([0.5], [True, False])
        with pytest.raises(ValueError):
            funcion([1.2, 0.5], [True, False])
        with pytest.raises(ValueError):
            funcion([-0.1, 0.5], [True, False])


# --- IC bootstrap -----------------------------------------------------------------------
def test_ic_bootstrap_dos_corridas_dan_lo_mismo_y_contiene_el_valor():
    confianzas = [0.95, 0.9, 0.85, 0.85, 0.98, 0.9, 0.95, 0.85] * 3
    aciertos = [True, True, False, True, True, False, True, False] * 3
    a = ic_bootstrap_metrica(confianzas, aciertos, brier)
    b = ic_bootstrap_metrica(confianzas, aciertos, brier)
    assert a == b
    assert a["valor"] == pytest.approx(brier(confianzas, aciertos))
    inferior, superior = a["ic"]
    assert inferior <= a["valor"] <= superior
    assert superior - inferior > 0.0


def test_ic_bootstrap_distinta_semilla_cambia_el_intervalo():
    confianzas = [0.95, 0.9, 0.85, 0.85, 0.98, 0.9, 0.95, 0.85] * 3
    aciertos = [True, True, False, True, True, False, True, False] * 3
    a = ic_bootstrap_metrica(confianzas, aciertos, ece, semilla=1)
    b = ic_bootstrap_metrica(confianzas, aciertos, ece, semilla=2)
    assert a["ic"] != b["ic"]


def test_ic_bootstrap_auroc_omite_remuestras_sin_ambas_clases():
    confianzas = [0.9, 0.8, 0.3]
    aciertos = [True, True, False]
    r = ic_bootstrap_metrica(confianzas, aciertos, auroc, remuestreos=200)
    assert r["valor"] == 1.0
    assert r["remuestras_validas"] <= 200
    assert r["ic"] is not None


def test_ic_bootstrap_con_metrica_indefinida_devuelve_none():
    r = ic_bootstrap_metrica([0.9, 0.8], [True, True], auroc)
    assert r["valor"] is None and r["ic"] is None
