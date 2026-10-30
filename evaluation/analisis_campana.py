"""
CLI de solo lectura del analisis de la campana (c-167, D10).

Lee las entradas de la campana (planilla C1, registro de sujetos C2, export de intervencion
C5, plan C6, corpus de campana, predicciones in-sample y fuera de muestra C9), re-verifica lo
minimo con un error accionable que nombra el archivo y la columna, delega en las funciones
puras de `evaluation/campana.py` y `evaluation/kappa.py` y escribe SOLO tres archivos en la
carpeta de salida: `resultados.json`, `resultados.md` y `SHA256SUMS.txt` (SHA-256 de cada
salida y de cada entrada leida).

No escribe `evaluation/report.md`, `evaluation/predicciones.json` ni
`evaluation/predicciones_calibracion.json`; rechaza una carpeta de salida que apunte a un
artefacto congelado (via `plan_campana.es_archivo_frozen`). No usa red ni Gemini: cada seccion
se ejecuta de forma independiente y un dataset ausente se declara "no se obtuvo" sin abortar
las demas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
from dataclasses import fields, is_dataclass
from typing import Any, Mapping, Sequence

from evaluation.campana import (
    COLUMNAS_INTERVENCION_USADAS,
    COLUMNAS_REGISTRO_SUJETOS,
    COTA_SUBHIPOTESIS_2,
    FueraDeMuestraError,
    REFERENCIA_CONSENSO_NUEVO,
    REFERENCIAS,
    Referencia,
    analizar_intervencion,
    cargar_corpus_solo_lectura,
    construir_referencia,
    efecto_orden,
    evaluar_fuera_de_muestra,
    exactitud_brazo_manual,
)
from evaluation.doble_etiquetado import COLUMNAS_C1
from evaluation.kappa import kappa_doble_etiquetado
from evaluation.metrics import REMUESTREOS_BOOTSTRAP, SEMILLA_BOOTSTRAP
from evaluation.plan_campana import es_archivo_congelado, leer_plan_csv
from evaluation.run_evaluation import cargar_predicciones

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parent
RUTA_ENTRADA_POR_DEFECTO = RAIZ_EVALUATION / "data" / "campana"
RUTA_SALIDA_POR_DEFECTO = RAIZ_EVALUATION / "data" / "campana" / "analisis"

#: Nombres canonicos de las entradas dentro de la carpeta `--entrada`.
NOMBRE_PLANILLA = "plantilla_etiquetado.csv"
NOMBRE_REGISTRO = "registro_sujetos.csv"
NOMBRE_INTERVENCIONES = "intervenciones.csv"
NOMBRE_PLAN = "plan_campana.csv"
NOMBRE_CORPUS_CAMPANA = "corpus_campana.json"
NOMBRE_PREDICCIONES_IN_SAMPLE = "predicciones_in_sample.json"
NOMBRE_PREDICCIONES_INDEPENDIENTE = "predicciones_independiente.json"
NOMBRE_CORPUS_INDEPENDIENTE = "corpus_independiente.json"

#: Archivos que el CLI escribe, y SOLO estos, en la carpeta de salida.
SALIDAS: tuple[str, ...] = ("resultados.json", "resultados.md", "SHA256SUMS.txt")

#: Columnas del plan de campana (C6); las valida `leer_plan_csv`, aca se usan para el error.
COLUMNAS_PLAN: tuple[str, ...] = (
    "id_caso",
    "posicion",
    "mitad",
    "brazo_primero",
    "modo",
    "seed",
)

#: Secciones del analisis, en el orden de reporte.
SECCIONES: tuple[str, ...] = (
    "kappa",
    "exactitud_brazo_manual",
    "intervencion",
    "orden",
    "fuera_de_muestra",
)

ENCABEZADO = "Analisis de la campana (c-167)"


class ErrorDeEntrada(ValueError):
    """
    Una entrada no cumple su contrato minimo.

    El mensaje nombra el archivo y la columna (o el valor) para que el error sea accionable;
    aborta el CLI antes de escribir cualquier salida.
    """


# ---------------------------------------------------------------------------
# Lectura y validacion minima
# ---------------------------------------------------------------------------
def _leer_csv(ruta: pathlib.Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    """Encabezado y filas de un CSV UTF-8; no falla si esta vacio."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.reader(archivo)
        try:
            encabezado = tuple(next(lector))
        except StopIteration:
            return (), []
        filas = [dict(zip(encabezado, fila)) for fila in lector if fila != []]
    return encabezado, filas


