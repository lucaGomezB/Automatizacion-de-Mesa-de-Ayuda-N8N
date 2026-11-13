#!/usr/bin/env python3
"""Contraste pareado entre la linea de base clasica y el hibrido (c-213).

Solo lectura y determinista. Reconstruye las predicciones por caso de la linea de base
con `evaluation.linea_de_base.predecir` (semilla 42), lee las del hibrido de
`predicciones_independiente.json` y calcula sobre los mismos casos la tabla 2x2 de
aciertos estrictos, el contraste de McNemar (`evaluation.stats.contraste_mcnemar`) y la
diferencia de exactitudes pareadas con IC bootstrap percentil pareado. Aborta sin escribir
si no reproduce los aciertos agregados de c-205 y c-210. Sin red, sin Gemini. Aditivo: no
reemplaza ningun numero canonico.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/contraste_linea_de_base_c213.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import sys
from typing import Iterable, Mapping, Optional, Sequence

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import cargar_corpus_solo_lectura  # noqa: E402
from evaluation.linea_de_base import (  # noqa: E402
    RUTA_CORPUS_CAMPANA,
    RUTA_CORPUS_INDEPENDIENTE,
    SEMILLA,
    VARIANTES,
    metricas_de_prediccion,
    predecir,
)
from evaluation.metrics import (  # noqa: E402
    CLASES,
    NIVEL_CONFIANZA,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402
from evaluation.stats import contraste_mcnemar  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_PRED_HIBRIDO = CAMPANA / "predicciones_independiente.json"
RUTA_C205 = SALIDA / "analisis_fuera_de_muestra_c205.json"
RUTA_C210 = SALIDA / "linea_de_base_clasica_c210.json"

NOMBRE_BASE = "contraste_linea_de_base_c213"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

N_ESPERADO = 103
REMUESTREOS = 10_000
SISTEMAS = ("hibrido", "balanceada", "sin_repoderacion")


def declaracion_aditiva(n: int) -> str:
    """Declaracion aditiva; el conteo de casos se interpola para no mentir en el n."""
    return (
        "Las cifras de este contraste son aditivas: no reemplazan ningun numero canonico de la "
        "tesis ni el clasificador de produccion. Comparan al hibrido congelado con un unico "
        "clasificador supervisado clasico entrenado con 200 casos, sobre los "
        f"{n} casos con consenso; no es el brazo solo-LLM ni contrasta la hipotesis de eficiencia."
    )


DECLARACION_ADITIVA = declaracion_aditiva(N_ESPERADO)


class AnclaNoReproducida(RuntimeError):
    """Los aciertos reconstruidos no coinciden con los agregados versionados."""


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def emparejar(
    referencia: Mapping[str, str],
    sistema_1: Mapping[str, str],
    sistema_2: Mapping[str, str],
) -> tuple[list[str], list[bool], list[bool]]:
    """Empareja por `caso_id` (orden de la referencia); aborta si falta alguna pareja."""
    ids = list(referencia)
    for nombre, sistema in (("sistema 1", sistema_1), ("sistema 2", sistema_2)):
        faltantes = [i for i in ids if i not in sistema]
        if faltantes:
            raise ValueError(f"casos sin prediccion en el {nombre}: {faltantes}")
    return (
        ids,
        [sistema_1[i] == referencia[i] for i in ids],
        [sistema_2[i] == referencia[i] for i in ids],
    )


def _diferencia_pareada(a: Sequence[bool], b: Sequence[bool], indices: Sequence[int]) -> float:
    return sum(int(a[i]) - int(b[i]) for i in indices) / len(indices)


def contraste_pareado(
    aciertos_hibrido: Sequence[bool],
    aciertos_base: Sequence[bool],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS,
) -> dict:
    """Tabla 2x2, McNemar y diferencia `(b - c)/n` con IC bootstrap percentil pareado."""
    mc = contraste_mcnemar(aciertos_hibrido, aciertos_base)  # valida las longitudes
    n = mc.pares
    todos = range(n)
    valor = _diferencia_pareada(aciertos_hibrido, aciertos_base, todos) if n else 0.0
    if mc.aplicable:
        generador = random.Random(semilla)
        muestras = [
            _diferencia_pareada(aciertos_hibrido, aciertos_base, indices)
            for indices in remuestreos_indices(generador, n, remuestreos)
        ]
        inferior, superior = percentil_intervalo(muestras, NIVEL_CONFIANZA)
    else:
        inferior = superior = valor
    return {
        "n": n,
        "tabla_2x2": {
            "ambos_aciertan": mc.ambas,
            "solo_hibrido": mc.solo_a,
            "solo_linea_de_base": mc.solo_b,
            "ninguno": mc.ninguna,
        },
        "mcnemar": {
            "aplicable": mc.aplicable,
            "p_exacto": mc.p_exacto,
            "p_corregido": mc.p_corregido,
            "estadistico_corregido": mc.estadistico,
            "criterio_stats": mc.criterio,
            "p_primario_stats": mc.p_primario,
        },
        "diferencia_exactitud": {
            "definicion": "exactitud(hibrido) - exactitud(linea de base) = (b - c) / n",
            "valor": valor,
            "ic95": [inferior, superior],
            "metodo_ic": "bootstrap percentil pareado (remuestreo de casos)",
            "remuestreos": remuestreos,
            "semilla": semilla,
        },
    }


def verificar_anclas(observados: Mapping[str, int], esperados: Mapping[str, int]) -> None:
    """Aborta si algun acierto reconstruido difiere del agregado versionado."""
    diferencias = [
        f"{sistema}: reconstruido {observados.get(sistema)} != versionado {esperado}"
        for sistema, esperado in esperados.items()
        if observados.get(sistema) != esperado
    ]
    if diferencias:
        raise AnclaNoReproducida("; ".join(diferencias))


def parsear_anclas(tokens: Optional[Sequence[str]]) -> Optional[dict[str, int]]:
    """Convierte `["hibrido=142", ...]` en `{"hibrido": 142, ...}` (None si vacio)."""
    if not tokens:
        return None
    anclas: dict[str, int] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"ancla con formato invalido (se espera SISTEMA=N): {token!r}")
        sistema, _, valor = token.partition("=")
        sistema = sistema.strip()
        if sistema not in SISTEMAS:
            raise ValueError(
                f"sistema desconocido en ancla: {sistema!r}; validos: {', '.join(SISTEMAS)}"
            )
        try:
            anclas[sistema] = int(valor)
        except ValueError as error:
            raise ValueError(f"valor de ancla no entero en {token!r}") from error
    return anclas


def metricas_globales(
    ids: Sequence[str],
    referencia: Mapping[str, str],
    predicciones: Mapping[str, Mapping[str, str]],
    conjuntos_verdad: Sequence[Iterable[Iterable[str]]],
) -> dict:
    """Metricas globales y por clase de cada sistema (verdad = referencia del corpus)."""
    reales = [referencia[i] for i in ids]
    conjuntos = [frozenset(conjunto) for conjunto in conjuntos_verdad]
    return {
        nombre: metricas_de_prediccion(reales, [prediccion[i] for i in ids], conjuntos)
        for nombre, prediccion in predicciones.items()
    }


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def anclas_versionadas(ruta_c205: pathlib.Path = RUTA_C205, ruta_c210: pathlib.Path = RUTA_C210) -> dict:
    """Aciertos estrictos agregados de los artefactos de c-205 (hibrido) y c-210."""
    c205 = json.loads(ruta_c205.read_text(encoding="utf-8"))
    c210 = json.loads(ruta_c210.read_text(encoding="utf-8"))
    anclas = {"hibrido": c205["exactitud_estricta"]["aciertos"]}
    for nombre, _ in VARIANTES:
        metricas = c210["variantes"][nombre]["lectura_muestral"]["metricas"]
        anclas[nombre] = metricas["exactitud_estricta"]["aciertos"]
    return anclas


def construir_documento(
    ruta_referencia: pathlib.Path = RUTA_CORPUS_INDEPENDIENTE,
    n_esperado: int = N_ESPERADO,
    *,
    ruta_entrenamiento: pathlib.Path = RUTA_CORPUS_CAMPANA,
    ruta_pred_hibrido: pathlib.Path = RUTA_PRED_HIBRIDO,
    anclas_esperadas: Optional[Mapping[str, int]] = None,
    remuestreos: int = REMUESTREOS,
    con_metricas_globales: bool = False,
) -> dict:
    """Calcula el contraste; falla antes de devolver nada si no reproduce las anclas."""
    entrenamiento = cargar_corpus_solo_lectura(ruta_entrenamiento)
    prueba = cargar_corpus_solo_lectura(ruta_referencia)
    if len(prueba) != n_esperado:
        raise ValueError(f"n esperado {n_esperado}, la referencia tiene {len(prueba)} casos.")

    referencia = {caso.id: caso.sector_asignado for caso in prueba}
    hibrido = {p.caso_id: p.sector_predicho for p in cargar_predicciones(ruta_pred_hibrido)}
    predicciones = {"hibrido": hibrido}
    for nombre, class_weight in VARIANTES:
        predichos = predecir(entrenamiento, prueba, class_weight=class_weight)
        predicciones[nombre] = {caso.id: p for caso, p in zip(prueba, predichos)}

    aciertos: dict[str, list[bool]] = {}
    ids: list[str] = []
    for nombre, pred in predicciones.items():
        ids, aciertos[nombre], _ = emparejar(referencia, pred, pred)
    totales = {nombre: sum(valores) for nombre, valores in aciertos.items()}
    esperadas = anclas_versionadas() if anclas_esperadas is None else anclas_esperadas
    verificar_anclas(totales, esperadas)

    contrastes = {
        nombre: contraste_pareado(aciertos["hibrido"], aciertos[nombre], remuestreos=remuestreos)
        for nombre in ("balanceada", "sin_repoderacion")
    }
    casos = [
        {
            "caso_id": i,
            "referencia": referencia[i],
            "hibrido": hibrido[i],
            "balanceada": predicciones["balanceada"][i],
            "sin_repoderacion": predicciones["sin_repoderacion"][i],
            "acierto_hibrido": aciertos["hibrido"][k],
            "acierto_balanceada": aciertos["balanceada"][k],
            "acierto_sin_repoderacion": aciertos["sin_repoderacion"][k],
        }
        for k, i in enumerate(ids)
    ]
    documento = {
        "change": "c-213-integrar-la-linea-de-base-en-la-tesis",
        "generador": "evaluation/data/campana/analisis/contraste_linea_de_base_c213.py",
        "metodo": (
            "predicciones por caso de la linea de base reconstruidas con "
            "evaluation.linea_de_base.predecir (semilla 42); predicciones del hibrido leidas "
            f"de {_nombre(ruta_pred_hibrido)}; McNemar con evaluation.stats.contraste_mcnemar; "
            "IC bootstrap percentil pareado de la diferencia de exactitudes; sin red ni Gemini"
        ),
        "semilla_linea_de_base": SEMILLA,
        "n": len(ids),
        "n_entrenamiento": len(entrenamiento),
        "entradas_sha256": {
            _nombre(ruta_entrenamiento): sha256(ruta_entrenamiento),
            _nombre(ruta_referencia): sha256(ruta_referencia),
            _nombre(ruta_pred_hibrido): sha256(ruta_pred_hibrido),
            RUTA_C205.name: sha256(RUTA_C205),
            RUTA_C210.name: sha256(RUTA_C210),
        },
        "aciertos": totales,
        "anclas_verificadas": dict(esperadas),
        "contrastes": contrastes,
        "variante_primaria": "balanceada",
        "casos": casos,
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "declaracion": declaracion_aditiva(len(ids)),
        },
    }
    if con_metricas_globales:
        documento["metricas_globales"] = metricas_globales(
            ids,
            referencia,
            predicciones,
            [caso.conjunto_verdad for caso in prueba],
        )
    return documento


def _nombre(ruta: pathlib.Path) -> str:
    return pathlib.Path(ruta).name


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
def _num(valor: Optional[float]) -> str:
    return "n/a" if valor is None else f"{valor:.4f}"


def _p(valor: Optional[float]) -> str:
    """Valor p: decimal si es >= 0,0001; notacion cientifica si es menor."""
    if valor is None:
        return "n/a"
    return f"{valor:.4f}" if valor >= 1e-4 else f"{valor:.3e}"


def renderizar(doc: Mapping) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF."""
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    lineas = [
        "# Contraste pareado linea de base frente a hibrido (c-213)",
        "",
        f"Sobre los mismos {doc['n']} casos con consenso. {doc['aditivo']['declaracion']}",
        "",
        "| Sistema | Aciertos estrictos |",
        "|---|---|",
    ]
    for nombre in SISTEMAS:
        lineas.append(f"| {nombre} | {doc['aciertos'][nombre]}/{doc['n']} |")
    for nombre in ("balanceada", "sin_repoderacion"):
        c = doc["contrastes"][nombre]
        t, m, d = c["tabla_2x2"], c["mcnemar"], c["diferencia_exactitud"]
        lineas += [
            "",
            f"## Hibrido frente a linea de base `{nombre}`",
            "",
            "| | Linea de base acierta | Linea de base falla |",
            "|---|---|---|",
            f"| Hibrido acierta | {t['ambos_aciertan']} | {t['solo_hibrido']} |",
            f"| Hibrido falla | {t['solo_linea_de_base']} | {t['ninguno']} |",
            "",
            f"- McNemar exacta bilateral: p = {_p(m['p_exacto'])}; corregida por continuidad: "
            f"p = {_p(m['p_corregido'])} (criterio de stats.py: {m['criterio_stats']}).",
            f"- Diferencia de exactitudes (hibrido - linea de base): {_num(d['valor'])}, "
            f"IC 95 % bootstrap pareado [{_num(d['ic95'][0])}; {_num(d['ic95'][1])}] "
            f"({d['remuestreos']} remuestreos, semilla {d['semilla']}).",
        ]
    if "metricas_globales" in doc:
        lineas += [
            "",
            f"## Metricas globales (n = {doc['n']})",
            "",
            "| Sistema | Exactitud estricta | Exactitud laxa | Macro-F1 | Balanced accuracy |",
            "|---|---|---|---|---|",
        ]
        for nombre in SISTEMAS:
            m = doc["metricas_globales"][nombre]
            estricta, laxa = m["exactitud_estricta"], m["exactitud_laxa"]
            lineas.append(
                f"| {nombre} | {estricta['aciertos']}/{estricta['n']} ({_num(estricta['valor'])}) | "
                f"{laxa['aciertos']}/{laxa['n']} ({_num(laxa['valor'])}) | {_num(m['macro_f1'])} | "
                f"{_num(m['balanced_accuracy'])} |"
            )
        lineas += [
            "",
            "### F1 por clase con soporte",
            "",
            "| Sistema | Sector | Precision | Sensibilidad | F1 | Soporte |",
            "|---|---|---|---|---|---|",
        ]
        for nombre in SISTEMAS:
            for clase in CLASES:
                datos = doc["metricas_globales"][nombre]["por_clase"][clase]
                lineas.append(
                    f"| {nombre} | {clase} | {_num(datos['precision'])} | "
                    f"{_num(datos['sensibilidad'])} | {_num(datos['f1'])} | {datos['soporte']} |"
                )
    return texto_json, "\n".join(lineas) + "\n"


