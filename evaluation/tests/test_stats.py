"""
Tests para evaluation/stats.py — análisis estadístico de tiempos.

TDD — ciclo: RED → GREEN → TRIANGULATE → REFACTOR (Grupo 5)
"""

from __future__ import annotations

import pytest


def test_wilcoxon_diferencia_sistematica_es_significativa():
    """
    Cuando el flujo automatizado es SIEMPRE más rápido que el manual,
    la prueba debe devolver p < 0.05 y r (rank-biserial) de magnitud alta.
    """
    from evaluation.stats import wilcoxon_tiempos

    # Tiempos manuales vs automatizados: automatizado siempre 10x más rápido
    manual = [180.0, 210.0, 240.0, 195.0, 220.0, 200.0, 175.0, 160.0, 190.0]
    automatizado = [12.0, 14.0, 15.0, 13.0, 16.0, 14.0, 11.0, 10.0, 12.0]

    W, p, r = wilcoxon_tiempos(manual, automatizado)

    assert p < 0.05, f"Se esperaba p < 0.05, se obtuvo p={p}"
    # Efecto rank-biserial esperado alto (> 0.7 como mínimo)
    assert r > 0.7, f"Se esperaba r > 0.7, se obtuvo r={r}"
    # W >= 0
    assert W >= 0


def test_wilcoxon_series_de_distinta_longitud_lanza_error():
    """Cuando las series tienen longitudes distintas, debe lanzar un error."""
    from evaluation.stats import wilcoxon_tiempos

    manual = [180.0, 210.0, 240.0]
    automatizado = [12.0, 14.0]  # longitud distinta

    with pytest.raises(ValueError, match="longitud"):
        wilcoxon_tiempos(manual, automatizado)


# ---------------------------------------------------------------------------
# A2 — Fórmula rank-biserial y reporte de T+/T- (c-77)
# ---------------------------------------------------------------------------
def test_wilcoxon_detallado_reporta_t_positivos_y_negativos():
    """
    La función debe exponer T+ y T- de forma diferenciada y calcular
    r = (T+ - T-) / (n(n+1)/2), no un conteo de pares concordantes.
    """
    from evaluation.stats import wilcoxon_tiempos_detallado

    manual = [180.0, 210.0, 240.0, 195.0]
    automatizado = [12.0, 14.0, 15.0, 13.0]

    res = wilcoxon_tiempos_detallado(manual, automatizado)
    n = len(manual)
    denom = n * (n + 1) / 2

    assert res.t_positivos == denom
    assert res.t_negativos == 0
    assert res.estadistico == 0  # W = min(T+, T-)
    assert res.r == pytest.approx((res.t_positivos - res.t_negativos) / denom)
    assert res.r == pytest.approx(1.0)


def test_wilcoxon_detallado_pares_invertidos_conocidos():
    """
    TRIANGULATE: 4 pares a favor y 1 en contra con rangos conocidos.
    T+ = 1+2+3+4 = 10, T- = 5, n(n+1)/2 = 15 -> r = 5/15 = 1/3.
    """
    from evaluation.stats import wilcoxon_tiempos_detallado

    # Diferencias manual-automatizado: +10, +20, +30, +40, -50
    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]

    res = wilcoxon_tiempos_detallado(manual, automatizado)

    assert res.t_positivos == 10
    assert res.t_negativos == 5
    assert res.estadistico == 5
    assert res.r == pytest.approx(1 / 3)


def test_wilcoxon_detallado_efecto_no_es_uno_con_invertidos():
    """
    TRIANGULATE: 12 de 200 pares invertidos -> el efecto NO es 1,00.
    Con todos los rangos empatados, r = (188 - 12)/200 = 0,88.
    """
    from evaluation.stats import wilcoxon_tiempos_detallado

    manual = [100.0] * 188 + [100.0] * 12
    automatizado = [0.0] * 188 + [200.0] * 12  # 188 a favor, 12 en contra

    res = wilcoxon_tiempos_detallado(manual, automatizado)

    assert res.n == 200
    assert res.t_positivos > res.t_negativos
    assert res.r == pytest.approx(0.88)
    assert res.r != pytest.approx(1.0)


# ===========================================================================
# c-99 — Normalidad (Shapiro-Wilk) y reducción de tiempos como funciones puras
# ===========================================================================
def test_shapiro_normalidad_serie_normal_no_rechaza():
    """Una serie aproximadamente normal devuelve W, p y n sin rechazar H0."""
    from evaluation.stats import shapiro_normalidad

    datos = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

    res = shapiro_normalidad(datos)

    assert res.aplicable is True
    assert res.n == 9
    assert 0.0 <= res.w <= 1.0
    assert res.p > 0.05, f"Se esperaba no rechazar la normalidad, p={res.p}"


