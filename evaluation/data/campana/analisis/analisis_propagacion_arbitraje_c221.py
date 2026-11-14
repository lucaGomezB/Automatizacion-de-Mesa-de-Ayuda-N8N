#!/usr/bin/env python3
"""Propagacion del arbitraje fuera de muestra: tres lecturas, desgloses, calibracion
descriptiva y sensibilidad del balance (c-221).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica, no reentrena y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es aditivo: la seccion 3.32 del memo
registra sus cifras y NO reemplaza ningun valor `vigente` de las secciones 3.1 a 3.31.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/corpus_independiente_arbitrado.json` (206 casos: I001..I150
  originales, I151..I206 de refuerzo; `canal_origen` y `sector_asignado`).
- `evaluation/data/campana/predicciones_arbitrado.json` (`hybrid-v3` congelado sobre los 206).
- `evaluation/data/campana/predicciones_independiente.json` (primera corrida sobre los 103 con
  consenso de E3/E4).
- `evaluation/data/campana/arbitraje_tres_vias.json` (`origen` y bandera `tres_vias`).
- `evaluation/data/campana/doble_etiquetado_arbitrado.csv` (marcas de tiempo de E3, E4 y E5).
- `data/corpus_evaluacion_pseudonimizado.json` (pesos por `sector_asignado` del corpus de ajuste).

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo y los parametros se fijan aqui antes de generar cualquier salida. El preregistro
NO es ciego: los agregados canonicos (142/206, macro-F1 0,7024, 87/103, 0,8146, ECE 0,1715,
Brier 0,1935, celdas del balance) ya se conocian; lo que no se habia observado es la
distribucion bootstrap, que estas reglas gobiernan. Se informan TODOS los resultados,
favorables o no.

1. Tres lecturas de la exactitud estricta fuera de muestra (D1).
   (i) Primaria: cruda sobre el corpus arbitrado completo (206 casos), con IC de Wilson.
   (ii) Complementaria ponderada: suma de la sensibilidad de cada clase por su peso en la
        composicion por `sector_asignado` del corpus de ajuste de 200 casos, con IC bootstrap
        percentil por caso (`B = 2000`, semilla `20261021`); las replicas a las que les falta
        alguna clase con peso se DESCARTAN y se cuentan.
   (iii) Complementaria de los 150 casos del diseno original (I001..I150) con referencia
        arbitrada, sin exclusion, con IC de Wilson.
   La ponderada y la de 150 son complementarias y no reemplazan a la primaria. Para cada
   lectura se informa si el limite superior del intervalo queda por debajo de 0,85. La regla
   de lectura (D1) es que el veredicto sobre el umbral se lee con las tres.

2. Pesos leidos del corpus de ajuste (D1). El vector esperado es `Sistemas` 16,
   `Soporte Tecnico Hardware` 85, `Soporte Tecnico Software` 67, `Seguridad Informatica` 31 y
   `Bases de Datos` 1 (suma 200); si el conteo leido difiere, el analisis aborta sin escribir.

3. Desgloses (OOS-021). Aciertos, n, exactitud e IC de Wilson por origen de la referencia
   (`consenso_e3_e4` vs `arbitraje_e5`), por bloque (consenso del diseno original,
   discordantes del diseno original y refuerzo), por etapa (deterministica y Gemini) y por
   canal. Para `Sistemas`: sensibilidad, precision, F1, destinos de error y composicion. Los
   conjuntos se derivan de los archivos; se verifica que los arbitrados son 64, los
   discordantes originales 47, el refuerzo 56 (ninguno en `predicciones_independiente.json`) y
   los de tres vias 6.

4. Calibracion descriptiva (CAL-007). Sobre los casos de la etapa Gemini del corpus arbitrado
   (91) se informan exactitud, confianza media, sobreconfianza, ECE (10 bandas de igual ancho),
   Brier y AUROC con IC bootstrap, mas el barrido de los candidatos de la regla prerregistrada
   de c-214 (0,70 vigente, 0,86, 0,91, 0,96, 0,99 y derivar todo) con casos aceptados y
   exactitud selectiva. NO se selecciona, confirma ni modifica ningun umbral: la regla
   prerregistrada elige solo con los 200 casos de ajuste. La fila de 34 del prerregistro se
   conserva y se reproduce como contraste.

5. Sensibilidad del balance neto (OOS-022). `B = (N/3600) * [dt - (e_aut - e_man) * c]` con
   `N = 2646`, `dt = 43,82` s y `e_man = 26/151`, con `e_aut` igual al complemento de la lectura
   ponderada y a la tasa cruda sobre el corpus arbitrado, y `c` en una rejilla propia de 5, 10 y
   15 minutos. Como c-220 ya fijo en el memo (3.31) el costo medido `c = 69,5074` s, se agrega
   como ESCENARIO CENTRAL adicional, conservando la rejilla como sensibilidad. El resultado se
   rotula como SENSIBILIDAD que mezcla corpus y referencias y MUST NOT reemplazar el balance
   con referencia comun.

6. Controles de reproducibilidad (OOS-023). Se comparan `predicciones_independiente.json` y
   `predicciones_arbitrado.json` en los casos comunes y se informa cuantos difieren en sector,
   en etapa y en confianza, con sus identificadores. Para cada archivo se registra el `commit`
   declarado y si es alcanzable desde `origin/main` con
   `git merge-base --is-ancestor <commit> origin/main`: codigo 0, alcanzable; 1, no alcanzable;
   cualquier otro codigo (por ejemplo 128, objeto ausente del clon), tambien no alcanzable, con
   aviso en CONSOLA de que el objeto no esta presente en este clon. Si no es alcanzable se
   registra el commit que versiono el archivo con `git log --diff-filter=A --format=%h -- <archivo>`.
   NO se usa `git cat-file -t`: prueba solo la presencia local del objeto y da resultados
   distintos segun el clon. El JSON registra la alcanzabilidad y el commit que versiono el
   archivo, no la presencia local, de modo que las salidas no dependen del clon.

7. Anclajes que abortan antes de escribir (exit distinto de cero, sin salidas): 142/206 y
   macro-F1 0,7024 sobre el arbitrado; 87/103 y la ponderada 0,8146 sobre los 103 de
   `predicciones_independiente.json`; ECE 0,1715 y Brier 0,1935 sobre los 34 casos Gemini con
   consenso; la celda +6,9 del balance (15 %, 5 minutos, e_aut = 53/200) y +25,4/+18,7/+11,9
   con la referencia comun; el vector de pesos; las cardinalidades 64/47/56/6 y los 103 dentro
   de I001..I150; y, si `analisis_sesgo_corpus_referencia_c219.json` esta presente, los
   aciertos y el n por origen de c-219 (109/142 y 33/64).

Salidas (UTF-8 sin BOM, LF, en esta misma carpeta): `analisis_propagacion_arbitraje_c221.json`,
`.md` y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte
a byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del repositorio):

    python3 evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.py
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import pathlib
import random
import subprocess
import sys
from typing import Mapping, Optional, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.calibracion_gate import (  # noqa: E402
    auroc,
    barrido_umbral,
    brier,
    ece,
    ic_bootstrap_metrica,
    sobreconfianza,
)
from evaluation.metrics import (  # noqa: E402
    CLASES,
    f1_macro,
    f1_por_clase,
    intervalo_wilson,
    matriz_confusion,
    percentil_intervalo,
    precision_por_clase,
    remuestreos_indices,
    sensibilidad_por_clase,
    soporte_por_clase,
)

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_CORPUS_ARBITRADO = CAMPANA / "corpus_independiente_arbitrado.json"
RUTA_PRED_ARBITRADO = CAMPANA / "predicciones_arbitrado.json"
RUTA_PRED_INDEPENDIENTE = CAMPANA / "predicciones_independiente.json"
RUTA_ARBITRAJE = CAMPANA / "arbitraje_tres_vias.json"
RUTA_ETIQUETADO = CAMPANA / "doble_etiquetado_arbitrado.csv"
RUTA_CORPUS_AJUSTE = ROOT / "data/corpus_evaluacion_pseudonimizado.json"
RUTA_C219 = SALIDA / "analisis_sesgo_corpus_referencia_c219.json"

NOMBRE_BASE = "analisis_propagacion_arbitraje_c221"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

# Parametros fijados en el preregistro (docstring).
SEMILLA = 20261021
REMUESTREOS = 2000
NIVEL = 0.95
BANDAS_ECE = 10
UMBRALES = (0.70, 0.86, 0.91, 0.96, 0.99, math.inf)
UMBRAL_OBJETIVO = 0.85

# Balance neto (constantes del memo canonico).
N_BALANCE = 2646
DELTA_T_S = 43.82
E_MAN = 26 / 151
E_MAN_PRELIMINAR = 0.15
E_AUT_CANONICO = 53 / 200
E_AUT_REFERENCIA_COMUN = 28 / 138
C_GRID_S = (300.0, 600.0, 900.0)
C_MEDIDO_S = 69.50741008771931  # memo 3.31 (c-220), escenario medido
C_ETIQUETAS = ("5", "10", "15")

# Cardinalidades esperadas de las entradas (aborta si no coinciden).
N_ARBITRADO = 206
N_ORIGINAL = 150
N_REFUERZO = 56
N_ARBITRADOS = 64
N_DISCORDANTES_ORIGINALES = 47
N_TRES_VIAS = 6
N_103_EN_150 = 103

# Anclajes canonicos que deben reproducirse antes de escribir.
ANCLA_TOTAL = (142, 206)
ANCLA_MACRO_F1 = 0.7024
ANCLA_103 = (87, 103)
ANCLA_PONDERADA_103 = 0.8146
ANCLA_ECE_34 = 0.1715
ANCLA_BRIER_34 = 0.1935
ANCLA_BALANCE_6_9 = 6.9
ANCLA_BALANCE_COMUN = (25.4, 18.7, 11.9)
ANCLA_C219 = {"consenso": (109, 142), "arbitrado": (33, 64)}

PESOS_ESPERADOS = {
    "Sistemas": 16,
    "Soporte Tecnico Hardware": 85,
    "Soporte Tecnico Software": 67,
    "Seguridad Informatica": 31,
    "Bases de Datos": 1,
}

ORIGEN_CONSENSO = "consenso_e3_e4"
ORIGEN_ARBITRADO = "arbitraje_e5"
BLOQUE_CONSENSO = "consenso_diseno_original"
BLOQUE_DISCORDANTES = "discordantes_diseno_original"
BLOQUE_REFUERZO = "refuerzo"

# Nombres de archivo de las predicciones con control de `commit`.
COMMIT_PRED_ARBITRADO = RUTA_PRED_ARBITRADO.name
COMMIT_PRED_INDEPENDIENTE = RUTA_PRED_INDEPENDIENTE.name


class EntradaInconsistente(ValueError):
    """Los conteos, los identificadores o los pesos no coinciden con lo versionado."""


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
def exactitud_ponderada(
    reales: Sequence[str], predichos: Sequence[str], pesos: Mapping[str, float]
) -> float:
    """Suma de `peso_c * sensibilidad_c` normalizada; error si una clase con peso no tiene soporte."""
    mc = matriz_confusion(list(reales), list(predichos))
    sensibilidad = sensibilidad_por_clase(mc)
    soportes = soporte_por_clase(mc)
    sin_soporte = [c for c in CLASES if pesos.get(c, 0) and soportes[c] == 0]
    if sin_soporte:
        raise EntradaInconsistente(
            f"clases con peso y sin soporte en la remuestra: {sin_soporte}"
        )
    total = sum(pesos.get(c, 0) for c in CLASES)
    if total == 0:
        raise EntradaInconsistente("el vector de pesos esta vacio")
    return sum(pesos.get(c, 0) * sensibilidad[c] for c in CLASES) / total


def ic_bootstrap_ponderada(
    reales: Sequence[str],
    predichos: Sequence[str],
    pesos: Mapping[str, float],
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """IC bootstrap percentil por caso; descarta y cuenta las replicas sin alguna clase."""
    reales = list(reales)
    predichos = list(predichos)
    generador = random.Random(semilla)
    muestras: list[float] = []
    descartadas = 0
    for indices in remuestreos_indices(generador, len(reales), remuestreos):
        try:
            muestras.append(
                exactitud_ponderada(
                    [reales[i] for i in indices], [predichos[i] for i in indices], pesos
                )
            )
        except EntradaInconsistente:
            descartadas += 1
    return {
        "valor": exactitud_ponderada(reales, predichos, pesos),
        "ic": list(percentil_intervalo(muestras, NIVEL)),
        "remuestras_validas": len(muestras),
        "descartadas": descartadas,
        "remuestreos": remuestreos,
        "semilla": semilla,
        "nivel_confianza": NIVEL,
    }


def desglose(casos: Sequence[dict], clave: str) -> dict:
    """Aciertos, n, exactitud e IC de Wilson por valor de `clave` (los casos son dicts)."""
    grupos: dict[str, list[dict]] = {}
    for caso in casos:
        grupos.setdefault(caso[clave], []).append(caso)
    salida = {}
    for grupo in sorted(grupos):
        miembros = grupos[grupo]
        aciertos = sum(1 for c in miembros if c["real"] == c["predicho"])
        n = len(miembros)
        salida[grupo] = {
            "aciertos": aciertos,
            "n": n,
            "exactitud": (aciertos / n if n else None),
            "ic_wilson": list(intervalo_wilson(aciertos, n)),
        }
    return salida


def metricas_por_clase(reales: Sequence[str], predichos: Sequence[str]) -> dict:
    """Matriz 5x5, precision, sensibilidad, F1, soporte y macro-F1 del conjunto."""
    mc = matriz_confusion(list(reales), list(predichos))
    f1 = f1_por_clase(mc)
    return {
        "matriz": mc,
        "precision": precision_por_clase(mc),
        "sensibilidad": sensibilidad_por_clase(mc),
        "f1": f1,
        "soporte": soporte_por_clase(mc),
        "f1_macro": f1_macro(f1),
    }


def destinos_de_error(reales: Sequence[str], predichos: Sequence[str], clase: str) -> dict:
    """Conteo de sectores predichos en los errores de una clase (orden por conteo y nombre)."""
    conteo: dict[str, int] = {}
    for real, predicho in zip(reales, predichos):
        if real == clase and predicho != clase:
            conteo[predicho] = conteo.get(predicho, 0) + 1
    return dict(sorted(conteo.items(), key=lambda par: (-par[1], par[0])))


def _normalizar_umbral(umbral):
    """`inf` -> texto `"inf"` (JSON estricto y rotulo estable)."""
    if isinstance(umbral, float) and math.isinf(umbral):
        return "inf"
    return umbral


def calibracion_descriptiva(
    confianzas: Sequence[float],
    aciertos: Sequence[bool],
    umbrales: Sequence[float],
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Descriptiva (no elige umbral): exactitud, ECE, Brier, AUROC con IC y barrido."""
    n = len(confianzas)
    ok = sum(1 for a in aciertos if a)
    barrido = barrido_umbral(confianzas, aciertos, umbrales, n_total_corpus=n)
    for fila in barrido:
        fila["umbral"] = _normalizar_umbral(fila["umbral"])
    return {
        "n": n,
        "aciertos": ok,
        "exactitud": ok / n if n else None,
        "confianza_media": sum(confianzas) / n if n else None,
        "sobreconfianza": ic_bootstrap_metrica(
            confianzas, aciertos, sobreconfianza, remuestreos=remuestreos, semilla=semilla
        ),
        "ece": ic_bootstrap_metrica(
            confianzas, aciertos, ece, remuestreos=remuestreos, semilla=semilla
        ),
        "brier": ic_bootstrap_metrica(
            confianzas, aciertos, brier, remuestreos=remuestreos, semilla=semilla
        ),
        "auroc": ic_bootstrap_metrica(
            confianzas, aciertos, auroc, remuestreos=remuestreos, semilla=semilla
        ),
        "barrido": barrido,
        "umbral_seleccionado": None,
    }


