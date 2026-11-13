#!/usr/bin/env python3
"""Analisis de solo lectura para el dictamen CONEAU v1.3.0 (c-207).

Bloques: `ic_reduccion_tiempo`, `acuerdo_e3_e4` y `balance_neto_referencia_comun`.
Reutiliza `evaluation.metrics`, `evaluation.kappa` y `evaluation.campana` sin editarlos.
Sin red y sin Gemini. Determinista.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import random
import sys
from statistics import fmean

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import (  # noqa: E402
    REFERENCIA_CONSENSO_NUEVO,
    cargar_corpus_solo_lectura,
    construir_referencia,
)
from evaluation.kappa import kappa_cohen, parear_doble_etiquetado  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402

RUTA_CORPUS_200 = ROOT / "data/corpus_evaluacion_pseudonimizado.json"
SALIDA = pathlib.Path(__file__).resolve().parent
RUTA_PRIMARIA = ROOT / "evaluation/data/campana/doble_etiquetado_independiente.csv"
RUTA_C205 = SALIDA / "analisis_fuera_de_muestra_c205.json"
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_PLANILLA = CAMPANA / "plantilla_etiquetado.csv"
RUTA_PRED_IN_SAMPLE = CAMPANA / "predicciones_in_sample.json"
RUTA_CORPUS_CAMPANA = CAMPANA / "corpus_campana.json"

# Insumos del balance neto (Secciones 3.1 y 3.4 del memo canonico).
DELTA_T_S = 43.82  # ahorro medio por incidente, s
N_TRIMESTRAL = 2646  # incidentes por trimestre
COSTO_MIN_GRILLA = (5, 10, 15)  # costo por derivacion erronea, min (supuesto)
REF_ORIGINAL = "etiquetado original del corpus (sector_asignado)"
REF_CONSENSO = "consenso de E1 y E2 (138 casos; discordantes excluidos)"


def cargar_pares_tiempo(ruta: pathlib.Path = RUTA_CORPUS_200) -> tuple[list[float], list[float]]:
    """Tiempos `(manual, automatizado)` por caso del corpus versionado, en orden de archivo."""
    casos = json.loads(ruta.read_text(encoding="utf-8"))["casos"]
    return (
        [float(c["tiempo_manual_s"]) for c in casos],
        [float(c["tiempo_automatizado_s"]) for c in casos],
    )


def ic_reduccion_tiempo(
    manual: list[float],
    automatizado: list[float],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> dict:
    """Reduccion relativa `1 - media(aut)/media(man)` con IC bootstrap percentil por pares."""
    if len(manual) != len(automatizado):
        raise ValueError("las series manual y automatizada deben tener la misma longitud.")
    n = len(manual)
    if n == 0:
        raise ValueError("no hay pares de tiempos.")
    if fmean(manual) == 0:
        raise ValueError("la media manual es cero: la reduccion relativa no esta definida.")

    reducciones: list[float] = []
    diferencias: list[float] = []
    generador = random.Random(semilla)
    for indices in remuestreos_indices(generador, n, remuestreos):
        media_man = fmean(manual[i] for i in indices)
        media_aut = fmean(automatizado[i] for i in indices)
        if media_man == 0:
            continue
        reducciones.append(1.0 - media_aut / media_man)
        diferencias.append(media_man - media_aut)
    return {
        "n": n,
        "reduccion": 1.0 - fmean(automatizado) / fmean(manual),
        "ic_reduccion": list(percentil_intervalo(reducciones, NIVEL_CONFIANZA)),
        "diferencia_medias_s": fmean(manual) - fmean(automatizado),
        "ic_diferencia_medias_s": list(percentil_intervalo(diferencias, NIVEL_CONFIANZA)),
        "metodo": "bootstrap percentil remuestreando pares (casos) con reemplazo",
        "nivel_confianza": NIVEL_CONFIANZA,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }


def _kappa_dict(resultado) -> dict:
    return {
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
        "rotulos_ic_asintotico": list(resultado.rotulos_ic_asintotico),
        "rotulos_ic_bootstrap": list(resultado.rotulos_ic_bootstrap),
    }


def acuerdo_e3_e4(
    filas: list[dict], *, esperado_concordantes: int, esperado_total: int
) -> dict:
    """Acuerdo observado y kappa de Cohen entre los dos etiquetadores (sector principal).

    Falla con `ValueError` si el total o las concordantes no coinciden con lo esperado
    (n efectivo de c-191): no se ajusta a mano.
    """
    etiquetadores, pares = parear_doble_etiquetado(filas)
    sectores = [
        (p.registro_1["sector_etiquetado"], p.registro_2["sector_etiquetado"]) for p in pares
    ]
    total = len(sectores)
    concordantes = sum(1 for a, b in sectores if a == b)
    if total != esperado_total:
        raise ValueError(f"el total de casos {total} no coincide con el esperado {esperado_total}.")
    if concordantes != esperado_concordantes:
        raise ValueError(
            f"las concordantes {concordantes} no coinciden con el n efectivo esperado "
            f"{esperado_concordantes}."
        )
    return {
        "etiquetadores": list(etiquetadores),
        "total": total,
        "concordantes": concordantes,
        "discordantes": total - concordantes,
        "acuerdo_observado": concordantes / total,
        "kappa": _kappa_dict(kappa_cohen(sectores)),
        "rotulo": "fiabilidad inter-etiquetador E3/E4 sobre el sector principal de los 150 casos",
    }


def acuerdo_e3_e4_versionado() -> dict:
    """`acuerdo_e3_e4` sobre `doble_etiquetado_independiente.csv` contra el n efectivo de c-205."""
    n_efectivo = int(json.loads(RUTA_C205.read_text(encoding="utf-8"))["n_efectivo"])
    total = int(json.loads(RUTA_C205.read_text(encoding="utf-8"))["total_primaria"])
    with RUTA_PRIMARIA.open(newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    resultado = acuerdo_e3_e4(filas, esperado_concordantes=n_efectivo, esperado_total=total)
    resultado["n_efectivo_c205"] = n_efectivo
    return resultado


# ---------------------------------------------------------------------------
# Balance neto con referencia comun (rec. 5)
# ---------------------------------------------------------------------------
def hay_asimetria_de_referencia(e_aut: dict, e_man: dict) -> bool:
    """`True` si las dos tasas se miden contra referencias distintas."""
    return e_aut["referencia"] != e_man["referencia"]


def _tasa(errores: int, n: int, referencia: str, unidad: str) -> dict:
    return {
        "errores": errores,
        "n": n,
        "tasa": errores / n,
        "referencia": referencia,
        "unidad": unidad,
    }


def _errores_manual(
    filas_manual: list[dict], referencia: dict[str, str]
) -> dict[str, tuple[int, int]]:
    """Por caso de la referencia: `(errores, derivaciones)` del brazo manual (acierto estricto)."""
    por_caso: dict[str, tuple[int, int]] = {}
    for fila in filas_manual:
        caso = fila["id_caso"]
        if caso not in referencia:
            continue  # caso discordante de la referencia: queda afuera
        errores, derivaciones = por_caso.get(caso, (0, 0))
        fallo = int(fila["sector_etiquetado"] != referencia[caso])
        por_caso[caso] = (errores + fallo, derivaciones + 1)
    return por_caso


def _casos_comunes(
    referencia: dict[str, str],
    predichos: dict[str, str],
    filas_manual: list[dict],
) -> list[tuple[int, int, int]]:
    """Tuplas `(error_aut, errores_man, derivaciones_man)` por caso, en orden de id."""
    manual = _errores_manual(filas_manual, referencia)
    faltan = sorted(set(referencia) - set(manual))
    if faltan:
        raise ValueError(f"casos de la referencia sin derivaciones del brazo manual: {faltan[:3]}")
    return [
        (int(predichos[caso] != referencia[caso]), *manual[caso]) for caso in sorted(referencia)
    ]


def _estadisticos(casos: list[tuple[int, int, int]], indices) -> tuple[float, float]:
    n = len(indices)
    derivaciones = sum(casos[i][2] for i in indices)
    e_aut = sum(casos[i][0] for i in indices) / n
    e_man = sum(casos[i][1] for i in indices) / derivaciones
    return e_aut, e_man


def _balance(e_aut: float, e_man: float, costo_min: int) -> float:
    return N_TRIMESTRAL / 3600 * (DELTA_T_S - (e_aut - e_man) * costo_min * 60)


def _a_estrella(e_man: float, costo_min: int) -> float:
    return 1.0 - e_man - DELTA_T_S / (costo_min * 60)


def _signo(inferior: float, superior: float) -> str:
    if inferior > 0:
        return "positivo"
    if superior < 0:
        return "negativo"
    return "no fijado"


def balance_con_referencia_comun(
    casos: list[tuple[int, int, int]],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> dict:
    """Balance neto `B` y `a*` con `e_aut` y `e_man` medidos contra la MISMA referencia.

    `casos` son tuplas `(error_aut, errores_man, derivaciones_man)` por caso. `e_aut` es por
    caso; `e_man` es por derivacion (errores / derivaciones). El IC es un bootstrap percentil
    que remuestrea casos y empareja las derivaciones del brazo manual con su caso.
    """
    if not casos:
        raise ValueError("no hay casos.")
    if any(derivaciones < 1 for _, _, derivaciones in casos):
        raise ValueError("todo caso debe tener al menos una derivacion manual.")
    n = len(casos)
    e_aut, e_man = _estadisticos(casos, range(n))
    generador = random.Random(semilla)
    remuestras = [
        _estadisticos(casos, indices)
        for indices in remuestreos_indices(generador, n, remuestreos)
    ]
    diferencias = [a - m for a, m in remuestras]
    escenarios = []
    for costo in COSTO_MIN_GRILLA:
        balances = [_balance(a, m, costo) for a, m in remuestras]
        inferior, superior = percentil_intervalo(balances, NIVEL_CONFIANZA)
        a_est = [_a_estrella(m, costo) for _, m in remuestras]
        escenarios.append(
            {
                "costo_min": costo,
                "balance_h": _balance(e_aut, e_man, costo),
                "balance_h_ic": [inferior, superior],
                "signo_fijado_por_ic": _signo(inferior, superior),
                "a_estrella": _a_estrella(e_man, costo),
                "a_estrella_ic": list(percentil_intervalo(a_est, NIVEL_CONFIANZA)),
            }
        )
    return {
        "e_aut": e_aut,
        "e_man": e_man,
        "diferencia": e_aut - e_man,
        "diferencia_ic": list(percentil_intervalo(diferencias, NIVEL_CONFIANZA)),
        "escenarios": escenarios,
        "metodo": "bootstrap percentil por caso (empareja las derivaciones manuales con su caso)",
        "nivel_confianza": NIVEL_CONFIANZA,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }


def _leer_planilla() -> list[dict]:
    with RUTA_PLANILLA.open(newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def _insumos_balance() -> dict:
    """Referencias, predicciones y derivaciones manuales leidas de los artefactos."""
    planilla = _leer_planilla()
    manual = [f for f in planilla if f["tarea"] == "brazo_manual"]
    consenso_ref = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=planilla)
    consenso = {caso: datos.sector for caso, datos in consenso_ref.casos.items()}
    corpus = cargar_corpus_solo_lectura(RUTA_CORPUS_CAMPANA)
    original = {caso.id: caso.sector_asignado for caso in corpus}
    predichos = {p.caso_id: p.sector_predicho for p in cargar_predicciones(RUTA_PRED_IN_SAMPLE)}
    return {
        "manual": manual,
        "consenso": consenso,
        "original": original,
        "predichos": predichos,
    }


def _conteos(referencia: dict[str, str], insumos: dict) -> dict:
    casos = _casos_comunes(referencia, insumos["predichos"], insumos["manual"])
    return {
        "casos": len(casos),
        "errores_automatizado": sum(c[0] for c in casos),
        "errores_manual": sum(c[1] for c in casos),
        "derivaciones_manual": sum(c[2] for c in casos),
        "_casos": casos,
    }


def verificar_asimetria_balance(insumos: dict | None = None) -> dict:
    """Paso de verificacion (D4): referencia de cada tasa tal como la usa el texto actual."""
    insumos = insumos or _insumos_balance()
    original = _conteos(insumos["original"], insumos)
    consenso = _conteos(insumos["consenso"], insumos)
    e_aut_texto = _tasa(
        original["errores_automatizado"], original["casos"], REF_ORIGINAL, "por caso"
    )
    e_man_texto = _tasa(
        consenso["errores_manual"], consenso["derivaciones_manual"], REF_CONSENSO, "por derivacion"
    )
    return {
        "e_aut_texto": e_aut_texto,
        "e_man_texto": e_man_texto,
        "e_aut_consenso": _tasa(
            consenso["errores_automatizado"], consenso["casos"], REF_CONSENSO, "por caso"
        ),
        "asimetria_confirmada": hay_asimetria_de_referencia(e_aut_texto, e_man_texto),
    }


LIMITES_NO_IGUALABLES = [
    {
        "limite": "unidad de conteo",
        "detalle": (
            "e_aut se cuenta por caso y e_man por derivacion de operador (13 casos de la "
            "referencia de consenso y 20 del corpus completo tienen doble cobertura); el "
            "bootstrap empareja las derivaciones con su caso, pero la unidad no se iguala"
        ),
    },
    {
        "limite": "origen del ahorro de tiempo",
        "detalle": (
            "dt = 43,82 s proviene de la campana 2026-10 (cronometraje con carga del ticket); "
            "el brazo manual de la campana complementaria mide solo la decision de sector. "
            "dt se trata como constante y su incertidumbre no entra en el IC de B"
        ),
    },
    {
        "limite": "cobertura de la referencia de consenso",
        "detalle": (
            "la referencia de consenso excluye los casos discordantes entre E1 y E2, que "
            "tienden a ser los mas dificiles; ambas tasas quedan acotadas a los casos faciles"
        ),
    },
    {
        "limite": "costo por derivacion erronea",
        "detalle": "c (5, 10 o 15 min) es un supuesto propio: la campana no cronometra reasignaciones",
    },
    {
        "limite": "referencia original para el brazo manual",
        "detalle": (
            "contra el etiquetado original, el acierto estricto del brazo manual es bajo porque "
            "el 53,5 % de los casos admite mas de un sector (la comparacion es estricta contra el "
            "sector asignado); se informa como segunda referencia comun, no como la principal"
        ),
    },
]


def balance_neto_referencia_comun() -> dict:
    """Bloque completo: verificacion de la asimetria y recalculo con referencia comun."""
    insumos = _insumos_balance()
    verificacion = verificar_asimetria_balance(insumos)
    bloque: dict = {
        "estado": "condicional",
        "formula": "B = (N / 3600) * [dt - (e_aut - e_man) * c]; a* = 1 - e_man - dt / c",
        "insumos": {
            "delta_t_s": DELTA_T_S,
            "n_trimestral": N_TRIMESTRAL,
            "ahorro_bruto_h": N_TRIMESTRAL * DELTA_T_S / 3600,
            "procedencia": "dt y N: Secciones 3.1 y 3.4 de numeros-canonicos.md; c: supuesto",
        },
        "verificacion": verificacion,
        "limites_no_igualables": LIMITES_NO_IGUALABLES,
    }
    if not verificacion["asimetria_confirmada"]:
        return bloque
    for clave, referencia, rotulo in (
        ("referencia_consenso", insumos["consenso"], REF_CONSENSO),
        ("referencia_original", insumos["original"], REF_ORIGINAL),
    ):
        conteos = _conteos(referencia, insumos)
        casos = conteos.pop("_casos")
        bloque[clave] = {"rotulo": rotulo, **conteos, **balance_con_referencia_comun(casos)}
    return bloque


# ---------------------------------------------------------------------------
# Documento y salidas
# ---------------------------------------------------------------------------
NOMBRE_BASE = "analisis_dictamen_c207"
ENTRADAS = (
    RUTA_CORPUS_200,
    RUTA_PLANILLA,
    RUTA_PRED_IN_SAMPLE,
    RUTA_CORPUS_CAMPANA,
    RUTA_PRIMARIA,
    RUTA_C205,
)


def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def construir_documento() -> dict:
    """Calcula los tres bloques; falla antes de devolver nada si el acuerdo no reproduce c-191."""
    acuerdo = acuerdo_e3_e4_versionado()
    manual, automatizado = cargar_pares_tiempo()
    return {
        "change": "c-207-atender-el-dictamen-coneau-v1-3-0",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "solo lectura; evaluation.metrics + evaluation.kappa + evaluation.campana; sin red "
            "ni Gemini; deterministico"
        ),
        "entradas_sha256": {
            ruta.relative_to(ROOT).as_posix(): sha256(ruta) for ruta in ENTRADAS
        },
        "ic_reduccion_tiempo": ic_reduccion_tiempo(manual, automatizado),
        "acuerdo_e3_e4": acuerdo,
        "balance_neto_referencia_comun": balance_neto_referencia_comun(),
    }


def _p(valor: float, decimales: int = 4) -> str:
    return f"{valor:.{decimales}f}"


def _par(par: list[float] | None, decimales: int = 4) -> str:
    return "n/a" if not par else f"[{_p(par[0], decimales)}; {_p(par[1], decimales)}]"


def _md_balance(bloque: dict) -> list[str]:
    ver = bloque["verificacion"]
    lineas = [
        "## Balance neto con referencia comun (rec. 5)",
        "",
        f"- Formula: {bloque['formula']}; N = {bloque['insumos']['n_trimestral']}; "
        f"dt = {bloque['insumos']['delta_t_s']} s; ahorro bruto = "
        f"{_p(bloque['insumos']['ahorro_bruto_h'], 2)} h-persona por trimestre.",
        f"- Verificacion: e_aut del texto = {ver['e_aut_texto']['errores']}/"
        f"{ver['e_aut_texto']['n']} ({ver['e_aut_texto']['referencia']}); e_man del texto = "
        f"{ver['e_man_texto']['errores']}/{ver['e_man_texto']['n']} "
        f"({ver['e_man_texto']['referencia']}); e_aut contra el consenso = "
        f"{ver['e_aut_consenso']['errores']}/{ver['e_aut_consenso']['n']}.",
        f"- asimetria_confirmada: {str(ver['asimetria_confirmada']).lower()}",
        "",
    ]
    for clave in ("referencia_consenso", "referencia_original"):
        if clave not in bloque:
            continue
        r = bloque[clave]
        lineas += [
            f"### {clave}: {r['rotulo']}",
            "",
            f"- e_aut = {r['errores_automatizado']}/{r['casos']} = {_p(r['e_aut'])}; "
            f"e_man = {r['errores_manual']}/{r['derivaciones_manual']} = {_p(r['e_man'])}",
            f"- e_aut - e_man = {_p(r['diferencia'])} IC95 {_par(r['diferencia_ic'])} "
            f"({r['metodo']}; semilla {r['semilla']}; B = {r['remuestreos']})",
            "",
            "| c (min) | B (h-persona) | IC95 de B | Signo por IC | a* | IC95 de a* |",
            "|---|---|---|---|---|---|",
        ]
        for e in r["escenarios"]:
            lineas.append(
                f"| {e['costo_min']} | {_p(e['balance_h'], 1)} | {_par(e['balance_h_ic'], 1)} | "
                f"{e['signo_fijado_por_ic']} | {_p(e['a_estrella'])} | {_par(e['a_estrella_ic'])} |"
            )
        lineas.append("")
    lineas.append("### Limites no igualables")
    lineas.append("")
    lineas += [f"- {x['limite']}: {x['detalle']}." for x in bloque["limites_no_igualables"]]
    lineas.append("")
    return lineas


def renderizar(doc: dict) -> tuple[str, str]:
    """`(json, markdown)` en texto con LF y sin BOM."""
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    t, a, k = doc["ic_reduccion_tiempo"], doc["acuerdo_e3_e4"], doc["acuerdo_e3_e4"]["kappa"]
    lineas = [
        "# Analisis del dictamen CONEAU v1.3.0 (c-207)",
        "",
        "Solo lectura; reutiliza `evaluation/metrics.py`, `evaluation/kappa.py` y "
        "`evaluation/campana.py`. Sin red, sin Gemini.",
        "",
        "## IC de la reduccion relativa del tiempo (rec. 6)",
        "",
        f"- Pares: {t['n']}; reduccion = {_p(t['reduccion'])}; IC95 {_par(t['ic_reduccion'])}",
        f"- Diferencia de medias = {_p(t['diferencia_medias_s'], 2)} s; IC95 "
        f"{_par(t['ic_diferencia_medias_s'], 2)} s",
        f"- Metodo: {t['metodo']}; semilla {t['semilla']}; B = {t['remuestreos']}",
        "",
        "## Acuerdo entre E3 y E4 (rec. 1)",
        "",
        f"- {a['rotulo']}",
        f"- Concordantes {a['concordantes']} de {a['total']} (discordantes {a['discordantes']}); "
        f"acuerdo observado = {_p(a['acuerdo_observado'])}",
        f"- kappa de Cohen = {_p(k['kappa'])}; IC asintotico {_par(k['ic_asintotico'])}; "
        f"IC bootstrap {_par(k['ic_bootstrap'])}; p_e = {_p(k['p_e'])}; PABAK = {_p(k['pabak'])}; "
        f"rotulo de Landis y Koch: {k['rotulo_landis_koch']}",
        "",
    ]
    lineas += _md_balance(doc["balance_neto_referencia_comun"])
    lineas += ["## Entradas (SHA-256)", ""]
    lineas += [f"- `{ruta}`: `{h}`" for ruta, h in doc["entradas_sha256"].items()]
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
    args = parser.parse_args(argv)
    doc = construir_documento()  # falla antes de escribir si el acuerdo no reproduce c-191
    for ruta in escribir(doc, args.salida):
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
