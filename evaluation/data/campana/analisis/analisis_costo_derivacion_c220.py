#!/usr/bin/env python3
"""Costo de la derivacion erronea: descomposicion medida y cota anclada (c-220).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni
base de datos, no reclasifica ni modifica el corpus, las predicciones, los artefactos
congelados ni ningun numero canonico. Es aditivo: la seccion 3.31 del memo registra sus
cifras y NO reemplaza ningun valor `vigente` de las secciones 3.1 a 3.30.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/intervenciones.csv` (147 filas; 138 con `duracion_s`)
- `evaluation/data/campana/brazo_manual.csv` (220 decisiones de sector; 110 por operador)

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo y la regla de decision se fijan aqui antes de generar cualquier salida. El
preregistro NO es ciego: los conteos (147/138, 220, 25/122), la tabla de valores
esperados del `design.md` del change y los agregados del memo ya se conocian; lo que no
se habia observado es la distribucion bootstrap, que estas reglas gobiernan. Se informan
TODOS los resultados, favorables o no.

1. Definicion operacional de `c` (D2). `c` es el tiempo-persona ADICIONAL que una
   derivacion erronea consume respecto de una correcta, no el tiempo calendario hasta
   que el caso llega al sector correcto. Se distinguen dos regimenes:
   - Corto: el error se detecta y corrige en la compuerta de revision. Componente unico:
     correccion en la compuerta.
   - Largo: el error escapa y el sector receptor lo rediagnostica y lo devuelve.
     Componentes: rediagnostico (proxy), reasignacion y reanudacion de la tarea
     interrumpida.

2. Estimadores por `cambio_sector` (D3). Grupos por `cambio_sector` sobre las
   intervenciones CON `duracion_s`; se informa `n`, media, mediana, desvio estandar
   poblacional e IC bootstrap percentil al 95 % de la media y de la mediana
   (`B = 2000`, semilla `20261021`). El remuestreo de cada cantidad usa un generador
   `random.Random(20261021)` propio y reextrae una muestra del tamano del grupo. El IC
   percentil replica `evaluation.metrics.percentil_intervalo` (interpolacion lineal sobre
   `q * (n - 1)`), reimplementado con la biblioteca estandar para mantener el script
   autocontenido.

3. Diferencia de medias entre grupos (D3). Estimador del costo INCREMENTAL de corregir
   en la compuerta: remuestreo bootstrap independiente de cada grupo, en el mismo flujo
   de un generador `random.Random(20261021)`, con IC percentil al 95 %.

4. Proxy de rediagnostico (D3). Mediana del tiempo de decision de sector del brazo
   manual (`brazo_manual.csv`), informada agrupada y por operador (`O1`, `O2`). No se
   elige el operador conveniente: el agrupado es la estimacion y el operador lento es una
   cota superior de sensibilidad declarada. La dispersion entre operadores acota la
   precision del proxy.

5. Composicion de `c` (D2, D4). Tramo activo medido = correccion en la compuerta +
   re-decision proxy. Tramo anclado = reanudacion tras interrupcion, SOLO en el regimen
   largo y reportado como cota superior. El intervalo compuesto se propaga por SUMA DE
   EXTREMOS de los intervalos bootstrap de cada tramo (cota exterior conservadora; no
   asume independencia ni aplica ninguna fraccion para "calzar" la banda). Escenario
   bajo: solo los tramos medidos. Escenario alto: agrega el ancla sin promediarla.

6. Tramo anclado (D4, regla de verificacion). El tramo de reanudacion no se mide en este
   corpus. Se incorpora con UNA sola fuente primaria de la literatura sobre costo de
   interrupcion, verificada contra su texto COMPLETO (no contra el resumen) y con la
   poblacion y la tarea del estudio declaradas. Este analisis corre OFFLINE: no puede
   verificar la fuente contra el texto completo, de modo que NO se inventa ni se cita
   ninguna; el tramo se declara `no medido` con cota `no disponible` (regla D4.3) y `c`
   queda con dos tramos, sin ancla. El change no se bloquea.

7. Compuerta de decision D5 (fijada de antemano). El intervalo compuesto se compara con
   la banda canonica `[600; 900] s`:
   - Rama A: lo intersecta o queda contenido. El memo conserva `c = 10 a 15 min` como
     valor canonico y solo cambia su procedencia.
   - Rama B: lo excluye. El memo registra el hallazgo y remite a una DECISION DEL DUENO;
     el change NO recalcula el balance neto `B` ni `a*` y NO edita `08`, `09`, `10`, `12`
     ni `00-resumen`.

8. Justificacion del 85 % (D6). Paridad medida `1 - e_man` con `e_man = 26/151 = 0,1722`
   da `0,8278`; el umbral de `85 %` es mas exigente que la paridad con la tasa de error
   manual. Costo marginal por punto de exactitud: `N * 0,01 * c / 3600` horas-persona por
   trimestre, con `N = 2646` (universo trimestral, memo 3.11) y el `c` medido compuesto.

9. Frontera con el tiempo de revision (D7). El flujo automatizado SI agrega tiempo de
   revision: media de `duracion_s` sobre las 138 intervenciones. El termino `r` y su
   efecto `N * r / 3600` horas por trimestre se informan como SENSIBILIDAD SEPARADA Y
   ADITIVA: no se incorporan a `B` ni reescriben `08`, y el `B` canonico no se toca.

Salidas (UTF-8 sin BOM, LF, en esta misma carpeta):
`analisis_costo_derivacion_c220.json`, `.md` y `.SHA256SUMS.txt`. Dos corridas con las
mismas entradas producen salidas identicas byte a byte; el script imprime el SHA-256 de
cada salida.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_costo_derivacion_c220.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import random
import statistics
import sys
from datetime import datetime

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = SALIDA.parent
RUTA_INTERVENCIONES = CAMPANA / "intervenciones.csv"
RUTA_BRAZO_MANUAL = CAMPANA / "brazo_manual.csv"
RUTA_RESULTADOS = SALIDA / "resultados.json"

NOMBRE_BASE = "analisis_costo_derivacion_c220"
NOMBRE_JSON = f"{NOMBRE_BASE}.json"
NOMBRE_MD = f"{NOMBRE_BASE}.md"
NOMBRE_SUMAS = f"{NOMBRE_BASE}.SHA256SUMS.txt"

# Parametros fijados en el preregistro (docstring).
SEMILLA = 20261021
REMUESTREOS = 2000
NIVEL = 0.95
BANDA_CANONICA = (600.0, 900.0)
N_UNIVERSO = 2646
E_MAN = 26 / 151
OPERADORES = ("O1", "O2")
# Cobertura esperada de la entrada (aborta si no coincide).
N_INTERVENCIONES_ESPERADO = 147
N_CON_DURACION_ESPERADO = 138
N_CAMBIO_TRUE_ESPERADO = 25
N_BRAZO_ESPERADO = 220


class EntradaInconsistente(ValueError):
    """Los conteos de las entradas no coinciden con los valores versionados."""


# ---------------------------------------------------------------------------
# Funciones puras: percentil y bootstrap
# ---------------------------------------------------------------------------
def percentil_intervalo(muestras: list[float], confianza: float = NIVEL) -> tuple[float, float]:
    """Intervalo percentil con interpolacion lineal sobre `q * (n - 1)`.

    Replica `evaluation.metrics.percentil_intervalo` con la biblioteca estandar. Una
    muestra vacia devuelve `(0.0, 0.0)` y una de un solo valor, ese valor repetido.
    """
    ordenados = sorted(muestras)
    n = len(ordenados)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return ordenados[0], ordenados[0]

    alfa = 1.0 - confianza

    def _cuantil(q: float) -> float:
        posicion = q * (n - 1)
        bajo = int(math.floor(posicion))
        alto = int(math.ceil(posicion))
        if bajo == alto:
            return ordenados[bajo]
        fraccion = posicion - bajo
        return ordenados[bajo] * (1.0 - fraccion) + ordenados[alto] * fraccion

    return _cuantil(alfa / 2.0), _cuantil(1.0 - alfa / 2.0)


def _remuestrear(valores: list[float], generador: random.Random) -> list[float]:
    """Una remuestra bootstrap con reemplazo, del tamano de `valores`."""
    n = len(valores)
    return [valores[generador.randrange(n)] for _ in range(n)]


def bootstrap_estadistico(
    valores: list[float],
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
    estadistico=statistics.mean,
) -> tuple[float, float]:
    """IC bootstrap percentil de un estadistico; determinista para una semilla dada."""
    if not valores:
        raise ValueError("No se puede bootstrapear un grupo vacio")
    generador = random.Random(semilla)
    muestras = [estadistico(_remuestrear(valores, generador)) for _ in range(remuestreos)]
    return percentil_intervalo(muestras, NIVEL)


def resumen_grupo(
    valores: list[float],
    etiqueta: str,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """`n`, media, mediana, desvio poblacional e IC bootstrap de media y mediana."""
    if not valores:
        raise ValueError(f"El grupo {etiqueta!r} esta vacio")
    return {
        "etiqueta": etiqueta,
        "n": len(valores),
        "media": statistics.mean(valores),
        "mediana": statistics.median(valores),
        "desvio": statistics.pstdev(valores),
        "ic_media": bootstrap_estadistico(valores, remuestreos, semilla, statistics.mean),
        "ic_mediana": bootstrap_estadistico(valores, remuestreos, semilla, statistics.median),
    }


def diferencia_de_medias(
    grupo_a: list[float],
    grupo_b: list[float],
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Diferencia de medias `a - b` con IC bootstrap independiente."""
    if not grupo_a or not grupo_b:
        raise ValueError("La diferencia de medias exige dos grupos no vacios")
    generador = random.Random(semilla)
    na, nb = len(grupo_a), len(grupo_b)
    muestras = [
        statistics.mean(_remuestrear(grupo_a, generador))
        - statistics.mean(_remuestrear(grupo_b, generador))
        for _ in range(remuestreos)
    ]
    return {
        "diferencia": statistics.mean(grupo_a) - statistics.mean(grupo_b),
        "ic": percentil_intervalo(muestras, NIVEL),
    }