def _verificar_columnas(ruta: pathlib.Path, encabezado: Sequence[str], columnas: Sequence[str]) -> None:
    faltantes = [columna for columna in columnas if columna not in encabezado]
    if faltantes:
        raise ErrorDeEntrada(
            f"el archivo {ruta.name} no tiene la columna {faltantes[0]!r} "
            f"(columnas exigidas: {', '.join(columnas)})."
        )


def _leer_entrada_csv(ruta: pathlib.Path, columnas: Sequence[str]) -> list[dict[str, str]] | None:
    if not ruta.is_file():
        return None
    encabezado, filas = _leer_csv(ruta)
    _verificar_columnas(ruta, encabezado, columnas)
    return filas


def _leer_plan(ruta: pathlib.Path):
    if not ruta.is_file():
        return None
    # `leer_plan_csv` valida el contrato completo; se le da un encabezado ya verificado.
    encabezado, _ = _leer_csv(ruta)
    _verificar_columnas(ruta, encabezado, COLUMNAS_PLAN)
    return leer_plan_csv(ruta)


def _leer_corpus(ruta: pathlib.Path):
    return cargar_corpus_solo_lectura(ruta) if ruta.is_file() else None


def _leer_predicciones(ruta: pathlib.Path):
    return cargar_predicciones(ruta) if ruta.is_file() else None


class Entradas:
    """Entradas leidas (o ausentes) de la carpeta de entrada."""

    def __init__(self, entrada: pathlib.Path) -> None:
        self.entrada = entrada
        self.planilla = _leer_entrada_csv(entrada / NOMBRE_PLANILLA, COLUMNAS_C1)
        self.registro = _leer_entrada_csv(entrada / NOMBRE_REGISTRO, COLUMNAS_REGISTRO_SUJETOS)
        self.intervenciones = _leer_entrada_csv(entrada / NOMBRE_INTERVENCIONES, COLUMNAS_INTERVENCION_USADAS)
        self.plan = _leer_plan(entrada / NOMBRE_PLAN)
        self.corpus_campana = _leer_corpus(entrada / NOMBRE_CORPUS_CAMPANA)
        self.predicciones_in_sample = _leer_predicciones(entrada / NOMBRE_PREDICCIONES_IN_SAMPLE)

    def archivos_leidos(self) -> list[pathlib.Path]:
        """Rutas de las entradas que existen (para el SHA-256); ordenadas por nombre."""
        nombres = (
            NOMBRE_PLANILLA,
            NOMBRE_REGISTRO,
            NOMBRE_INTERVENCIONES,
            NOMBRE_PLAN,
            NOMBRE_CORPUS_CAMPANA,
            NOMBRE_PREDICCIONES_IN_SAMPLE,
            NOMBRE_PREDICCIONES_INDEPENDIENTE,
            NOMBRE_CORPUS_INDEPENDIENTE,
        )
        return sorted(
            (self.entrada / nombre for nombre in nombres if (self.entrada / nombre).is_file()),
            key=lambda ruta: ruta.name,
        )


# ---------------------------------------------------------------------------
# Serializacion determinista
# ---------------------------------------------------------------------------
def _a_jsonable(valor: Any) -> Any:
    """Convierte dataclasses, mapeos, tuplas, conjuntos y escalares a JSON determinista."""
    if is_dataclass(valor) and not isinstance(valor, type):
        return {campo.name: _a_jsonable(getattr(valor, campo.name)) for campo in fields(valor)}
    if isinstance(valor, Mapping):
        return {str(clave): _a_jsonable(contenido) for clave, contenido in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_a_jsonable(elemento) for elemento in valor]
    if isinstance(valor, (set, frozenset)):
        return sorted(_a_jsonable(elemento) for elemento in valor)
    if isinstance(valor, pathlib.Path):
        return str(valor)
    if isinstance(valor, (str, bool, int, float)) or valor is None:
        return valor
    raise TypeError(f"no se puede serializar a JSON un valor de tipo {type(valor).__name__}")


