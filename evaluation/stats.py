"""
Análisis estadístico de tiempos — funciones puras.

Envuelve scipy.stats.wilcoxon para la prueba de rangos con signo de dos colas
y calcula el tamaño del efecto rank-biserial, consistente con §4.7 y §7.1
de la tesis.

Convención (c-77, D-A1/D-A2):
    T+ = suma de rangos de las diferencias positivas (manual - automatizado).
    T- = suma de rangos de las diferencias negativas.
    W  = min(T+, T-) es el estadístico de contraste de dos colas de scipy.
    r  = (T+ - T-) / (n(n+1)/2), equivalente a 1 - 4W/(n(n+1)) cuando W = T-.
    Rango teórico de r: [-1, +1]. NO se usa r = 1 - 2W/(n(n+1)) (rango [0, 1]).
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, median
from typing import List, Optional, Sequence, Tuple

# Mínimo de pares que exige scipy.stats.shapiro.
_MIN_PARES_SHAPIRO = 3


@dataclass(frozen=True)
class ResultadoWilcoxon:
    """
    Resultado completo de la prueba de Wilcoxon de rangos con signo.

    Attributes:
        estadistico: Estadístico de contraste W = min(T+, T-) (dos colas).
        t_positivos: Suma de rangos de las diferencias positivas (T+).
        t_negativos: Suma de rangos de las diferencias negativas (T-).
        p: Valor p bilateral.
        r: Tamaño del efecto rank-biserial (T+ - T-) / (n(n+1)/2).
        n: Número de pares.
    """

    estadistico: float
    t_positivos: float
    t_negativos: float
    p: float
    r: float
    n: int


def wilcoxon_tiempos_detallado(
    manual: List[float],
    automatizado: List[float],
) -> ResultadoWilcoxon:
    """
    Prueba de Wilcoxon de rangos con signo sobre pares (manual, automatizado).

    Contrasta H₀: mediana(diferencias) = 0 con la variante de dos colas.
    El tamaño del efecto se calcula directamente como
    r = (T+ - T-) / (n(n+1)/2), donde T+ y T- son las sumas de rangos de las
    diferencias positivas y negativas.

    Args:
        manual: Lista de tiempos del flujo manual (en segundos).
        automatizado: Lista de tiempos del flujo automatizado (en segundos).
            Debe tener la misma longitud que `manual`.

    Returns:
        ResultadoWilcoxon con el estadístico de contraste, T+, T-, el valor p,
        el tamaño del efecto y el número de pares.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    if len(manual) != len(automatizado):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Se recibieron: manual={len(manual)}, automatizado={len(automatizado)}."
        )

    try:
        from scipy.stats import rankdata, wilcoxon  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "scipy es requerido para el análisis de tiempos. "
            "Instalá las dependencias con: pip install -r evaluation/requirements.txt"
        ) from exc

    diferencias = [m - a for m, a in zip(manual, automatizado)]
    n = len(diferencias)

    resultado = wilcoxon(diferencias, alternative="two-sided")
    p = float(resultado.pvalue)

    # Sumas de rangos calculadas explícitamente (los empates en |d| reciben
    # el rango promedio vía rankdata; las diferencias nulas no aportan a T+/T-).
    rangos = rankdata([abs(d) for d in diferencias])
    t_positivos = float(
        sum(rk for rk, d in zip(rangos, diferencias) if d > 0)
    )
    t_negativos = float(
        sum(rk for rk, d in zip(rangos, diferencias) if d < 0)
    )

    estadistico = min(t_positivos, t_negativos)

    denominador = n * (n + 1) / 2
    if denominador == 0:
        r = 0.0
    else:
        r = (t_positivos - t_negativos) / denominador

    return ResultadoWilcoxon(
        estadistico=estadistico,
        t_positivos=t_positivos,
        t_negativos=t_negativos,
        p=p,
        r=r,
        n=n,
    )


def wilcoxon_tiempos(
    manual: List[float],
    automatizado: List[float],
) -> Tuple[float, float, float]:
    """
    Envoltorio compatible: devuelve (W, p, r).

    W = min(T+, T-) es el estadístico de contraste de dos colas y
    r = (T+ - T-) / (n(n+1)/2) es el tamaño del efecto rank-biserial.
    Para el detalle de T+ y T-, usar `wilcoxon_tiempos_detallado`.
    """
    resultado = wilcoxon_tiempos_detallado(manual, automatizado)
    return resultado.estadistico, resultado.p, resultado.r


