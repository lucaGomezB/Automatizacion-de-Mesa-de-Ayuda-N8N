"""
Fixtures compartidos para la suite de evaluacion.

El FakeClassifier cumple el contrato async de BaseClassifier devolviendo
predicciones predeterminadas por descripcion. Nunca llama a Gemini ni al
backend; es el clasificador inyectable en todos los tests del runner.

Las predicciones se cargan desde el archivo auto-generado
fake_classifier_mappings.py, que es producido por generate_corpus.py
y mantenido sincronizado con el corpus calibrado.
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

# Mappings generados por evaluation/generate_corpus.py
FAKE_MAPPINGS_DIR = pathlib.Path(__file__).parent / "data"
FAKE_MAPPINGS_PATH = FAKE_MAPPINGS_DIR / "fake_classifier_mappings.py"
CALIBRATED_CORPUS_PATH = (
    pathlib.Path(__file__).parent.parent / "data" / "corpus_evaluacion.csv"
)


# ---------------------------------------------------------------------------
# ClasificacionResult minimo para evaluacion (no depende del backend)
# ---------------------------------------------------------------------------
@dataclass
class ClasificacionResultFake:
    """DTO minimo que emula ClasificacionResult del backend para los tests."""

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

    Devuelve respuestas deterministicas predefinidas para cada descripcion
    o, si no se encuentra un mapeo, devuelve la respuesta por defecto.
    Nunca realiza llamadas a Gemini ni a ningun servicio externo.

    Uso:
        fake = FakeClassifier(predicciones={
            "desc1": ClasificacionResultFake(categoria="Sistemas", ...),
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


def _load_calibrated_mappings() -> Dict[str, ClasificacionResultFake]:
    """Carga los mapeos calibrados desde el archivo auto-generado."""
    if not FAKE_MAPPINGS_PATH.exists():
        return {}

    # Leer y ejecutar el archivo Python generado
    namespace: dict = {}
    mapping_code = FAKE_MAPPINGS_PATH.read_text(encoding="utf-8")
    exec(mapping_code, namespace)

    raw: dict[str, tuple[str, float, str]] = namespace.get(
        "FAKE_CLASSIFIER_MAPPINGS", {}
    )

    result: Dict[str, ClasificacionResultFake] = {}
    for desc, (cat, conf, etapa) in raw.items():
        result[desc] = ClasificacionResultFake(
            categoria=cat,
            confianza=conf,
            etapa=etapa,
        )
    return result


# ---------------------------------------------------------------------------
# Fixtures de pytest
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_classifier() -> FakeClassifier:
    """FakeClassifier con predicciones alineadas al corpus calibrado (200 casos)."""
    from evaluation.tests.conftest import _load_calibrated_mappings

    predicciones = _load_calibrated_mappings()

    # Fallback: si no se genero el archivo, usar predicciones del fixture original
    if not predicciones:
        predicciones = {
            "El servidor de base de datos no responde y los usuarios no pueden acceder al sistema ERP.": ClasificacionResultFake(
                categoria="Sistemas", confianza=0.95, etapa="deterministic"
            ),
            "La red del piso 3 esta caida y los equipos no tienen conectividad a internet.": ClasificacionResultFake(
                categoria="Sistemas", confianza=0.93, etapa="deterministic"
            ),
            "Se detecto un acceso no autorizado a la base de datos de clientes.": ClasificacionResultFake(
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
                categoria="Soporte Tecnico", confianza=0.96, etapa="deterministic"
            ),
            "El mouse inalambrico del puesto 14 dejo de funcionar y necesita reemplazo urgente.": ClasificacionResultFake(
                categoria="Soporte Tecnico", confianza=0.94, etapa="deterministic"
            ),
            "El software de facturacion instalado en la PC del area contable lanza error al imprimir.": ClasificacionResultFake(
                categoria="Soporte Tecnico", confianza=0.92, etapa="deterministic"
            ),
        }
    return FakeClassifier(predicciones=predicciones)


@pytest.fixture
def corpus_fixture_path() -> pathlib.Path:
    """Ruta al corpus sintetico de fixtures."""
    return CORPUS_FIXTURE_PATH


@pytest.fixture
def corpus_calibrado_path() -> pathlib.Path:
    """Ruta al corpus calibrado de 200 casos."""
    return CALIBRATED_CORPUS_PATH