def test_shapiro_normalidad_serie_sesgada_rechaza():
    """Una serie fuertemente sesgada (exponencial) rechaza la normalidad."""
    from evaluation.stats import shapiro_normalidad

    datos = [0.1, 0.2, 0.3, 0.5, 0.8, 1.3, 2.1, 3.4, 5.5, 8.9, 14.4, 23.3, 37.7]

    res = shapiro_normalidad(datos)

    assert res.aplicable is True
    assert res.n == 13
    assert res.p < 0.05, f"Se esperaba rechazar la normalidad, p={res.p}"


def test_shapiro_normalidad_n_insuficiente_declara_no_aplicable():
    """Con menos del mínimo de pares (n<3) no produce W/p: no aplicable."""
    from evaluation.stats import shapiro_normalidad

    for datos in ([], [1.0], [1.0, 2.0]):
        res = shapiro_normalidad(datos)
        assert res.aplicable is False, f"n={len(datos)} debería ser no aplicable"
        assert res.n == len(datos)
        assert res.w is None
        assert res.p is None


def test_reduccion_tiempos_reportada_y_conservadora():
    """
    Reducción reportada = manual - automatizado; conservadora descuenta 1 s
    al manual por su redondeo al alza. Pares no más rápidos = aut >= manual.
    """
    from evaluation.stats import reduccion_tiempos

    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]

    res = reduccion_tiempos(manual, automatizado)

    assert res.n == 5
    assert res.reduccion_media_reportada == pytest.approx(10.0)
    assert res.reduccion_mediana_reportada == pytest.approx(20.0)
    assert res.reduccion_media_conservadora == pytest.approx(9.0)
    assert res.reduccion_mediana_conservadora == pytest.approx(19.0)
    assert res.pares_no_mas_rapidos == 1


def test_shapiro_normalidad_triangulate_con_empates_rechaza():
    """TRIANGULATE: una serie bipartita con empates fuertes rechaza la normalidad."""
    from evaluation.stats import shapiro_normalidad

    datos = [3.0] * 5 + [7.0] * 5

    res = shapiro_normalidad(datos)

    assert res.aplicable is True
    assert res.n == 10
    assert res.p < 0.05


def test_reduccion_tiempos_triangulate_con_empates_e_invertidos():
    """TRIANGULATE: empates y pares invertidos con valores conocidos."""
    from evaluation.stats import reduccion_tiempos

    manual = [100.0, 100.0, 100.0, 100.0]
    automatizado = [100.0, 50.0, 150.0, 80.0]

    res = reduccion_tiempos(manual, automatizado)

    # Diferencias reportadas: 0, 50, -50, 20 -> media 5, mediana 10.
    assert res.reduccion_media_reportada == pytest.approx(5.0)
    assert res.reduccion_mediana_reportada == pytest.approx(10.0)
    # Conservadora (manual - 1): -1, 49, -51, 19 -> media 4, mediana 9.
    assert res.reduccion_media_conservadora == pytest.approx(4.0)
    assert res.reduccion_mediana_conservadora == pytest.approx(9.0)
    # No más rápidos: 100>=100 (sí), 50>=100 (no), 150>=100 (sí), 80>=100 (no).
    assert res.pares_no_mas_rapidos == 2


# ===========================================================================
# c-134 — Descriptivos, reducción relativa, p unilateral, d_z, MDE,
#         sensibilidad del redondeo y granularidad de la medición manual
# ===========================================================================
def test_descriptivos_serie_conocida_usa_desvio_muestral():
    """
    2.1 RED: serie [10, 20, 30, 40].
    media = 25, mediana = 25, mínimo = 10, máximo = 40.
    Desvío muestral (divisor n-1) = sqrt(500/3) = 12.9099; el poblacional
    (divisor n) sería 11.1803 y NO debe usarse.
    """
    from evaluation.stats import estadisticos_descriptivos

    res = estadisticos_descriptivos([10, 20, 30, 40])

    assert res.n == 4
    assert res.media == pytest.approx(25.0)
    assert res.mediana == pytest.approx(25.0)
    assert res.minimo == pytest.approx(10.0)
    assert res.maximo == pytest.approx(40.0)
    assert res.desvio == pytest.approx(12.9099, abs=1e-4)
    assert res.desvio != pytest.approx(11.1803, abs=1e-4)


