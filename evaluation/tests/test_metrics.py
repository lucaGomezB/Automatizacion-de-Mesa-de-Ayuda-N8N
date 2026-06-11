"""
Tests para evaluation/metrics.py — métricas de clasificación.

TDD — ciclos: RED → GREEN → TRIANGULATE → REFACTOR
Grupos 2, 3, 4 de las tasks.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Orden de clases fijo (filas=real, columnas=predicho)
# ---------------------------------------------------------------------------
CLASES = ["Sistemas", "Operaciones", "Soporte Técnico"]


# ===========================================================================
# Grupo 2 — Matriz de confusión
# ===========================================================================

def test_matriz_confusion_clasificacion_perfecta_es_diagonal():
    """Cuando todas las predicciones son correctas, la matriz es diagonal."""
    from evaluation.metrics import matriz_confusion

    reales = ["Sistemas", "Operaciones", "Soporte Técnico",
              "Sistemas", "Operaciones"]
    predichos = ["Sistemas", "Operaciones", "Soporte Técnico",
                 "Sistemas", "Operaciones"]

    mc = matriz_confusion(reales, predichos)

    # Diagonal debe tener los conteos; off-diagonal debe ser 0
    assert mc["Sistemas"]["Sistemas"] == 2
    assert mc["Operaciones"]["Operaciones"] == 2
    assert mc["Soporte Técnico"]["Soporte Técnico"] == 1
    # Fuera de diagonal
    assert mc["Sistemas"]["Operaciones"] == 0
    assert mc["Sistemas"]["Soporte Técnico"] == 0
    assert mc["Operaciones"]["Sistemas"] == 0
    assert mc["Soporte Técnico"]["Sistemas"] == 0


def test_matriz_confusion_error_va_fuera_de_la_diagonal():
    """Real=Sistemas, predicho=Operaciones → celda (Sistemas,Operaciones)=1; diagonal no cuenta."""
    from evaluation.metrics import matriz_confusion

    reales = ["Sistemas"]
    predichos = ["Operaciones"]

    mc = matriz_confusion(reales, predichos)

    assert mc["Sistemas"]["Operaciones"] == 1
    assert mc["Sistemas"]["Sistemas"] == 0  # la diagonal no cuenta ese caso


def test_matriz_confusion_mixta_conteos_fila_columna():
    """Caso mixto: verificar conteos por fila y columna."""
    from evaluation.metrics import matriz_confusion

    reales = [
        "Sistemas",       # predicho correcto
        "Sistemas",       # predicho incorrecto → Operaciones
        "Operaciones",    # predicho correcto
        "Soporte Técnico",  # predicho correcto
    ]
    predichos = [
        "Sistemas",
        "Operaciones",
        "Operaciones",
        "Soporte Técnico",
    ]

    mc = matriz_confusion(reales, predichos)

    assert mc["Sistemas"]["Sistemas"] == 1
    assert mc["Sistemas"]["Operaciones"] == 1
    assert mc["Operaciones"]["Operaciones"] == 1
    assert mc["Soporte Técnico"]["Soporte Técnico"] == 1
    # Verificar que la suma de la fila Sistemas es correcta
    total_sistemas = sum(mc["Sistemas"].values())
    assert total_sistemas == 2  # 2 casos reales de Sistemas


# ===========================================================================
# Grupo 3 — Métricas por clase y macro
# ===========================================================================

def test_f1_por_clase_es_media_armonica():
    """F1 = 2*P*R/(P+R) para valores conocidos."""
    from evaluation.metrics import f1_por_clase, matriz_confusion

    # 3 Sistemas correctos, 1 predicho incorrecto como Operaciones
    # Precision Sistemas = 3/3 = 1.0
    # Recall Sistemas = 3/4 = 0.75 (4 reales de Sistemas pero solo 3 predichos bien)
    reales = ["Sistemas", "Sistemas", "Sistemas", "Sistemas",
              "Operaciones", "Operaciones", "Soporte Técnico"]
    predichos = ["Sistemas", "Sistemas", "Sistemas", "Operaciones",
                 "Operaciones", "Operaciones", "Soporte Técnico"]

    mc = matriz_confusion(reales, predichos)
    f1s = f1_por_clase(mc)

    # Precisión Sistemas = TP/(TP+FP) = 3/(3+0)=1.0; Recall = 3/(3+1)=0.75
    esperado_sistemas = 2 * 1.0 * 0.75 / (1.0 + 0.75)
    assert abs(f1s["Sistemas"] - esperado_sistemas) < 1e-9


def test_f1_macro_pondera_clases_por_igual():
    """F1 macro = media aritmética de los 3 F1, independiente de tamaños de clase."""
    from evaluation.metrics import f1_macro, f1_por_clase, matriz_confusion

    # Distribución desbalanceada: 10 Sistemas, 2 Operaciones, 1 Soporte Técnico
    reales = (
        ["Sistemas"] * 10
        + ["Operaciones"] * 2
        + ["Soporte Técnico"] * 1
    )
    predichos = reales[:]  # predicción perfecta → F1=1.0 para cada clase

    mc = matriz_confusion(reales, predichos)
    f1s = f1_por_clase(mc)
    macro = f1_macro(f1s)

    # Con predicción perfecta F1 de cada clase = 1.0 → macro = 1.0
    assert abs(macro - 1.0) < 1e-9


def test_precision_clase_sin_predicciones_es_cero():
    """Si ninguna predicción cae en una clase, precisión = 0.0 (sin excepción)."""
    from evaluation.metrics import precision_por_clase, matriz_confusion

    # Ningún caso predicho como "Soporte Técnico"
    reales = ["Sistemas", "Operaciones"]
    predichos = ["Sistemas", "Operaciones"]

    mc = matriz_confusion(reales, predichos)
    precisiones = precision_por_clase(mc)

    # No hay predicciones de Soporte Técnico → denominador cero → 0.0
    assert precisiones["Soporte Técnico"] == 0.0


def test_sensibilidad_clase_sin_casos_reales_es_cero():
    """Si no hay casos reales de una clase, sensibilidad = 0.0 (sin excepción)."""
    from evaluation.metrics import sensibilidad_por_clase, matriz_confusion

    # No hay casos reales de Soporte Técnico
    reales = ["Sistemas", "Operaciones"]
    predichos = ["Sistemas", "Soporte Técnico"]  # uno predice mal

    mc = matriz_confusion(reales, predichos)
    sensibilidades = sensibilidad_por_clase(mc)

    assert sensibilidades["Soporte Técnico"] == 0.0


# ===========================================================================
# Grupo 4 — Exactitud global e IC de Wilson
# ===========================================================================

def test_exactitud_global_es_proporcion_de_aciertos():
    """K aciertos / N casos totales."""
    from evaluation.metrics import exactitud_global

    reales = ["Sistemas", "Operaciones", "Soporte Técnico", "Sistemas"]
    predichos = ["Sistemas", "Operaciones", "Sistemas", "Sistemas"]

    # 3 aciertos de 4
    exactitud = exactitud_global(reales, predichos)
    assert abs(exactitud - 0.75) < 1e-9


def test_exactitud_global_prediccion_perfecta():
    """Cuando todos los casos son correctos, exactitud = 1.0."""
    from evaluation.metrics import exactitud_global

    reales = ["Sistemas", "Operaciones", "Soporte Técnico"]
    predichos = ["Sistemas", "Operaciones", "Soporte Técnico"]

    assert exactitud_global(reales, predichos) == 1.0


def test_wilson_contiene_la_proporcion_puntual():
    """El IC de Wilson acota el valor puntual: lower <= p_hat <= upper y [0,1]."""
    from evaluation.metrics import intervalo_wilson

    aciertos = 8
    total = 10
    lower, upper = intervalo_wilson(aciertos, total)

    p_hat = aciertos / total
    assert 0.0 <= lower
    assert upper <= 1.0
    assert lower <= p_hat
    assert p_hat <= upper


def test_wilson_caso_referencia_tesis():
    """184/200 → IC aproximado [0.872, 0.952] según §7.2 (tolerancia ±0.01)."""
    from evaluation.metrics import intervalo_wilson

    lower, upper = intervalo_wilson(184, 200)

    assert abs(lower - 0.872) < 0.015
    assert abs(upper - 0.952) < 0.015


def test_exactitud_cross_check_sklearn():
    """Cross-check: exactitud propia == sklearn.metrics.accuracy_score (marcado no-TDD)."""
    pytest.importorskip("sklearn")
    from sklearn.metrics import accuracy_score

    from evaluation.metrics import exactitud_global

    reales = ["Sistemas", "Operaciones", "Soporte Técnico", "Sistemas", "Operaciones"]
    predichos = ["Sistemas", "Operaciones", "Sistemas", "Sistemas", "Operaciones"]

    propio = exactitud_global(reales, predichos)
    sklearn_result = accuracy_score(reales, predichos)

    assert abs(propio - sklearn_result) < 1e-9
