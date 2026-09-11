"""
Tests para evaluation/metrics.py — metricas de clasificacion multietiqueta (C-27).

TDD — ciclos: RED -> GREEN -> TRIANGULATE -> REFACTOR
Cubre la matriz primaria 5x5, las metricas por sector one-vs-rest, micro/macro F1,
el subconjunto exacto, la perdida de Hamming, Jaccard y el IC de Wilson en las dos
definiciones de acierto (igualdad estricta y pertenencia).
"""

from __future__ import annotations

import pytest

# Sectores canonicos abreviados para legibilidad
SEG = "Seguridad Informatica"
SIH = "Soporte Tecnico Hardware"
SISW = "Soporte Tecnico Software"
BD = "Bases de Datos"
SIS = "Sistemas"


# ===========================================================================
# Grupo 2 — Matriz de confusion primaria 5x5
# ===========================================================================
def test_matriz_confusion_clasificacion_perfecta_es_diagonal():
    """Con predicciones correctas, la matriz es diagonal."""
    from evaluation.metrics import matriz_confusion

    reales = [SEG, SIH, SISW, BD, SIS, SIS]
    predichos = [SEG, SIH, SISW, BD, SIS, SIS]

    mc = matriz_confusion(reales, predichos)

    assert mc[SEG][SEG] == 1
    assert mc[SIH][SIH] == 1
    assert mc[SISW][SISW] == 1
    assert mc[BD][BD] == 1
    assert mc[SIS][SIS] == 2
    assert mc[SIS][BD] == 0
    assert mc[BD][SIS] == 0


def test_matriz_confusion_error_va_fuera_de_la_diagonal():
    """Asignado=Bases de Datos, predicho=Sistemas -> celda (BD, SIS)=1; diagonal no cuenta."""
    from evaluation.metrics import matriz_confusion

    mc = matriz_confusion([BD], [SIS])

    assert mc[BD][SIS] == 1
    assert mc[BD][BD] == 0


def test_matriz_confusion_mixta_conteos_fila_columna():
    """Caso mixto: verificar conteos por fila y columna."""
    from evaluation.metrics import matriz_confusion

    reales = [SIS, SIS, BD, SIH]
    predichos = [SIS, BD, BD, SIH]

    mc = matriz_confusion(reales, predichos)

    assert mc[SIS][SIS] == 1
    assert mc[SIS][BD] == 1
    assert mc[BD][BD] == 1
    assert mc[SIH][SIH] == 1
    assert sum(mc[SIS].values()) == 2


def test_matriz_confusion_cubre_los_cinco_sectores():
    """La matriz tiene una fila y una columna por cada sector canonico."""
    from evaluation.metrics import CLASES, matriz_confusion

    mc = matriz_confusion([SIS], [SIS])

    assert set(CLASES) == {SEG, SIH, SISW, BD, SIS}
    for fila in CLASES:
        assert set(mc[fila].keys()) == set(CLASES)


# ===========================================================================
# Grupo 3 — Metricas por sector y promedios
# ===========================================================================
def test_f1_por_clase_es_media_armonica():
    """F1 = 2*P*R/(P+R) para valores conocidos."""
    from evaluation.metrics import f1_por_clase, matriz_confusion

    # Sistemas: 3 correctos de 4 reales, precision 1.0, recall 0.75
    reales = [SIS, SIS, SIS, SIS, BD, BD, SIH]
    predichos = [SIS, SIS, SIS, BD, BD, BD, SIH]

    f1s = f1_por_clase(matriz_confusion(reales, predichos))

    esperado_sistemas = 2 * 1.0 * 0.75 / (1.0 + 0.75)
    assert abs(f1s[SIS] - esperado_sistemas) < 1e-9


def test_f1_macro_pondera_los_cinco_sectores_por_igual():
    """Con los cinco sectores poblados y prediccion perfecta, macro F1 = 1.0."""
    from evaluation.metrics import f1_macro, f1_por_clase, matriz_confusion

    reales = [SEG, SIH, SISW, BD, SIS]
    f1s = f1_por_clase(matriz_confusion(reales, reales[:]))

    assert abs(f1_macro(f1s) - 1.0) < 1e-9


def test_f1_macro_incluye_sectores_ausentes_como_cero():
    """Un sector sin casos reales ni predicciones aporta F1=0.0 a la media macro."""
    from evaluation.metrics import f1_macro, f1_por_clase, matriz_confusion

    reales = [SIS, BD]
    f1s = f1_por_clase(matriz_confusion(reales, reales[:]))

    # 2 sectores con F1=1.0 y 3 con F1=0.0 -> macro = 2/5
    assert abs(f1_macro(f1s) - (2 / 5)) < 1e-9


def test_precision_clase_sin_predicciones_es_cero():
    """Si ninguna prediccion cae en un sector, su precision es 0.0 sin excepcion."""
    from evaluation.metrics import matriz_confusion, precision_por_clase

    precisiones = precision_por_clase(matriz_confusion([SIS, BD], [SIS, BD]))

    assert precisiones[SIH] == 0.0


def test_sensibilidad_clase_sin_casos_reales_es_cero():
    """Si no hay casos reales de un sector, su sensibilidad es 0.0 sin excepcion."""
    from evaluation.metrics import matriz_confusion, sensibilidad_por_clase

    sensibilidades = sensibilidad_por_clase(matriz_confusion([SIS, BD], [SIS, SIH]))

    assert sensibilidades[SIH] == 0.0


def test_soporte_por_clase_cuenta_reales():
    """El soporte de un sector es la cantidad de casos reales de ese sector."""
    from evaluation.metrics import matriz_confusion, soporte_por_clase

    soportes = soporte_por_clase(matriz_confusion([SIS, SIS, BD], [SIS, BD, BD]))

    assert soportes[SIS] == 2
    assert soportes[BD] == 1
    assert soportes[SIH] == 0


