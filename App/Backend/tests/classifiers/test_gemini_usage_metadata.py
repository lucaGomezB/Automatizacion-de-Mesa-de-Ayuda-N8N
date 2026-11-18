"""
Captura aditiva de uso de tokens y version del modelo (c-243, compuerta G3).

Contrato verificado:
    - ``GeminiProvider.generate`` devuelve el texto crudo MAS el uso de tokens
      (``usage_metadata``: ``prompt_token_count``, ``candidates_token_count``,
      ``total_token_count``) y la version del modelo (``model_version``) cuando la
      API los expone. El contrato publico previo (el texto) se conserva en
      ``GenerationResult.text``.
    - Cuando la API no expone ``usage_metadata`` (o no trae conteos), el uso es
      ``None``: no se inventan tokens.
    - El evento ``gemini_classified`` agrega ``modelo_solicitado``,
      ``model_version``, ``tokens_entrada``, ``tokens_salida``, ``tokens_total`` y
      ``tokens_origen`` (``api`` o ``ausente``), SIN texto del prompt, sin PII y sin
      la clave de API.

Es aditivo y de solo lectura: no altera el camino de costo cero ni los
parametros de inferencia. Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from __future__ import annotations

import types
from unittest.mock import MagicMock

import pytest

from app.classifiers import gemini_classifier as gemini_module
from app.classifiers.gemini_classifier import GeminiClassifier, GeminiProvider
from app.classifiers.provider import GenerationResult, InferenceParams, TokenUsage
from app.config.settings import Settings, get_settings

# Clave Fernet de prueba (no contiene datos reales).
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_VALID_JSON = '{"categoría": "Sistemas", "confianza": 0.92}'


def _settings(**overrides) -> Settings:
    fields = {
        "database_url": "sqlite+aiosqlite:///:memory:",
        "gemini_api_key": "fake-gemini-key",  # gitleaks:allow
        "pseudonymization_encryption_key": _TEST_KEY,
        "jwt_secret_key": "fake-jwt-secret",
    }
    fields.update(overrides)
    return Settings(**fields)


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Dobles: respuesta genai con/sin usage_metadata y model_version
# ---------------------------------------------------------------------------
class _Respuesta:
    def __init__(self, text: str, usage_metadata=None, model_version=None) -> None:
        self.text = text
        if usage_metadata is not None:
            self.usage_metadata = usage_metadata
        if model_version is not None:
            self.model_version = model_version


class _ModelosFalsos:
    def __init__(self, respuesta) -> None:
        self._respuesta = respuesta
        self.calls = 0

    async def generate_content(self, **kwargs):
        self.calls += 1
        return self._respuesta


class _ClienteFalso:
    def __init__(self, respuesta) -> None:
        self.aio = types.SimpleNamespace(models=_ModelosFalsos(respuesta))


def _params() -> InferenceParams:
    return InferenceParams(
        model="gemini-3.6-flash",
        temperature=0.3,
        top_p=0.9,
        max_output_tokens=100,
        candidate_count=1,
        timeout=30.0,
    )


async def _generar(respuesta):
    proveedor = GeminiProvider(client=_ClienteFalso(respuesta))
    return await proveedor.generate(prompt="p", params=_params())


class _ProveedorFalso:
    """Proveedor que devuelve un ``GenerationResult`` prefijado (sin SDK)."""

    def __init__(self, resultado: GenerationResult) -> None:
        self._resultado = resultado
        self.llamadas = 0

    async def generate(self, *, prompt: str, params: InferenceParams) -> GenerationResult:
        self.llamadas += 1
        return self._resultado


# ---------------------------------------------------------------------------
# 1.1 — El proveedor expone uso y version sin romper el texto crudo
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_generate_devuelve_uso_de_tokens_y_version_del_modelo() -> None:
    uso = types.SimpleNamespace(
        prompt_token_count=812, candidates_token_count=17, total_token_count=829
    )
    resultado = await _generar(
        _Respuesta(_VALID_JSON, usage_metadata=uso, model_version="gemini-3.6-flash-001")
    )

    assert isinstance(resultado, GenerationResult)
    assert resultado.text == _VALID_JSON
    assert resultado.usage == TokenUsage(
        prompt_tokens=812, candidates_tokens=17, total_tokens=829
    )
    assert resultado.model_version == "gemini-3.6-flash-001"


@pytest.mark.asyncio
async def test_generate_sin_usage_metadata_devuelve_uso_ausente() -> None:
    resultado = await _generar(_Respuesta(_VALID_JSON))

    assert resultado.text == _VALID_JSON
    assert resultado.usage is None
    assert resultado.model_version is None


@pytest.mark.asyncio
async def test_generate_con_usage_metadata_vacia_no_inventa_tokens() -> None:
    uso = types.SimpleNamespace(
        prompt_token_count=None, candidates_token_count=None, total_token_count=None
    )
    resultado = await _generar(_Respuesta(_VALID_JSON, usage_metadata=uso))

    assert resultado.usage is None


# ---------------------------------------------------------------------------
# 1.2 — El evento gemini_classified agrega los campos de uso
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_evento_registra_tokens_version_y_modelo_solicitado(monkeypatch) -> None:
    monkeypatch.setattr(gemini_module, "get_settings", lambda: _settings())
    resultado = GenerationResult(
        text=_VALID_JSON,
        usage=TokenUsage(prompt_tokens=812, candidates_tokens=17, total_tokens=829),
        model_version="gemini-3.6-flash-001",
    )
    clasificador = GeminiClassifier(provider=_ProveedorFalso(resultado))

    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    descripcion = "El servidor de correo de la sucursal no responde desde las 9"
    await clasificador.classify(descripcion)

    payload = repr(mock_logger.mock_calls)
    assert "gemini_classified" in payload
    assert "modelo_solicitado='gemini-3.6-flash'" in payload
    assert "model_version='gemini-3.6-flash-001'" in payload
    assert "tokens_entrada=812" in payload
    assert "tokens_salida=17" in payload
    assert "tokens_total=829" in payload
    assert "tokens_origen='api'" in payload
    # Sin texto del prompt ni clave.
    assert descripcion not in payload
    assert "fake-gemini-key" not in payload


@pytest.mark.asyncio
async def test_evento_sin_uso_marca_origen_ausente(monkeypatch) -> None:
    monkeypatch.setattr(gemini_module, "get_settings", lambda: _settings())
    clasificador = GeminiClassifier(
        provider=_ProveedorFalso(GenerationResult(text=_VALID_JSON))
    )

    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    await clasificador.classify("descripcion de prueba")

    payload = repr(mock_logger.mock_calls)
    assert "tokens_origen='ausente'" in payload
    assert "tokens_entrada=None" in payload
    assert "tokens_salida=None" in payload
    assert "tokens_total=None" in payload
    assert "model_version=None" in payload