def balance_neto(n: float, delta_t: float, e_aut: float, e_man: float, costo_s: float) -> float:
    """Balance neto trimestral en horas-persona: `(N/3600) * [dt - (e_aut - e_man) * c]`."""
    return (n / 3600.0) * (delta_t - (e_aut - e_man) * costo_s)


def diferencias_entre_corridas(pred_a: Mapping[str, dict], pred_b: Mapping[str, dict]) -> dict:
    """Casos comunes con sector, etapa o confianza distintos (identificadores incluidos)."""
    comunes = sorted(set(pred_a) & set(pred_b))

    def distintos(campo: str) -> list[str]:
        return [caso for caso in comunes if pred_a[caso][campo] != pred_b[caso][campo]]

    return {
        "casos_comunes": len(comunes),
        "sector": distintos("sector_predicho"),
        "etapa": distintos("etapa"),
        "confianza": distintos("confianza"),
    }


# ---------------------------------------------------------------------------
# Control de alcanzabilidad del commit declarado
# ---------------------------------------------------------------------------
def clasificar_codigo_commit(codigo: int) -> bool:
    """`0` -> alcanzable desde `main`; cualquier otro codigo -> no alcanzable."""
    return codigo == 0


def nota_consola_commit(codigo: int) -> Optional[str]:
    """Aviso de consola cuando el objeto no esta presente en el clon (codigo distinto de 0/1)."""
    if codigo in (0, 1):
        return None
    return "el objeto del commit no esta presente en este clon (no viaja con fetch ni con clone)"


