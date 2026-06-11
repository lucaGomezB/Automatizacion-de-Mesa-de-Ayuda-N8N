"""
Tests de la configuración de generación enviada a la API de Gemini.

Responsabilidad:
    Verifica que GeminiClassifier construya GenerateContentConfig con los
    parámetros que garantizan una respuesta JSON parseable por el validador
    estricto del Anexo H §H.3:

        - response_mime_type="application/json": fuerza el modo JSON de la API,
          impidiendo que el modelo envuelva la respuesta en fences de Markdown
          (```json ... ```), que el validador rechaza por especificación.
        - thinking_config.thinking_budget=0: Gemini 2.5 Flash es un modelo con
          razonamiento ("thinking") activado por defecto; esos tokens consumen
          el presupuesto de max_output_tokens=100 y truncan la respuesta visible.
          Con presupuesto 0 el modelo responde directo y el JSON entra completo.

    Contexto: bug observado en la verificación funcional de C-04 — la respuesta
    cruda de Gemini fue únicamente "```json" (truncada por thinking + fence),
    forzando el fallback con confianza=0.0 en un caso que Gemini podía resolver.

Notas:
    - No se realizan llamadas de red: genai.Client se construye con una clave
      falsa y solo se inspecciona la configuración local del clasificador.
    - Se inyectan Settings de prueba monkeypatcheando get_settings en el módulo
      del clasificador, siguiendo el patrón de test_settings_pseudonymization.py.
"""

import pytest

from app.config.settings import Settings, get_settings

# Clave Fernet de prueba (no contiene datos reales)
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

# Campos mínimos para instanciar Settings directamente en tests
_REQUIRED_FIELDS = {
    "database_url": "sqlite+aiosqlite:///:memory:",
    "gemini_api_key": "fake-gemini-key",
    "pseudonymization_encryption_key": _TEST_KEY,
}


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Limpia el caché LRU de get_settings() antes y después de cada test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def classifier(monkeypatch):
    """GeminiClassifier construido con Settings de prueba (sin red ni .env)."""
    from app.classifiers import gemini_classifier as module

    monkeypatch.setattr(module, "get_settings", lambda: Settings(**_REQUIRED_FIELDS))
    return module.GeminiClassifier()


def test_generation_config_fuerza_json_mode(classifier) -> None:
    """
    response_mime_type debe ser "application/json" para activar el modo JSON
    de la API. Sin esto, el modelo puede envolver la respuesta en un bloque
    Markdown que el validador del Anexo H rechaza (ver
    test_markdown_wrapped_json_raises en test_gemini_validation.py).
    """
    assert classifier._generation_config.response_mime_type == "application/json"


def test_generation_config_desactiva_thinking(classifier) -> None:
    """
    thinking_budget debe ser 0: los tokens de razonamiento de Gemini 2.5 Flash
    cuentan contra max_output_tokens (100), y con thinking activo la respuesta
    visible se trunca antes de completar el JSON.
    """
    thinking = classifier._generation_config.thinking_config
    assert thinking is not None
    assert thinking.thinking_budget == 0


def test_generation_config_preserva_parametros_calibrados(classifier) -> None:
    """
    Los parámetros calibrados del Anexo H §H.2 deben permanecer en la config
    junto a los nuevos: el modo JSON no reemplaza la calibración empírica
    (temperature=0.3, top_p=0.9, max_output_tokens=100, candidate_count=1)
    validada sobre el corpus de 200 casos.
    """
    config = classifier._generation_config
    assert config.temperature == 0.3
    assert config.top_p == 0.9
    assert config.max_output_tokens == 100
    assert config.candidate_count == 1