def _segundos_entre(inicio: str, fin: str) -> float:
    """Segundos entre dos marcas ISO-8601 (con zona horaria)."""
    return (datetime.fromisoformat(fin) - datetime.fromisoformat(inicio)).total_seconds()


def resumen_decisiones(
    registros: list[dict],
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Resumen del tiempo de decision de sector, agrupado y por operador."""
    if not registros:
        raise ValueError("El brazo manual esta vacio")
    duraciones = [r["duracion_s"] for r in registros]
    resumen = resumen_grupo(duraciones, "brazo_manual", remuestreos, semilla)
    por_operador = {}
    for operador in OPERADORES:
        valores = [r["duracion_s"] for r in registros if r["operador"] == operador]
        if not valores:
            raise ValueError(f"El operador {operador!r} no tiene decisiones")
        item = resumen_grupo(valores, operador, remuestreos, semilla)
        item.pop("etiqueta", None)
        por_operador[operador] = item
    resumen.pop("etiqueta", None)
    resumen["por_operador"] = por_operador
    return resumen


# ---------------------------------------------------------------------------
# Funciones puras: cobertura, composicion, compuerta, efectos
# ---------------------------------------------------------------------------
def cobertura_duracion(registros: list[dict]) -> dict:
    """Cobertura de `duracion_s`; enumera los casos sin dato y NO imputa."""
    faltantes = [r["id_caso"] for r in registros if r["duracion_s"] is None]
    con_duracion = len(registros) - len(faltantes)
    return {
        "total": len(registros),
        "con_duracion": con_duracion,
        "faltantes": faltantes,
        "proporcion": con_duracion / len(registros) if registros else 0.0,
    }


def _suma_componentes(componentes: list[dict]) -> dict:
    """Suma de puntos y de extremos de los intervalos (cota exterior conservadora)."""
    punto = sum(c["punto"] for c in componentes)
    bajo = sum(c["intervalo"][0] for c in componentes)
    alto = sum(c["intervalo"][1] for c in componentes)
    return {
        "componentes": [c["etiqueta"] for c in componentes],
        "punto": punto,
        "intervalo": (bajo, alto),
    }


def componer_c(componentes_medidos: list[dict], ancla: dict | None) -> dict:
    """Compone `c`: escenario bajo (medido) y alto (con ancla, sin promediar)."""
    if not componentes_medidos:
        raise ValueError("La composicion exige al menos un componente medido")
    bajo = _suma_componentes(componentes_medidos)
    if ancla is None:
        alto = {
            "disponible": False,
            "motivo": (
                "ancla de reanudacion no medido: cota no disponible (fuente de "
                "interrupcion no verificable offline, regla D4.3)"
            ),
        }
    else:
        alto = {"disponible": True, **_suma_componentes(componentes_medidos + [ancla])}
    return {
        "metodo": (
            "propagacion por suma de extremos de los intervalos bootstrap de cada tramo "
            "(cota exterior conservadora; no asume independencia)"
        ),
        "escenarios": {"bajo": bajo, "alto": alto},
    }


def comparar_banda(intervalo: tuple[float, float], banda: tuple[float, float] = BANDA_CANONICA) -> dict:
    """Compara un intervalo con la banda canonica y aplica la regla D5."""
    bajo, alto = intervalo
    banda_bajo, banda_alto = banda
    if alto < banda_bajo or bajo > banda_alto:
        relacion = "excluida"
    elif bajo >= banda_bajo and alto <= banda_alto:
        relacion = "contenida"
    else:
        relacion = "intersecta"
    return {
        "intervalo": (bajo, alto),
        "banda": (banda_bajo, banda_alto),
        "relacion": relacion,
        "rama": "B" if relacion == "excluida" else "A",
    }


def termino_revision(valores: list[float], remuestreos: int = REMUESTREOS, semilla: int = SEMILLA) -> dict:
    """Termino de revision `r` informado como sensibilidad separada (D7)."""
    if not valores:
        raise ValueError("El termino de revision exige intervenciones con duracion")
    resumen = resumen_grupo(valores, "revision", remuestreos, semilla)
    resumen.pop("etiqueta", None)
    return resumen


def horas_revision_por_trimestre(r_media: float, n_universo: int = N_UNIVERSO) -> float:
    """Efecto aditivo del termino de revision sobre `B` (horas-persona por trimestre)."""
    return n_universo * r_media / 3600.0


def costo_marginal_por_punto(c_segundos: float, n_universo: int = N_UNIVERSO) -> float:
    """Horas-persona por trimestre que agrega cada punto de exactitud perdido."""
    return n_universo * 0.01 * c_segundos / 3600.0


def paridad_manual(e_man: float = E_MAN) -> float:
    """Paridad con la tasa de error manual medida: `1 - e_man`."""
    return 1.0 - e_man


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _parsear_bool(texto: str) -> bool:
    valor = texto.strip().lower()
    if valor not in ("true", "false"):
        raise EntradaInconsistente(f"Valor booleano invalido en cambio_sector: {texto!r}")
    return valor == "true"


def cargar_intervenciones(ruta: pathlib.Path = RUTA_INTERVENCIONES) -> list[dict]:
    """Lee las intervenciones; `duracion_s` vacia queda en `None` (sin imputar)."""
    registros = []
    with pathlib.Path(ruta).open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            cruda = fila["duracion_s"].strip()
            registros.append(
                {
                    "id_caso": fila["id_caso"],
                    "duracion_s": float(cruda) if cruda else None,
                    "cambio_sector": _parsear_bool(fila["cambio_sector"]),
                }
            )
    return registros


def cargar_brazo_manual(ruta: pathlib.Path = RUTA_BRAZO_MANUAL) -> list[dict]:
    """Lee las decisiones de sector; la duracion es `timestamp - inicio` en segundos."""
    registros = []
    with pathlib.Path(ruta).open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            registros.append(
                {
                    "id_caso": fila["id_caso"],
                    "operador": fila["id_etiquetador"],
                    "tarea": fila["tarea"],
                    "duracion_s": _segundos_entre(fila["inicio"], fila["timestamp"]),
                }
            )
    return registros


def verificar_conteos(intervenciones: list[dict], brazo: list[dict]) -> None:
    """Aborta si los conteos no coinciden con los valores versionados."""
    problemas = []
    if len(intervenciones) != N_INTERVENCIONES_ESPERADO:
        problemas.append(f"intervenciones = {len(intervenciones)} != {N_INTERVENCIONES_ESPERADO}")
    con_duracion = sum(1 for r in intervenciones if r["duracion_s"] is not None)
    if con_duracion != N_CON_DURACION_ESPERADO:
        problemas.append(f"con duracion = {con_duracion} != {N_CON_DURACION_ESPERADO}")
    n_true = sum(1 for r in intervenciones if r["cambio_sector"])
    if n_true != N_CAMBIO_TRUE_ESPERADO:
        problemas.append(f"cambio_sector true = {n_true} != {N_CAMBIO_TRUE_ESPERADO}")
    if len(brazo) != N_BRAZO_ESPERADO:
        problemas.append(f"brazo manual = {len(brazo)} != {N_BRAZO_ESPERADO}")
    if problemas:
        raise EntradaInconsistente("; ".join(problemas))


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def _componente(etiqueta: str, resumen: dict) -> dict:
    """Componente de composicion a partir de un resumen de grupo."""
    return {"etiqueta": etiqueta, "punto": resumen["media"], "intervalo": resumen["ic_media"]}


def construir_documento(
    entradas: dict | None = None,
    *,
    remuestreos: int = REMUESTREOS,
    semilla: int = SEMILLA,
) -> dict:
    """Construye el documento completo; aborta si los conteos no coinciden."""
    if entradas is None:
        intervenciones = cargar_intervenciones()
        brazo = cargar_brazo_manual()
    else:
        intervenciones = entradas["intervenciones"]
        brazo = entradas["brazo"]
    verificar_conteos(intervenciones, brazo)

    cobertura = cobertura_duracion(intervenciones)
    con_duracion = [r for r in intervenciones if r["duracion_s"] is not None]
    grupo_si = [r["duracion_s"] for r in con_duracion if r["cambio_sector"]]
    grupo_no = [r["duracion_s"] for r in con_duracion if not r["cambio_sector"]]
    duraciones = [r["duracion_s"] for r in con_duracion]

    resumen_si = resumen_grupo(grupo_si, "cambio_sector_true", remuestreos, semilla)
    resumen_no = resumen_grupo(grupo_no, "cambio_sector_false", remuestreos, semilla)
    diferencia = diferencia_de_medias(grupo_si, grupo_no, remuestreos, semilla)
    brazo_resumen = resumen_decisiones(brazo, remuestreos, semilla)
    revision = termino_revision(duraciones, remuestreos, semilla)

    correccion = {
        "etiqueta": "correccion_compuerta",
        "punto": diferencia["diferencia"],
        "intervalo": diferencia["ic"],
    }
    redeccion = {
        "etiqueta": "redeccion_proxy",
        "punto": brazo_resumen["mediana"],
        "intervalo": brazo_resumen["ic_mediana"],
    }
    composicion = componer_c([correccion, redeccion], ancla=None)
    # El tramo de reanudacion queda `no medido`; la compuerta usa el escenario medido.
    intervalo_compuesto = composicion["escenarios"]["bajo"]["intervalo"]
    compuerta = comparar_banda(intervalo_compuesto, BANDA_CANONICA)

    c_medido = composicion["escenarios"]["bajo"]["punto"]
    return {
        "change": "c-220-cuantificar-el-costo-de-la-derivacion-erronea",
        "generador": "evaluation/data/campana/analisis/analisis_costo_derivacion_c220.py",
        "metodo": (
            "Descomposicion de `c` (tiempo-persona adicional de una derivacion erronea) en "
            "un tramo activo medido y un tramo anclado: duraciones por `cambio_sector` con "
            "IC bootstrap percentil al 95 %, diferencia de medias con IC independiente, "
            "tiempo de decision de sector del brazo manual como proxy del rediagnostico, y "
            "composicion por suma de extremos. Solo lectura, sin red ni Gemini; no "
            "reclasifica ni reentrena."
        ),
        "preregistro": {
            "fijado_en_docstring": True,
            "ciego": False,
            "declaracion": (
                "El metodo y la regla de decision se fijaron antes de generar las salidas. "
                "El preregistro NO fue ciego: los conteos y los agregados ya se conocian; no "
                "se habia observado la distribucion bootstrap."
            ),
        },
        "parametros": {
            "remuestreos": remuestreos,
            "B": remuestreos,
            "semilla": semilla,
            "nivel_confianza": NIVEL,
            "banda_canonica": list(BANDA_CANONICA),
            "n_universo": N_UNIVERSO,
            "e_man": E_MAN,
        },
        "entradas_sha256": {
            pathlib.Path(ruta).name: sha256(pathlib.Path(ruta))
            for ruta in (RUTA_INTERVENCIONES, RUTA_BRAZO_MANUAL, RUTA_RESULTADOS)
        },
        "cobertura_duracion": cobertura,
        "grupos_cambio_sector": {
            "true": resumen_si,
            "false": resumen_no,
        },
        "diferencia_de_medias": {
            "diferencia": diferencia["diferencia"],
            "ic": diferencia["ic"],
            "interpretacion": (
                "costo incremental de corregir en la compuerta (regimen corto): tiempo "
                "adicional de las intervenciones que cambian el sector respecto de las que "
                "lo confirman"
            ),
        },
        "brazo_manual": brazo_resumen,
        "termino_revision": {
            **revision,
            "B_canonico_no_modificado": True,
            "efecto_sobre_b_horas_trimestre": horas_revision_por_trimestre(revision["media"]),
            "rotulo": (
                "sensibilidad separada y aditiva (D7): el flujo automatizado SI agrega "
                "tiempo de revision, en contra del supuesto del balance; NO se incorpora a "
                "`B` ni reescribe 08"
            ),
        },
        "componentes": {
            "correccion_compuerta": correccion,
            "redeccion_proxy": redeccion,
            "reanudacion": {
                "etiqueta": "reanudacion",
                "estado": "no medido",
                "cota": "no disponible",
                "motivo": (
                    "no se mide en este corpus; la fuente de interrupcion no se pudo "
                    "verificar contra su texto completo offline (regla D4.3)"
                ),
            },
        },
        "composicion": composicion,
        "compuerta_d5": {
            **compuerta,
            "banda_canonica": list(BANDA_CANONICA),
            "intervalo": list(compuerta["intervalo"]),
            "banda": list(compuerta["banda"]),
            "regla": (
                "A: el intervalo intersecta o contiene la banda; B: la excluye y remite a "
                "decision del dueno sin recalcular B ni a*"
            ),
        },
        "justificacion_umbral": {
            "paridad_manual": paridad_manual(),
            "e_man": E_MAN,
            "referencia_previa": (
                "el 15 % de paridad (85 %) se conserva como aproximacion, superada por la "
                "medicion"
            ),
            "costo_marginal_por_punto_horas_trimestre": costo_marginal_por_punto(c_medido),
            "c_medido_usado": c_medido,
            "formula": "N * 0,01 * c / 3600",
        },
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "3.31",
            "declaracion": (
                "Las cifras de este analisis son aditivas: van a la seccion 3.31 del memo y "
                "no reemplazan ningun valor `vigente` de las secciones 3.1 a 3.30; no "
                "cambian el umbral de 85 %, el balance neto `B`, `a*` ni los artefactos "
                "congelados."
            ),
        },
    }


def _num(valor: float, decimales: int = 4) -> str:
    return f"{valor:.{decimales}f}"


def renderizar(doc: dict) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF."""
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    grupo_si = doc["grupos_cambio_sector"]["true"]
    grupo_no = doc["grupos_cambio_sector"]["false"]
    compuerta = doc["compuerta_d5"]
    lineas = [
        "# Costo de la derivacion erronea: descomposicion medida y cota anclada (c-220)",
        "",
        f"Sobre `{doc['entradas_sha256']['intervenciones.csv'][:12]}...` (intervenciones) y "
        f"`{doc['entradas_sha256']['brazo_manual.csv'][:12]}...` (brazo manual). "
        f"{doc['aditivo']['declaracion']}",
        "",
        "## Preregistro",
        "",
        f"- Fijado en el docstring antes de generar las salidas: "
        f"{doc['preregistro']['fijado_en_docstring']}.",
        f"- Ciego: {doc['preregistro']['ciego']}. {doc['preregistro']['declaracion']}",
        f"- Remuestreos: {doc['parametros']['B']}; semilla: {doc['parametros']['semilla']}; "
        f"nivel: {_num(doc['parametros']['nivel_confianza'], 2)}.",
        "",
        "## Cobertura de duraciones",
        "",
        f"- Total de intervenciones: {doc['cobertura_duracion']['total']}; con duracion: "
        f"{doc['cobertura_duracion']['con_duracion']} "
        f"({_num(doc['cobertura_duracion']['proporcion'])}).",
        f"- Casos sin duracion (no imputados): "
        + ", ".join(doc["cobertura_duracion"]["faltantes"])
        + ".",
        "",
        "## Duraciones por `cambio_sector`",
        "",
        "| Grupo | n | Media (s) | Mediana (s) | Desvio (s) | IC 95 % media (s) | IC 95 % mediana (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for resumen in (grupo_si, grupo_no):
        lineas.append(
            f"| `cambio_sector={resumen['etiqueta'].rsplit('_', 1)[-1]}` | {resumen['n']} | "
            f"{_num(resumen['media'])} | {_num(resumen['mediana'])} | {_num(resumen['desvio'])} | "
            f"[{_num(resumen['ic_media'][0])}; {_num(resumen['ic_media'][1])}] | "
            f"[{_num(resumen['ic_mediana'][0])}; {_num(resumen['ic_mediana'][1])}] |"
        )
    lineas += [
        "",
        f"- Diferencia de medias (costo incremental de corregir en la compuerta): "
        f"{_num(doc['diferencia_de_medias']['diferencia'])} s, IC 95 % "
        f"[{_num(doc['diferencia_de_medias']['ic'][0])}; "
        f"{_num(doc['diferencia_de_medias']['ic'][1])}].",
        f"- {doc['diferencia_de_medias']['interpretacion']}.",
        "",
        "## Proxy de rediagnostico (brazo manual)",
        "",
        "| Ambito | n | Media (s) | Mediana (s) | IC 95 % mediana (s) |",
        "|---|---|---|---|---|",
        f"| Agrupado | {doc['brazo_manual']['n']} | {_num(doc['brazo_manual']['media'])} | "
        f"{_num(doc['brazo_manual']['mediana'])} | "
        f"[{_num(doc['brazo_manual']['ic_mediana'][0])}; "
        f"{_num(doc['brazo_manual']['ic_mediana'][1])}] |",
    ]
    for operador, resumen in doc["brazo_manual"]["por_operador"].items():
        lineas.append(
            f"| `{operador}` | {resumen['n']} | {_num(resumen['media'])} | "
            f"{_num(resumen['mediana'])} | "
            f"[{_num(resumen['ic_mediana'][0])}; {_num(resumen['ic_mediana'][1])}] |"
        )
    lineas += [
        "",
        "- No se elige el operador conveniente: el agrupado es la estimacion y el operador "
        "lento es una cota superior de sensibilidad.",
        "",
        "## Composicion de `c`",
        "",
        f"- Metodo de propagacion: {doc['composicion']['metodo']}.",
        f"- Tramo activo medido: correccion en la compuerta "
        f"({_num(doc['componentes']['correccion_compuerta']['punto'])} s) + re-decision proxy "
        f"({_num(doc['componentes']['redeccion_proxy']['punto'])} s).",
        f"- Tramo anclado (reanudacion): estado `{doc['componentes']['reanudacion']['estado']}`, "
        f"cota `{doc['componentes']['reanudacion']['cota']}`. "
        f"{doc['componentes']['reanudacion']['motivo']}.",
        f"- Escenario bajo (solo medido): punto "
        f"{_num(doc['composicion']['escenarios']['bajo']['punto'])} s, intervalo 95 % "
        f"[{_num(doc['composicion']['escenarios']['bajo']['intervalo'][0])}; "
        f"{_num(doc['composicion']['escenarios']['bajo']['intervalo'][1])}] s.",
        "",
        "## Compuerta de decision D5",
        "",
        f"- Intervalo compuesto comparado con la banda canonica "
        f"[{_num(compuerta['banda_canonica'][0], 0)}; {_num(compuerta['banda_canonica'][1], 0)}] s.",
        f"- Relacion: {compuerta['relacion']}; rama: {compuerta['rama']}.",
        f"- El intervalo [{_num(compuerta['intervalo'][0])}; {_num(compuerta['intervalo'][1])}] s "
        f"excluye la banda: el valor previo (`10 a 15 min`) no es tiempo-persona activo.",
        "- Se remite a DECISION DEL DUENO; este analisis no recalcula `B` ni `a*`.",
        "",
        "## Justificacion del umbral del 85 % (D6)",
        "",
        f"- Paridad medida `1 - e_man` con `e_man = {_num(E_MAN)}`: "
        f"{_num(doc['justificacion_umbral']['paridad_manual'])}. El umbral es mas exigente.",
        f"- Costo marginal por punto de exactitud: "
        f"{_num(doc['justificacion_umbral']['costo_marginal_por_punto_horas_trimestre'])} "
        f"horas-persona por trimestre (`{doc['justificacion_umbral']['formula']}`, "
        f"c = {_num(doc['justificacion_umbral']['c_medido_usado'])} s).",
        "",
        "## Termino de revision (D7)",
        "",
        f"- `r` (media de `duracion_s`, {doc['termino_revision']['n']} casos): "
        f"{_num(doc['termino_revision']['media'])} s; mediana "
        f"{_num(doc['termino_revision']['mediana'])} s.",
        f"- Efecto aditivo sobre `B`: "
        f"{_num(doc['termino_revision']['efecto_sobre_b_horas_trimestre'])} horas-persona por "
        f"trimestre. {doc['termino_revision']['rotulo']}",
        "",
        "## Entradas y SHA-256",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for nombre, digest in doc["entradas_sha256"].items():
        lineas.append(f"| `{nombre}` | `{digest}` |")
    lineas.append("")
    return texto_json, "\n".join(lineas) + "\n"


def escribir(
    doc: dict,
    directorio: pathlib.Path = SALIDA,
    nombre_base: str = NOMBRE_BASE,
) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `SHA256SUMS` (UTF-8 sin BOM, LF)."""
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
    sumas = "".join(f"{sha256(ruta)}  {ruta.name}\n" for ruta in rutas)
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
    """Construye y escribe el analisis; no escribe si los conteos no coinciden."""
    doc = construir_documento(remuestreos=remuestreos, semilla=semilla)
    return escribir(doc, salida, nombre_base=nombre_base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
    except (EntradaInconsistente, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    for ruta in rutas:
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
