"""Recuenta los errores estrictos por frontera y los aciertos laxos (c-159).

Fuente de las cifras de la Seccion 8.6 y de la Tabla 16 de la tesis. Es de solo
lectura: no invoca al clasificador y no usa `evaluation.corpus.cargar_corpus`
(que reescribe el corpus si `metadata.total_casos` esta desincronizado).

Valida antes de computar: SHA-256 del corpus con fin de linea normalizado a LF,
`cache_meta` de la evidencia (hash del corpus, cantidad de casos y version del
clasificador) y la union por identificador con descripciones identicas. Si una
validacion falla, termina con codigo distinto de 0 sin imprimir cifras.

Uso, desde la raiz del repositorio:

    python docs/Tesis/Correcciones/recontar_errores_frontera.py

Pruebas (imagen Docker con pytest):

    docker run --rm -v "<raiz>:/repo" -w /repo eval-tests python -m pytest docs/Tesis/Correcciones/test_recontar_errores_frontera.py -q

Solo biblioteca estandar; compatible con Python 3.12 y 3.14.
"""
import argparse
import hashlib
import json
import sys
from collections import namedtuple
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evaluation.metrics import CLASES, aciertos_laxos  # noqa: E402

RUTA_CORPUS = "data/corpus_evaluacion_pseudonimizado.json"
RUTA_EVIDENCIA = "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"
HASH_CORPUS_CANONICO = "1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb"
CASOS_ESPERADOS = 200
VERSION_CLASIFICADOR = "hybrid-v3"
CASOS_ILUSTRATIVOS = ("R001", "R032", "R015")

HW = "Soporte Tecnico Hardware"
SW = "Soporte Tecnico Software"
SEG = "Seguridad Informatica"
SIS = "Sistemas"
ETIQUETA_RESTO = "Demás fronteras"


class ValidacionError(Exception):
    """Una validacion previa de las entradas fallo."""


Resultado = namedtuple(
    "Resultado",
    "total_casos total_errores total_laxos por_frontera aciertos_estrictos aciertos_laxos_totales",
)


def hash_normalizado(contenido):
    """SHA-256 del contenido con CRLF normalizado a LF."""
    return hashlib.sha256(contenido.replace(b"\r\n", b"\n")).hexdigest()


def verificar_hash(contenido, esperado):
    obtenido = hash_normalizado(contenido)
    if obtenido != esperado:
        raise ValidacionError(f"hash del corpus {obtenido} distinto del esperado {esperado}")


def validar_cache_meta(meta, hash_corpus, casos, version):
    esperado = {
        "corpus_hash": hash_corpus,
        "corpus_count": casos,
        "classifier_version": version,
    }
    for clave, valor in esperado.items():
        if meta.get(clave) != valor:
            raise ValidacionError(f"cache_meta.{clave}={meta.get(clave)!r}, se esperaba {valor!r}")


def unir_casos(casos_corpus, predicciones):
    """Une corpus y evidencia por identificador, en el orden del corpus."""
    por_id = {}
    for pred in predicciones:
        cid = pred["caso_id"]
        if cid in por_id:
            raise ValidacionError(f"prediccion duplicada para {cid}")
        por_id[cid] = pred
    ids_corpus = {caso["id"] for caso in casos_corpus}
    if len(ids_corpus) != len(casos_corpus):
        raise ValidacionError("identificador duplicado en el corpus")
    sobrantes = set(por_id) - ids_corpus
    if sobrantes:
        raise ValidacionError(f"predicciones sin caso en el corpus: {sorted(sobrantes)}")
    unidos = []
    for caso in casos_corpus:
        pred = por_id.get(caso["id"])
        if pred is None:
            raise ValidacionError(f"caso {caso['id']} sin prediccion")
        if pred["descripcion"] != caso["descripcion"]:
            raise ValidacionError(f"descripcion distinta en {caso['id']}")
        unidos.append(
            {
                "id": caso["id"],
                "descripcion": caso["descripcion"],
                "sector_asignado": caso["sector_asignado"],
                "sectores_adicionales": list(caso.get("sectores_adicionales", [])),
                "sector_predicho": pred["sector_predicho"],
                "confianza": pred["confianza"],
                "etapa": pred["etapa"],
            }
        )
    return unidos


def _orden(sector):
    return (CLASES.index(sector), "") if sector in CLASES else (len(CLASES), sector)


def frontera(asignado, predicho):
    """Par no ordenado de sectores, en el orden de CLASES."""
    return tuple(sorted((asignado, predicho), key=_orden))


