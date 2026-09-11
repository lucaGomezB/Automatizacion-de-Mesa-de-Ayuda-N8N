"""
Tests del casing/enum de la respuesta de Gemini (C-27).

El enum, el prompt y la validación pasan a los cinco sectores canónicos sin
tildes. La red de seguridad (respuesta con casing incorrecto → fallback) queda
intacta.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from app.classifiers import gemini_classifier as _gemini_module
from app.classifiers.gemini_classifier import _PROMPT_TEMPLATE, _validate_gemini_response
from app.config.settings import Settings, get_settings
from app.constants import SECTORES_CANONICOS
from app.core.exceptions import GeminiResponseInvalidError

_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REQUIRED_FIELDS = {
    "database_url": "sqlite+aiosqlite:///:memory:",
    "gemini_api_key": "fake-gemini-key",
    "pseudonymization_encryption_key": _TEST_KEY,
}


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def classifier(monkeypatch):
    monkeypatch.setattr(_gemini_module, "get_settings", lambda: Settings(**_REQUIRED_FIELDS))
    return _gemini_module.GeminiClassifier()


class TestResponseSchemaEnum:
    def test_enum_contiene_los_cinco_sectores(self, classifier) -> None:
        schema = classifier._generation_config.response_schema
        assert schema is not None
        assert "categoría" in schema.properties
        enum_values = schema.properties["categoría"].enum
        assert set(enum_values) == set(SECTORES_CANONICOS)

    def test_schema_incluye_confianza(self, classifier) -> None:
        schema = classifier._generation_config.response_schema
        assert "confianza" in schema.properties

    def test_schema_required_contiene_ambos_campos(self, classifier) -> None:
        schema = classifier._generation_config.response_schema
        required = set(schema.required or [])
        assert "categoría" in required
        assert "confianza" in required


class TestPrompt:
    @pytest.mark.parametrize("sector", SECTORES_CANONICOS)
    def test_prompt_contiene_los_cinco_literales(self, sector) -> None:
        assert sector in _PROMPT_TEMPLATE

    def test_prompt_no_menciona_operaciones(self) -> None:
        assert "Operaciones" not in _PROMPT_TEMPLATE

    def test_prompt_contiene_instruccion_casing(self) -> None:
        assert "casing" in _PROMPT_TEMPLATE.lower()


class TestNoRegresionAnexoH:
    @pytest.mark.parametrize(
        "categoria_invalida",
        ["SISTEMAS", "OPERACIONES", "SOPORTE TÉCNICO", "sistemas"],
    )
    def test_casing_incorrecto_cae_a_validacion_invalida(self, categoria_invalida) -> None:
        with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
            _validate_gemini_response(
                f'{{"categoría": "{categoria_invalida}", "confianza": 0.9}}'
            )

    @pytest.mark.parametrize("sector", SECTORES_CANONICOS)
    def test_sectores_canonicos_validan(self, sector) -> None:
        result = _validate_gemini_response(
            f'{{"categoría": "{sector}", "confianza": 0.9}}'
        )
        assert result["categoría"] == sector


class TestClassifyFlowConMock:
    @pytest_asyncio.fixture
    async def classifier_with_mock(self, monkeypatch):
        monkeypatch.setattr(_gemini_module, "get_settings", lambda: Settings(**_REQUIRED_FIELDS))
        return _gemini_module.GeminiClassifier()

    @pytest.mark.asyncio
    async def test_classify_respuesta_valida(self, classifier_with_mock, monkeypatch) -> None:
        mock_response = MagicMock()
        mock_response.text = '{"categoría": "Bases de Datos", "confianza": 0.91}'
        monkeypatch.setattr(
            classifier_with_mock._client.aio.models,
            "generate_content",
            AsyncMock(return_value=mock_response),
        )
        result = await classifier_with_mock.classify("El backup falló")
        assert result.sector_predicho == "Bases de Datos"
        assert result.confianza == 0.91
        assert result.etapa == "gemini"
        assert result.requiere_revision_humana is False

    @pytest.mark.asyncio
    async def test_classify_casing_incorrecto_fallback(self, classifier_with_mock, monkeypatch) -> None:
        mock_response = MagicMock()
        mock_response.text = '{"categoría": "SISTEMAS", "confianza": 0.9}'
        monkeypatch.setattr(
            classifier_with_mock._client.aio.models,
            "generate_content",
            AsyncMock(return_value=mock_response),
        )
        result = await classifier_with_mock.classify("El servidor no responde")
        assert result.etapa == "fallback"
        assert result.confianza == 0.0
        assert result.requiere_revision_humana is True
