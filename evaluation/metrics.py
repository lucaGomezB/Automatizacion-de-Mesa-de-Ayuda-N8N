"""
Métricas de evaluación del clasificador — funciones puras.

Todas las funciones operan sobre las tres categorías fijas del sistema en
orden canónico. No realizan I/O ni dependencias de red; son completamente
testeables con asserts numéricos.

Orden de clases: ["Sistemas", "Operaciones", "Soporte Técnico"]
Convención de la matriz: filas = categoría real, columnas = categoría predicha.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Constante de orden de clases (todas las funciones la usan)
# ---------------------------------------------------------------------------
CLASES: List[str] = ["Sistemas", "Operaciones", "Soporte Técnico"]

# Tipo alias para legibilidad
MatrizConfusion = Dict[str, Dict[str, int]]


# ---------------------------------------------------------------------------
# Helper: denominador cero → 0.0
# ---------------------------------------------------------------------------
def _dividir_seguro(numerador: float, denominador: float) -> float:
    """
    Divide numerador/denominador devolviendo 0.0 si el denominador es cero.

    Esto implementa la convención del spec: 'Clase sin predicciones → 0.0'.
    """
    if denominador == 0:
        return 0.0
    return numerador / denominador


# ---------------------------------------------------------------------------
# Grupo 2 — Matriz de confusión
# ---------------------------------------------------------------------------
def matriz_confusion(
    reales: List[str],
    predichos: List[str],
) -> MatrizConfusion:
    """
    Calcula la matriz de confusión sobre las tres clases fijas.

    Args:
        reales: Lista de categorías reales (verdad fundamental).
        predichos: Lista de categorías predichas (misma longitud).

    Returns:
        Diccionario mc[real][predicho] con los conteos.
        Filas = categoría real; columnas = categoría predicha.
    """
    # Inicializar en cero
    mc: MatrizConfusion = {c: {p: 0 for p in CLASES} for c in CLASES}

    for real, predicho in zip(reales, predichos):
        mc[real][predicho] += 1

    return mc


# ---------------------------------------------------------------------------
# Grupo 3 — Métricas por clase y macro
# ---------------------------------------------------------------------------
def precision_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """
    Precisión por clase = TP / (TP + FP).

    Denominador cero → 0.0 (ninguna predicción cayó en esa clase).
    """
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        tp = mc[clase][clase]
        # FP = otras clases que fueron predichas como `clase`
        fp = sum(mc[real][clase] for real in CLASES if real != clase)
        resultado[clase] = _dividir_seguro(tp, tp + fp)
    return resultado


def sensibilidad_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """
    Sensibilidad (recall) por clase = TP / (TP + FN).

    Denominador cero → 0.0 (no hay casos reales de esa clase).
    """
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        tp = mc[clase][clase]
        # FN = casos reales de `clase` predichos como otra clase
        fn = sum(mc[clase][pred] for pred in CLASES if pred != clase)
        resultado[clase] = _dividir_seguro(tp, tp + fn)
    return resultado


def f1_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """
    F1 por clase = 2 * P * R / (P + R).

    Denominador cero → 0.0 (cuando P + R = 0).
    """
    precisiones = precision_por_clase(mc)
    sensibilidades = sensibilidad_por_clase(mc)
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        p = precisiones[clase]
        r = sensibilidades[clase]
        resultado[clase] = _dividir_seguro(2 * p * r, p + r)
    return resultado


def f1_macro(f1s: Dict[str, float]) -> float:
    """
    F1 macro = media aritmética de los F1 por clase.

    Pondera las tres clases por igual (independiente de distribución).
    """
    return sum(f1s[c] for c in CLASES) / len(CLASES)


# ---------------------------------------------------------------------------
# Grupo 4 — Exactitud global e IC de Wilson
# ---------------------------------------------------------------------------
def exactitud_global(reales: List[str], predichos: List[str]) -> float:
    """
    Exactitud = K aciertos / N casos totales.

    Args:
        reales: Lista de categorías reales.
        predichos: Lista de categorías predichas.

    Returns:
        Proporción de aciertos en [0.0, 1.0].
    """
    if not reales:
        return 0.0
    aciertos = sum(r == p for r, p in zip(reales, predichos))
    return aciertos / len(reales)


def intervalo_wilson(
    aciertos: int,
    total: int,
    confianza: float = 0.95,
) -> Tuple[float, float]:
    """
    Intervalo de confianza de Wilson para una proporción binomial.

    Implementa la fórmula cerrada de Wilson (1927), consistente con §4.7:

        p̂ = aciertos / total
        z = z_{α/2} para el nivel de confianza
        lower/upper = (p̂ + z²/2n ± z√(p̂(1-p̂)/n + z²/4n²)) / (1 + z²/n)

    Args:
        aciertos: Número de clasificaciones correctas.
        total: Número total de casos.
        confianza: Nivel de confianza (default 0.95).

    Returns:
        Tupla (lower, upper) acotada en [0, 1].
    """
    # z_{α/2} para 95% ≈ 1.96
    # Usamos el valor exacto de la distribución normal estándar
    # Para confianza=0.95, z=1.9599639845400536
    # Implementado con la fórmula inversa sin scipy para evitar dependencia
    # (si scipy está disponible, usar stats.norm.ppf es equivalente)
    from math import sqrt

    try:
        from scipy.stats import norm  # type: ignore[import]

        z = norm.ppf(1 - (1 - confianza) / 2)
    except ImportError:
        # Aproximación para 95% sin scipy
        z = 1.959963984540054

    p_hat = aciertos / total
    n = total

    z2 = z * z
    denominador = 1 + z2 / n
    centro = (p_hat + z2 / (2 * n)) / denominador
    margen = (z * sqrt(p_hat * (1 - p_hat) / n + z2 / (4 * n * n))) / denominador

    lower = max(0.0, centro - margen)
    upper = min(1.0, centro + margen)

    return lower, upper