def test_descriptivos_serie_con_empates_triangula_otra_serie():
    """
    2.1 TRIANGULATE: serie [1, 2, 2, 9].
    media = 3.5, mediana = 2.0; suma de desvíos al cuadrado = 6.25 + 2.25 + 2.25
    + 30.25 = 41, desvío muestral = sqrt(41/3) = 3.6968.
    """
    from evaluation.stats import estadisticos_descriptivos

    res = estadisticos_descriptivos([1, 2, 2, 9])

    assert res.media == pytest.approx(3.5)
    assert res.mediana == pytest.approx(2.0)
    assert res.desvio == pytest.approx(3.6968, abs=1e-4)
    assert (res.minimo, res.maximo) == (1.0, 9.0)


def test_descriptivos_un_unico_valor_declara_desvio_no_aplicable():
    """2.1 TRIANGULATE: con un único valor el desvío es None, sin fabricar 0."""
    from evaluation.stats import estadisticos_descriptivos

    res = estadisticos_descriptivos([7.5])

    assert res.n == 1
    assert res.media == pytest.approx(7.5)
    assert res.mediana == pytest.approx(7.5)
    assert res.minimo == pytest.approx(7.5)
    assert res.maximo == pytest.approx(7.5)
    assert res.desvio is None


def test_descriptivos_serie_vacia_lanza_error():
    """2.1 TRIANGULATE: una serie vacía no tiene descriptivos."""
    from evaluation.stats import estadisticos_descriptivos

    with pytest.raises(ValueError, match="vac"):
        estadisticos_descriptivos([])


def test_reduccion_relativa_media_y_mediana_calculadas_a_mano():
    """
    2.2 RED: manual [100, 200, 600] vs automatizado [20, 60, 70].
    Medias: 300 y 50 -> 1 - 50/300 = 0.8333.
    Medianas: 200 y 60 -> 1 - 60/200 = 0.7000.
    """
    from evaluation.stats import reduccion_relativa

    res = reduccion_relativa([100, 200, 600], [20, 60, 70])

    assert res.media == pytest.approx(0.8333, abs=1e-4)
    assert res.mediana == pytest.approx(0.7000, abs=1e-4)


def test_reduccion_relativa_longitudes_distintas_lanza_error():
    """2.2 RED: series de distinta longitud no se pueden comparar."""
    from evaluation.stats import reduccion_relativa

    with pytest.raises(ValueError, match="longitud"):
        reduccion_relativa([100, 200], [20])


def test_reduccion_relativa_triangula_otra_serie():
    """
    2.2 TRIANGULATE: manual [50, 50] vs automatizado [10, 40].
    Media: 1 - 25/50 = 0.5; mediana: 1 - 25/50 = 0.5 (ambas series de 2).
    """
    from evaluation.stats import reduccion_relativa

    res = reduccion_relativa([50, 50], [10, 40])

    assert res.media == pytest.approx(0.5)
    assert res.mediana == pytest.approx(0.5)


def test_reduccion_relativa_base_manual_nula_declara_no_aplicable():
    """
    2.2 TRIANGULATE: media o mediana manual igual a cero -> None, sin dividir.
    manual [0, 0, 30]: media 10 (aplicable), mediana 0 (no aplicable).
    manual [0, 0]: ambas bases cero.
    """
    from evaluation.stats import reduccion_relativa

    parcial = reduccion_relativa([0, 0, 30], [5, 5, 5])
    assert parcial.mediana is None
    assert parcial.media == pytest.approx(0.5)  # 1 - 5/10

    total = reduccion_relativa([0, 0], [1, 2])
    assert total.media is None
    assert total.mediana is None


def test_wilcoxon_p_unilateral_exacto_en_serie_pequena():
    """
    2.3 RED: diferencias +10, +20, +30, +40, -50 (rangos 1..5).
    T+ = 1+2+3+4 = 10, T- = 5, W = 5.
    p bilateral exacto = 0.625; p unilateral (manual > automatizado) =
    P(T+ >= 10) = 10/32 = 0.3125.
    """
    from evaluation.stats import wilcoxon_tiempos_detallado

    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]

    res = wilcoxon_tiempos_detallado(manual, automatizado)

    assert res.estadistico == 5
    assert res.p == pytest.approx(0.625)
    assert res.p_unilateral == pytest.approx(0.3125)


def test_wilcoxon_p_unilateral_en_la_direccion_opuesta():
    """
    2.3 TRIANGULATE: diferencias -10, -20, -30, -40, +50 (T+ = 5).
    p unilateral = P(T+ >= 5) = 25/32 = 0.78125 (> 0.5);
    el p bilateral no cambia respecto de la serie simétrica (0.625).
    """
    from evaluation.stats import wilcoxon_tiempos_detallado

    manual = [90.0, 80.0, 70.0, 60.0, 150.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 100.0]

    res = wilcoxon_tiempos_detallado(manual, automatizado)

    assert res.p_unilateral == pytest.approx(0.78125)
    assert res.p == pytest.approx(0.625)


