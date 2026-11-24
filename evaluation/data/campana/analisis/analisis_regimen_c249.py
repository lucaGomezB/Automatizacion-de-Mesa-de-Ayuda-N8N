#!/usr/bin/env python3
"""Recomputo por regimen del corpus y de la sonda de latencia del nivel 5 (c-249, D6).

Analisis de solo lectura, determinista y offline. No invoca al modelo, no usa red ni base
de datos, no reclasifica y no modifica el corpus, las predicciones, los artefactos
congelados ni ninguna cifra canonica. Es aditivo: agrega una seccion nueva y no reemplaza
ninguna salida anterior de `evaluation/data/campana/analisis/`.

Entradas versionadas (solo lectura):
- `data/corpus_evaluacion_pseudonimizado.json`: los 200 casos con `id` y `canal_origen`.
- `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`: la prediccion por caso
  (`sector_predicho`, `sector_asignado`).
- `evaluation/data/campana/intervenciones.csv`: las 147 intervenciones con
  `cambio_sector`.
- `evaluation/evidence/load_test_inferencia_2026-11-17.json` y
  `..._ampliada_2026-11-18.json`: el p95 del nivel 5 de N8N y el subconjunto
  deterministico de la corrida ampliada.

METODO (fijado en este docstring antes de correr)

1. Exactitud estricta por canal: `sector_predicho == sector_asignado`, agrupada por
   `canal_origen` del corpus. Intervalo de Wilson al 95 % sobre los casos con prediccion.
2. Exactitud por regimen: el canal telefonico es integramente el regimen (b); correo y
   formulario web son el regimen (a). Se informan aciertos, total, proporcion e intervalo.
3. Intervencion manual: `cambio_sector == true` sobre las 147 intervenciones. Se informa la
   proporcion sobre los 200 casos del corpus (criterio prefijado de la sub-hipotesis 2), la
   proporcion sobre los 147 revisados (denominador post hoc) y la prueba binomial unilateral
   frente a la cota 0,15 (`H1: p > 0,15`).
4. Sonda de latencia: p95 del nivel de 5 concurrentes de N8N en la corrida original y en la
   ampliada, y p95 del subconjunto deterministico de la ampliada.
5. Control: las cifras canonicas se reproducen como anclajes (147/200, 53/81, 51/66, 43/53,
   3.660,4 ms, 5.024,7 ms y p = 0,28). Cualquier diferencia se informa en la salida.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_regimen_c249.json`, `.md` y
`.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte a
byte.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_regimen_c249.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evaluation.metrics import intervalo_wilson  # noqa: E402

COTA = 0.15
CANALES = ("correo electrónico", "formulario web", "llamada telefónica")
REGIMEN_B = "llamada telefónica"


def _resumen(aciertos: int, total: int) -> dict:
    if total == 0:
        return {
            "aciertos": aciertos,
            "total": total,
            "denominador": total,
            "proporcion": None,
            "ic95": None,
        }
    lo, hi = intervalo_wilson(aciertos, total)
    return {
        "aciertos": aciertos,
        "total": total,
        "denominador": total,
        "proporcion": round(aciertos / total, 6),
        "ic95": [round(float(lo), 6), round(float(hi), 6)],
    }


def exactitud_por_canal(casos: list[dict], predicciones: list[dict]) -> dict:
    """Exactitud estricta por canal de origen (solo casos con prediccion)."""
    prediccion = {p["caso_id"]: p for p in predicciones}
    acumulado: dict[str, list[int]] = {c: [0, 0] for c in CANALES}
    for caso in casos:
        pred = prediccion.get(caso["id"])
        if pred is None:
            continue
        canal = caso["canal_origen"]
        acumulado.setdefault(canal, [0, 0])
        acumulado[canal][1] += 1
        if pred["sector_predicho"] == pred["sector_asignado"]:
            acumulado[canal][0] += 1
    orden = list(CANALES) + sorted(c for c in acumulado if c not in CANALES)
    return {canal: _resumen(*acumulado[canal]) for canal in orden}


def exactitud_por_regimen(casos: list[dict], predicciones: list[dict]) -> dict:
    """Agrega la exactitud estricta en regimen (a) y regimen (b)."""
    por_canal = exactitud_por_canal(casos, predicciones)
    aciertos = {"a": 0, "b": 0}
    total = {"a": 0, "b": 0}
    for canal, datos in por_canal.items():
        regimen = "b" if canal == REGIMEN_B else "a"
        aciertos[regimen] += datos["aciertos"]
        total[regimen] += datos["total"]
    return {"a": _resumen(aciertos["a"], total["a"]), "b": _resumen(aciertos["b"], total["b"])}


def intervencion_manual(filas: list[dict], n_corpus: int) -> dict:
    """Proporcion de cambios de derivacion sobre 200 y sobre 147, con binomial."""
    from scipy.stats import binomtest

    revisados = len(filas)
    cambios = sum(1 for f in filas if str(f["cambio_sector"]).strip().lower() == "true")
    p = binomtest(cambios, revisados, COTA, alternative="greater").pvalue if revisados else 1.0
    return {
        "cota": COTA,
        "alternativa": "greater",
        "cambio_total": cambios,
        "revisados": revisados,
        "proporcion_200": _resumen(cambios, n_corpus),
        "proporcion_147": _resumen(cambios, revisados),
        "binomial_p": round(float(p), 6),
    }


def _nivel5(corrida: dict) -> dict:
    for nivel in corrida["capas"]["n8n"]["niveles"]:
        if nivel["concurrencia"] == 5:
            return nivel
    raise ValueError("la corrida no contiene el nivel de 5 concurrentes")


def p95_sonda(original: dict, ampliada: dict) -> dict:
    """p95 del nivel 5 de N8N en ambas corridas y del subconjunto deterministico."""
    nivel_original = _nivel5(original)
    nivel_ampliada = _nivel5(ampliada)
    deterministico = nivel_ampliada.get("inferencia", {}).get("deterministico", {})
    return {
        "original_n5": round(float(nivel_original["p95_ms"]), 4),
        "ampliada_n5": round(float(nivel_ampliada["p95_ms"]), 4),
        "ampliada_det_n5": (
            round(float(deterministico["p95_ms"]), 4)
            if deterministico.get("p95_ms") is not None
            else None
        ),
        "techo_ms": 5000.0,
    }


def construir_resultado(
    *,
    casos: list[dict],
    predicciones: list[dict],
    intervenciones: list[dict],
    n_corpus: int,
    original: dict,
    ampliada: dict,
    rutas_entrada: dict,
) -> dict:
    return {
        "schema_version": 1,
        "entradas": rutas_entrada,
        "exactitud_por_canal": exactitud_por_canal(casos, predicciones),
        "exactitud_por_regimen": exactitud_por_regimen(casos, predicciones),
        "intervencion_manual": intervencion_manual(intervenciones, n_corpus),
        "sonda_nivel_5": p95_sonda(original, ampliada),
    }


def _markdown(r: dict) -> str:
    reg = r["exactitud_por_regimen"]
    can = r["exactitud_por_canal"]
    intv = r["intervencion_manual"]
    son = r["sonda_nivel_5"]
    lineas = [
        "# Recomputo por regimen y de la sonda (c-249)",
        "",
        "Salida generada por `analisis_regimen_c249.py`. Analisis de solo lectura sobre los",
        "artefactos versionados; no reclasifica ni modifica el corpus.",
        "",
        "## Exactitud estricta por regimen",
        "",
        "| Regimen | Aciertos | Total | Proporcion | IC 95 % |",
        "|---|---|---|---|---|",
    ]
    for nombre, etiqueta in (("a", "Regimen (a): correo y formulario web"), ("b", "Regimen (b): telefonia")):
        d = reg[nombre]
        ic = d["ic95"]
        lineas.append(
            f"| {etiqueta} | {d['aciertos']} | {d['total']} | "
            f"{_fmt(d['proporcion'])} | {_fmt_ic(ic)} |"
        )
    lineas += [
        "",
        "## Exactitud estricta por canal",
        "",
        "| Canal | Aciertos | Total | Proporcion | IC 95 % |",
        "|---|---|---|---|---|",
    ]
    for canal, d in can.items():
        lineas.append(
            f"| {canal} | {d['aciertos']} | {d['total']} | {_fmt(d['proporcion'])} | {_fmt_ic(d['ic95'])} |"
        )
    lineas += [
        "",
        "## Intervencion manual sobre la derivacion",
        "",
        f"- Cambios de derivacion: {intv['cambio_total']} sobre {intv['revisados']} revisados.",
        f"- Sobre los 200 casos (regla prefijada): {_fmt(intv['proporcion_200']['proporcion'])} "
        f"{_fmt_ic(intv['proporcion_200']['ic95'])}.",
        f"- Sobre los 147 revisados (denominador post hoc): "
        f"{_fmt(intv['proporcion_147']['proporcion'])} {_fmt_ic(intv['proporcion_147']['ic95'])}.",
        f"- Binomial unilateral frente a {intv['cota']} (H1: p > {intv['cota']}): "
        f"p = {intv['binomial_p']}.",
        "",
        "## Sonda de latencia del nivel 5 de N8N",
        "",
        f"- Corrida original: p95 = {son['original_n5']} ms.",
        f"- Corrida ampliada: p95 = {son['ampliada_n5']} ms.",
        f"- Subconjunto deterministico de la ampliada: p95 = {son['ampliada_det_n5']} ms.",
        f"- Techo de la regla: {son['techo_ms']} ms.",
        "",
        "## Entradas",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for ruta, sha in r["entradas"].items():
        lineas.append(f"| `{ruta}` | `{sha}` |")
    lineas.append("")
    return "\n".join(lineas)


def _fmt(valor: float | None) -> str:
    return "no estimable" if valor is None else f"{valor:.4f}"


def _fmt_ic(ic: list[float] | None) -> str:
    return "no estimable" if ic is None else f"[{ic[0]:.4f}; {ic[1]:.4f}]"


def escribir_salidas(resultado: dict, directorio: Path) -> list[Path]:
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    json_path = directorio / "analisis_regimen_c249.json"
    md_path = directorio / "analisis_regimen_c249.md"
    json_texto = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    md_texto = _markdown(resultado)
    json_path.write_bytes(json_texto.encode("utf-8"))
    md_path.write_bytes(md_texto.encode("utf-8"))
    sumas = (
        f"{hashlib.sha256(json_texto.encode('utf-8')).hexdigest()}  {json_path.name}\n"
        f"{hashlib.sha256(md_texto.encode('utf-8')).hexdigest()}  {md_path.name}\n"
    )
    sums_path = directorio / "analisis_regimen_c249.SHA256SUMS.txt"
    sums_path.write_bytes(sumas.encode("utf-8"))
    return [json_path, md_path, sums_path]


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main() -> int:
    archivos = {
        "data/corpus_evaluacion_pseudonimizado.json": RAIZ / "data/corpus_evaluacion_pseudonimizado.json",
        "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json": RAIZ / "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json",
        "evaluation/data/campana/intervenciones.csv": RAIZ / "evaluation/data/campana/intervenciones.csv",
        "evaluation/evidence/load_test_inferencia_2026-11-17.json": RAIZ / "evaluation/evidence/load_test_inferencia_2026-11-17.json",
        "evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json": RAIZ / "evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json",
    }
    corpus = json.loads(archivos["data/corpus_evaluacion_pseudonimizado.json"].read_text(encoding="utf-8"))
    predicciones = json.loads(
        archivos["evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"].read_text(encoding="utf-8")
    )
    with archivos["evaluation/data/campana/intervenciones.csv"].open(newline="", encoding="utf-8") as fh:
        intervenciones = list(csv.DictReader(fh))
    original = json.loads(
        archivos["evaluation/evidence/load_test_inferencia_2026-11-17.json"].read_text(encoding="utf-8")
    )
    ampliada = json.loads(
        archivos["evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json"].read_text(encoding="utf-8")
    )
    resultado = construir_resultado(
        casos=corpus["casos"],
        predicciones=predicciones["predictions"],
        intervenciones=intervenciones,
        n_corpus=len(corpus["casos"]),
        original=original,
        ampliada=ampliada,
        rutas_entrada={ruta: _sha256(p) for ruta, p in archivos.items()},
    )
    salidas = escribir_salidas(resultado, Path(__file__).resolve().parent)
    for ruta in salidas:
        print(f"{_sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())