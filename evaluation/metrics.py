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

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

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


# ---------------------------------------------------------------------------
# Grupo 6 — Calibracion de la confianza (c-77, A6)
# ---------------------------------------------------------------------------
# Convencion de bandas: intervalo semiabierto [limite_inferior, limite_superior),
# salvo la ultima banda, cerrada en 1.0. Contiguas y sin solapamiento.
BANDAS_CALIBRACION_DEFECTO: Tuple[Tuple[float, float], ...] = (
    (0.0, 0.5),
    (0.5, 0.7),
    (0.7, 0.85),
    (0.85, 0.95),
    (0.95, 1.0),
)


@dataclass(frozen=True)
class BandaCalibracion:
    """Exactitud observada dentro de una banda de confianza declarada."""

    limite_inferior: float
    limite_superior: float
    total: int
    aciertos: int
    exactitud: float


@dataclass(frozen=True)
class ContingenciaConfianza:
    """Contingencia 2x2 en torno al umbral del gate de revision humana."""

    umbral: float
    alta_total: int
    alta_aciertos: int
    alta_exactitud: float
    baja_total: int
    baja_aciertos: int
    baja_exactitud: float


def _acierto(real: str, predicho: str) -> int:
    return 1 if real == predicho else 0


def calibracion_por_bandas(
    confianzas: Sequence[float],
    reales: Sequence[str],
    predichos: Sequence[str],
    bandas: Sequence[Tuple[float, float]] = BANDAS_CALIBRACION_DEFECTO,
) -> List[BandaCalibracion]:
    """
    Exactitud por banda de confianza declarada.

    Cada banda es `[limite_inferior, limite_superior)`, salvo la ultima, cerrada
    en 1.0. Bandas vacias devuelven `exactitud = 0.0` (denominador cero).
    """
    resultado: List[BandaCalibracion] = []
    for indice, (inferior, superior) in enumerate(bandas):
        es_ultima = indice == len(bandas) - 1
        aciertos = total = 0
        for confianza, real, predicho in zip(confianzas, reales, predichos):
            dentro = (
                inferior <= confianza <= superior
                if es_ultima
                else inferior <= confianza < superior
            )
            if not dentro:
                continue
            total += 1
            aciertos += _acierto(real, predicho)
        resultado.append(
            BandaCalibracion(
                limite_inferior=inferior,
                limite_superior=superior,
                total=total,
                aciertos=aciertos,
                exactitud=_dividir_seguro(aciertos, total),
            )
        )
    return resultado


def contingencia_confianza(
    confianzas: Sequence[float],
    reales: Sequence[str],
    predichos: Sequence[str],
    umbral: float = 0.70,
) -> ContingenciaConfianza:
    """
    Contingencia alta/baja en torno al umbral (por defecto 0,70, el gate).

    Alta = confianza >= umbral (el sistema no escala a revision humana);
    baja = confianza < umbral (el sistema escala).
    """
    alta_total = alta_aciertos = baja_total = baja_aciertos = 0
    for confianza, real, predicho in zip(confianzas, reales, predichos):
        acierto = _acierto(real, predicho)
        if confianza >= umbral:
            alta_total += 1
            alta_aciertos += acierto
        else:
            baja_total += 1
            baja_aciertos += acierto
    return ContingenciaConfianza(
        umbral=umbral,
        alta_total=alta_total,
        alta_aciertos=alta_aciertos,
        alta_exactitud=_dividir_seguro(alta_aciertos, alta_total),
        baja_total=baja_total,
        baja_aciertos=baja_aciertos,
        baja_exactitud=_dividir_seguro(baja_aciertos, baja_total),
    )


# ---------------------------------------------------------------------------
# Grupo 7 — Intervalos de confianza por clase y de conjunto (c-108)
# ---------------------------------------------------------------------------
# Procedimiento declarado (design.md D2/D3 de c-108):
# - Precision y sensibilidad por clase son proporciones binomiales
#   (una contra el resto): se estiman con el IC de Wilson (`intervalo_wilson`).
# - F1 por clase y las metricas de conjunto no son proporciones simples: se
#   estiman por bootstrap percentil a nivel de caso, con semilla fija y B
#   remuestreos, para reproducibilidad exacta.
SEMILLA_BOOTSTRAP: int = 20261021
REMUESTREOS_BOOTSTRAP: int = 2000
NIVEL_CONFIANZA: float = 0.95
# Clase con soporte unitario: sin IC, no estimable (design.md D4).
MIN_SOPORTE_ESTIMABLE: int = 2


@dataclass(frozen=True)
class IntervaloClase:
    """IC por clase. `None` cuando la clase no es estimable."""

    clase: str
    soporte: int
    estimable: bool
    precision: Optional[Tuple[float, float]]
    sensibilidad: Optional[Tuple[float, float]]
    f1: Optional[Tuple[float, float]]