def alcanzabilidad_commit(
    commit: str, ruta_archivo: pathlib.Path, *, repo: pathlib.Path = ROOT
) -> dict:
    """Alcanzabilidad desde `origin/main` y commit que versiono el archivo (solo lectura)."""
    proceso = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "origin/main"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    alcanzable = clasificar_codigo_commit(proceso.returncode)
    versionador = None
    if not alcanzable:
        relativas = _ruta_relativa(ruta_archivo, repo)
        log = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%h", "--", relativas],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        lineas = [linea for linea in log.stdout.splitlines() if linea.strip()]
        versionador = lineas[-1] if lineas else None
    return {
        "commit": commit,
        "alcanzable_desde_main": alcanzable,
        "commit_que_versiono_el_archivo": versionador,
        "codigo_salida": proceso.returncode,
    }


def _ruta_relativa(ruta: pathlib.Path, repo: pathlib.Path) -> str:
    try:
        return pathlib.Path(ruta).resolve().relative_to(pathlib.Path(repo).resolve()).as_posix()
    except ValueError:
        return str(ruta)


# ---------------------------------------------------------------------------
# Lectura de entradas
# ---------------------------------------------------------------------------
def cargar_pesos(ruta: pathlib.Path = RUTA_CORPUS_AJUSTE) -> dict[str, int]:
    """Pesos por `sector_asignado` del corpus de ajuste (solo lectura)."""
    documento = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    conteo = collections.Counter(caso["sector_asignado"] for caso in documento["casos"])
    if set(conteo) - set(CLASES):
        raise EntradaInconsistente(f"sectores fuera del conjunto canonico: {sorted(set(conteo) - set(CLASES))}")
    return {clase: conteo.get(clase, 0) for clase in CLASES}


