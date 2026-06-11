"""
Tests para evaluation/run_evaluation.py — runner de evaluación.

TDD — ciclos: RED → GREEN → TRIANGULATE → REFACTOR (Grupo 6)
"""

from __future__ import annotations

import pathlib

import pytest

from evaluation.tests.conftest import CORPUS_FIXTURE_PATH


# ---------------------------------------------------------------------------
# 6.1 RED → 6.2 GREEN: runner recolecta una predicción por caso
# ---------------------------------------------------------------------------
async def test_runner_recolecta_una_prediccion_por_caso(
    fake_classifier,
    corpus_fixture_path,
):
    """Por cada caso del corpus fixture, el runner registra exactamente una predicción."""
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import evaluar_corpus

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    # Una predicción por caso
    assert len(predicciones) == len(corpus)

    # Cada predicción tiene los campos esperados
    for pred in predicciones:
        assert hasattr(pred, "categoria_predicha")
        assert hasattr(pred, "confianza")
        assert hasattr(pred, "etapa")
        assert pred.categoria_predicha in {"Sistemas", "Operaciones", "Soporte Técnico"}
        assert 0.0 <= pred.confianza <= 1.0
        assert pred.etapa in {"deterministic", "gemini", "fallback"}


# ---------------------------------------------------------------------------
# 6.3 RED → 6.4 GREEN: runner genera report.md con métricas
# ---------------------------------------------------------------------------
async def test_runner_genera_report_md_con_metricas(
    fake_classifier,
    corpus_fixture_path,
    tmp_path,
):
    """Tras correr, se escribe report.md con matriz de confusión, exactitud y métricas."""
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import evaluar_corpus, generar_reporte

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    reporte_path = tmp_path / "report.md"
    generar_reporte(predicciones, corpus, output_path=reporte_path)

    assert reporte_path.exists()
    contenido = reporte_path.read_text(encoding="utf-8")

    # El reporte debe contener las secciones clave
    assert "Exactitud" in contenido or "exactitud" in contenido
    assert "Matriz" in contenido or "matriz" in contenido
    # Debe mencionar las tres clases
    assert "Sistemas" in contenido
    assert "Operaciones" in contenido
    assert "Soporte Técnico" in contenido


# ---------------------------------------------------------------------------
# 6.5 TRIANGULATE: corpus real ausente falla con mensaje claro
# ---------------------------------------------------------------------------
async def test_runner_corpus_real_ausente_falla_claro(fake_classifier):
    """Si el corpus real no existe, el runner falla con mensaje claro y no inventa datos."""
    from evaluation.run_evaluation import main_con_corpus_real

    with pytest.raises((FileNotFoundError, ValueError), match="corpus|corpus_evaluacion"):
        await main_con_corpus_real(classifier=fake_classifier)
