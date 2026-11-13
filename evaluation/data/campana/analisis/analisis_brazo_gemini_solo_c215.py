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


def _razon(numerador: Sequence[float], denominador: Sequence[float], remuestras: List[List[int]]) -> dict:
    """Razon `sum(num) / sum(den)` con IC95 bootstrap pareado (mismos remuestreos de casos)."""
    total = sum(denominador)
    valor = sum(numerador) / total if total else None
    muestras = []
    for idx in remuestras:
        d = sum(denominador[i] for i in idx)
        if d:
            muestras.append(sum(numerador[i] for i in idx) / d)
    ic = list(percentil_intervalo(muestras, NIVEL_CONFIANZA)) if muestras and valor is not None else None
    return {"valor": valor, "ic95": ic}


def _costo_usd(tokens_entrada: float, tokens_salida: float, precio: Mapping[str, float]) -> float:
    return tokens_entrada * 1e-6 * precio["entrada"] + tokens_salida * 1e-6 * precio["salida"]


NOTA_LATENCIA = (
    "Latencia de clasificacion del lado del cliente, medida desde la maquina de los autores; no es "
    "tiempo de extremo a extremo. Para el hibrido se imputa la latencia de Gemini del mismo caso "
    "donde escalo y 0 ms donde resolvieron las reglas (cota inferior: las reglas tardan milisegundos). "
    "No entra en la regla de decision."
)


def _eficiencia(
    ids: Sequence[str],
    escalado: Sequence[bool],
    gemini_solo: Mapping[str, dict],
    precios: Mapping[str, Mapping[str, float]],
    remuestras: List[List[int]],
) -> dict:
    registros = [gemini_solo[i] for i in ids]
    llamadas_l = [int(r["intentos"]) for r in registros]
    llamadas_h = [c if e else 0 for c, e in zip(llamadas_l, escalado)]
    entrada_l = [int(r["tokens_entrada"]) for r in registros]
    salida_l = [int(r["tokens_salida"]) for r in registros]
    entrada_h = [t if e else 0 for t, e in zip(entrada_l, escalado)]
    salida_h = [t if e else 0 for t, e in zip(salida_l, escalado)]
    latencia_l = [float(r["latencia_ms"]) for r in registros]
    latencia_h = [t if e else 0.0 for t, e in zip(latencia_l, escalado)]
    costo_l = {k: [_costo_usd(a, b, p) for a, b in zip(entrada_l, salida_l)] for k, p in precios.items()}
    costo_h = {k: [_costo_usd(a, b, p) for a, b in zip(entrada_h, salida_h)] for k, p in precios.items()}
    principal = "introductorio"
    diferencias = [a - b for a, b in zip(latencia_l, latencia_h)]
    n = len(ids)
    muestras_lat = [sum(diferencias[i] for i in idx) / n for idx in remuestras]
    inferior, superior = percentil_intervalo(muestras_lat, NIVEL_CONFIANZA) if muestras_lat else (0.0, 0.0)
    fallos = sum(1 for r in registros if r["etapa"] == "fallback")
    return {
        "llamadas": {
            "L": sum(llamadas_l),
            "H": sum(llamadas_h),
            "por_caso_L": sum(llamadas_l) / n,
            "por_caso_H": sum(llamadas_h) / n,
            "razon": _razon(llamadas_h, llamadas_l, remuestras),
        },
        "tokens": {
            "L": {"entrada": sum(entrada_l), "salida": sum(salida_l)},
            "H": {"entrada": sum(entrada_h), "salida": sum(salida_h)},
            "casos_con_tokens_supuestos": sum(1 for r in registros if r.get("tokens_origen") != "api"),
        },
        "costo_usd": {k: {"L": sum(costo_l[k]), "H": sum(costo_h[k])} for k in precios},
        "razon_costo": {
            **_razon(costo_h[principal], costo_l[principal], remuestras),
            "escenario": principal,
            "nota": "la razon no depende del escenario: ambos precios son proporcionales",
        },
        "latencia_ms": {
            "media_L": sum(latencia_l) / n,
            "media_H": sum(latencia_h) / n,
            "diferencia_L_menos_H": {
                "valor": sum(diferencias) / n,
                "ic95": [inferior, superior],
                "remuestreos": len(remuestras),
            },
            "nota": NOTA_LATENCIA,
        },
        "casos_escalados_h": sum(escalado),
        "fallbacks_o_errores_l": fallos,
        "tasa_fallos_l": fallos / n,
    }


