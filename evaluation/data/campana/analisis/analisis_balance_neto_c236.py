#!/usr/bin/env python3
"""Balance neto acotado y umbral a priori: recomputo offline con el termino de revision (c-236).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica, no reentrena y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es sucesor y aditivo de c-222: la seccion
nueva del memo registra sus cifras y NO reemplaza ningun valor de las secciones 3.1 a 3.45
ni edita `analisis_costo_derivacion_c220.*` ni `analisis_balance_neto_c222.*`.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/analisis/analisis_costo_derivacion_c220.json`: el costo medido
  `c = 69,5074` s y su IC 95 % `[33,42; 106,56]` s, y el termino de revision
  (`termino_revision`: media `22,0632` s, mediana `9,9565` s, `n = 138`); el grupo
  `cambio_sector=false` da la `r` de las confirmaciones (sin solapamiento).
- `evaluation/data/campana/analisis/analisis_balance_neto_c222.json`: la referencia comun
  (`N`, `dt`, `e_aut`, `e_man` y su IC), el `c` medido y el balance sin revision (`+30,6`).
- `evaluation/data/campana/intervenciones.csv`: las 138 duraciones con `duracion_s` (para
  remuestrear `r` y reproducir su media).
- `evaluation/data/campana/plantilla_etiquetado.csv` y
  `evaluation/data/campana/predicciones_in_sample.json`: las fuentes por caso con las que
  c-207/c-222 construyeron la referencia comun (emparejamiento por caso, reutilizado).

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo, la regla de eleccion y los parametros se fijan aqui antes de generar cualquier
salida. El preregistro NO es ciego: el valor central ya es conocido (el tribunal lo
publico: `+18,7`), y los anclajes de c-220 y c-222 ya se conocian; lo que no se habia
observado es la distribucion bootstrap recomputada con el termino de revision. Se informan
TODOS los resultados, favorables o no.

1. Formula (D1). `B_r = (N/3600) x [dt - rho x r - (e_aut - e_man) x c]` y
   `a*_r = 1 - e_man - (dt - rho x r) / c`. El termino de revision solo resta del lado
   automatizado: el flujo manual no tiene una revision equivalente posterior al registro.

2. Tasa de revision (D1). `rho = 147/200 = 0,735` es la proporcion de casos que reciben
   revision humana en la configuracion evaluada (regla VIS-005; `07-resultados.tex`). `rho`
   depende de la mezcla de canales del corpus y de esa regla: un universo con otra mezcla
   tiene otro `rho`.

3. Eleccion de `r` (D2). Se usa la MEDIA (`22,0632` s), fijada aqui antes de generar las
   salidas: `B` agrega tiempo sobre `N x rho` revisiones, y el estimador del total es
   `N x rho x media`. La mediana (`9,9565` s), con una distribucion sesgada a derecha
   (desvio `43,40` > media), subestimaria el total; se informa solo como sensibilidad.

4. Lectura (D5). `B_r` se informa como COTA SUPERIOR del balance respecto del tramo de
   reanudacion no medido: `c` cubre solo el tramo activo y es una cota inferior del costo.
   El signo del balance real NO se declara fijado: depende del tramo de reanudacion no
   medido. Se informa la rejilla de 5, 10 y 15 minutos con revision como sensibilidad al
   tramo no medido, y el costo de equilibrio `c* = (dt - rho x r) / (e_aut - e_man)` con su
   margen del tramo no medido.

5. Incertidumbre (D4). (a) Intervalo condicional con `c` y `rho` fijos: bootstrap percentil
   al 95 %, `B = 2000`, semilla `20261021`; se remuestrean de forma independiente los casos
   de la referencia comun (para `e_aut - e_man`, reutilizando el emparejamiento de c-222) y
   las 138 duraciones (para `r`). (b) Cota combinada por suma de extremos sobre 16 esquinas:
   `rho` en Wilson al 95 % de `147/200`, `r` en su IC de la media, `e_aut - e_man` en su IC y
   `c` en su IC. Es la cota exterior conservadora del tramo activo medido, no del balance
   real.

6. Anclajes que abortan antes de escribir (sin salidas): el balance sin revision `+30,64`
   de c-222, el costo medido `69,51` s, la `r` media `22,06` s con `n = 138` y la tasa de
   revision `147/200`. Los insumos se leen de los artefactos versionados, no de constantes.

7. No-incorporacion. NO se incluye ninguna cifra fuera de muestra (ni `+13,2`, ni `-28,9`,
   ni `+28,2`, ni `+25,1`): c-235 retiro esa validacion y este change no la restituye.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_balance_neto_c236.json`, `.md` y
`.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte a
byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_balance_neto_c236.py
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import random
import statistics
import sys
from typing import Optional, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[4]
SALIDA = pathlib.Path(__file__).resolve().parent
for _ruta in (ROOT, SALIDA):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

from evaluation.metrics import (  # noqa: E402
    intervalo_wilson,
    percentil_intervalo,
    remuestreos_indices,
)

# Reutiliza el emparejamiento, los lectores y el SHA-256 de c-222 (no se copian).
from analisis_balance_neto_c222 import (  # noqa: E402
    _estadisticos,
    cargar_planilla,
    cargar_predicciones_caso,
    casos_referencia_comun,
    sha256,
)

CAMPANA = ROOT / "evaluation/data/campana"
RUTA_C220 = SALIDA / "analisis_costo_derivacion_c220.json"
RUTA_C222 = SALIDA / "analisis_balance_neto_c222.json"
RUTA_INTERVENCIONES = CAMPANA / "intervenciones.csv"
RUTA_PLANILLA = CAMPANA / "plantilla_etiquetado.csv"
RUTA_PRED_IN_SAMPLE = CAMPANA / "predicciones_in_sample.json"

NOMBRE_BASE = "analisis_balance_neto_c236"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

# Parametros fijados en el preregistro (docstring).
SEMILLA = 20261021
REMUESTREOS = 2000
NIVEL = 0.95
C_GRILLA_S = (300.0, 600.0, 900.0)
C_GRILLA_MIN = (5, 10, 15)
N_REVISIONES = 147
N_TASA = 200
RHO = N_REVISIONES / N_TASA

# Anclajes canonicos que deben reproducirse antes de escribir.
ANCLA_BALANCE_C222 = 30.64
ANCLA_C_S = 69.51
ANCLA_R = 22.06
ANCLA_N_DURACIONES = 138
ANCLA_RHO = N_REVISIONES / N_TASA

DECIMALES_TESIS = 1
DECIMALES_PORCENTAJE = 1

ROTULO_COTA_SUPERIOR = "cota superior respecto del tramo de reanudacion no medido"
ROTULO_COTA_COMBINADA = "cota combinada del tramo activo medido (no del balance real)"
ROTULO_TRAMO_NO_MEDIDO = "sensibilidad al tramo no medido (reanudacion)"


class EntradaInconsistente(ValueError):
    """Los conteos o los identificadores no coinciden con lo versionado."""


class AnclaNoReproducida(ValueError):
    """Un anclaje canonico no se reproduce: no se escribe ninguna salida."""


def _media(valores: Sequence[float]) -> float:
    """Media aritmetica de `valores` (falla si la secuencia esta vacia)."""
    return statistics.fmean(valores)


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def balance_neto_con_revision(
    n: float,
    delta_t: float,
    rho: float,
    r: float,
    e_aut: float,
    e_man: float,
    c_s: float,
) -> float:
    """Balance neto trimestral con revision: `(N/3600) x [dt - rho x r - (e_aut - e_man) x c]`."""
    return (n / 3600.0) * (delta_t - rho * r - (e_aut - e_man) * c_s)


def exactitud_equilibrio_con_revision(
    e_man: float,
    delta_t: float,
    rho: float,
    r: float,
    c_s: float,
) -> float:
    """Exactitud minima de equilibrio con revision: `a* = 1 - e_man - (dt - rho x r) / c`."""
    return 1.0 - e_man - (delta_t - rho * r) / c_s


def costo_equilibrio(
    delta_t: float,
    rho: float,
    r: float,
    diferencia: float,
) -> Optional[float]:
    """Costo de equilibrio `c* = (dt - rho x r) / (e_aut - e_man)`.

    Devuelve `None` si `diferencia <= 0`: con un error manual mayor o igual que el
    automatizado no existe un costo finito que anule el balance.
    """
    if diferencia <= 0.0:
        return None
    return (delta_t - rho * r) / diferencia


def margen_tramo_no_medido(
    delta_t: float,
    rho: float,
    r: float,
    diferencia: float,
    c_s: float,
) -> Optional[float]:
    """Margen del tramo no medido: `c* - c`. `None` si no hay `c*` finito."""
    c_estrella = costo_equilibrio(delta_t, rho, r, diferencia)
    if c_estrella is None:
        return None
    return c_estrella - c_s


def suma_de_extremos(valores: Sequence[float]) -> tuple[float, float]:
    """Cota exterior por suma de extremos: el minimo y el maximo de un conjunto de valores."""
    if not valores:
        raise ValueError("la suma de extremos exige al menos un valor")
    return min(valores), max(valores)


def cota_combinada(
    n: float,
    delta_t: float,
    rho_ic: Sequence[float],
    r_ic: Sequence[float],
    diferencia_ic: Sequence[float],
    c_ic: Sequence[float],
) -> tuple[float, float]:
    """Cota combinada de `B_r` sobre las 16 esquinas (`rho` x `r` x `diferencia` x `c`)."""
    esquinas = [
        balance_neto_con_revision(n, delta_t, rho, r, diferencia, 0.0, c_s)
        for rho in rho_ic
        for r in r_ic
        for diferencia in diferencia_ic
        for c_s in c_ic
    ]
    return suma_de_extremos(esquinas)


def intervalos_condicionales_con_revision(
    casos: Sequence[tuple[int, int, int]],
    duraciones: Sequence[float],
    n: float,
    delta_t: float,
    rho: float,
    costos: Sequence[float],
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
    nivel: float = NIVEL,
) -> dict:
    """`B_r` y `a*_r` (punto e IC condicional con `c` y `rho` fijos) por costo.

    Bootstrap percentil con remuestreo INDEPENDIENTE: los casos de la referencia comun
    (para `e_aut - e_man`, reutilizando el emparejamiento de c-222) y las duraciones (para
    `r`). Un unico generador `random.Random(semilla)` produce primero las tandas de casos y
    despues las de duraciones, de modo que la corrida es reproducible byte a byte.
    """
    if not casos:
        raise ValueError("no hay casos de la referencia comun")
    if not duraciones:
        raise ValueError("no hay duraciones de revision")
    generador = random.Random(semilla)
    idx_casos = list(remuestreos_indices(generador, len(casos), remuestreos))
    idx_duraciones = list(remuestreos_indices(generador, len(duraciones), remuestreos))
    e_aut, e_man = _estadisticos(casos, range(len(casos)))
    r = _media(duraciones)
    por_costo = []
    for c_s in costos:
        balances: list[float] = []
        exactitudes: list[float] = []
        for idx_caso, idx_duracion in zip(idx_casos, idx_duraciones):
            e_aut_r, e_man_r = _estadisticos(casos, idx_caso)
            r_remuestra = _media([duraciones[i] for i in idx_duracion])
            balances.append(
                balance_neto_con_revision(n, delta_t, rho, r_remuestra, e_aut_r, e_man_r, c_s)
            )
            exactitudes.append(
                exactitud_equilibrio_con_revision(e_man_r, delta_t, rho, r_remuestra, c_s)
            )
        inferior, superior = percentil_intervalo(balances, nivel)
        a_inferior, a_superior = percentil_intervalo(exactitudes, nivel)
        por_costo.append(
            {
                "c_s": c_s,
                "balance": balance_neto_con_revision(n, delta_t, rho, r, e_aut, e_man, c_s),
                "balance_ic": [inferior, superior],
                "a_estrella": exactitud_equilibrio_con_revision(e_man, delta_t, rho, r, c_s),
                "a_estrella_ic": [a_inferior, a_superior],
            }
        )
    return {
        "e_aut": e_aut,
        "e_man": e_man,
        "r": r,
        "por_costo": por_costo,
        "metodo": (
            "bootstrap percentil al 95 % con c y rho fijos; remuestrea de forma independiente "
            "los casos de la referencia comun (emparejamiento de c-222) y las 138 duraciones"
        ),
        "nivel_confianza": nivel,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }


# ---------------------------------------------------------------------------
# Lectura de entradas
# ---------------------------------------------------------------------------
def _leer_json(ruta: pathlib.Path) -> dict:
    return json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))


def cargar_duraciones_revision(ruta: pathlib.Path = RUTA_INTERVENCIONES) -> list[float]:
    """Duraciones `duracion_s` con dato (las 138 intervenciones con `duracion_s`)."""
    duraciones: list[float] = []
    with pathlib.Path(ruta).open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            crudo = fila["duracion_s"].strip()
            if crudo:
                duraciones.append(float(crudo))
    return duraciones


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def _redondear(valor: float, decimales: int) -> float:
    return round(valor, decimales)


def _porcentaje(valor: float, decimales: int = DECIMALES_PORCENTAJE) -> float:
    return _redondear(valor * 100.0, decimales)


def _sensibilidad(
    n: float,
    delta_t: float,
    e_aut: float,
    e_man: float,
    c_s: float,
    *,
    rho: float,
    r: float,
    rotulo: str,
) -> dict:
    """Balance puntual de una variante de sensibilidad (`r` o `rho`)."""
    return {
        "rho": rho,
        "r_s": r,
        "balance": balance_neto_con_revision(n, delta_t, rho, r, e_aut, e_man, c_s),
        "rotulo": rotulo,
    }


def construir_documento(
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Construye el documento completo; aborta si un anclaje no se reproduce."""
    c220 = _leer_json(RUTA_C220)
    c222 = _leer_json(RUTA_C222)

    n = c222["insumos"]["n"]
    delta_t = c222["insumos"]["delta_t_s"]
    e_aut = c222["insumos"]["e_aut"]
    e_man = c222["insumos"]["e_man"]
    diferencia = c222["insumos"]["diferencia"]
    diferencia_ic = c222["insumos"]["diferencia_ic"]
    balance_sin_revision_artefacto = c222["condicional_c_fijo"]["balance"]
    c_s = c220["composicion"]["escenarios"]["bajo"]["punto"]
    c_ic = c220["composicion"]["escenarios"]["bajo"]["intervalo"]
    r_artefacto = c220["termino_revision"]["media"]
    r_mediana = c220["termino_revision"]["mediana"]
    n_revision = c220["termino_revision"]["n"]
    r_sin_solapamiento = c220["grupos_cambio_sector"]["false"]["media"]

    duraciones = cargar_duraciones_revision()
    r = _media(duraciones)

    # --- Anclajes baratos (abortan antes del bootstrap) ---
    problemas: list[str] = []
    if _redondear(balance_sin_revision_artefacto, 2) != ANCLA_BALANCE_C222:
        problemas.append(
            f"balance sin revision de c-222 = {_redondear(balance_sin_revision_artefacto, 2)} "
            f"!= {ANCLA_BALANCE_C222}"
        )
    balance_sin_revision = balance_neto_con_revision(n, delta_t, 0.0, 0.0, e_aut, e_man, c_s)
    if _redondear(balance_sin_revision, 2) != ANCLA_BALANCE_C222:
        problemas.append(
            f"balance sin revision recomputado = {_redondear(balance_sin_revision, 2)} "
            f"!= {ANCLA_BALANCE_C222}"
        )
    if _redondear(c_s, 2) != ANCLA_C_S:
        problemas.append(f"c medido = {_redondear(c_s, 2)} != {ANCLA_C_S}")
    if _redondear(r, 2) != ANCLA_R:
        problemas.append(f"r media = {_redondear(r, 2)} != {ANCLA_R}")
    if len(duraciones) != ANCLA_N_DURACIONES:
        problemas.append(f"duraciones = {len(duraciones)} != {ANCLA_N_DURACIONES}")
    if n_revision != ANCLA_N_DURACIONES:
        problemas.append(f"n de revision de c-220 = {n_revision} != {ANCLA_N_DURACIONES}")
    if abs(r - r_artefacto) > 1e-9:
        problemas.append(f"r media = {r} != termino_revision.media de c-220 = {r_artefacto}")
    if _redondear(RHO, 4) != _redondear(ANCLA_RHO, 4):
        problemas.append(f"rho = {RHO} != {ANCLA_RHO}")
    if sha256(RUTA_INTERVENCIONES, normalizar_lf=False) != c220["entradas_sha256"]["intervenciones.csv"]:
        problemas.append("intervenciones.csv no coincide con el SHA-256 registrado por c-220")
    if problemas:
        raise AnclaNoReproducida("; ".join(problemas))

    # --- Referencia comun (emparejamiento reutilizado de c-222) ---
    planilla = cargar_planilla()
    predichos = cargar_predicciones_caso()
    casos = casos_referencia_comun(planilla, predichos)
    if len(casos) != ANCLA_N_DURACIONES:
        problemas.append(f"casos de la referencia comun = {len(casos)} != {ANCLA_N_DURACIONES}")

    # --- Bootstrap condicional (rejilla + lectura central) ---
    costos = (*C_GRILLA_S, c_s)
    resultado = intervalos_condicionales_con_revision(
        casos, duraciones, n, delta_t, RHO, costos, remuestreos=remuestreos, semilla=semilla
    )
    grid = resultado["por_costo"][: len(C_GRILLA_S)]
    medida = resultado["por_costo"][len(C_GRILLA_S)]

    rho_ic = tuple(float(v) for v in intervalo_wilson(N_REVISIONES, N_TASA, NIVEL))
    r_ic = tuple(float(v) for v in c220["termino_revision"]["ic_media"])
    combinado = cota_combinada(n, delta_t, rho_ic, r_ic, diferencia_ic, c_ic)

    c_estrella = costo_equilibrio(delta_t, RHO, r, diferencia)
    margen = margen_tramo_no_medido(delta_t, RHO, r, diferencia, c_s)
    c_estrella_alta = costo_equilibrio(delta_t, RHO, r, diferencia_ic[1])
    margen_alta = margen_tramo_no_medido(delta_t, RHO, r, diferencia_ic[1], c_s)

    sensibilidad_al_tramo = [
        {
            "c_min": c_min,
            "c_s": fila["c_s"],
            "balance": fila["balance"],
            "balance_ic": fila["balance_ic"],
            "a_estrella": fila["a_estrella"],
            "a_estrella_ic": fila["a_estrella_ic"],
            "estado": "condicional",
            "rotulo": ROTULO_TRAMO_NO_MEDIDO,
        }
        for c_min, fila in zip(C_GRILLA_MIN, grid)
    ]

    entradas_sha = {
        ruta.name: sha256(ruta)
        for ruta in (
            RUTA_C220,
            RUTA_C222,
            RUTA_INTERVENCIONES,
            RUTA_PLANILLA,
            RUTA_PRED_IN_SAMPLE,
        )
    }

    return {
        "change": "c-236-acotar-el-balance-neto-y-declarar-el-umbral-a-priori",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "Solo lectura, offline y determinista; reutiliza evaluation.metrics "
            "(remuestreos_indices, percentil_intervalo, intervalo_wilson) y el "
            "emparejamiento de c-222; sin red ni Gemini. El balance con el termino de "
            "revision se informa como cota superior respecto del tramo de reanudacion no "
            "medido; el costo medido es una cota inferior."
        ),
        "preregistro": {
            "fijado_en_docstring": True,
            "ciego": False,
            "declaracion": (
                "El metodo, la regla de eleccion de r (media) y los parametros se fijaron en "
                "el docstring antes de generar las salidas. El preregistro NO fue ciego: el "
                "valor central ya lo publico el tribunal y los anclajes de c-220 y c-222 ya "
                "se conocian; no se habia observado la distribucion bootstrap recomputada con "
                "el termino de revision."
            ),
        },
        "parametros": {
            "B": remuestreos,
            "semilla": semilla,
            "nivel_confianza": NIVEL,
            "grilla_c_min": list(C_GRILLA_MIN),
            "rho": RHO,
            "n_revisiones": N_REVISIONES,
            "n_tasa": N_TASA,
        },
        "entradas_sha256": entradas_sha,
        "anclajes": {
            "balance_sin_revision": balance_sin_revision_artefacto,
            "balance_sin_revision_redondeado": _redondear(balance_sin_revision_artefacto, 2),
            "c_s": c_s,
            "c_s_redondeado": _redondear(c_s, 2),
            "r_media": r,
            "r_media_redondeada": _redondear(r, 2),
            "n_duraciones": len(duraciones),
            "rho": RHO,
        },
        "insumos": {
            "n": n,
            "delta_t_s": delta_t,
            "e_aut": e_aut,
            "e_man": e_man,
            "diferencia": diferencia,
            "diferencia_ic": list(diferencia_ic),
            "c_s": c_s,
            "c_ic": list(c_ic),
            "rho": RHO,
            "r_s": r,
            "r_mediana": r_mediana,
            "r_sin_solapamiento": r_sin_solapamiento,
            "n_revision": n_revision,
            "fuente_r": "seccion 3.31 (c-220); media de las 138 duraciones con duracion_s",
            "fuente_rho": "147 de 200 casos revisados (regla VIS-005; 07-resultados.tex)",
            "fuente_c": "seccion 3.31 (c-220); tramo activo medido, cota inferior del costo",
        },
        "lectura_central": {
            "rotulo": ROTULO_COTA_SUPERIOR,
            "balance": medida["balance"],
            "balance_ic": medida["balance_ic"],
            "a_estrella": medida["a_estrella"],
            "a_estrella_ic": medida["a_estrella_ic"],
            "cota_combinada": list(combinado),
            "cota_combinada_rotulo": ROTULO_COTA_COMBINADA,
            "metodo": resultado["metodo"],
        },
        "costo_equilibrio": {
            "c_s": c_estrella,
            "c_min": None if c_estrella is None else c_estrella / 60.0,
            "margen_s": margen,
            "margen_min": None if margen is None else margen / 60.0,
            "c_s_con_diferencia_alta": c_estrella_alta,
            "margen_con_diferencia_alta_s": margen_alta,
            "metodo": "c* = (dt - rho x r) / (e_aut - e_man); margen = c* - c medido",
        },
        "sensibilidad_al_tramo_no_medido": sensibilidad_al_tramo,
        "sensibilidades": {
            "r_mediana": _sensibilidad(
                n, delta_t, e_aut, e_man, c_s,
                rho=RHO, r=r_mediana, rotulo="r mediana (subestima el total; solo sensibilidad)",
            ),
            "r_sin_solapamiento": _sensibilidad(
                n, delta_t, e_aut, e_man, c_s,
                rho=RHO, r=r_sin_solapamiento,
                rotulo="r de las confirmaciones (D3; variante sin solapamiento)",
            ),
            "rho_uno": _sensibilidad(
                n, delta_t, e_aut, e_man, c_s,
                rho=1.0, r=r, rotulo="rho = 1 (aplica r a todo N; sobreestima la revision)",
            ),
        },
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "nueva (aditiva; primer numero libre al aplicar)",
            "declaracion": (
                "Las cifras de este analisis son aditivas: van a la seccion nueva del memo y "
                "no reemplazan ningun valor de las secciones 3.1 a 3.45; no cambian el umbral "
                "del 85 %, ni los artefactos de c-220 y c-222, ni el corpus. El signo del "
                "balance real no se declara fijado: depende del tramo de reanudacion no medido."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------
def _p(valor, decimales: int = 4) -> str:
    if valor is None:
        return "n/d"
    return f"{valor:.{decimales}f}".replace(".", ",")


def _ic(par) -> str:
    if not par:
        return "n/d"
    return f"[{_p(par[0])}; {_p(par[1])}]"


def _clave_json() -> dict:
    return {"ensure_ascii": False, "indent": 2, "sort_keys": True, "allow_nan": False}


def renderizar(doc: dict) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF, UTF-8 sin BOM."""
    texto_json = json.dumps(doc, **_clave_json()) + "\n"
    ins = doc["insumos"]
    lectura = doc["lectura_central"]
    costo = doc["costo_equilibrio"]
    rejilla = doc["sensibilidad_al_tramo_no_medido"]
    sens = doc["sensibilidades"]
    lineas = [
        "# Balance neto acotado con el termino de revision (c-236)",
        "",
        f"Solo lectura, offline y determinista; sin red ni Gemini. {doc['aditivo']['declaracion']}",
        "",
        "## Preregistro",
        "",
        f"- Fijado en el docstring antes de generar las salidas: "
        f"{doc['preregistro']['fijado_en_docstring']}.",
        f"- Ciego: {doc['preregistro']['ciego']}. {doc['preregistro']['declaracion']}",
        f"- Remuestreos: {doc['parametros']['B']}; semilla: {doc['parametros']['semilla']}; "
        f"nivel: {_p(doc['parametros']['nivel_confianza'], 2)}.",
        "",
        "## Anclajes reproducidos antes de escribir",
        "",
        f"- Balance sin revision de c-222: `{_p(doc['anclajes']['balance_sin_revision_redondeado'], 2)}` "
        "horas-persona por trimestre.",
        f"- Costo medido: `c = {_p(doc['anclajes']['c_s'], 2)}` s.",
        f"- `r` media: `{_p(doc['anclajes']['r_media'], 2)}` s sobre `{doc['anclajes']['n_duraciones']}` "
        "duraciones.",
        f"- Tasa de revision: `rho = {_p(doc['anclajes']['rho'], 3)}` (`147/200`).",
        "",
        "## Insumos",
        "",
        f"- `N = {ins['n']}`; `dt = {_p(ins['delta_t_s'], 2)}` s.",
        f"- `e_aut = {_p(ins['e_aut'])}`; `e_man = {_p(ins['e_man'])}`.",
        f"- `e_aut - e_man = {_p(ins['diferencia'])}`, IC 95 % {_ic(ins['diferencia_ic'])}.",
        f"- `rho = {_p(ins['rho'], 3)}` ({ins['fuente_rho']}).",
        f"- `r = {_p(ins['r_s'], 4)}` s (media de {ins['n_revision']} duraciones; {ins['fuente_r']}).",
        f"- `c = {_p(ins['c_s'], 2)}` s, IC 95 % {_ic(ins['c_ic'])} ({ins['fuente_c']}).",
        "",
        "## Lectura central (cota superior con el tramo activo medido)",
        "",
        f"- Forma: `B_r = (N/3.600) x [dt - rho x r - (e_aut - e_man) x c]`; "
        "`a*_r = 1 - e_man - (dt - rho x r) / c`.",
        f"- `B_r = {_p(lectura['balance'], 1)}` horas-persona por trimestre; intervalo "
        f"condicional ({lectura['metodo']}) 95 % {_ic(lectura['balance_ic'])}.",
        f"- `a*_r = {_p(lectura['a_estrella'] * 100, 1)}` %; IC 95 % "
        f"{_ic([v * 100 for v in lectura['a_estrella_ic']])} %.",
        f"- Cota combinada 95 % {_ic(lectura['cota_combinada'])} "
        f"({lectura['cota_combinada_rotulo']}).",
        f"- Rotulo: {lectura['rotulo']}.",
        "",
        "## Costo de equilibrio y margen del tramo no medido",
        "",
        f"- `c* = {_p(costo['c_s'], 1)}` s (`{_p(costo['c_min'], 1)}` min).",
        f"- Margen del tramo no medido: `{_p(costo['margen_s'], 1)}` s "
        f"(`{_p(costo['margen_min'], 1)}` min).",
        f"- `c*` con `e_aut - e_man = {_p(ins['diferencia_ic'][1])}`: "
        f"`{_p(costo['c_s_con_diferencia_alta'], 1)}` s; margen "
        f"`{_p(costo['margen_con_diferencia_alta_s'], 1)}` s.",
        "",
        "## Sensibilidad al tramo no medido (rejilla de 5, 10 y 15 minutos con revision)",
        "",
        "| `c` (min) | `B_r` (h-persona) | IC 95 % de `B_r` | `a*_r` (%) | IC 95 % de `a*_r` (%) | Estado |",
        "|---|---|---|---|---|---|",
    ]
    for fila in rejilla:
        lineas.append(
            f"| {fila['c_min']} | {_p(fila['balance'], 2)} | {_ic(fila['balance_ic'])} | "
            f"{_p(fila['a_estrella'] * 100, 2)} | "
            f"{_ic([v * 100 for v in fila['a_estrella_ic']])} | {fila['estado']} |"
        )
    lineas += [
        "",
        f"- Rotulo: {ROTULO_TRAMO_NO_MEDIDO}. No es la lectura central; depende del tramo no medido.",
        "",
        "## Sensibilidades de `r` y de `rho`",
        "",
        f"- `r` mediana: `B_r = {_p(sens['r_mediana']['balance'], 2)}` "
        f"({sens['r_mediana']['rotulo']}).",
        f"- `r` sin solapamiento: `B_r = {_p(sens['r_sin_solapamiento']['balance'], 2)}` "
        f"({sens['r_sin_solapamiento']['rotulo']}).",
        f"- `rho = 1`: `B_r = {_p(sens['rho_uno']['balance'], 2)}` "
        f"({sens['rho_uno']['rotulo']}).",
        "",
        "## Entradas (SHA-256)",
        "",
    ]
    for nombre, huella in doc["entradas_sha256"].items():
        lineas.append(f"- `{nombre}`: `{huella}`")
    lineas.append("")
    return texto_json, "\n".join(lineas) + "\n"


def escribir(
    doc: dict,
    directorio: pathlib.Path = SALIDA,
    nombre_base: str = NOMBRE_BASE,
) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for nombre, texto in (
        (f"{nombre_base}.json", texto_json),
        (f"{nombre_base}.md", texto_md),
    ):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}\n" for ruta in rutas)
    ruta_sumas = directorio / f"{nombre_base}.SHA256SUMS.txt"
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(
    salida: pathlib.Path = SALIDA,
    nombre_base: str = NOMBRE_BASE,
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> list[pathlib.Path]:
    """Construye y escribe el analisis; no escribe si un anclaje no se reproduce."""
    doc = construir_documento(remuestreos=remuestreos, semilla=semilla)
    return escribir(doc, salida, nombre_base=nombre_base)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Balance neto acotado con el termino de revision (c-236)"
    )
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--nombre", default=NOMBRE_BASE)
    parser.add_argument("--remuestreos", type=int, default=REMUESTREOS)
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    args = parser.parse_args(argv)
    try:
        rutas = ejecutar(
            args.salida,
            args.nombre,
            remuestreos=args.remuestreos,
            semilla=args.semilla,
        )
    except (AnclaNoReproducida, EntradaInconsistente, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for ruta in rutas:
        print(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
