"""
Huella canonica de las predicciones oficiales (c-131, D10).

Test de CARACTERIZACION DE DATOS, no de TDD: no conduce codigo de produccion y por
eso no sigue el ciclo RED/GREEN. Verifica que las predicciones oficiales
(`hybrid-v3`, corrida del 2026-10-07) reproducen los agregados canonicos de la
tesis. Sirve de oraculo para aceptar o rechazar una cache como fuente.

Fuente de datos (fallback documentado): primero `evaluation/predicciones.json`
(copia viva, ignorada por git); si falta, la copia congelada y versionada de
`evaluation/evidence/` (c-143). Asi el test corre PASSED en CI sin versionar la
copia viva. Sin ninguna de las dos, SKIPPED.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from evaluation.metrics import (
    calibracion_por_bandas,
    calibracion_por_etapa,
    contingencia_confianza,
    desglose_exactitud,
    distribucion_confianza,
    ETAPAS_PIPELINE,
    resumen_exactitud,
)

_REPO = pathlib.Path(__file__).resolve().parents[2]
_VIVA = _REPO / "evaluation" / "predicciones.json"
_EVIDENCIA = _REPO / "evaluation" / "evidence" / "predicciones_hybrid-v3_2026-10-07.json"
_CORPUS = _REPO / "data" / "corpus_evaluacion_pseudonimizado.json"
CRLF = bytes([13, 10])
LF = bytes([10])
HASH_CANONICO = "1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb"


def _ruta_predicciones():
    for ruta in (_VIVA, _EVIDENCIA):
        if ruta.exists():
            return ruta
    return None


_RUTA = _ruta_predicciones()
_hay_cache = pytest.mark.skipif(
    _RUTA is None or not _CORPUS.exists(),
    reason="ni evaluation/predicciones.json ni la evidencia de evaluation/evidence/ (o el corpus) estan presentes",
)


@pytest.fixture(scope="module")
def datos():
    from evaluation.corpus import cargar_corpus

    contenido = json.loads(_RUTA.read_text(encoding="utf-8"))
    predicciones = contenido["predictions"]
    corpus = cargar_corpus(_CORPUS)
    assert [p["caso_id"] for p in predicciones] == [c.id for c in corpus]
    return {
        "meta": contenido["cache_meta"],
        "reales": [c.sector_asignado for c in corpus],
        "predichos": [p["sector_predicho"] for p in predicciones],
        "verdad": [c.conjunto_verdad for c in corpus],
        "confianzas": [p["confianza"] for p in predicciones],
        "etapas": [p["etapa"] for p in predicciones],
        "canales": [c.canal_origen for c in corpus],
    }


@_hay_cache
def test_metadata_de_la_corrida_oficial(datos):
    meta = datos["meta"]
    assert meta["corpus_hash"] == HASH_CANONICO
    assert meta["corpus_count"] == 200
    assert meta["classifier_version"] == "hybrid-v3"
    assert meta["generated_at"].startswith("2026-10-07")


@_hay_cache
def test_exactitud_global_y_etapas(datos):
    global_ = resumen_exactitud(datos["reales"], datos["predichos"], datos["verdad"])
    assert (global_.aciertos_estrictos, global_.casos) == (147, 200)
    por_etapa = desglose_exactitud(
        datos["etapas"], datos["reales"], datos["predichos"], datos["verdad"],
        orden=ETAPAS_PIPELINE,
    )
    assert [(e, r.casos) for e, r in por_etapa.items()] == [
        ("deterministic", 131), ("gemini", 69), ("fallback", 0)
    ]
    assert por_etapa["deterministic"].aciertos_estrictos == 97
    assert por_etapa["gemini"].aciertos_estrictos == 50


@_hay_cache
def test_bandas_globales_y_por_etapa(datos):
    args = (datos["confianzas"], datos["reales"], datos["predichos"])
    globales = calibracion_por_bandas(*args)
    assert [b.total for b in globales] == [98, 26, 6, 31, 39]
    assert [b.aciertos for b in globales] == [75, 19, 2, 22, 29]
    por_etapa = calibracion_por_etapa(*args, datos["etapas"])
    assert [b.total for b in por_etapa["deterministic"]] == [98, 26, 6, 0, 1]
    assert [b.total for b in por_etapa["gemini"]] == [0, 0, 0, 31, 38]
    assert [b.aciertos for b in por_etapa["gemini"]] == [0, 0, 0, 22, 28]


@_hay_cache
def test_contingencia_y_tramo_de_alta_confianza(datos):
    c = contingencia_confianza(
        datos["confianzas"], datos["reales"], datos["predichos"], umbral=0.70
    )
    assert (c.alta_total, c.alta_aciertos) == (76, 53)
    assert (c.baja_total, c.baja_aciertos) == (124, 94)

    en_tramo = [i for i, v in enumerate(datos["confianzas"]) if v >= 0.90]
    errores = [i for i in en_tramo if datos["reales"][i] != datos["predichos"][i]]
    assert (len(en_tramo), len(errores)) == (46, 13)
    assert sum(1 for i in en_tramo if datos["etapas"][i] == "gemini") == 45

    det_alta = [
        i for i, e in enumerate(datos["etapas"])
        if e == "deterministic" and datos["confianzas"][i] >= 0.70
    ]
    assert len(det_alta) == 7  # el segmento >= 0,70 reune 7 deterministicos y 69 de Gemini


@_hay_cache
def test_distribucion_de_confianza_por_etapa(datos):
    def distribucion(etapa):
        idx = [i for i, e in enumerate(datos["etapas"]) if e == etapa]
        return distribucion_confianza(
            [datos["confianzas"][i] for i in idx],
            [datos["reales"][i] for i in idx],
            [datos["predichos"][i] for i in idx],
        )

    # La banda [0; 0,5) de 98 casos reune dos valores: 0,0 (90) y 1/6 (8).
    assert {v.valor: v.casos for v in distribucion("deterministic")} == {
        0.0: 90, 0.1667: 8, 0.5: 26, 0.75: 6, 1.0: 1
    }
    assert {v.valor: (v.casos, v.aciertos) for v in distribucion("gemini")}.keys() == {
        0.85, 0.9, 0.95, 0.98
    }
    gem = {v.valor: v.casos for v in distribucion("gemini")}
    assert (gem[0.85], gem[0.9]) == (24, 7)
    assert gem[0.95] + gem[0.98] == 38


@pytest.mark.skipif(not _CORPUS.exists(), reason="corpus local ausente")
def test_hash_del_corpus_es_el_canonico_en_la_copia_de_trabajo():
    """Con `.gitattributes` (LF) el SHA-256 de los bytes coincide con el del blob versionado."""
    assert hashlib.sha256(_CORPUS.read_bytes()).hexdigest() == HASH_CANONICO


@pytest.mark.skipif(not _CORPUS.exists(), reason="corpus local ausente")
def test_hash_del_runner_es_el_canonico_aun_con_fines_de_linea_crlf(tmp_path):
    from evaluation.run_evaluation import _compute_corpus_hash

    crlf = tmp_path / "corpus.json"
    base = _CORPUS.read_bytes().replace(CRLF, LF)
    crlf.write_bytes(base.replace(LF, CRLF))

    assert _compute_corpus_hash(_CORPUS) == HASH_CANONICO
    assert _compute_corpus_hash(crlf) == HASH_CANONICO