def _decision_de(contraste: Mapping, eficiencia: Mapping) -> dict:
    d = contraste["diferencia_exactitud"]["ic95"]

    def limite_superior(razon: Mapping) -> Optional[float]:
        return razon["ic95"][1] if razon["ic95"] else None

    return decidir(
        delta_inf=d[0],
        delta_sup=d[1],
        razon_costo_sup=limite_superior(eficiencia["razon_costo"]),
        razon_llamadas_sup=limite_superior(eficiencia["llamadas"]["razon"]),
        tasa_fallos=eficiencia["tasa_fallos_l"],
    )


def _deriva_de_un_bloque(
    ids: Sequence[str], escalado: Sequence[bool], pred_h: Sequence[Optional[str]], pred_l: Sequence[Optional[str]],
    reales: Sequence[str],
) -> dict:
    seleccion = [k for k, e in enumerate(escalado) if e]
    concordantes = sum(1 for k in seleccion if pred_h[k] == pred_l[k])
    mc = contraste_mcnemar([reales[k] == pred_h[k] for k in seleccion], [reales[k] == pred_l[k] for k in seleccion])
    return {
        "n_escalados": len(seleccion),
        "concordancia": _proporcion(concordantes, len(seleccion)),
        "mcnemar_aciertos_h_vs_nueva": {
            "aplicable": mc.aplicable,
            "p_exacto": mc.p_exacto,
            "solo_cache_h": mc.solo_a,
            "solo_nueva_corrida": mc.solo_b,
        },
    }


def _analizar_bloque(
    bloque: str,
    corpus: Sequence[Any],
    hibrido: Mapping[str, Any],
    gemini_solo: Mapping[str, dict],
    precios: Mapping[str, Mapping[str, float]],
    remuestreos: int,
) -> dict:
    ids = [c.id for c in corpus]
    _verificar_ids(f"hibrido ({bloque})", ids, list(hibrido))
    _verificar_ids(f"cache del brazo ({bloque})", ids, [i for i, r in gemini_solo.items() if r["bloque"] == bloque])
    reales = [c.sector_asignado for c in corpus]
    verdad = [c.conjunto_verdad for c in corpus]
    pred_h = [hibrido[i].sector_predicho for i in ids]
    pred_l = [gemini_solo[i]["sector_predicho"] for i in ids]
    escalado = [hibrido[i].etapa != "deterministic" for i in ids]
    pred_hstar = [l if e else h for h, l, e in zip(pred_h, pred_l, escalado)]
    acierto_h = [r == p for r, p in zip(reales, pred_h)]
    acierto_l = [r == p for r, p in zip(reales, pred_l)]
    acierto_hstar = [r == p for r, p in zip(reales, pred_hstar)]
    remuestras = list(remuestreos_indices(random.Random(SEMILLA_BOOTSTRAP), len(ids), remuestreos))
    contraste = _contraste(acierto_h, acierto_l, remuestras, SEMILLA_BOOTSTRAP)
    eficiencia = _eficiencia(ids, escalado, gemini_solo, precios, remuestras)
    contraste_hstar = _contraste(acierto_hstar, acierto_l, remuestras, SEMILLA_BOOTSTRAP)
    return {
        "n": len(ids),
        "brazos": {
            "H": _calidad_brazo(reales, pred_h, verdad),
            "L": _calidad_brazo(reales, pred_l, verdad),
        },
        "contraste": contraste,
        "eficiencia": eficiencia,
        "decision": _decision_de(contraste, eficiencia),
        "sensibilidad_hstar": {
            "definicion": (
                "H*: prediccion cacheada de H donde las reglas resolvieron y prediccion NUEVA de L "
                "donde H escalo; aisla el enrutamiento del ruido o la deriva del modelo"
            ),
            "exactitud_estricta": _proporcion(sum(acierto_hstar), len(ids)),
            "contraste": contraste_hstar,
            "decision": _decision_de(contraste_hstar, eficiencia),
        },
        "_deriva": _deriva_de_un_bloque(ids, escalado, pred_h, pred_l, reales),
        "_escalados": [(pred_h[k], pred_l[k], reales[k]) for k, e in enumerate(escalado) if e],
    }


