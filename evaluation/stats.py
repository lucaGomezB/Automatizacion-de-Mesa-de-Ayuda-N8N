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
from typing import List, Tuple


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
