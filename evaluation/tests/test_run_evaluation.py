"""
Tests para evaluation/run_evaluation.py — runner de evaluacion multietiqueta (C-27).

TDD — ciclos: RED -> GREEN -> TRIANGULATE -> REFACTOR
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: el runner recolecta una prediccion multietiqueta por caso
# ---------------------------------------------------------------------------
async def test_runner_recolecta_una_prediccion_por_caso(
    fake_classifier,
    corpus_fixture_path,
):
    """Por cada caso del corpus JSON, el runner registra exactamente una prediccion."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import CLASES
    from evaluation.run_evaluation import evaluar_corpus

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    assert len(predicciones) == len(corpus)

    for pred in predicciones:
        assert hasattr(pred, "sector_asignado")
        assert hasattr(pred, "sector_predicho")
        assert hasattr(pred, "sectores_adicionales")
        assert hasattr(pred, "confianza")
        assert hasattr(pred, "etapa")
        assert not hasattr(pred, "categoria_real")
        assert not hasattr(pred, "categoria_predicha")
        assert pred.sector_predicho in CLASES
        assert isinstance(pred.sectores_adicionales, list)
        for sector in pred.sectores_adicionales:
            assert sector in CLASES
        assert 0.0 <= pred.confianza <= 1.0
        assert pred.etapa in {"deterministic", "gemini", "fallback"}


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: el reporte expone todas las metricas multietiqueta
# ---------------------------------------------------------------------------
async def test_runner_genera_report_md_con_metricas(
    fake_classifier,
    corpus_fixture_path,
    tmp_path,
):
    """Tras correr, se escribe report.md con matriz 5x5, exactitud, subset, Hamming y F1."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import CLASES
    from evaluation.run_evaluation import evaluar_corpus, generar_reporte

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    reporte_path = tmp_path / "report.md"
    contenido = generar_reporte(predicciones, corpus, output_path=reporte_path)

    assert reporte_path.exists()
    assert "Exactitud" in contenido
    assert "Matriz" in contenido
    assert "Subset" in contenido or "subconjunto" in contenido.lower()
    assert "Hamming" in contenido
    assert "Micro" in contenido
    assert "Macro" in contenido
    for sector in CLASES:
        assert sector in contenido


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: corpus real ausente falla con mensaje claro
# ---------------------------------------------------------------------------
async def test_runner_corpus_real_ausente_falla_claro(fake_classifier, tmp_path):
    """Si el corpus JSON no existe, el runner falla claro y no inventa datos."""
    from evaluation.run_evaluation import main_con_corpus_real

    ruta_ausente = tmp_path / "corpus_ausente.json"
    with pytest.raises(FileNotFoundError, match="corpus_ausente.json"):
        await main_con_corpus_real(corpus_path=ruta_ausente, classifier=fake_classifier)


def test_ruta_canonica_del_corpus_real_es_json():
    """La ruta por defecto del corpus real debe apuntar al JSON, no al CSV."""
    from evaluation.run_evaluation import CORPUS_REAL_PATH

    assert CORPUS_REAL_PATH.suffix == ".json"
    assert CORPUS_REAL_PATH.name == "corpus_evaluacion_pseudonimizado.json"
