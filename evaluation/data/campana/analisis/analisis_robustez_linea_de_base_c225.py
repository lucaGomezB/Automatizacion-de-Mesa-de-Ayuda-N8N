#!/usr/bin/env python3
"""Robustez de la brecha hibrido menos linea de base frente a la referencia (c-225).

Analisis de solo lectura, determinista y offline. No invoca a Gemini, no usa red ni base
de datos, no reclasifica ni reentrena, y no modifica el corpus, las predicciones, los
artefactos congelados ni ningun numero canonico. Es aditivo: sus cifras van a la seccion
3.36 del memo y NO reemplazan ningun valor de las secciones 3.1 a 3.35.

Entradas versionadas (solo lectura):
- `evaluation/data/campana/corpus_campana.json`: 200 casos de ajuste de la linea de base.
- `evaluation/data/campana/corpus_independiente_arbitrado.json`: referencia de los 206
  casos (consenso de `E3` y `E4`; `E5` cuando difieren).
- `evaluation/data/campana/predicciones_arbitrado.json`: prediccion congelada de
  `hybrid-v3` sobre los 206 casos.
- `evaluation/data/campana/arbitraje_tres_vias.json`: `origen` por caso
  (`consenso_e3_e4` o `arbitraje_e5`) y bandera `tres_vias`.
- `evaluation/data/campana/analisis/linea_de_base_clasica_c210.json`: anclas agregadas de
  la linea de base (`101/206` y `88/206`).

METODO COMPLETO, FIJADO EN ESTE DOCSTRING ANTES DE CORRER (preregistro)
======================================================================

El metodo y los parametros se fijan aqui antes de generar cualquier salida. El
preregistro NO es ciego: las anclas ya se conocian; lo que no se habia observado es la
brecha por subconjunto ni su intervalo.

1. Subconjuntos (D2). Se derivan de los artefactos, sin reglas ad hoc:
   `consenso_e3_e4` = casos con `origen == "consenso_e3_e4"` (`n = 142`);
   `original_150` = casos con id `I001`..`I150` (`n = 150`, diseno original sin exclusion);
   `arbitrado_completo` = todos los casos del corpus (`n = 206`). Si una cardinalidad
   difiere, el analisis termina con error y no escribe salidas.

2. Predicciones (D1). Las de la linea de base se reconstruyen con
   `evaluation.linea_de_base.predecir` (semilla 42) entrenando con los 200 casos de
   `corpus_campana.json`; las del hibrido se leen de `predicciones_arbitrado.json`. Las
   dos variantes de la linea de base son `balanceada` y `sin_repoderacion`.

3. Anclas (D3). Antes de escribir se verifica: hibrido `142/206`, `109/142` y `112/150`;
   linea de base balanceada `101/206` y sin re-ponderacion `88/206`. Si un ancla no
   coincide, el script aborta sin escribir ningun archivo.

4. Contraste (D4). Por subconjunto y por variante: tabla 2x2 de aciertos estrictos,
   McNemar con `p` exacta bilateral y corregida por continuidad (misma convencion de
   `evaluation.stats.contraste_mcnemar`; criterio exacto si `b + c < 25`) y diferencia de
   exactitudes `(b - c) / n` con IC 95 % bootstrap percentil pareado (10000 remuestreos,
   semilla 20261021). Las tres lecturas son descriptivas y no se corrigen por
   multiplicidad.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_robustez_linea_de_base_c225.json`,
`.md` y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas
byte a byte; el script imprime el SHA-256 de cada salida.

Uso (desde la raiz del replicatorio):
    python3 evaluation/data/campana/analisis/analisis_robustez_linea_de_base_c225.py
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys
from typing import Mapping, Sequence

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = SALIDA.parent
ROOT = SALIDA.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.campana import cargar_corpus_solo_lectura  # noqa: E402
from evaluation.linea_de_base import (  # noqa: E402
    RUTA_CORPUS_CAMPANA,
    SEMILLA,
    VARIANTES,
    predecir,
)
from evaluation.metrics import (  # noqa: E402
    NIVEL_CONFIANZA,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.run_evaluation import cargar_predicciones  # noqa: E402
from evaluation.stats import contraste_mcnemar  # noqa: E402

NOMBRE_BASE = "analisis_robustez_linea_de_base_c225"
SALIDA_JSON = f"{NOMBRE_BASE}.json"
SALIDA_MD = f"{NOMBRE_BASE}.md"
SALIDA_SHA = f"{NOMBRE_BASE}.SHA256SUMS.txt"

RUTA_REFERENCIA = "corpus_independiente_arbitrado.json"
RUTA_PREDICCIONES = "predicciones_arbitrado.json"
RUTA_ORIGEN = "arbitraje_tres_vias.json"

SUBCONJUNTOS = ("consenso_e3_e4", "original_150", "arbitrado_completo")
N_ESPERADO = {"consenso_e3_e4": 142, "original_150": 150, "arbitrado_completo": 206}
REMUESTREOS = 10_000
VARIANTES_LINEA_DE_BASE = tuple(nombre for nombre, _ in VARIANTES)
SISTEMAS = ("hibrido",) + VARIANTES_LINEA_DE_BASE

CRITERIO_SUBCONJUNTO = {
    "consenso_e3_e4": 'casos con origen == "consenso_e3_e4" en arbitraje_tres_vias.json',
    "original_150": "casos con id I001..I150 del corpus arbitrado (diseno original)",
    "arbitrado_completo": "todos los casos del corpus arbitrado",
}


class AnclaNoReproducida(RuntimeError):
    """Los agregados reconstruidos no coinciden con los versionados."""


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------
def cargar_ids_y_origen(ruta: pathlib.Path) -> tuple[list[str], dict[str, str]]:
    """Devuelve los ids del corpus y `caso -> origen` leidos del sidecar del arbitraje."""
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    casos = documento["casos"]
    return [caso["id"] for caso in casos], {caso["id"]: caso["origen"] for caso in casos}


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------
def _es_original_150(caso_id: str) -> bool:
    """True si el id es `I001`..`I150` (diseno original, sin exclusion)."""
    if len(caso_id) != 4 or caso_id[0] != "I" or not caso_id[1:].isdigit():
        return False
    return 1 <= int(caso_id[1:]) <= 150


def derivar_subconjuntos(
    ids: Sequence[str],
    origen: Mapping[str, str],
    n_esperado: Mapping[str, int] = N_ESPERADO,
) -> dict[str, list[str]]:
    """Deriva los tres subconjuntos y aborta si falta un origen o una cardinalidad."""
    subconjuntos = {
        "consenso_e3_e4": [],
        "original_150": [],
        "arbitrado_completo": list(ids),
    }
    for caso_id in ids:
        if caso_id not in origen:
            raise ValueError(f"caso sin origen en el sidecar del arbitraje: {caso_id}")
        if origen[caso_id] == "consenso_e3_e4":
            subconjuntos["consenso_e3_e4"].append(caso_id)
        if _es_original_150(caso_id):
            subconjuntos["original_150"].append(caso_id)
    for nombre, esperado in n_esperado.items():
        obtenido = len(subconjuntos[nombre])
        if obtenido != esperado:
            raise ValueError(
                f"cardinalidad de {nombre}: obtenido {obtenido}, esperado {esperado}"
            )
    return subconjuntos

def _diferencia_pareada(
    aciertos_a: Sequence[bool], aciertos_b: Sequence[bool], indices: Sequence[int]
) -> float:
    """Diferencia de exactitudes pareadas `(b - c) / n` sobre los indices dados."""
    return sum(int(aciertos_a[i]) - int(aciertos_b[i]) for i in indices) / len(indices)


def contraste_pareado(
    aciertos_hibrido: Sequence[bool],
    aciertos_base: Sequence[bool],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS,
) -> dict:
    """Tabla 2x2, McNemar y diferencia de exactitudes con IC bootstrap percentil pareado.

    Usa la misma convencion que `contraste_linea_de_base_c213.py` (LBP-01): `b` es
    `solo_hibrido` y `c` es `solo_linea_de_base`; la diferencia es `(b - c) / n`.
    """
    mc = contraste_mcnemar(aciertos_hibrido, aciertos_base)  # valida las longitudes
    n = mc.pares
    valor = _diferencia_pareada(aciertos_hibrido, aciertos_base, range(n)) if n else 0.0
    if mc.aplicable:
        generador = random.Random(semilla)
        muestras = [
            _diferencia_pareada(aciertos_hibrido, aciertos_base, indices)
            for indices in remuestreos_indices(generador, n, remuestreos)
        ]
        inferior, superior = percentil_intervalo(muestras, NIVEL_CONFIANZA)
    else:
        inferior = superior = valor
    return {
        "n": n,
        "aciertos": {
            "hibrido": sum(int(valor) for valor in aciertos_hibrido),
            "linea_de_base": sum(int(valor) for valor in aciertos_base),
        },
        "tabla_2x2": {
            "ambos_aciertan": mc.ambas,
            "solo_hibrido": mc.solo_a,
            "solo_linea_de_base": mc.solo_b,
            "ninguno": mc.ninguna,
        },
        "mcnemar": {
            "aplicable": mc.aplicable,
            "p_exacto": mc.p_exacto,
            "p_corregido": mc.p_corregido,
            "estadistico_corregido": mc.estadistico,
            "criterio_stats": mc.criterio,
            "p_primario_stats": mc.p_primario,
        },
        "diferencia_exactitud": {
            "definicion": "exactitud(hibrido) - exactitud(linea de base) = (b - c) / n",
            "valor": valor,
            "ic95": [inferior, superior],
            "metodo_ic": "bootstrap percentil pareado (remuestreo de casos)",
            "remuestreos": remuestreos,
            "semilla": semilla,
            "nivel_confianza": NIVEL_CONFIANZA,
        },
    }


ANCLAS_ESPERADAS = {
    "hibrido": {"consenso_e3_e4": 109, "original_150": 112, "arbitrado_completo": 142},
    "balanceada": {"arbitrado_completo": 101},
    "sin_repoderacion": {"arbitrado_completo": 88},
}


def verificar_anclas(
    observados: Mapping[str, Mapping[str, int]],
    esperados: Mapping[str, Mapping[str, int]] = ANCLAS_ESPERADAS,
) -> None:
    """Aborta con `AnclaNoReproducida` si algun acierto reconstruido difiere del versionado."""
    diferencias = []
    for sistema, por_subconjunto in esperados.items():
        for subconjunto, esperado in por_subconjunto.items():
            obtenido = observados.get(sistema, {}).get(subconjunto)
            if obtenido != esperado:
                diferencias.append(
                    f"{sistema}/{subconjunto}: reconstruido {obtenido} != versionado {esperado}"
                )
    if diferencias:
        raise AnclaNoReproducida("; ".join(diferencias))


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
def sha256(ruta: pathlib.Path, *, normalizar_lf: bool = True) -> str:
    """SHA-256 del archivo; con `normalizar_lf` colapsa CRLF a LF."""
    datos = pathlib.Path(ruta).read_bytes()
    if normalizar_lf:
        datos = datos.replace(b"\r\n", b"\n")
    return hashlib.sha256(datos).hexdigest()


def declaracion_aditiva() -> str:
    """Declaracion aditiva y de sensibilidad; las cifras canonicas no cambian."""
    return (
        "Lectura de sensibilidad/robustez: las tres brechas son descriptivas, se reportan "
        "juntas y no se corrigen por multiplicidad. No son una medicion nueva ni reemplazan "
        "ningun numero canonico: la cifra primaria 0,6893/206, el macro-F1 0,7024 y el "
        "veredicto del umbral 0,85 no cambian. Registro aditivo en la seccion 3.36 del memo."
    )


def _aciertos(
    ids: Sequence[str],
    referencia: Mapping[str, str],
    predicciones: Mapping[str, Mapping[str, str]],
) -> dict[str, list[bool]]:
    """Aciertos estrictos por sistema sobre los ids dados (mismo orden)."""
    return {
        sistema: [predicciones[sistema][caso] == referencia[caso] for caso in ids]
        for sistema in SISTEMAS
    }


def construir_documento(
    campana: pathlib.Path = CAMPANA,
    *,
    ruta_entrenamiento: pathlib.Path = RUTA_CORPUS_CAMPANA,
    anclas_esperadas: Mapping[str, Mapping[str, int]] | None = None,
    remuestreos: int = REMUESTREOS,
) -> dict:
    """Deriva los subconjuntos, reconstruye ambos clasificadores y calcula la brecha.

    Falla antes de devolver nada si falta una cardinalidad o si un ancla versionada no se
    reproduce. No escribe archivos.
    """
    ids, origen = cargar_ids_y_origen(campana / RUTA_ORIGEN)
    prueba = cargar_corpus_solo_lectura(campana / RUTA_REFERENCIA)
    if [caso.id for caso in prueba] != ids:
        raise ValueError("los ids del corpus arbitrado y del sidecar de arbitraje difieren")
    subconjuntos = derivar_subconjuntos(ids, origen)

    entrenamiento = cargar_corpus_solo_lectura(ruta_entrenamiento)
    referencia = {caso.id: caso.sector_asignado for caso in prueba}
    predicciones: dict[str, dict[str, str]] = {
        "hibrido": {
            pred.caso_id: pred.sector_predicho
            for pred in cargar_predicciones(campana / RUTA_PREDICCIONES)
        }
    }
    for nombre, class_weight in VARIANTES:
        predichos = predecir(entrenamiento, prueba, class_weight=class_weight)
        predicciones[nombre] = {
            caso.id: sector for caso, sector in zip(prueba, predichos)
        }

    booleanos_por_subconjunto = {
        nombre: _aciertos(ids_sub, referencia, predicciones)
        for nombre, ids_sub in subconjuntos.items()
    }
    aciertos = {
        sistema: {
            nombre: sum(booleanos[sistema])
            for nombre, booleanos in booleanos_por_subconjunto.items()
        }
        for sistema in SISTEMAS
    }
    esperadas = ANCLAS_ESPERADAS if anclas_esperadas is None else anclas_esperadas
    verificar_anclas(aciertos, esperadas)

    detalle = {}
    for nombre, ids_sub in subconjuntos.items():
        booleanos = booleanos_por_subconjunto[nombre]
        detalle[nombre] = {
            "criterio": CRITERIO_SUBCONJUNTO[nombre],
            "n": len(ids_sub),
            "ids": list(ids_sub),
            "aciertos": {sistema: sum(booleanos[sistema]) for sistema in SISTEMAS},
            "contrastes": {
                variante: contraste_pareado(
                    booleanos["hibrido"], booleanos[variante], remuestreos=remuestreos
                )
                for variante in VARIANTES_LINEA_DE_BASE
            },
        }

    origenes = list(origen.values())
    return {
        "change": "c-225-robustez-de-la-linea-de-base-frente-a-la-referencia",
        "generador": "evaluation/data/campana/analisis/analisis_robustez_linea_de_base_c225.py",
        "metodo": (
            "subconjuntos derivados de arbitraje_tres_vias.json y de los ids I001..I150; "
            "predicciones de la linea de base reconstruidas con evaluation.linea_de_base."
            "predecir (semilla 42) entrenando con 200 casos; predicciones del hibrido leidas "
            "de predicciones_arbitrado.json; McNemar con evaluation.stats.contraste_mcnemar; "
            "IC bootstrap percentil pareado de la diferencia de exactitudes; sin red ni Gemini"
        ),
        "semilla_linea_de_base": SEMILLA,
        "semilla_bootstrap": SEMILLA_BOOTSTRAP,
        "nivel_confianza": NIVEL_CONFIANZA,
        "remuestreos": remuestreos,
        "n_entrenamiento": len(entrenamiento),
        "entradas_sha256": {
            RUTA_CORPUS_CAMPANA.name: sha256(ruta_entrenamiento),
            RUTA_REFERENCIA: sha256(campana / RUTA_REFERENCIA),
            RUTA_PREDICCIONES: sha256(campana / RUTA_PREDICCIONES),
            RUTA_ORIGEN: sha256(campana / RUTA_ORIGEN),
        },
        "anclas_verificadas": {
            sistema: dict(por_subconjunto) for sistema, por_subconjunto in esperadas.items()
        },
        "variante_primaria": "balanceada",
        "subconjuntos": detalle,
        "contexto": {
            "arbitraje_e5": origenes.count("arbitraje_e5"),
            "tres_vias": sum(
                1
                for caso in json.loads((campana / RUTA_ORIGEN).read_text(encoding="utf-8"))[
                    "casos"
                ]
                if caso["tres_vias"]
            ),
            "nota": "particiones de contexto; no son subconjuntos de contraste",
        },
        "aditivo": {
            "reemplaza_numeros_canonicos": False,
            "seccion_memo": "3.36",
            "declaracion": declaracion_aditiva(),
        },
    }


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
def _p(valor: float | None, decimales: int = 4) -> str:
    """Numero con coma decimal (convencion de la tesis)."""
    if valor is None:
        return "n/d"
    return f"{valor:.{decimales}f}".replace(".", ",")


def _p_valor(valor: float | None) -> str:
    """Valor p: decimal si es >= 0,0001; notacion cientifica si es menor."""
    if valor is None:
        return "n/d"
    texto = f"{valor:.4f}" if valor >= 1e-4 else f"{valor:.3e}"
    return texto.replace(".", ",")


def renderizar(documento: Mapping) -> tuple[str, str]:
    """Devuelve `(json, md)` como texto con LF, UTF-8 sin BOM."""
    texto_json = (
        json.dumps(
            documento, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    )
    lineas = [
        "# Robustez de la brecha hibrido menos linea de base (c-225)",
        "",
        "Solo lectura, offline y determinista; sin red ni Gemini. "
        + documento["aditivo"]["declaracion"],
        "",
        "## Metodo",
        "",
        "- Subconjuntos: consenso `E3`/`E4` (`n = 142`), `150` originales sin exclusion "
        "(`n = 150`) y corpus arbitrado completo (`n = 206`).",
        f"- Linea de base: TF-IDF + regresion logistica, semilla "
        f"{documento['semilla_linea_de_base']}, entrenada con "
        f"{documento['n_entrenamiento']} casos; variante primaria "
        f"`{documento['variante_primaria']}`.",
        f"- IC 95 % bootstrap percentil pareado con {documento['remuestreos']} remuestreos y "
        f"semilla {documento['semilla_bootstrap']}; McNemar con `p` exacta y corregida por "
        "continuidad.",
        f"- Las particiones de contexto son `arbitraje_e5` "
        f"({documento['contexto']['arbitraje_e5']} casos) y `tres_vias` "
        f"({documento['contexto']['tres_vias']} casos); no son subconjuntos de contraste.",
    ]
    for variante, rotulo in (
        ("balanceada", "balanceada"),
        ("sin_repoderacion", "sin reponderacion"),
    ):
        lineas += [
            "",
            f"## Brecha con la linea de base {rotulo}",
            "",
            "| Subconjunto | n | Aciertos hibrido | Aciertos linea de base | "
            "Solo hibrido (b) | Solo linea de base (c) | Brecha | IC 95 % | McNemar |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for nombre in SUBCONJUNTOS:
            datos = documento["subconjuntos"][nombre]
            contraste = datos["contrastes"][variante]
            diferencia = contraste["diferencia_exactitud"]
            tabla = contraste["tabla_2x2"]
            mcnemar = contraste["mcnemar"]
            p_primario = mcnemar["p_primario_stats"]
            lineas.append(
                f"| {nombre} | {datos['n']} | {datos['aciertos']['hibrido']} | "
                f"{datos['aciertos'][variante]} | {tabla['solo_hibrido']} | "
                f"{tabla['solo_linea_de_base']} | {_p(diferencia['valor'])} | "
                f"[{_p(diferencia['ic95'][0])}; {_p(diferencia['ic95'][1])}] | "
                f"p = {_p_valor(p_primario)} ({mcnemar['criterio_stats']}) |"
            )
    lineas += [
        "",
        "## Anclas verificadas",
        "",
        "| Sistema | consenso_e3_e4 | original_150 | arbitrado_completo |",
        "|---|---|---|---|",
    ]
    for sistema in SISTEMAS:
        lineas.append(
            f"| {sistema} | "
            f"{documento['subconjuntos']['consenso_e3_e4']['aciertos'][sistema]}/{142} | "
            f"{documento['subconjuntos']['original_150']['aciertos'][sistema]}/{150} | "
            f"{documento['subconjuntos']['arbitrado_completo']['aciertos'][sistema]}/{206} |"
        )
    lineas += [
        "",
        "Las lineas de base solo tienen ancla sobre el corpus completo (101/206 y 88/206); "
        "sobre los subconjuntos se reportan sin ancla externa y su lectura es descriptiva.",
        "",
    ]
    return texto_json, "\n".join(lineas) + "\n"


def escribir(documento: Mapping, directorio: pathlib.Path = SALIDA) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(documento)
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
    campana: pathlib.Path = CAMPANA,
    salida: pathlib.Path = SALIDA,
    anclas_esperadas: Mapping[str, Mapping[str, int]] | None = None,
    remuestreos: int = REMUESTREOS,
) -> dict:
    """Construye, verifica anclas y escribe; aborta sin escribir si un ancla falla."""
    documento = construir_documento(
        campana, anclas_esperadas=anclas_esperadas, remuestreos=remuestreos
    )
    escribir(documento, salida)
    for ruta in (salida / SALIDA_JSON, salida / SALIDA_MD, salida / SALIDA_SHA):
        print(f"{sha256(ruta, normalizar_lf=False)}  {ruta.name}")
    return documento


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--remuestreos", type=int, default=REMUESTREOS)
    args = parser.parse_args(argv)
    try:
        ejecutar(salida=args.salida, remuestreos=args.remuestreos)
    except (AnclaNoReproducida, ValueError) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