def contar(unidos):
    por_frontera = {}
    errores = 0
    laxos = 0
    for caso in unidos:
        if caso["sector_predicho"] == caso["sector_asignado"]:
            continue
        errores += 1
        verdad = {caso["sector_asignado"], *caso["sectores_adicionales"]}
        laxo = aciertos_laxos([caso["sector_predicho"]], [verdad])
        laxos += laxo
        par = frontera(caso["sector_asignado"], caso["sector_predicho"])
        previos = por_frontera.get(par, (0, 0))
        por_frontera[par] = (previos[0] + 1, previos[1] + laxo)
    total = len(unidos)
    return Resultado(total, errores, laxos, por_frontera, total - errores, total - errores + laxos)


FRONTERAS_PRINCIPALES = (
    ("Hardware-Software", frontera(HW, SW)),
    ("Sistemas-Software", frontera(SIS, SW)),
    ("Seguridad-Software", frontera(SEG, SW)),
)


def agrupar(por_frontera):
    """Filas (etiqueta, errores, laxos): las tres fronteras principales y el resto."""
    filas = []
    usadas = set()
    for etiqueta, par in FRONTERAS_PRINCIPALES:
        errores, laxos = por_frontera.get(par, (0, 0))
        filas.append((etiqueta, errores, laxos))
        usadas.add(par)
    resto = [v for par, v in por_frontera.items() if par not in usadas]
    filas.append((ETIQUETA_RESTO, sum(e for e, _ in resto), sum(la for _, la in resto)))
    return filas


def porcentaje(numerador, denominador):
    valor = Decimal(numerador) * 100 / Decimal(denominador)
    return str(valor.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)).replace(".", ",")


def formatear(res, unidos, ids_casos):
    pleno = res.total_errores - res.total_laxos
    lineas = [
        f"Casos: {res.total_casos}",
        f"Errores estrictos: {res.total_errores} de {res.total_casos}",
        "Aciertos laxos entre los errores: "
        f"{res.total_laxos} de {res.total_errores} ({porcentaje(res.total_laxos, res.total_errores)} %)",
        f"Errores plenos: {pleno} de {res.total_errores} ({porcentaje(pleno, res.total_errores)} %)",
        f"Identidad: {res.aciertos_estrictos} + {res.total_laxos} = {res.aciertos_laxos_totales}",
        "",
        "| Frontera | Errores | Aciertos laxos | % del total de errores | % laxos de la frontera |",
        "|---|---|---|---|---|",
    ]
    for etiqueta, errores, laxos in agrupar(res.por_frontera):
        pct_total = porcentaje(errores, res.total_errores) if res.total_errores else "0,0"
        pct_laxo = porcentaje(laxos, errores) if errores else "0,0"
        lineas.append(f"| {etiqueta} | {errores} | {laxos} | {pct_total} | {pct_laxo} |")
    lineas += ["", "Casos ilustrativos:"]
    por_id = {u["id"]: u for u in unidos}
    for cid in ids_casos:
        u = por_id[cid]
        lineas.append(
            f"- {cid} | {u['descripcion']} | asignado: {u['sector_asignado']} | "
            f"predicho: {u['sector_predicho']} | confianza: {u['confianza']} | "
            f"etapa: {u['etapa']} | adicionales: {', '.join(u['sectores_adicionales']) or '-'}"
        )
    return "\n".join(lineas) + "\n"


def cargar_y_unir(ruta_corpus, ruta_evidencia, hash_esperado=HASH_CORPUS_CANONICO,
                  casos_esperados=CASOS_ESPERADOS, version=VERSION_CLASIFICADOR):
    contenido = Path(ruta_corpus).read_bytes()
    verificar_hash(contenido, hash_esperado)
    corpus = json.loads(contenido.replace(b"\r\n", b"\n").decode("utf-8"))
    evidencia = json.loads(Path(ruta_evidencia).read_text(encoding="utf-8"))
    validar_cache_meta(evidencia["cache_meta"], hash_esperado, casos_esperados, version)
    if len(corpus["casos"]) != casos_esperados:
        raise ValidacionError(f"el corpus no tiene {casos_esperados} casos")
    return unir_casos(corpus["casos"], evidencia["predictions"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", default=str(RAIZ / RUTA_CORPUS))
    ap.add_argument("--evidencia", default=str(RAIZ / RUTA_EVIDENCIA))
    ap.add_argument("--hash-esperado", default=HASH_CORPUS_CANONICO)
    ap.add_argument("--casos-esperados", type=int, default=CASOS_ESPERADOS)
    ap.add_argument("--casos", nargs="*", default=list(CASOS_ILUSTRATIVOS))
    args = ap.parse_args(argv)
    try:
        unidos = cargar_y_unir(args.corpus, args.evidencia, args.hash_esperado, args.casos_esperados)
        salida = formatear(contar(unidos), unidos, args.casos)
    except (ValidacionError, OSError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
