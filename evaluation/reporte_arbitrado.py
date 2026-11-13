"""
Reporte de la validacion fuera de muestra sobre el corpus arbitrado (c-206, tarea 6.2).

Corre `evaluar_fuera_de_muestra` con el cache arbitrado y reporta el **n efectivo sin
exclusion** (los `47` discordantes ya no se excluyen: `E5` fija su referencia) y las **metricas
por clase** (exactitud estricta y laxa con IC de Wilson de cada sector canonico, agrupando por
`sector_asignado` de referencia). Reutiliza `evaluation.campana.evaluar_fuera_de_muestra` y
`evaluation.metrics.resumen_exactitud`: no reclasifica ni toca el clasificador.

No invoca a Gemini: lee las predicciones persistidas. Cuando todavia no existe el cache
arbitrado, declara "no se obtuvo" nombrando el artefacto faltante en vez de sustituirlo.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass
from typing import Mapping, Sequence

from evaluation.campana import FueraDeMuestraError, cargar_corpus_solo_lectura, evaluar_fuera_de_muestra
from evaluation.corpus import SECTORES_CANONICOS
from evaluation.metrics import MIN_SOPORTE_ESTIMABLE, resumen_exactitud
from evaluation.run_evaluation import cargar_predicciones

#: Pines del cache in-sample (el cache de v9 no registra pines; ver README de la campana).
PINES_IN_SAMPLE: Mapping[str, str] = {"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
RANGO_GOOGLE_GENAI_VIGENTE = ">=2.33,<3"

EXIT_OK = 0
EXIT_NO_OBTENIDO = 2

RUTA_PREDICCIONES_IN_SAMPLE = pathlib.Path("evaluation/data/campana/predicciones_in_sample.json")
RUTA_CORPUS_AJUSTE = pathlib.Path("data/corpus_evaluacion_pseudonimizado.json")
RUTA_PREDICCIONES_ARBITRADO = pathlib.Path("evaluation/data/campana/predicciones_arbitrado.json")
RUTA_CORPUS_ARBITRADO = pathlib.Path("evaluation/data/campana/corpus_independiente_arbitrado.json")


@dataclass(frozen=True)
class ResumenClase:
    """Metricas de un sector de referencia en el bloque fuera de muestra."""

    sector: str
    n: int
    aciertos_estrictos: int
    aciertos_laxos: int
    exactitud_estricta: float | None
    ic_estricta: tuple[float, float] | None
    exactitud_laxa: float | None
    estimable: bool


@dataclass(frozen=True)
class ReporteArbitrado:
    """Resultado de `evaluar_fuera_de_muestra` con el desglose por clase del corpus arbitrado."""

    obtenido: bool
    motivo: str | None
    n_efectivo: int
    exactitud_estricta: float | None
    ic_estricta: tuple[float, float] | None
    exactitud_laxa: float | None
    ic_laxa: tuple[float, float] | None
    por_clase: tuple[ResumenClase, ...]


def resumir_fuera_de_muestra_arbitrado(
    predicciones_in_sample: pathlib.Path | str,
    corpus_ajuste: pathlib.Path | str,
    predicciones_arbitrado: pathlib.Path | str,
    corpus_arbitrado: pathlib.Path | str,
    *,
    pines_in_sample: Mapping[str, str] | None = None,
    rango_google_genai_vigente: str | None = None,
    commit_in_sample: str | None = None,
) -> ReporteArbitrado:
    """Corre la validacion fuera de muestra y resume el n efectivo y las metricas por clase.

    Devuelve un `ReporteArbitrado` con `obtenido=False` (y el motivo) cuando falta un artefacto
    o el clasificador no esta congelado, en vez de propagar la excepcion: el reporte nunca se
    sustituye por datos in-sample.
    """
    try:
        resultado = evaluar_fuera_de_muestra(
            predicciones_in_sample,
            corpus_ajuste,
            predicciones_arbitrado,
            corpus_arbitrado,
            pines_in_sample=pines_in_sample if pines_in_sample is not None else PINES_IN_SAMPLE,
            rango_google_genai_vigente=(
                rango_google_genai_vigente
                if rango_google_genai_vigente is not None
                else RANGO_GOOGLE_GENAI_VIGENTE
            ),
            commit_in_sample=commit_in_sample,
        )
    except FueraDeMuestraError as exc:
        return ReporteArbitrado(False, str(exc), 0, None, None, None, None, ())
    if not resultado.obtenido:
        return ReporteArbitrado(False, resultado.motivo, 0, None, None, None, None, ())

    oos = resultado.out_of_sample
    predicciones = cargar_predicciones(predicciones_arbitrado)
    verdad = {caso.id: caso.conjunto_verdad for caso in cargar_corpus_solo_lectura(corpus_arbitrado)}
    por_clase = []
    for sector in SECTORES_CANONICOS:
        del_sector = [p for p in predicciones if p.sector_asignado == sector]
        resumen = resumen_exactitud(
            [p.sector_asignado for p in del_sector],
            [p.sector_predicho for p in del_sector],
            [verdad[p.caso_id] for p in del_sector],
        )
        por_clase.append(
            ResumenClase(
                sector=sector,
                n=resumen.casos,
                aciertos_estrictos=resumen.aciertos_estrictos,
                aciertos_laxos=resumen.aciertos_laxos,
                exactitud_estricta=resumen.exactitud_estricta,
                ic_estricta=tuple(resumen.ic_estricta) if resumen.ic_estricta else None,
                exactitud_laxa=resumen.exactitud_laxa,
                estimable=resumen.casos >= MIN_SOPORTE_ESTIMABLE,
            )
        )
    return ReporteArbitrado(
        obtenido=True,
        motivo=None,
        n_efectivo=oos.casos,
        exactitud_estricta=oos.resumen.exactitud_estricta,
        ic_estricta=tuple(oos.resumen.ic_estricta) if oos.resumen.ic_estricta else None,
        exactitud_laxa=oos.resumen.exactitud_laxa,
        ic_laxa=tuple(oos.resumen.ic_laxa) if oos.resumen.ic_laxa else None,
        por_clase=tuple(por_clase),
    )


def _pct(valor: float | None) -> str:
    return "no estimable" if valor is None else f"{valor * 100:.2f} %"


def _ic(intervalo: tuple[float, float] | None) -> str:
    return "n/a" if intervalo is None else f"[{intervalo[0]:.4f}; {intervalo[1]:.4f}]"


def formatear_reporte(reporte: ReporteArbitrado) -> str:
    """Reporte legible en texto (sin emojis) del n efectivo y las metricas por clase."""
    if not reporte.obtenido:
        return f"no se obtuvo la evaluacion fuera de muestra: {reporte.motivo}"
    lineas = [
        f"n efectivo (sin exclusion): {reporte.n_efectivo}",
        f"exactitud estricta global: {_pct(reporte.exactitud_estricta)} IC Wilson {_ic(reporte.ic_estricta)}",
        f"exactitud laxa global: {_pct(reporte.exactitud_laxa)} IC Wilson {_ic(reporte.ic_laxa)}",
        "",
        "metricas por clase (sector de referencia):",
    ]
    for clase in reporte.por_clase:
        estado = "estimable" if clase.estimable else "no estimable (soporte < 2)"
        lineas.append(
            f"- {clase.sector}: n={clase.n}; estricta {clase.aciertos_estrictos}/{clase.n} "
            f"({_pct(clase.exactitud_estricta)}) IC {_ic(clase.ic_estricta)}; "
            f"laxa {clase.aciertos_laxos}/{clase.n}; {estado}"
        )
    return "\n".join(lineas)


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI. Imprime el reporte y devuelve `0` o `2` si no se obtuvo."""
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.reporte_arbitrado",
        description=(
            "Validacion fuera de muestra del corpus arbitrado (c-206, tarea 6.2): n efectivo "
            "sin exclusion y metricas por clase. Sin red y sin Gemini."
        ),
    )
    parser.add_argument("--predicciones-in-sample", type=pathlib.Path, default=RUTA_PREDICCIONES_IN_SAMPLE)
    parser.add_argument("--corpus-ajuste", type=pathlib.Path, default=RUTA_CORPUS_AJUSTE)
    parser.add_argument("--predicciones-arbitrado", type=pathlib.Path, default=RUTA_PREDICCIONES_ARBITRADO)
    parser.add_argument("--corpus-arbitrado", type=pathlib.Path, default=RUTA_CORPUS_ARBITRADO)
    args = parser.parse_args(argv)
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    reporte = resumir_fuera_de_muestra_arbitrado(
        args.predicciones_in_sample,
        args.corpus_ajuste,
        args.predicciones_arbitrado,
        args.corpus_arbitrado,
    )
    print(formatear_reporte(reporte))
    return EXIT_OK if reporte.obtenido else EXIT_NO_OBTENIDO


if __name__ == "__main__":
    raise SystemExit(main())