def _cargar_predicciones(ruta: pathlib.Path) -> dict:
    documento = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    return {p["caso_id"]: p for p in documento["predictions"]}, documento.get("cache_meta", {})


def cargar_entradas() -> dict:
    """Lee todos los artefactos versionados; no escribe nada ni imprime texto."""
    corpus_doc = json.loads(RUTA_CORPUS_ARBITRADO.read_text(encoding="utf-8"))
    casos = corpus_doc["casos"]
    referencia = {c["id"]: c["sector_asignado"] for c in casos}
    canal = {c["id"]: c["canal_origen"] for c in casos}
    if len(referencia) != len(casos):
        raise EntradaInconsistente("identificadores de caso duplicados en el corpus arbitrado")

    arb, meta_arb = _cargar_predicciones(RUTA_PRED_ARBITRADO)
    ind, meta_ind = _cargar_predicciones(RUTA_PRED_INDEPENDIENTE)

    arbitraje_doc = json.loads(RUTA_ARBITRAJE.read_text(encoding="utf-8"))
    origen = {c["id"]: c["origen"] for c in arbitraje_doc["casos"]}
    tres_vias = {c["id"]: bool(c["tres_vias"]) for c in arbitraje_doc["casos"]}

    etiquetado = []
    with RUTA_ETIQUETADO.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            etiquetado.append(fila)

    return {
        "referencia": referencia,
        "canal": canal,
        "arb": arb,
        "ind": ind,
        "meta_arb": meta_arb,
        "meta_ind": meta_ind,
        "origen": origen,
        "tres_vias": tres_vias,
        "etiquetado": etiquetado,
    }


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def _clave_numerica(caso_id: str) -> int:
    try:
        return int(caso_id[1:])
    except (ValueError, IndexError):
        return 0


def _bloque(caso_id: str, origen: Mapping[str, str]) -> str:
    if _clave_numerica(caso_id) > N_ORIGINAL:
        return BLOQUE_REFUERZO
    return BLOQUE_DISCORDANTES if origen[caso_id] == ORIGEN_ARBITRADO else BLOQUE_CONSENSO


def _verificar_cardinalidades(entradas: dict, pesos: Mapping[str, int]) -> dict:
    arb = entradas["arb"]
    ind = entradas["ind"]
    origen = entradas["origen"]
    referencia = entradas["referencia"]
    ids = sorted(referencia)
    ids_original = [i for i in ids if _clave_numerica(i) <= N_ORIGINAL]
    ids_refuerzo = [i for i in ids if _clave_numerica(i) > N_ORIGINAL]
    arbitr_todos = [i for i in ids if origen[i] == ORIGEN_ARBITRADO]
    disc_original = [i for i in ids_original if origen[i] == ORIGEN_ARBITRADO]
    tres = [i for i in ids if entradas["tres_vias"][i]]

    problemas = []
    if len(ids) != N_ARBITRADO:
        problemas.append(f"corpus arbitrado = {len(ids)} != {N_ARBITRADO}")
    if len(ids_original) != N_ORIGINAL:
        problemas.append(f"originales = {len(ids_original)} != {N_ORIGINAL}")
    if len(ids_refuerzo) != N_REFUERZO:
        problemas.append(f"refuerzo = {len(ids_refuerzo)} != {N_REFUERZO}")
    if len(arbitr_todos) != N_ARBITRADOS:
        problemas.append(f"arbitrados = {len(arbitr_todos)} != {N_ARBITRADOS}")
    if len(disc_original) != N_DISCORDANTES_ORIGINALES:
        problemas.append(f"discordantes originales = {len(disc_original)} != {N_DISCORDANTES_ORIGINALES}")
    if len(tres) != N_TRES_VIAS:
        problemas.append(f"tres vias = {len(tres)} != {N_TRES_VIAS}")
    n_103 = sum(1 for i in ind if _clave_numerica(i) <= N_ORIGINAL)
    if n_103 != N_103_EN_150:
        problemas.append(f"predicciones_independiente en I001..I150 = {n_103} != {N_103_EN_150}")
    solape = set(ids_refuerzo) & set(ind)
    if solape:
        problemas.append(f"el refuerzo no debe estar en predicciones_independiente: {sorted(solape)[:5]}")
    if pesos != PESOS_ESPERADOS:
        problemas.append(f"pesos leidos = {pesos} != {PESOS_ESPERADOS}")
    if problemas:
        raise EntradaInconsistente("; ".join(problemas))
    return {
        "original": ids_original,
        "refuerzo": ids_refuerzo,
        "arbitrados": arbitr_todos,
        "discordantes_originales": disc_original,
        "tres_vias": tres,
    }


