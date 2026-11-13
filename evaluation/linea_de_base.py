"""Linea de base clasica supervisada para la clasificacion de la mesa de ayuda (c-209).

Entrena un clasificador supervisado clasico de texto (TF-IDF de palabras y de
caracteres mas regresion logistica regularizada de scikit-learn) con los 200 casos
in-sample del corpus de ajuste y predice los 103 casos fuera de muestra con
referencia por consenso E3/E4: el mismo n efectivo de c-191/c-205. Reutiliza las
funciones puras de `evaluation/metrics.py` para que las cifras sean comparables.

Totalmente offline: no usa red, ni Gemini, ni ninguna API paga. Deterministico:
semilla fija y dos corridas producen artefactos identicos byte a byte; el script
imprime el SHA-256 de cada salida. Es ADITIVO: no cambia ningun numero canonico ni
el clasificador de produccion. La comparacion con el hibrido se LEE de
`analisis_fuera_de_muestra_c205.json` y no se recalcula.

Uso:
    python3 -m evaluation.linea_de_base --salida <directorio>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import Counter
from typing import Iterable, Mapping, Optional, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from evaluation.campana import cargar_corpus_solo_lectura
from evaluation.corpus import SECTORES_CANONICOS, CasoEvaluacion
from evaluation.metrics import (
    aciertos_estrictos,
    aciertos_laxos,
    f1_macro,
    f1_por_clase,
    matriz_confusion,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
CLASES: list[str] = list(SECTORES_CANONICOS)

#: Semilla fija del modelo: garantiza reproducibilidad byte a byte.
SEMILLA: int = 42

#: Raiz del repositorio: `evaluation/linea_de_base.py` -> parents[1].
ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]

RUTA_CORPUS_CAMPANA: pathlib.Path = ROOT / "evaluation/data/campana/corpus_campana.json"
RUTA_CORPUS_INDEPENDIENTE: pathlib.Path = ROOT / "evaluation/data/campana/corpus_independiente.json"
RUTA_HIBRIDO_C205: pathlib.Path = (
    ROOT / "evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json"
)

NOMBRE_JSON: str = "linea_de_base_clasica_c210.json"
NOMBRE_MD: str = "linea_de_base_clasica_c210.md"

#: Variantes del modelo: la primaria re-pondera clases; la otra es sensibilidad.
VARIANTES: tuple[tuple[str, Optional[str]], ...] = (
    ("balanceada", "balanced"),
    ("sin_repoderacion", None),
)

#: n de prueba efectivo y discordantes excluidos (c-191/c-205): NO se reinterpretan.
N_PRUEBA_EFECTIVO: int = 103
DISCORDANTES_EXCLUIDOS: int = 47

ROTULO_MUESTRAL = "metricas sobre los 103 casos fuera de muestra tal como estan"
PROCEDENCIA_MUESTRAL = "corpus_independiente.json (referencia por consenso E3/E4)"
ROTULO_PONDERADA = (
    "post-estratificacion a la prevalencia natural de los 200 casos in-sample; no es una "
    "medicion nueva"
)
PROCEDENCIA_PONDERADA = "distribucion de sector_asignado de corpus_campana.json"

DECLARACION_ADITIVA = (
    "Las cifras de esta medicion son aditivas: no reemplazan ningun numero canonico de la "
    "tesis ni el clasificador de produccion. El n de prueba es el efectivo 103; los 47 "
    "discordantes sin referencia no se usan y no se extrapola al 150."
)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def sha256_de_archivo(ruta: pathlib.Path | str) -> str:
    """SHA-256 del contenido binario del archivo."""
    return hashlib.sha256(pathlib.Path(ruta).read_bytes()).hexdigest()


def _relativa(ruta: pathlib.Path) -> str:
    """Ruta relativa a la raiz del repositorio cuando es posible."""
    try:
        return str(ruta.relative_to(ROOT))
    except ValueError:
        return str(ruta)


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------
def construir_pipeline(class_weight: Optional[str]) -> Pipeline:
    """
    Pipeline TF-IDF (palabras + caracteres) + regresion logistica regularizada.

    `class_weight="balanced"` re-pondera las clases (el corpus de ajuste tiene una
    sola clase `Bases de Datos`); `class_weight=None` es la variante de sensibilidad.
    Semilla fija y `solver="lbfgs"`: deterministas en este entorno.
    """
    vectorizador = FeatureUnion(
        [
            (
                "palabras",
                TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, analyzer="word"),
            ),
            (
                "caracteres",
                TfidfVectorizer(ngram_range=(2, 5), sublinear_tf=True, analyzer="char_wb"),
            ),
        ]
    )
    clasificador = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        random_state=SEMILLA,
        class_weight=class_weight,
    )
    return Pipeline([("tfidf", vectorizador), ("logreg", clasificador)])


def predecir(
    entrenamiento: Sequence[CasoEvaluacion],
    prueba: Sequence[CasoEvaluacion],
    *,
    class_weight: Optional[str],
) -> list[str]:
    """Entrena con `entrenamiento` (verdad = `sector_asignado`) y predice `prueba`."""
    x_entrenamiento = [caso.descripcion for caso in entrenamiento]
    y_entrenamiento = [caso.sector_asignado for caso in entrenamiento]
    pipeline = construir_pipeline(class_weight)
    pipeline.fit(x_entrenamiento, y_entrenamiento)
    return [str(sector) for sector in pipeline.predict([caso.descripcion for caso in prueba])]


# ---------------------------------------------------------------------------
# Metricas
# ---------------------------------------------------------------------------
def metricas_de_prediccion(
    reales: Sequence[str],
    predichos: Sequence[str],
    conjuntos_verdad: Iterable[Iterable[str]],
) -> dict:
    """Metricas globales y por clase con las funciones puras de `evaluation/metrics.py`."""
    reales = list(reales)
    predichos = list(predichos)
    conjuntos_verdad = [frozenset(conjunto) for conjunto in conjuntos_verdad]
    n = len(reales)

    matriz = matriz_confusion(reales, predichos)
    precision = precision_por_clase(matriz)
    sensibilidad = sensibilidad_por_clase(matriz)
    f1 = f1_por_clase(matriz)
    soporte = soporte_por_clase(matriz)

    estrictos = aciertos_estrictos(reales, predichos)
    laxos = aciertos_laxos(predichos, conjuntos_verdad)
    balanced = sum(sensibilidad[clase] for clase in CLASES) / len(CLASES)

    por_clase = {
        clase: {
            "precision": precision[clase],
            "sensibilidad": sensibilidad[clase],
            "f1": f1[clase],
            "soporte": soporte[clase],
        }
        for clase in CLASES
    }
    return {
        "n": n,
        "exactitud_estricta": {
            "aciertos": estrictos,
            "n": n,
            "valor": estrictos / n if n else 0.0,
        },
        "exactitud_laxa": {
            "aciertos": laxos,
            "n": n,
            "valor": laxos / n if n else 0.0,
        },
        "macro_f1": f1_macro(f1),
        "macro_f1_definicion": (
            "media aritmetica de las cinco F1 por clase, incluida toda clase de soporte cero "
            "(F1 = 0.0)"
        ),
        "balanced_accuracy": balanced,
        "balanced_accuracy_definicion": "media aritmetica de las sensibilidades por clase",
        "por_clase": por_clase,
        "matriz_confusion": {
            "filas": "sector de referencia (sector_asignado)",
            "columnas": "sector predicho principal",
            "orden": list(CLASES),
            "celdas": matriz,
        },
    }


def prevalencia_natural(casos: Sequence[CasoEvaluacion]) -> dict[str, float]:
    """Distribucion de `sector_asignado` de los casos de ajuste (prevalencia natural)."""
    conteo = Counter(caso.sector_asignado for caso in casos)
    total = len(casos)
    if total == 0:
        raise ValueError("la prevalencia natural exige al menos un caso de ajuste.")
    return {clase: conteo.get(clase, 0) / total for clase in CLASES}


def lectura_ponderada(
    por_clase: Mapping[str, Mapping[str, float]],
    prevalencia: Mapping[str, float],
) -> dict:
    """
    Re-pondera las metricas por clase a la prevalencia natural declarada.

    `macro_f1` ponderado = suma(prevalencia * f1); `balanced_accuracy` ponderada =
    suma(prevalencia * sensibilidad); la precision ponderada es la suma analoga.
    """
    precision = sum(prevalencia[clase] * por_clase[clase]["precision"] for clase in CLASES)
    sensibilidad = sum(prevalencia[clase] * por_clase[clase]["sensibilidad"] for clase in CLASES)
    f1 = sum(prevalencia[clase] * por_clase[clase]["f1"] for clase in CLASES)
    return {
        "precision": precision,
        "sensibilidad": sensibilidad,
        "f1": f1,
        "macro_f1": f1,
        "balanced_accuracy": sensibilidad,
        "f1_por_clase": {clase: por_clase[clase]["f1"] for clase in CLASES},
    }


# ---------------------------------------------------------------------------
# Comparacion con el hibrido (se LEE de c-205, no se recalcula)
# ---------------------------------------------------------------------------
def leer_comparacion_hibrido(ruta: pathlib.Path | str) -> dict:
    """Cifras del hibrido tomadas del artefacto de c-205, con su procedencia."""
    ruta = pathlib.Path(ruta)
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    return {
        "sistema": "hybrid-v3",
        "procedencia": _relativa(ruta),
        "rotulo": (
            "cifras canonicas del hibrido en el mismo n efectivo 103; se LEEN del artefacto "
            "de c-205 y no se recalculan"
        ),
        "n": documento["n_efectivo"],
        "exactitud_estricta": documento["exactitud_estricta"],
        "exactitud_laxa": documento["exactitud_laxa"],
        "macro_f1": documento["macro_f1"],
        "balanced_accuracy": documento["balanced_accuracy"],
        "por_clase": documento["por_clase"],
    }


def _veredicto(comparacion: dict, metricas_balanceada: dict, metricas_sin: dict) -> dict:
    """Veredicto honesto: la linea de base frente al hibrido, con las cifras exactas."""
    base = metricas_balanceada["exactitud_estricta"]["valor"]
    hibrido = comparacion["exactitud_estricta"]["valor"]
    delta = base - hibrido
    if delta > 0:
        lectura = "La linea de base balanceada supera al hibrido en exactitud estricta."
    elif delta < 0:
        lectura = "La linea de base balanceada queda por debajo del hibrido en exactitud estricta."
    else:
        lectura = "La linea de base balanceada iguala al hibrido en exactitud estricta."
    return {
        "lectura": lectura,
        "exactitud_estricta_linea_de_base_balanceada": base,
        "exactitud_estricta_hibrido": hibrido,
        "diferencia_balanceada_menos_hibrido": delta,
        "exactitud_estricta_linea_de_base_sin_repoderacion": metricas_sin["exactitud_estricta"][
            "valor"
        ],
        "declaracion": (
            "Veredicto honesto y sin maquillaje: se reportan las dos variantes de la linea de "
            "base y se declara el resultado tal como se mide, sea favorable o desfavorable."
        ),
    }


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def construir_documento(
    ruta_entrenamiento: pathlib.Path | str | None = None,
    ruta_prueba: pathlib.Path | str | None = None,
    ruta_hibrido: pathlib.Path | str | None = None,
) -> dict:
    """Construye el documento de la medicion de la linea de base (determinista)."""
    ruta_entrenamiento = pathlib.Path(ruta_entrenamiento or RUTA_CORPUS_CAMPANA)
    ruta_prueba = pathlib.Path(ruta_prueba or RUTA_CORPUS_INDEPENDIENTE)
    ruta_hibrido = pathlib.Path(ruta_hibrido or RUTA_HIBRIDO_C205)

    entrenamiento = cargar_corpus_solo_lectura(ruta_entrenamiento)
    prueba = cargar_corpus_solo_lectura(ruta_prueba)

    reales = [caso.sector_asignado for caso in prueba]
    conjuntos_verdad = [caso.conjunto_verdad for caso in prueba]
    prevalencia = prevalencia_natural(entrenamiento)

    variantes: dict[str, dict] = {}
    metricas_muestrales: dict[str, dict] = {}
    for nombre, class_weight in VARIANTES:
        predichos = predecir(entrenamiento, prueba, class_weight=class_weight)
        metricas = metricas_de_prediccion(reales, predichos, conjuntos_verdad)
        metricas_muestrales[nombre] = metricas
        variantes[nombre] = {
            "class_weight": class_weight,
            "lectura_muestral": {
                "rotulo": ROTULO_MUESTRAL,
                "procedencia": PROCEDENCIA_MUESTRAL,
                "metricas": metricas,
            },
            "lectura_ponderada_prevalencia_natural": {
                "rotulo": ROTULO_PONDERADA,
                "procedencia": PROCEDENCIA_PONDERADA,
                **lectura_ponderada(metricas["por_clase"], prevalencia),
            },
        }

    comparacion = leer_comparacion_hibrido(ruta_hibrido)

    return {
        "change": "c-210-medicion-de-la-linea-de-base",
        "generador": "evaluation/linea_de_base.py",
        "metodo": (
            "TF-IDF (palabras y caracteres) + regresion logistica regularizada (scikit-learn); "
            "metricas con evaluation/metrics.py; sin red ni Gemini; deterministico"
        ),
        "semilla": SEMILLA,
        "entradas_sha256": {
            "corpus_campana.json": sha256_de_archivo(ruta_entrenamiento),
            "corpus_independiente.json": sha256_de_archivo(ruta_prueba),
            "analisis_fuera_de_muestra_c205.json": sha256_de_archivo(ruta_hibrido),
        },
        "n_entrenamiento": len(entrenamiento),
        "n_prueba": len(prueba),
        "n_prueba_efectivo_declarado": N_PRUEBA_EFECTIVO,
        "discordantes_excluidos": DISCORDANTES_EXCLUIDOS,
        "excluidos": DISCORDANTES_EXCLUIDOS,
        "total_primaria": comparacion["n"] + DISCORDANTES_EXCLUIDOS,
        "prevalencia_natural": prevalencia,
        "variantes": variantes,
        "comparacion_hibrido": comparacion,
        "veredicto": _veredicto(
            comparacion,
            metricas_muestrales["balanceada"],
            metricas_muestrales["sin_repoderacion"],
        ),
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "declaracion": DECLARACION_ADITIVA,
            "no_se_reinterpreta_el_150": True,
        },
    }


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def _tabla_por_clase(por_clase: Mapping[str, Mapping[str, float]]) -> list[str]:
    lineas = ["| Sector | Precision | Sensibilidad | F1 | Soporte |", "|---|---|---|---|---|"]
    for clase in CLASES:
        datos = por_clase[clase]
        lineas.append(
            f"| {clase} | {datos['precision']:.4f} | {datos['sensibilidad']:.4f} | "
            f"{datos['f1']:.4f} | {datos['soporte']} |"
        )
    return lineas


def renderizar_md(doc: Mapping) -> str:
    """Resumen legible en Markdown (LF, UTF-8 sin BOM)."""
    comparacion = doc["comparacion_hibrido"]
    balanceada = doc["variantes"]["balanceada"]["lectura_muestral"]["metricas"]
    sin_rep = doc["variantes"]["sin_repoderacion"]["lectura_muestral"]["metricas"]
    ponderada = doc["variantes"]["balanceada"]["lectura_ponderada_prevalencia_natural"]
    veredicto = doc["veredicto"]

    lineas = [
        "# Linea de base clasica (c-210)",
        "",
        "TF-IDF (palabras y caracteres) + regresion logistica regularizada de scikit-learn. "
        "Reutiliza `evaluation/metrics.py`. Sin red, sin Gemini, sin API paga. Deterministico.",
        "",
        "## Conjunto de evaluacion",
        "",
        f"- Entrenamiento: {doc['n_entrenamiento']} casos in-sample (verdad = sector_asignado).",
        f"- Prueba: {doc['n_prueba']} casos fuera de muestra con referencia E3/E4 (n efectivo "
        f"declarado {doc['n_prueba_efectivo_declarado']}).",
        f"- Discordantes excluidos: {doc['discordantes_excluidos']} de {doc['total_primaria']}; "
        "no se usan ni se reinterpretan.",
        "",
        "## Metricas muestrales (n = 103)",
        "",
        "| Sistema | Exactitud estricta | Exactitud laxa | Macro-F1 | Balanced accuracy |",
        "|---|---|---|---|---|",
        f"| Linea de base (balanceada) | {balanceada['exactitud_estricta']['valor']:.4f} | "
        f"{balanceada['exactitud_laxa']['valor']:.4f} | {balanceada['macro_f1']:.4f} | "
        f"{balanceada['balanced_accuracy']:.4f} |",
        f"| Linea de base (sin re-ponderacion) | {sin_rep['exactitud_estricta']['valor']:.4f} | "
        f"{sin_rep['exactitud_laxa']['valor']:.4f} | {sin_rep['macro_f1']:.4f} | "
        f"{sin_rep['balanced_accuracy']:.4f} |",
        f"| Hibrido hybrid-v3 (c-205) | {comparacion['exactitud_estricta']['valor']:.4f} | "
        f"{comparacion['exactitud_laxa']['valor']:.4f} | {comparacion['macro_f1']:.4f} | "
        f"{comparacion['balanced_accuracy']['valor']:.4f} |",
        "",
        "## F1 por clase con soporte",
        "",
        "Linea de base (balanceada):",
        "",
        *_tabla_por_clase(balanceada["por_clase"]),
        "",
        "Hibrido hybrid-v3 (c-205):",
        "",
        *_tabla_por_clase(comparacion["por_clase"]),
        "",
        "## Lectura ponderada a la prevalencia natural (linea de base balanceada)",
        "",
        f"- Rotulo: {ponderada['rotulo']}.",
        f"- Procedencia: {ponderada['procedencia']}.",
        f"- Macro-F1 ponderado: {ponderada['macro_f1']:.4f}; balanced accuracy ponderada: "
        f"{ponderada['balanced_accuracy']:.4f}.",
        "",
        "## Veredicto",
        "",
        f"- {veredicto['lectura']}",
        f"- Exactitud estricta: linea de base (balanceada) "
        f"{veredicto['exactitud_estricta_linea_de_base_balanceada']:.4f}; hibrido "
        f"{veredicto['exactitud_estricta_hibrido']:.4f}; diferencia "
        f"{veredicto['diferencia_balanceada_menos_hibrido']:+.4f}.",
        f"- Sin re-ponderacion: {veredicto['exactitud_estricta_linea_de_base_sin_repoderacion']:.4f}.",
        f"- {veredicto['declaracion']}",
        "",
        "## Declaracion aditiva",
        "",
        f"- {doc['aditivo']['declaracion']}",
        "",
    ]
    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------------------------
# Salidas y CLI
# ---------------------------------------------------------------------------
def escribir_salidas(
    doc: Mapping,
    directorio: pathlib.Path | str,
    nombre_sums: str = "SHA256SUMS.txt",
) -> dict[str, str]:
    """Escribe el JSON, el Markdown y el archivo de sumas; devuelve el SHA-256 de cada salida."""
    directorio = pathlib.Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta_json = directorio / NOMBRE_JSON
    ruta_md = directorio / NOMBRE_MD

    ruta_json.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    ruta_md.write_text(renderizar_md(doc), encoding="utf-8", newline="\n")

    hashes = {
        ruta_json.name: sha256_de_archivo(ruta_json),
        ruta_md.name: sha256_de_archivo(ruta_md),
    }
    sumas = "\n".join(f"{digest}  {nombre}" for nombre, digest in hashes.items()) + "\n"
    (directorio / nombre_sums).write_text(sumas, encoding="utf-8", newline="\n")
    return hashes


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI: construye el documento y escribe las salidas; imprime el SHA-256 de cada una."""
    parser = argparse.ArgumentParser(
        description="Medicion de la linea de base clasica (c-209/c-210)."
    )
    parser.add_argument("--salida", required=True, help="Directorio de salida.")
    parser.add_argument("--nombre-sums", default="SHA256SUMS.txt", help="Nombre del archivo de sumas.")
    parser.add_argument("--entrenamiento", default=str(RUTA_CORPUS_CAMPANA))
    parser.add_argument("--prueba", default=str(RUTA_CORPUS_INDEPENDIENTE))
    parser.add_argument("--hibrido", default=str(RUTA_HIBRIDO_C205))
    args = parser.parse_args(argv)

    documento = construir_documento(args.entrenamiento, args.prueba, args.hibrido)
    hashes = escribir_salidas(documento, args.salida, args.nombre_sums)
    for nombre, digest in sorted(hashes.items()):
        print(f"{digest}  {nombre}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
