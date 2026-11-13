#!/usr/bin/env python3
"""Analisis de solo lectura de la validacion fuera de muestra de c-191.

Reproduce, a partir de los artefactos versionados (sin red y sin Gemini):

- la exactitud estricta y laxa sobre el n efectivo (103) con su IC de Wilson;
- el conteo de casos excluidos (discordantes fuera de la referencia por consenso);
- las metricas globales SIN ponderacion (las cifras crudas del bloque out-of-sample) y
  las ponderadas por la composicion por sector del corpus de 200 (design D2).

Reutiliza `evaluation.campana.evaluar_fuera_de_muestra` y
`evaluation.metrics.resumen_exactitud`: no reimplementa el clasificador ni las metricas.

Supuesto del design D2 (si la formula fuera ambigua, se sigue literalmente): la exactitud
de cada sector se calcula agrupando los casos out-of-sample por su sector de REFERENCIA
(`sector_asignado`) y el peso `w_sector` es la proporcion de ese sector en
`data/corpus_evaluacion_pseudonimizado.json`. Entonces
`exactitud_ponderada = suma_sector (w_sector * exactitud_sector)`. Un sector ausente del
out-of-sample contribuiria 0 (aclarado en la salida); en esta corrida los cinco sectores
tienen casos.

Salidas (mismo directorio, LF, UTF-8 sin BOM):

- `analisis_fuera_de_muestra_c191.json`
- `analisis_fuera_de_muestra_c191.md`
- `analisis_fuera_de_muestra_c191.txt`

El script imprime el SHA-256 de cada archivo escrito. No escribe fuera de su directorio.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sys
from collections import Counter

# Raiz del repositorio: evaluation/data/campana/analisis/ -> parents[4].
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import cargar_corpus_solo_lectura, evaluar_fuera_de_muestra  # noqa: E402
from evaluation.corpus import SECTORES_CANONICOS  # noqa: E402
from evaluation.metrics import resumen_exactitud  # noqa: E402
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent

RUTA_PRED_IN = ROOT / "evaluation/data/campana/predicciones_in_sample.json"
RUTA_CORPUS_AJUSTE = ROOT / "data/corpus_evaluacion_pseudonimizado.json"
RUTA_PRED_OOS = ROOT / "evaluation/data/campana/predicciones_independiente.json"
RUTA_CORPUS_OOS = ROOT / "evaluation/data/campana/corpus_independiente.json"
RUTA_PRIMARIA = ROOT / "evaluation/data/campana/doble_etiquetado_independiente.csv"

PINES_IN_SAMPLE = {"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
RANGO_GOOGLE_GENAI_VIGENTE = ">=2.33,<3"


def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _resumen_dict(resumen) -> dict:
    return {
        "casos": resumen.casos,
        "aciertos_estrictos": resumen.aciertos_estrictos,
        "aciertos_laxos": resumen.aciertos_laxos,
        "exactitud_estricta": resumen.exactitud_estricta,
        "ic_estricta_wilson": list(resumen.ic_estricta) if resumen.ic_estricta else None,
        "exactitud_laxa": resumen.exactitud_laxa,
        "ic_laxa_wilson": list(resumen.ic_laxa) if resumen.ic_laxa else None,
    }


def _bloque_dict(bloque) -> dict:
    return {
        "rotulo": bloque.rotulo,
        "classifier_version": bloque.classifier_version,
        "n": bloque.casos,
        "global": _resumen_dict(bloque.resumen),
        "por_etapa": {
            etapa: _resumen_dict(resumen) for etapa, resumen in bloque.por_etapa.items()
        },
    }


def _total_primaria() -> int:
    """Cantidad de casos distintos (id_caso) en la tabla primaria del doble etiquetado."""
    with RUTA_PRIMARIA.open(newline="", encoding="utf-8") as archivo:
        return len({fila["id_caso"] for fila in csv.DictReader(archivo)})


def main() -> int:
    resultado = evaluar_fuera_de_muestra(
        predicciones_in_sample=RUTA_PRED_IN,
        corpus_ajuste=RUTA_CORPUS_AJUSTE,
        predicciones_independiente=RUTA_PRED_OOS,
        corpus_independiente=RUTA_CORPUS_OOS,
        pines_in_sample=PINES_IN_SAMPLE,
        rango_google_genai_vigente=RANGO_GOOGLE_GENAI_VIGENTE,
    )
    if not resultado.obtenido:
        print(f"no se obtuvo la evaluacion fuera de muestra: {resultado.motivo}")
        return 2

    oos, ins = resultado.out_of_sample, resultado.in_sample

    # Pesos por sector del corpus de 200 (share = n_sector / n_total).
    corpus_200 = cargar_corpus_solo_lectura(RUTA_CORPUS_AJUSTE)
    conteo_200 = Counter(caso.sector_asignado for caso in corpus_200)
    total_200 = len(corpus_200)
    pesos = {sector: conteo_200[sector] / total_200 for sector in SECTORES_CANONICOS}

    # Desglose out-of-sample por sector de referencia.
    predicciones_oos = cargar_predicciones(RUTA_PRED_OOS)
    por_id = {caso.id: caso for caso in cargar_corpus_solo_lectura(RUTA_CORPUS_OOS)}
    sectores: dict[str, dict] = {}
    ponderada_estricta = 0.0
    ponderada_laxa = 0.0
    for sector in SECTORES_CANONICOS:
        del_sector = [p for p in predicciones_oos if p.sector_asignado == sector]
        resumen = resumen_exactitud(
            [p.sector_asignado for p in del_sector],
            [p.sector_predicho for p in del_sector],
            [por_id[p.caso_id].conjunto_verdad for p in del_sector],
        )
        peso = pesos[sector]
        aporte_estricta = peso * (resumen.exactitud_estricta or 0.0)
        aporte_laxa = peso * (resumen.exactitud_laxa or 0.0)
        ponderada_estricta += aporte_estricta
        ponderada_laxa += aporte_laxa
        sectores[sector] = {
            "n_out_of_sample": resumen.casos,
            "aciertos_estrictos": resumen.aciertos_estrictos,
            "exactitud_estricta": resumen.exactitud_estricta,
            "ic_estricta_wilson": list(resumen.ic_estricta) if resumen.ic_estricta else None,
            "aciertos_laxos": resumen.aciertos_laxos,
            "exactitud_laxa": resumen.exactitud_laxa,
            "peso_200": peso,
            "n_200": conteo_200[sector],
            "aporte_estricta": aporte_estricta,
            "aporte_laxa": aporte_laxa,
        }

    total_primaria = _total_primaria()
    n_efectivo = oos.casos
    excluidos = total_primaria - n_efectivo

    documento = {
        "change": "c-191-validacion-fuera-de-muestra-150-casos",
        "generador": "evaluation/data/campana/analisis/analisis_fuera_de_muestra_c191.py",
        "metodo": (
            "solo lectura; evaluar_fuera_de_muestra + resumen_exactitud; sin red ni Gemini; "
            "deterministico"
        ),
        "supuesto_d2": (
            "exactitud_sector agrupa los casos out-of-sample por sector_asignado (referencia); "
            "w_sector es la proporcion del sector en data/corpus_evaluacion_pseudonimizado.json; "
            "exactitud_ponderada = suma_sector (w_sector * exactitud_sector). Un sector ausente "
            "del out-of-sample contribuiria 0."
        ),
        "entradas_sha256": {
            "predicciones_in_sample.json": sha256(RUTA_PRED_IN),
            "corpus_evaluacion_pseudonimizado.json": sha256(RUTA_CORPUS_AJUSTE),
            "predicciones_independiente.json": sha256(RUTA_PRED_OOS),
            "corpus_independiente.json": sha256(RUTA_CORPUS_OOS),
            "doble_etiquetado_independiente.csv": sha256(RUTA_PRIMARIA),
        },
        "out_of_sample": _bloque_dict(oos),
        "in_sample_referencia": _bloque_dict(ins),
        "excluidos": {
            "total_primaria": total_primaria,
            "n_efectivo": n_efectivo,
            "excluidos": excluidos,
        },
        "global_sin_ponderar": {
            "origen": "bloque out-of-sample (cifras crudas)",
            "estricta": oos.resumen.exactitud_estricta,
            "ic_estricta_wilson": list(oos.resumen.ic_estricta),
            "laxa": oos.resumen.exactitud_laxa,
            "ic_laxa_wilson": list(oos.resumen.ic_laxa),
        },
        "global_ponderada": {
            "formula": "suma_sector (w_sector * exactitud_sector)",
            "pesos_200": pesos,
            "por_sector": sectores,
            "estricta": ponderada_estricta,
            "laxa": ponderada_laxa,
        },
    }

    # --- reporte legible ------------------------------------------------------------------
    def pct(valor):
        return "n/a" if valor is None else f"{valor * 100:.2f} %"

    def ic(intervalo):
        return "n/a" if not intervalo else f"[{intervalo[0]:.4f}; {intervalo[1]:.4f}]"

    lineas: list[str] = []
    lineas.append("# Analisis fuera de muestra (c-191)")
    lineas.append("")
    lineas.append("Solo lectura; reutiliza `evaluar_fuera_de_muestra` y `resumen_exactitud`. Sin red, sin Gemini.")
    lineas.append("")
    lineas.append("## Out-of-sample (n efectivo)")
    lineas.append("")
    lineas.append(f"- n efectivo: {oos.casos}")
    lineas.append(f"- Exactitud estricta: {oos.resumen.aciertos_estrictos}/{oos.casos} = {oos.resumen.exactitud_estricta:.4f} IC Wilson {ic(oos.resumen.ic_estricta)}")
    lineas.append(f"- Exactitud laxa: {oos.resumen.aciertos_laxos}/{oos.casos} = {oos.resumen.exactitud_laxa:.4f} IC Wilson {ic(oos.resumen.ic_laxa)}")
    lineas.append(f"- Casos excluidos: {excluidos} (de {total_primaria} en la tabla primaria; consenso n={n_efectivo})")
    lineas.append("")
    lineas.append("Por etapa de la cascada:")
    for etapa, resumen in oos.por_etapa.items():
        lineas.append(f"- {etapa}: {resumen.casos} casos; estricta {pct(resumen.exactitud_estricta)}")
    lineas.append("")
    lineas.append("## In-sample (referencia)")
    lineas.append("")
    lineas.append(f"- n: {ins.casos}")
    lineas.append(f"- Exactitud estricta: {ins.resumen.aciertos_estrictos}/{ins.casos} = {ins.resumen.exactitud_estricta:.4f} IC Wilson {ic(ins.resumen.ic_estricta)}")
    lineas.append(f"- Exactitud laxa: {ins.resumen.aciertos_laxos}/{ins.casos} = {ins.resumen.exactitud_laxa:.4f} IC Wilson {ic(ins.resumen.ic_laxa)}")
    for etapa, resumen in ins.por_etapa.items():
        lineas.append(f"- {etapa}: {resumen.casos} casos; estricta {pct(resumen.exactitud_estricta)}")
    lineas.append("")
    lineas.append("## Global sin ponderar (bloque out-of-sample)")
    lineas.append("")
    lineas.append(f"- Estricta: {oos.resumen.exactitud_estricta:.4f} IC Wilson {ic(oos.resumen.ic_estricta)}")
    lineas.append(f"- Laxa: {oos.resumen.exactitud_laxa:.4f} IC Wilson {ic(oos.resumen.ic_laxa)}")
    lineas.append("")
    lineas.append("## Global ponderada (design D2, composicion del corpus de 200)")
    lineas.append("")
    lineas.append("| Sector | n OOS | estricta OOS | w_200 | w*estricta | laxa OOS | w*laxa |")
    lineas.append("|---|---|---|---|---|---|---|")
    for sector in SECTORES_CANONICOS:
        d = sectores[sector]
        lineas.append(
            f"| {sector} | {d['n_out_of_sample']} | {pct(d['exactitud_estricta'])} | "
            f"{d['peso_200']:.4f} | {d['aporte_estricta']:.4f} | {pct(d['exactitud_laxa'])} | {d['aporte_laxa']:.4f} |"
        )
    lineas.append("")
    lineas.append(f"- Estricta ponderada: {ponderada_estricta:.4f}")
    lineas.append(f"- Laxa ponderada: {ponderada_laxa:.4f}")
    lineas.append("")
    lineas.append("## Comparabilidad del clasificador")
    lineas.append("")
    cmp_ = resultado.comparabilidad
    lineas.append(f"- classifier_version: {cmp_.classifier_version}; modelo: {cmp_.modelo}; google_genai instalada: {cmp_.google_genai_instalada}")
    lineas.append(f"- rango in-sample: {cmp_.rango_in_sample}; rango vigente: {cmp_.rango_vigente}; commit independiente: {cmp_.commit_independiente}")
    for limitacion in resultado.limitaciones:
        lineas.append(f"- limitacion: {limitacion}")
    lineas.append("")
    reporte = "\n".join(lineas) + "\n"

    # --- escritura ------------------------------------------------------------------------
    ruta_json = SALIDA / "analisis_fuera_de_muestra_c191.json"
    ruta_md = SALIDA / "analisis_fuera_de_muestra_c191.md"
    ruta_txt = SALIDA / "analisis_fuera_de_muestra_c191.txt"
    ruta_json.write_text(json.dumps(documento, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    ruta_md.write_text(reporte, encoding="utf-8", newline="\n")

    # El .txt es la salida de consola (el reporte mas el manifiesto de hashes de json y md).
    consola = reporte + "\n## SHA-256 de las salidas\n"
    consola += f"- {ruta_json.name}: {sha256(ruta_json)}\n"
    consola += f"- {ruta_md.name}: {sha256(ruta_md)}\n"
    ruta_txt.write_text(consola, encoding="utf-8", newline="\n")

    print(consola, end="")
    print(f"- {ruta_txt.name}: {sha256(ruta_txt)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
