"""
Análisis estadístico de tiempos — función pura.

Envuelve scipy.stats.wilcoxon para la prueba de rangos con signo
y calcula el tamaño del efecto rank-biserial, consistente con §7.1
de la tesis.
"""

from __future__ import annotations

from typing import List, Tuple


def wilcoxon_tiempos(
    manual: List[float],
    automatizado: List[float],
) -> Tuple[float, float, float]:
    """
    Prueba de Wilcoxon de rangos con signo sobre pares (manual, automatizado).

    Contrasta H₀: mediana(diferencias) = 0.

    Args:
        manual: Lista de tiempos del flujo manual (en segundos).
        automatizado: Lista de tiempos del flujo automatizado (en segundos).
            Debe tener la misma longitud que `manual`.

    Returns:
        Tupla (W, p, r) donde:
            W = estadístico de Wilcoxon (suma de rangos positivos)
            p = valor p bilateral
            r = tamaño del efecto rank-biserial:
                r = 1 − 2W / (n * (n + 1))
                Con W calculado sobre las diferencias d = manual − automatizado.
                Cuando automatizado < manual en todos los pares, r → 1.0.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    if len(manual) != len(automatizado):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Se recibieron: manual={len(manual)}, automatizado={len(automatizado)}."
        )

    try:
        from scipy.stats import wilcoxon  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "scipy es requerido para el análisis de tiempos. "
            "Instalá las dependencias con: pip install -r evaluation/requirements.txt"
        ) from exc

    diferencias = [m - a for m, a in zip(manual, automatizado)]

    resultado = wilcoxon(diferencias, alternative="greater")
    W_raw = float(resultado.statistic)
    p = float(resultado.pvalue)

    n = len(diferencias)
    max_possible_W = n * (n + 1) / 2  # 20100 for n=200

    # Normalize W to the sum of NEGATIVE ranks (thesis-compatible):
    # Different scipy versions return either sum(positive_ranks) or
    # sum(negative_ranks). We normalize to always return the SMALLER
    # of the two, which for all-positive differences is 0.
    # W = min(W_raw, max_possible_W - W_raw)
    W = min(W_raw, max_possible_W - W_raw)

    # Rank-biserial effect size (§7.1):
    # When manual > automated for all pairs, r = 1.0
    pares_concordantes = sum(1 for d in diferencias if d > 0)
    pares_discordantes = sum(1 for d in diferencias if d < 0)
    total_no_empates = pares_concordantes + pares_discordantes
    if total_no_empates == 0:
        r = 0.0
    else:
        r = (pares_concordantes - pares_discordantes) / total_no_empates

    return W, p, r
