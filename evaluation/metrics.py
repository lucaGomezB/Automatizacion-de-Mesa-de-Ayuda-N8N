"""
Metricas de evaluacion del clasificador multietiqueta (C-27, design D5).

Todas las funciones operan sobre los cinco sectores canonicos, en orden fijo.
No realizan I/O ni dependencias de red; son funciones puras y testeables.

Definiciones:
- Matriz primaria 5x5: filas = `sector_asignado`, columnas = `sector_predicho`.
- Exactitud primaria: proporcion de casos con `sector_predicho == sector_asignado`.
- Subset accuracy: conjunto predicho == conjunto de verdad.
- Perdida de Hamming: etiquetas erroneas sobre el universo del caso.
- Micro-F1: TP/FP/FN acumulados de todas las etiquetas.
- Macro-F1: media aritmetica de los F1 por sector (los cinco).
- One-vs-rest por sector: precision, recall, F1 y soporte.
- Wilson CI: sobre igualdad estricta y sobre pertenencia.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from evaluation.corpus import SECTORES_CANONICOS

# ---------------------------------------------------------------------------
# Clases canonicas (todas las funciones las usan)
# ---------------------------------------------------------------------------
CLASES: List[str] = list(SECTORES_CANONICOS)

MatrizConfusion = Dict[str, Dict[str, int]]

ConjuntoEtiquetas = Set[str]


# ---------------------------------------------------------------------------
# Helper: denominador cero -> 0.0
# ---------------------------------------------------------------------------
def _dividir_seguro(numerador: float, denominador: float) -> float:
    """Divide numerador/denominador devolviendo 0.0 si el denominador es cero."""
    if denominador == 0:
        return 0.0
    return numerador / denominador


# ---------------------------------------------------------------------------
# Grupo 2 — Matriz de confusion primaria 5x5
# ---------------------------------------------------------------------------
def matriz_confusion(reales: List[str], predichos: List[str]) -> MatrizConfusion:
    """
    Calcula la matriz de confusion 5x5 sobre las clases canonicas.

    Filas = sector asignado (real); columnas = sector predicho principal.
    """
    mc: MatrizConfusion = {c: {p: 0 for p in CLASES} for c in CLASES}

    for real, predicho in zip(reales, predichos):
        if real not in CLASES:
            raise ValueError(f"Sector real invalido: '{real}'. Validos: {CLASES}")
        if predicho not in CLASES:
            raise ValueError(f"Sector predicho invalido: '{predicho}'. Validos: {CLASES}")
        mc[real][predicho] += 1

    return mc


# ---------------------------------------------------------------------------
# Grupo 3 — Metricas por sector (one-vs-rest) y promedios
# ---------------------------------------------------------------------------
def precision_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """Precision por sector = TP / (TP + FP). Denominador cero -> 0.0."""
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        tp = mc[clase][clase]
        fp = sum(mc[real][clase] for real in CLASES if real != clase)
        resultado[clase] = _dividir_seguro(tp, tp + fp)
    return resultado


def sensibilidad_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """Sensibilidad (recall) por sector = TP / (TP + FN). Denominador cero -> 0.0."""
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        tp = mc[clase][clase]
        fn = sum(mc[clase][pred] for pred in CLASES if pred != clase)
        resultado[clase] = _dividir_seguro(tp, tp + fn)
    return resultado


def f1_por_clase(mc: MatrizConfusion) -> Dict[str, float]:
    """F1 por sector = 2 * P * R / (P + R). Denominador cero -> 0.0."""
    precisiones = precision_por_clase(mc)
    sensibilidades = sensibilidad_por_clase(mc)
    resultado: Dict[str, float] = {}
    for clase in CLASES:
        p = precisiones[clase]
        r = sensibilidades[clase]
        resultado[clase] = _dividir_seguro(2 * p * r, p + r)
    return resultado


def soporte_por_clase(mc: MatrizConfusion) -> Dict[str, int]:
    """Soporte por sector = cantidad de casos reales de ese sector (suma de la fila)."""
    return {clase: sum(mc[clase].values()) for clase in CLASES}


def f1_macro(f1s: Dict[str, float]) -> float:
    """F1 macro = media aritmetica de los cinco F1 por sector."""
    return sum(f1s[c] for c in CLASES) / len(CLASES)


def f1_micro(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
) -> float:
    """F1 micro sobre TP/FP/FN acumulados de todas las etiquetas."""
    tp = fp = fn = 0
    for verdad, predicho in zip(conjuntos_verdad, conjuntos_predichos):
        tp += len(verdad & predicho)
        fp += len(predicho - verdad)
        fn += len(verdad - predicho)

    precision = _dividir_seguro(tp, tp + fp)
    recall = _dividir_seguro(tp, tp + fn)
    return _dividir_seguro(2 * precision * recall, precision + recall)


# ---------------------------------------------------------------------------
# Grupo 4 — Exactitud primaria e IC de Wilson
# ---------------------------------------------------------------------------
def exactitud_global(reales: List[str], predichos: List[str]) -> float:
    """Exactitud primaria = K aciertos estrictos / N casos totales."""
    if not reales:
        return 0.0
    aciertos = sum(r == p for r, p in zip(reales, predichos))
    return aciertos / len(reales)


def aciertos_estrictos(reales: List[str], predichos: List[str]) -> int:
    """Cantidad de casos con `sector_predicho == sector_asignado`."""
    return sum(r == p for r, p in zip(reales, predichos))


def aciertos_pertenencia(
    asignados: List[str],
    predichos: List[str],
    adicionales_predichos: Iterable[Iterable[str]],
) -> int:
    """Cantidad de casos donde `sector_asignado` pertenece al conjunto predicho."""
    aciertos = 0
    for asignado, predicho, adicionales in zip(asignados, predichos, adicionales_predichos):
        conjunto = {predicho, *adicionales}
        if asignado in conjunto:
            aciertos += 1
    return aciertos


def intervalo_wilson(
    aciertos: int,
    total: int,
    confianza: float = 0.95,
) -> Tuple[float, float]:
    """
    Intervalo de confianza de Wilson para una proporcion binomial.

    Implementa la formula cerrada de Wilson (1927). Funcion pura, sin I/O.
    """
    from math import sqrt

    if total <= 0:
        return 0.0, 1.0

    try:
        from scipy.stats import norm  # type: ignore[import]

        z = norm.ppf(1 - (1 - confianza) / 2)
    except ImportError:
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


# ---------------------------------------------------------------------------
# Requisito ADDED — metricas de conjunto multietiqueta
# ---------------------------------------------------------------------------
def _pares_conjuntos(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
) -> List[Tuple[ConjuntoEtiquetas, ConjuntoEtiquetas]]:
    return list(zip(conjuntos_verdad, conjuntos_predichos))


def exactitud_subconjunto(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
) -> float:
    """Subset accuracy: proporcion de casos con conjunto predicho == conjunto de verdad."""
    pares = _pares_conjuntos(conjuntos_verdad, conjuntos_predichos)
    if not pares:
        return 0.0
    aciertos = sum(1 for verdad, predicho in pares if verdad == predicho)
    return aciertos / len(pares)


def perdida_hamming(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
) -> float:
    """
    Perdida de Hamming: proporcion de etiquetas del universo del caso que no coinciden.

    Universo del caso = union(conjunto de verdad, conjunto predicho). Promedio por caso.
    """
    pares = _pares_conjuntos(conjuntos_verdad, conjuntos_predichos)
    if not pares:
        return 0.0

    acumulado = 0.0
    for verdad, predicho in pares:
        universo = verdad | predicho
        if not universo:
            continue
        acumulado += len(verdad ^ predicho) / len(universo)
    return acumulado / len(pares)


def jaccard_por_caso(verdad: ConjuntoEtiquetas, predicho: ConjuntoEtiquetas) -> float:
    """Similitud de Jaccard = |interseccion| / |union|. Union vacia -> 0.0."""
    universo = verdad | predicho
    if not universo:
        return 0.0
    return len(verdad & predicho) / len(universo)


def jaccard_promedio(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
) -> float:
    """Promedio de Jaccard por caso."""
    pares = _pares_conjuntos(conjuntos_verdad, conjuntos_predichos)
    if not pares:
        return 0.0
    return sum(jaccard_por_caso(v, p) for v, p in pares) / len(pares)
