"""
Fixtures compartidos para la suite de evaluacion.

El FakeClassifier cumple el contrato async del clasificador del backend
(`sector_predicho` + `sectores_adicionales` + `confianza` + `etapa`) sin llamar
a Gemini ni al backend. Sus predicciones se derivan del unico fixture JSON
(`tests/fixtures/corpus_fixture.json`); ya no existe corpus sintetico ni
mapeos calibrados autogenerados (C-27, task 7.12).
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pytest


# ---------------------------------------------------------------------------
# Rutas de fixtures
# ---------------------------------------------------------------------------
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
CORPUS_FIXTURE_PATH = FIXTURES_DIR / "corpus_fixture.json"


# ---------------------------------------------------------------------------
# ClasificacionResult minimo para evaluacion (no depende del backend)
# ---------------------------------------------------------------------------
@dataclass
class ClasificacionResultFake:
    """DTO minimo que emula el resultado de clasificacion multietiqueta."""

    sector_predicho: str
    confianza: float
    etapa: str  # "deterministic" | "gemini" | "fallback"
    sectores_adicionales: List[str] = field(default_factory=list)
    requiere_revision_humana: bool = False
    respuesta_raw: Optional[str] = None


# ---------------------------------------------------------------------------
# FakeClassifier
# ---------------------------------------------------------------------------
class FakeClassifier:
    """
    Clasificador falso inyectable en tests.

    Devuelve respuestas deterministicas predefinidas para cada descripcion
    o, si no se encuentra un mapeo, la respuesta por defecto. Nunca realiza
    llamadas a Gemini ni a ningun servicio externo.
    """

    def __init__(
        self,
        predicciones: Optional[Dict[str, ClasificacionResultFake]] = None,
        default_sector: str = "Sistemas",
        default_confianza: float = 0.92,
        default_etapa: str = "deterministic",
        default_adicionales: Optional[List[str]] = None,
    ) -> None:
        self._predicciones: Dict[str, ClasificacionResultFake] = predicciones or {}
        self._default = ClasificacionResultFake(
            sector_predicho=default_sector,
            confianza=default_confianza,
            etapa=default_etapa,
            sectores_adicionales=list(default_adicionales or []),
        )

    async def classify(self, descripcion: str) -> ClasificacionResultFake:
        return self._predicciones.get(descripcion, self._default)


# ---------------------------------------------------------------------------
# Fixtures de pytest
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_classifier() -> FakeClassifier:
    """
    FakeClassifier perfecto derivado del fixture JSON.

    Predice, para cada caso, su `sector_asignado` real y sus
    `sectores_adicionales` reales. El fixture JSON es la unica fuente.
    """
    from evaluation.corpus import cargar_corpus

    casos = cargar_corpus(CORPUS_FIXTURE_PATH)
    predicciones = {
        caso.descripcion: ClasificacionResultFake(
            sector_predicho=caso.sector_asignado,
            sectores_adicionales=list(caso.sectores_adicionales),
            confianza=0.95,
            etapa="deterministic",
        )
        for caso in casos
    }
    return FakeClassifier(predicciones=predicciones)


@pytest.fixture
def corpus_fixture_path() -> pathlib.Path:
    """Ruta al fixture JSON del corpus de evaluacion."""
    return CORPUS_FIXTURE_PATH