# ---------------------------------------------------------------------------
# Normalidad (Shapiro-Wilk) — función pura (c-99, D1)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoShapiro:
    """
    Resultado del contraste de normalidad de Shapiro-Wilk.

    Attributes:
        n: Número de observaciones de la serie.
        w: Estadístico W de Shapiro-Wilk, o None si no aplica.
        p: Valor p bilateral, o None si no aplica.
        aplicable: False cuando la serie no alcanza el mínimo de pares de la
            prueba (`_MIN_PARES_SHAPIRO`); en ese caso `w` y `p` son None.
    """

    n: int
    w: Optional[float]
    p: Optional[float]
    aplicable: bool


def shapiro_normalidad(datos: Sequence[float]) -> ResultadoShapiro:
    """
    Contraste de normalidad de Shapiro-Wilk sobre una serie.

    Función pura, sin I/O ni dependencia del corpus en disco.

    Args:
        datos: Serie numérica a contrastar.

    Returns:
        ResultadoShapiro con W, p y n. Si la serie tiene menos del mínimo de
        pares que exige la prueba (n < 3), se declara no aplicable con
        `aplicable=False`, `w=None` y `p=None`.

    Raises:
        ImportError: Si scipy no está instalado.
    """
    n = len(datos)
    if n < _MIN_PARES_SHAPIRO:
        return ResultadoShapiro(n=n, w=None, p=None, aplicable=False)

    try:
        from scipy.stats import shapiro  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "scipy es requerido para el análisis de tiempos. "
            "Instalá las dependencias con: pip install -r evaluation/requirements.txt"
        ) from exc

    w, p = shapiro(list(datos))
    return ResultadoShapiro(n=n, w=float(w), p=float(p), aplicable=True)


# ---------------------------------------------------------------------------
# Reducción de tiempos — utilidades puras (c-99, D5)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoReduccion:
    """
    Reducción de tiempo entre el flujo manual y el automatizado.

    La reducción se expresa en segundos ahorrados (`manual - automatizado`).
    La cota conservadora descuenta 1 s al tiempo manual por caso, porque
    `tiempo_manual_s` se redondeó al alza y su valor real no es mayor que el
    reportado.

    Attributes:
        n: Número de pares.
        reduccion_media_reportada: Media de la reducción sobre valores reportados.
        reduccion_mediana_reportada: Mediana de la reducción reportada.
        reduccion_media_conservadora: Media de la reducción con descuento de 1 s.
        reduccion_mediana_conservadora: Mediana de la reducción conservadora.
        pares_no_mas_rapidos: Pares en que el automatizado NO fue más rápido
            (invertidos o empatados, `automatizado >= manual`).
    """

    n: int
    reduccion_media_reportada: float
    reduccion_mediana_reportada: float
    reduccion_media_conservadora: float
    reduccion_mediana_conservadora: float
    pares_no_mas_rapidos: int


def _media(xs: List[float]) -> float:
    return fmean(xs) if xs else 0.0


def _mediana(xs: List[float]) -> float:
    return float(median(xs)) if xs else 0.0


def reduccion_tiempos(
    manual: List[float],
    automatizado: List[float],
) -> ResultadoReduccion:
    """
    Calcula la reducción de tiempo reportada y su cota conservadora.

    Args:
        manual: Tiempos del flujo manual (segundos, redondeados al alza).
        automatizado: Tiempos del flujo automatizado (segundos).

    Returns:
        ResultadoReduccion con media/mediana reportada y conservadora, y el
        conteo de pares en que el automatizado no fue más rápido.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    if len(manual) != len(automatizado):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Se recibieron: manual={len(manual)}, automatizado={len(automatizado)}."
        )

    reducciones = [m - a for m, a in zip(manual, automatizado)]
    conservadoras = [(m - 1.0) - a for m, a in zip(manual, automatizado)]
    pares_no_mas_rapidos = sum(
        1 for m, a in zip(manual, automatizado) if a >= m
    )

    return ResultadoReduccion(
        n=len(reducciones),
        reduccion_media_reportada=_media(reducciones),
        reduccion_mediana_reportada=_mediana(reducciones),
        reduccion_media_conservadora=_media(conservadoras),
        reduccion_mediana_conservadora=_mediana(conservadoras),
        pares_no_mas_rapidos=pares_no_mas_rapidos,
    )
