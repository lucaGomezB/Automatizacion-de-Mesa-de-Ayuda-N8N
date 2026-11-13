#!/usr/bin/env python3
"""Analisis ampliado de solo lectura de la validacion fuera de muestra (c-205).

Completa el bloque de c-191 con, sobre el n efectivo (103 casos con consenso `E3`/`E4`):

- macro-F1 de las cinco clases y, por clase, precision, sensibilidad, F1 y soporte;
- *balanced accuracy* (media de las sensibilidades por clase);
- kappa de Cohen del clasificador contra la referencia (concordancia clasificador-referencia,
  NO fiabilidad inter-etiquetador);
- matriz de confusion 5x5 (filas = referencia, columnas = prediccion);
- precision alcanzada (semi-ancho del IC de Wilson) frente al objetivo de diseno D1 de c-191
  y el efecto minimo detectable declarado;
- sensibilidad al sesgo de exclusion de los 47 discordantes (peor caso, mejor caso, cota y
  regla de decision explicita; analisis de SENSIBILIDAD, no medicion);
- extension del balance neto de derivaciones erroneas (Seccion 3.11 del memo) con la tasa de
  error estricta fuera de muestra, insumos `condicional`.

Reutiliza `evaluation.metrics`, `evaluation.kappa` y `evaluation.stats`: no reimplementa el
clasificador ni las metricas. Solo lectura sobre los artefactos versionados de c-191, sin red
y sin Gemini. Determinista.

Salidas (mismo directorio, LF, UTF-8 sin BOM): `analisis_fuera_de_muestra_c205.json` y
`analisis_fuera_de_muestra_c205.md`. Imprime el SHA-256 de cada una.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import cargar_corpus_solo_lectura  # noqa: E402
from evaluation.corpus import SECTORES_CANONICOS  # noqa: E402
from evaluation.kappa import kappa_cohen  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    f1_macro,
    f1_por_clase,
    intervalo_wilson,
    matriz_confusion,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402
from evaluation.stats import efecto_minimo_detectable  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent
NOMBRE_BASE = "analisis_fuera_de_muestra_c205"

RUTA_PRED_OOS = ROOT / "evaluation/data/campana/predicciones_independiente.json"
RUTA_CORPUS_OOS = ROOT / "evaluation/data/campana/corpus_independiente.json"
RUTA_PRIMARIA = ROOT / "evaluation/data/campana/doble_etiquetado_independiente.csv"

# Umbral de exactitud de la tesis y objetivo de diseno D1 de c-191 (semi-ancho ~8,4 pts).
UMBRAL_EXACTITUD = 0.85
OBJETIVO_SEMI_ANCHO_D1 = 0.084
# Supuestos declarados del efecto minimo detectable.
ALFA_MDE = 0.05
POTENCIA_MDE = 0.80
# Insumos del balance neto (Seccion 3.11 del memo canonico; todos `condicional` aqui).
DELTA_T_S = Decimal("43.82")  # ahorro medio por incidente (Seccion 3.1)
N_TRIMESTRAL = Decimal("2646")  # universo trimestral (Seccion 3.4)
E_MAN_GRILLA = ("0.10", "0.15", "0.20", "0.265")
COSTO_MIN_GRILLA = (5, 10, 15)


def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def semi_ancho_wilson(aciertos: int, n: int) -> float:
    """Semi-ancho `(superior - inferior) / 2` del IC de Wilson 95 % de `aciertos/n`."""
    inferior, superior = intervalo_wilson(aciertos, n)
    return float((superior - inferior) / 2)


def metricas_clasificacion(reales: list[str], predichos: list[str]) -> dict:
    """Macro-F1, metricas por clase, balanced accuracy y matriz, desde `evaluation.metrics`."""
    matriz = matriz_confusion(reales, predichos)
    precision = precision_por_clase(matriz)
    sensibilidad = sensibilidad_por_clase(matriz)
    f1 = f1_por_clase(matriz)
    soporte = soporte_por_clase(matriz)
    por_clase = {
        sector: {
            "precision": precision[sector],
            "sensibilidad": sensibilidad[sector],
            "f1": f1[sector],
            "soporte": soporte[sector],
        }
        for sector in SECTORES_CANONICOS
    }
    aciertos = sum(matriz[sector][sector] for sector in SECTORES_CANONICOS)
    exactitud = aciertos / len(reales)
    balanced = sum(sensibilidad[sector] for sector in SECTORES_CANONICOS) / len(SECTORES_CANONICOS)
    return {
        "macro_f1": f1_macro(f1),
        "por_clase": por_clase,
        "balanced_accuracy": {
            "valor": balanced,
            "exactitud_estricta": exactitud,
            "diferencia_con_estricta": balanced - exactitud,
            "definicion": "media aritmetica de las sensibilidades por clase",
        },
        "matriz_confusion": {
            "filas": "sector de referencia (sector_asignado)",
            "columnas": "sector predicho principal",
            "orden": list(SECTORES_CANONICOS),
            "celdas": matriz,
        },
        "aciertos": aciertos,
        "n": len(reales),
    }


def escenarios_exclusion(
    aciertos: int, n_efectivo: int, excluidos: int, umbral: float = UMBRAL_EXACTITUD
) -> dict:
    """Sensibilidad al sesgo de excluir los discordantes (NO es una medicion).

    Universo = n_efectivo + excluidos. Peor caso: todos los excluidos fallan. Mejor caso:
    todos aciertan. Cota: los excluidos aciertan a la tasa del limite inferior del IC de
    Wilson del n efectivo. Se agrega el minimo de aciertos entre los excluidos para alcanzar
    el umbral sobre el universo completo.
    """
    universo = n_efectivo + excluidos
    inferior = float(intervalo_wilson(aciertos, n_efectivo)[0])
    aciertos_cota = aciertos + excluidos * inferior
    minimo = max(math.ceil(umbral * universo - aciertos - 1e-9), 0)
    peor = aciertos / universo
    sostiene = peor >= umbral
    if sostiene:
        veredicto = "El peor caso lo alcanza: el resultado sostiene el umbral."
    else:
        veredicto = (
            f"El peor caso ({aciertos}/{universo} = {peor:.4f}) queda por debajo del umbral: "
            "la exactitud sobre el n efectivo NO puede presentarse como superacion del umbral "
            f"sin el arbitraje de los {excluidos} discordantes."
        )
    return {
        "rotulo": "analisis de sensibilidad; no es una medicion del clasificador sobre los excluidos",
        "universo": universo,
        "excluidos": excluidos,
        "umbral": umbral,
        "peor_caso": {"aciertos": aciertos, "n": universo, "exactitud": peor},
        "mejor_caso": {
            "aciertos": aciertos + excluidos,
            "n": universo,
            "exactitud": (aciertos + excluidos) / universo,
        },
        "cota": {
            "definicion": (
                "los excluidos aciertan a la tasa del limite inferior del IC de Wilson 95 % "
                "del n efectivo"
            ),
            "tasa_excluidos": inferior,
            "aciertos_esperados": aciertos_cota,
            "n": universo,
            "exactitud": aciertos_cota / universo,
        },
        "aciertos_minimos_excluidos_para_umbral": {
            "minimo": minimo,
            "de": excluidos,
            "tasa_requerida": minimo / excluidos if excluidos else None,
            "alcanzable": minimo <= excluidos,
        },
        "regla_decision": {
            "enunciado": (
                f"El umbral {umbral:.2f} se sostiene sin condiciones solo si el peor caso lo "
                f"alcanza. {veredicto}"
            ),
            "peor_caso_sostiene_umbral": sostiene,
            "umbral": umbral,
        },
    }


def _redondear(valor: Decimal, decimales: str = "0.1") -> str:
    return str(valor.quantize(Decimal(decimales), ROUND_HALF_UP))


def balance_neto(errores: int, n_efectivo: int) -> dict:
    """Balance neto de derivaciones erroneas (Seccion 3.11) con `e_aut` fuera de muestra."""
    e_aut = Decimal(errores) / Decimal(n_efectivo)
    ahorro_bruto_h = DELTA_T_S * N_TRIMESTRAL / 3600
    escenarios = []
    for e_man_txt in E_MAN_GRILLA:
        e_man = Decimal(e_man_txt)
        for costo_min in COSTO_MIN_GRILLA:
            c = Decimal(costo_min * 60)
            balance = ahorro_bruto_h - (e_aut - e_man) * N_TRIMESTRAL * c / 3600
            a_estrella = 1 - e_man - DELTA_T_S / c
            escenarios.append(
                {
                    "e_man": e_man_txt,
                    "costo_min": costo_min,
                    "balance_h": _redondear(balance),
                    "a_estrella_pct": _redondear(a_estrella * 100),
                }
            )
    return {
        "estado": "condicional",
        "e_aut_fuera_de_muestra": {
            "errores": errores,
            "n": n_efectivo,
            "valor": float(e_aut),
        },
        "formula": "B = (N / 3600) * [dt - (e_aut - e_man) * c]; a* = 1 - e_man - dt / c",
        "insumos": {
            "delta_t_s": str(DELTA_T_S),
            "n_trimestral": str(N_TRIMESTRAL),
            "ahorro_bruto_h": _redondear(ahorro_bruto_h),
            "procedencia": (
                "dt y N: Secciones 3.1 y 3.4 de numeros-canonicos.md; e_man y c: Seccion 3.11 "
                "(supuestos condicional)"
            ),
        },
        "escenarios": escenarios,
        "no_computable": [
            {
                "insumo": "ahorro de tiempo por incidente (dt) medido en el corpus independiente",
                "motivo": (
                    "los artefactos fuera de muestra (corpus_independiente.json, "
                    "predicciones_independiente.json, doble_etiquetado_independiente.csv) no "
                    "registran tiempos de resolucion; dt se toma como supuesto condicional del "
                    "in-sample"
                ),
            },
            {
                "insumo": "tasa de derivacion erronea manual (e_man) y costo por derivacion (c)",
                "motivo": (
                    "no se midieron en el corpus independiente; se mantienen las rejillas "
                    "condicional de la Seccion 3.11"
                ),
            },
        ],
    }


def _kappa_dict(resultado) -> dict:
    return {
        "rotulo": (
            "concordancia del clasificador contra la referencia humana (E3/E4); NO es "
            "fiabilidad inter-etiquetador"
        ),
        "n": resultado.n,
        "kappa": resultado.kappa,
        "p_o": resultado.p_o,
        "p_e": resultado.p_e,
        "pabak": resultado.pabak,
        "error_estandar": resultado.error_estandar,
        "ic_asintotico": list(resultado.ic_asintotico) if resultado.ic_asintotico else None,
        "ic_bootstrap": list(resultado.ic_bootstrap) if resultado.ic_bootstrap else None,
        "nivel_confianza": resultado.nivel_confianza,
        "semilla": resultado.semilla,
        "remuestreos": resultado.remuestreos,
        "rotulo_landis_koch": resultado.rotulo,
        "declaraciones": list(resultado.declaraciones),
    }


def _total_primaria() -> int:
    with RUTA_PRIMARIA.open(newline="", encoding="utf-8") as archivo:
        return len({fila["id_caso"] for fila in csv.DictReader(archivo)})


def _frontera(matriz: dict) -> dict:
    """Celda fuera de la diagonal mas poblada (global) y desglose de los errores de Sistemas."""
    fuera = [
        (matriz[real][pred], real, pred)
        for real in SECTORES_CANONICOS
        for pred in SECTORES_CANONICOS
        if real != pred
    ]
    maximo = max(fuera, key=lambda t: (t[0], t[1] == "Sistemas"))
    errores_sistemas = {
        pred: matriz["Sistemas"][pred] for pred in SECTORES_CANONICOS if pred != "Sistemas"
    }
    return {
        "mayor_celda_fuera_de_diagonal": {
            "casos": maximo[0],
            "referencia": maximo[1],
            "prediccion": maximo[2],
        },
        "errores_de_sistemas_por_prediccion": errores_sistemas,
        "sistemas_soporte": sum(matriz["Sistemas"].values()),
        "sistemas_aciertos": matriz["Sistemas"]["Sistemas"],
    }


def construir_documento() -> dict:
    predicciones = cargar_predicciones(RUTA_PRED_OOS)
    por_id = {caso.id: caso for caso in cargar_corpus_solo_lectura(RUTA_CORPUS_OOS)}
    reales = [p.sector_asignado for p in predicciones]
    predichos = [p.sector_predicho for p in predicciones]
    laxos = sum(1 for p in predicciones if p.sector_predicho in por_id[p.caso_id].conjunto_verdad)
    metricas = metricas_clasificacion(reales, predichos)
    n = metricas["n"]
    aciertos = metricas["aciertos"]
    total_primaria = _total_primaria()
    excluidos = total_primaria - n

    ic_estricta = intervalo_wilson(aciertos, n)
    ic_laxa = intervalo_wilson(laxos, n)
    semi_ancho = semi_ancho_wilson(aciertos, n)
    mde = efecto_minimo_detectable(n, alfa=ALFA_MDE, potencia=POTENCIA_MDE, bilateral=True)
    kappa = kappa_cohen(list(zip(reales, predichos)))

    return {
        "change": "c-205-ampliar-el-analisis-fuera-de-muestra",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "solo lectura; evaluation.metrics + evaluation.kappa + evaluation.stats; sin red "
            "ni Gemini; deterministico"
        ),
        "entradas_sha256": {
            "predicciones_independiente.json": sha256(RUTA_PRED_OOS),
            "corpus_independiente.json": sha256(RUTA_CORPUS_OOS),
            "doble_etiquetado_independiente.csv": sha256(RUTA_PRIMARIA),
        },
        "n_efectivo": n,
        "total_primaria": total_primaria,
        "excluidos": excluidos,
        "exactitud_estricta": {
            "aciertos": aciertos,
            "n": n,
            "valor": aciertos / n,
            "ic_wilson": [float(x) for x in ic_estricta],
        },
        "exactitud_laxa": {
            "aciertos": laxos,
            "n": n,
            "valor": laxos / n,
            "ic_wilson": [float(x) for x in ic_laxa],
        },
        "macro_f1": metricas["macro_f1"],
        "macro_f1_definicion": (
            "media aritmetica de las cinco F1 por clase, incluida toda clase de soporte cero "
            "(F1 = 0.0); NO es equivalente de la exactitud estricta de etiqueta unica"
        ),
        "por_clase": metricas["por_clase"],
        "balanced_accuracy": metricas["balanced_accuracy"],
        "kappa_clasificador": _kappa_dict(kappa),
        "matriz_confusion": metricas["matriz_confusion"],
        "frontera_confusion": _frontera(metricas["matriz_confusion"]["celdas"]),
        "potencia_precision": {
            "n": n,
            "semi_ancho_wilson_observado": semi_ancho,
            "objetivo_semi_ancho_d1": OBJETIVO_SEMI_ANCHO_D1,
            "cumple_objetivo_d1": semi_ancho <= OBJETIVO_SEMI_ANCHO_D1,
            "nota": (
                "precision alcanzada con el n efectivo, no tamano muestral elegido; el objetivo "
                "D1 de c-191 (~8,4 pts) fue aceptado, no un requisito"
            ),
            "efecto_minimo_detectable": {
                "d_z": float(mde),
                "alfa": ALFA_MDE,
                "potencia": POTENCIA_MDE,
                "bilateral": True,
                "nota": "MDE en escala d_z para un contraste pareado de n pares (evaluation.stats)",
            },
        },
        "sesgo_exclusion": escenarios_exclusion(aciertos, n, excluidos),
        "balance_neto": balance_neto(n - aciertos, n),
    }


def renderizar_md(doc: dict) -> str:
    def ic(par):
        return "n/a" if not par else f"[{par[0]:.4f}; {par[1]:.4f}]"

    est, lax = doc["exactitud_estricta"], doc["exactitud_laxa"]
    ba, kp = doc["balanced_accuracy"], doc["kappa_clasificador"]
    pp, sb = doc["potencia_precision"], doc["sesgo_exclusion"]
    bn = doc["balance_neto"]
    minimos = sb["aciertos_minimos_excluidos_para_umbral"]
    lineas = [
        "# Analisis ampliado fuera de muestra (c-205)",
        "",
        "Solo lectura; reutiliza `evaluation/metrics.py`, `evaluation/kappa.py` y "
        "`evaluation/stats.py`. Sin red, sin Gemini.",
        "",
        "## Resultado base (n efectivo)",
        "",
        f"- n efectivo: {doc['n_efectivo']}; excluidos: {doc['excluidos']} (de {doc['total_primaria']})",
        f"- Exactitud estricta: {est['aciertos']}/{est['n']} = {est['valor']:.4f} IC Wilson {ic(est['ic_wilson'])}",
        f"- Exactitud laxa: {lax['aciertos']}/{lax['n']} = {lax['valor']:.4f} IC Wilson {ic(lax['ic_wilson'])}",
        "",
        "## Macro-F1 y metricas por clase",
        "",
        f"- Macro-F1 (cinco clases): {doc['macro_f1']:.4f}. {doc['macro_f1_definicion']}.",
        "",
        "| Sector | Precision | Sensibilidad | F1 | Soporte |",
        "|---|---|---|---|---|",
    ]
    for sector in SECTORES_CANONICOS:
        d = doc["por_clase"][sector]
        lineas.append(
            f"| {sector} | {d['precision']:.4f} | {d['sensibilidad']:.4f} | {d['f1']:.4f} | {d['soporte']} |"
        )
    lineas += [
        "",
        f"- Balanced accuracy ({ba['definicion']}): {ba['valor']:.4f}; difiere de la exactitud "
        f"estricta ({ba['exactitud_estricta']:.4f}) en {ba['diferencia_con_estricta']:+.4f} por el "
        "desbalance de clases.",
        "",
        "## Kappa del clasificador contra la referencia",
        "",
        f"- {kp['rotulo']}",
        f"- kappa = {kp['kappa']:.4f}; p_o = {kp['p_o']:.4f}; p_e = {kp['p_e']:.4f}; "
        f"PABAK = {kp['pabak']:.4f}; n = {kp['n']}",
        f"- IC asintotico 95 %: {ic(kp['ic_asintotico'])}; IC bootstrap 95 % "
        f"(semilla {kp['semilla']}, {kp['remuestreos']} remuestreos): {ic(kp['ic_bootstrap'])}",
        f"- Rotulo de Landis y Koch: {kp['rotulo_landis_koch']}",
        "",
        "## Matriz de confusion 5x5 (filas = referencia, columnas = prediccion)",
        "",
        "| Referencia / Prediccion | " + " | ".join(SECTORES_CANONICOS) + " |",
        "|---|" + "---|" * len(SECTORES_CANONICOS),
    ]
    for real in SECTORES_CANONICOS:
        celdas = doc["matriz_confusion"]["celdas"][real]
        lineas.append(f"| {real} | " + " | ".join(str(celdas[p]) for p in SECTORES_CANONICOS) + " |")
    fr = doc["frontera_confusion"]
    mayor = fr["mayor_celda_fuera_de_diagonal"]
    lineas += [
        "",
        f"- Mayor celda fuera de la diagonal: {mayor['casos']} casos de {mayor['referencia']} "
        f"predichos como {mayor['prediccion']}.",
        f"- Sistemas: {fr['sistemas_aciertos']}/{fr['sistemas_soporte']} aciertos; errores por "
        "prediccion: "
        + "; ".join(f"{k} {v}" for k, v in fr["errores_de_sistemas_por_prediccion"].items()),
        "",
        "## Potencia y precision del n efectivo",
        "",
        f"- Semi-ancho de Wilson observado (n = {pp['n']}): {pp['semi_ancho_wilson_observado'] * 100:.2f} pts; "
        f"objetivo D1 de c-191: {pp['objetivo_semi_ancho_d1'] * 100:.1f} pts; cumple: "
        f"{'si' if pp['cumple_objetivo_d1'] else 'no'}.",
        f"- MDE (d_z) = {pp['efecto_minimo_detectable']['d_z']:.4f} con alfa = "
        f"{pp['efecto_minimo_detectable']['alfa']}, potencia = "
        f"{pp['efecto_minimo_detectable']['potencia']}, bilateral.",
        f"- {pp['nota']}.",
        "",
        "## Sesgo de exclusion de los discordantes (sensibilidad, no medicion)",
        "",
        f"- {sb['rotulo']}.",
        f"- Peor caso: {sb['peor_caso']['aciertos']}/{sb['peor_caso']['n']} = {sb['peor_caso']['exactitud']:.4f}",
        f"- Mejor caso: {sb['mejor_caso']['aciertos']}/{sb['mejor_caso']['n']} = {sb['mejor_caso']['exactitud']:.4f}",
        f"- Cota ({sb['cota']['definicion']}): tasa {sb['cota']['tasa_excluidos']:.4f}; "
        f"{sb['cota']['aciertos_esperados']:.2f}/{sb['cota']['n']} = {sb['cota']['exactitud']:.4f}",
        f"- Aciertos minimos entre los {sb['excluidos']} excluidos para alcanzar {sb['umbral']:.2f} "
        f"sobre {sb['universo']}: {minimos['minimo']} (tasa {minimos['tasa_requerida']:.4f}).",
        f"- Regla de decision: {sb['regla_decision']['enunciado']}",
        "",
        "## Balance neto con la tasa de error fuera de muestra (condicional)",
        "",
        f"- e_aut fuera de muestra = {bn['e_aut_fuera_de_muestra']['errores']}/{bn['e_aut_fuera_de_muestra']['n']} "
        f"= {bn['e_aut_fuera_de_muestra']['valor']:.4f}; ahorro bruto {bn['insumos']['ahorro_bruto_h']} h/trimestre.",
        f"- Formula: {bn['formula']}.",
        "",
        "| e_man | c (min) | B (h) | a* (%) |",
        "|---|---|---|---|",
    ]
    for e in bn["escenarios"]:
        lineas.append(f"| {e['e_man']} | {e['costo_min']} | {e['balance_h']} | {e['a_estrella_pct']} |")
    lineas.append("")
    for item in bn["no_computable"]:
        lineas.append(f"- No computable: {item['insumo']}. {item['motivo']}.")
    lineas.append("")
    return "\n".join(lineas) + "\n"


def escribir_salidas(doc: dict, directorio: pathlib.Path) -> dict[str, str]:
    """Escribe el JSON y el Markdown (LF, UTF-8 sin BOM); devuelve su SHA-256."""
    directorio = pathlib.Path(directorio)
    ruta_json = directorio / f"{NOMBRE_BASE}.json"
    ruta_md = directorio / f"{NOMBRE_BASE}.md"
    ruta_json.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    ruta_md.write_text(renderizar_md(doc), encoding="utf-8", newline="\n")
    return {ruta_json.name: sha256(ruta_json), ruta_md.name: sha256(ruta_md)}


def main() -> int:
    hashes = escribir_salidas(construir_documento(), SALIDA)
    for nombre, digest in hashes.items():
        print(f"{digest}  {nombre}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
