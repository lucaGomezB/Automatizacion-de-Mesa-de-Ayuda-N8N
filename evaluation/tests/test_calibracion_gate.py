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


# ======================================================================================
# Grupo 2: barrido, regla de seleccion, evaluacion fuera de muestra, isotonica
# ======================================================================================
import math  # noqa: E402

from evaluation.calibracion_gate import (  # noqa: E402
    aplicar_isotonica,
    ajustar_isotonica,
    barrido_umbral,
    evaluar_fuera_de_muestra_gate,
    seleccionar_umbral,
)

INF = math.inf
SENALES = [0.85, 0.85, 0.85, 0.90, 0.90, 0.95, 0.95, 0.95, 0.95, 0.98]
ACIERTOS = [False, False, True, False, True, True, True, True, False, True]


def _fila(barrido, t):
    return next(f for f in barrido if f["umbral"] == t)


def test_barrido_umbral_vigente_sin_derivaciones():
    b = barrido_umbral(SENALES, ACIERTOS, [0.70, INF], n_total_corpus=20)
    f = _fila(b, 0.70)
    assert (f["aceptados"], f["derivados"]) == (10, 0)
    assert f["cobertura"] == 1.0
    assert f["errores_atrapados"] == 0
    assert f["carga_revision"] == 0.0
    assert f["exactitud_selectiva"] == pytest.approx(6 / 10)
    assert f["exactitud_derivados"] is None


def test_barrido_derivar_todo_tiene_cobertura_cero_y_carga_de_los_escalados():
    f = _fila(barrido_umbral(SENALES, ACIERTOS, [INF], n_total_corpus=20), INF)
    assert f["cobertura"] == 0.0
    assert f["aceptados"] == 0 and f["derivados"] == 10
    assert f["carga_revision"] == pytest.approx(10 / 20)
    assert f["errores_atrapados"] == 4
    assert f["exactitud_selectiva"] is None and f["ic_wilson"] is None


def test_barrido_umbral_intermedio_cuenta_aceptados_derivados_y_wilson():
    f = _fila(barrido_umbral(SENALES, ACIERTOS, [0.91], n_total_corpus=20), 0.91)
    # aceptados: 0.95 x4 y 0.98 -> 5 casos, aciertos 3+1 = 4
    assert (f["aceptados"], f["aciertos_aceptados"]) == (5, 4)
    assert f["exactitud_selectiva"] == pytest.approx(0.8)
    assert f["derivados"] == 5 and f["errores_atrapados"] == 3
    assert f["exactitud_derivados"] == pytest.approx(2 / 5)
    assert f["ic_wilson"][0] < 0.8 < f["ic_wilson"][1]
    assert f["carga_revision"] == pytest.approx(5 / 20)


def test_barrido_rechaza_senales_y_aciertos_de_distinta_longitud():
    with pytest.raises(ValueError):
        barrido_umbral([0.9], [True, False], [0.5], n_total_corpus=2)


def _barrido_sintetico():
    # t=0.5: 20 aceptados, exactitud 0.70 ; t=0.8: 12 aceptados, 0.90 ; t=0.9: 4 aceptados, 1.0
    senales = [0.5] * 8 + [0.8] * 8 + [0.9] * 4
    aciertos = [True] * 2 + [False] * 6 + [True] * 7 + [False] + [True] * 4
    return barrido_umbral(senales, aciertos, [0.5, 0.8, 0.9, INF], n_total_corpus=20)


def test_seleccionar_elige_el_menor_umbral_que_cumple_piso_y_minimo():
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.85, min_aceptados=10) == 0.8


def test_seleccionar_exige_el_minimo_de_aceptados():
    # con t=0.9 la exactitud es 1.0 pero solo hay 4 aceptados; con minimo 4 gana t=0.8 por menor
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.99, min_aceptados=10) is None
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.99, min_aceptados=4) == 0.9


