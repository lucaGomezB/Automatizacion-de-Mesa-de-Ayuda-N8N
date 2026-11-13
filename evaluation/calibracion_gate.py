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
    intervalo_wilson,
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


# ---------------------------------------------------------------------------
# Barrido de umbral y regla de seleccion (D3, D4)
# ---------------------------------------------------------------------------
MIN_ACEPTADOS = 10


def barrido_umbral(
    senales: Sequence[float],
    aciertos: Sequence[bool],
    umbrales: Sequence[float],
    *,
    n_total_corpus: int,
) -> list[dict]:
    """Politica «aceptar si senal >= t» para cada umbral (`inf` = derivar todo lo escalado).

    `senales`/`aciertos` son los casos escalados; `n_total_corpus` es el total de casos del
    corpus (denominador de la carga de revision del sistema).
    """
    if len(senales) != len(aciertos):
        raise ValueError("la senal y los aciertos deben tener la misma longitud.")
    if n_total_corpus <= 0:
        raise ValueError("n_total_corpus debe ser positivo.")
    filas: list[dict] = []
    for t in umbrales:
        aceptados = [a for s, a in zip(senales, aciertos) if s >= t]
        derivados = [a for s, a in zip(senales, aciertos) if s < t]
        k, d = len(aceptados), len(derivados)
        ok = sum(1 for a in aceptados if a)
        filas.append(
            {
                "umbral": t,
                "escalados": len(senales),
                "aceptados": k,
                "derivados": d,
                "cobertura": k / len(senales) if senales else 0.0,
                "aciertos_aceptados": ok,
                "exactitud_selectiva": ok / k if k else None,
                "ic_wilson": list(intervalo_wilson(ok, k)) if k else None,
                "exactitud_derivados": (
                    sum(1 for a in derivados if a) / d if d else None
                ),
                "errores_atrapados": sum(1 for a in derivados if not a),
                "errores_aceptados": sum(1 for a in aceptados if not a),
                "carga_revision": d / n_total_corpus,
            }
        )
    return filas


def seleccionar_umbral(
    barrido: Sequence[dict], *, piso: float, min_aceptados: int = MIN_ACEPTADOS
) -> Optional[float]:
    """Menor `t` (distinto de `inf`) con exactitud selectiva >= `piso` y >= `min_aceptados`."""
    candidatos = [
        f["umbral"]
        for f in barrido
        if f["umbral"] != float("inf")
        and f["aceptados"] >= min_aceptados
        and f["exactitud_selectiva"] is not None
        and f["exactitud_selectiva"] >= piso
    ]
    return min(candidatos) if candidatos else None


def evaluar_fuera_de_muestra_gate(
    umbral: Optional[float],
    senales: Sequence[float],
    aciertos: Sequence[bool],
    *,
    piso: float,
    n_total_corpus: int,
    min_aceptados: int = MIN_ACEPTADOS,
) -> dict:
    """Evalua SIN reajuste el umbral elegido dentro de la muestra (resultado de tres vias).

    No recibe candidatos: no puede reelegir el umbral con estos datos. Si `umbral` es `None`
    (nada cumplio el piso dentro de la muestra) el veredicto es «sin umbral seleccionado».
    """
    if umbral is None:
        return {"umbral": None, "veredicto": "sin umbral seleccionado"}
    fila = barrido_umbral(senales, aciertos, [umbral], n_total_corpus=n_total_corpus)[0]
    sel, der = fila["exactitud_selectiva"], fila["exactitud_derivados"]
    if fila["aceptados"] < min_aceptados or fila["derivados"] == 0:
        veredicto = "no estimable"
    elif sel >= piso and der < sel:
        veredicto = "confirmado"
    else:
        veredicto = "no confirmado"
    return {**fila, "piso": piso, "min_aceptados": min_aceptados, "veredicto": veredicto}


# ---------------------------------------------------------------------------
# Recalibracion isotonica (solo correccion de nivel)
# ---------------------------------------------------------------------------
def ajustar_isotonica(
    senales: Sequence[float], aciertos: Sequence[bool]
) -> list[tuple[float, float]]:
    """Regresion isotonica (PAVA ponderada) de aciertos sobre la senal.

    Devuelve `[(x, valor)]` con un punto por valor distinto de la senal, no decreciente.
    """
    _validar(senales, aciertos)
    por_x: dict[float, list[float]] = {}
    for s, a in zip(senales, aciertos):
        acumulado = por_x.setdefault(s, [0.0, 0.0])
        acumulado[0] += 1.0 if a else 0.0
        acumulado[1] += 1.0
    xs = sorted(por_x)
    bloques: list[list] = []  # [suma, peso, [xs del bloque]]
    for x in xs:
        bloques.append([por_x[x][0], por_x[x][1], [x]])
        while len(bloques) > 1 and (
            bloques[-2][0] / bloques[-2][1] > bloques[-1][0] / bloques[-1][1]
        ):
            ultimo = bloques.pop()
            bloques[-1][0] += ultimo[0]
            bloques[-1][1] += ultimo[1]
            bloques[-1][2].extend(ultimo[2])
    return [(x, b[0] / b[1]) for b in bloques for x in b[2]]


def aplicar_isotonica(
    modelo: Sequence[tuple[float, float]], senales: Sequence[float]
) -> list[float]:
    """Funcion escalon: valor del mayor `x` ajustado <= senal (el primero si esta por debajo)."""
    if not modelo:
        raise ValueError("el modelo isotonico esta vacio.")
    salida: list[float] = []
    for s in senales:
        valor = modelo[0][1]
        for x, v in modelo:
            if x <= s:
                valor = v
            else:
                break
        salida.append(valor)
    return salida