def _seccion(resultado: Any) -> dict[str, Any]:
    return {"obtenido": True, "resultado": _a_jsonable(resultado)}


def _ausente(motivo: str) -> dict[str, Any]:
    return {"obtenido": False, "motivo": motivo}


# ---------------------------------------------------------------------------
# Secciones (delegacion en las funciones puras)
# ---------------------------------------------------------------------------
def _referencia(
    rotulo: str, entradas: Entradas
) -> Referencia:
    return construir_referencia(
        rotulo,
        doble_etiquetado=entradas.planilla,
        corpus=entradas.corpus_campana,
    )


def _seccion_kappa(entradas: Entradas) -> dict[str, Any]:
    if entradas.planilla is None:
        return _ausente(f"no se obtuvo: falta {NOMBRE_PLANILLA}.")
    try:
        return _seccion(kappa_doble_etiquetado(entradas.planilla))
    except ValueError as exc:
        return _ausente(f"no se obtuvo el kappa: {exc}")


def _seccion_exactitud(entradas: Entradas, rotulo: str) -> dict[str, Any]:
    if entradas.planilla is None or entradas.registro is None:
        faltantes = [
            nombre
            for nombre, presente in (
                (NOMBRE_PLANILLA, entradas.planilla),
                (NOMBRE_REGISTRO, entradas.registro),
            )
            if presente is None
        ]
        return _ausente(f"no se obtuvo: falta(n) {', '.join(faltantes)}.")
    try:
        referencia = _referencia(rotulo, entradas)
        return _seccion(
            exactitud_brazo_manual(
                entradas.planilla,
                referencia,
                entradas.registro,
                predicciones=entradas.predicciones_in_sample,
            )
        )
    except ValueError as exc:
        return _ausente(f"no se obtuvo la exactitud del brazo manual: {exc}")


def _seccion_intervencion(entradas: Entradas, cota: float) -> dict[str, Any]:
    faltantes = [
        nombre
        for nombre, presente in (
            (NOMBRE_INTERVENCIONES, entradas.intervenciones),
            (NOMBRE_PLAN, entradas.plan),
            (NOMBRE_CORPUS_CAMPANA, entradas.corpus_campana),
        )
        if presente is None
    ]
    if faltantes:
        return _ausente(f"no se obtuvo: falta(n) {', '.join(faltantes)}.")
    casos_corrida = [fila.id_caso for fila in entradas.plan]
    tiempos = {caso.id: caso.tiempo_automatizado_s for caso in entradas.corpus_campana}
    try:
        return _seccion(
            analizar_intervencion(entradas.intervenciones, casos_corrida, tiempos, cota=cota)
        )
    except ValueError as exc:
        return _ausente(f"no se obtuvo la tasa de intervencion: {exc}")


def _seccion_orden(entradas: Entradas, rotulo: str) -> dict[str, Any]:
    faltantes = [
        nombre
        for nombre, presente in (
            (NOMBRE_PLANILLA, entradas.planilla),
            (NOMBRE_PLAN, entradas.plan),
        )
        if presente is None
    ]
    if faltantes:
        return _ausente(f"no se obtuvo: falta(n) {', '.join(faltantes)}.")
    try:
        referencia = _referencia(rotulo, entradas)
        return _seccion(efecto_orden(entradas.planilla, entradas.plan, referencia=referencia))
    except ValueError as exc:
        return _ausente(f"no se obtuvo el efecto de orden: {exc}")


def _seccion_fuera_de_muestra(
    entradas: Entradas,
    *,
    pines_in_sample: Mapping[str, str] | None,
    rango_google_genai_vigente: str | None,
    commit_in_sample: str | None,
) -> dict[str, Any]:
    # `evaluar_fuera_de_muestra` ya devuelve `obtenido = False` con el artefacto faltante: la
    # seccion se declara "no se obtuvo" cuando falta cualquiera de los cuatro artefactos.
    try:
        resultado = evaluar_fuera_de_muestra(
            entradas.entrada / NOMBRE_PREDICCIONES_IN_SAMPLE,
            entradas.entrada / NOMBRE_CORPUS_CAMPANA,
            entradas.entrada / NOMBRE_PREDICCIONES_INDEPENDIENTE,
            entradas.entrada / NOMBRE_CORPUS_INDEPENDIENTE,
            pines_in_sample=pines_in_sample,
            rango_google_genai_vigente=rango_google_genai_vigente,
            commit_in_sample=commit_in_sample,
        )
    except FueraDeMuestraError as exc:
        return _ausente(f"no se obtuvo la evaluacion fuera de muestra: {exc}")
    if not resultado.obtenido:
        return _ausente(resultado.motivo)
    return _seccion(resultado)


