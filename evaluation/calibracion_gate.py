"""Calibracion y discriminacion de la confianza del gate (c-214).

Funciones puras y deterministas, sin red ni modelo. Reutilizan `evaluation.metrics` para el
bootstrap y el IC de Wilson.
"""

from __future__ import annotations

import random
from typing import Callable, Optional, Sequence

from evaluation.metrics import (
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)

BANDAS_ECE = 10


def _validar(senales: Sequence[float], aciertos: Sequence[bool]) -> None:
    if len(senales) != len(aciertos):
        raise ValueError("la senal y los aciertos deben tener la misma longitud.")
    if len(senales) == 0:
        raise ValueError("no hay observaciones.")
    if any(not (0.0 <= s <= 1.0) for s in senales):
        raise ValueError("la senal debe estar en [0, 1].")


def auroc(senales: Sequence[float], aciertos: Sequence[bool]) -> Optional[float]:
    """AUROC de la senal para separar aciertos de errores (Mann-Whitney, empates a 0,5).

    Devuelve `None` si falta alguna de las dos clases (no definido).
    """
    _validar(senales, aciertos)
    positivos = [s for s, a in zip(senales, aciertos) if a]
    negativos = [s for s, a in zip(senales, aciertos) if not a]
    if not positivos or not negativos:
        return None
    suma = 0.0
    for p in positivos:
        for n in negativos:
            suma += 1.0 if p > n else 0.5 if p == n else 0.0
    return suma / (len(positivos) * len(negativos))


def ece(
    senales: Sequence[float], aciertos: Sequence[bool], bandas: int = BANDAS_ECE
) -> float:
    """ECE con `bandas` bandas de igual ancho en [0, 1] (la ultima cerrada en 1,0)."""
    _validar(senales, aciertos)
    n = len(senales)
    grupos: dict[int, list[tuple[float, bool]]] = {}
    for s, a in zip(senales, aciertos):
        indice = min(int(s * bandas), bandas - 1)
        grupos.setdefault(indice, []).append((s, a))
    total = 0.0
    for observaciones in grupos.values():
        k = len(observaciones)
        confianza_media = sum(s for s, _ in observaciones) / k
        exactitud = sum(1 for _, a in observaciones if a) / k
        total += (k / n) * abs(confianza_media - exactitud)
    return total


def brier(senales: Sequence[float], aciertos: Sequence[bool]) -> float:
    """Puntaje de Brier: media de (senal - acierto)^2."""
    _validar(senales, aciertos)
    return sum((s - (1.0 if a else 0.0)) ** 2 for s, a in zip(senales, aciertos)) / len(senales)


def sobreconfianza(senales: Sequence[float], aciertos: Sequence[bool]) -> float:
    """Confianza media menos exactitud."""
    _validar(senales, aciertos)
    n = len(senales)
    return sum(senales) / n - sum(1 for a in aciertos if a) / n


def ic_bootstrap_metrica(
    senales: Sequence[float],
    aciertos: Sequence[bool],
    metrica: Callable[[Sequence[float], Sequence[bool]], Optional[float]],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> dict:
    """Valor de la metrica con IC95 bootstrap percentil por caso.

    Las remuestras en las que la metrica no esta definida (`None`) se omiten y se cuentan en
    `remuestras_validas`. Si la metrica no esta definida en la muestra original, `ic = None`.
    """
    _validar(senales, aciertos)
    valor = metrica(senales, aciertos)
    generador = random.Random(semilla)
    valores: list[float] = []
    for indices in remuestreos_indices(generador, len(senales), remuestreos):
        v = metrica([senales[i] for i in indices], [aciertos[i] for i in indices])
        if v is not None:
            valores.append(v)
    ic = None
    if valor is not None and valores:
        ic = list(percentil_intervalo(valores, NIVEL_CONFIANZA))
    return {
        "valor": valor,
        "ic": ic,
        "remuestras_validas": len(valores),
        "nivel_confianza": NIVEL_CONFIANZA,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }
