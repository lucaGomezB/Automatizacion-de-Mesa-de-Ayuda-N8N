"""
Fixtures compartidos para la suite de evaluación.

El FakeClassifier cumple el contrato async de BaseClassifier devolviendo
predicciones predeterminadas por id de caso. Nunca llama a Gemini ni al
backend; es el clasificador inyectable en todos los tests del runner.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Dict

import pytest


# ---------------------------------------------------------------------------
# Rutas de fixtures
# ---------------------------------------------------------------------------
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
CORPUS_FIXTURE_PATH = FIXTURES_DIR / "corpus_fixture.csv"


# ---------------------------------------------------------------------------
# ClasificacionResult mínimo para evaluación (no depende del backend)
# ---------------------------------------------------------------------------
@dataclass
class ClasificacionResultFake:
    """DTO mínimo que emula ClasificacionResult del backend para los tests."""

    categoria: str
    confianza: float
    etapa: str  # "deterministic" | "gemini" | "fallback"
    requiere_revision_humana: bool = False
    respuesta_raw: str | None = None


# ---------------------------------------------------------------------------
# FakeClassifier
# ---------------------------------------------------------------------------
class FakeClassifier:
    """
    Clasificador falso inyectable en tests.

    Devuelve respuestas determinísticas predefinidas para cada descripción
    o, si no se encuentra un mapeo, devuelve la respuesta por defecto.
    Nunca realiza llamadas a Gemini ni a ningún servicio externo.

    Uso:
        fake = FakeClassifier(predicciones={
            "desc1": ClasificacionResultFake(categoria="Sistemas", confianza=0.95, etapa="deterministic"),
        })
        result = await fake.classify("desc1")
    """

    def __init__(
        self,
        predicciones: Dict[str, ClasificacionResultFake] | None = None,
        default_categoria: str = "Sistemas",
        default_confianza: float = 0.92,
        default_etapa: str = "deterministic",
    ) -> None:
        self._predicciones: Dict[str, ClasificacionResultFake] = predicciones or {}
        self._default = ClasificacionResultFake(
            categoria=default_categoria,
            confianza=default_confianza,
            etapa=default_etapa,
        )

    async def classify(self, descripcion: str) -> ClasificacionResultFake:
        return self._predicciones.get(descripcion, self._default)


# ---------------------------------------------------------------------------
# Fixtures de pytest
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_classifier() -> FakeClassifier:
    """FakeClassifier con predicciones alineadas al corpus_fixture.csv."""
    predicciones = {
        "El servidor de base de datos no responde y los usuarios no pueden acceder al sistema ERP.": ClasificacionResultFake(
            categoria="Sistemas", confianza=0.95, etapa="deterministic"
        ),
        "La red del piso 3 esta caida y los equipos no tienen conectividad a internet.": ClasificacionResultFake(
            categoria="Sistemas", confianza=0.93, etapa="deterministic"
        ),
        "Se detectó un acceso no autorizado a la base de datos de clientes.": ClasificacionResultFake(
            categoria="Sistemas", confianza=0.91, etapa="deterministic"
        ),
        "El proceso de cierre mensual no puede ejecutarse porque el modulo de planificacion falla.": ClasificacionResultFake(
            categoria="Operaciones", confianza=0.88, etapa="gemini"
        ),
        "El servicio de gestion de turnos no esta disponible y hay cola de atencion acumulada.": ClasificacionResultFake(
            categoria="Operaciones", confianza=0.85, etapa="gemini"
        ),
        "El sistema de continuidad del negocio no genera los reportes de disponibilidad.": ClasificacionResultFake(
            categoria="Operaciones", confianza=0.87, etapa="gemini"
        ),
        "La laptop del empleado Juan no enciende y tiene una reunion importante en una hora.": ClasificacionResultFake(
            categoria="Soporte Técnico", confianza=0.96, etapa="deterministic"
        ),
        "El mouse inalambrico del puesto 14 dejó de funcionar y necesita reemplazo urgente.": ClasificacionResultFake(
            categoria="Soporte Técnico", confianza=0.94, etapa="deterministic"
        ),
        "El software de facturacion instalado en la PC del area contable lanza error al imprimir.": ClasificacionResultFake(
            categoria="Soporte Técnico", confianza=0.92, etapa="deterministic"
        ),
    }
    return FakeClassifier(predicciones=predicciones)


@pytest.fixture
def corpus_fixture_path() -> pathlib.Path:
    """Ruta al corpus sintético de fixtures."""
    return CORPUS_FIXTURE_PATH
