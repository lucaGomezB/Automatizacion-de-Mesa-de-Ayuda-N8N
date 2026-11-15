#!/usr/bin/env python3
"""Acotacion del arbitraje por mayoria (c-224).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica, no reentrena y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es aditivo: la seccion nueva del memo
registra sus cifras y NO reemplaza ningun valor de las secciones 3.1 a 3.34.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/doble_etiquetado_arbitrado.csv`: etiquetas de `E3`, `E4` y `E5`
  por caso (476 filas; `E5` solo en los 64 casos arbitrados).
- `evaluation/data/campana/arbitraje_tres_vias.json`: `origen` por caso
  (`consenso_e3_e4` o `arbitraje_e5`) y bandera `tres_vias`.
- `evaluation/data/campana/predicciones_arbitrado.json`: prediccion congelada de
  `hybrid-v3` sobre los 206 casos.
- `evaluation/data/campana/corpus_independiente_arbitrado.json`: referencia vigente de los
  206 casos (consenso de `E3` y `E4`; `E5` cuando difieren).

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo y los parametros se fijan aqui antes de generar cualquier salida. El
preregistro NO es ciego: los anclajes ya se conocian; lo que no se habia observado es la
coincidencia exacta entre la regla vigente y la mayoria de `{E3, E4, E5}` ni el efecto de
reasignar los 6 casos sin mayoria.

1. Regla vigente (D1). En los 142 casos de consenso `E3 = E4`, la regla usa esa etiqueta.
   En los 64 casos arbitrados, `E5` fija la referencia. La mayoria de `{E3, E4, E5}` es la
   etiqueta que aparece al menos dos veces; si las tres son distintas, no hay mayoria.

2. Coincidencia estructural (D2). La regla vigente coincide con la mayoria en `200` de
   `206` casos: los `142` de consenso coinciden por construccion y `58` de los `64`
   arbitrados tienen una mayoria que ya es la etiqueta de `E5`. Los `6` casos sin mayoria
   son `I033`, `I042`, `I056`, `I130`, `I194` e `I198`. La identidad `142 + 58 = 200` se
   verifica desde los archivos; no se presenta como medicion nueva.

3. Rango de exactitud (D3). La exactitud vigente es `142/206` (`0,6893`). Para cada uno de
   los 6 casos sin mayoria se lee la prediccion congelada y se comprueba si cae entre las
   tres etiquetas posibles. Si cae, el caso puede reasignarse a una etiqueta que acierta;
   si no, no puede convertirse en acierto con ninguna asignacion. El maximo es `142 + k`
   con `k = 5`, de modo que el rango es `142/206` (`0,6893`) a `147/206` (`0,7136`). El
   rango se rotula como cota de sensibilidad y no reemplaza la cifra primaria.

4. Metricas por clase bajo extremos (D3). Se calculan dos referencias: (a) la vigente (los
   6 casos con la etiqueta de `E5`) y (b) el extremo maximo, con cada caso reasignado a la
   etiqueta que coincide con la prediccion cuando existe, o a `E5` si no. Se guardan ambas
   matrices `5x5` y ambos vectores de precision, sensibilidad y F1 con el soporte.

5. Anclajes que abortan antes de escribir (exit distinto de cero, sin salidas): `200` casos
   con acuerdo, los `6` identificadores sin mayoria, `64` casos arbitrados, `142/206` de
   exactitud estricta, macro-F1 `0,7024` sobre la referencia vigente y el rango
   `142/206`-`147/206`. Los conjuntos se derivan de los archivos, no de constantes.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_arbitraje_mayoria_c224.json`,
`.md` y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas
byte a byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_arbitraje_mayoria_c224.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import sys
from typing import Mapping, Optional

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = SALIDA.parent
ROOT = SALIDA.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import (  # noqa: E402
    f1_macro,
    f1_por_clase,
    matriz_confusion,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)

NOMBRE_BASE = "analisis_arbitraje_mayoria_c224"
SALIDA_JSON = f"{NOMBRE_BASE}.json"
SALIDA_MD = f"{NOMBRE_BASE}.md"
SALIDA_SHA = f"{NOMBRE_BASE}.SHA256SUMS.txt"

RUTA_ETIQUETAS = "doble_etiquetado_arbitrado.csv"
RUTA_ORIGEN = "arbitraje_tres_vias.json"
RUTA_PREDICCIONES = "predicciones_arbitrado.json"
RUTA_REFERENCIA = "corpus_independiente_arbitrado.json"

SIN_MAYORIA_ESPERADOS = ["I033", "I042", "I056", "I130", "I194", "I198"]

ANCLA_COINCIDENCIA = 200
ANCLA_TOTAL = 206
ANCLA_CONSENSO = 142
ANCLA_ARBITRADOS = 64
ANCLA_ARBITRADOS_CON_MAYORIA = 58
ANCLA_SUMA = 200
ANCLA_ACIERTOS = 142
ANCLA_K = 5
ANCLA_MAX = 147
ANCLA_MACRO_F1 = 0.7024


class AnclajeError(Exception):
    """Un anclaje no se reproduce: no se escribe ninguna salida."""


def sha256(ruta: pathlib.Path, *, normalizar_lf: bool = True) -> str:
    """SHA-256 del archivo; con `normalizar_lf` colapsa CRLF a LF."""
    datos = pathlib.Path(ruta).read_bytes()
    if normalizar_lf:
        datos = datos.replace(b"\r\n", b"\n")
    return hashlib.sha256(datos).hexdigest()


def cargar_etiquetas(ruta: pathlib.Path) -> dict[str, dict[str, Optional[str]]]:
    """Devuelve `caso -> {E3, E4, E5}` leyendo el CSV de doble etiquetado."""
    etiquetas: dict[str, dict[str, Optional[str]]] = {}
    with ruta.open(newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            caso = fila["id_caso"]
            etiquetador = fila["id_etiquetador"]
            etiquetas.setdefault(caso, {"E3": None, "E4": None, "E5": None})[etiquetador] = fila[
                "sector_etiquetado"
            ]
    return etiquetas


def cargar_origen(ruta: pathlib.Path) -> dict[str, dict[str, object]]:
    """Devuelve `caso -> {origen, tres_vias}` leyendo el sidecar del arbitraje."""
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    return {
        caso["id"]: {"origen": caso["origen"], "tres_vias": bool(caso["tres_vias"])}
        for caso in documento["casos"]
    }


def cargar_predicciones(ruta: pathlib.Path) -> dict[str, str]:
    """Devuelve `caso -> sector_predicho` leyendo las predicciones congeladas."""
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    return {p["caso_id"]: p["sector_predicho"] for p in documento["predictions"]}


def cargar_referencia(ruta: pathlib.Path) -> dict[str, str]:
    """Devuelve `caso -> sector_asignado` leyendo la referencia vigente."""
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    return {c["id"]: c["sector_asignado"] for c in documento["casos"]}


def regla_vigente(etiquetas: Mapping[str, Optional[str]], origen: Mapping[str, object]) -> str:
    """Regla vigente: consenso `E3 = E4`; en caso contrario, `E5`."""
    if etiquetas["E3"] == etiquetas["E4"]:
        return etiquetas["E3"]
    return etiquetas["E5"]


def mayoria(etiquetas: Mapping[str, Optional[str]]) -> Optional[str]:
    """Etiqueta repetida al menos dos veces entre `E3`, `E4` y `E5`; `None` si no hay."""
    valores = [v for v in (etiquetas["E3"], etiquetas["E4"], etiquetas["E5"]) if v is not None]
    for valor in valores:
        if valores.count(valor) >= 2:
            return valor
    return None


def acuerdo_con_mayoria(casos: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    """Cuenta y lista los casos en que la regla vigente coincide con la mayoria."""
    ids = []
    for caso in sorted(casos):
        etiquetas = casos[caso]["etiquetas"]
        origen = casos[caso]["origen"]
        if regla_vigente(etiquetas, origen) == mayoria(etiquetas):
            ids.append(caso)
    return {"n": len(ids), "total": len(casos), "ids": ids}


def casos_sin_mayoria(casos: Mapping[str, Mapping[str, object]]) -> list[str]:
    """Lista los casos con tres etiquetas distintas (sin mayoria)."""
    return [caso for caso in sorted(casos) if mayoria(casos[caso]["etiquetas"]) is None]


def rango_exactitud(
    referencia: Mapping[str, str],
    predicciones: Mapping[str, str],
    seis: Mapping[str, Mapping[str, Optional[str]]],
) -> dict[str, object]:
    """Calcula aciertos, total, k, maximo y los casos reasignables y no reasignables."""
    aciertos = sum(1 for caso in referencia if predicciones.get(caso) == referencia[caso])
    total = len(referencia)
    reasignables = []
    no_reasignables = []
    for caso in sorted(seis):
        etiquetas = seis[caso]
        valores = {v for v in (etiquetas["E3"], etiquetas["E4"], etiquetas["E5"]) if v is not None}
        if predicciones.get(caso) in valores:
            reasignables.append(caso)
        else:
            no_reasignables.append(caso)
    k = len(reasignables)
    return {
        "aciertos": aciertos,
        "total": total,
        "k": k,
        "max": aciertos + k,
        "reasignables": reasignables,
        "no_reasignables": no_reasignables,
    }


def _metricas_desde(
    referencia: Mapping[str, str], predicciones: Mapping[str, str]
) -> dict[str, object]:
    """Matriz 5x5 y metricas por clase para una referencia dada."""
    casos = sorted(referencia)
    reales = [referencia[c] for c in casos]
    predichos = [predicciones[c] for c in casos]
    mc = matriz_confusion(reales, predichos)
    precision = precision_por_clase(mc)
    sensibilidad = sensibilidad_por_clase(mc)
    f1 = f1_por_clase(mc)
    soporte = soporte_por_clase(mc)
    return {
        "matriz": mc,
        "precision": precision,
        "sensibilidad": sensibilidad,
        "f1": f1,
        "soporte": soporte,
        "macro_f1": f1_macro(f1),
    }


def metricas_por_clase_bajo_extremos(
    referencia: Mapping[str, str],
    predicciones: Mapping[str, str],
    seis: Mapping[str, Mapping[str, Optional[str]]],
) -> dict[str, object]:
    """Metricas bajo la referencia vigente y bajo el extremo maximo reasignado."""
    vigente = _metricas_desde(referencia, predicciones)
    referencia_max = dict(referencia)
    for caso in seis:
        etiquetas = seis[caso]
        pred = predicciones.get(caso)
        valores = {v for v in (etiquetas["E3"], etiquetas["E4"], etiquetas["E5"]) if v is not None}
        if pred in valores:
            referencia_max[caso] = pred
        else:
            referencia_max[caso] = etiquetas["E5"]
    maximo = _metricas_desde(referencia_max, predicciones)
    return {"vigente": vigente, "maximo": maximo}


def construir_reporte(campana: pathlib.Path) -> dict[str, object]:
    """Construye el reporte completo a partir de las cuatro entradas versionadas."""
    etiquetas = cargar_etiquetas(campana / RUTA_ETIQUETAS)
    origen = cargar_origen(campana / RUTA_ORIGEN)
    predicciones = cargar_predicciones(campana / RUTA_PREDICCIONES)
    referencia = cargar_referencia(campana / RUTA_REFERENCIA)

    casos = {
        caso: {"etiquetas": etiquetas[caso], "origen": origen[caso]}
        for caso in sorted(etiquetas)
    }

    consenso = sum(1 for c in origen.values() if c["origen"] == "consenso_e3_e4")
    arbitrados = sum(1 for c in origen.values() if c["origen"] == "arbitraje_e5")

    coincidencia = acuerdo_con_mayoria(casos)
    sin_mayoria = casos_sin_mayoria(casos)
    arbitrados_con_mayoria = arbitrados - len(sin_mayoria)

    seis = {caso: etiquetas[caso] for caso in sin_mayoria}
    exactitud = rango_exactitud(referencia, predicciones, seis)
    metricas = metricas_por_clase_bajo_extremos(referencia, predicciones, seis)

    detalle = {
        caso: {
            "E3": etiquetas[caso]["E3"],
            "E4": etiquetas[caso]["E4"],
            "E5": etiquetas[caso]["E5"],
            "prediccion": predicciones.get(caso),
            "referencia": referencia.get(caso),
        }
        for caso in sin_mayoria
    }

    return {
        "arbitraje": {"consenso": consenso, "arbitrados": arbitrados},
        "identidad": {
            "consenso": consenso,
            "arbitrados_con_mayoria": arbitrados_con_mayoria,
            "suma": consenso + arbitrados_con_mayoria,
        },
        "coincidencia": coincidencia,
        "sin_mayoria": sin_mayoria,
        "detalle_sin_mayoria": detalle,
        "exactitud": exactitud,
        "metricas": metricas,
        "anclajes": {"verificados": False},
    }


def verificar_anclajes(reporte: Mapping[str, object]) -> None:
    """Aborta con `AnclajeError` si algun anclaje canonico no se reproduce."""
    comprobaciones = [
        (reporte["coincidencia"]["n"], ANCLA_COINCIDENCIA, "coincidencia.n"),
        (reporte["coincidencia"]["total"], ANCLA_TOTAL, "coincidencia.total"),
        (reporte["arbitraje"]["consenso"], ANCLA_CONSENSO, "arbitraje.consenso"),
        (reporte["arbitraje"]["arbitrados"], ANCLA_ARBITRADOS, "arbitraje.arbitrados"),
        (
            reporte["identidad"]["arbitrados_con_mayoria"],
            ANCLA_ARBITRADOS_CON_MAYORIA,
            "identidad.arbitrados_con_mayoria",
        ),
        (reporte["identidad"]["suma"], ANCLA_SUMA, "identidad.suma"),
        (reporte["exactitud"]["aciertos"], ANCLA_ACIERTOS, "exactitud.aciertos"),
        (reporte["exactitud"]["total"], ANCLA_TOTAL, "exactitud.total"),
        (reporte["exactitud"]["k"], ANCLA_K, "exactitud.k"),
        (reporte["exactitud"]["max"], ANCLA_MAX, "exactitud.max"),
        (
            round(reporte["metricas"]["vigente"]["macro_f1"], 4),
            ANCLA_MACRO_F1,
            "metricas.vigente.macro_f1",
        ),
    ]
    for obtenido, esperado, nombre in comprobaciones:
        if obtenido != esperado:
            raise AnclajeError(f"Anclaje {nombre}: obtenido {obtenido}, esperado {esperado}")
    if reporte["sin_mayoria"] != SIN_MAYORIA_ESPERADOS:
        raise AnclajeError(f"Anclaje sin_mayoria: {reporte['sin_mayoria']}")


def _clave_json() -> dict:
    return {"ensure_ascii": False, "indent": 2, "sort_keys": True, "allow_nan": False}


def _p(valor, decimales: int = 4) -> str:
    if valor is None:
        return "n/d"
    return f"{valor:.{decimales}f}".replace(".", ",")


def renderizar(reporte: Mapping[str, object]) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF, UTF-8 sin BOM."""
    texto_json = json.dumps(reporte, **_clave_json()) + "\n"
    exactitud = reporte["exactitud"]
    metricas = reporte["metricas"]
    lineas = [
        "# Acotacion del arbitraje por mayoria (c-224)",
        "",
        "Solo lectura, offline y determinista; sin red ni Gemini. Registro aditivo: no "
        "reemplaza ningun valor de las secciones 3.1 a 3.34.",
        "",
        "## Coincidencia estructural",
        "",
        f"- La regla vigente coincide con la mayoria de {{E3, E4, E5}} en "
        f"{reporte['coincidencia']['n']} de {reporte['coincidencia']['total']} casos.",
        f"- Identidad: {reporte['identidad']['consenso']} + "
        f"{reporte['identidad']['arbitrados_con_mayoria']} = {reporte['identidad']['suma']}.",
        "",
        "## Casos sin mayoria",
        "",
    ]
    for caso in reporte["sin_mayoria"]:
        detalle = reporte["detalle_sin_mayoria"][caso]
        lineas.append(
            f"- {caso}: E3={detalle['E3']}; E4={detalle['E4']}; E5={detalle['E5']}; "
            f"prediccion={detalle['prediccion']}; referencia={detalle['referencia']}."
        )
    lineas += [
        "",
        "## Rango de exactitud",
        "",
        f"- Minimo vigente: {exactitud['aciertos']}/{exactitud['total']} "
        f"({_p(exactitud['aciertos'] / exactitud['total'])}).",
        f"- Maximo con reasignacion: {exactitud['max']}/{exactitud['total']} "
        f"({_p(exactitud['max'] / exactitud['total'])}).",
        f"- Casos reasignables: {', '.join(exactitud['reasignables'])}.",
        f"- Casos no reasignables: {', '.join(exactitud['no_reasignables'])}.",
        "",
        "## Metricas por clase bajo extremos",
        "",
        "| Clase | Precision vigente | Sensibilidad vigente | F1 vigente | "
        "Precision maximo | Sensibilidad maximo | F1 maximo |",
        "|---|---|---|---|---|---|---|",
    ]
    for clase in sorted(metricas["vigente"]["precision"]):
        v = metricas["vigente"]
        m = metricas["maximo"]
        lineas.append(
            f"| {clase} | {_p(v['precision'][clase])} | {_p(v['sensibilidad'][clase])} | "
            f"{_p(v['f1'][clase])} | {_p(m['precision'][clase])} | "
            f"{_p(m['sensibilidad'][clase])} | {_p(m['f1'][clase])} |"
        )
    lineas += [
        "",
        f"- Macro-F1 vigente: {_p(metricas['vigente']['macro_f1'])}.",
        f"- Macro-F1 maximo: {_p(metricas['maximo']['macro_f1'])}.",
        "",
        "## Anclajes verificados",
        "",
        f"- Coincidencia: {reporte['coincidencia']['n']}/{reporte['coincidencia']['total']}.",
        f"- Sin mayoria: {len(reporte['sin_mayoria'])} casos.",
        f"- Arbitrados: {reporte['arbitraje']['arbitrados']}.",
        f"- Exactitud estricta: {exactitud['aciertos']}/{exactitud['total']}.",
        f"- Maximo: {exactitud['max']}/{exactitud['total']}.",
        "",
    ]
    return texto_json, "\n".join(lineas) + "\n"


def escribir(
    reporte: Mapping[str, object], directorio: pathlib.Path = SALIDA
) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(reporte)
    rutas = []
    for nombre, texto in ((SALIDA_JSON, texto_json), (SALIDA_MD, texto_md)):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}\n" for ruta in rutas)
    ruta_sumas = directorio / SALIDA_SHA
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(
    campana: pathlib.Path = CAMPANA, salida: pathlib.Path = SALIDA
) -> dict[str, object]:
    """Construye, verifica anclajes y escribe las salidas; aborta sin escribir si falla."""
    reporte = construir_reporte(campana)
    verificar_anclajes(reporte)
    reporte["anclajes"]["verificados"] = True
    escribir(reporte, salida)
    for ruta in (salida / SALIDA_JSON, salida / SALIDA_MD, salida / SALIDA_SHA):
        print(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}")
    return reporte


if __name__ == "__main__":
    ejecutar()