def test_f1_micro_agrega_tp_fp_fn_globales():
    """Micro F1 acumula TP/FP/FN de todas las etiquetas: TP=3, FP=1, FN=1 -> 0.75."""
    from evaluation.metrics import f1_micro

    verdad = [frozenset({SIS}), frozenset({BD, SIS}), frozenset({SIH})]
    predicho = [frozenset({SIS}), frozenset({BD}), frozenset({SIH, SISW})]

    assert abs(f1_micro(verdad, predicho) - 0.75) < 1e-9


# ===========================================================================
# Grupo 4 — Exactitud primaria e IC de Wilson
# ===========================================================================
def test_exactitud_global_es_proporcion_de_aciertos():
    """K aciertos / N casos totales sobre la igualdad estricta del sector principal."""
    from evaluation.metrics import exactitud_global

    reales = [SIS, BD, SIH, SIS]
    predichos = [SIS, BD, SIS, SIS]

    assert abs(exactitud_global(reales, predichos) - 0.75) < 1e-9


def test_exactitud_global_prediccion_perfecta():
    """Con todos los aciertos, exactitud primaria = 1.0."""
    from evaluation.metrics import exactitud_global

    reales = [SIS, BD, SIH]
    assert exactitud_global(reales, reales[:]) == 1.0


def test_wilson_contiene_la_proporcion_puntual():
    """El IC de Wilson acota el valor puntual y queda en [0, 1]."""
    from evaluation.metrics import intervalo_wilson

    lower, upper = intervalo_wilson(8, 10)
    p_hat = 0.8

    assert 0.0 <= lower
    assert upper <= 1.0
    assert lower <= p_hat <= upper


def test_aciertos_pertenencia_es_mas_laxo_que_el_estricto():
    """Si el sector asignado aparece en los adicionales predichos, pertenencia acierta."""
    from evaluation.metrics import aciertos_estrictos, aciertos_pertenencia

    asignados = [BD]
    predichos = [SIS]
    adicionales_predichos = [[BD]]

    assert aciertos_estrictos(asignados, predichos) == 0
    assert aciertos_pertenencia(asignados, predichos, adicionales_predichos) == 1


def test_wilson_pertenencia_contiene_su_proporcion():
    """El IC por pertenencia acota la proporcion por pertenencia."""
    from evaluation.metrics import intervalo_wilson

    aciertos = 9
    total = 10
    lower, upper = intervalo_wilson(aciertos, total)

    assert lower <= 0.9 <= upper


# ===========================================================================
# Requisito ADDED — metricas de conjunto multietiqueta
# ===========================================================================
def test_exactitud_subconjunto_coincidencia_perfecta():
    """Si el conjunto predicho iguala al de verdad, subset accuracy = 1.0."""
    from evaluation.metrics import exactitud_subconjunto

    verdad = [frozenset({SIS}), frozenset({BD, SIS})]
    predicho = [frozenset({SIS}), frozenset({BD, SIS})]

    assert abs(exactitud_subconjunto(verdad, predicho) - 1.0) < 1e-9


def test_exactitud_subconjunto_parcial():
    """Un caso con conjunto distinto no cuenta como acierto de subconjunto."""
    from evaluation.metrics import exactitud_subconjunto

    verdad = [frozenset({SIS}), frozenset({BD}), frozenset({SIH, SISW})]
    predicho = [frozenset({SIS}), frozenset({BD, SIS}), frozenset({SIH, SISW})]

    assert abs(exactitud_subconjunto(verdad, predicho) - (2 / 3)) < 1e-9


def test_perdida_hamming_perfecta_es_cero():
    """Con conjuntos identicos, la perdida de Hamming es 0.0."""
    from evaluation.metrics import perdida_hamming

    verdad = [frozenset({SIS, BD}), frozenset({SIH})]
    predicho = [frozenset({SIS, BD}), frozenset({SIH})]

    assert perdida_hamming(verdad, predicho) == 0.0


def test_perdida_hamming_disjuntos_es_uno():
    """Conjuntos disjuntos -> perdida de Hamming 1.0."""
    from evaluation.metrics import perdida_hamming

    assert perdida_hamming([frozenset({SIS})], [frozenset({BD})]) == 1.0


def test_perdida_hamming_solapamiento_parcial():
    """Verdad {SIS,BD}, predicho {BD,SIH}: simetrica 2 sobre union 3 -> 2/3."""
    from evaluation.metrics import perdida_hamming

    assert abs(perdida_hamming([frozenset({SIS, BD})], [frozenset({BD, SIH})]) - (2 / 3)) < 1e-9


def test_jaccard_coincidencia_disjuntos_y_parcial():
    """Jaccard = |interseccion| / |union|."""
    from evaluation.metrics import jaccard_por_caso, jaccard_promedio

    assert jaccard_por_caso(frozenset({SIS, BD}), frozenset({SIS, BD})) == 1.0
    assert jaccard_por_caso(frozenset({SIS}), frozenset({BD})) == 0.0
    assert abs(
        jaccard_por_caso(frozenset({SIS, BD}), frozenset({BD, SIH})) - (1 / 3)
    ) < 1e-9

    verdad = [frozenset({SIS, BD}), frozenset({SIH})]
    predicho = [frozenset({BD, SIH}), frozenset({SIH})]
    assert abs(jaccard_promedio(verdad, predicho) - ((1 / 3) + 1.0) / 2) < 1e-9


def test_operaciones_no_es_clase_valida():
    """`Operaciones` no pertenece a las clases canonicas de evaluacion."""
    from evaluation.metrics import CLASES

    assert "Operaciones" not in CLASES
