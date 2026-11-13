#!/usr/bin/env python3
"""Calibracion y punto de operacion del gate de confianza (c-214). PRERREGISTRO.

Este docstring congela las decisiones D2-D5 del `design.md` del change ANTES de generar
ninguna salida; el commit que lo introduce precede al de las salidas. Sin red, sin Gemini,
sin Docker. Determinista. No modifica configuracion productiva (CAL-005).

Declaracion de no ceguera
-------------------------
Para comprobar la factibilidad, quien propuso el change tabulo la distribucion de confianzas y
los aciertos por nivel en ambos corpus. Las reglas siguientes se fijan por principio (las
recomendaciones ya publicadas en la seccion 10 de la tesis), no por lo que esa tabulacion
sugiera, y se informan TODOS los resultados, favorables o no. El prerregistro NO fue ciego.

Insumos (solo lectura)
----------------------
- Dentro de la muestra: `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (200
  casos; referencia = `sector_asignado`, la original). Control: consenso E1/E2 sobre los 138
  casos de la planilla de la campana.
- Fuera de la muestra: `evaluation/data/campana/predicciones_independiente.json` (103 casos;
  referencia = `sector_asignado`, consenso E3/E4). Acierto = exactitud estricta.
- Secundarios NO ejecutados en esta aplicacion: (a) predicciones de un brazo Gemini solo (un
  change futuro, no propuesto todavia); (b) corpus arbitrado de c-206 (aun inexistente).

D2 - Metricas (por etapa y corpus)
----------------------------------
Etapas: Gemini (con su `confianza`) y determinista (con su `confianza` y con su
`score_correctitud` recomputado). Tabla de fiabilidad por valor observado (casos, aciertos,
exactitud, Wilson 95 %); ECE con 10 bandas de igual ancho en [0; 1] (la ultima cerrada);
Brier (media de (confianza - acierto)^2); sobreconfianza media (confianza media - exactitud);
AUROC de la senal para separar aciertos de errores (Mann-Whitney, empates a 0,5; `None` si
falta una de las dos clases). IC95 bootstrap percentil por caso con `SEMILLA_BOOTSTRAP` y
`REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py`.

D3 - Barrido de umbral (etapa Gemini)
-------------------------------------
Candidatos T = {0,70 (vigente); 0,86; 0,91; 0,96; 0,99; inf}; se acepta si confianza >= t;
inf = derivar todo lo escalado. Por t: cobertura (aceptados / escalados), exactitud selectiva
de los aceptados (Wilson), exactitud de los derivados, errores atrapados en los derivados y
carga de revision del sistema (derivados / casos del corpus).

D4 - Regla de seleccion (prerregistrada)
----------------------------------------
- Piso primario phi = 0,85; secundario phi' = 0,8278 (informado aparte).
- Seleccion en los 200: t* = el menor t en T excluido inf cuya exactitud selectiva de los
  aceptados sea >= phi con al menos 10 aceptados; si ninguno cumple, t* = ninguno.
- Evaluacion en los 103, sin reajuste: `no estimable` si hay menos de 10 aceptados o ningun
  derivado; `confirmado` si la exactitud selectiva es >= phi y la de los derivados es menor
  que la de los aceptados; `no confirmado` en los demas casos.
- Si t* = ninguno: el resultado es que la senal no sostiene un umbral con el piso fijado;
  fuera de la muestra el barrido y el AUROC se informan solo como descripcion.
- Recalibracion isotonica (ajustada en los 200) solo como correccion de nivel (ECE y Brier
  fuera de muestra); no cambia el orden ni la curva riesgo-cobertura.
- Prohibido elegir umbrales con los datos fuera de la muestra; toda lectura adicional se
  rotula exploratoria.

D5 - Senales alternativas (costo cero), misma regla
---------------------------------------------------
- S1, acuerdo entre etapas: en los casos escalados, el sector que habrian dado las reglas
  (ganador unico, aun por debajo de tau = 0,5166) frente al de Gemini: acuerdo / desacuerdo /
  sin prediccion de las reglas (sin senal o empate). Politica: aceptar si hay acuerdo, derivar
  si no. Candidato unico t = 1,0 sobre la senal binaria (acuerdo = 1, resto = 0).
- S2, `score_correctitud` de las reglas en los casos escalados: candidatos {0,0 (sin derivar);
  cuantiles 0,25; 0,50; 0,75 del score en los escalados de los 200 (rango por posicion,
  `sorted[ceil(q * n) - 1]`); inf}; se acepta si score >= t.
- Seleccion en los 200 y evaluacion en los 103 con las mismas condiciones de D4.
- El recomputo de las reglas debe reproducir exactamente la etapa y el sector de los casos
  cortocircuitados de las caches (131/131 y 69/69); si no, se detiene y se informa la deriva.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import pathlib
import sys

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.calibracion_gate import (  # noqa: E402
    ACUERDO,
    ENTORNO_OFFLINE_C214,
    NO_APLICA,
    ajustar_isotonica,
    aplicar_isotonica,
    asegurar_backend_en_path,
    auroc,
    barrido_umbral,
    brier,
    cargar_clasificador_deterministico,
    ece,
    evaluar_fuera_de_muestra_gate,
    ic_bootstrap_metrica,
    recomputar_senales_reglas,
    seleccionar_umbral,
    sobreconfianza,
    verificar_reproduccion_cortocircuito,
)
from evaluation.campana import (  # noqa: E402
    REFERENCIA_CONSENSO_NUEVO,
    construir_referencia,
)
from evaluation.metrics import intervalo_wilson  # noqa: E402

CAMPANA = ROOT / "evaluation/data/campana"
SALIDA = pathlib.Path(__file__).resolve().parent
NOMBRE_BASE = "analisis_calibracion_gate_c214"
RUTA_PRED_DENTRO = ROOT / "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"
RUTA_PRED_FUERA = CAMPANA / "predicciones_independiente.json"
RUTA_PLANILLA = CAMPANA / "plantilla_etiquetado.csv"
RUTA_SENALES = CAMPANA / "senales_reglas_c214.csv"
ENTRADAS = (RUTA_PRED_DENTRO, RUTA_PRED_FUERA, RUTA_PLANILLA, RUTA_SENALES)

INF = math.inf
UMBRALES_GEMINI = [0.70, 0.86, 0.91, 0.96, 0.99, INF]
UMBRALES_S1 = [0.0, 1.0, INF]
PISOS = {"piso_0.85": 0.85, "piso_0.8278": 0.8278}
MIN_ACEPTADOS = 10
CUANTILES_S2 = (0.25, 0.50, 0.75)
COLUMNAS_SENALES = ("caso_id", "corpus", "score_correctitud", "sector_reglas", "acuerdo_con_gemini")
CORPUS_DENTRO = "dentro_muestra"
CORPUS_FUERA = "fuera_muestra"


def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Bloques por senal
# ---------------------------------------------------------------------------
def distribucion_valores(senales) -> dict[str, int]:
    """Cantidad de casos por valor observado de la senal (claves en texto, orden creciente)."""
    conteo: dict[float, int] = {}
    for s in senales:
        conteo[s] = conteo.get(s, 0) + 1
    return {repr(v): conteo[v] for v in sorted(conteo)}


def bloque_senal(senales, aciertos) -> dict:
    """Fiabilidad por valor, ECE, Brier, sobreconfianza y AUROC (con IC95 bootstrap)."""
    n = len(senales)
    ok = sum(1 for a in aciertos if a)
    fiabilidad = []
    for valor in sorted(set(senales)):
        k = sum(1 for s in senales if s == valor)
        h = sum(1 for s, a in zip(senales, aciertos) if s == valor and a)
        fiabilidad.append(
            {
                "valor": valor,
                "casos": k,
                "aciertos": h,
                "exactitud": h / k,
                "ic_wilson": list(intervalo_wilson(h, k)),
            }
        )
    return {
        "n": n,
        "aciertos": ok,
        "exactitud": ok / n,
        "ic_wilson": list(intervalo_wilson(ok, n)),
        "confianza_media": sum(senales) / n,
        "fiabilidad": fiabilidad,
        "ece": ic_bootstrap_metrica(senales, aciertos, ece),
        "brier": ic_bootstrap_metrica(senales, aciertos, brier),
        "sobreconfianza": ic_bootstrap_metrica(senales, aciertos, sobreconfianza),
        "auroc": ic_bootstrap_metrica(senales, aciertos, auroc),
    }


def umbrales_s2(scores_escalados) -> list[float]:
    """Candidatos de S2: sin derivar (0,0), cuantiles por rango de posicion y derivar todo."""
    ordenados = sorted(scores_escalados)
    n = len(ordenados)
    cortes = [ordenados[math.ceil(q * n) - 1] for q in CUANTILES_S2]
    return [0.0, *cortes, INF]


# ---------------------------------------------------------------------------
# Politica: seleccion dentro de la muestra, evaluacion fuera (D4)
# ---------------------------------------------------------------------------
def evaluar_politica(dentro, fuera, umbrales, *, piso: float, n_total) -> dict:
    """`dentro`/`fuera` son `(senales, aciertos)` de los casos escalados de cada corpus.

    El umbral se elige SOLO con `dentro`; `fuera` se evalua sin reajuste. El barrido fuera de la
    muestra se adjunta como descripcion, nunca para elegir.
    """
    senales_d, aciertos_d = dentro
    senales_f, aciertos_f = fuera
    barrido_d = barrido_umbral(senales_d, aciertos_d, umbrales, n_total_corpus=n_total[0])
    elegido = seleccionar_umbral(barrido_d, piso=piso, min_aceptados=MIN_ACEPTADOS)
    evaluacion = evaluar_fuera_de_muestra_gate(
        elegido,
        senales_f,
        aciertos_f,
        piso=piso,
        n_total_corpus=n_total[1],
        min_aceptados=MIN_ACEPTADOS,
    )
    if elegido is None:
        lectura = (
            "la senal no sostiene un umbral con el piso fijado: ningun candidato alcanza "
            f"{piso} con al menos {MIN_ACEPTADOS} aceptados dentro de la muestra; fuera de la "
            "muestra el barrido se informa solo como descripcion"
        )
    else:
        lectura = (
            f"umbral elegido dentro de la muestra: {elegido!r}; "
            f"fuera de la muestra: {evaluacion['veredicto']}"
        )
    return {
        "piso": piso,
        "min_aceptados": MIN_ACEPTADOS,
        "umbral_seleccionado": elegido,
        "barrido_dentro": barrido_d,
        "fuera_de_muestra": evaluacion,
        "barrido_fuera_descriptivo": barrido_umbral(
            senales_f, aciertos_f, umbrales, n_total_corpus=n_total[1]
        ),
        "lectura": lectura,
    }


# ---------------------------------------------------------------------------
# Senales de las reglas: recomputo offline y archivo versionado
# ---------------------------------------------------------------------------
def _cargar_predicciones(ruta: pathlib.Path) -> list[dict]:
    return json.loads(ruta.read_text(encoding="utf-8"))["predictions"]


def generar_senales_csv(destino: pathlib.Path = RUTA_SENALES) -> dict:
    """Recomputa con el `DeterministicClassifier` real, verifica contra las caches y persiste.

    Se detiene (`ValueError`) si el recomputo no reproduce la etapa y el sector de los casos
    cortocircuitados. Escribe UTF-8 sin BOM con LF.
    """
    for clave, valor in ENTORNO_OFFLINE_C214.items():
        os.environ.setdefault(clave, valor)
    asegurar_backend_en_path()
    from app.config.settings import get_settings  # type: ignore

    get_settings.cache_clear()
    tau = get_settings().deterministic_score_threshold
    clasificador = cargar_clasificador_deterministico()
    filas: list[dict] = []
    resumen: dict = {}
    for corpus, ruta in ((CORPUS_DENTRO, RUTA_PRED_DENTRO), (CORPUS_FUERA, RUTA_PRED_FUERA)):
        predicciones = _cargar_predicciones(ruta)
        senales = recomputar_senales_reglas(predicciones, clasificador, tau=tau)
        resumen[corpus] = verificar_reproduccion_cortocircuito(senales, predicciones)
        filas += [{**s, "corpus": corpus} for s in senales]
    with destino.open("w", encoding="utf-8", newline="\n") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(COLUMNAS_SENALES)
        for f in filas:
            escritor.writerow(
                [
                    f["caso_id"],
                    f["corpus"],
                    repr(f["score_correctitud"]),
                    f["sector_reglas"] or "",
                    f["acuerdo_con_gemini"],
                ]
            )
    return resumen


def leer_senales_csv(ruta: pathlib.Path = RUTA_SENALES) -> dict[str, dict[str, dict]]:
    """`{corpus: {caso_id: senales}}` leido del archivo versionado (sin backend)."""
    salida: dict[str, dict[str, dict]] = {CORPUS_DENTRO: {}, CORPUS_FUERA: {}}
    with ruta.open(newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            salida[fila["corpus"]][fila["caso_id"]] = {
                "caso_id": fila["caso_id"],
                "score_correctitud": float(fila["score_correctitud"]),
                "sector_reglas": fila["sector_reglas"] or None,
                "acuerdo_con_gemini": fila["acuerdo_con_gemini"],
                "cortocircuita": fila["acuerdo_con_gemini"] == NO_APLICA,
            }
    return salida


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def _acierto(p: dict, referencia: dict[str, str] | None = None) -> bool:
    real = p["sector_asignado"] if referencia is None else referencia[p["caso_id"]]
    return p["sector_predicho"] == real


def _bloque_corpus(predicciones: list[dict], senales: dict[str, dict], referencia=None) -> dict:
    """Metricas por etapa y distribucion de confianza para un corpus (con su referencia)."""
    gem = [p for p in predicciones if p["etapa"] == "gemini"]
    det = [p for p in predicciones if p["etapa"] == "deterministic"]
    conf_gem = [p["confianza"] for p in gem]
    ac_gem = [_acierto(p, referencia) for p in gem]
    ac_det = [_acierto(p, referencia) for p in det]
    return {
        "n": len(predicciones),
        "escalados_a_gemini": len(gem),
        "cortocircuitados": len(det),
        "etapas": {
            "gemini": {"confianza": bloque_senal(conf_gem, ac_gem)},
            "deterministic": {
                "confianza": bloque_senal([p["confianza"] for p in det], ac_det),
                "score_correctitud": bloque_senal(
                    [senales[p["caso_id"]]["score_correctitud"] for p in det], ac_det
                ),
            },
        },
        "distribucion_confianza_gemini": distribucion_valores(conf_gem),
        "barrido_gemini": barrido_umbral(
            conf_gem, ac_gem, UMBRALES_GEMINI, n_total_corpus=len(predicciones)
        ),
    }


def _escalados(predicciones: list[dict], senales: dict[str, dict]) -> dict:
    """Por caso escalado: confianza de Gemini, acuerdo binario y score de las reglas."""
    gem = [p for p in predicciones if p["etapa"] == "gemini"]
    aciertos = [_acierto(p) for p in gem]
    return {
        "confianza": ([p["confianza"] for p in gem], aciertos),
        "s1": (
            [1.0 if senales[p["caso_id"]]["acuerdo_con_gemini"] == ACUERDO else 0.0 for p in gem],
            aciertos,
        ),
        "s2": ([senales[p["caso_id"]]["score_correctitud"] for p in gem], aciertos),
        "acuerdo": [senales[p["caso_id"]]["acuerdo_con_gemini"] for p in gem],
    }


def _categorias_s1(escalados: dict) -> dict:
    out: dict[str, dict] = {}
    for categoria in sorted(set(escalados["acuerdo"])):
        aciertos = [a for c, a in zip(escalados["acuerdo"], escalados["s1"][1]) if c == categoria]
        out[categoria] = {
            "casos": len(aciertos),
            "aciertos_gemini": sum(aciertos),
            "exactitud_gemini": sum(aciertos) / len(aciertos),
        }
    return out


def _isotonica(dentro, fuera) -> dict:
    modelo = ajustar_isotonica(*dentro)
    recal = aplicar_isotonica(modelo, fuera[0])
    return {
        "ajuste": "regresion isotonica (PAVA) de aciertos sobre la confianza de Gemini, 200 casos",
        "puntos": [[x, v] for x, v in modelo],
        "fuera_de_muestra": {
            "n": len(fuera[0]),
            "ece_original": ece(*fuera),
            "ece_recalibrada": ece(recal, fuera[1]),
            "brier_original": brier(*fuera),
            "brier_recalibrada": brier(recal, fuera[1]),
            "auroc_original": auroc(*fuera),
            "auroc_recalibrada": auroc(recal, fuera[1]),
        },
        "nota": (
            "correccion de nivel solamente: la transformacion es monotona no decreciente y no "
            "invierte el orden; si agrupa niveles vecinos introduce empates y el AUROC puede cambiar"
        ),
    }


def _gobernanza(politicas: dict) -> dict:
    confirmadas = [
        f"{nombre} ({clave}, umbral {r['umbral_seleccionado']!r})"
        for nombre, por_piso in politicas.items()
        for clave, r in por_piso.items()
        if r["fuera_de_muestra"]["veredicto"] == "confirmado"
    ]
    if confirmadas:
        recomendacion = (
            "candidatas a un change posterior de gobernanza HIGH, con su limite de n chico: "
            + "; ".join(confirmadas)
        )
    else:
        recomendacion = (
            "ninguna politica quedo confirmada fuera de la muestra: la derivacion por confianza "
            "autodeclarada no es reparable por recalibracion en este corpus; la supervision debe "
            "apoyarse en otra senal o en muestreo"
        )
    return {
        "cambia_configuracion": False,
        "politicas_confirmadas_fuera_de_muestra": confirmadas,
        "recomendacion": recomendacion,
        "alcance": (
            "el change informa; openspec/config.yaml, settings.py, el prompt y el clasificador "
            "no se modifican"
        ),
    }


def construir_documento() -> dict:
    """Calcula todos los bloques desde las caches y el CSV de senales (sin backend ni red)."""
    senales = leer_senales_csv()
    pred_d = _cargar_predicciones(RUTA_PRED_DENTRO)
    pred_f = _cargar_predicciones(RUTA_PRED_FUERA)
    reproduccion = {
        corpus: verificar_reproduccion_cortocircuito(
            [senales[corpus][p["caso_id"]] for p in preds], preds
        )
        for corpus, preds in ((CORPUS_DENTRO, pred_d), (CORPUS_FUERA, pred_f))
    }
    with RUTA_PLANILLA.open(newline="", encoding="utf-8") as archivo:
        planilla = list(csv.DictReader(archivo))
    consenso = {
        caso: datos.sector
        for caso, datos in construir_referencia(
            REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla
        ).casos.items()
    }
    pred_control = [p for p in pred_d if p["caso_id"] in consenso]

    corpora = {
        CORPUS_DENTRO: {
            "referencia": "etiquetado original del corpus (sector_asignado)",
            **_bloque_corpus(pred_d, senales[CORPUS_DENTRO]),
        },
        CORPUS_FUERA: {
            "referencia": "consenso de E3 y E4 (sector_asignado de la cache independiente)",
            **_bloque_corpus(pred_f, senales[CORPUS_FUERA]),
        },
        "control_consenso_e1_e2": {
            "referencia": "consenso de E1 y E2 (138 casos; discordantes excluidos)",
            **_bloque_corpus(pred_control, senales[CORPUS_DENTRO], consenso),
        },
    }

    esc_d = _escalados(pred_d, senales[CORPUS_DENTRO])
    esc_f = _escalados(pred_f, senales[CORPUS_FUERA])
    n_total = (len(pred_d), len(pred_f))
    umbrales_s2_fijados = umbrales_s2(esc_d["s2"][0])
    definiciones = {
        "confianza_gemini": ("confianza", UMBRALES_GEMINI),
        "s1_acuerdo_entre_etapas": ("s1", UMBRALES_S1),
        "s2_score_reglas": ("s2", umbrales_s2_fijados),
    }
    politicas: dict = {}
    for nombre, (clave, umbrales) in definiciones.items():
        auroc_dentro = ic_bootstrap_metrica(*esc_d[clave], auroc)
        auroc_fuera = ic_bootstrap_metrica(*esc_f[clave], auroc)
        politicas[nombre] = {
            etiqueta: {
                **evaluar_politica(
                    esc_d[clave], esc_f[clave], umbrales, piso=piso, n_total=n_total
                ),
                "auroc_dentro": auroc_dentro,
                "auroc_fuera": auroc_fuera,
            }
            for etiqueta, piso in PISOS.items()
        }
    return {
        "change": "c-214-calibracion-y-punto-de-operacion-del-gate-de-confianza",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "solo lectura; evaluation.calibracion_gate + evaluation.metrics; sin red ni Gemini; "
            "deterministico; regla de seleccion prerregistrada en el docstring del generador"
        ),
        "no_ceguera": "el prerregistro NO fue ciego (ver docstring del generador)",
        "entradas_sha256": {r.relative_to(ROOT).as_posix(): sha256(r) for r in ENTRADAS},
        "parametros": {
            "umbrales_gemini": UMBRALES_GEMINI,
            "umbrales_s1": UMBRALES_S1,
            "umbrales_s2_fijados_en_los_200": umbrales_s2_fijados,
            "pisos": PISOS,
            "min_aceptados": MIN_ACEPTADOS,
            "bandas_ece": 10,
        },
        "reproduccion_reglas": reproduccion,
        "corpora": corpora,
        "s1_categorias": {
            CORPUS_DENTRO: _categorias_s1(esc_d),
            CORPUS_FUERA: _categorias_s1(esc_f),
        },
        "politicas": politicas,
        "isotonica": _isotonica(esc_d["confianza"], esc_f["confianza"]),
        "secundarios": {
            "brazo_gemini_solo": (
                "no ejecutado: requiere las predicciones de un brazo Gemini solo "
                "(change futuro, no propuesto todavia)"
            ),
            "corpus_arbitrado_c206": "no ejecutado: el corpus arbitrado de c-206 todavia no existe",
        },
        "gobernanza": _gobernanza(politicas),
    }


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------
def a_json_seguro(obj):
    """Reemplaza `inf` por el texto `"inf"` (JSON estricto)."""
    if isinstance(obj, float) and math.isinf(obj):
        return "inf" if obj > 0 else "-inf"
    if isinstance(obj, dict):
        return {k: a_json_seguro(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [a_json_seguro(v) for v in obj]
    return obj


def _p(v, d: int = 4) -> str:
    return "n/d" if v is None else f"{v:.{d}f}"


def _ic(par, d: int = 4) -> str:
    return "n/d" if not par else f"[{_p(par[0], d)}; {_p(par[1], d)}]"


def _m(b: dict) -> str:
    return f"{_p(b['valor'])} IC95 {_ic(b['ic'])}"


def _md_barrido(barrido: list[dict]) -> str:
    filas = [
        "| Umbral t | Aceptados | Derivados | Cobertura | Exactitud selectiva (Wilson) | "
        "Exactitud derivados | Errores atrapados | Carga de revision |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for f in barrido:
        umbral = "inf" if f["umbral"] == INF else _p(f["umbral"])
        wilson = _ic(f["ic_wilson"], 3) if f["ic_wilson"] else ""
        filas.append(
            f"| {umbral} | {f['aceptados']} | {f['derivados']} | {_p(f['cobertura'], 3)} | "
            f"{_p(f['exactitud_selectiva'], 3)} {wilson} | {_p(f['exactitud_derivados'], 3)} | "
            f"{f['errores_atrapados']} | {_p(f['carga_revision'], 3)} |"
        )
    return "\n".join(filas)


def _md_corpus(nombre: str, c: dict) -> list[str]:
    lineas = [
        f"### {nombre}",
        "",
        f"- Referencia: {c['referencia']}; n = {c['n']}; escalados a Gemini = "
        f"{c['escalados_a_gemini']}; cortocircuitados = {c['cortocircuitados']}",
    ]
    for etapa, senal, b in (
        ("Gemini", "confianza", c["etapas"]["gemini"]["confianza"]),
        ("Determinista", "confianza", c["etapas"]["deterministic"]["confianza"]),
        ("Determinista", "score_correctitud", c["etapas"]["deterministic"]["score_correctitud"]),
    ):
        lineas += [
            "",
            f"**{etapa} ({senal})**: n = {b['n']}, exactitud = {_p(b['exactitud'])} "
            f"IC Wilson {_ic(b['ic_wilson'])}, senal media = {_p(b['confianza_media'])}",
            f"- ECE = {_m(b['ece'])}; Brier = {_m(b['brier'])}",
            f"- Sobreconfianza = {_m(b['sobreconfianza'])}; AUROC = {_m(b['auroc'])}",
        ]
    distribucion = ", ".join(f"{k}: {v}" for k, v in c["distribucion_confianza_gemini"].items())
    lineas += [
        "",
        f"Distribucion de la confianza de Gemini: {distribucion}",
        "",
        "| Valor (Gemini) | Casos | Aciertos | Exactitud | IC Wilson |",
        "|---|---|---|---|---|",
    ]
    for f in c["etapas"]["gemini"]["confianza"]["fiabilidad"]:
        lineas.append(
            f"| {_p(f['valor'], 2)} | {f['casos']} | {f['aciertos']} | "
            f"{_p(f['exactitud'])} | {_ic(f['ic_wilson'])} |"
        )
    lineas += ["", _md_barrido(c["barrido_gemini"]), ""]
    return lineas


def renderizar(doc: dict) -> tuple[str, str]:
    """`(json, markdown)` en texto con LF y sin BOM."""
    texto_json = (
        json.dumps(a_json_seguro(doc), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    lineas = [
        "# Calibracion y punto de operacion del gate de confianza (c-214)",
        "",
        "Solo lectura; reglas de seleccion prerregistradas en el docstring del generador. "
        "El prerregistro NO fue ciego. Sin red, sin Gemini. No modifica configuracion productiva.",
        "",
        "## Reproduccion del recomputo de las reglas",
        "",
    ]
    for corpus, r in doc["reproduccion_reglas"].items():
        lineas.append(
            f"- {corpus}: {r['cortocircuitados']} cortocircuitados reproducidos de {r['total']} casos"
        )
    lineas += ["", "## Calibracion y discriminacion por etapa", ""]
    for nombre, c in doc["corpora"].items():
        lineas += _md_corpus(nombre, c)
    lineas += ["## Politicas de derivacion (seleccion dentro, evaluacion fuera de la muestra)", ""]
    for nombre, por_piso in doc["politicas"].items():
        for etiqueta, r in por_piso.items():
            elegido = r["umbral_seleccionado"]
            lineas += [
                f"### {nombre} / {etiqueta} (piso {r['piso']})",
                "",
                "- Umbral seleccionado dentro de la muestra: "
                + ("ninguno" if elegido is None else _p(elegido)),
                f"- Veredicto fuera de la muestra: {r['fuera_de_muestra']['veredicto']}",
                f"- AUROC dentro = {_m(r['auroc_dentro'])}; fuera = {_m(r['auroc_fuera'])}",
                f"- {r['lectura']}",
                "",
                "Barrido dentro de la muestra:",
                "",
                _md_barrido(r["barrido_dentro"]),
                "",
                "Barrido fuera de la muestra (descriptivo; no se elige con el):",
                "",
                _md_barrido(r["barrido_fuera_descriptivo"]),
                "",
            ]
    lineas += ["## S1: Gemini por categoria de acuerdo con las reglas", ""]
    for corpus, cats in doc["s1_categorias"].items():
        for cat, v in cats.items():
            lineas.append(
                f"- {corpus} / {cat}: {v['casos']} casos, {v['aciertos_gemini']} aciertos "
                f"({_p(v['exactitud_gemini'])})"
            )
    iso = doc["isotonica"]["fuera_de_muestra"]
    lineas += [
        "",
        "## Recalibracion isotonica (solo nivel)",
        "",
        f"- ECE fuera de la muestra: {_p(iso['ece_original'])} -> {_p(iso['ece_recalibrada'])}; "
        f"Brier: {_p(iso['brier_original'])} -> {_p(iso['brier_recalibrada'])}; "
        f"AUROC: {_p(iso['auroc_original'])} -> {_p(iso['auroc_recalibrada'])}",
        f"- {doc['isotonica']['nota']}",
        "",
        "## Secundarios",
        "",
    ]
    lineas += [f"- {k}: {v}" for k, v in doc["secundarios"].items()]
    g = doc["gobernanza"]
    lineas += [
        "",
        "## Gobernanza",
        "",
        f"- cambia_configuracion: {str(g['cambia_configuracion']).lower()}",
        f"- {g['recomendacion']}",
        f"- {g['alcance']}",
        "",
        "## Entradas (SHA-256)",
        "",
    ]
    lineas += [f"- `{r}`: `{h}`" for r, h in doc["entradas_sha256"].items()]
    return texto_json, "\n".join(lineas) + "\n"


def escribir(doc: dict, directorio: pathlib.Path) -> list[pathlib.Path]:
    """Escribe `.json` y `.md` (UTF-8 sin BOM, LF) y devuelve las rutas."""
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for extension, texto in (("json", texto_json), ("md", texto_md)):
        ruta = directorio / f"{NOMBRE_BASE}.{extension}"
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    return rutas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument(
        "--recomputar-senales",
        action="store_true",
        help="recomputa y reescribe senales_reglas_c214.csv con el backend (offline)",
    )
    args = parser.parse_args(argv)
    if args.recomputar_senales:
        print(json.dumps(generar_senales_csv(), indent=2))
        print(f"{sha256(RUTA_SENALES)}  {RUTA_SENALES.name}")
    for ruta in escribir(construir_documento(), args.salida):
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