def _casos_grupo(
    ids: Sequence[str], entradas: dict
) -> list[dict]:
    referencia = entradas["referencia"]
    arb = entradas["arb"]
    return [
        {
            "real": referencia[i],
            "predicho": arb[i]["sector_predicho"],
            "origen": entradas["origen"][i],
            "etapa": arb[i]["etapa"],
            "canal": entradas["canal"][i],
            "bloque": _bloque(i, entradas["origen"]),
        }
        for i in ids
    ]


def _lectura_con_wilson(aciertos: int, n: int, etiqueta: str) -> dict:
    ic = list(intervalo_wilson(aciertos, n))
    return {
        "etiqueta": etiqueta,
        "aciertos": aciertos,
        "n": n,
        "exactitud": aciertos / n if n else None,
        "ic_wilson": ic,
        "limite_superior_debajo_de_085": bool(ic[1] < UMBRAL_OBJETIVO),
    }


def _construir_documento(
    entradas: dict,
    *,
    remuestreos: int,
    semilla: int,
    avisos: Optional[list[str]],
) -> dict:
    pesos = cargar_pesos()
    conjuntos = _verificar_cardinalidades(entradas, pesos)
    referencia = entradas["referencia"]
    arb = entradas["arb"]
    ind = entradas["ind"]
    ids = sorted(referencia)

    # --- Anclajes baratos (abortan antes de calcular bootstrap) ---
    reales_tot = [referencia[i] for i in ids]
    predichos_tot = [arb[i]["sector_predicho"] for i in ids]
    total_aciertos = sum(1 for r, p in zip(reales_tot, predichos_tot) if r == p)
    macro_f1 = f1_macro(f1_por_clase(matriz_confusion(reales_tot, predichos_tot)))
    ids_ind = sorted(ind)
    reales_103 = [ind[i]["sector_asignado"] for i in ids_ind]
    predichos_103 = [ind[i]["sector_predicho"] for i in ids_ind]
    aciertos_103 = sum(1 for r, p in zip(reales_103, predichos_103) if r == p)
    ponderada_103 = exactitud_ponderada(reales_103, predichos_103, pesos)
    gem_34 = [ind[i] for i in ids_ind if ind[i]["etapa"] == "gemini"]
    ece_34 = ece([p["confianza"] for p in gem_34], [p["sector_predicho"] == p["sector_asignado"] for p in gem_34])
    brier_34 = brier([p["confianza"] for p in gem_34], [p["sector_predicho"] == p["sector_asignado"] for p in gem_34])
    balance_6_9 = balance_neto(N_BALANCE, DELTA_T_S, E_AUT_CANONICO, E_MAN_PRELIMINAR, 300.0)
    balance_comun = tuple(
        round(balance_neto(N_BALANCE, DELTA_T_S, E_AUT_REFERENCIA_COMUN, E_MAN, c), 1)
        for c in C_GRID_S
    )

    problemas = []
    if (total_aciertos, len(ids)) != ANCLA_TOTAL:
        problemas.append(f"total = {(total_aciertos, len(ids))} != {ANCLA_TOTAL}")
    if abs(macro_f1 - ANCLA_MACRO_F1) > 5e-5:
        problemas.append(f"macro-F1 = {macro_f1:.4f} != {ANCLA_MACRO_F1}")
    if (aciertos_103, len(ids_ind)) != ANCLA_103:
        problemas.append(f"lectura 103 = {(aciertos_103, len(ids_ind))} != {ANCLA_103}")
    if abs(ponderada_103 - ANCLA_PONDERADA_103) > 5e-5:
        problemas.append(f"ponderada 103 = {ponderada_103:.4f} != {ANCLA_PONDERADA_103}")
    if abs(ece_34 - ANCLA_ECE_34) > 5e-5:
        problemas.append(f"ECE 34 = {ece_34:.4f} != {ANCLA_ECE_34}")
    if abs(brier_34 - ANCLA_BRIER_34) > 5e-5:
        problemas.append(f"Brier 34 = {brier_34:.4f} != {ANCLA_BRIER_34}")
    if round(balance_6_9, 1) != ANCLA_BALANCE_6_9:
        problemas.append(f"balance +6,9 = {balance_6_9:.4f} != {ANCLA_BALANCE_6_9}")
    if balance_comun != ANCLA_BALANCE_COMUN:
        problemas.append(f"balance referencia comun = {balance_comun} != {ANCLA_BALANCE_COMUN}")
    if problemas:
        raise AnclaNoReproducida("; ".join(problemas))

    # --- Anclaje opcional de c-219 ---
    c219 = None
    if RUTA_C219.exists():
        documento_c219 = json.loads(RUTA_C219.read_text(encoding="utf-8"))
        sub = documento_c219["subconjuntos"]
        c219 = {
            "presente": True,
            "consenso": (sub["consenso"]["aciertos"], sub["consenso"]["casos"]),
            "arbitrado": (sub["arbitrado"]["aciertos"], sub["arbitrado"]["casos"]),
        }
        if c219["consenso"] != ANCLA_C219["consenso"] or c219["arbitrado"] != ANCLA_C219["arbitrado"]:
            raise AnclaNoReproducida(
                f"c-219 por origen = {c219['consenso']}/{c219['arbitrado']} != "
                f"{ANCLA_C219['consenso']}/{ANCLA_C219['arbitrado']}"
            )

    # --- Tres lecturas ---
    primaria = _lectura_con_wilson(total_aciertos, len(ids), "primaria")
    ponderada = ic_bootstrap_ponderada(
        reales_tot, predichos_tot, pesos, remuestreos=remuestreos, semilla=semilla
    )
    ponderada.update(
        {
            "etiqueta": "complementaria",
            "limite_superior_debajo_de_085": bool(ponderada["ic"][1] < UMBRAL_OBJETIVO),
        }
    )
    ids_150 = [i for i in ids if _clave_numerica(i) <= N_ORIGINAL]
    aciertos_150 = sum(1 for i in ids_150 if referencia[i] == arb[i]["sector_predicho"])
    ciento_cincuenta = _lectura_con_wilson(aciertos_150, len(ids_150), "complementaria")
    lectura_103 = _lectura_con_wilson(aciertos_103, len(ids_ind), "etapa_previa")

    # --- Desgloses ---
    casos = _casos_grupo(ids, entradas)
    desglose_grupos = {
        "origen": desglose(casos, "origen"),
        "bloque": desglose(casos, "bloque"),
        "etapa": desglose(casos, "etapa"),
        "canal": desglose(casos, "canal"),
    }

    # --- Metricas por clase y Sistemas ---
    metricas = metricas_por_clase(reales_tot, predichos_tot)
    sistemas_ids = [i for i in ids if referencia[i] == "Sistemas"]
    sistemas_original = [i for i in sistemas_ids if _clave_numerica(i) <= N_ORIGINAL]
    sistemas_refuerzo = [i for i in sistemas_ids if _clave_numerica(i) > N_ORIGINAL]
    sistemas = {
        "soporte": len(sistemas_ids),
        "sensibilidad": metricas["sensibilidad"]["Sistemas"],
        "precision": metricas["precision"]["Sistemas"],
        "f1": metricas["f1"]["Sistemas"],
        "destinos_error": destinos_de_error(reales_tot, predichos_tot, "Sistemas"),
        "destinos_error_original": destinos_de_error(
            [referencia[i] for i in sistemas_original],
            [arb[i]["sector_predicho"] for i in sistemas_original],
            "Sistemas",
        ),
        "destinos_error_refuerzo": destinos_de_error(
            [referencia[i] for i in sistemas_refuerzo],
            [arb[i]["sector_predicho"] for i in sistemas_refuerzo],
            "Sistemas",
        ),
        "original_n": len(sistemas_original),
        "refuerzo_n": len(sistemas_refuerzo),
        "composicion_original": dict(sorted(collections.Counter(referencia[i] for i in conjuntos["original"]).items())),
        "composicion_refuerzo": dict(sorted(collections.Counter(referencia[i] for i in conjuntos["refuerzo"]).items())),
    }

    # --- Calibracion descriptiva ---
    gem_91 = [arb[i] for i in ids if arb[i]["etapa"] == "gemini"]
    calibracion = {
        "arbitrado": calibracion_descriptiva(
            [p["confianza"] for p in gem_91],
            [p["sector_predicho"] == referencia[p["caso_id"]] for p in gem_91],
            UMBRALES,
            remuestreos=remuestreos,
            semilla=semilla,
        ),
        "contraste_34": calibracion_descriptiva(
            [p["confianza"] for p in gem_34],
            [p["sector_predicho"] == p["sector_asignado"] for p in gem_34],
            UMBRALES,
            remuestreos=remuestreos,
            semilla=semilla,
        ),
    }

    # --- Balance de sensibilidad ---
    e_aut_ponderada = 1.0 - ponderada["valor"]
    e_aut_cruda = 1.0 - primaria["exactitud"]
    balance = {
        "formula": "B = (N/3600) * [dt - (e_aut - e_man) * c]",
        "rotulo": "sensibilidad",
        "declaracion": (
            "sensibilidad que mezcla corpus y referencias; NO reemplaza el balance con "
            "referencia comun de la seccion 3.21"
        ),
        "n": N_BALANCE,
        "delta_t_s": DELTA_T_S,
        "e_man": E_MAN,
        "es_coste_medido_incluido": True,
        "c_medido_s": C_MEDIDO_S,
        "por_tasa": {
            "ponderada": {
                "e_aut": e_aut_ponderada,
                "fuente_e_aut": "complemento de la lectura ponderada (1 - valor)",
                "rejilla": {
                    etiqueta: balance_neto(N_BALANCE, DELTA_T_S, e_aut_ponderada, E_MAN, c)
                    for etiqueta, c in zip(C_ETIQUETAS, C_GRID_S)
                },
                "c_medido": balance_neto(N_BALANCE, DELTA_T_S, e_aut_ponderada, E_MAN, C_MEDIDO_S),
            },
            "cruda": {
                "e_aut": e_aut_cruda,
                "fuente_e_aut": "tasa cruda sobre el corpus arbitrado (1 - 142/206)",
                "rejilla": {
                    etiqueta: balance_neto(N_BALANCE, DELTA_T_S, e_aut_cruda, E_MAN, c)
                    for etiqueta, c in zip(C_ETIQUETAS, C_GRID_S)
                },
                "c_medido": balance_neto(N_BALANCE, DELTA_T_S, e_aut_cruda, E_MAN, C_MEDIDO_S),
            },
        },
        "anclajes": {
            "celda_6_9": balance_6_9,
            "referencia_comun": list(balance_comun),
        },
    }

    # --- Reproducibilidad: diferencias y commits ---
    commits = {}
    for nombre, ruta, meta in (
        (COMMIT_PRED_ARBITRADO, RUTA_PRED_ARBITRADO, entradas["meta_arb"]),
        (COMMIT_PRED_INDEPENDIENTE, RUTA_PRED_INDEPENDIENTE, entradas["meta_ind"]),
    ):
        commit = meta.get("commit")
        if commit:
            control = alcanzabilidad_commit(commit, ruta)
            if avisos is not None:
                nota = nota_consola_commit(control["codigo_salida"])
                if nota:
                    avisos.append(f"{nombre}: {nota}")
            commits[nombre] = {
                "commit": control["commit"],
                "alcanzable_desde_main": control["alcanzable_desde_main"],
                "commit_que_versiono_el_archivo": control["commit_que_versiono_el_archivo"],
            }
    reproducibilidad = {
        "diferencias": diferencias_entre_corridas(ind, arb),
        "commits": commits,
        "nota": (
            "el commit declarado en predicciones_independiente.json puede existir como objeto "
            "colgante en el clon donde se hizo la corrida, pero no viaja con fetch ni con clone; "
            "se registra por alcanzabilidad desde origin/main y por el commit que versiono el "
            "archivo, no por la presencia local del objeto (git cat-file -t prohibido)."
        ),
    }

    # --- Cuotas observadas y ventana del refuerzo ---
    refuerzo_set = set(conjuntos["refuerzo"])
    etiquetado_refuerzo = [f for f in entradas["etiquetado"] if f["id_caso"] in refuerzo_set]
    marcas = sorted(f["timestamp"] for f in etiquetado_refuerzo)
    por_etiquetador = {}
    for fila in etiquetado_refuerzo:
        por_etiquetador.setdefault(fila["id_etiquetador"], []).append(fila["timestamp"])
    cuotas = {
        "canal_150": dict(collections.Counter(entradas["canal"][i] for i in conjuntos["original"])),
        "canal_refuerzo": dict(collections.Counter(entradas["canal"][i] for i in conjuntos["refuerzo"])),
        "sector_150": dict(collections.Counter(referencia[i] for i in conjuntos["original"])),
        "sector_refuerzo": dict(collections.Counter(referencia[i] for i in conjuntos["refuerzo"])),
        "ventana_refuerzo": {
            "filas": len(etiquetado_refuerzo),
            "desde": marcas[0] if marcas else None,
            "hasta": marcas[-1] if marcas else None,
            "por_etiquetador": {
                k: (min(v), max(v)) for k, v in sorted(por_etiquetador.items())
            },
        },
    }

    entradas_sha = {
        ruta.name: sha256(ruta)
        for ruta in (
            RUTA_CORPUS_ARBITRADO,
            RUTA_PRED_ARBITRADO,
            RUTA_PRED_INDEPENDIENTE,
            RUTA_ARBITRAJE,
            RUTA_ETIQUETADO,
            RUTA_CORPUS_AJUSTE,
        )
    }

    return {
        "change": "c-221-propagar-el-arbitraje-y-atender-el-dictamen-post-v1-3-0",
        "generador": f"evaluation/data/campana/analisis/{NOMBRE_BASE}.py",
        "metodo": (
            "solo lectura; evaluation.metrics + evaluation.calibracion_gate; sin red ni Gemini; "
            "deterministico; metodo prerregistrado en el docstring del generador"
        ),
        "preregistro": {
            "fijado_en_docstring": True,
            "ciego": False,
            "declaracion": (
                "El metodo y los parametros se fijaron antes de generar las salidas. El "
                "preregistro NO fue ciego: los agregados canonicos ya se conocian; no se habia "
                "observado la distribucion bootstrap."
            ),
        },
        "parametros": {
            "B": remuestreos,
            "semilla": semilla,
            "nivel_confianza": NIVEL,
            "bandas_ece": BANDAS_ECE,
            "umbrales": [0.70, 0.86, 0.91, 0.96, 0.99, "inf"],
            "umbral_objetivo": UMBRAL_OBJETIVO,
            "rejilla_c_min": [5, 10, 15],
            "c_medido_s": C_MEDIDO_S,
            "pesos": pesos,
        },
        "entradas_sha256": entradas_sha,
        "anclajes": {
            "total": ANCLA_TOTAL,
            "macro_f1": macro_f1,
            "lectura_103": ANCLA_103,
            "ponderada_103": ponderada_103,
            "ece_34": ece_34,
            "brier_34": brier_34,
            "arbitrados": len(conjuntos["arbitrados"]),
            "discordantes_originales": len(conjuntos["discordantes_originales"]),
            "refuerzo": len(conjuntos["refuerzo"]),
            "tres_vias": len(conjuntos["tres_vias"]),
            "balance_6_9": balance_6_9,
            "balance_referencia_comun": list(balance_comun),
        },
        "c219_origen": c219,
        "lecturas": {
            "primaria": primaria,
            "ponderada": ponderada,
            "ciento_cincuenta": ciento_cincuenta,
        },
        "lectura_103_etapa_previa": lectura_103,
        "desglose": desglose_grupos,
        "metricas_por_clase": metricas,
        "sistemas": sistemas,
        "calibracion": calibracion,
        "balance": balance,
        "reproducibilidad": reproducibilidad,
        "cuotas": cuotas,
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "3.32",
            "declaracion": (
                "Las cifras de este analisis son aditivas: van a la seccion 3.32 del memo y no "
                "reemplazan ningun valor `vigente` de las secciones 3.1 a 3.31; no cambian el "
                "umbral de 85 %, el balance neto `B`, `a*` ni los artefactos congelados."
            ),
        },
    }


