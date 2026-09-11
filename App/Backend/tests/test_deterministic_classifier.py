"""
Tests unitarios del clasificador determinístico basado en reglas (C-27).

Vocabulario canonico de 5 sectores. `Operaciones` deja de existir y sus
terminos se redistribuyen. Un sector debe ganar para cada caso canonico.

Strict TDD:
    3.1 RED   -> los tests exigen los 5 sectores y `Soporte Tecnico Hardware`.
    3.2 GREEN -> keywords.py redistribuido.
    3.3 TRIANGULATE -> un caso por sector + un caso ambiguo.
"""

import pytest

from app.classifiers.deterministic import DeterministicClassifier
from app.constants import SECTORES_CANONICOS


@pytest.fixture
def classifier() -> DeterministicClassifier:
    return DeterministicClassifier()


class TestRedistribucionSectores:
    @pytest.mark.asyncio
    async def test_todos_los_sectores_tienen_terminos(self, classifier):
        """Los cinco sectores canonicos tienen al menos un patron de keywords."""
        from app.classifiers.keywords import KEYWORD_MAP

        assert set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)
        for sector, patrones in KEYWORD_MAP.items():
            assert patrones, f"El sector {sector!r} no tiene terminos"

    @pytest.mark.asyncio
    async def test_hardware_clasifica_como_soporte_tecnico_hardware(self, classifier):
        """Un termino de hardware debe clasificar como `Soporte Tecnico Hardware`."""
        result = await classifier.classify(
            "Mi impresora no imprime. Sale papel atascado. Código de error 13."
        )
        assert result.sector_predicho == "Soporte Tecnico Hardware"
        assert result.confianza > 0.0
        assert result.etapa == "deterministic"

    @pytest.mark.asyncio
    async def test_ninguna_prediccion_es_operaciones(self, classifier):
        """Ninguna prediccion puede ser `Operaciones` (eliminada del dominio)."""
        textos = [
            "Necesitamos reservar una sala para una reunión de planificación.",
            "Trámite administrativo de continuidad operativa pendiente.",
            "El servidor no responde por un timeout en la red.",
            "La impresora no enciende.",
            "El backup de la base de datos falló.",
            "Detectamos phishing y malware.",
        ]
        for texto in textos:
            result = await classifier.classify(texto)
            assert result.sector_predicho != "Operaciones"
            assert result.sector_predicho in SECTORES_CANONICOS


class TestCasosCanonicos:
    @pytest.mark.asyncio
    async def test_seguridad_informatica(self, classifier):
        result = await classifier.classify(
            "Detectamos un ataque de phishing y actividad de malware en la red."
        )
        assert result.sector_predicho == "Seguridad Informatica"

    @pytest.mark.asyncio
    async def test_soporte_tecnico_software(self, classifier):
        result = await classifier.classify(
            "No puedo abrir Outlook, la aplicación de escritorio se traba."
        )
        assert result.sector_predicho == "Soporte Tecnico Software"

    @pytest.mark.asyncio
    async def test_bases_de_datos(self, classifier):
        result = await classifier.classify(
            "El backup de la base de datos falló durante la replicación."
        )
        assert result.sector_predicho == "Bases de Datos"

    @pytest.mark.asyncio
    async def test_sistemas_servidor(self, classifier):
        result = await classifier.classify(
            "Se cayó el servidor de correo. Error SMTP timeout en la red."
        )
        assert result.sector_predicho == "Sistemas"

    @pytest.mark.asyncio
    async def test_termino_ambiguo_devuelve_sector_canonico(self, classifier):
        """Un texto con señal mixta devuelve uno de los 5 sectores, nunca Operaciones."""
        result = await classifier.classify(
            "El servidor de base de datos tiene un firewall nuevo y no responde."
        )
        assert result.sector_predicho in SECTORES_CANONICOS


class TestInvariantes:
    @pytest.mark.asyncio
    async def test_confidence_is_normalised(self, classifier):
        result = await classifier.classify(
            "impresora teclado mouse pantalla laptop periférico"
        )
        assert 0.0 <= result.confianza <= 1.0

    @pytest.mark.asyncio
    async def test_empty_description_returns_result(self, classifier):
        result = await classifier.classify("x")
        assert result.sector_predicho in SECTORES_CANONICOS
        assert 0.0 <= result.confianza <= 1.0