def escribir(
    doc: Mapping,
    directorio: pathlib.Path,
    nombre_base: str = NOMBRE_BASE,
) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `SHA256SUMS` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for nombre, texto in ((f"{nombre_base}.json", texto_json), (f"{nombre_base}.md", texto_md)):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(r)}  {r.name}\n" for r in rutas)
    ruta_sumas = directorio / f"{nombre_base}.SHA256SUMS.txt"
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(
    salida: pathlib.Path = SALIDA,
    ruta_referencia: pathlib.Path = RUTA_CORPUS_INDEPENDIENTE,
    n_esperado: int = N_ESPERADO,
    anclas_esperadas: Optional[Mapping[str, int]] = None,
    *,
    ruta_pred_hibrido: pathlib.Path = RUTA_PRED_HIBRIDO,
    nombre_base: str = NOMBRE_BASE,
    con_metricas_globales: bool = False,
) -> list[pathlib.Path]:
    doc = construir_documento(
        ruta_referencia,
        n_esperado,
        ruta_pred_hibrido=ruta_pred_hibrido,
        anclas_esperadas=anclas_esperadas,
        con_metricas_globales=con_metricas_globales,
    )
    return escribir(doc, salida, nombre_base=nombre_base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--referencia", type=pathlib.Path, default=RUTA_CORPUS_INDEPENDIENTE)
    parser.add_argument("--predicciones", type=pathlib.Path, default=RUTA_PRED_HIBRIDO)
    parser.add_argument("--n-esperado", type=int, default=N_ESPERADO)
    parser.add_argument("--nombre", default=NOMBRE_BASE)
    parser.add_argument(
        "--anclas",
        nargs="+",
        default=None,
        metavar="SISTEMA=N",
        help="Aciertos estrictos esperados por sistema (p. ej. hibrido=142).",
    )
    args = parser.parse_args(argv)
    try:
        anclas = parsear_anclas(args.anclas)
        rutas = ejecutar(
            args.salida,
            args.referencia,
            args.n_esperado,
            anclas_esperadas=anclas,
            ruta_pred_hibrido=args.predicciones,
            nombre_base=args.nombre,
            con_metricas_globales=anclas is not None,
        )
    except (AnclaNoReproducida, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for ruta in rutas:
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