# ---------------------------------------------------------------------------
# Reporte en Markdown
# ---------------------------------------------------------------------------
def _fmt(valor: Any) -> str:
    if valor is None:
        return "no estimable"
    if isinstance(valor, float):
        return f"{valor:.6f}"
    if isinstance(valor, (list, tuple)):
        return "[" + ", ".join(_fmt(elemento) for elemento in valor) + "]"
    return str(valor)


def _markdown(documento: Mapping[str, Any]) -> str:
    lineas = [f"# {ENCABEZADO}", ""]
    lineas.append(f"- Referencia del brazo manual: {documento['referencia_usada']}")
    lineas.append(f"- Semilla bootstrap: {documento['semilla']}")
    lineas.append(f"- Remuestreos bootstrap: {documento['remuestreos']}")
    lineas.append("")
    lineas.append("## Kappa de Cohen (etiquetadores nuevos)")
    lineas.extend(_detalle(documento["secciones"]["kappa"]))
    lineas.append("")
    lineas.append("## Exactitud del brazo manual")
    lineas.extend(_detalle(documento["secciones"]["exactitud_brazo_manual"]))
    lineas.append("")
    lineas.append("## Intervencion humana de la campana")
    lineas.extend(_detalle(documento["secciones"]["intervencion"]))
    lineas.append("")
    lineas.append("## Efecto de orden de condicion y de posicion")
    lineas.extend(_detalle(documento["secciones"]["orden"]))
    lineas.append("")
    lineas.append("## Evaluacion fuera de muestra")
    lineas.extend(_detalle(documento["secciones"]["fuera_de_muestra"]))
    lineas.append("")
    lineas.append("## Entradas leidas")
    lineas.extend(f"- {nombre}: {digest}" for nombre, digest in sorted(documento["entradas"].items()))
    lineas.append("")
    return "\n".join(lineas)


def _detalle(seccion: Mapping[str, Any]) -> list[str]:
    """Lineas del reporte para una seccion: el detalle completo queda en resultados.json."""
    if not seccion["obtenido"]:
        return [seccion["motivo"]]
    resumen = seccion["resultado"]
    lineas: list[str] = []
    for campo, valor in _campos_destacados(resumen):
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True)
        else:
            valor = _fmt(valor)
        lineas.append(f"- {campo}: {valor}")
    return lineas


