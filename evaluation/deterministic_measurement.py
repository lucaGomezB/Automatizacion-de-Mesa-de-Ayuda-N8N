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
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

from evaluation.corpus import CasoEvaluacion
from evaluation.metrics import CLASES

#: Piso de precision por defecto del cortocircuito (OQ1).
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


def umbrales_candidatos(
    observaciones: Iterable[ObservacionDeterminista],
) -> List[float]:
    """Umbrales candidatos: las confianzas observadas + 1.0, ordenados."""
    candidatos = {1.0}
    for obs in observaciones:
        if _es_cortocircuitable(obs):
            candidatos.add(round(obs.confianza, 6))
    return sorted(candidatos)


def punto_en_umbral(
    observaciones: Sequence[ObservacionDeterminista],
    umbral: float,
) -> PuntoCurva:
    """Punto de la curva en un umbral: cobertura y precision estricta."""
    total = len(observaciones)
    subconjunto = [
        obs
        for obs in observaciones
        if _es_cortocircuitable(obs) and obs.confianza >= umbral
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


def curva_precision_cobertura(
    observaciones: Sequence[ObservacionDeterminista],
    umbrales: Optional[Iterable[float]] = None,
) -> List[PuntoCurva]:
    """Curva precision/cobertura del subconjunto cortocircuitable."""
    if umbrales is None:
        umbrales = umbrales_candidatos(observaciones)
    return [punto_en_umbral(observaciones, u) for u in sorted(set(umbrales))]


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
    """Corre la calibracion offline y escribe el reporte (sin Gemini)."""
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