def construir_documento(
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
    avisos: Optional[list[str]] = None,
) -> dict:
    """Verifica anclajes y mide; lanza ante cualquier inconsistencia (no escribe nada)."""
    return _construir_documento(
        cargar_entradas(), remuestreos=remuestreos, semilla=semilla, avisos=avisos
    )


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
    lecturas = doc["lecturas"]
    primaria = lecturas["primaria"]
    ponderada = lecturas["ponderada"]
    c150 = lecturas["ciento_cincuenta"]
    ancla = doc["anclajes"]
    sistemas = doc["sistemas"]
    calibracion = doc["calibracion"]
    balance = doc["balance"]
    lineas = [
        "# Propagacion del arbitraje fuera de muestra (c-221)",
        "",
        f"Solo lectura, offline y determinista; sin red ni Gemini. {doc['aditivo']['declaracion']}",
        "",
        "## Anclajes reproducidos antes de escribir",
        "",
        f"- Exactitud estricta cruda del corpus arbitrado: {ancla['total'][0]}/{ancla['total'][1]}; "
        f"macro-F1 {_p(ancla['macro_f1'])}.",
        f"- Lectura con exclusion (etapa previa): {ancla['lectura_103'][0]}/{ancla['lectura_103'][1]}; "
        f"ponderada {_p(ancla['ponderada_103'])}.",
        f"- ECE {_p(ancla['ece_34'])} y Brier {_p(ancla['brier_34'])} sobre los 34 casos Gemini con consenso.",
        f"- Cardinalidades: arbitrados {ancla['arbitrados']}, discordantes originales "
        f"{ancla['discordantes_originales']}, refuerzo {ancla['refuerzo']}, tres vias {ancla['tres_vias']}.",
        f"- Balance: celda +6,9 reproducida ({_p(ancla['balance_6_9'], 1)}); referencia comun "
        f"{[round(v, 1) for v in ancla['balance_referencia_comun']]}.",
        "",
        "## Tres lecturas de la exactitud estricta fuera de muestra",
        "",
        "| Lectura | Rotulo | Aciertos | n | Exactitud | IC 95 % | Limite superior < 0,85 |",
        "|---|---|---|---|---|---|---|",
        f"| Cruda (arbitrado) | {primaria['etiqueta']} | {primaria['aciertos']} | {primaria['n']} | "
        f"{_p(primaria['exactitud'])} | {_ic(primaria['ic_wilson'])} | {primaria['limite_superior_debajo_de_085']} |",
        f"| Ponderada | {ponderada['etiqueta']} | - | {ancla['total'][1]} | {_p(ponderada['valor'])} | "
        f"{_ic(ponderada['ic'])} | {ponderada['limite_superior_debajo_de_085']} |",
        f"| 150 originales sin exclusion | {c150['etiqueta']} | {c150['aciertos']} | {c150['n']} | "
        f"{_p(c150['exactitud'])} | {_ic(c150['ic_wilson'])} | {c150['limite_superior_debajo_de_085']} |",
        "",
        f"- Replicas descartadas por falta de alguna clase en la ponderada: {ponderada['descartadas']}.",
        "",
        "## Desglose por origen, bloque, etapa y canal",
        "",
    ]
    for clave, valores in doc["desglose"].items():
        lineas.append(f"### Por {clave}")
        lineas.append("")
        lineas.append("| Grupo | Aciertos | n | Exactitud | IC 95 % Wilson |")
        lineas.append("|---|---|---|---|---|")
        for grupo, valor in valores.items():
            lineas.append(
                f"| {grupo} | {valor['aciertos']} | {valor['n']} | {_p(valor['exactitud'])} | "
                f"{_ic(valor['ic_wilson'])} |"
            )
        lineas.append("")
    lineas += [
        "## Sistemas con soporte ampliado",
        "",
        f"- Soporte: {sistemas['soporte']} ({sistemas['original_n']} originales, "
        f"{sistemas['refuerzo_n']} de refuerzo); sensibilidad {_p(sistemas['sensibilidad'])}; "
        f"F1 {_p(sistemas['f1'])}.",
        f"- Destinos de error: {sistemas['destinos_error']}.",
        "",
        "## Calibracion descriptiva (etapa Gemini)",
        "",
        f"- Arbitrado (n = {calibracion['arbitrado']['n']}): exactitud "
        f"{_p(calibracion['arbitrado']['exactitud'])}, confianza media "
        f"{_p(calibracion['arbitrado']['confianza_media'])}, ECE "
        f"{_p(calibracion['arbitrado']['ece']['valor'])}, Brier "
        f"{_p(calibracion['arbitrado']['brier']['valor'])}, AUROC "
        f"{_p(calibracion['arbitrado']['auroc']['valor'])}. Umbral seleccionado: "
        f"{calibracion['arbitrado']['umbral_seleccionado']}.",
        f"- Contraste de 34 con consenso: ECE {_p(calibracion['contraste_34']['ece']['valor'])}; "
        f"Brier {_p(calibracion['contraste_34']['brier']['valor'])}.",
        "",
        "## Balance neto de sensibilidad",
        "",
        f"- Rotulo: {balance['rotulo']}. {balance['declaracion']}",
        f"- Formula: {balance['formula']}; N = {balance['n']}; dt = {_p(balance['delta_t_s'], 2)} s; "
        f"e_man = {_p(balance['e_man'])}.",
    ]
    for tasa, datos in balance["por_tasa"].items():
        filas = ", ".join(f"{k} min: {_p(v, 1)}" for k, v in datos["rejilla"].items())
        lineas.append(
            f"- e_aut {tasa} ({_p(datos['e_aut'])}): {filas}; c medido "
            f"{_p(balance['c_medido_s'], 2)} s: {_p(datos['c_medido'], 1)}."
        )
    lineas += [
        "",
        "## Reproducibilidad",
        "",
        f"- Diferencias entre corridas en {doc['reproducibilidad']['diferencias']['casos_comunes']} "
        f"casos comunes: sector {doc['reproducibilidad']['diferencias']['sector']}, etapa "
        f"{doc['reproducibilidad']['diferencias']['etapa']}, confianza "
        f"{doc['reproducibilidad']['diferencias']['confianza']}.",
    ]
    for nombre, control in doc["reproducibilidad"]["commits"].items():
        lineas.append(
            f"- `{nombre}`: commit {control['commit']}, alcanzable desde main "
            f"{control['alcanzable_desde_main']}, versionado por "
            f"{control['commit_que_versiono_el_archivo']}."
        )
    lineas += [
        "",
        "## Cuotas observadas y ventana del refuerzo",
        "",
        f"- Canal de los 150: {doc['cuotas']['canal_150']}; canal del refuerzo: {doc['cuotas']['canal_refuerzo']}.",
        f"- Sector del refuerzo: {doc['cuotas']['sector_refuerzo']}.",
        f"- Ventana del refuerzo: {doc['cuotas']['ventana_refuerzo']['desde']} a "
        f"{doc['cuotas']['ventana_refuerzo']['hasta']} "
        f"({doc['cuotas']['ventana_refuerzo']['filas']} filas).",
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
    """Escribe `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
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
    avisos: Optional[list[str]] = None,
) -> list[pathlib.Path]:
    """Construye y escribe el analisis; no escribe si un anclaje no se reproduce."""
    doc = construir_documento(remuestreos=remuestreos, semilla=semilla, avisos=avisos)
    return escribir(doc, salida, nombre_base=nombre_base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propagacion del arbitraje fuera de muestra (c-221)")
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--nombre", default=NOMBRE_BASE)
    parser.add_argument("--remuestreos", type=int, default=REMUESTREOS)
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    args = parser.parse_args(argv)
    avisos: list[str] = []
    try:
        rutas = ejecutar(
            args.salida,
            args.nombre,
            remuestreos=args.remuestreos,
            semilla=args.semilla,
            avisos=avisos,
        )
    except (AnclaNoReproducida, EntradaInconsistente) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for aviso in avisos:
        print(f"NOTA: {aviso}", file=sys.stderr)
    for ruta in rutas:
        print(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