def test_wilcoxon_p_unilateral_no_altera_estadistico_ni_p_ni_r():
    """
    2.3 TRIANGULATE: W, T+, T-, p bilateral y r conservan su definición
    (W = min(T+, T-), r = (T+ - T-) / (n(n+1)/2)).
    Diferencias +10..+40 y -50: r = (10 - 5) / 15 = 1/3.
    """
    from evaluation.stats import wilcoxon_tiempos, wilcoxon_tiempos_detallado

    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]

    res = wilcoxon_tiempos_detallado(manual, automatizado)

    assert (res.t_positivos, res.t_negativos) == (10.0, 5.0)
    assert res.estadistico == 5.0
    assert res.r == pytest.approx(1 / 3)
    assert wilcoxon_tiempos(manual, automatizado) == (
        res.estadistico,
        res.p,
        res.r,
    )


def test_dz_calculado_a_mano():
    """
    2.4 RED: manual [3, 5, 7] vs automatizado [1, 2, 3] -> diferencias 2, 3, 4.
    media(d) = 3, desvío muestral = 1 -> d_z = 3.0.
    """
    from evaluation.stats import tamano_efecto_dz

    assert tamano_efecto_dz([3, 5, 7], [1, 2, 3]) == pytest.approx(3.0)


def test_dz_triangula_con_diferencias_mixtas():
    """
    2.4 TRIANGULATE: diferencias 1, -1, 2, 0 (manual [2, 0, 3, 1] vs
    automatizado [1, 1, 1, 1]).
    media(d) = 0.5; desvío muestral = sqrt((0.25+2.25+2.25+0.25)/3) = 1.2910
    -> d_z = 0.5 / 1.2910 = 0.3873.
    """
    from evaluation.stats import tamano_efecto_dz

    assert tamano_efecto_dz([2, 0, 3, 1], [1, 1, 1, 1]) == pytest.approx(
        0.3873, abs=1e-4
    )


def test_dz_no_aplicable_con_desvio_nulo_o_menos_de_dos_pares():
    """2.4 TRIANGULATE: diferencias constantes o n < 2 -> None (sin infinito)."""
    from evaluation.stats import tamano_efecto_dz

    assert tamano_efecto_dz([10, 20, 30], [5, 15, 25]) is None  # d = 5, 5, 5
    assert tamano_efecto_dz([10], [5]) is None


def test_dz_longitudes_distintas_lanza_error():
    """2.4: series de distinta longitud no forman pares."""
    from evaluation.stats import tamano_efecto_dz

    with pytest.raises(ValueError, match="longitud"):
        tamano_efecto_dz([1, 2, 3], [1, 2])


def test_efecto_minimo_detectable_n_200_sin_ajuste():
    """
    2.5 RED: alfa = 0.05 bilateral, potencia 0.80, n = 200, ARE = 1.
    MDE = (1.95996 + 0.84162) / sqrt(200) = 2.80158 / 14.1421 = 0.1981.
    """
    from evaluation.stats import efecto_minimo_detectable

    assert efecto_minimo_detectable(200) == pytest.approx(0.1981, abs=1e-4)


def test_efecto_minimo_detectable_triangula_are_n_y_lateralidad():
    """
    2.5 TRIANGULATE (valores a mano, z_0.975 = 1.95996, z_0.95 = 1.64485,
    z_0.80 = 0.84162):
    - ARE 0.864, n = 200: 2.80158 / sqrt(172.8) = 0.2131.
    - n = 81, ARE 1: 2.80158 / 9 = 0.3113.
    - unilateral n = 200: (1.64485 + 0.84162) / 14.1421 = 0.1758.
    """
    from evaluation.stats import ARE_WILCOXON_MINIMA, efecto_minimo_detectable

    assert ARE_WILCOXON_MINIMA == pytest.approx(0.864)
    assert efecto_minimo_detectable(
        200, eficiencia_relativa=ARE_WILCOXON_MINIMA
    ) == pytest.approx(0.2131, abs=1e-4)
    assert efecto_minimo_detectable(81) == pytest.approx(0.3113, abs=1e-4)
    assert efecto_minimo_detectable(200, bilateral=False) == pytest.approx(
        0.1758, abs=1e-4
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n": 0},
        {"n": 10, "alfa": 0.0},
        {"n": 10, "alfa": 1.0},
        {"n": 10, "potencia": 0.0},
        {"n": 10, "potencia": 1.0},
        {"n": 10, "eficiencia_relativa": 0.0},
        {"n": 10, "eficiencia_relativa": -0.5},
    ],
)
def test_efecto_minimo_detectable_parametros_invalidos_lanzan_error(kwargs):
    """2.5 TRIANGULATE: n < 1, alfa/potencia fuera de (0, 1) o ARE <= 0."""
    from evaluation.stats import efecto_minimo_detectable

    with pytest.raises(ValueError):
        efecto_minimo_detectable(**kwargs)