def _control_deriva(bloques: Mapping[str, dict]) -> dict:
    por_bloque = {nombre: b["_deriva"] for nombre, b in bloques.items()}
    pares = [p for b in bloques.values() for p in b["_escalados"]]
    concordantes = sum(1 for h, l, _ in pares if h == l)
    mc = contraste_mcnemar([r == h for h, _, r in pares], [r == l for _, l, r in pares])
    total = {
        "n_escalados": len(pares),
        "concordancia": _proporcion(concordantes, len(pares)),
        "mcnemar_aciertos_h_vs_nueva": {
            "aplicable": mc.aplicable,
            "p_exacto": mc.p_exacto,
            "solo_cache_h": mc.solo_a,
            "solo_nueva_corrida": mc.solo_b,
        },
    }
    bandera = bool(pares) and total["concordancia"]["valor"] < UMBRAL_CONCORDANCIA_DERIVA
    return {
        **por_bloque,
        "total": total,
        "umbral": UMBRAL_CONCORDANCIA_DERIVA,
        "bandera": bandera,
        "lectura": (
            "deriva o ruido relevante: leer el contraste con cautela (la concordancia con la prediccion "
            "cacheada de H en los casos que H ya escalo es menor que el umbral; este control no separa "
            "deriva del modelo de azar de muestreo a temperatura 0,3)"
            if bandera
            else "sin senal de inestabilidad entre la nueva corrida y la cache de H en los casos que H ya escalo (este control no "
            "separa deriva del modelo de azar de muestreo a temperatura 0,3)"
        ),
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
            f"no existe el cache del brazo 'Gemini solo' ({ruta_cache}): la corrida paga todavia no se hizo"
        )
    meta, gemini_solo, _ = leer_cache(ruta_cache)
    if meta is None:
        raise CorridaIncompletaError(f"el cache {ruta_cache.name} no tiene la linea de metadatos")
    for clave, ruta in (("corpus_hash_dentro", ruta_corpus_dentro), ("corpus_hash_fuera", ruta_corpus_fuera)):
        if meta.get(clave) != _compute_corpus_hash(pathlib.Path(ruta)):
            raise CorridaIncompletaError(
                f"{clave} del cache ({meta.get(clave)}) difiere del corpus vigente {pathlib.Path(ruta).name}"
            )
    precios = meta["precios_usd_por_millon"]
    bloques = {}
    for bloque, ruta_corpus, ruta_h in (
        (BLOQUE_DENTRO, ruta_corpus_dentro, ruta_hibrido_dentro),
        (BLOQUE_FUERA, ruta_corpus_fuera, ruta_hibrido_fuera),
    ):
        corpus = cargar_corpus_solo_lectura(ruta_corpus)
        hibrido = {p.caso_id: p for p in cargar_predicciones(pathlib.Path(ruta_h))}
        bloques[bloque] = _analizar_bloque(bloque, corpus, hibrido, gemini_solo, precios, remuestreos)
    deriva = _control_deriva(bloques)
    for b in bloques.values():
        b.pop("_deriva")
        b.pop("_escalados")
    entradas = {
        pathlib.Path(r).name: sha256(r)
        for r in (ruta_cache, ruta_corpus_dentro, ruta_corpus_fuera, ruta_hibrido_dentro, ruta_hibrido_fuera)
    }
    return {
        "change": "c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia",
        "generador": "evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py",
        "prerregistro": {
            "bloque_primario": BLOQUE_PRIMARIO,
            "margen_no_inferioridad": MARGEN_NO_INFERIORIDAD,
            "umbral_razon_eficiencia": UMBRAL_RAZON_EFICIENCIA,
            "tope_tasa_fallos": TOPE_TASA_FALLOS,
            "umbral_concordancia_deriva": UMBRAL_CONCORDANCIA_DERIVA,
            "semilla_bootstrap": SEMILLA_BOOTSTRAP,
            "remuestreos": remuestreos,
            "una_sola_corrida": True,
        },
        "procedencia": {
            clave: meta.get(clave)
            for clave in (
                "modelo", "temperatura", "top_p", "max_output_tokens", "max_reintentos", "sdk_version",
                "prompt_sha256", "commit", "generado_en", "tope_llamadas", "precios_usd_por_millon",
            )
        },
        "llamadas_totales_cache": sum(int(r["intentos"]) for r in gemini_solo.values()),
        "entradas_sha256": entradas,
        "bloques": bloques,
        "control_deriva": deriva,
        "veredicto": {
            "bloque": BLOQUE_PRIMARIO,
            **bloques[BLOQUE_PRIMARIO]["decision"],
            "bandera_deriva": deriva["bandera"],
        },
        "aditivo": {"reemplaza_numeros_canonicos": False, "declaracion": DECLARACION_ADITIVA},
    }


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
def _num(valor: Optional[float], decimales: int = 4) -> str:
    return "n/a" if valor is None else f"{valor:.{decimales}f}"


def _p(valor: Optional[float]) -> str:
    if valor is None:
        return "n/a"
    return f"{valor:.4f}" if valor >= 1e-4 else f"{valor:.3e}"


