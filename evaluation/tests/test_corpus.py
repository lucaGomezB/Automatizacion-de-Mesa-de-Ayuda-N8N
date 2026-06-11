"""
Tests para evaluation/corpus.py — carga y contrato del corpus.

TDD — ciclos: RED → GREEN → TRIANGULATE → REFACTOR
"""

from __future__ import annotations

import pathlib

import pytest

from evaluation.tests.conftest import CORPUS_FIXTURE_PATH


# ---------------------------------------------------------------------------
# 1.1 RED → 1.2 GREEN: carga válida
# ---------------------------------------------------------------------------
def test_cargar_corpus_valido_devuelve_todos_los_casos():
    """Un CSV válido con 9 casos devuelve 9 CasoEvaluacion y preserva el primero."""
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(CORPUS_FIXTURE_PATH)

    assert len(casos) == 9
    primero = casos[0]
    assert primero.id == "1"
    assert "servidor de base de datos" in primero.descripcion
    assert primero.categoria_real == "Sistemas"


# ---------------------------------------------------------------------------
# 1.3 TRIANGULATE: errores de carga
# ---------------------------------------------------------------------------
def test_cargar_corpus_inexistente_lanza_error(tmp_path):
    """Una ruta que no existe lanza un error que menciona el nombre del archivo."""
    from evaluation.corpus import cargar_corpus

    ruta_falsa = tmp_path / "no_existe.csv"
    with pytest.raises(FileNotFoundError, match="no_existe.csv"):
        cargar_corpus(ruta_falsa)


def test_cargar_corpus_columna_faltante_lanza_error(tmp_path):
    """Un CSV sin la columna 'categoria_real' lanza error que identifica la columna."""
    from evaluation.corpus import cargar_corpus

    csv_incompleto = tmp_path / "sin_columna.csv"
    csv_incompleto.write_text("id,descripcion\n1,Un incidente sin categoria\n", encoding="utf-8")

    with pytest.raises(ValueError, match="categoria_real"):
        cargar_corpus(csv_incompleto)


# ---------------------------------------------------------------------------
# 1.4 TRIANGULATE: categorías inválidas
# ---------------------------------------------------------------------------
def test_cargar_corpus_categoria_invalida_minuscula_lanza_error(tmp_path):
    """Una categoría 'sistemas' (minúscula) lanza error que identifica el valor y el caso."""
    from evaluation.corpus import cargar_corpus

    csv_invalido = tmp_path / "cat_invalida.csv"
    csv_invalido.write_text(
        "id,descripcion,categoria_real\n1,El servidor falla,sistemas\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="sistemas"):
        cargar_corpus(csv_invalido)


def test_cargar_corpus_categoria_invalida_redes_lanza_error(tmp_path):
    """Una categoría 'Redes' (no pertenece al dominio) lanza error que identifica el valor."""
    from evaluation.corpus import cargar_corpus

    csv_invalido = tmp_path / "cat_redes.csv"
    csv_invalido.write_text(
        "id,descripcion,categoria_real\n5,Problema de red,Redes\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Redes"):
        cargar_corpus(csv_invalido)
