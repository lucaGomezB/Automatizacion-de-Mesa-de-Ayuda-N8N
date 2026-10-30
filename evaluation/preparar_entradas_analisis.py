"""
Ensambla las dos entradas que consume el analisis de campana (c-170, ECM-011..013).

El CLI de analisis de c-167 (`evaluation/analisis_campana.py`) lee dos entradas canonicas
de `evaluation/data/campana/` que ningun runbook de la campana producia:

- `plantilla_etiquetado.csv`: la union, bajo un unico encabezado C1, de las filas de
  `doble_etiquetado.csv` (`tarea = doble_etiquetado`) y de `brazo_manual.csv`
  (`tarea = brazo_manual`), preservando el orden de origen.
- `predicciones_in_sample.json`: copia **byte a byte** del cache congelado
  `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`.

El modulo es puro y offline: solo stdlib, `evaluation.corpus`, `evaluation.doble_etiquetado`
y `evaluation.plan_campana`. Re-valida cada tarea con `validar_doble_etiquetado` antes de
escribir, aborta con un error accionable que nombra el archivo (y la `tarea`) si una fuente
falta o no pasa el validador, y se niega a escribir sobre un artefacto congelado, sobre
`evaluation/evidence/**` o sobre sus propias fuentes.

CLI (desde la raiz del repositorio)::

    python -m evaluation.preparar_entradas_analisis \
      --entrada evaluation/data/campana \
      --corpus data/corpus_evaluacion_pseudonimizado.json \
      --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json

Imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente) y devuelve
`0`. Con las mismas fuentes, dos corridas producen salidas byte a byte identicas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Sequence

from evaluation.corpus import CasoEvaluacion, cargar_corpus
from evaluation.doble_etiquetado import (
    COLUMNAS_C1,
    TAREA_BRAZO_MANUAL,
    TAREA_DOBLE_ETIQUETADO,
    validar_doble_etiquetado,
)
from evaluation.plan_campana import RAIZ_REPO, es_archivo_congelado

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parent

#: Ruta por defecto de la carpeta de campana dentro de `evaluation/`.
RUTA_CAMPANA_POR_DEFECTO = RAIZ_EVALUATION / "data" / "campana"
#: Corpus contra el que se re-valida cada tarea.
RUTA_CORPUS_POR_DEFECTO = RAIZ_REPO / "data" / "corpus_evaluacion_pseudonimizado.json"
#: Cache congelado que se copia byte a byte como referencia in-sample.
RUTA_CACHE_IN_SAMPLE_POR_DEFECTO = (
    RAIZ_EVALUATION / "evidence" / "predicciones_hybrid-v3_2026-10-07.json"
)

#: Nombres canonicos de las fuentes y de las salidas dentro de la carpeta de campana.
NOMBRE_DOBLE_ETIQUETADO = "doble_etiquetado.csv"
NOMBRE_BRAZO_MANUAL = "brazo_manual.csv"
NOMBRE_PLANILLA = "plantilla_etiquetado.csv"
NOMBRE_IN_SAMPLE = "predicciones_in_sample.json"

#: Fuentes de la union C1, con la tarea con la que se re-valida cada una.
FUENTES_C1: tuple[tuple[str, str], ...] = (
    (NOMBRE_DOBLE_ETIQUETADO, TAREA_DOBLE_ETIQUETADO),
    (NOMBRE_BRAZO_MANUAL, TAREA_BRAZO_MANUAL),
)

#: Subcarpeta, relativa a la raiz del repo, en la que nunca se escribe.
SUBCARPETA_EVIDENCE = pathlib.Path("evaluation") / "evidence"


class PrepararEntradasError(ValueError):
    """Una entrada no cumple su contrato o el destino esta protegido.

    El mensaje nombra el archivo (y la `tarea`) para que el error sea accionable; el modulo
    aborta antes de escribir cualquier salida.
    """


@dataclass(frozen=True)
class Procedencia:
    """Fuente de una salida: ruta, SHA-256 y tarea (si aplica)."""

    ruta: pathlib.Path
    sha256: str
    tarea: str | None = None


@dataclass(frozen=True)
class EntradaProducida:
    """Una salida ensamblada con su SHA-256 y sus procedencias."""

    nombre: str
    ruta: pathlib.Path
    sha256: str
    procedencias: tuple[Procedencia, ...]


@dataclass(frozen=True)
class ResultadoPreparacion:
    """Las dos entradas producidas por `preparar_entradas`."""

    planilla: EntradaProducida
    in_sample: EntradaProducida


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _leer_csv(ruta: pathlib.Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        columnas = tuple(lector.fieldnames or ())
        filas = [dict(fila) for fila in lector]
    return columnas, filas


def _verificar_columnas(ruta: pathlib.Path, columnas: Sequence[str]) -> None:
    faltantes = [columna for columna in COLUMNAS_C1 if columna not in columnas]
    if faltantes:
        raise PrepararEntradasError(
            f"el archivo {ruta.name} no tiene la columna {faltantes[0]!r} "
            f"(columnas exigidas: {', '.join(COLUMNAS_C1)})."
        )


def _dentro_de_evidence(destino: pathlib.Path | str, raiz: pathlib.Path | str) -> bool:
    evidence = pathlib.Path(raiz).resolve() / SUBCARPETA_EVIDENCE
    candidatos = {
        pathlib.Path(destino).resolve(),
        (pathlib.Path(raiz) / destino).resolve(),
    }
    for candidato in candidatos:
        try:
            candidato.relative_to(evidence)
            return True
        except ValueError:
            pass
    return False


def _verificar_destino(
    destino: pathlib.Path, raiz: pathlib.Path | str, fuentes: Sequence[pathlib.Path] = ()
) -> None:
    if es_archivo_congelado(destino, raiz):
        raise PrepararEntradasError(
            f"el destino {destino} es un artefacto congelado y no se escribe sobre el; "
            "elegi otra ruta."
        )
    if _dentro_de_evidence(destino, raiz):
        raise PrepararEntradasError(
            f"el destino {destino} esta dentro de evaluation/evidence/ y no se escribe "
            "sobre el; elegi otra ruta."
        )
    resuelto = destino.resolve()
    for fuente in fuentes:
        if resuelto == pathlib.Path(fuente).resolve():
            raise PrepararEntradasError(
                f"el destino {destino} coincide con una fuente de solo lectura; "
                "elegi otra ruta."
            )


def _validar_fuente(
    ruta: pathlib.Path, tarea: str, corpus: Sequence[CasoEvaluacion]
) -> list[dict[str, str]]:
    if not ruta.is_file():
        raise PrepararEntradasError(
            f"falta el archivo fuente {ruta.name} (tarea={tarea}); la campana no puede "
            f"ensamblar {NOMBRE_PLANILLA} sin el."
        )
    columnas, filas = _leer_csv(ruta)
    _verificar_columnas(ruta, columnas)
    resultado = validar_doble_etiquetado(filas, corpus, tarea)
    if not resultado.valida:
        ofensa = resultado.ofensas[0]
        raise PrepararEntradasError(
            f"la planilla {ruta.name} (tarea={tarea}) no pasa validar_doble_etiquetado: "
            f"[regla {ofensa.regla}] id_caso={ofensa.id_caso} "
            f"id_etiquetador={ofensa.id_etiquetador}: {ofensa.detalle}"
        )
    return filas


# ---------------------------------------------------------------------------
# Ensamblado
# ---------------------------------------------------------------------------
def preparar_planilla(
    fuente_doble: pathlib.Path | str,
    fuente_brazo: pathlib.Path | str,
    destino: pathlib.Path | str,
    corpus: Sequence[CasoEvaluacion],
    *,
    raiz: pathlib.Path | str = RAIZ_REPO,
) -> pathlib.Path:
    """Escribe la union C1 de `doble_etiquetado.csv` y `brazo_manual.csv` en `destino`.

    Re-valida cada tarea contra `corpus` antes de escribir. Si una fuente falta o no pasa
    el validador, aborta con un error accionable y no escribe nada. La salida usa fin de
    linea LF y UTF-8 sin BOM, de modo que su SHA-256 coincide entre sistemas.
    """
    fuente_doble = pathlib.Path(fuente_doble)
    fuente_brazo = pathlib.Path(fuente_brazo)
    destino = pathlib.Path(destino)
    _verificar_destino(destino, raiz, fuentes=(fuente_doble, fuente_brazo))

    filas_por_tarea = [
        _validar_fuente(fuente_doble, TAREA_DOBLE_ETIQUETADO, corpus),
        _validar_fuente(fuente_brazo, TAREA_BRAZO_MANUAL, corpus),
    ]
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(COLUMNAS_C1)
        for filas in filas_por_tarea:
            for fila in filas:
                escritor.writerow([fila.get(columna) or "" for columna in COLUMNAS_C1])
    return destino


def copia_in_sample(
    origen: pathlib.Path | str,
    destino: pathlib.Path | str,
    *,
    raiz: pathlib.Path | str = RAIZ_REPO,
) -> pathlib.Path:
    """Copia `origen` byte a byte en `destino` (la fuente es de solo lectura).

    No regenera predicciones ni escribe en `evaluation/evidence/`.
    """
    origen = pathlib.Path(origen)
    destino = pathlib.Path(destino)
    if not origen.is_file():
        raise PrepararEntradasError(
            f"falta el cache congelado {origen.name}; la campana no puede materializar "
            f"{NOMBRE_IN_SAMPLE} sin el."
        )
    _verificar_destino(destino, raiz, fuentes=(origen,))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(origen.read_bytes())
    return destino


def preparar_entradas(
    entrada: pathlib.Path | str,
    corpus: pathlib.Path | str,
    cache_in_sample: pathlib.Path | str,
    *,
    raiz: pathlib.Path | str = RAIZ_REPO,
) -> ResultadoPreparacion:
    """Produce las dos entradas del analisis en `entrada` y devuelve su procedencia."""
    entrada = pathlib.Path(entrada)
    corpus_cargado = cargar_corpus(pathlib.Path(corpus))
    fuente_doble = entrada / NOMBRE_DOBLE_ETIQUETADO
    fuente_brazo = entrada / NOMBRE_BRAZO_MANUAL
    cache = pathlib.Path(cache_in_sample)
    ruta_planilla = entrada / NOMBRE_PLANILLA
    ruta_in_sample = entrada / NOMBRE_IN_SAMPLE

    preparar_planilla(fuente_doble, fuente_brazo, ruta_planilla, corpus_cargado, raiz=raiz)
    copia_in_sample(cache, ruta_in_sample, raiz=raiz)

    planilla = EntradaProducida(
        nombre=NOMBRE_PLANILLA,
        ruta=ruta_planilla,
        sha256=_sha256(ruta_planilla),
        procedencias=(
            Procedencia(fuente_doble, _sha256(fuente_doble), TAREA_DOBLE_ETIQUETADO),
            Procedencia(fuente_brazo, _sha256(fuente_brazo), TAREA_BRAZO_MANUAL),
        ),
    )
    in_sample = EntradaProducida(
        nombre=NOMBRE_IN_SAMPLE,
        ruta=ruta_in_sample,
        sha256=_sha256(ruta_in_sample),
        procedencias=(Procedencia(cache, _sha256(cache)),),
    )
    return ResultadoPreparacion(planilla=planilla, in_sample=in_sample)


def _resumen(resultado: ResultadoPreparacion) -> str:
    lineas: list[str] = []
    for entrada in (resultado.planilla, resultado.in_sample):
        lineas.append(f"{entrada.nombre} sha256={entrada.sha256}")
        for procedencia in entrada.procedencias:
            sufijo = "" if procedencia.tarea is None else f" (tarea={procedencia.tarea})"
            lineas.append(
                f"  fuente: {procedencia.ruta} sha256={procedencia.sha256}{sufijo}"
            )
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.preparar_entradas_analisis",
        description=(
            "Ensambla las dos entradas del analisis de campana (c-170): una planilla C1 "
            "unificada y la copia in-sample del cache congelado."
        ),
    )
    parser.add_argument(
        "--entrada",
        default=str(RUTA_CAMPANA_POR_DEFECTO),
        help="carpeta de campana con doble_etiquetado.csv y brazo_manual.csv",
    )
    parser.add_argument(
        "--corpus",
        default=str(RUTA_CORPUS_POR_DEFECTO),
        help="corpus contra el que se re-valida cada tarea",
    )
    parser.add_argument(
        "--cache-in-sample",
        default=str(RUTA_CACHE_IN_SAMPLE_POR_DEFECTO),
        help="cache congelado que se copia byte a byte como referencia in-sample",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI; devuelve 0 si escribio las dos entradas y 2 ante un error."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    args = _construir_parser().parse_args(argv)
    try:
        resultado = preparar_entradas(args.entrada, args.corpus, args.cache_in_sample)
    except (OSError, ValueError) as exc:  # PrepararEntradasError y CorpusError son ValueError
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(_resumen(resultado))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
