#!/usr/bin/env python3
"""Recomputo de la asimetria telefonica y de la sub-hipotesis 1 sin telefonia (c-250, D6).

Analisis de solo lectura, determinista y offline. No invoca al modelo, no usa red ni base
de datos, no reclasifica y no modifica el corpus ni ningun artefacto congelado. Es aditivo:
agrega las lecturas que el dictamen de quinta instancia pidio (C-03) y no reemplaza ninguna
salida anterior de `evaluation/data/campana/analisis/`.

Entradas versionadas (solo lectura):

- `data/corpus_resultados_telefonia.json`: lista de 81 registros de telefonia, cada uno con
  `duracion_segundos` (grabacion cruda recitada) y `t_e2e_s` (grabacion mas procesamiento).
- `data/corpus_evaluacion_pseudonimizado.json`: los 200 casos con `canal_origen`,
  `tiempo_manual_s` y `tiempo_automatizado_s`.

METODO (fijado en este docstring antes de correr)

1. Telefonia: mediana y media de `duracion_segundos` y de `t_e2e_s` sobre los registros que
   los declaran. `t_e2e_s` se resume solo sobre los registros que lo tienen (los ausentes se
   omiten de ese resumen, no del conteo de grabaciones).
2. Sin telefonia (correo electronico + formulario web, regimen (a)): se filtran los casos
   cuyo `canal_origen` no es `llamada telefonica`. Se informa la media de `tiempo_manual_s`
   y de `tiempo_automatizado_s`, la diferencia pareada (manual menos automatizado) por caso
   y la reduccion relativa de la media:
   `reduccion = (media_manual - media_automatizada) / media_manual`.
3. Intervalos: bootstrap percentil al 95 %, por pares, remuestreando los indices de los
   pares con reemplazo (2000 remuestreos, semilla 20261021, la misma del contraste
   primario). Para cada remuestra se recomputa la cantidad de interes (diferencia pareada
   media o reduccion) y se toman los percentiles 2,5 y 97,5.
4. Contraste de Wilcoxon de rangos con signo sobre las diferencias pareadas sin telefonia,
   informado como lectura suplementaria (no es el contraste primario de la sub-hipotesis 1,
   que sigue siendo el de los 200 pares).

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_quinta_instancia_c250.json`, `.md`
y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte a
byte.

Uso (desde la raiz del repositorio):

    python3 evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[4]

CANALES_WEB = ("correo electrónico", "formulario web")
SEMILLA = 20261021
REMUESTREOS = 2000
CONFIANZA = 0.95


def _resumen(valores: list[float]) -> dict:
    """Resumen descriptivo de una lista de valores (media, mediana, minimo y maximo)."""
    if not valores:
        return {"n": 0, "media": None, "mediana": None, "min": None, "max": None}
    arr = np.asarray(valores, dtype=float)
    return {
        "n": int(len(arr)),
        "media": round(float(arr.mean()), 4),
        "mediana": round(float(np.median(arr)), 4),
        "min": round(float(arr.min()), 4),
        "max": round(float(arr.max()), 4),
    }


def telefonia_duraciones(filas: list[dict]) -> dict:
    """Mediana y media de ``duracion_segundos`` y de ``t_e2e_s`` de las grabaciones.

    ``t_e2e_s`` se resume solo sobre los registros que lo declaran; ``duracion_segundos``
    resume todas las grabaciones presentes.
    """
    duraciones = [float(f["duracion_segundos"]) for f in filas if f.get("duracion_segundos") is not None]
    t_e2e = [float(f["t_e2e_s"]) for f in filas if f.get("t_e2e_s") is not None]
    return {
        "n": len(filas),
        "duracion_segundos": _resumen(duraciones),
        "t_e2e_s": _resumen(t_e2e),
    }


def pares_web(casos: list[dict]) -> tuple[list[float], list[float]]:
    """Pares (manual, automatizado) de los casos de correo y formulario (regimen (a))."""
    manual: list[float] = []
    auto: list[float] = []
    for caso in casos:
        if caso["canal_origen"] in CANALES_WEB:
            manual.append(float(caso["tiempo_manual_s"]))
            auto.append(float(caso["tiempo_automatizado_s"]))
    return manual, auto


def _bootstrap_pareado(manual: np.ndarray, auto: np.ndarray, func, semilla: int, remuestreos: int) -> tuple[float, float]:
    """Intervalo bootstrap percentil por pares de una funcion de los dos brazos."""
    rng = np.random.default_rng(semilla)
    n = len(manual)
    muestras = []
    for _ in range(remuestreos):
        idx = rng.integers(0, n, n)
        muestras.append(func(manual[idx], auto[idx]))
    lo, hi = np.percentile(muestras, [(1 - CONFIANZA) / 2 * 100, (1 + CONFIANZA) / 2 * 100])
    return float(lo), float(hi)


def _reduccion(manual: np.ndarray, auto: np.ndarray) -> float:
    return (float(manual.mean()) - float(auto.mean())) / float(manual.mean())


def sin_telefonia(casos: list[dict]) -> dict:
    """Desagregacion y reduccion sin telefonia (correo + formulario web)."""
    manual, auto = pares_web(casos)
    n = len(manual)
    if n == 0:
        return {
            "n": 0,
            "media_manual_s": None,
            "media_automatizada_s": None,
            "reduccion": {"puntual": None, "ic95": None},
            "diferencia_pareada": {"media_s": None, "ic95": None},
            "wilcoxon": {"T": None, "p": None},
        }
    m = np.asarray(manual, dtype=float)
    a = np.asarray(auto, dtype=float)
    diffs = m - a

    puntual = _reduccion(m, a)
    lo_red, hi_red = _bootstrap_pareado(m, a, _reduccion, SEMILLA, REMUESTREOS)

    media_diff = float(diffs.mean())
    lo_diff, hi_diff = _bootstrap_pareado(m, a, lambda mm, aa: float((mm - aa).mean()), SEMILLA, REMUESTREOS)

    w = wilcoxon(m, a)
    return {
        "n": n,
        "media_manual_s": round(float(m.mean()), 4),
        "media_automatizada_s": round(float(a.mean()), 4),
        "reduccion": {"puntual": round(puntual, 6), "ic95": [round(lo_red, 6), round(hi_red, 6)]},
        "diferencia_pareada": {"media_s": round(media_diff, 4), "ic95": [round(lo_diff, 4), round(hi_diff, 4)]},
        "wilcoxon": {"T": float(w.statistic), "p": float(w.pvalue)},
    }


def construir_resultado(*, filas_telefonia: list[dict], casos: list[dict], rutas_entrada: dict) -> dict:
    return {
        "schema_version": 1,
        "entradas": rutas_entrada,
        "metodo": {
            "canales_sin_telefonia": list(CANALES_WEB),
            "semilla_bootstrap": SEMILLA,
            "remuestreos_bootstrap": REMUESTREOS,
            "confianza": CONFIANZA,
        },
        "telefonia": telefonia_duraciones(filas_telefonia),
        "sin_telefonia": sin_telefonia(casos),
    }


def _fmt(valor: float | None) -> str:
    return "no estimable" if valor is None else f"{valor:.4f}"


def _fmt_p(valor: float | None) -> str:
    return "no estimable" if valor is None else f"{valor:.3e}"


def _fmt_ic(ic: list[float] | None) -> str:
    return "no estimable" if ic is None else f"[{ic[0]:.4f}; {ic[1]:.4f}]"


def _markdown(r: dict) -> str:
    tel = r["telefonia"]
    st = r["sin_telefonia"]
    dur = tel["duracion_segundos"]
    e2e = tel["t_e2e_s"]
    lineas = [
        "# Recomputo de la asimetria telefonica y de la sub-hipotesis 1 sin telefonia (c-250)",
        "",
        "Salida generada por `analisis_quinta_instancia_c250.py`. Analisis de solo lectura "
        "sobre los artefactos versionados; no reclasifica ni modifica el corpus.",
        "",
        "## Telefonia: grabacion cruda frente a grabacion mas procesamiento",
        "",
        f"- Casos (grabaciones): {tel['n']}.",
        f"- `duracion_segundos` (grabacion cruda): media {_fmt(dur['media'])} s; "
        f"mediana {_fmt(dur['mediana'])} s; rango [{_fmt(dur['min'])}; {_fmt(dur['max'])}] s.",
        f"- `t_e2e_s` (grabacion mas procesamiento): media {_fmt(e2e['media'])} s; "
        f"mediana {_fmt(e2e['mediana'])} s.",
        "",
        "## Sub-hipotesis 1 sin telefonia (correo electronico + formulario web, regimen (a))",
        "",
        f"- Casos: {st['n']}.",
        f"- Media manual: {_fmt(st['media_manual_s'])} s.",
        f"- Media automatizada: {_fmt(st['media_automatizada_s'])} s.",
        f"- Reduccion (media): {_fmt(st['reduccion']['puntual'] * 100 if st['reduccion']['puntual'] is not None else None)} % "
        f"{_fmt_ic([x * 100 for x in st['reduccion']['ic95']] if st['reduccion']['ic95'] else None)}.",
        f"- Diferencia pareada media: {_fmt(st['diferencia_pareada']['media_s'])} s "
        f"{_fmt_ic(st['diferencia_pareada']['ic95'])}.",
        f"- Wilcoxon pareado (lectura suplementaria): T = {_fmt(st['wilcoxon']['T'])}, p = {_fmt_p(st['wilcoxon']['p'])}.",
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


def escribir_salidas(resultado: dict, directorio: Path) -> list[Path]:
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    json_path = directorio / "analisis_quinta_instancia_c250.json"
    md_path = directorio / "analisis_quinta_instancia_c250.md"
    json_texto = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    md_texto = _markdown(resultado)
    json_path.write_bytes(json_texto.encode("utf-8"))
    md_path.write_bytes(md_texto.encode("utf-8"))
    sumas = (
        f"{hashlib.sha256(json_texto.encode('utf-8')).hexdigest()}  {json_path.name}\n"
        f"{hashlib.sha256(md_texto.encode('utf-8')).hexdigest()}  {md_path.name}\n"
    )
    sums_path = directorio / "analisis_quinta_instancia_c250.SHA256SUMS.txt"
    sums_path.write_bytes(sumas.encode("utf-8"))
    return [json_path, md_path, sums_path]


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main() -> int:
    archivos = {
        "data/corpus_resultados_telefonia.json": RAIZ / "data/corpus_resultados_telefonia.json",
        "data/corpus_evaluacion_pseudonimizado.json": RAIZ / "data/corpus_evaluacion_pseudonimizado.json",
    }
    telefonia = json.loads(
        archivos["data/corpus_resultados_telefonia.json"].read_text(encoding="utf-8")
    )
    corpus = json.loads(
        archivos["data/corpus_evaluacion_pseudonimizado.json"].read_text(encoding="utf-8")
    )
    resultado = construir_resultado(
        filas_telefonia=telefonia,
        casos=corpus["casos"],
        rutas_entrada={ruta: _sha256(p) for ruta, p in archivos.items()},
    )
    salidas = escribir_salidas(resultado, Path(__file__).resolve().parent)
    for ruta in salidas:
        print(f"{_sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
