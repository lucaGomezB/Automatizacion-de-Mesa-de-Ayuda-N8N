"""
Identidad de inferencia en la cache de predicciones (c-227, D2; tarea 2.3).

Verifica que la cache distingue la version de modelo y el proveedor, y que la
evidencia congelada —cuyas predicciones no declaran esos campos— sigue siendo
valida bajo los defaults (proveedor y modelo vigentes).

Funciones puras y offline: no invocan al clasificador ni al proveedor.
"""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.run_evaluation import _identidad_inferencia_por_defecto, _is_cache_valid

EVIDENCIA = (
    Path(__file__).resolve().parents[1]
    / "evidence"
    / "predicciones_hybrid-v3_2026-10-07.json"
)
CORPUS_HASH_ESTRICTO = (
    "1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb"
)


def _cache(tmp_path, meta: dict) -> Path:
    ruta = tmp_path / "predicciones.json"
    ruta.write_text(
        json.dumps({"cache_meta": meta, "predictions": []}), encoding="utf-8"
    )
    return ruta


def test_identidad_por_defecto_es_la_vigente() -> None:
    assert _identidad_inferencia_por_defecto() == ("gemini", "gemini-3.6-flash")


def test_cache_sin_provider_ni_model_es_valida(tmp_path) -> None:
    """La ausencia de provider/model se interpreta como los defaults (D2)."""
    ruta = _cache(
        tmp_path,
        {
            "corpus_hash": "h",
            "corpus_count": 1,
            "classifier_version": "hybrid-v3",
        },
    )
    assert _is_cache_valid(ruta, "h", 1, "hybrid-v3") is True


def test_cache_con_identidad_coincidente_es_valida(tmp_path) -> None:
    ruta = _cache(
        tmp_path,
        {
            "corpus_hash": "h",
            "corpus_count": 1,
            "classifier_version": "hybrid-v3",
            "provider": "gemini",
            "model": "gemini-3.6-flash",
        },
    )
    assert _is_cache_valid(ruta, "h", 1, "hybrid-v3") is True


def test_version_de_modelo_distinta_invalida(tmp_path) -> None:
    ruta = _cache(
        tmp_path,
        {
            "corpus_hash": "h",
            "corpus_count": 1,
            "classifier_version": "hybrid-v3",
            "provider": "gemini",
            "model": "gemini-otro",
        },
    )
    assert _is_cache_valid(ruta, "h", 1, "hybrid-v3") is False


def test_proveedor_distinto_invalida(tmp_path) -> None:
    ruta = _cache(
        tmp_path,
        {
            "corpus_hash": "h",
            "corpus_count": 1,
            "classifier_version": "hybrid-v3",
            "provider": "otro",
            "model": "gemini-3.6-flash",
        },
    )
    assert _is_cache_valid(ruta, "h", 1, "hybrid-v3") is False


def test_evidencia_congelada_sigue_valida_bajo_defaults() -> None:
    """La evidencia congelada no declara provider/model: es valida por defaults."""
    assert EVIDENCIA.exists()
    assert _is_cache_valid(EVIDENCIA, CORPUS_HASH_ESTRICTO, 200, "hybrid-v3") is True