def test_seleccionar_ninguno_si_nadie_cumple_y_nunca_elige_derivar_todo():
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.999, min_aceptados=1) == 0.9
    solo_inf = barrido_umbral([0.9, 0.9], [True, True], [INF], n_total_corpus=2)
    assert seleccionar_umbral(solo_inf, piso=0.5, min_aceptados=1) is None


def test_evaluar_confirmado():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 11 + [False] + [True, False, False, False]
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "confirmado"
    assert r["exactitud_selectiva"] == pytest.approx(11 / 12)
    assert r["exactitud_derivados"] == pytest.approx(1 / 4)


def test_evaluar_no_confirmado_si_la_exactitud_selectiva_no_alcanza_el_piso():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 8 + [False] * 4 + [False] * 4
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "no confirmado"


def test_evaluar_no_confirmado_si_los_derivados_no_son_peores():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 11 + [False] + [True] * 4  # derivados 100 % > aceptados 91,7 %
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "no confirmado"


def test_evaluar_no_estimable_con_pocos_aceptados_o_sin_derivados():
    pocos = evaluar_fuera_de_muestra_gate(
        0.8, [0.9] * 9 + [0.5] * 5, [True] * 14, piso=0.85, n_total_corpus=20
    )
    assert pocos["veredicto"] == "no estimable"
    sin_derivados = evaluar_fuera_de_muestra_gate(
        0.8, [0.9] * 12, [True] * 12, piso=0.85, n_total_corpus=20
    )
    assert sin_derivados["veredicto"] == "no estimable"


def test_evaluar_sin_umbral_seleccionado_solo_describe():
    r = evaluar_fuera_de_muestra_gate(None, [0.9, 0.5], [True, False], piso=0.85, n_total_corpus=2)
    assert r["veredicto"] == "sin umbral seleccionado"
    assert r["umbral"] is None


def test_evaluar_no_acepta_reelegir_el_umbral_con_datos_fuera_de_muestra():
    with pytest.raises(TypeError):
        evaluar_fuera_de_muestra_gate(  # type: ignore[call-arg]
            0.8, [0.9], [True], piso=0.85, n_total_corpus=1, umbrales=[0.5, 0.9]
        )


def test_isotonica_es_monotona_y_corrige_el_nivel():
    # confianza 0.9 con exactitud 0.5 en el ajuste -> la recalibrada vale 0.5 en 0.9
    modelo = ajustar_isotonica([0.8, 0.8, 0.9, 0.9], [False, False, True, False])
    salidas = aplicar_isotonica(modelo, [0.5, 0.8, 0.85, 0.9, 0.99])
    assert all(a <= b for a, b in zip(salidas, salidas[1:]))
    # escalon: por debajo del minimo ajustado vale el primer bloque; luego el bloque de x <= entrada
    assert salidas == [pytest.approx(0.0), pytest.approx(0.0), pytest.approx(0.0),
                       pytest.approx(0.5), pytest.approx(0.5)]


def test_isotonica_pava_agrupa_violaciones_con_pesos():
    # x=1: 1 de 1 ; x=2: 0 de 3 -> violacion; bloque unico con media 1/4 para ambos
    modelo = ajustar_isotonica([0.1, 0.2, 0.2, 0.2], [True, False, False, False])
    assert aplicar_isotonica(modelo, [0.1, 0.2]) == [pytest.approx(0.25), pytest.approx(0.25)]


def test_isotonica_no_invierte_el_orden_y_conserva_el_auroc_si_no_hay_agrupacion():
    fit_s = [0.2, 0.4, 0.6, 0.8]
    fit_a = [False, False, True, True]
    modelo = ajustar_isotonica(fit_s, fit_a)
    senales = [0.2, 0.4, 0.6, 0.8, 0.8, 0.4]
    aciertos = [False, False, True, True, False, True]
    recal = aplicar_isotonica(modelo, senales)
    assert auroc(recal, aciertos) == pytest.approx(auroc(senales, aciertos))


def test_isotonica_rechaza_ajuste_vacio():
    with pytest.raises(ValueError):
        ajustar_isotonica([], [])