def _ic(ic: Optional[Sequence[float]], decimales: int = 4) -> str:
    return "n/a" if not ic else f"[{ic[0]:.{decimales}f}; {ic[1]:.{decimales}f}]"


ROTULO_BLOQUE = {
    BLOQUE_FUERA: "Fuera de muestra (primario, referencia consenso E3/E4)",
    BLOQUE_DENTRO: "Dentro de la muestra (secundario; optimista para H, no es prueba limpia)",
}


def _lineas_bloque(nombre: str, b: Mapping) -> List[str]:
    c, e, d = b["contraste"], b["eficiencia"], b["decision"]
    t, m, dif = c["tabla_2x2"], c["mcnemar"], c["diferencia_exactitud"]
    lineas = [
        "",
        f"## {ROTULO_BLOQUE[nombre]}",
        "",
        f"Casos: {b['n']}.",
        "",
        "| Brazo | Exactitud estricta (Wilson) | Exactitud laxa (Wilson) | Macro-F1 |",
        "|---|---|---|---|",
    ]
    for brazo, rotulo in (("H", "Hibrido (H)"), ("L", "Gemini solo (L)")):
        q = b["brazos"][brazo]
        es, ex = q["exactitud_estricta"], q["exactitud_laxa"]
        lineas.append(
            f"| {rotulo} | {es['aciertos']}/{es['n']} = {_num(es['valor'])} {_ic(es['ic95_wilson'])} | "
            f"{ex['aciertos']}/{ex['n']} = {_num(ex['valor'])} {_ic(ex['ic95_wilson'])} | {_num(q['macro_f1'])} |"
        )
    lineas += [
        "",
        "| | L acierta | L falla |",
        "|---|---|---|",
        f"| H acierta | {t['ambos_aciertan']} | {t['solo_hibrido']} |",
        f"| H falla | {t['solo_gemini_solo']} | {t['ninguno']} |",
        "",
        f"- McNemar exacta bilateral: p = {_p(m['p_exacto'])} (corregida por continuidad: "
        f"p = {_p(m['p_corregido'])}; criterio de stats.py: {m['criterio_stats']}). Una diferencia no "
        "significativa se lee «no se detecto diferencia», nunca «equivalentes».",
        f"- Diferencia de exactitudes (H - L): {_num(dif['valor'])}, IC 95 % bootstrap pareado "
        f"{_ic(dif['ic95'])} ({dif['remuestreos']} remuestreos, semilla {dif['semilla']}).",
        "",
        "### Eficiencia (H imputado con los tokens y la latencia de L en los casos que escalo)",
        "",
        f"- Llamadas: L = {e['llamadas']['L']} ({_num(e['llamadas']['por_caso_L'], 3)} por caso); "
        f"H = {e['llamadas']['H']} ({_num(e['llamadas']['por_caso_H'], 3)} por caso); razon H/L = "
        f"{_num(e['llamadas']['razon']['valor'])} {_ic(e['llamadas']['razon']['ic95'])}.",
        f"- Tokens: L = {e['tokens']['L']['entrada']} de entrada y {e['tokens']['L']['salida']} de salida; "
        f"H = {e['tokens']['H']['entrada']} y {e['tokens']['H']['salida']}. Casos con tokens supuestos "
        f"(la API no los devolvio): {e['tokens']['casos_con_tokens_supuestos']}.",
    ]
    for escenario, costo in e["costo_usd"].items():
        lineas.append(f"- Costo estimado ({escenario}): L = USD {costo['L']:.4f}; H = USD {costo['H']:.4f}.")
    lat = e["latencia_ms"]
    lineas += [
        f"- Razon de costo H/L: {_num(e['razon_costo']['valor'])} {_ic(e['razon_costo']['ic95'])} "
        f"({e['razon_costo']['nota']}).",
        f"- Latencia media por caso: L = {_num(lat['media_L'], 1)} ms; H = {_num(lat['media_H'], 1)} ms; "
        f"diferencia L - H = {_num(lat['diferencia_L_menos_H']['valor'], 1)} ms "
        f"{_ic(lat['diferencia_L_menos_H']['ic95'], 1)}. {lat['nota']}",
        f"- Casos que H escalo: {e['casos_escalados_h']}; fallbacks o errores de L: "
        f"{e['fallbacks_o_errores_l']} ({_num(e['tasa_fallos_l'], 3)}).",
        "",
        f"### Sensibilidad H* (hibrido recompuesto)",
        "",
        f"{b['sensibilidad_hstar']['definicion']}.",
        "",
        f"- Exactitud estricta de H*: {b['sensibilidad_hstar']['exactitud_estricta']['aciertos']}/"
        f"{b['n']}; diferencia H* - L = {_num(b['sensibilidad_hstar']['contraste']['diferencia_exactitud']['valor'])} "
        f"{_ic(b['sensibilidad_hstar']['contraste']['diferencia_exactitud']['ic95'])}; "
        f"McNemar p = {_p(b['sensibilidad_hstar']['contraste']['mcnemar']['p_exacto'])}; "
        f"regla aplicada a H*: {b['sensibilidad_hstar']['decision']['veredicto']} (no cambia el veredicto).",
        "",
        f"Regla prerregistrada aplicada a este bloque: exactitud {d['componente_exactitud']}, "
        f"eficiencia {d['componente_eficiencia']} -> **{d['veredicto']}**."
        + ("" if nombre == BLOQUE_PRIMARIO else " (informativo; solo decide el bloque primario)"),
    ]
    return lineas


