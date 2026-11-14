#!/usr/bin/env python3
"""Recomputo del balance neto con el costo medido (c-222).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica, no reentrena y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es aditivo: la seccion nueva del memo
registra sus cifras y NO reemplaza ningun valor de las secciones 3.1 a 3.32.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/analisis/analisis_costo_derivacion_c220.json`: el costo medido
  `c = 69,5074` s y su IC 95 % `[33,42; 106,56]` s (memo 3.31).
- `evaluation/data/campana/analisis/analisis_dictamen_c207.json`: la referencia comun de
  la seccion 3.21 (`balance_neto_referencia_comun`): `N`, `dt`, `e_aut`, `e_man` y el IC de
  `e_aut - e_man`.
- `evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.json`: la
  sensibilidad mixta `+28,2 / +25,1` (memo 3.32), citada y NO promovida.
- `evaluation/data/campana/plantilla_etiquetado.csv` y
  `evaluation/data/campana/predicciones_in_sample.json`: las fuentes por caso con las que
  c-207 construyo la referencia comun (emparejamiento por caso).

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo y los parametros se fijan aqui antes de generar cualquier salida. El
preregistro NO es ciego: las celdas del balance de la seccion 3.21, el `c` medido y los
anclajes ya se conocian; lo que no se habia observado es la distribucion bootstrap
recomputada con el `c` fijo. Se informan TODOS los resultados, favorables o no.

1. Referencia base (D2). La lectura central del balance es la referencia comun de la
   seccion 3.21 (consenso `E1`/`E2`: `e_aut = 28/138`, `e_man = 26/151`) con el `c` medido
   `69,5074` s de la seccion 3.31. No se promueve la sensibilidad mixta de c-221.

2. Intervalo condicional con `c` fijo (D1). Bootstrap percentil por caso al 95 % (`B = 2000`,
   semilla `20261021`) que remuestrea los casos de la referencia y empareja cada derivacion
   manual con su caso; `c` se mantiene constante. Se recomputa (no se interpola): el IC de
   `B` de la 3.21 depende del emparejamiento por caso.

3. Intervalo combinado (D1). Suma de extremos (aritmetica de intervalos): `B` se evalua en
   las cuatro esquinas `c in {lo, hi}` x `(e_aut - e_man) in {lo, hi}` y se toma el minimo y
   el maximo. Cota exterior conservadora; no asume independencia. `a*` se deriva de la misma
   mecanica.

4. Anclajes que abortan antes de escribir (exit distinto de cero, sin salidas): las celdas
   `+25,4 / +18,7 / +11,9` horas-persona por trimestre de la 3.21, el `69,51` s de la 3.31 y
   los tres IC de la 3.21 `[+8,6; +42,4]`, `[-15,0; +52,5]`, `[-38,6; +62,7]`. Los insumos
   (`N`, `dt`, `e_aut`, `e_man`, `c` y sus intervalos) se leen de los artefactos versionados,
   no de constantes.

5. Grilla superada. La rejilla de 5, 10 y 15 minutos se conserva con sus cifras y se rotula
   como sensibilidad del supuesto superado (estado `condicional`). La sensibilidad mixta de
   c-221 (`+28,2 / +25,1`) se cita y NO se promueve.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_balance_neto_c222.json`, `.md` y
`.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte a
byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_balance_neto_c222.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import random
import sys
from typing import Mapping, Optional, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import REFERENCIA_CONSENSO_NUEVO, construir_referencia  # noqa: E402
from evaluation.metrics import percentil_intervalo, remuestreos_indices  # noqa: E402
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_C220 = SALIDA / "analisis_costo_derivacion_c220.json"
RUTA_C207 = SALIDA / "analisis_dictamen_c207.json"
RUTA_C221 = SALIDA / "analisis_propagacion_arbitraje_c221.json"
RUTA_PLANILLA = CAMPANA / "plantilla_etiquetado.csv"
RUTA_PRED_IN_SAMPLE = CAMPANA / "predicciones_in_sample.json"

NOMBRE_BASE = "analisis_balance_neto_c222"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

# Parametros fijados en el preregistro (docstring).
SEMILLA = 20261021
REMUESTREOS = 2000
NIVEL = 0.95
C_GRILLA_S = (300.0, 600.0, 900.0)
C_GRILLA_MIN = (5, 10, 15)
TAREA_BRAZO_MANUAL = "brazo_manual"

# Anclajes canonicos que deben reproducirse antes de escribir.
ANCLA_C_S = 69.51
ANCLA_BALANCE_REFERENCIA_COMUN = (25.4, 18.7, 11.9)
ANCLA_BALANCE_IC = ((8.6, 42.4), (-15.0, 52.5), (-38.6, 62.7))
ANCLA_CONTEOS = {
    "casos": 138,
    "errores_automatizado": 28,
    "errores_manual": 26,
    "derivaciones_manual": 151,
}

DECIMALES_TESIS = 1
DECIMALES_PORCENTAJE = 1


class EntradaInconsistente(ValueError):
    """Los conteos o los identificadores no coinciden con lo versionado."""


class AnclaNoReproducida(ValueError):
    """Un anclaje canonico no se reproduce: no se escribe ninguna salida."""


def sha256(ruta: pathlib.Path, *, normalizar_lf: bool = True) -> str:
    """SHA-256 del archivo; con `normalizar_lf` colapsa CRLF a LF (como c-213/c-214)."""
    datos = pathlib.Path(ruta).read_bytes()
    if normalizar_lf:
        datos = datos.replace(b"\r\n", b"\n")
    return hashlib.sha256(datos).hexdigest()


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def balance_neto(n: float, delta_t: float, e_aut: float, e_man: float, c_s: float) -> float:
    """Balance neto trimestral en horas-persona: `(N/3600) * [dt - (e_aut - e_man) * c]`."""
    return (n / 3600.0) * (delta_t - (e_aut - e_man) * c_s)


def exactitud_equilibrio(e_man: float, delta_t: float, c_s: float) -> float:
    """Exactitud minima de equilibrio: `a* = 1 - e_man - dt / c`."""
    return 1.0 - e_man - delta_t / c_s


def _estadisticos(
    casos: Sequence[tuple[int, int, int]], indices: Sequence[int]
) -> tuple[float, float]:
    """`(e_aut, e_man)` de una remuestra; `e_aut` por caso, `e_man` por derivacion."""
    n = len(indices)
    derivaciones = sum(casos[i][2] for i in indices)
    e_aut = sum(casos[i][0] for i in indices) / n
    e_man = sum(casos[i][1] for i in indices) / derivaciones
    return e_aut, e_man


def _validar_casos(casos: Sequence[tuple[int, int, int]]) -> None:
    if not casos:
        raise ValueError("no hay casos de la referencia comun")
    if any(derivaciones < 1 for _, _, derivaciones in casos):
        raise ValueError("todo caso debe tener al menos una derivacion manual")


def emparejar_referencia_manual(
    referencia: Mapping[str, str],
    filas_manual: Sequence[Mapping[str, str]],
    predichos: Mapping[str, str],
) -> list[tuple[int, int, int]]:
    """Tuplas `(error_aut, errores_man, derivaciones_man)` por caso, en orden de id.

    `e_aut` se cuenta por caso; `e_man` se cuenta por derivacion: cada derivacion del
    brazo manual se empareja con su caso. Los casos de la referencia sin derivaciones
    abortan (no se imputa).
    """
    por_caso: dict[str, tuple[int, int]] = {}
    for fila in filas_manual:
        caso = fila["id_caso"]
        if caso not in referencia:
            continue
        errores, derivaciones = por_caso.get(caso, (0, 0))
        fallo = int(fila["sector_etiquetado"] != referencia[caso])
        por_caso[caso] = (errores + fallo, derivaciones + 1)
    faltan = sorted(set(referencia) - set(por_caso))
    if faltan:
        raise EntradaInconsistente(
            f"casos de la referencia sin derivaciones del brazo manual: {faltan[:3]}"
        )
    return [
        (int(predichos[caso] != referencia[caso]), *por_caso[caso]) for caso in sorted(referencia)
    ]


def bootstrap_casos(
    casos: Sequence[tuple[int, int, int]],
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> list[tuple[float, float]]:
    """Remuestras bootstrap `(e_aut, e_man)` que emparejan cada derivacion con su caso."""
    _validar_casos(casos)
    generador = random.Random(semilla)
    return [
        _estadisticos(casos, indices)
        for indices in remuestreos_indices(generador, len(casos), remuestreos)
    ]


def intervalos_condicionales(
    casos: Sequence[tuple[int, int, int]],
    n: float,
    delta_t: float,
    costos: Sequence[float],
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
    nivel: float = NIVEL,
) -> dict:
    """`B` y `a*` (punto e IC condicional con `c` fijo) por costo, sobre una sola tanda.

    El IC es el bootstrap percentil por caso con `c` constante; a diferencia del IC de la
    grilla de la 3.21, que dependia del emparejamiento por caso, se recomputa en lugar de
    interpolarse.
    """
    _validar_casos(casos)
    e_aut, e_man = _estadisticos(casos, range(len(casos)))
    remuestras = bootstrap_casos(casos, remuestreos=remuestreos, semilla=semilla)
    por_costo = []
    for c_s in costos:
        balances = [balance_neto(n, delta_t, a, m, c_s) for a, m in remuestras]
        a_estrella = [exactitud_equilibrio(m, delta_t, c_s) for _, m in remuestras]
        inferior, superior = percentil_intervalo(balances, nivel)
        por_costo.append(
            {
                "c_s": c_s,
                "balance": balance_neto(n, delta_t, e_aut, e_man, c_s),
                "balance_ic": [inferior, superior],
                "signo_fijado": signo_fijado(inferior, superior),
                "a_estrella": exactitud_equilibrio(e_man, delta_t, c_s),
                "a_estrella_ic": list(percentil_intervalo(a_estrella, nivel)),
            }
        )
    return {
        "e_aut": e_aut,
        "e_man": e_man,
        "diferencia": e_aut - e_man,
        "por_costo": por_costo,
        "nivel_confianza": nivel,
        "semilla": semilla,
        "remuestreos": remuestreos,
    }


def ic_bootstrap_condicional(
    casos: Sequence[tuple[int, int, int]],
    n: float,
    delta_t: float,
    c_s: float,
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
    nivel: float = NIVEL,
) -> dict:
    """Conveniencia: el intervalo condicional con `c` fijo para un unico costo."""
    return intervalos_condicionales(
        casos, n, delta_t, (c_s,), remuestreos=remuestreos, semilla=semilla, nivel=nivel
    )["por_costo"][0]


def suma_de_extremos(valores: Sequence[float]) -> tuple[float, float]:
    """Cota exterior por suma de extremos: el minimo y el maximo de un conjunto de valores."""
    if not valores:
        raise ValueError("la suma de extremos exige al menos un valor")
    return min(valores), max(valores)


def intervalo_combinado(
    n: float,
    delta_t: float,
    diferencia_ic: Sequence[float],
    c_ic: Sequence[float],
) -> tuple[float, float]:
    """Cota combinada de `B`: `B` en las cuatro esquinas (`diferencia` x `c`) y su min/max."""
    esquinas = [
        balance_neto(n, delta_t, diferencia, 0.0, c_s)
        for c_s in c_ic
        for diferencia in diferencia_ic
    ]
    return suma_de_extremos(esquinas)


def signo_fijado(inferior: float, superior: float) -> str:
    """Signo que fija un intervalo frente a cero; `no fijado` si lo contiene."""
    if inferior > 0:
        return "positivo"
    if superior < 0:
        return "negativo"
    return "no fijado"


# ---------------------------------------------------------------------------
# Lectura de entradas
# ---------------------------------------------------------------------------
def cargar_planilla(ruta: pathlib.Path = RUTA_PLANILLA) -> list[dict]:
    """Lee la planilla de etiquetado (doble etiquetado y brazo manual)."""
    with pathlib.Path(ruta).open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def cargar_predicciones_caso(ruta: pathlib.Path = RUTA_PRED_IN_SAMPLE) -> dict[str, str]:
    """`id_caso -> sector_predicho` del corpus in-sample (mismo que uso c-207)."""
    return {p.caso_id: p.sector_predicho for p in cargar_predicciones(pathlib.Path(ruta))}


def referencia_comun(filas_planilla: Sequence[Mapping[str, str]]) -> dict[str, str]:
    """Sector de consenso `E1`/`E2` por caso (138 casos; discordantes excluidos)."""
    referencia = construir_referencia(REFERENCIA_CONSENSO_NUEVO, doble_etiquetado=filas_planilla)
    return {caso: datos.sector for caso, datos in referencia.casos.items()}


def casos_referencia_comun(
    filas_planilla: Sequence[Mapping[str, str]],
    predichos: Mapping[str, str],
) -> list[tuple[int, int, int]]:
    """Casos de la referencia comun con su emparejamiento por caso (fuente de la 3.21)."""
    manual = [f for f in filas_planilla if f["tarea"] == TAREA_BRAZO_MANUAL]
    return emparejar_referencia_manual(referencia_comun(filas_planilla), manual, predichos)


def _leer_json(ruta: pathlib.Path) -> dict:
    return json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def _redondear(valor: float, decimales: int) -> float:
    return round(valor, decimales)


def _porcentaje(valor: float, decimales: int = DECIMALES_PORCENTAJE) -> float:
    return _redondear(valor * 100.0, decimales)


def _resumen_caso(casos: Sequence[tuple[int, int, int]]) -> dict:
    return {
        "casos": len(casos),
        "errores_automatizado": sum(c[0] for c in casos),
        "errores_manual": sum(c[1] for c in casos),
        "derivaciones_manual": sum(c[2] for c in casos),
    }


def _conteos_coinciden(referencia: Mapping, conteos: Mapping) -> bool:
    claves = ("casos", "errores_automatizado", "errores_manual", "derivaciones_manual")
    return all(referencia.get(clave) == conteos.get(clave) for clave in claves)


def construir_documento(
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Construye el documento completo; aborta si un anclaje no se reproduce."""
    c220 = _leer_json(RUTA_C220)
    c207 = _leer_json(RUTA_C207)
    c221 = _leer_json(RUTA_C221)

    bloque_207 = c207["balance_neto_referencia_comun"]
    referencia = bloque_207["referencia_consenso"]
    n = bloque_207["insumos"]["n_trimestral"]
    delta_t = bloque_207["insumos"]["delta_t_s"]
    c_s = c220["composicion"]["escenarios"]["bajo"]["punto"]
    c_ic = c220["composicion"]["escenarios"]["bajo"]["intervalo"]
    diferencia_ic = referencia["diferencia_ic"]

    planilla = cargar_planilla()
    predichos = cargar_predicciones_caso()
    casos = casos_referencia_comun(planilla, predichos)
    conteos = _resumen_caso(casos)
    e_aut, e_man = _estadisticos(casos, range(len(casos)))

    # --- Anclajes baratos (abortan antes de calcular el bootstrap) ---
    problemas = []
    if conteos != ANCLA_CONTEOS:
        problemas.append(f"conteos = {conteos} != {ANCLA_CONTEOS}")
    if not _conteos_coinciden(referencia, conteos):
        problemas.append(f"conteos de la 3.21 = {referencia} != {conteos}")
    if _redondear(c_s, 2) != ANCLA_C_S:
        problemas.append(f"c medido = {_redondear(c_s, 2)} != {ANCLA_C_S}")
    celdas = tuple(
        _redondear(balance_neto(n, delta_t, e_aut, e_man, c), DECIMALES_TESIS) for c in C_GRILLA_S
    )
    if celdas != ANCLA_BALANCE_REFERENCIA_COMUN:
        problemas.append(f"celdas 3.21 = {celdas} != {ANCLA_BALANCE_REFERENCIA_COMUN}")
    celdas_artefacto = tuple(
        _redondear(escenario["balance_h"], DECIMALES_TESIS)
        for escenario in referencia["escenarios"]
    )
    if celdas_artefacto != ANCLA_BALANCE_REFERENCIA_COMUN:
        problemas.append(
            f"celdas del artefacto 3.21 = {celdas_artefacto} != {ANCLA_BALANCE_REFERENCIA_COMUN}"
        )
    if problemas:
        raise AnclaNoReproducida("; ".join(problemas))

    # --- Intervalos condicionales (grilla superada + c medido) ---
    costos = (*C_GRILLA_S, c_s)
    resultado = intervalos_condicionales(
        casos, n, delta_t, costos, remuestreos=remuestreos, semilla=semilla
    )
    grid = resultado["por_costo"][: len(C_GRILLA_S)]
    medida = resultado["por_costo"][len(C_GRILLA_S)]

    problemas = []
    grid_ic = tuple(
        (_redondear(fila["balance_ic"][0], DECIMALES_TESIS),
         _redondear(fila["balance_ic"][1], DECIMALES_TESIS))
        for fila in grid
    )
    if grid_ic != ANCLA_BALANCE_IC:
        problemas.append(f"IC de la 3.21 = {grid_ic} != {ANCLA_BALANCE_IC}")
    grid_ic_artefacto = tuple(
        (_redondear(escenario["balance_h_ic"][0], DECIMALES_TESIS),
         _redondear(escenario["balance_h_ic"][1], DECIMALES_TESIS))
        for escenario in referencia["escenarios"]
    )
    if grid_ic_artefacto != ANCLA_BALANCE_IC:
        problemas.append(f"IC del artefacto 3.21 = {grid_ic_artefacto} != {ANCLA_BALANCE_IC}")
    if problemas:
        raise AnclaNoReproducida("; ".join(problemas))

    combinado = intervalo_combinado(n, delta_t, diferencia_ic, c_ic)

    grilla_superada = [
        {
            "c_min": c_min,
            "c_s": fila["c_s"],
            "balance": fila["balance"],
            "balance_ic": fila["balance_ic"],
            "signo_fijado": fila["signo_fijado"],
            "a_estrella": fila["a_estrella"],
            "a_estrella_ic": fila["a_estrella_ic"],
            "rotulo": "sensibilidad del supuesto superado (costo supuesto)",
            "estado": "condicional",
        }
        for c_min, fila in zip(C_GRILLA_MIN, grid)
    ]

    mixta = c221["balance"]["por_tasa"]
    entradas_sha = {
        ruta.name: sha256(ruta)
        for ruta in (
            RUTA_C220,
            RUTA_C207,
            RUTA_C221,
            RUTA_PLANILLA,
            RUTA_PRED_IN_SAMPLE,
        )
    }

    return {
        "change": "c-222-recalcular-el-balance-neto-con-el-costo-medido",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "Solo lectura, offline y determinista; reutiliza evaluation.metrics "
            "(remuestreos_indices, percentil_intervalo), evaluation.campana y "
            "evaluation.run_evaluation; sin red ni Gemini. Referencia comun de la seccion 3.21 "
            "con el c medido de la 3.31; bootstrap por caso con c fijo y cota combinada por "
            "suma de extremos."
        ),
        "preregistro": {
            "fijado_en_docstring": True,
            "ciego": False,
            "declaracion": (
                "El metodo y los parametros se fijaron antes de generar las salidas. El "
                "preregistro NO fue ciego: las celdas del balance de la 3.21, el c medido y los "
                "anclajes ya se conocian; no se habia observado la distribucion bootstrap "
                "recomputada con el c fijo."
            ),
        },
        "parametros": {
            "B": remuestreos,
            "semilla": semilla,
            "nivel_confianza": NIVEL,
            "grilla_c_min": list(C_GRILLA_MIN),
        },
        "entradas_sha256": entradas_sha,
        "anclajes": {
            "c_s": c_s,
            "c_s_redondeado": _redondear(c_s, 2),
            "referencia_comun": [fila["balance"] for fila in grid],
            "referencia_comun_redondeada": [
                _redondear(fila["balance"], DECIMALES_TESIS) for fila in grid
            ],
            "referencia_comun_ic_redondeada": [
                [_redondear(fila["balance_ic"][0], DECIMALES_TESIS),
                 _redondear(fila["balance_ic"][1], DECIMALES_TESIS)]
                for fila in grid
            ],
            "conteos": conteos,
        },
        "insumos": {
            "n": n,
            "delta_t_s": delta_t,
            "e_aut": e_aut,
            "e_man": e_man,
            "diferencia": e_aut - e_man,
            "diferencia_ic": list(diferencia_ic),
            "c_s": c_s,
            "c_ic": list(c_ic),
            **conteos,
            "fuente_e_aut": "consenso de E1 y E2 (28/138, por caso)",
            "fuente_e_man": "consenso de E1 y E2 (26/151, por derivacion)",
            "fuente_c": "seccion 3.31 (c-220); composicion por suma de extremos",
        },
        "condicional_c_fijo": {
            "metodo": (
                "bootstrap percentil por caso al 95 % (empareja las derivaciones manuales con "
                "su caso) con c constante; recomputado, no interpolado"
            ),
            "c_s": medida["c_s"],
            "balance": medida["balance"],
            "balance_ic": medida["balance_ic"],
            "signo_fijado": medida["signo_fijado"],
            "a_estrella": medida["a_estrella"],
            "a_estrella_ic": medida["a_estrella_ic"],
        },
        "combinado": {
            "metodo": (
                "suma de extremos: B en las cuatro esquinas (c x (e_aut - e_man)); cota "
                "exterior conservadora, no asume independencia"
            ),
            "balance_ic": list(combinado),
            "signo_fijado": signo_fijado(*combinado),
        },
        "referencia_comun": {
            "rotulo": referencia["rotulo"],
            "casos": referencia["casos"],
            "errores_automatizado": referencia["errores_automatizado"],
            "errores_manual": referencia["errores_manual"],
            "derivaciones_manual": referencia["derivaciones_manual"],
            "e_aut": referencia["e_aut"],
            "e_man": referencia["e_man"],
            "diferencia": referencia["diferencia"],
            "diferencia_ic": list(diferencia_ic),
        },
        "grilla_superada": grilla_superada,
        "sensibilidad_mixta_c221": {
            "ponderada_c_medido": mixta["ponderada"]["c_medido"],
            "cruda_c_medido": mixta["cruda"]["c_medido"],
            "promovida": False,
            "rotulo": (
                "sensibilidad que mezcla corpus y referencias (seccion 3.32); NO reemplaza el "
                "balance con referencia comun"
            ),
        },
        "trazabilidad": {
            "balance_central": "condicional_c_fijo.balance",
            "intervalo_condicional": "condicional_c_fijo.balance_ic",
            "intervalo_combinado": "combinado.balance_ic",
            "a_estrella": "condicional_c_fijo.a_estrella",
            "celdas_3_21": "grilla_superada[*].balance",
            "ic_3_21": "grilla_superada[*].balance_ic",
        },
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "nueva (aditiva; primer numero libre al aplicar)",
            "declaracion": (
                "Las cifras de este analisis son aditivas: van a la seccion nueva del memo y no "
                "reemplazan ningun valor de las secciones 3.1 a 3.32; no cambian el umbral de "
                "85 %, el costo supuesto de la rejilla, los artefactos congelados ni el corpus."
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
    return "n/d" if not par else f"[{_p(par[0])}; {_p(par[1])}]"


def _clave_json() -> dict:
    return {"ensure_ascii": False, "indent": 2, "sort_keys": True, "allow_nan": False}


def renderizar(doc: dict) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF, UTF-8 sin BOM."""
    texto_json = json.dumps(doc, **_clave_json()) + "\n"
    ins = doc["insumos"]
    cond = doc["condicional_c_fijo"]
    comb = doc["combinado"]
    ancla = doc["anclajes"]
    grilla = doc["grilla_superada"]
    mixta = doc["sensibilidad_mixta_c221"]
    lineas = [
        "# Balance neto recalculado con el costo medido (c-222)",
        "",
        f"Solo lectura, offline y determinista; sin red ni Gemini. {doc['aditivo']['declaracion']}",
        "",
        "## Anclajes reproducidos antes de escribir",
        "",
        f"- Costo medido: `c = {_p(ancla['c_s'], 2)}` s "
        f"(redondeado `{_p(ancla['c_s_redondeado'], 2)}`).",
        f"- Celdas de la 3.21: "
        + ", ".join(_p(v, 1) for v in ancla["referencia_comun_redondeada"])
        + ".",
        f"- IC de la 3.21: "
        + ", ".join(_ic(par) for par in ancla["referencia_comun_ic_redondeada"])
        + ".",
        f"- Conteos: casos {ancla['conteos']['casos']}, errores del automatizado "
        f"{ancla['conteos']['errores_automatizado']}, errores manuales "
        f"{ancla['conteos']['errores_manual']}, derivaciones "
        f"{ancla['conteos']['derivaciones_manual']}.",
        "",
        "## Insumos",
        "",
        f"- `N = {ins['n']}`; `dt = {_p(ins['delta_t_s'], 2)}` s.",
        f"- `e_aut = {_p(ins['e_aut'])}` ({ins['fuente_e_aut']}); "
        f"`e_man = {_p(ins['e_man'])}` ({ins['fuente_e_man']}).",
        f"- `e_aut - e_man = {_p(ins['diferencia'])}`, IC 95 % {_ic(ins['diferencia_ic'])}.",
        f"- `c = {_p(ins['c_s'], 2)}` s, IC 95 % {_ic(ins['c_ic'])} ({ins['fuente_c']}).",
        "",
        "## Escenario central con el costo medido",
        "",
        f"- `B = {_p(cond['balance'], 1)}` horas-persona por trimestre; intervalo condicional "
        f"({cond['metodo']}) 95 % {_ic(cond['balance_ic'])}; signo {cond['signo_fijado']}.",
        f"- `a* = {_p(cond['a_estrella'] * 100, 1)}` %; IC 95 % "
        f"{_ic([v * 100 for v in cond['a_estrella_ic']])} %.",
        f"- Intervalo combinado ({comb['metodo']}) 95 % {_ic(comb['balance_ic'])}; signo "
        f"{comb['signo_fijado']}.",
        "",
        "## Grilla superada (5, 10 y 15 minutos)",
        "",
        "| `c` (min) | `B` (h-persona) | IC 95 % de `B` | Signo | `a*` (%) | IC 95 % de `a*` (%) | Estado |",
        "|---|---|---|---|---|---|---|",
    ]
    for fila in grilla:
        lineas.append(
            f"| {fila['c_min']} | {_p(fila['balance'], 1)} | {_ic(fila['balance_ic'])} | "
            f"{fila['signo_fijado']} | {_p(fila['a_estrella'] * 100, 1)} | "
            f"{_ic([v * 100 for v in fila['a_estrella_ic']])} | {fila['estado']} |"
        )
    lineas += [
        "",
        f"- Rotulo: {grilla[0]['rotulo']}. Cifras conservadas; no es insumo vigente.",
        "",
        "## Sensibilidad mixta de c-221 (no promovida)",
        "",
        f"- Con `e_aut` ponderada y el `c` medido: `{_p(mixta['ponderada_c_medido'], 1)}`; con "
        f"`e_aut` cruda y el `c` medido: `{_p(mixta['cruda_c_medido'], 1)}`.",
        f"- Promovida: {mixta['promovida']}. {mixta['rotulo']}.",
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
    parser = argparse.ArgumentParser(description="Balance neto recalculado con el costo medido (c-222)")
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
