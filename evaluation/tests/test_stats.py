"""
Tests para evaluation/stats.py — análisis estadístico de tiempos.

TDD — ciclo: RED → GREEN → TRIANGULATE → REFACTOR (Grupo 5)
"""

from __future__ import annotations

import pytest


def test_wilcoxon_diferencia_sistematica_es_significativa():
    """
    Cuando el flujo automatizado es SIEMPRE más rápido que el manual,
    la prueba debe devolver p < 0.05 y r (rank-biserial) de magnitud alta.
    """
    from evaluation.stats import wilcoxon_tiempos

    # Tiempos manuales vs automatizados: automatizado siempre 10x más rápido
    manual = [180.0, 210.0, 240.0, 195.0, 220.0, 200.0, 175.0, 160.0, 190.0]
    automatizado = [12.0, 14.0, 15.0, 13.0, 16.0, 14.0, 11.0, 10.0, 12.0]

    W, p, r = wilcoxon_tiempos(manual, automatizado)

    assert p < 0.05, f"Se esperaba p < 0.05, se obtuvo p={p}"
    # Efecto rank-biserial esperado alto (> 0.7 como mínimo)
    assert r > 0.7, f"Se esperaba r > 0.7, se obtuvo r={r}"
    # W >= 0
    assert W >= 0


def test_wilcoxon_series_de_distinta_longitud_lanza_error():
    """Cuando las series tienen longitudes distintas, debe lanzar un error."""
    from evaluation.stats import wilcoxon_tiempos

    manual = [180.0, 210.0, 240.0]
    automatizado = [12.0, 14.0]  # longitud distinta

    with pytest.raises(ValueError, match="longitud"):
        wilcoxon_tiempos(manual, automatizado)