def renderizar(doc: Mapping) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF."""
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    v, p, dv = doc["veredicto"], doc["procedencia"], doc["control_deriva"]
    lineas = [
        "# Brazo «Gemini solo» frente al hibrido: contraste de la hipotesis de eficiencia (c-215)",
        "",
        doc["aditivo"]["declaracion"],
        "",
        "## Veredicto prerregistrado (bloque primario: fuera de muestra)",
        "",
        f"**{v['veredicto']}**: {v['motivo']}.",
        "",
        f"- Margen de no inferioridad: {v['margen_no_inferioridad']}; ahorro material si el limite "
        f"superior del IC de las razones de costo y de llamadas es menor que {v['umbral_razon']}.",
        f"- Componente de exactitud: {v['componente_exactitud']}; componente de eficiencia: "
        f"{v['componente_eficiencia']}; tasa de fallos del brazo: {_num(v['tasa_fallos'], 3)}.",
        "",
        "## Control de deriva (casos que H ya escalo)",
        "",
        f"Concordancia pooled con la prediccion cacheada de H: {dv['total']['concordancia']['aciertos']}/"
        f"{dv['total']['n_escalados']} = {_num(dv['total']['concordancia']['valor'])} "
        f"{_ic(dv['total']['concordancia']['ic95_wilson'])} (umbral {dv['umbral']}). {dv['lectura']}.",
        "",
        "## Procedencia de la corrida",
        "",
        f"Modelo {p['modelo']}, temperatura {p['temperatura']}, google-genai {p['sdk_version']}, commit "
        f"{p['commit']}, generada el {p['generado_en']}; una sola corrida; llamadas acumuladas en el "
        f"cache: {doc['llamadas_totales_cache']} (tope {p['tope_llamadas']}). Precios (USD por millon "
        f"de tokens de entrada/salida, parametro declarado): {json.dumps(p['precios_usd_por_millon'])}.",
    ]
    for nombre in (BLOQUE_FUERA, BLOQUE_DENTRO):
        lineas += _lineas_bloque(nombre, doc["bloques"][nombre])
    return texto_json, "\n".join(lineas) + "\n"


def escribir(doc: Mapping, directorio: pathlib.Path) -> List[pathlib.Path]:
    """Escribe `.json`, `.md` y `SHA256SUMS` (UTF-8 sin BOM, LF)."""
    directorio = pathlib.Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for nombre, texto in ((NOMBRE_JSON, texto_json), (NOMBRE_MD, texto_md)):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(r)}  {r.name}\n" for r in rutas)
    ruta_sumas = directorio / NOMBRE_SUMAS
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=pathlib.Path, default=RUTA_CACHE_DEFECTO)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--corpus-dentro", type=pathlib.Path, default=RUTA_CORPUS_DENTRO)
    parser.add_argument("--corpus-fuera", type=pathlib.Path, default=RUTA_CORPUS_FUERA)
    parser.add_argument("--hibrido-dentro", type=pathlib.Path, default=RUTA_HIBRIDO_DENTRO)
    parser.add_argument("--hibrido-fuera", type=pathlib.Path, default=RUTA_HIBRIDO_FUERA)
    args = parser.parse_args(argv)
    try:
        doc = construir_documento(
            args.cache,
            ruta_corpus_dentro=args.corpus_dentro,
            ruta_corpus_fuera=args.corpus_fuera,
            ruta_hibrido_dentro=args.hibrido_dentro,
            ruta_hibrido_fuera=args.hibrido_fuera,
        )
    except CacheAusenteError as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 2
    except (CorridaIncompletaError, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for ruta in escribir(doc, args.salida):
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
