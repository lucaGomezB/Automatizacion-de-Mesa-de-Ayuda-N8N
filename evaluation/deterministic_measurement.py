"""
Medicion y calibracion OFFLINE del clasificador deterministico (c-71).

Objetivo:
    Construir, sin invocar a Gemini, la curva de precision/cobertura del
    subconjunto cortocircuitable del clasificador deterministico sobre el
    corpus, elegir el umbral que maximiza cobertura sujeto a un PISO DE
    PRECISION (OQ1: >= 0.90) y reportar la cobertura del vocabulario.

Definiciones:
    - Cortocircuitable: caso con senal determinista (no `sin_prediccion`) y sin
      ambiguedad (`ambiguo == False`).
    - Precision del cortocircuito: exactitud ESTRICTA (`sector_predicho ==
      sector_asignado`) sobre el subconjunto que supera el umbral.
    - Cobertura: fraccion del corpus que el umbral cortocircuitaria.
    - Cobertura del vocabulario: fraccion de casos con al menos un match
      (`sin_prediccion == False`), global y por sector real.

El modulo es puro (no lee credenciales ni red) excepto `main()`, que importa el
clasificador real de forma diferida. Reutiliza `evaluation.corpus` y
`evaluation.metrics`; NO modifica `evaluation/corpus.py::_a_float`.
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

from evaluation.corpus import CasoEvaluacion
from evaluation.metrics import (
    CLASES,
    aciertos_estrictos,
    exactitud_global,
    exactitud_subconjunto,
    f1_macro,
    f1_micro,
    f1_por_clase,
    jaccard_promedio,
    matriz_confusion,
    perdida_hamming,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)

#: Piso de precision ABSOLUTO por defecto del cortocircuito (OQ1 de c-71).
#: c-74 (OQ3 revisado): RETIRADO como criterio de operacion. El punto de
#: operacion vigente es COMPARATIVO (`precision_det >= precision_gem`, ver
#: PROCEDENCIA_COMPARATIVA). Esta constante se conserva SOLO para los helpers de
#: curva absoluta heredados de c-71 (`elegir_umbral`, `seleccionar_umbral`,
#: `calibrar_out_of_fold`), que ya no gobiernan el cortocircuito.
PISO_PRECISION_DEFAULT = 0.90


class ClasificadorDeterministicoProtocol(Protocol):
    """Protocolo minimo del clasificador deterministico inyectable."""

    async def classify(self, descripcion: str) -> Any:
        ...


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ObservacionDeterminista:
    """Resultado deterministico de un caso, con su verdad multietiqueta."""

    caso_id: str
    sector_asignado: str
    verdad: frozenset[str]
    sector_predicho: Optional[str]
    confianza: float
    sin_prediccion: bool
    ambiguo: bool
    # c-74 (ASG-010): score de correctitud del determinista (ordena la
    # correctitud esperada; NO es una probabilidad calibrada).
    score: float = 0.0
    sectores_adicionales: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PuntoCurva:
    """Punto de la curva precision/cobertura para un umbral dado."""

    umbral: float
    cortocircuitados: int
    aciertos_estrictos: int
    precision: float
    cobertura: float


@dataclass(frozen=True)
class ResumenVocabulario:
    """Cobertura del vocabulario determinista sobre el corpus."""

    total: int
    sin_match: int
    cobertura_global: float
    cobertura_por_sector: Dict[str, float] = field(default_factory=dict)
    no_match_por_sector: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Recoleccion
# ---------------------------------------------------------------------------
async def recolectar_observaciones(
    corpus: Sequence[CasoEvaluacion],
    classifier: ClasificadorDeterministicoProtocol,
) -> List[ObservacionDeterminista]:
    """Corre el clasificador deterministico caso por caso (sin Gemini)."""
    observaciones: List[ObservacionDeterminista] = []
    for caso in corpus:
        resultado = await classifier.classify(caso.descripcion)
        observaciones.append(
            ObservacionDeterminista(
                caso_id=caso.id,
                sector_asignado=caso.sector_asignado,
                verdad=caso.conjunto_verdad,
                sector_predicho=getattr(resultado, "sector_predicho", None),
                confianza=float(resultado.confianza),
                sin_prediccion=bool(getattr(resultado, "sin_prediccion", False)),
                ambiguo=bool(getattr(resultado, "ambiguo", False)),
                score=float(getattr(resultado, "score_correctitud", 0.0)),
                sectores_adicionales=tuple(
                    getattr(resultado, "sectores_adicionales", []) or []
                ),
            )
        )
    return observaciones


# ---------------------------------------------------------------------------
# Curva y eleccion de umbral
# ---------------------------------------------------------------------------
def _es_cortocircuitable(obs: ObservacionDeterminista) -> bool:
    return not obs.sin_prediccion and not obs.ambiguo


def _umbrales_candidatos_para(
    observaciones: Iterable[ObservacionDeterminista],
    valor_fn: "Callable[[ObservacionDeterminista], float]",
) -> List[float]:
    """Umbrales candidatos genericos: los valores observados + 1.0, ordenados."""
    candidatos = {1.0}
    for obs in observaciones:
        if _es_cortocircuitable(obs):
            candidatos.add(round(valor_fn(obs), 6))
    return sorted(candidatos)


def umbrales_candidatos(
    observaciones: Iterable[ObservacionDeterminista],
) -> List[float]:
    """Umbrales candidatos sobre la confianza (fuerza de senal)."""
    return _umbrales_candidatos_para(observaciones, lambda obs: obs.confianza)


def umbrales_candidatos_score(
    observaciones: Iterable[ObservacionDeterminista],
) -> List[float]:
    """Umbrales candidatos sobre el score de correctitud (c-74).

    El score ORDENA la correctitud esperada; NO es una probabilidad calibrada.
    """
    return _umbrales_candidatos_para(observaciones, lambda obs: obs.score)


def _punto_para_valor(
    observaciones: Sequence[ObservacionDeterminista],
    umbral: float,
    valor_fn: "Callable[[ObservacionDeterminista], float]",
) -> PuntoCurva:
    """Punto de la curva en un umbral: cobertura y precision estricta."""
    total = len(observaciones)
    subconjunto = [
        obs
        for obs in observaciones
        if _es_cortocircuitable(obs) and valor_fn(obs) >= umbral
    ]
    cortocircuitados = len(subconjunto)
    aciertos = sum(1 for obs in subconjunto if obs.sector_predicho == obs.sector_asignado)
    precision = (aciertos / cortocircuitados) if cortocircuitados else 0.0
    cobertura = (cortocircuitados / total) if total else 0.0
    return PuntoCurva(
        umbral=umbral,
        cortocircuitados=cortocircuitados,
        aciertos_estrictos=aciertos,
        precision=precision,
        cobertura=cobertura,
    )


def punto_en_umbral(
    observaciones: Sequence[ObservacionDeterminista],
    umbral: float,
) -> PuntoCurva:
    """Punto de la curva sobre la confianza (compatibilidad c-71)."""
    return _punto_para_valor(observaciones, umbral, lambda obs: obs.confianza)


def punto_score_en_umbral(
    observaciones: Sequence[ObservacionDeterminista],
    umbral: float,
) -> PuntoCurva:
    """Punto de la curva sobre el score de correctitud (c-74).

    El score ORDENA la correctitud esperada; NO es una probabilidad calibrada.
    """
    return _punto_para_valor(observaciones, umbral, lambda obs: obs.score)


def _curva_para_valor(
    observaciones: Sequence[ObservacionDeterminista],
    valor_fn: "Callable[[ObservacionDeterminista], float]",
    umbrales: Optional[Iterable[float]],
) -> List[PuntoCurva]:
    if umbrales is None:
        umbrales = _umbrales_candidatos_para(observaciones, valor_fn)
    return [_punto_para_valor(observaciones, u, valor_fn) for u in sorted(set(umbrales))]


def curva_precision_cobertura(
    observaciones: Sequence[ObservacionDeterminista],
    umbrales: Optional[Iterable[float]] = None,
) -> List[PuntoCurva]:
    """Curva precision/cobertura sobre la confianza (compatibilidad c-71)."""
    return _curva_para_valor(observaciones, lambda obs: obs.confianza, umbrales)


def curva_precision_cobertura_score(
    observaciones: Sequence[ObservacionDeterminista],
    umbrales: Optional[Iterable[float]] = None,
) -> List[PuntoCurva]:
    """Curva precision/cobertura sobre el score de correctitud (c-74)."""
    return _curva_para_valor(observaciones, lambda obs: obs.score, umbrales)


def elegir_umbral(
    curva: Sequence[PuntoCurva],
    piso_precision: float = PISO_PRECISION_DEFAULT,
) -> Optional[float]:
    """
    Elige el umbral que maximiza cobertura sujeto al piso de precision.

    Prefiere PRECISION sobre cobertura ante conflicto (OQ1): solo considera
    puntos que igualan o superan el piso. Devuelve None si ningun umbral lo
    alcanza con al menos un caso cortocircuitado.
    """
    validos = [
        punto
        for punto in curva
        if punto.cortocircuitados > 0 and punto.precision >= piso_precision
    ]
    if not validos:
        return None
    mejor = max(validos, key=lambda p: (p.cobertura, -p.umbral))
    return mejor.umbral


# ---------------------------------------------------------------------------
# Calibracion con procedencia anti-fuga: cross-fitting out-of-fold (c-74, OQ2)
# ---------------------------------------------------------------------------
#: Procedencia elegida por el autor (OQ2): cross-fitting / conformal out-of-fold.
PROCEDENCIA_CROSS_FITTING = (
    "cross-fitting out-of-fold: el umbral de cada fold se calibra SOLO con los "
    "folds de entrenamiento (excluye el fold evaluado) y las metricas se "
    "reportan out-of-fold. El corpus de evaluacion (test reportado) nunca "
    "participa del ajuste de un caso evaluado."
)


@dataclass(frozen=True)
class PuntoFoldOOF:
    """Resultado de un fold: umbral ajustado fuera del fold y su evaluacion."""

    fold: int
    umbral: Optional[float]
    cortocircuitados: int
    aciertos_estrictos: int
    precision: float
    cobertura: float
    n_test: int


@dataclass(frozen=True)
class ResultadoCalibracionOOF:
    """Metricas out-of-fold del cortocircuito calibrado por cross-fitting."""

    n_folds: int
    piso_precision: float
    umbrales_por_fold: Tuple[Optional[float], ...]
    puntos: Tuple[PuntoFoldOOF, ...]
    cortocircuitados_oof: int
    aciertos_oof: int
    precision_oof: float
    cobertura_oof: float
    procedencia: str = PROCEDENCIA_CROSS_FITTING


def asignar_folds(
    observaciones: Sequence[ObservacionDeterminista],
    n_folds: int = 5,
) -> Dict[str, int]:
    """
    Asigna cada caso a un fold de forma DETERMINISTA y reproducible.

    El fold se deriva de la posicion del `caso_id` en el orden ordenado, de modo
    que la particion no depende del orden de recoleccion ni de aleatoriedad.
    """
    if n_folds < 2:
        raise ValueError("n_folds debe ser >= 2 para poder excluir un fold.")
    ids_ordenados = sorted(obs.caso_id for obs in observaciones)
    return {caso_id: idx % n_folds for idx, caso_id in enumerate(ids_ordenados)}


def seleccionar_umbral(
    entrenamiento: Sequence[ObservacionDeterminista],
    piso_precision: float = PISO_PRECISION_DEFAULT,
) -> Optional[float]:
    """
    Elige el umbral sobre el SCORE de correctitud en un conjunto de entrenamiento.

    Maximiza cobertura sujeto al piso de precision (misma politica que
    `elegir_umbral`). Es la operacion de "ajuste" del punto de operacion; en
    cross-fitting se invoca SOLO con los folds que excluyen el evaluado.
    """
    curva = curva_precision_cobertura_score(entrenamiento)
    return elegir_umbral(curva, piso_precision)


def calibrar_out_of_fold(
    observaciones: Sequence[ObservacionDeterminista],
    piso_precision: float = PISO_PRECISION_DEFAULT,
    n_folds: int = 5,
    asignacion: Optional[Dict[str, int]] = None,
) -> ResultadoCalibracionOOF:
    """
    Calibra el cortocircuito con cross-fitting y reporta metricas out-of-fold.

    Para cada fold se ajusta el umbral con los restantes (excluyendo el fold
    evaluado) y se aplica a ese fold. La metrica reportada se agrega sobre los
    folds evaluados, de modo que NINGUN caso se mide con un umbral que lo uso
    para ajustar (anti data leakage; evaluation-framework).
    """
    total = len(observaciones)
    if asignacion is None:
        folds = asignar_folds(observaciones, n_folds)
        n_folds_efectivo = n_folds
    else:
        folds = dict(asignacion)
        n_folds_efectivo = (max(folds.values()) + 1) if folds else 0

    umbrales: List[Optional[float]] = []
    puntos: List[PuntoFoldOOF] = []
    cortocircuitados_total = 0
    aciertos_total = 0

    for fold in range(n_folds_efectivo):
        entrenamiento = [o for o in observaciones if folds.get(o.caso_id) != fold]
        prueba = [o for o in observaciones if folds.get(o.caso_id) == fold]
        umbral = seleccionar_umbral(entrenamiento, piso_precision)
        subconjunto = [
            o
            for o in prueba
            if _es_cortocircuitable(o) and umbral is not None and o.score >= umbral
        ]
        cortocircuitados = len(subconjunto)
        aciertos = sum(
            1 for o in subconjunto if o.sector_predicho == o.sector_asignado
        )
        precision = (aciertos / cortocircuitados) if cortocircuitados else 0.0
        cobertura = (cortocircuitados / total) if total else 0.0
        umbrales.append(umbral)
        puntos.append(
            PuntoFoldOOF(
                fold=fold,
                umbral=umbral,
                cortocircuitados=cortocircuitados,
                aciertos_estrictos=aciertos,
                precision=precision,
                cobertura=cobertura,
                n_test=len(prueba),
            )
        )
        cortocircuitados_total += cortocircuitados
        aciertos_total += aciertos

    return ResultadoCalibracionOOF(
        n_folds=n_folds_efectivo,
        piso_precision=piso_precision,
        umbrales_por_fold=tuple(umbrales),
        puntos=tuple(puntos),
        cortocircuitados_oof=cortocircuitados_total,
        aciertos_oof=aciertos_total,
        precision_oof=(
            (aciertos_total / cortocircuitados_total) if cortocircuitados_total else 0.0
        ),
        cobertura_oof=(
            (cortocircuitados_total / total) if total else 0.0
        ),
    )


# ---------------------------------------------------------------------------
# Punto de operacion COMPARATIVO (c-74, OQ3 revisado)
# ---------------------------------------------------------------------------
#: Criterio elegido por el autor (OQ3 revisado): piso COMPARATIVO contra Gemini.
PROCEDENCIA_COMPARATIVA = (
    "piso comparativo out-of-fold: se maximiza la cobertura del subconjunto "
    "cortocircuitable S sujeta a precision_det(S) >= precision_gem(S), usando "
    "las predicciones de Gemini CACHEADAS (sin invocar al proveedor) y ajustando "
    "el umbral de cada fold SOLO con los folds de entrenamiento (excluye el fold "
    "evaluado). El corpus de evaluacion es el test reportado: no participa del "
    "ajuste."
)


@dataclass(frozen=True)
class PuntoComparativo:
    """Punto de operacion comparativo: cobertura sujeta al piso vs Gemini."""

    umbral: float
    cortocircuitados: int
    aciertos_det: int
    precision_det: float
    casos_gem: int
    aciertos_gem: int
    precision_gem: float
    cobertura: float
    cumple_piso_comparativo: bool


def _umbrales_candidatos_exactos(
    observaciones: Iterable[ObservacionDeterminista],
) -> List[float]:
    """Umbrales candidatos sobre el score EXACTO de los cortocircuitables.

    A diferencia de los helpers de curva, NO redondea: el minimo exacto define
    el punto de operacion que incluye el conjunto no ambiguo completo.
    """
    candidatos = {0.0}
    for obs in observaciones:
        if _es_cortocircuitable(obs):
            candidatos.add(float(obs.score))
    return sorted(candidatos)


def _punto_comparativo_para(
    observaciones: Sequence[ObservacionDeterminista],
    umbral: float,
    gemini_por_caso: "Mapping[str, Optional[str]]",
) -> PuntoComparativo:
    """Evalua un umbral sobre el score y compara determinista vs Gemini (cache)."""
    total = len(observaciones)
    subconjunto = [
        obs
        for obs in observaciones
        if _es_cortocircuitable(obs) and obs.score >= umbral
    ]
    cortocircuitados = len(subconjunto)
    aciertos_det = sum(
        1 for obs in subconjunto if obs.sector_predicho == obs.sector_asignado
    )
    precision_det = (aciertos_det / cortocircuitados) if cortocircuitados else 0.0

    casos_gem = 0
    aciertos_gem = 0
    for obs in subconjunto:
        prediccion_gem = gemini_por_caso.get(obs.caso_id)
        if prediccion_gem is None:
            continue
        casos_gem += 1
        if prediccion_gem == obs.sector_asignado:
            aciertos_gem += 1
    precision_gem = (aciertos_gem / casos_gem) if casos_gem else 0.0

    return PuntoComparativo(
        umbral=umbral,
        cortocircuitados=cortocircuitados,
        aciertos_det=aciertos_det,
        precision_det=precision_det,
        casos_gem=casos_gem,
        aciertos_gem=aciertos_gem,
        precision_gem=precision_gem,
        cobertura=(cortocircuitados / total) if total else 0.0,
        cumple_piso_comparativo=precision_det >= precision_gem,
    )


def curva_comparativa(
    observaciones: Sequence[ObservacionDeterminista],
    gemini_por_caso: "Mapping[str, Optional[str]]",
    umbrales: Optional[Iterable[float]] = None,
) -> List[PuntoComparativo]:
    """Curva del piso comparativo: det vs gem por umbral sobre el score."""
    if umbrales is None:
        umbrales = _umbrales_candidatos_exactos(observaciones)
    return [
        _punto_comparativo_para(observaciones, u, gemini_por_caso)
        for u in sorted(set(umbrales))
    ]


def elegir_punto_comparativo(
    curva: Sequence[PuntoComparativo],
) -> Optional[PuntoComparativo]:
    """
    Maximiza cobertura sujeta al piso comparativo (det >= gem).

    Ante empate de cobertura prefiere el umbral MAYOR (punto menos permisivo que
    cubre el mismo conjunto). Devuelve None si ningun punto cumple el piso.
    """
    validos = [
        punto
        for punto in curva
        if punto.cortocircuitados > 0 and punto.cumple_piso_comparativo
    ]
    if not validos:
        return None
    return max(validos, key=lambda p: (p.cobertura, p.umbral))


@dataclass(frozen=True)
class ResultadoComparativoOOF:
    """Metricas out-of-fold del punto de operacion comparativo."""

    n_folds: int
    umbrales_por_fold: Tuple[Optional[float], ...]
    cortocircuitados_oof: int
    aciertos_det_oof: int
    precision_det_oof: float
    casos_gem_oof: int
    aciertos_gem_oof: int
    precision_gem_oof: float
    cobertura_oof: float
    procedencia: str = PROCEDENCIA_COMPARATIVA


def calibrar_comparativo_out_of_fold(
    observaciones: Sequence[ObservacionDeterminista],
    gemini_por_caso: "Mapping[str, Optional[str]]",
    n_folds: int = 5,
    asignacion: Optional[Dict[str, int]] = None,
) -> ResultadoComparativoOOF:
    """
    Calibra el punto comparativo con cross-fitting y reporta metricas OOF.

    El umbral de cada fold se ajusta SOLO con los folds de entrenamiento
    (excluye el evaluado) y se aplica a ese fold. Ningun caso se mide con un
    umbral que lo uso para ajustar (anti data leakage).
    """
    total = len(observaciones)
    if asignacion is None:
        folds = asignar_folds(observaciones, n_folds)
        n_folds_efectivo = n_folds
    else:
        folds = dict(asignacion)
        n_folds_efectivo = (max(folds.values()) + 1) if folds else 0

    umbrales: List[Optional[float]] = []
    cc_total = 0
    ad_total = 0
    cg_total = 0
    ag_total = 0

    for fold in range(n_folds_efectivo):
        entrenamiento = [o for o in observaciones if folds.get(o.caso_id) != fold]
        prueba = [o for o in observaciones if folds.get(o.caso_id) == fold]
        punto = elegir_punto_comparativo(
            curva_comparativa(entrenamiento, gemini_por_caso)
        )
        umbral = punto.umbral if punto is not None else None
        umbrales.append(umbral)
        subconjunto = (
            [
                o
                for o in prueba
                if _es_cortocircuitable(o) and o.score >= umbral
            ]
            if umbral is not None
            else []
        )
        cc_total += len(subconjunto)
        for o in subconjunto:
            if o.sector_predicho == o.sector_asignado:
                ad_total += 1
            prediccion_gem = gemini_por_caso.get(o.caso_id)
            if prediccion_gem is not None:
                cg_total += 1
                if prediccion_gem == o.sector_asignado:
                    ag_total += 1

    return ResultadoComparativoOOF(
        n_folds=n_folds_efectivo,
        umbrales_por_fold=tuple(umbrales),
        cortocircuitados_oof=cc_total,
        aciertos_det_oof=ad_total,
        precision_det_oof=(ad_total / cc_total) if cc_total else 0.0,
        casos_gem_oof=cg_total,
        aciertos_gem_oof=ag_total,
        precision_gem_oof=(ag_total / cg_total) if cg_total else 0.0,
        cobertura_oof=(cc_total / total) if total else 0.0,
    )


# ---------------------------------------------------------------------------
# Tau CONGELADO derivado out-of-fold (c-74, W1)
# ---------------------------------------------------------------------------
#: Precision decimal (truncado HACIA ABAJO) del tau que se congela en Settings.
#: El score minimo exacto de un conjunto suele ser un decimal periodico
#: (p. ej. 0.516666...); se trunca hacia abajo para no excluir, por redondeo,
#: ningun caso cuyo score iguale ese minimo.
DECIMALES_TAU_SETTINGS = 4


def tau_oof_agregado(
    resultado: ResultadoComparativoOOF,
) -> Optional[float]:
    """
    Agrega los umbrales por fold out-of-fold en un unico tau (regla determinista).

    Si todos los folds con umbral viable coinciden, se usa ese valor; si
    discrepan, se toma el MINIMO (el punto menos restrictivo, que corresponde al
    minimo exacto de la union de casos cortocircuitables). Se ignoran los folds
    sin umbral viable (None). Devuelve None si ningun fold tuvo umbral.
    """
    validos = [u for u in resultado.umbrales_por_fold if u is not None]
    if not validos:
        return None
    return min(validos)


def umbral_de_settings_oof(
    resultado: ResultadoComparativoOOF,
    decimales: int = DECIMALES_TAU_SETTINGS,
) -> Optional[float]:
    """
    Deriva el tau CONGELADO en Settings a partir del resultado out-of-fold.

    Es la procedencia anti-fuga (evaluation-framework): el valor que gobierna el
    cortocircuito NO se elige in-sample sobre el corpus de test reportado, sino
    que se agrega de `ResultadoComparativoOOF.umbrales_por_fold` (cada fold se
    ajusta excluyendo su propio fold). El agregado se trunca hacia abajo a
    `decimales` para conservar el conjunto cortocircuitable completo (el valor
    exacto suele ser periodico). Devuelve None si no hay folds viables.
    """
    exacto = tau_oof_agregado(resultado)
    if exacto is None:
        return None
    factor = 10 ** decimales
    return math.floor(exacto * factor) / factor


# ---------------------------------------------------------------------------
# Re-medicion hibrida OFFLINE con la cache de Gemini (c-74, task 4.4)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PrediccionCacheada:
    """Prediccion de la etapa semantica persistida por el runner (C-34)."""

    sector_predicho: Optional[str]
    sectores_adicionales: Tuple[str, ...] = ()
    etapa: str = "gemini"


#: Cache OFICIAL del pipeline hibrido real, escrita por `run_evaluation.py`.
#: En hybrid-v3 los 131 casos cortocircuitables NO llaman a Gemini, por lo que
#: esta cache NO contiene predicciones semanticas sobre el conjunto
#: cortocircuitable (reutilizarla degenera `precision_gem(S)` a 0/0).
PREDICCIONES_OFICIALES_PATH = "evaluation/predicciones.json"

#: Cache FORCE-ESCALATE para la calibracion comparativa. Se genera con el
#: cortocircuito determinista deshabilitado (umbral de score alto), de modo que
#: TODOS los casos pasan por Gemini y la cache SI cubre el conjunto
#: cortocircuitable. Es la fuente valida de `precision_gem(S)`.
CALIBRACION_CACHE_PATH = "evaluation/predicciones_calibracion.json"


def resolver_cache_calibracion(repo_root) -> "pathlib.Path":
    """
    Resuelve la cache que debe usar la calibracion comparativa.

    Prefiere `evaluation/predicciones_calibracion.json` (FORCE-ESCALATE) cuando
    existe y cae a `evaluation/predicciones.json` (OFICIAL) en caso contrario.
    La corrida OFICIAL hybrid-v3 cortocircuita los casos cortocircuitables, por
    lo que su cache no permite estimar `precision_gem(S)`; la calibracion
    necesita predicciones de Gemini sobre ese conjunto (cache FORCE-ESCALATE).
    """
    import pathlib

    repo_root = pathlib.Path(repo_root)
    calibracion = repo_root / CALIBRACION_CACHE_PATH
    if calibracion.exists():
        return calibracion
    return repo_root / PREDICCIONES_OFICIALES_PATH


def cargar_predicciones_cacheadas(path) -> Dict[str, PrediccionCacheada]:
    """Carga la cache de `evaluation/predicciones.json` indexada por `caso_id`.

    Compatible con el formato del runner (`{"cache_meta": ..., "predictions": [...]}`)
    y con el arreglo plano heredado. NO invoca a Gemini.
    """
    import json
    import pathlib

    path = pathlib.Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("predictions") if isinstance(data, dict) else data
    cache: Dict[str, PrediccionCacheada] = {}
    for item in items or []:
        cache[str(item["caso_id"])] = PrediccionCacheada(
            sector_predicho=item.get("sector_predicho"),
            sectores_adicionales=tuple(item.get("sectores_adicionales") or []),
            etapa=str(item.get("etapa") or "gemini"),
        )
    return cache


def medir_hibrido_con_cache(
    observaciones: Sequence[ObservacionDeterminista],
    cache: "Mapping[str, PrediccionCacheada]",
    umbral_score: float,
) -> Dict[str, Any]:
    """
    Simula el pipeline hibrido con el punto de operacion dado, SIN Gemini.

    Los casos cortocircuitables con `score >= umbral_score` usan la prediccion
    determinista; el resto reutiliza la prediccion semantica CACHEADa (o None si
    no hay). Replica las metricas de `run_evaluation.generar_reporte`.
    """
    mix = {"deterministic": 0, "gemini": 0}
    reales: List[str] = []
    predichas: List[str] = []
    adicionales: List[List[str]] = []
    conjuntos_verdad: List[frozenset] = []
    conjuntos_predichos: List[frozenset] = []

    for obs in observaciones:
        if _es_cortocircuitable(obs) and obs.score >= umbral_score:
            mix["deterministic"] += 1
            predicho = obs.sector_predicho
            adic = list(obs.sectores_adicionales)
        else:
            mix["gemini"] += 1
            cached = cache.get(obs.caso_id)
            predicho = cached.sector_predicho if cached is not None else None
            adic = list(cached.sectores_adicionales) if cached is not None else []

        reales.append(obs.sector_asignado)
        predichas.append(predicho or "")
        adicionales.append(adic)
        conjuntos_verdad.append(obs.verdad)
        conjuntos_predichos.append(
            frozenset(e for e in (predicho, *adic) if e in CLASES)
        )

    pares = [(r, p) for r, p in zip(reales, predichas) if p in CLASES]
    mc = matriz_confusion([r for r, _ in pares], [p for _, p in pares])
    f1s = f1_por_clase(mc)
    return {
        "mix": mix,
        "exactitud_estricta": exactitud_global(reales, predichas),
        "aciertos_estrictos": aciertos_estrictos(reales, predichas),
        "f1_macro_estricto": f1_macro(f1s),
        "f1_micro": f1_micro(conjuntos_verdad, conjuntos_predichos),
        "subset_accuracy": exactitud_subconjunto(conjuntos_verdad, conjuntos_predichos),
        "hamming_loss": perdida_hamming(conjuntos_verdad, conjuntos_predichos),
        "jaccard_promedio": jaccard_promedio(conjuntos_verdad, conjuntos_predichos),
        "per_class": {
            sector: {
                "precision": precision_por_clase(mc)[sector],
                "sensibilidad": sensibilidad_por_clase(mc)[sector],
                "f1": f1s[sector],
                "soporte": soporte_por_clase(mc)[sector],
            }
            for sector in CLASES
        },
    }


# ---------------------------------------------------------------------------
# Cobertura del vocabulario
# ---------------------------------------------------------------------------
def resumen_vocabulario(
    observaciones: Sequence[ObservacionDeterminista],
) -> ResumenVocabulario:
    """Cobertura global y por sector real, y cantidad de casos sin match."""
    total = len(observaciones)
    sin_match = sum(1 for obs in observaciones if obs.sin_prediccion)

    cobertura_por_sector: Dict[str, float] = {}
    no_match_por_sector: Dict[str, int] = {}
    for sector in CLASES:
        del_sector = [obs for obs in observaciones if obs.sector_asignado == sector]
        faltantes = sum(1 for obs in del_sector if obs.sin_prediccion)
        no_match_por_sector[sector] = faltantes
        cobertura_por_sector[sector] = (
            (len(del_sector) - faltantes) / len(del_sector) if del_sector else 0.0
        )

    return ResumenVocabulario(
        total=total,
        sin_match=sin_match,
        cobertura_global=((total - sin_match) / total) if total else 0.0,
        cobertura_por_sector=cobertura_por_sector,
        no_match_por_sector=no_match_por_sector,
    )


# ---------------------------------------------------------------------------
# Metricas F1 del determinista (estricto y pertenencia)
# ---------------------------------------------------------------------------
def _f1_macro_desde_tp_fp_fn(
    tp: Dict[str, int], fp: Dict[str, int], fn: Dict[str, int]
) -> float:
    f1s = []
    for sector in CLASES:
        precision = tp[sector] / (tp[sector] + fp[sector]) if (tp[sector] + fp[sector]) else 0.0
        recall = tp[sector] / (tp[sector] + fn[sector]) if (tp[sector] + fn[sector]) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(CLASES)


def metricas_deterministas(
    observaciones: Sequence[ObservacionDeterminista],
) -> Dict[str, float]:
    """
    F1 macro estricto y de pertenencia del determinista (None cuenta como error).

    - Estricto: acierto si `sector_predicho == sector_asignado`.
    - Pertenencia: acierto si `sector_asignado` esta en el conjunto predicho.
    """
    tp_e = {s: 0 for s in CLASES}
    fp_e = {s: 0 for s in CLASES}
    fn_e = {s: 0 for s in CLASES}
    tp_p = {s: 0 for s in CLASES}
    fp_p = {s: 0 for s in CLASES}
    fn_p = {s: 0 for s in CLASES}

    for obs in observaciones:
        real = obs.sector_asignado
        predicho = obs.sector_predicho
        if predicho is not None and predicho in CLASES:
            if predicho == real:
                tp_e[predicho] += 1
            else:
                fp_e[predicho] += 1
                fn_e[real] += 1
        else:
            fn_e[real] += 1

        conjunto = {p for p in (predicho, *obs.sectores_adicionales) if p in CLASES}
        for sector in CLASES:
            if sector in conjunto and real == sector:
                tp_p[sector] += 1
            elif sector in conjunto and real != sector:
                fp_p[sector] += 1
        if real not in conjunto:
            fn_p[real] += 1

    exactitud_estricta = (
        sum(tp_e.values()) / len(observaciones) if observaciones else 0.0
    )
    exactitud_pertenencia = (
        sum(tp_p.values()) / len(observaciones) if observaciones else 0.0
    )
    return {
        "exactitud_estricta": exactitud_estricta,
        "exactitud_pertenencia": exactitud_pertenencia,
        "f1_macro_estricto": _f1_macro_desde_tp_fp_fn(tp_e, fp_e, fn_e),
        "f1_macro_pertenencia": _f1_macro_desde_tp_fp_fn(tp_p, fp_p, fn_p),
    }


# ---------------------------------------------------------------------------
# Punto de entrada offline (camino real, sin Gemini)
# ---------------------------------------------------------------------------
def cargar_corpus_tolerante(path) -> List[CasoEvaluacion]:
    """
    Carga el corpus admitiendo tiempos faltantes/None.

    `evaluation.corpus.cargar_corpus` exige tiempos numericos y NO se modifica
    (regla dura: `_a_float` intocable). El corpus real pseudonimizado tiene 56
    casos con `tiempo_automatizado_s: null`; esta carga tolerante reutiliza
    `CasoEvaluacion` (cuyos tiempos son Optional) y valida los sectores contra
    el vocabulario canonico sin tocar `_a_float`.
    """
    import json
    import pathlib

    from evaluation.corpus import CATEGORIAS_VALIDAS, CasoEvaluacion, CorpusError

    path = pathlib.Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el corpus de evaluacion en: {path}")

    documento = json.loads(path.read_text(encoding="utf-8"))
    casos: List[CasoEvaluacion] = []
    for item in documento["casos"]:
        sector = item["sector_asignado"]
        if sector not in CATEGORIAS_VALIDAS:
            raise CorpusError(
                f"Sector invalido '{sector}' en el caso id='{item.get('id')}'."
            )

        def _opt(valor: object):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                return None
            return float(valor)

        casos.append(
            CasoEvaluacion(
                id=str(item["id"]),
                descripcion=str(item["descripcion"]),
                sector_asignado=sector,
                sectores_adicionales=list(item.get("sectores_adicionales") or []),
                canal_origen=item.get("canal_origen"),
                tiempo_manual_s=_opt(item.get("tiempo_manual_s")),
                tiempo_automatizado_s=_opt(item.get("tiempo_automatizado_s")),
            )
        )
    return casos


def _cargar_corpus_real():
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent
    corpus_path = repo_root / "data" / "corpus_evaluacion_pseudonimizado.json"
    return cargar_corpus_tolerante(corpus_path)


def _resolver_clasificador_real() -> ClasificadorDeterministicoProtocol:
    import sys

    import pathlib

    backend_path = str(pathlib.Path(__file__).parent.parent / "App" / "Backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.classifiers.deterministic import DeterministicClassifier  # type: ignore

    return DeterministicClassifier()


def formatear_reporte(
    resumen: ResumenVocabulario,
    curva: Sequence[PuntoCurva],
    umbral_elegido: Optional[float],
    piso_precision: float,
    umbral_actual: Optional[float] = None,
    metricas: Optional[Dict[str, float]] = None,
) -> str:
    """Reporte textual de la calibracion y la cobertura del vocabulario."""
    lineas = [
        "# Calibracion offline del clasificador deterministico (c-71)",
        "",
        f"- Casos: {resumen.total}",
        f"- Casos sin match: {resumen.sin_match}",
        f"- Cobertura global del vocabulario: {resumen.cobertura_global:.4f}",
        f"- Piso de precision exigido (OQ1): {piso_precision:.2f}",
        f"- Umbral elegido: {umbral_elegido}",
    ]
    if umbral_actual is not None:
        lineas.append(f"- Umbral vigente en Settings: {umbral_actual}")
    if metricas is not None:
        lineas += [
            "",
            "## Metricas del determinista sobre el corpus (None = error)",
            "",
            f"- Exactitud estricta: {metricas['exactitud_estricta']:.4f}",
            f"- Exactitud de pertenencia: {metricas['exactitud_pertenencia']:.4f}",
            f"- F1 macro estricto: {metricas['f1_macro_estricto']:.4f}",
            f"- F1 macro de pertenencia: {metricas['f1_macro_pertenencia']:.4f}",
        ]
    lineas += ["", "## Cobertura por sector (real)", ""]
    for sector in CLASES:
        lineas.append(
            f"- {sector}: cobertura {resumen.cobertura_por_sector[sector]:.4f} "
            f"({resumen.no_match_por_sector[sector]} sin match)"
        )
    lineas += [
        "",
        "## Curva precision/cobertura (cortocircuito)",
        "",
        "| Umbral | Cortocircuitados | Aciertos | Precision | Cobertura |",
        "|--------|------------------|----------|-----------|-----------|",
    ]
    for punto in curva:
        lineas.append(
            f"| {punto.umbral:.4f} | {punto.cortocircuitados} | "
            f"{punto.aciertos_estrictos} | {punto.precision:.4f} | {punto.cobertura:.4f} |"
        )
    return "\n".join(lineas)


async def main(
    piso_precision: float = PISO_PRECISION_DEFAULT,
    output_path: Optional[str] = None,
    umbral_actual: Optional[float] = None,
) -> str:
    """Corre la calibracion comparativa offline y escribe el reporte (sin Gemini)."""
    import pathlib

    corpus = _cargar_corpus_real()
    classifier = _resolver_clasificador_real()
    observaciones = await recolectar_observaciones(corpus, classifier)

    resumen = resumen_vocabulario(observaciones)
    metricas_det = metricas_deterministas(observaciones)

    # Curva ABSOLUTA heredada (retirada como criterio de operacion).
    curva_legacy = curva_precision_cobertura(observaciones)
    umbral_legacy = elegir_umbral(curva_legacy, piso_precision)

    # Punto de operacion COMPARATIVO sobre la cache de Gemini (sin proveedor).
    repo_root = pathlib.Path(__file__).parent.parent
    cache_path = resolver_cache_calibracion(repo_root)
    cache = cargar_predicciones_cacheadas(cache_path)
    gem_map = {
        caso_id: (p.sector_predicho if p.etapa == "gemini" else None)
        for caso_id, p in cache.items()
    }
    curva_comp = curva_comparativa(observaciones, gem_map)

    # c-74 (W1): la calibracion OUT-OF-FOLD se calcula primero y es la fuente
    # del punto de operacion CONGELADO. El corpus de test reportado NO
    # selecciona el punto (procedencia anti-fuga; evaluation-framework).
    oof = calibrar_comparativo_out_of_fold(observaciones, gem_map)
    tau_oof = tau_oof_agregado(oof)
    tau_settings_oof = umbral_de_settings_oof(oof)

    from app.config.settings import get_settings  # noqa: E402  (path resuelto arriba)

    umbral_settings = get_settings().deterministic_score_threshold

    # Punto reportado anclado al tau OOF (NO `elegir_punto_comparativo` in-sample).
    punto = (
        _punto_comparativo_para(observaciones, tau_settings_oof, gem_map)
        if tau_settings_oof is not None
        else None
    )
    umbral_op = punto.umbral if punto is not None else None
    hibrido = (
        medir_hibrido_con_cache(observaciones, cache, umbral_score=umbral_op)
        if umbral_op is not None
        else None
    )

    contenido = formatear_reporte_comparativo(
        resumen=resumen,
        metricas_det=metricas_det,
        curva_legacy=curva_legacy,
        umbral_legacy=umbral_legacy,
        piso_precision=piso_precision,
        curva_comp=curva_comp,
        punto=punto,
        tau_oof=tau_oof,
        oof=oof,
        umbral_settings=umbral_settings,
        hibrido=hibrido,
        ruta_cache_calibracion=str(cache_path.relative_to(repo_root)),
    )
    print(contenido)
    if output_path is not None:
        pathlib.Path(output_path).write_text(contenido, encoding="utf-8")
    return contenido


def formatear_reporte_comparativo(
    *,
    resumen: ResumenVocabulario,
    metricas_det: Dict[str, float],
    curva_legacy: Sequence[PuntoCurva],
    umbral_legacy: Optional[float],
    piso_precision: float,
    curva_comp: Sequence[PuntoComparativo],
    punto: Optional[PuntoComparativo],
    oof: ResultadoComparativoOOF,
    umbral_settings: float,
    hibrido: Optional[Dict[str, Any]],
    tau_oof: Optional[float] = None,
    ruta_cache_calibracion: Optional[str] = None,
) -> str:
    """Reporte markdown de la calibracion comparativa y la re-medicion hibrida."""
    cache_mostrada = ruta_cache_calibracion or PREDICCIONES_OFICIALES_PATH
    lineas: List[str] = [
        "# Calibracion offline del clasificador deterministico (c-71 + c-74)",
        "",
        "> c-74 (OQ3 revisado): el punto de operacion es COMPARATIVO contra la",
        "> etapa semantica, no un piso ABSOLUTO. La calibracion corre offline y",
        "> reutiliza las predicciones de Gemini cacheadas (sin invocar al proveedor).",
        "",
        "## Corpus y cobertura del vocabulario",
        "",
        f"- Casos: {resumen.total}",
        f"- Casos sin match: {resumen.sin_match}",
        f"- Cobertura global del vocabulario: {resumen.cobertura_global:.4f}",
        "",
        "## Metricas del determinista sobre el corpus (None = error)",
        "",
        f"- Exactitud estricta: {metricas_det['exactitud_estricta']:.4f}",
        f"- Exactitud de pertenencia: {metricas_det['exactitud_pertenencia']:.4f}",
        f"- F1 macro estricto: {metricas_det['f1_macro_estricto']:.4f}",
        f"- F1 macro de pertenencia: {metricas_det['f1_macro_pertenencia']:.4f}",
        "",
        "## Punto de operacion COMPARATIVO (OQ3 revisado)",
        "",
        f"- Criterio: maximizar cobertura sujeta a `precision_det(S) >= precision_gem(S)`.",
        f"- Procedencia: {oof.procedencia}",
        "- Predicciones de Gemini: CACHEADAS; fuente FORCE-ESCALATE de la calibracion "
        f"en `{cache_mostrada}` (sin proveedor).",
        "- El tau congelado se DERIVA OUT-OF-FOLD: NO se elige in-sample sobre el corpus de test reportado.",
    ]

    if punto is not None:
        lineas += [
            f"- tau OOF exacto (agregado de folds): {tau_oof}",
            f"- tau aplicado (OOF, truncado hacia abajo a 4 decimales): {punto.umbral}",
            f"- Cobertura del punto: {punto.cobertura:.4f} "
            f"({punto.cortocircuitados}/{resumen.total})",
            f"- precision_det(S): {punto.precision_det:.4f} "
            f"({punto.aciertos_det}/{punto.cortocircuitados})",
            f"- precision_gem(S): {punto.precision_gem:.4f} "
            f"({punto.aciertos_gem}/{punto.casos_gem})",
        ]
    else:
        lineas.append("- SIN punto valido: ningun umbral OOF cumple el piso comparativo.")

    lineas += [
        f"- tau fijado en Settings (`deterministic_score_threshold`): {umbral_settings} "
        "(derivado OUT-OF-FOLD)",
        "",
        "## Calibracion comparativa out-of-fold (anti-fuga)",
        "",
        f"- Folds: {oof.n_folds}",
        f"- Umbrales por fold: {oof.umbrales_por_fold}",
        f"- Cobertura OOF: {oof.cobertura_oof:.4f} ({oof.cortocircuitados_oof}/{resumen.total})",
        f"- precision_det OOF: {oof.precision_det_oof:.4f} "
        f"({oof.aciertos_det_oof}/{oof.cortocircuitados_oof})",
        f"- precision_gem OOF: {oof.precision_gem_oof:.4f} "
        f"({oof.aciertos_gem_oof}/{oof.casos_gem_oof})",
        "",
        "## Curva comparativa (det vs gem por umbral)",
        "",
        "| Umbral | Cortocircuitados | Cobertura | precision_det | precision_gem | Cumple piso |",
        "|--------|------------------|-----------|---------------|---------------|-------------|",
    ]
    for p in curva_comp:
        lineas.append(
            f"| {p.umbral:.6f} | {p.cortocircuitados} | {p.cobertura:.4f} | "
            f"{p.precision_det:.4f} | {p.precision_gem:.4f} | "
            f"{'si' if p.cumple_piso_comparativo else 'no'} |"
        )

    if hibrido is not None:
        lineas += [
            "",
            "## Re-medicion hibrida OFFLINE con la cache de Gemini (task 4.4)",
            "",
            "| Etapa | Casos |",
            "|-------|-------|",
            f"| Deterministic (cortocircuito) | {hibrido['mix']['deterministic']} |",
            f"| Gemini (cache) | {hibrido['mix']['gemini']} |",
            "",
            "| Metrica | Valor |",
            "|---------|-------|",
            f"| Exactitud estricta | {hibrido['exactitud_estricta']:.4f} |",
            f"| F1 macro estricto | {hibrido['f1_macro_estricto']:.4f} |",
            f"| Micro-F1 (conjunto) | {hibrido['f1_micro']:.4f} |",
            f"| Subset accuracy | {hibrido['subset_accuracy']:.4f} |",
            f"| Hamming loss | {hibrido['hamming_loss']:.4f} |",
            f"| Jaccard promedio | {hibrido['jaccard_promedio']:.4f} |",
            "",
            "### Delta contra la linea base / policy-B",
            "",
            "| Comparacion | Baseline | c-74 | Delta |",
            "|-------------|----------|------|-------|",
            "| Cobertura del cortocircuito (piso absoluto c-71) | 0.0050 (1/200) | "
            f"{punto.cobertura:.4f} ({punto.cortocircuitados}/200) | "
            f"+{(punto.cobertura - 0.0050):.4f} |"
            if punto is not None
            else "| Cobertura | 0.0050 | n/d | n/d |",
            "| Macro-F1 hibrido (policy-B) | 0.5165 | "
            f"{hibrido['f1_macro_estricto']:.4f} | "
            f"{hibrido['f1_macro_estricto'] - 0.5165:+.4f} |",
            "| Micro-F1 (policy-B) | 0.6654 | "
            f"{hibrido['f1_micro']:.4f} | {hibrido['f1_micro'] - 0.6654:+.4f} |",
            "",
            "**Task 4.6 (COMPLETADA, 2026-10-07):** la corrida OFICIAL paga de",
            "`evaluation/run_evaluation.py` (hybrid-v3) se ejecuto y quedo registrada en",
            "`docs/deterministic_calibration.md`. Los valores de ESTA seccion son OFFLINE y",
            "reutilizan la cache FORCE-ESCALATE de Gemini; no se fabrica ningun resultado de",
            "proveedor. La cache OFICIAL hybrid-v3 no sirve para la calibracion: en esa",
            "corrida los cortocircuitables no llaman a Gemini (ver convencion de dos caches).",
        ]

    lineas += [
        "",
        "## Curva ABSOLUTA heredada (retirada como criterio de operacion)",
        "",
        f"- Piso absoluto (legacy): {piso_precision:.2f}",
        f"- Umbral legacy elegido: {umbral_legacy}",
        "",
        "| Umbral | Cortocircuitados | Aciertos | Precision | Cobertura |",
        "|--------|------------------|----------|-----------|-----------|",
    ]
    for p in curva_legacy:
        lineas.append(
            f"| {p.umbral:.4f} | {p.cortocircuitados} | {p.aciertos_estrictos} | "
            f"{p.precision:.4f} | {p.cobertura:.4f} |"
        )

    lineas += ["", "## Cobertura por sector (real)", ""]
    for sector in CLASES:
        lineas.append(
            f"- {sector}: cobertura {resumen.cobertura_por_sector[sector]:.4f} "
            f"({resumen.no_match_por_sector[sector]} sin match)"
        )
    return "\n".join(lineas)


async def _main_legacy(
    piso_precision: float = PISO_PRECISION_DEFAULT,
    output_path: Optional[str] = None,
    umbral_actual: Optional[float] = None,
) -> str:
    """Corre la calibracion absoluta heredada y escribe el reporte (sin Gemini)."""
    corpus = _cargar_corpus_real()
    classifier = _resolver_clasificador_real()
    observaciones = await recolectar_observaciones(corpus, classifier)
    curva = curva_precision_cobertura(observaciones)
    umbral_elegido = elegir_umbral(curva, piso_precision)
    resumen = resumen_vocabulario(observaciones)
    metricas = metricas_deterministas(observaciones)
    contenido = formatear_reporte(
        resumen,
        curva,
        umbral_elegido,
        piso_precision,
        umbral_actual=umbral_actual,
        metricas=metricas,
    )
    print(contenido)
    if output_path is not None:
        import pathlib

        pathlib.Path(output_path).write_text(contenido, encoding="utf-8")
    return contenido


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Calibracion offline del clasificador deterministico (sin Gemini)."
    )
    parser.add_argument("--piso-precision", type=float, default=PISO_PRECISION_DEFAULT)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--umbral-actual", type=float, default=None)
    args = parser.parse_args()
    asyncio.run(
        main(
            piso_precision=args.piso_precision,
            output_path=args.output,
            umbral_actual=args.umbral_actual,
        )
    )