def _campos_destacados(resumen: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Primeros campos del resultado, que el reporte lista antes del detalle en JSON."""
    return [(campo, resumen[campo]) for campo in list(resumen)[:6]]


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
def _sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _escribir(ruta: pathlib.Path, contenido: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8", newline="\n")


def _verificar_destino(salida: pathlib.Path) -> None:
    # Defensa en profundidad: INALCANZABLE con el conjunto de escritura actual, porque el CLI
    # solo escribe los tres nombres fijos de SALIDAS ("resultados.json", "resultados.md" y
    # "SHA256SUMS.txt"), y ninguno puede ser un artefacto congelado. Se conserva por si el
    # conjunto de escritura crece en el futuro.
    for nombre in SALIDAS:
        destino = salida / nombre
        if es_archivo_congelado(destino):
            raise ErrorDeEntrada(
                f"la carpeta de salida {salida} apuntaria a un artefacto congelado ({nombre}); "
                "elegi otra --salida."
            )
    if salida.exists() and not salida.is_dir():
        raise ErrorDeEntrada(f"la ruta de salida {salida} existe y no es un directorio.")


def ejecutar(
    entrada: pathlib.Path | str,
    salida: pathlib.Path | str,
    *,
    rotulo_referencia: str = REFERENCIA_CONSENSO_NUEVO,
    cota: float = COTA_SUBHIPOTESIS_2,
    pines_in_sample: Mapping[str, str] | None = None,
    rango_google_genai_vigente: str | None = None,
    commit_in_sample: str | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el analisis y escribe las tres salidas; devuelve el documento de `resultados.json`.
    """
    entrada, salida = pathlib.Path(entrada), pathlib.Path(salida)
    if rotulo_referencia not in REFERENCIAS:
        raise ErrorDeEntrada(
            f"referencia desconocida: {rotulo_referencia!r} (validas: {', '.join(REFERENCIAS)})."
        )
    if not entrada.is_dir():
        raise ErrorDeEntrada(f"la carpeta de entrada {entrada} no existe o no es un directorio.")
    _verificar_destino(salida)

    entradas = Entradas(entrada)
    documento: dict[str, Any] = {
        "generador": "evaluation/analisis_campana.py",
        "referencia_usada": rotulo_referencia,
        "semilla": SEMILLA_BOOTSTRAP,
        "remuestreos": REMUESTREOS_BOOTSTRAP,
        "entradas": {ruta.name: _sha256(ruta) for ruta in entradas.archivos_leidos()},
        "secciones": {
            "kappa": _seccion_kappa(entradas),
            "exactitud_brazo_manual": _seccion_exactitud(entradas, rotulo_referencia),
            "intervencion": _seccion_intervencion(entradas, cota),
            "orden": _seccion_orden(entradas, rotulo_referencia),
            "fuera_de_muestra": _seccion_fuera_de_muestra(
                entradas,
                pines_in_sample=pines_in_sample,
                rango_google_genai_vigente=rango_google_genai_vigente,
                commit_in_sample=commit_in_sample,
            ),
        },
    }

    ruta_json = salida / "resultados.json"
    _escribir(ruta_json, json.dumps(documento, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    ruta_md = salida / "resultados.md"
    _escribir(ruta_md, _markdown(documento))

    hashes = {ruta.name: _sha256(ruta) for ruta in entradas.archivos_leidos()}
    hashes[ruta_json.name] = _sha256(ruta_json)
    hashes[ruta_md.name] = _sha256(ruta_md)
    _escribir(
        salida / "SHA256SUMS.txt",
        "".join(f"{digest}  {nombre}\n" for nombre, digest in sorted(hashes.items())),
    )
    return documento


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _pines_desde_texto(texto: str | None) -> Mapping[str, str] | None:
    if not texto:
        return None
    try:
        valor = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorDeEntrada(f"--pines-in-sample no es JSON valido: {exc}") from exc
    if not isinstance(valor, dict):
        raise ErrorDeEntrada("--pines-in-sample debe ser un objeto JSON con google_genai y modelo.")
    return valor


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.analisis_campana",
        description="Analisis de solo lectura de la campana (c-167): escribe resultados.json, resultados.md y SHA256SUMS.txt.",
    )
    parser.add_argument("--entrada", default=str(RUTA_ENTRADA_POR_DEFECTO), help="carpeta con las entradas canonicas")
    parser.add_argument("--salida", default=str(RUTA_SALIDA_POR_DEFECTO), help="carpeta de salida")
    parser.add_argument(
        "--referencia",
        default=REFERENCIA_CONSENSO_NUEVO,
        choices=list(REFERENCIAS),
        help="referencia del brazo manual",
    )
    parser.add_argument("--cota", type=float, default=COTA_SUBHIPOTESIS_2, help="cota de la sub-hipotesis 2")
    parser.add_argument(
        "--pines-in-sample",
        default=None,
        help='JSON de pines in-sample, por ejemplo {"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}',
    )
    parser.add_argument("--rango-google-genai-vigente", default=None, help="pin vigente de google-genai (openspec/config.yaml)")
    parser.add_argument("--commit-in-sample", default=None, help="commit del bloque in-sample (opcional)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI; devuelve 0 si escribio las tres salidas."""
    argumentos = _construir_parser().parse_args(argv)
    ejecutar(
        argumentos.entrada,
        argumentos.salida,
        rotulo_referencia=argumentos.referencia,
        cota=argumentos.cota,
        pines_in_sample=_pines_desde_texto(argumentos.pines_in_sample),
        rango_google_genai_vigente=argumentos.rango_google_genai_vigente,
        commit_in_sample=argumentos.commit_in_sample,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
