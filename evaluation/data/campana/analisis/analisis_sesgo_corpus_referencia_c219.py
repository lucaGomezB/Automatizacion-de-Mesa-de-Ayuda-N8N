#!/usr/bin/env python3
"""Sesgo de corpus y fragilidad de la referencia (c-219). PRERREGISTRO.

Este docstring congela el metodo (design.md D1-D4) ANTES de escribir codigo y de abrir
ninguna descripcion de los corpus. Solo lectura, sin red, sin Gemini, sin Docker.
Determinista. No modifica el corpus, las predicciones, el vocabulario vigente V1 ni la
configuracion productiva.

Declaracion de no ceguera (CBM-002)
-----------------------------------
El prerregistro NO es ciego en sentido estricto. El vocabulario corpus-blind lo derivo un
asistente de IA por encargo de los autores, sin haber leido ninguna descripcion de los
corpus de evaluacion, ni el vocabulario vigente V1, ni la lista de los 62 patrones
derivados del corpus; solo conocia la forma de la estructura de datos. Si leyo
`docs/prompt_gemini.txt` completo (ejemplos y reglas de frontera incluidos) y por eso
excluyo los terminos que aparecen solo alli. La independencia es PROCEDIMENTAL (no se
inspecciono el corpus al derivarlo); este analisis NO afirma que los terminos del
vocabulario no aparezcan en el corpus.

Vocabulario corpus-blind (D1)
-----------------------------
Artefacto: `vocabulario_corpus_blind_c219.json` (misma carpeta), fijado y hasheado el
2026-11-13 a las 23:52 (-03:00), ANTES de abrir descripciones y de toda medicion. Fuentes:
(1) las definiciones canonicas de los cinco sectores (`CLAUDE.md` de la raiz) y (2) el
"Glosario de terminos de ciberseguridad: una guia de aproximacion para el empresario"
(INCIBE, 2017, v1; https://www.incibe.es/sites/default/files/contenidos/guias/doc/
guia_glosario_ciberseguridad_metad.pdf; consultado el 2026-11-13). Procedimiento y origen
de cada patron: ver el JSON. El script exige que el hash del contenido del vocabulario
coincida con `SHA256_VOCABULARIO_FIJADO`; si no coincide, aborta (el vocabulario no se
modifica despues de ver resultados). Limite declarado: el glosario publico es de
ciberseguridad, no de mesa de ayuda; el vocabulario de Hardware y Software es pobre.

Etapa determinista (D2)
-----------------------
Se replica la etapa 1 del clasificador (`App/Backend/app/classifiers/deterministic.py`):
puntaje de un sector = cantidad de patrones distintos que matchean (re.IGNORECASE |
re.UNICODE); ganador unico = maximo sin empate; `score_correctitud` con las funciones
puras del backend (`extraer_features`, `score_correctitud`, pesos 0,5/0,3/0,2 y longitud
de referencia 200, `min_matches = 2`); cortocircuita si hay ganador unico y
`score_correctitud >= TAU = 0,5166`. Para cada vocabulario (V1 vigente, corpus-blind y el
control V0 de c-142, 89 patrones previos a c-71, con la logica vigente) se informa:
- cobertura = casos con al menos un match;
- cortocircuito = casos que cortocircuitan;
- aciertos y precision estricta (sector del ganador == `sector_asignado` de la referencia
  arbitrada) sobre los cortocircuitados, con IC de Wilson 95 %;
- delta frente a V1 en cobertura, cortocircuito y precision (puntos), rotulado SENSIBILIDAD
  al ajuste del vocabulario, no exactitud corregida; los conjuntos de casos
  cortocircuitados difieren entre vocabularios, y la comparacion de precision no es
  pareada.
El adaptador sobre V1 debe reproducir caso a caso al clasificador real.

Subconjuntos de la referencia (D3)
----------------------------------
Desde `arbitraje_tres_vias.json`: consenso (`origen = consenso_e3_e4`, n = 142), arbitrado
(`origen = arbitraje_e5`, n = 64), tres vias (`tres_vias = true`, n = 6, subconjunto de los
arbitrados) y total (206). Exactitud estricta del hibrido congelado (hybrid-v3) en cada uno
con Wilson; la exactitud laxa (la prediccion coincide con el sector asignado o con uno de
sus sectores adicionales) se informa aparte. El subconjunto literal E3 = E4 = E5 es VACIO
por construccion (E5 solo etiqueto los 64 discordantes): se declara como hallazgo y no se
fuerza. No se afirma causalidad de la referencia.

Anclajes a reproducir antes de medir (si alguno falla, aborta sin escribir)
---------------------------------------------------------------------------
206 casos, 476 filas de etiquetado, 142 consenso, 64 arbitrados, 6 tres vias; etapa
determinista V1: cobertura 131, cortocircuito 115, aciertos 88/115 (0,7652); hibrido
142/206 (0,6893); consenso 109/142, arbitrado 33/64.

Salidas (D4)
------------
`analisis_sesgo_corpus_referencia_c219.json`, `.md` y `.SHA256SUMS.txt` en esta carpeta,
UTF-8 sin BOM y LF; dos corridas son identicas byte a byte.

Uso (desde la raiz del repositorio, con las variables dummy del CI fijadas)::

    python evaluation/data/campana/analisis/analisis_sesgo_corpus_referencia_c219.py
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import os
import pathlib
import re
import sys
from typing import Mapping, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import intervalo_wilson  # noqa: E402

SALIDA = pathlib.Path(__file__).resolve().parent
CAMPANA = ROOT / "evaluation/data/campana"
RUTA_CORPUS = CAMPANA / "corpus_independiente_arbitrado.json"
RUTA_PREDICCIONES = CAMPANA / "predicciones_arbitrado.json"
RUTA_ETIQUETADO = CAMPANA / "doble_etiquetado_arbitrado.csv"
RUTA_ARBITRAJE = CAMPANA / "arbitraje_tres_vias.json"
RUTA_VOCABULARIO = SALIDA / "vocabulario_corpus_blind_c219.json"
RUTA_V0 = ROOT / "evaluation/data/sensibilidad_ajustes/keywords_pre_c71.json"

NOMBRE_BASE = "analisis_sesgo_corpus_referencia_c219"

CLASES_CANONICAS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)

# Hash del contenido del vocabulario corpus-blind, fijado el 2026-11-13 antes de medir.
SHA256_VOCABULARIO_FIJADO = "ec350b9615410defe531183e317c197a21f778638eb5ccccdbe9a77b2a34d581"

# Logica vigente de la etapa determinista (settings.py del backend).
TAU = 0.5166
MIN_MATCHES = 2
PESO_MARGEN = 0.5
PESO_EVIDENCIA = 0.3
PESO_DENSIDAD = 0.2
LONGITUD_REFERENCIA = 200.0

N_CASOS = 206
N_ETIQUETADO = 476
N_CONSENSO = 142
N_ARBITRADOS = 64
N_TRES_VIAS = 6
ANCLA_CORTOCIRCUITO = 115
ANCLA_ACIERTOS_DET = 88
ANCLA_ACIERTOS_HIBRIDO = 142
ANCLA_COBERTURA = 131
ANCLA_MACRO_F1 = 0.7024
ANCLA_CONSENSO = (109, 142)
ANCLA_ARBITRADO = (33, 64)

ORIGEN_CONSENSO = "consenso_e3_e4"
ORIGEN_ARBITRADO = "arbitraje_e5"

ENTORNO_OFFLINE = {
    "DATABASE_URL": "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy",
    "GEMINI_API_KEY": "offline-dummy-key-sin-llamadas",  # gitleaks:allow (ficticio)
    "PSEUDONYMIZATION_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",  # gitleaks:allow (ficticio)
    "JWT_SECRET_KEY": "ci-dummy-jwt-secret-key-for-testing-only",  # gitleaks:allow (ficticio)
    "COST_GUARD_CALLER_HMAC_KEY": "ci-dummy-cost-guard-caller-hmac-key",  # gitleaks:allow (ficticio)
    "DIRECTORY_BLIND_INDEX_KEY": "ci-dummy-directory-blind-index-key",  # gitleaks:allow (ficticio)
}


class EntradaInconsistente(ValueError):
    """Los conteos, los identificadores o el vocabulario no coinciden con lo esperado."""


class AnclaNoReproducida(ValueError):
    """Un anclaje canonico no se reproduce: no se escribe ninguna salida."""


def sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Etapa determinista con un vocabulario arbitrario
# ---------------------------------------------------------------------------
def _funciones_backend():
    """Funciones puras del backend (diferidas: requieren `App/Backend` en sys.path)."""
    backend = str(ROOT / "App" / "Backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.classifiers.deterministic import (  # type: ignore
        PesosScore,
        extraer_features,
        score_correctitud,
    )

    return PesosScore, extraer_features, score_correctitud


def compilar_vocabulario(vocabulario: Mapping[str, Sequence[str]]) -> dict[str, list[re.Pattern]]:
    return {
        clase: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patrones]
        for clase, patrones in vocabulario.items()
    }


def puntuar_sectores(texto: str, compilado: Mapping[str, Sequence[re.Pattern]]) -> dict[str, float]:
    """Cantidad de patrones distintos que matchean, por sector."""
    return {
        clase: float(sum(1 for patron in patrones if patron.search(texto)))
        for clase, patrones in compilado.items()
    }


def evaluar_texto(
    texto: str,
    compilado: Mapping[str, Sequence[re.Pattern]],
    *,
    tau: float = TAU,
    min_matches: int = MIN_MATCHES,
) -> dict:
    """Replica la etapa 1: ganador unico, `score_correctitud` y cortocircuito."""
    PesosScore, extraer_features, score_correctitud = _funciones_backend()
    puntajes = puntuar_sectores(texto, compilado)
    maximo = max(puntajes.values()) if puntajes else 0.0
    cubierto = maximo > 0.0
    ganadores = [c for c, v in puntajes.items() if v == maximo] if cubierto else []
    sector = ganadores[0] if len(ganadores) == 1 else None
    score = 0.0
    if sector is not None:
        features = extraer_features(puntajes, text_length=len(texto), min_matches=min_matches)
        pesos = PesosScore(PESO_MARGEN, PESO_EVIDENCIA, PESO_DENSIDAD, LONGITUD_REFERENCIA)
        score = score_correctitud(features, pesos)
    return {
        "puntajes": puntajes,
        "cubierto": cubierto,
        "sector": sector,
        "score_correctitud": score,
        "cortocircuita": sector is not None and score >= tau,
    }


def metricas_vocabulario(
    evaluaciones: Mapping[str, dict], referencia: Mapping[str, str]
) -> dict:
    """Cobertura, cortocircuito y precision estricta (Wilson) de un vocabulario."""
    cortos = [c for c, e in evaluaciones.items() if e["cortocircuita"]]
    aciertos = sum(1 for c in cortos if evaluaciones[c]["sector"] == referencia[c])
    return {
        "casos": len(evaluaciones),
        "cobertura": sum(1 for e in evaluaciones.values() if e["cubierto"]),
        "cortocircuito": len(cortos),
        "aciertos": aciertos,
        "precision": aciertos / len(cortos) if cortos else None,
        "ic_precision": intervalo_wilson(aciertos, len(cortos)),
    }


def delta_frente_a(metricas: Mapping, base: Mapping) -> dict:
    """Diferencia frente a la base (sensibilidad; conjuntos de casos distintos)."""
    if metricas["precision"] is None or base["precision"] is None:
        puntos = None
    else:
        puntos = (metricas["precision"] - base["precision"]) * 100.0
    return {
        "cobertura": metricas["cobertura"] - base["cobertura"],
        "cortocircuito": metricas["cortocircuito"] - base["cortocircuito"],
        "precision_puntos": puntos,
    }


# ---------------------------------------------------------------------------
# Subconjuntos de la referencia
# ---------------------------------------------------------------------------
def construir_subconjuntos(origen: Mapping[str, str], tres_vias_ids: Sequence[str]) -> dict:
    desconocidos = sorted({v for v in origen.values() if v not in (ORIGEN_CONSENSO, ORIGEN_ARBITRADO)})
    if desconocidos:
        raise EntradaInconsistente(f"Origen de referencia desconocido: {desconocidos}")
    consenso = sorted(c for c, v in origen.items() if v == ORIGEN_CONSENSO)
    arbitrado = sorted(c for c, v in origen.items() if v == ORIGEN_ARBITRADO)
    fuera = [c for c in tres_vias_ids if c not in set(arbitrado)]
    if fuera:
        raise EntradaInconsistente(f"Casos de tres vias que no son arbitrados: {fuera}")
    return {
        "consenso": consenso,
        "arbitrado": arbitrado,
        "tres_vias": sorted(tres_vias_ids),
        "total": sorted(origen),
    }


def conjunto_e3_e4_e5(etiquetas: Mapping[str, Mapping[str, str]]) -> list[str]:
    """Casos con E3, E4 y E5 etiquetados y coincidentes (vacio por construccion)."""
    ids = []
    for caso, por_etiquetador in sorted(etiquetas.items()):
        if all(e in por_etiquetador for e in ("E3", "E4", "E5")) and (
            por_etiquetador["E3"] == por_etiquetador["E4"] == por_etiquetador["E5"]
        ):
            ids.append(caso)
    return ids


def exactitud_subconjunto(
    ids: Sequence[str],
    referencia: Mapping[str, str],
    predicciones: Mapping[str, str],
    adicionales: Mapping[str, Sequence[str]],
) -> dict:
    """Exactitud estricta (y laxa, aparte) del clasificador en un subconjunto."""
    estrictos = sum(1 for c in ids if predicciones[c] == referencia[c])
    laxos = sum(
        1
        for c in ids
        if predicciones[c] == referencia[c] or predicciones[c] in adicionales.get(c, ())
    )
    n = len(ids)
    return {
        "casos": n,
        "aciertos": estrictos,
        "exactitud": estrictos / n if n else None,
        "ic": intervalo_wilson(estrictos, n),
        "aciertos_laxos": laxos,
        "exactitud_laxa": laxos / n if n else None,
        "ic_laxa": intervalo_wilson(laxos, n),
    }


# ---------------------------------------------------------------------------
# Vocabulario corpus-blind y anclajes
# ---------------------------------------------------------------------------
def hash_vocabulario(vocabulario: Mapping[str, Sequence[str]]) -> str:
    canonico = json.dumps(
        {k: list(v) for k, v in vocabulario.items()},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def cargar_vocabulario_corpus_blind(ruta: pathlib.Path = RUTA_VOCABULARIO) -> dict[str, list[str]]:
    documento = json.loads(ruta.read_text(encoding="utf-8"))
    vocabulario = documento["vocabulario"]
    if set(vocabulario) != set(CLASES_CANONICAS) or not all(vocabulario.values()):
        raise EntradaInconsistente("El vocabulario corpus-blind no cubre las cinco clases canonicas")
    if hash_vocabulario(vocabulario) != SHA256_VOCABULARIO_FIJADO:
        raise EntradaInconsistente(
            "El vocabulario corpus-blind no coincide con el hash fijado antes de medir"
        )
    return vocabulario


def verificar_anclajes(*, cortocircuito: int, aciertos_det: int, aciertos_hibrido: int, n: int) -> None:
    esperados = {
        "cortocircuito": (cortocircuito, ANCLA_CORTOCIRCUITO),
        "aciertos_det": (aciertos_det, ANCLA_ACIERTOS_DET),
        "aciertos_hibrido": (aciertos_hibrido, ANCLA_ACIERTOS_HIBRIDO),
        "n": (n, N_CASOS),
    }
    diferencias = [f"{k}: {obs} != {esp}" for k, (obs, esp) in esperados.items() if obs != esp]
    if diferencias:
        raise AnclaNoReproducida("; ".join(diferencias))


# ---------------------------------------------------------------------------
# Lectura de entradas
# ---------------------------------------------------------------------------
def cargar_entradas(
    ruta_corpus: pathlib.Path = RUTA_CORPUS,
    ruta_predicciones: pathlib.Path = RUTA_PREDICCIONES,
    ruta_etiquetado: pathlib.Path = RUTA_ETIQUETADO,
    ruta_arbitraje: pathlib.Path = RUTA_ARBITRAJE,
) -> dict:
    """Lee y valida los cuatro artefactos versionados; no escribe nada ni imprime texto."""
    corpus = json.loads(ruta_corpus.read_text(encoding="utf-8"))
    casos = corpus["casos"]
    referencia = {c["id"]: c["sector_asignado"] for c in casos}
    if len(referencia) != len(casos):
        raise EntradaInconsistente("Identificadores de caso duplicados en el corpus")
    descripciones = {c["id"]: c["descripcion"] for c in casos}
    adicionales = {c["id"]: list(c.get("sectores_adicionales") or []) for c in casos}

    crudas = json.loads(ruta_predicciones.read_text(encoding="utf-8"))
    filas_pred = crudas["predictions"]
    predicciones = {p["caso_id"]: p["sector_predicho"] for p in filas_pred}
    etapas = {p["caso_id"]: p["etapa"] for p in filas_pred}

    etiquetas: dict[str, dict[str, str]] = {}
    filas = 0
    with ruta_etiquetado.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            filas += 1
            etiquetas.setdefault(fila["id_caso"], {})[fila["id_etiquetador"]] = fila["sector_etiquetado"]

    arbitraje = json.loads(ruta_arbitraje.read_text(encoding="utf-8"))
    origen = {c["id"]: c["origen"] for c in arbitraje["casos"]}
    tres_vias_ids = [c["id"] for c in arbitraje["casos"] if c["tres_vias"]]

    subconjuntos = construir_subconjuntos(origen, tres_vias_ids)
    conteos = {
        "casos": len(referencia),
        "filas_etiquetado": filas,
        "consenso": len(subconjuntos["consenso"]),
        "arbitrados_e5": len(subconjuntos["arbitrado"]),
        "tres_vias": len(subconjuntos["tres_vias"]),
        "predicciones": len(predicciones),
    }
    esperados = {
        "casos": N_CASOS,
        "filas_etiquetado": N_ETIQUETADO,
        "consenso": N_CONSENSO,
        "arbitrados_e5": N_ARBITRADOS,
        "tres_vias": N_TRES_VIAS,
        "predicciones": N_CASOS,
    }
    diferencias = [f"{k}: {conteos[k]} != {v}" for k, v in esperados.items() if conteos[k] != v]
    if diferencias:
        raise EntradaInconsistente("; ".join(diferencias))
    if set(origen) != set(referencia) or set(predicciones) != set(referencia):
        raise EntradaInconsistente("El corpus, las predicciones y el arbitraje no cubren los mismos casos")
    if set(etiquetas) != set(referencia):
        raise EntradaInconsistente("El etiquetado no cubre los mismos casos que el corpus")
    return {
        "referencia": referencia,
        "descripciones": descripciones,
        "adicionales": adicionales,
        "predicciones": predicciones,
        "etapas": etapas,
        "filas_predicciones": filas_pred,
        "etiquetas": etiquetas,
        "subconjuntos": subconjuntos,
        "conteos": conteos,
        "entradas_sha256": {
            ruta.name: sha256(ruta)
            for ruta in (ruta_corpus, ruta_predicciones, ruta_etiquetado, ruta_arbitraje)
        },
    }


@contextlib.contextmanager
def _sin_env_local():
    """Ejecuta en una carpeta sin `.env`: `Settings` lee `.env` del directorio actual y el
    de la raiz tiene valores reales que no deben cargarse ni imprimirse."""
    anterior = pathlib.Path.cwd()
    os.chdir(SALIDA)
    try:
        yield
    finally:
        os.chdir(anterior)


def aplicar_entorno_offline() -> None:
    """Fija las variables inertes del CI para construir `Settings` sin credenciales reales."""
    for clave, valor in ENTORNO_OFFLINE.items():
        os.environ[clave] = valor
    try:  # silencia los eventos debug del clasificador (imprimen puntajes por caso)
        import logging

        import structlog

        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING))
    except ImportError:
        pass


def vocabulario_vigente() -> dict[str, list[str]]:
    """Vocabulario V1 vigente (solo lectura; se importa del backend sin modificarlo)."""
    _funciones_backend()
    from app.classifiers.keywords import KEYWORD_MAP  # type: ignore

    return {clase: list(patrones) for clase, patrones in KEYWORD_MAP.items()}


def vocabulario_previo_v0(ruta: pathlib.Path = RUTA_V0) -> dict[str, list[str]]:
    """Control V0 de c-142: 89 patrones previos a c-71 (artefacto versionado)."""
    v0 = json.loads(ruta.read_text(encoding="utf-8"))
    if set(v0) != set(CLASES_CANONICAS):
        raise EntradaInconsistente("V0 no cubre las cinco clases canonicas")
    return {clase: list(v0[clase]) for clase in CLASES_CANONICAS}


def _contar(vocabulario: Mapping[str, Sequence[str]]) -> dict[str, int]:
    return {clase: len(vocabulario[clase]) for clase in CLASES_CANONICAS}


def evaluar_corpus(descripciones: Mapping[str, str], vocabulario: Mapping[str, Sequence[str]]) -> dict[str, dict]:
    compilado = compilar_vocabulario(vocabulario)
    return {caso: evaluar_texto(texto, compilado) for caso, texto in sorted(descripciones.items())}


def _comun_con_v1(evaluaciones: Mapping[str, dict], v1: Mapping[str, dict], referencia: Mapping[str, str]) -> dict:
    """Pareado sobre los casos que cortocircuitan en ambos vocabularios."""
    comunes = [c for c in evaluaciones if evaluaciones[c]["cortocircuita"] and v1[c]["cortocircuita"]]
    return {
        "casos": len(comunes),
        "aciertos_vocabulario": sum(1 for c in comunes if evaluaciones[c]["sector"] == referencia[c]),
        "aciertos_v1": sum(1 for c in comunes if v1[c]["sector"] == referencia[c]),
        "mismo_sector": sum(1 for c in comunes if evaluaciones[c]["sector"] == v1[c]["sector"]),
    }


def construir_documento(entradas: dict | None = None) -> dict:
    """Verifica anclajes y mide; lanza ante cualquier inconsistencia (no escribe nada)."""
    with _sin_env_local():
        return _construir_documento(entradas)


def _construir_documento(entradas: dict | None) -> dict:
    from evaluation.calibracion_gate import (  # noqa: E402
        cargar_clasificador_deterministico,
        recomputar_senales_reglas,
        verificar_reproduccion_cortocircuito,
    )
    from evaluation.metrics import f1_macro, f1_por_clase, matriz_confusion  # noqa: E402

    aplicar_entorno_offline()
    entradas = entradas if entradas is not None else cargar_entradas()
    referencia = entradas["referencia"]
    descripciones = entradas["descripciones"]
    predicciones = entradas["predicciones"]
    sub = entradas["subconjuntos"]

    # --- Vocabularios (el corpus-blind se valida contra el hash fijado antes de medir) ---
    v_blind = cargar_vocabulario_corpus_blind()
    v1 = vocabulario_vigente()
    v0 = vocabulario_previo_v0()
    patrones_v1 = sum(len(v) for v in v1.values())
    patrones_v0 = sum(len(v) for v in v0.values())
    solo_v1 = sum(len(set(v1[c]) - set(v0[c])) for c in CLASES_CANONICAS)
    v0_incluido = all(set(v0[c]) <= set(v1[c]) for c in CLASES_CANONICAS)
    if (patrones_v1, patrones_v0, solo_v1) != (151, 89, 62) or not v0_incluido:
        raise AnclaNoReproducida(
            f"V1/V0/derivados del corpus: {patrones_v1}/{patrones_v0}/{solo_v1}, V0 incluido: {v0_incluido}"
        )

    # --- Anclaje 1: la etapa determinista real reproduce la cache (deriva = aborta) ---
    clasificador = cargar_clasificador_deterministico()
    filas_pred = [
        {
            "caso_id": p["caso_id"],
            "descripcion": descripciones[p["caso_id"]],
            "etapa": p["etapa"],
            "sector_predicho": p["sector_predicho"],
        }
        for p in entradas["filas_predicciones"]
    ]
    senales = recomputar_senales_reglas(filas_pred, clasificador)
    try:
        verificar_reproduccion_cortocircuito(senales, filas_pred)
    except ValueError as error:
        raise AnclaNoReproducida(str(error)) from error

    # --- Anclaje 2: el adaptador sobre V1 reproduce caso a caso al clasificador real ---
    ev_v1 = evaluar_corpus(descripciones, v1)
    reales = {s["caso_id"]: s for s in senales}
    distintos = [
        c
        for c, e in ev_v1.items()
        if e["cortocircuita"] != reales[c]["cortocircuita"]
        or (e["cortocircuita"] and e["sector"] != reales[c]["sector_reglas"])
    ]
    if distintos:
        raise AnclaNoReproducida(f"El adaptador difiere del clasificador real en {len(distintos)} casos")

    m_v1 = metricas_vocabulario(ev_v1, referencia)
    hibrido = exactitud_subconjunto(sub["total"], referencia, predicciones, entradas["adicionales"])
    verificar_anclajes(
        cortocircuito=m_v1["cortocircuito"],
        aciertos_det=m_v1["aciertos"],
        aciertos_hibrido=hibrido["aciertos"],
        n=len(referencia),
    )
    orden = sorted(referencia)
    macro_f1 = f1_macro(
        f1_por_clase(matriz_confusion([referencia[c] for c in orden], [predicciones[c] for c in orden]))
    )
    if abs(macro_f1 - ANCLA_MACRO_F1) > 5e-5:
        raise AnclaNoReproducida(f"macro-F1 {macro_f1:.4f} != {ANCLA_MACRO_F1}")
    anclajes = {
        "casos": len(referencia),
        "cortocircuito_v1": m_v1["cortocircuito"],
        "aciertos_det_v1": m_v1["aciertos"],
        "precision_det_v1": m_v1["precision"],
        "cobertura_v1": m_v1["cobertura"],
        "aciertos_hibrido": hibrido["aciertos"],
        "exactitud_hibrido": hibrido["exactitud"],
        "macro_f1_hibrido": macro_f1,
        "cobertura_esperada_131": ANCLA_COBERTURA,
        "cobertura_reproduce_131": m_v1["cobertura"] == ANCLA_COBERTURA,
        "patrones": {"v1": patrones_v1, "v0": patrones_v0, "derivados_del_corpus": solo_v1},
    }

    # --- Mediciones ---
    ev_blind = evaluar_corpus(descripciones, v_blind)
    ev_v0 = evaluar_corpus(descripciones, v0)
    m_blind = metricas_vocabulario(ev_blind, referencia)
    m_v0 = metricas_vocabulario(ev_v0, referencia)
    vocabularios = {
        "v1": {"nombre": "V1 vigente", "patrones": _contar(v1), **m_v1},
        "corpus_blind": {
            "nombre": "Corpus-blind (fuente externa)",
            "patrones": _contar(v_blind),
            **m_blind,
            "delta_frente_a_v1": delta_frente_a(m_blind, m_v1),
            "comun_con_v1": _comun_con_v1(ev_blind, ev_v1, referencia),
        },
        "v0": {
            "nombre": "V0 (control de c-142, 89 patrones previos a c-71)",
            "patrones": _contar(v0),
            **m_v0,
            "delta_frente_a_v1": delta_frente_a(m_v0, m_v1),
            "comun_con_v1": _comun_con_v1(ev_v0, ev_v1, referencia),
        },
    }

    subconjuntos = {
        nombre: exactitud_subconjunto(ids, referencia, predicciones, entradas["adicionales"])
        for nombre, ids in (
            ("consenso", sub["consenso"]),
            ("arbitrado", sub["arbitrado"]),
            ("tres_vias", sub["tres_vias"]),
            ("total", sub["total"]),
        )
    }
    if (subconjuntos["consenso"]["aciertos"], subconjuntos["consenso"]["casos"]) != ANCLA_CONSENSO:
        raise AnclaNoReproducida("consenso no reproduce 109/142")
    if (subconjuntos["arbitrado"]["aciertos"], subconjuntos["arbitrado"]["casos"]) != ANCLA_ARBITRADO:
        raise AnclaNoReproducida("arbitrado no reproduce 33/64")
    triple = conjunto_e3_e4_e5(entradas["etiquetas"])

    vocab_json = json.loads(RUTA_VOCABULARIO.read_text(encoding="utf-8"))
    return {
        "analisis": NOMBRE_BASE,
        "rotulo": "sensibilidad (no exactitud corregida; la referencia no se afirma causal)",
        "entradas": {
            "conteos": entradas["conteos"],
            "sha256": {
                **entradas["entradas_sha256"],
                RUTA_VOCABULARIO.name: sha256(RUTA_VOCABULARIO),
                RUTA_V0.name: sha256(RUTA_V0),
            },
        },
        "vocabulario_corpus_blind": {
            "derivado_en": vocab_json["derivado_en"],
            "sha256_contenido": hash_vocabulario(v_blind),
            "independencia": vocab_json["independencia"]["tipo"],
            "fuente_publica": vocab_json["fuentes"][1]["titulo"],
            "organizacion": vocab_json["fuentes"][1]["organizacion"],
            "url": vocab_json["fuentes"][1]["url"],
            "consultada": vocab_json["fuentes"][1]["consultada"],
        },
        "anclajes": anclajes,
        "vocabularios": vocabularios,
        "subconjuntos": subconjuntos,
        "conjunto_literal_e3_e4_e5": {"casos": len(triple), "ids": triple},
    }


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------
def _num(valor, decimales: int = 4) -> str:
    return "n/d" if valor is None else f"{valor:.{decimales}f}".replace(".", ",")


def _ic(par) -> str:
    return f"[{_num(par[0])}; {_num(par[1])}]"


def _puntos(valor) -> str:
    return "n/d" if valor is None else f"{valor:+.1f}".replace(".", ",")


def renderizar(doc: dict) -> tuple[str, str]:
    texto_json = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    voc = doc["vocabularios"]
    sub = doc["subconjuntos"]
    ancla = doc["anclajes"]
    vb = doc["vocabulario_corpus_blind"]
    lineas = [
        "# Sesgo de corpus y fragilidad de la referencia (c-219)",
        "",
        "Analisis offline, de solo lectura y determinista, sin red ni Gemini. Los resultados se",
        "rotulan como **sensibilidad**: no son una exactitud corregida ni afirman que la",
        "referencia cause las diferencias. Metodo prerregistrado en el docstring del script.",
        "",
        "## Anclajes reproducidos antes de medir",
        "",
        f"- Casos: {ancla['casos']}. Etapa determinista V1: cortocircuito {ancla['cortocircuito_v1']}, "
        f"aciertos {ancla['aciertos_det_v1']}/{ancla['cortocircuito_v1']} ({_num(ancla['precision_det_v1'])}).",
        f"- Cobertura de V1 (casos con al menos un match): {ancla['cobertura_v1']} "
        f"(esperada {ancla['cobertura_esperada_131']}; reproduce: {'si' if ancla['cobertura_reproduce_131'] else 'no'}).",
        f"- Hibrido congelado: {ancla['aciertos_hibrido']}/{ancla['casos']} ({_num(ancla['exactitud_hibrido'])}), macro-F1 {_num(ancla['macro_f1_hibrido'])}.",
        f"- Patrones: V1 {ancla['patrones']['v1']}, V0 {ancla['patrones']['v0']}, "
        f"derivados del corpus {ancla['patrones']['derivados_del_corpus']} (V1 menos V0).",
        "",
        "## Vocabulario corpus-blind",
        "",
        f"- Fuente publica: {vb['fuente_publica']} ({vb['organizacion']}), {vb['url']}, consultada el {vb['consultada']}.",
        "- Mas las definiciones canonicas de los cinco sectores (`CLAUDE.md`).",
        f"- Derivado el {vb['derivado_en']}; SHA-256 del contenido: `{vb['sha256_contenido']}`.",
        f"- Independencia: {vb['independencia']}. No se afirma que sus terminos no aparezcan en el corpus.",
        "",
        "## Etapa determinista por vocabulario (n = 206)",
        "",
        "| Vocabulario | Patrones | Cobertura | Cortocircuito | Aciertos | Precision | IC 95 % Wilson | "
        "Delta cobertura | Delta cortocircuito | Delta precision (puntos) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for clave in ("v1", "corpus_blind", "v0"):
        v = voc[clave]
        d = v.get("delta_frente_a_v1")
        lineas.append(
            f"| {v['nombre']} | {sum(v['patrones'].values())} | {v['cobertura']} | {v['cortocircuito']} | "
            f"{v['aciertos']} | {_num(v['precision'])} | {_ic(v['ic_precision'])} | "
            f"{'-' if d is None else d['cobertura']} | {'-' if d is None else d['cortocircuito']} | "
            f"{'-' if d is None else _puntos(d['precision_puntos'])} |"
        )
    lineas += [
        "",
        "Los conjuntos de casos cortocircuitados difieren entre vocabularios: la diferencia de",
        "precision no es pareada. Pareado sobre los casos que cortocircuitan en ambos:",
        "",
        "| Vocabulario | Casos comunes con V1 | Aciertos del vocabulario | Aciertos de V1 | Mismo sector |",
        "|---|---|---|---|---|",
    ]
    for clave in ("corpus_blind", "v0"):
        c = voc[clave]["comun_con_v1"]
        lineas.append(
            f"| {voc[clave]['nombre']} | {c['casos']} | {c['aciertos_vocabulario']} | {c['aciertos_v1']} | {c['mismo_sector']} |"
        )
    lineas += [
        "",
        "## Exactitud estricta del hibrido congelado por subconjunto de la referencia",
        "",
        "| Subconjunto | Casos | Aciertos | Exactitud | IC 95 % Wilson | Exactitud laxa |",
        "|---|---|---|---|---|---|",
    ]
    for clave, etiqueta in (
        ("consenso", "Consenso E3 = E4"),
        ("arbitrado", "Arbitrado por E5"),
        ("tres_vias", "Discordancia de tres vias (subconjunto de los arbitrados)"),
        ("total", "Total"),
    ):
        s = sub[clave]
        lineas.append(
            f"| {etiqueta} | {s['casos']} | {s['aciertos']} | {_num(s['exactitud'])} | {_ic(s['ic'])} | {_num(s['exactitud_laxa'])} |"
        )
    lineas += [
        "",
        f"El subconjunto literal E3 = E4 = E5 tiene {doc['conjunto_literal_e3_e4_e5']['casos']} casos: es vacio por",
        "construccion, porque E5 solo etiqueto los 64 casos discordantes. No se fuerza un subconjunto.",
        "La diferencia entre subconjuntos es descriptiva; no se afirma que la referencia la cause.",
        "",
        "## Entradas (SHA-256)",
        "",
    ]
    for nombre, huella in sorted(doc["entradas"]["sha256"].items()):
        lineas.append(f"- `{nombre}`: `{huella}`")
    lineas.append("")
    return texto_json, "\n".join(lineas)


def escribir(doc: dict, directorio: pathlib.Path = SALIDA, nombre_base: str = NOMBRE_BASE) -> list[pathlib.Path]:
    """Escribe `.json`, `.md` y `.SHA256SUMS.txt` (UTF-8 sin BOM, LF)."""
    directorio.mkdir(parents=True, exist_ok=True)
    texto_json, texto_md = renderizar(doc)
    rutas = []
    for nombre, texto in ((f"{nombre_base}.json", texto_json), (f"{nombre_base}.md", texto_md)):
        ruta = directorio / nombre
        ruta.write_bytes(texto.encode("utf-8"))
        rutas.append(ruta)
    sumas = "".join(f"{sha256(r)}  {r.name}\n" for r in rutas)
    ruta_sumas = directorio / f"{nombre_base}.SHA256SUMS.txt"
    ruta_sumas.write_bytes(sumas.encode("utf-8"))
    rutas.append(ruta_sumas)
    return rutas


def ejecutar(salida: pathlib.Path = SALIDA, nombre_base: str = NOMBRE_BASE) -> list[pathlib.Path]:
    """Construye y escribe el analisis; no escribe si un ancla no se reproduce."""
    return escribir(construir_documento(), salida, nombre_base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sesgo de corpus y referencia (c-219)")
    parser.add_argument("--salida", type=pathlib.Path, default=SALIDA)
    parser.add_argument("--nombre", default=NOMBRE_BASE)
    args = parser.parse_args(argv)
    try:
        rutas = ejecutar(args.salida, args.nombre)
    except (AnclaNoReproducida, EntradaInconsistente) as error:
        print(f"ABORTA sin escribir salidas: {error}", file=sys.stderr)
        return 1
    except ValueError as error:  # p. ej. validacion de Settings: no se imprime su contenido
        print(f"ABORTA sin escribir salidas: {type(error).__name__}", file=sys.stderr)
        return 1
    for ruta in rutas:
        print(f"{sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