@dataclass(frozen=True)
class IntervalosConjunto:
    """IC bootstrap de las metricas de conjunto multietiqueta."""

    subset_accuracy: Tuple[float, float]
    hamming_loss: Tuple[float, float]
    micro_f1: Tuple[float, float]


def _percentil_intervalo(
    muestras: Sequence[float],
    confianza: float,
) -> Tuple[float, float]:
    """Intervalo percentil con interpolacion lineal sobre la muestra ordenada."""
    ordenados = sorted(muestras)
    n = len(ordenados)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return ordenados[0], ordenados[0]

    alfa = 1.0 - confianza

    def _cuantil(q: float) -> float:
        posicion = q * (n - 1)
        bajo = int(math.floor(posicion))
        alto = int(math.ceil(posicion))
        if bajo == alto:
            return ordenados[bajo]
        fraccion = posicion - bajo
        return ordenados[bajo] * (1.0 - fraccion) + ordenados[alto] * fraccion

    return _cuantil(alfa / 2.0), _cuantil(1.0 - alfa / 2.0)


def _remuestreos_indices(
    generador: random.Random,
    n: int,
    remuestreos: int,
) -> Iterable[List[int]]:
    """Genera `remuestreos` listas de indices de casos (con reemplazo)."""
    for _ in range(max(0, remuestreos)):
        yield [generador.randrange(n) for _ in range(n)] if n else []


def intervalos_por_clase(
    reales: Sequence[str],
    predichos: Sequence[str],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
    confianza: float = NIVEL_CONFIANZA,
) -> Dict[str, IntervaloClase]:
    """
    IC de precision, sensibilidad y F1 por clase (una contra el resto).

    Precision y sensibilidad usan el IC de Wilson sobre la matriz primaria
    completa; F1 usa bootstrap percentil a nivel de caso con semilla fija.
    Una clase con soporte menor que `MIN_SOPORTE_ESTIMABLE` se declara no
    estimable y devuelve intervalos `None`.
    """
    reales = list(reales)
    predichos = list(predichos)
    mc = matriz_confusion(reales, predichos)
    soportes = soporte_por_clase(mc)

    generador = random.Random(semilla)
    n = len(reales)
    muestras_f1: Dict[str, List[float]] = {clase: [] for clase in CLASES}
    for indices in _remuestreos_indices(generador, n, remuestreos):
        f1s = f1_por_clase(
            matriz_confusion([reales[i] for i in indices], [predichos[i] for i in indices])
        )
        for clase in CLASES:
            muestras_f1[clase].append(f1s[clase])

    resultado: Dict[str, IntervaloClase] = {}
    for clase in CLASES:
        soporte = soportes[clase]
        if soporte < MIN_SOPORTE_ESTIMABLE:
            resultado[clase] = IntervaloClase(
                clase=clase,
                soporte=soporte,
                estimable=False,
                precision=None,
                sensibilidad=None,
                f1=None,
            )
            continue

        tp = mc[clase][clase]
        fp = sum(mc[real][clase] for real in CLASES if real != clase)
        resultado[clase] = IntervaloClase(
            clase=clase,
            soporte=soporte,
            estimable=True,
            precision=intervalo_wilson(tp, tp + fp, confianza),
            sensibilidad=intervalo_wilson(tp, soporte, confianza),
            f1=_percentil_intervalo(muestras_f1[clase], confianza),
        )
    return resultado


def intervalos_conjunto(
    conjuntos_verdad: Iterable[ConjuntoEtiquetas],
    conjuntos_predichos: Iterable[ConjuntoEtiquetas],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
    confianza: float = NIVEL_CONFIANZA,
) -> IntervalosConjunto:
    """
    IC bootstrap percentil (nivel de caso) de subset accuracy, Hamming loss y micro-F1.

    Cada remuestreo extrae, con reemplazo, `n` casos de la verdad multietiqueta
    y de la prediccion, y recalcula las tres metricas de conjunto. Misma
    semilla y numero de remuestreos que `intervalos_por_clase`.
    """
    pares = _pares_conjuntos(conjuntos_verdad, conjuntos_predichos)
    n = len(pares)

    generador = random.Random(semilla)
    muestras_subset: List[float] = []
    muestras_hamming: List[float] = []
    muestras_micro: List[float] = []
    for indices in _remuestreos_indices(generador, n, remuestreos):
        verdad = [pares[i][0] for i in indices]
        predicho = [pares[i][1] for i in indices]
        muestras_subset.append(exactitud_subconjunto(verdad, predicho))
        muestras_hamming.append(perdida_hamming(verdad, predicho))
        muestras_micro.append(f1_micro(verdad, predicho))
    return IntervalosConjunto(
        subset_accuracy=_percentil_intervalo(muestras_subset, confianza),
        hamming_loss=_percentil_intervalo(muestras_hamming, confianza),
        micro_f1=_percentil_intervalo(muestras_micro, confianza),
    )