def test_escenario_sensibilidad_descuento_calculado_a_mano():
    """
    2.6 RED: manual [30, 40, 50], automatizado [10, 10, 10], descuento 5 s.
    Manual ajustado [25, 35, 45] -> media 35; automatizado media 10;
    reducción relativa de la media = 1 - 10/35 = 0.7143.
    Wilcoxon sobre las diferencias ajustadas 15, 25, 35 (todas positivas,
    n = 3): p bilateral exacto = 2/8 = 0.25, p unilateral = 1/8 = 0.125.
    """
    from evaluation.stats import escenario_sensibilidad

    res = escenario_sensibilidad([30, 40, 50], [10, 10, 10], descuento_s=5)

    assert res.descuento_s == 5
    assert res.media_manual_ajustada == pytest.approx(35.0)
    assert res.reduccion_relativa_media == pytest.approx(0.7143, abs=1e-4)
    assert res.wilcoxon.n == 3
    assert res.wilcoxon.t_positivos == 6.0
    assert res.wilcoxon.p == pytest.approx(0.25)
    assert res.wilcoxon.p_unilateral == pytest.approx(0.125)


def test_escenario_sensibilidad_descuento_cero_reproduce_wilcoxon_original():
    """2.6 TRIANGULATE: con descuento 0 el contraste es el de los pares originales."""
    from evaluation.stats import escenario_sensibilidad, wilcoxon_tiempos_detallado

    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]

    res = escenario_sensibilidad(manual, automatizado, descuento_s=0)

    assert res.wilcoxon == wilcoxon_tiempos_detallado(manual, automatizado)
    assert res.media_manual_ajustada == pytest.approx(sum(manual) / 5)


def test_escenario_sensibilidad_mayor_descuento_reduce_la_reduccion():
    """
    2.6 TRIANGULATE: descuento 10 s sobre manual [30, 40, 50] vs [10, 10, 10]:
    media ajustada 30 -> reducción 1 - 10/30 = 0.6667 (< 0.7143 del descuento 5).
    """
    from evaluation.stats import escenario_sensibilidad

    res = escenario_sensibilidad([30, 40, 50], [10, 10, 10], descuento_s=10)

    assert res.media_manual_ajustada == pytest.approx(30.0)
    assert res.reduccion_relativa_media == pytest.approx(0.6667, abs=1e-4)


def test_escenario_sensibilidad_longitudes_distintas_lanza_error():
    """2.6: series de distinta longitud no forman pares."""
    from evaluation.stats import escenario_sensibilidad

    with pytest.raises(ValueError, match="longitud"):
        escenario_sensibilidad([30, 40], [10], descuento_s=5)


def test_granularidad_manual_cuenta_multiplos_de_5_y_10():
    """
    2.7 RED: [10, 15, 20, 23] -> múltiplos de 5: 10, 15, 20 (3);
    múltiplos de 10: 10, 20 (2).
    """
    from evaluation.stats import granularidad_manual

    assert granularidad_manual([10, 15, 20, 23]) == {5: 3, 10: 2}


def test_granularidad_manual_flotantes_y_multiplos_personalizados():
    """
    2.7 TRIANGULATE: 15.0 cuenta como múltiplo de 5 y 15.5 no; con
    multiplos=(3,) la serie [3, 6, 7.0] cuenta 2 múltiplos de 3.
    """
    from evaluation.stats import granularidad_manual

    assert granularidad_manual([15.0, 15.5]) == {5: 1, 10: 0}
    assert granularidad_manual([3, 6, 7.0], multiplos=(3,)) == {3: 2}


def test_granularidad_manual_serie_vacia_devuelve_ceros():
    """2.7 TRIANGULATE: sin valores, todos los conteos son 0."""
    from evaluation.stats import granularidad_manual

    assert granularidad_manual([]) == {5: 0, 10: 0}


def test_reduccion_tiempos_longitudes_distintas_lanza_error():
    """2.8 REFACTOR: la validación de longitud se comparte entre funciones."""
    from evaluation.stats import reduccion_tiempos

    with pytest.raises(ValueError, match="longitud"):
        reduccion_tiempos([100.0, 200.0], [10.0])
