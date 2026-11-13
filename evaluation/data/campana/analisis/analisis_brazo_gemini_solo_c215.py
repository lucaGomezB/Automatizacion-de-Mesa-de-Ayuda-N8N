#!/usr/bin/env python3
"""Analisis pareado del brazo «Gemini solo» frente al hibrido congelado (c-215).

Solo lectura y determinista. Toma el cache JSONL del brazo (`evaluation/brazo_gemini_solo.py`)
y las predicciones congeladas de `hybrid-v3`, y calcula por bloque (dentro de la muestra: 200;
fuera de muestra: 103) la calidad (exactitud estricta y laxa, macro-F1), el contraste pareado
(McNemar exacta bilateral y diferencia de exactitudes con IC bootstrap pareado), la eficiencia
(llamadas, tokens, costo y latencia por caso), el control de deriva y el veredicto de tres vias
de la hipotesis de eficiencia, segun la regla PRERREGISTRADA en
`openspec/changes/c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia/design.md`.

Sin red y sin Gemini. Si el cache real no existe o esta incompleto, sale con codigo distinto de
cero y NO escribe salidas. Aditivo: no reemplaza ningun numero canonico.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.brazo_gemini_solo import (  # noqa: E402
    BLOQUE_DENTRO,
    BLOQUE_FUERA,
    RUTA_CACHE_DEFECTO,
    RUTA_CORPUS_DENTRO,
    RUTA_CORPUS_FUERA,
    leer_cache,
)
from evaluation.campana import cargar_corpus_solo_lectura  # noqa: E402
from evaluation.corpus import SECTORES_CANONICOS  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    NIVEL_CONFIANZA,
    SEMILLA_BOOTSTRAP,
    intervalo_wilson,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.run_evaluation import _compute_corpus_hash, cargar_predicciones  # noqa: E402
from evaluation.stats import contraste_mcnemar  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent
RUTA_HIBRIDO_DENTRO = ROOT / "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"
RUTA_HIBRIDO_FUERA = ROOT / "evaluation/data/campana/predicciones_independiente.json"

NOMBRE_BASE = "analisis_brazo_gemini_solo_c215"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

REMUESTREOS = 10_000

# Parametros PRERREGISTRADOS en design.md D7 y D8 (no se ajustan con los datos).
MARGEN_NO_INFERIORIDAD = 0.05
UMBRAL_RAZON_EFICIENCIA = 0.90
TOPE_TASA_FALLOS = 0.05
UMBRAL_CONCORDANCIA_DERIVA = 0.90
BLOQUE_PRIMARIO = BLOQUE_FUERA

DECLARACION_ADITIVA = (
    "Las cifras de este analisis son aditivas: no reemplazan ningun numero canonico de la tesis "
    "ni el clasificador de produccion. Comparan al hibrido congelado con el brazo «Gemini solo» "
    "(una sola corrida, temperatura 0,3), pareado caso a caso."
)


class CacheAusenteError(RuntimeError):
    """No existe el cache del brazo: la corrida paga todavia no se hizo."""


class CorridaIncompletaError(RuntimeError):
    """El cache no cubre exactamente los casos esperados o no corresponde a los corpus vigentes."""


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def decidir(
    *,
    delta_inf: float,
    delta_sup: float,
    razon_costo_sup: Optional[float],
    razon_llamadas_sup: Optional[float],
    tasa_fallos: float,
    margen: float = MARGEN_NO_INFERIORIDAD,
    umbral_razon: float = UMBRAL_RAZON_EFICIENCIA,
    tope_fallos: float = TOPE_TASA_FALLOS,
) -> dict:
    """Regla de tres vias prerregistrada (design.md D7). Funcion pura."""
    if delta_inf > -margen:
        exactitud = "no inferior"
    elif delta_sup < -margen:
        exactitud = "inferior"
    else:
        exactitud = "indeterminado"
    cumplida = (
        razon_costo_sup is not None
        and razon_llamadas_sup is not None
        and razon_costo_sup < umbral_razon
        and razon_llamadas_sup < umbral_razon
    )
    eficiencia = "cumplido" if cumplida else "no cumplido"
    if tasa_fallos > tope_fallos:
        veredicto = "no concluyente"
        motivo = (
            f"el {tasa_fallos:.1%} de los casos del brazo «Gemini solo» termino en fallback o error, "
            f"por encima del tope de {tope_fallos:.0%}: la medicion del brazo queda comprometida"
        )
    elif exactitud == "inferior" or eficiencia == "no cumplido":
        veredicto = "no sostenida"
        motivo = (
            "el hibrido es inferior en exactitud por mas del margen"
            if exactitud == "inferior"
            else f"el ahorro no es material: algun limite superior de las razones no es menor que {umbral_razon}"
        )
    elif exactitud == "no inferior":
        veredicto = "sostenida"
        motivo = "no inferior en exactitud y con ahorro material de llamadas y costo"
    else:
        veredicto = "no concluyente"
        motivo = "la no inferioridad en exactitud es indeterminada con el ahorro cumplido"
    return {
        "margen_no_inferioridad": margen,
        "umbral_razon": umbral_razon,
        "tope_tasa_fallos": tope_fallos,
        "tasa_fallos": tasa_fallos,
        "componente_exactitud": exactitud,
        "componente_eficiencia": eficiencia,
        "veredicto": veredicto,
        "motivo": motivo,
    }


def f1_macro_con_sin_prediccion(reales: Sequence[str], predichos: Sequence[Optional[str]]) -> float:
    """Macro-F1 sobre las cinco clases; un caso sin prediccion (None) es falso negativo de su clase."""
    f1s = []
    for clase in SECTORES_CANONICOS:
        tp = sum(1 for r, p in zip(reales, predichos) if r == clase and p == clase)
        fp = sum(1 for r, p in zip(reales, predichos) if r != clase and p == clase)
        fn = sum(1 for r, p in zip(reales, predichos) if r == clase and p != clase)
        denominador = 2 * tp + fp + fn
        f1s.append(2 * tp / denominador if denominador else 0.0)
    return sum(f1s) / len(f1s)


def _diferencia(a: Sequence[bool], b: Sequence[bool], indices: Sequence[int]) -> float:
    return sum(int(a[i]) - int(b[i]) for i in indices) / len(indices)


def _contraste(aciertos_h: Sequence[bool], aciertos_l: Sequence[bool], remuestras: List[List[int]], semilla: int) -> dict:
    mc = contraste_mcnemar(aciertos_h, aciertos_l)
    n = mc.pares
    valor = _diferencia(aciertos_h, aciertos_l, range(n)) if n else 0.0
    if mc.aplicable:
        inferior, superior = percentil_intervalo(
            [_diferencia(aciertos_h, aciertos_l, idx) for idx in remuestras], NIVEL_CONFIANZA
        )
    else:
        inferior = superior = valor
    return {
        "n": n,
        "tabla_2x2": {
            "ambos_aciertan": mc.ambas,
            "solo_hibrido": mc.solo_a,
            "solo_gemini_solo": mc.solo_b,
            "ninguno": mc.ninguna,
        },
        "mcnemar": {
            "aplicable": mc.aplicable,
            "p_exacto": mc.p_exacto,
            "p_corregido": mc.p_corregido,
            "estadistico_corregido": mc.estadistico,
            "criterio_stats": mc.criterio,
        },
        "diferencia_exactitud": {
            "definicion": "exactitud(hibrido) - exactitud(gemini solo) = (b - c) / n",
            "valor": valor,
            "ic95": [inferior, superior],
            "metodo_ic": "bootstrap percentil pareado (remuestreo de casos)",
            "remuestreos": len(remuestras),
            "semilla": semilla,
        },
    }


def _proporcion(aciertos: int, n: int) -> dict:
    inferior, superior = intervalo_wilson(aciertos, n)
    return {
        "aciertos": aciertos,
        "n": n,
        "valor": aciertos / n if n else 0.0,
        "ic95_wilson": [inferior, superior],
    }


def _calidad_brazo(reales: Sequence[str], predichos: Sequence[Optional[str]], verdad: Sequence[frozenset]) -> dict:
    estrictos = sum(1 for r, p in zip(reales, predichos) if r == p)
    laxos = sum(1 for p, v in zip(predichos, verdad) if p is not None and p in v)
    n = len(reales)
    return {
        "exactitud_estricta": _proporcion(estrictos, n),
        "exactitud_laxa": _proporcion(laxos, n),
        "macro_f1": f1_macro_con_sin_prediccion(reales, predichos),
    }


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(pathlib.Path(ruta).read_bytes()).hexdigest()


def _verificar_ids(rotulo: str, esperados: Sequence[str], presentes: Sequence[str]) -> None:
    faltan = [i for i in esperados if i not in set(presentes)]
    sobran = [i for i in presentes if i not in set(esperados)]
    if faltan or sobran:
        raise CorridaIncompletaError(
            f"{rotulo}: faltan {len(faltan)} casos {faltan[:5]} y sobran {len(sobran)} {sobran[:5]}"
        )


def _analizar_bloque(
    bloque: str,
    corpus: Sequence[Any],
    hibrido: Mapping[str, Any],
    gemini_solo: Mapping[str, dict],
    remuestreos: int,
) -> dict:
    ids = [c.id for c in corpus]
    _verificar_ids(f"hibrido ({bloque})", ids, list(hibrido))
    _verificar_ids(f"cache del brazo ({bloque})", ids, [i for i, r in gemini_solo.items() if r["bloque"] == bloque])
    reales = [c.sector_asignado for c in corpus]
    verdad = [c.conjunto_verdad for c in corpus]
    pred_h = [hibrido[i].sector_predicho for i in ids]
    pred_l = [gemini_solo[i]["sector_predicho"] for i in ids]
    acierto_h = [r == p for r, p in zip(reales, pred_h)]
    acierto_l = [r == p for r, p in zip(reales, pred_l)]
    remuestras = list(remuestreos_indices(random.Random(SEMILLA_BOOTSTRAP), len(ids), remuestreos))
    return {
        "n": len(ids),
        "brazos": {
            "H": _calidad_brazo(reales, pred_h, verdad),
            "L": _calidad_brazo(reales, pred_l, verdad),
        },
        "contraste": _contraste(acierto_h, acierto_l, remuestras, SEMILLA_BOOTSTRAP),
    }


def construir_documento(
    ruta_cache: pathlib.Path = RUTA_CACHE_DEFECTO,
    *,
    ruta_corpus_dentro: pathlib.Path = RUTA_CORPUS_DENTRO,
    ruta_corpus_fuera: pathlib.Path = RUTA_CORPUS_FUERA,
    ruta_hibrido_dentro: pathlib.Path = RUTA_HIBRIDO_DENTRO,
    ruta_hibrido_fuera: pathlib.Path = RUTA_HIBRIDO_FUERA,
    remuestreos: int = REMUESTREOS,
) -> dict:
    """Calcula el analisis; falla antes de devolver nada si el cache falta o no cuadra."""
    ruta_cache = pathlib.Path(ruta_cache)
    if not ruta_cache.exists():
        raise CacheAusenteError(
            f"no existe el cache del brazo «Gemini solo» ({ruta_cache}): la corrida paga todavia no se hizo"
        )
    meta, gemini_solo, _ = leer_cache(ruta_cache)
    if meta is None:
        raise CorridaIncompletaError(f"el cache {ruta_cache.name} no tiene la linea de metadatos")
    for clave, ruta in (("corpus_hash_dentro", ruta_corpus_dentro), ("corpus_hash_fuera", ruta_corpus_fuera)):
        if meta.get(clave) != _compute_corpus_hash(pathlib.Path(ruta)):
            raise CorridaIncompletaError(
                f"{clave} del cache ({meta.get(clave)}) difiere del corpus vigente {pathlib.Path(ruta).name}"
            )
    bloques = {}
    for bloque, ruta_corpus, ruta_h in (
        (BLOQUE_DENTRO, ruta_corpus_dentro, ruta_hibrido_dentro),
        (BLOQUE_FUERA, ruta_corpus_fuera, ruta_hibrido_fuera),
    ):
        corpus = cargar_corpus_solo_lectura(ruta_corpus)
        hibrido = {p.caso_id: p for p in cargar_predicciones(pathlib.Path(ruta_h))}
        bloques[bloque] = _analizar_bloque(bloque, corpus, hibrido, gemini_solo, remuestreos)
    return {
        "change": "c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia",
        "generador": "evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py",
        "bloques": bloques,
        "aditivo": {"reemplaza_numeros_canonicos": False, "declaracion": DECLARACION_ADITIVA},
    }
