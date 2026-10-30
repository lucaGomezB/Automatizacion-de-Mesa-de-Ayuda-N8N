"""
Kappa de Cohen entre los etiquetadores nuevos del doble etiquetado (c-167, D4).

Kappa no ponderado, con las cinco clases de `SECTORES_CANONICOS`, sobre la etiqueta
primaria (`sector_etiquetado`) y con exactamente dos etiquetadores fijos. Son funciones
puras: reciben datos ya cargados y no hacen I/O.

- `kappa_cohen(pares)`: kappa de una lista de pares `(etiqueta_E1, etiqueta_E2)`.
- `kappa_doble_etiquetado(registros)`: lo mismo desde las filas `tarea = doble_etiquetado`
  de la planilla de C1 (exige exactamente dos `id_etiquetador`).
- `parear_doble_etiquetado(registros)`: los dos registros de cada caso (los reutiliza
  `evaluation/campana.py` para armar la referencia del consenso).

Cada resultado trae kappa, p_o, p_e, PABAK = (k p_o - 1) / (k - 1) con k = 5, n, el IC
asintotico con la varianza bajo H1 de Fleiss, Cohen y Everitt (1969), el IC bootstrap
percentil por casos (`SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP` de `metrics.py`, con las
remuestras de p_e = 1 descartadas y contadas), el rotulo de Landis y Koch del valor puntual y
las declaraciones de alcance: Fleiss queda fuera y este es el kappa de los etiquetadores
NUEVOS, no un IC del 0,87 original.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from statistics import NormalDist
from typing import Mapping, Sequence

from evaluation.corpus import SECTORES_CANONICOS
from evaluation.doble_etiquetado import TAREA_DOBLE_ETIQUETADO
from evaluation.metrics import (
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)

#: Cantidad de clases (k) del kappa y del PABAK: las cinco canonicas.
N_CLASES: int = len(SECTORES_CANONICOS)

_INDICE_DE_CLASE: dict[str, int] = {sector: i for i, sector in enumerate(SECTORES_CANONICOS)}

#: Fraccion maxima de remuestras degeneradas (p_e = 1) que tolera el IC bootstrap.
UMBRAL_DEGENERADAS: float = 0.05

#: Categorias de Landis y Koch (1977), de menor a mayor acuerdo.
ROTULOS_LANDIS_KOCH: tuple[str, ...] = (
    "pobre",
    "leve",
    "aceptable",
    "moderado",
    "sustancial",
    "casi perfecto",
)
#: Limite superior (incluido) de cada categoria salvo la primera y la ultima.
_LIMITES_LANDIS_KOCH: tuple[float, ...] = (0.20, 0.40, 0.60, 0.80)

#: Declaraciones que acompanan todo resultado de kappa (proposal, "Declaracion sobre el kappa").
DECLARACION_FLEISS: str = (
    "Fleiss fuera del alcance: el kappa se calcula solo para exactamente dos etiquetadores."
)
DECLARACION_ALCANCE: str = "kappa de etiquetadores nuevos, no IC del 0,87 original"
DECLARACIONES: tuple[str, ...] = (DECLARACION_FLEISS, DECLARACION_ALCANCE)


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoKappa:
    """
    Kappa de Cohen sobre `n` pares de etiquetas.

    Con p_e = 1 (un unico sector usado por ambos) el kappa no es estimable: `kappa`,
    `error_estandar`, los dos IC y los rotulos quedan vacios, y `p_o`, `p_e` y `pabak`
    se informan igual. `bootstrap_computable` es False cuando el IC bootstrap no se emite
    (kappa no estimable o mas del 5 % de remuestras degeneradas) y `motivo_bootstrap`
    dice por que.
    """

    n: int
    kappa: float | None
    p_o: float
    p_e: float
    error_estandar: float | None
    ic_asintotico: tuple[float, float] | None
    nivel_confianza: float
    ic_bootstrap: tuple[float, float] | None
    bootstrap_computable: bool
    motivo_bootstrap: str | None
    remuestras_degeneradas: int
    remuestreos: int
    semilla: int
    pabak: float
    rotulo: str | None
    rotulos_ic_asintotico: tuple[str, ...]
    rotulos_ic_bootstrap: tuple[str, ...]
    nota_rotulo_ic: str | None
    etiquetadores: tuple[str, ...] = ()
    declaraciones: tuple[str, ...] = DECLARACIONES


# ---------------------------------------------------------------------------
# Rotulos de Landis y Koch
# ---------------------------------------------------------------------------
def rotulo_landis_koch(valor: float) -> str:
    """
    Rotulo de Landis y Koch (1977) de un valor de kappa.

    pobre (< 0); leve [0; 0,20]; aceptable (0,20; 0,40]; moderado (0,40; 0,60];
    sustancial (0,60; 0,80]; casi perfecto (0,80; 1]. Cada categoria incluye su limite
    superior.
    """
    if valor < 0.0:
        return ROTULOS_LANDIS_KOCH[0]
    for rotulo, limite_superior in zip(ROTULOS_LANDIS_KOCH[1:], _LIMITES_LANDIS_KOCH):
        if valor <= limite_superior:
            return rotulo
    return ROTULOS_LANDIS_KOCH[-1]


def _rotulos_del_intervalo(intervalo: tuple[float, float] | None) -> tuple[str, ...]:
    """Categorias que abarca un IC, de la de su limite inferior a la de su limite superior."""
    if intervalo is None:
        return ()
    inferior = ROTULOS_LANDIS_KOCH.index(rotulo_landis_koch(intervalo[0]))
    superior = ROTULOS_LANDIS_KOCH.index(rotulo_landis_koch(intervalo[1]))
    return ROTULOS_LANDIS_KOCH[inferior : superior + 1]


def _enumerar(categorias: Sequence[str]) -> str:
    """'a', 'a y b' o 'a, b y c'."""
    if len(categorias) <= 1:
        return "".join(categorias)
    return ", ".join(categorias[:-1]) + " y " + categorias[-1]


def _nota_rotulo_ic(asintotico: Sequence[str], bootstrap: Sequence[str]) -> str:
    """Aclara que el rotulo es del valor puntual y que cada IC puede abarcar varias categorias."""
    bootstrap_texto = _enumerar(bootstrap) if bootstrap else "no computable"
    return (
        "El rotulo de Landis y Koch corresponde al valor puntual; el rotulo del IC puede abarcar "
        f"dos o mas categorias (IC asintotico: {_enumerar(asintotico)}; "
        f"IC bootstrap: {bootstrap_texto})."
    )


# ---------------------------------------------------------------------------
# Calculo
# ---------------------------------------------------------------------------
def _pabak(p_o: float) -> float:
    """PABAK = (k * p_o - 1) / (k - 1) con k = 5 clases."""
    return (N_CLASES * p_o - 1.0) / (N_CLASES - 1.0)


def _matriz_de_frecuencias(pares: Sequence[tuple[str, str]]) -> list[list[int]]:
    """Matriz k x k de frecuencias (filas = primer etiquetador, columnas = segundo)."""
    matriz = [[0] * N_CLASES for _ in range(N_CLASES)]
    for etiqueta_1, etiqueta_2 in pares:
        for etiqueta in (etiqueta_1, etiqueta_2):
            if etiqueta not in _INDICE_DE_CLASE:
                raise ValueError(
                    f"etiqueta no canonica: {etiqueta!r} (validas: {', '.join(SECTORES_CANONICOS)})."
                )
        matriz[_INDICE_DE_CLASE[etiqueta_1]][_INDICE_DE_CLASE[etiqueta_2]] += 1
    return matriz


def _varianza_bajo_h1(matriz: list[list[int]], kappa: float, p_e: float) -> float:
    """
    Varianza asintotica de kappa bajo H1 (Fleiss, Cohen y Everitt, 1969).

    Var(k) = [ sum_i p_ii (1 - (p_i. + p_.i)(1 - k))^2
               + (1 - k)^2 sum_{i != j} p_ij (p_.i + p_j.)^2
               - (k - p_e (1 - k))^2 ] / (n (1 - p_e)^2)

    Un valor negativo por redondeo (diagonal perfecta) se lleva a 0.
    """
    n = sum(sum(fila) for fila in matriz)
    p = [[matriz[i][j] / n for j in range(N_CLASES)] for i in range(N_CLASES)]
    fila = [sum(p[i]) for i in range(N_CLASES)]
    columna = [sum(p[i][j] for i in range(N_CLASES)) for j in range(N_CLASES)]
    diagonal = sum(
        p[i][i] * (1.0 - (fila[i] + columna[i]) * (1.0 - kappa)) ** 2 for i in range(N_CLASES)
    )
    fuera_de_la_diagonal = (1.0 - kappa) ** 2 * sum(
        p[i][j] * (columna[i] + fila[j]) ** 2
        for i in range(N_CLASES)
        for j in range(N_CLASES)
        if i != j
    )
    centrado = (kappa - p_e * (1.0 - kappa)) ** 2
    varianza = (diagonal + fuera_de_la_diagonal - centrado) / (n * (1.0 - p_e) ** 2)
    return max(varianza, 0.0)


def _ic_asintotico(
    kappa: float, error_estandar: float, nivel_confianza: float
) -> tuple[float, float]:
    """IC kappa +- z * SE con los limites recortados al rango valido [-1, 1]."""
    z = NormalDist().inv_cdf(1.0 - (1.0 - nivel_confianza) / 2.0)
    return (
        max(-1.0, kappa - z * error_estandar),
        min(1.0, kappa + z * error_estandar),
    )


def _kappa_bootstrap(
    pares: Sequence[tuple[str, str]],
    semilla: int,
    remuestreos: int,
    nivel_confianza: float,
) -> tuple[tuple[float, float] | None, str | None, int]:
    """
    IC bootstrap percentil por casos del kappa.

    Se remuestrean los PARES (casos) con reemplazo. Las remuestras con p_e = 1 no tienen
    kappa: se descartan y se cuentan; si superan `UMBRAL_DEGENERADAS` de los remuestreos
    el IC no se emite.

    Returns:
        `(intervalo, motivo_de_no_computable, remuestras_degeneradas)`; el intervalo es
        None cuando no es computable y entonces el motivo lo explica.
    """
    clases = [(_INDICE_DE_CLASE[a], _INDICE_DE_CLASE[b]) for a, b in pares]
    n = len(clases)
    generador = random.Random(semilla)
    valores: list[float] = []
    degeneradas = 0
    for indices in remuestreos_indices(generador, n, remuestreos):
        filas = [0] * N_CLASES
        columnas = [0] * N_CLASES
        aciertos = 0
        for i in indices:
            fila, columna = clases[i]
            filas[fila] += 1
            columnas[columna] += 1
            aciertos += fila == columna
        acuerdo_esperado = sum(f * c for f, c in zip(filas, columnas))
        if acuerdo_esperado == n * n:
            degeneradas += 1
            continue
        p_e = acuerdo_esperado / (n * n)
        valores.append((aciertos / n - p_e) / (1.0 - p_e))
    if degeneradas > UMBRAL_DEGENERADAS * remuestreos:
        motivo = (
            f"IC bootstrap no computable: {degeneradas} de {remuestreos} remuestras "
            f"degeneradas (p_e = 1), mas del {UMBRAL_DEGENERADAS:.0%} admitido."
        )
        return None, motivo, degeneradas
    return percentil_intervalo(valores, nivel_confianza), None, degeneradas


def kappa_cohen(
    pares: Sequence[tuple[str, str]],
    nivel_confianza: float = NIVEL_CONFIANZA,
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> ResultadoKappa:
    """
    Kappa de Cohen no ponderado de los pares `(etiqueta_E1, etiqueta_E2)`.

    Raises:
        ValueError: Sin pares o con una etiqueta fuera de las cinco canonicas.
    """
    matriz = _matriz_de_frecuencias(pares)
    n = sum(sum(fila) for fila in matriz)
    if n == 0:
        raise ValueError("no hay pares de etiquetas: el kappa necesita al menos un caso.")
    filas = [sum(fila) for fila in matriz]
    columnas = [sum(matriz[i][j] for i in range(N_CLASES)) for j in range(N_CLASES)]
    p_o = sum(matriz[i][i] for i in range(N_CLASES)) / n
    # p_e = 1 solo ocurre con un unico sector usado por ambos: se detecta en enteros, sin
    # depender del redondeo de punto flotante.
    acuerdo_esperado = sum(filas[i] * columnas[i] for i in range(N_CLASES))
    p_e = acuerdo_esperado / (n * n)

    kappa: float | None = None
    error_estandar: float | None = None
    ic_asintotico: tuple[float, float] | None = None
    ic_bootstrap: tuple[float, float] | None = None
    motivo_bootstrap: str | None = "kappa no estimable (p_e = 1): no se calcula el IC bootstrap."
    degeneradas = 0
    if acuerdo_esperado != n * n:
        kappa = (p_o - p_e) / (1.0 - p_e)
        error_estandar = math.sqrt(_varianza_bajo_h1(matriz, kappa, p_e))
        ic_asintotico = _ic_asintotico(kappa, error_estandar, nivel_confianza)
        ic_bootstrap, motivo_bootstrap, degeneradas = _kappa_bootstrap(
            pares, semilla, remuestreos, nivel_confianza
        )

    rotulos_asintotico = _rotulos_del_intervalo(ic_asintotico)
    rotulos_bootstrap = _rotulos_del_intervalo(ic_bootstrap)
    return ResultadoKappa(
        n=n,
        kappa=kappa,
        p_o=p_o,
        p_e=p_e,
        error_estandar=error_estandar,
        ic_asintotico=ic_asintotico,
        nivel_confianza=nivel_confianza,
        ic_bootstrap=ic_bootstrap,
        bootstrap_computable=ic_bootstrap is not None,
        motivo_bootstrap=motivo_bootstrap,
        remuestras_degeneradas=degeneradas,
        remuestreos=remuestreos,
        semilla=semilla,
        pabak=_pabak(p_o),
        rotulo=None if kappa is None else rotulo_landis_koch(kappa),
        rotulos_ic_asintotico=rotulos_asintotico,
        rotulos_ic_bootstrap=rotulos_bootstrap,
        nota_rotulo_ic=(
            None if kappa is None else _nota_rotulo_ic(rotulos_asintotico, rotulos_bootstrap)
        ),
    )


# ---------------------------------------------------------------------------
# Kappa desde la planilla de etiquetado (C1, tarea = doble_etiquetado)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParDobleEtiquetado:
    """Los dos registros que los etiquetadores fijos dejaron sobre un mismo caso."""

    id_caso: str
    registro_1: Mapping[str, str]
    registro_2: Mapping[str, str]


def parear_doble_etiquetado(
    registros: Sequence[Mapping[str, str]],
) -> tuple[tuple[str, str], list[ParDobleEtiquetado]]:
    """
    Pares de registros de los dos etiquetadores de las filas `tarea = doble_etiquetado`.

    Exige exactamente dos `id_etiquetador` distintos, cada uno con una etiqueta canonica por
    caso, y falla con `ValueError` nombrando los alias, el caso o el sector. Los pares salen
    ordenados por `id_caso` (el resultado no depende del orden de las filas) y los alias,
    en orden alfabetico (`E1` antes que `E2`). Las filas de otras tareas se ignoran.
    """
    filas = [r for r in registros if r["tarea"] == TAREA_DOBLE_ETIQUETADO]
    etiquetadores = tuple(sorted({r["id_etiquetador"] for r in filas}))
    if len(etiquetadores) != 2:
        encontrados = ", ".join(etiquetadores) if etiquetadores else "ninguno"
        raise ValueError(
            "el kappa de Cohen exige exactamente dos id_etiquetador en tarea = "
            f"{TAREA_DOBLE_ETIQUETADO} y se encontraron {len(etiquetadores)} ({encontrados}); "
            "el kappa de Fleiss (mas de dos etiquetadores) queda fuera del alcance."
        )
    por_caso: dict[str, dict[str, Mapping[str, str]]] = {}
    for fila in filas:
        caso, alias = fila["id_caso"], fila["id_etiquetador"]
        registros_del_caso = por_caso.setdefault(caso, {})
        if alias in registros_del_caso:
            raise ValueError(f"el caso {caso} tiene mas de una etiqueta de {alias}.")
        if fila["sector_etiquetado"] not in _INDICE_DE_CLASE:
            raise ValueError(
                f"el caso {caso} tiene un sector no canonico de {alias}: "
                f"{fila['sector_etiquetado']!r} (validos: {', '.join(SECTORES_CANONICOS)})."
            )
        registros_del_caso[alias] = fila
    primero, segundo = etiquetadores
    pares: list[ParDobleEtiquetado] = []
    for caso in sorted(por_caso):
        for alias in etiquetadores:
            if alias not in por_caso[caso]:
                raise ValueError(f"el caso {caso} no tiene etiqueta de {alias}.")
        pares.append(ParDobleEtiquetado(caso, por_caso[caso][primero], por_caso[caso][segundo]))
    return (primero, segundo), pares


def kappa_doble_etiquetado(
    registros: Sequence[Mapping[str, str]],
    nivel_confianza: float = NIVEL_CONFIANZA,
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> ResultadoKappa:
    """
    Kappa de Cohen entre los dos etiquetadores del doble etiquetado (etiqueta primaria).

    `registros` son las filas de la planilla de C1; se usan solo las de `tarea =
    doble_etiquetado`. Ver `parear_doble_etiquetado` para las condiciones y los errores.
    """
    etiquetadores, pares = parear_doble_etiquetado(registros)
    resultado = kappa_cohen(
        [(par.registro_1["sector_etiquetado"], par.registro_2["sector_etiquetado"]) for par in pares],
        nivel_confianza,
        semilla=semilla,
        remuestreos=remuestreos,
    )
    return replace(resultado, etiquetadores=etiquetadores)
