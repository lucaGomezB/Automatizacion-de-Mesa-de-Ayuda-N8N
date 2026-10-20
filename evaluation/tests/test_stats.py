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
