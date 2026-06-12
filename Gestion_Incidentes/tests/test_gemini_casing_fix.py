"""
Tests TDD para el fix de casing de categorías en la respuesta de Gemini 2.5 Flash.

Contexto del bug:
    Gemini a veces devuelve la categoría en MAYÚSCULAS ("SISTEMAS" en lugar de
    "Sistemas"). La validación del Anexo H §H.3 es case-sensitive POR ESPECIFICACIÓN,
    así que esos casos caen a fallback (confianza=0.0, revisión humana).

    El fix va en el ORIGEN (request a Gemini), no en la validación:
        1. response_schema con enum de los 3 strings exactos → el modelo queda
           restringido por la API a emitir solo esos valores.
        2. Refuerzo del prompt → instrucción explícita de casing + los 3 literales.

    La red de seguridad del Anexo H §H.3 queda intacta: si Gemini devuelve casing
    incorrecto pese a las restricciones, la validación sigue cayendo a fallback.

Suite:
    Task A — response_schema con enum
        A.1  test_config_gemini_incluye_response_schema_con_enum_exacto
             Inspecciona el GenerateContentConfig construido y verifica que
             response_schema.properties["categoría"].enum contenga los 3 strings exactos.
        A.2  test_config_response_schema_incluye_campo_confianza
             El schema también define el campo "confianza" (NUMBER) en el objeto raíz.
        A.3  test_config_response_schema_required_contiene_ambos_campos
             El schema marca "categoría" y "confianza" como required.

    Task B — refuerzo del prompt
        B.1  test_prompt_contiene_instruccion_casing_explicita
             El texto del prompt enviado incluye una instrucción de casing (p. ej.
             "exactamente" o "respetando mayúsculas") junto a los 3 literales en formato
             correcto para que el modelo sepa qué strings usar.
        B.2  test_prompt_contiene_los_tres_literales_exactos
             Los 3 strings con casing correcto aparecen en el prompt:
             "Sistemas", "Operaciones", "Soporte Técnico".

    Task C — NO REGRESIÓN del Anexo H §H.3
        C.1  test_casing_incorrecto_SISTEMAS_cae_a_fallback
             Respuesta mockeada "SISTEMAS" → fallback (confianza=0.0, revisión humana).
             La red de seguridad del Anexo H queda intacta.
        C.2  test_happy_path_sistemas_clasifica_normal
             Respuesta mockeada "Sistemas" → ClasificacionResult válido, etapa="gemini".
        C.3  test_happy_path_operaciones_clasifica_normal
             Respuesta mockeada "Operaciones" → ClasificacionResult válido.
        C.4  test_happy_path_soporte_tecnico_con_tilde_clasifica_normal
             "Soporte Técnico" (con é y tilde) → ClasificacionResult válido.
        C.5  test_casing_incorrecto_OPERACIONES_cae_a_fallback
             "OPERACIONES" en mayúsculas → fallback.
        C.6  test_casing_incorrecto_SOPORTE_TECNICO_cae_a_fallback
             "SOPORTE TÉCNICO" en mayúsculas → fallback.

Notas:
    - Tasks A y B ejercen el GenerateContentConfig y el texto del prompt (no llaman red).
    - Task C ejerce _validate_gemini_response y el método classify() con mock.
    - El fixture classifier inyecta Settings de prueba (sin .env ni red).
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from app.classifiers.gemini_classifier import _validate_gemini_response, _PROMPT_TEMPLATE
from app.classifiers import gemini_classifier as _gemini_module
from app.config.settings import Settings, get_settings
from app.core.exceptions import GeminiResponseInvalidError

# ── Fixtures ─────────────────────────────────────────────────────────────────

# Clave Fernet de prueba (no contiene datos reales)
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

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
    monkeypatch.setattr(_gemini_module, "get_settings", lambda: Settings(**_REQUIRED_FIELDS))
    return _gemini_module.GeminiClassifier()


# ── Task A: response_schema con enum ─────────────────────────────────────────

class TestResponseSchemaEnum:
    """
    Task A: GenerateContentConfig debe incluir response_schema con enum exacto.

    Sin este schema, la API de Gemini puede devolver cualquier string como
    categoría (incluyendo variantes en mayúsculas), lo que dispara el fallback
    del Anexo H §H.3 y infla la cola de revisión humana.
    """

    def test_config_gemini_incluye_response_schema_con_enum_exacto(self, classifier) -> None:
        """
        response_schema.properties["categoría"].enum debe contener exactamente
        los 3 strings canónicos con su casing correcto y tildes incluidas.

        Este test es el RED principal: hoy GeminiClassifier no tiene response_schema,
        así que fallará hasta que se implemente el fix.
        """
        schema = classifier._generation_config.response_schema
        assert schema is not None, "response_schema no está configurado en GenerateContentConfig"

        assert "categoría" in schema.properties, (
            "El schema no define la propiedad 'categoría'"
        )
        enum_values = schema.properties["categoría"].enum
        assert enum_values is not None, "categoría no tiene enum definido"

        expected = {"Sistemas", "Operaciones", "Soporte Técnico"}
        assert set(enum_values) == expected, (
            f"El enum de categoría contiene {set(enum_values)!r}, se esperaba {expected!r}"
        )

    def test_config_response_schema_incluye_campo_confianza(self, classifier) -> None:
        """
        El schema también debe incluir la propiedad "confianza" de tipo numérico
        para que el modo JSON de la API produzca exactamente los 2 campos que
        el validador del Anexo H §H.3 espera.
        """
        schema = classifier._generation_config.response_schema
        assert schema is not None
        assert "confianza" in schema.properties, (
            "El schema no define la propiedad 'confianza'"
        )

    def test_config_response_schema_required_contiene_ambos_campos(self, classifier) -> None:
        """
        Ambos campos deben estar en la lista 'required' del schema para que
        la API garantice su presencia en la respuesta (sin required, el campo
        puede estar ausente si Gemini elige omitirlo).
        """
        schema = classifier._generation_config.response_schema
        assert schema is not None
        required = set(schema.required or [])
        assert "categoría" in required, "'categoría' debe ser campo required del schema"
        assert "confianza" in required, "'confianza' debe ser campo required del schema"


# ── Task B: refuerzo del prompt ───────────────────────────────────────────────

class TestPromptCasingRefuerzo:
    """
    Task B: El prompt enviado a Gemini debe incluir instrucción explícita de casing.

    El response_schema es la garantía principal, pero el prompt refuerza el mensaje
    al modelo en texto natural (defensa en profundidad). Gemini puede ignorar el
    schema en casos de jailbreak o mal entrenamiento, pero el prompt suma otro
    vector de restricción.
    """

    def test_prompt_contiene_los_tres_literales_exactos(self) -> None:
        """
        Los 3 strings canónicos con casing correcto deben aparecer literalmente
        en el prompt. El modelo aprende el formato esperado por el ejemplo directo.
        """
        assert "Sistemas" in _PROMPT_TEMPLATE, (
            "El prompt no contiene 'Sistemas' (con S mayúscula, resto minúscula)"
        )
        assert "Operaciones" in _PROMPT_TEMPLATE, (
            "El prompt no contiene 'Operaciones' (con O mayúscula, resto minúscula)"
        )
        assert "Soporte Técnico" in _PROMPT_TEMPLATE, (
            "El prompt no contiene 'Soporte Técnico' (con tildes y casing exacto)"
        )

    def test_prompt_contiene_instruccion_casing_categorias(self) -> None:
        """
        El prompt debe incluir una instrucción explícita sobre el casing de los
        VALORES de categoría en el JSON de respuesta.

        La instrucción esperada debe contener alguna de las siguientes frases
        que sean inequívocas respecto al casing del VALOR del campo "categoría":
            - "casing exacto"
            - "respeta el casing"
            - "usa exactamente"
            - "CASING"

        Este test es RED si el prompt actual no tiene ninguna de esas frases.
        La instrucción reforzada se agregará en el bloque CASING en el fix.
        """
        prompt_lower = _PROMPT_TEMPLATE.lower()

        # Frases inequívocas — ninguna aparece en el prompt actual
        has_casing_instruction = any(
            phrase in prompt_lower
            for phrase in [
                "casing exacto",
                "respeta el casing",
                "usa exactamente",
                "casing",
            ]
        )
        assert has_casing_instruction, (
            "El prompt no contiene instrucción explícita de casing para el VALOR de 'categoría'. "
            "Se esperaba alguna de: 'casing exacto', 'respeta el casing', 'usa exactamente', 'casing'. "
            f"Prompt VALIDACIÓN y FORMATO (últimos 400 chars):\n{_PROMPT_TEMPLATE[-400:]}"
        )


# ── Task C: NO REGRESIÓN Anexo H §H.3 ────────────────────────────────────────

class TestAnexoHNoRegresion:
    """
    Task C: la red de seguridad del Anexo H §H.3 debe quedar intacta.

    Aunque el response_schema restrinja el enum, la validación downstream
    sigue activa como última barrera. Estos tests son de NO REGRESIÓN:
    verifican que el comportamiento de fallback ante casing incorrecto
    sigue funcionando igual que antes del fix.
    """

    # ── C.1 / C.5 / C.6: casing incorrecto → falla la validación ─────────────

    def test_casing_incorrecto_SISTEMAS_cae_a_fallback(self) -> None:
        """
        'SISTEMAS' (todo mayúsculas) NO está en el conjunto canónico →
        GeminiResponseInvalidError. La red de seguridad está intacta.
        """
        with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
            _validate_gemini_response('{"categoría": "SISTEMAS", "confianza": 0.9}')

    def test_casing_incorrecto_OPERACIONES_cae_a_fallback(self) -> None:
        """
        'OPERACIONES' (todo mayúsculas) → GeminiResponseInvalidError.
        """
        with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
            _validate_gemini_response('{"categoría": "OPERACIONES", "confianza": 0.85}')

    def test_casing_incorrecto_SOPORTE_TECNICO_cae_a_fallback(self) -> None:
        """
        'SOPORTE TÉCNICO' (todo mayúsculas) → GeminiResponseInvalidError.
        """
        with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
            _validate_gemini_response('{"categoría": "SOPORTE TÉCNICO", "confianza": 0.80}')

    # ── C.2 / C.3 / C.4: casing correcto → happy path ─────────────────────────

    def test_happy_path_sistemas_clasifica_normal(self) -> None:
        """
        'Sistemas' con casing correcto → _validate_gemini_response retorna dict válido.
        """
        result = _validate_gemini_response('{"categoría": "Sistemas", "confianza": 0.92}')
        assert result["categoría"] == "Sistemas"
        assert result["confianza"] == 0.92

    def test_happy_path_operaciones_clasifica_normal(self) -> None:
        """
        'Operaciones' con casing correcto → dict válido.
        """
        result = _validate_gemini_response('{"categoría": "Operaciones", "confianza": 0.87}')
        assert result["categoría"] == "Operaciones"

    def test_happy_path_soporte_tecnico_con_tilde_clasifica_normal(self) -> None:
        """
        'Soporte Técnico' (con é y tilde en 'Técnico') → dict válido.

        Este es el caso más crítico para encoding: la é y el acento son
        especialmente vulnerables a discrepancias de charset.
        """
        result = _validate_gemini_response('{"categoría": "Soporte Técnico", "confianza": 0.78}')
        assert result["categoría"] == "Soporte Técnico"
        assert result["confianza"] == 0.78


# ── Task D: classify() con mock - integración del schema en el flujo ──────────

class TestClassifyFlowConMock:
    """
    Task D: classify() con respuestas mockeadas verifica la integración del
    response_schema en el flujo completo.
    """

    @pytest_asyncio.fixture
    async def classifier_with_mock(self, monkeypatch):
        """GeminiClassifier con cliente Gemini completamente mockeado."""
        monkeypatch.setattr(_gemini_module, "get_settings", lambda: Settings(**_REQUIRED_FIELDS))
        clf = _gemini_module.GeminiClassifier()
        return clf

    @pytest.mark.asyncio
    async def test_classify_con_respuesta_valida_sistemas_retorna_resultado(
        self, classifier_with_mock, monkeypatch
    ) -> None:
        """
        classify() con respuesta mockeada válida "Sistemas" retorna
        ClasificacionResult con etapa="gemini" y confianza correcta.
        """
        mock_response = MagicMock()
        mock_response.text = '{"categoría": "Sistemas", "confianza": 0.91}'

        mock_models = AsyncMock(return_value=mock_response)
        monkeypatch.setattr(
            classifier_with_mock._client.aio.models,
            "generate_content",
            mock_models,
        )

        result = await classifier_with_mock.classify("El servidor de base de datos no responde")
        assert result.categoria == "Sistemas"
        assert result.confianza == 0.91
        assert result.etapa == "gemini"
        assert result.requiere_revision_humana is False

    @pytest.mark.asyncio
    async def test_classify_con_respuesta_casing_incorrecto_retorna_fallback(
        self, classifier_with_mock, monkeypatch
    ) -> None:
        """
        Incluso si el response_schema restringe el enum, la red de seguridad
        del Anexo H sigue activa: si Gemini devuelve "SISTEMAS" (casing incorrecto),
        classify() retorna fallback con confianza=0.0 y revisión humana=True.
        """
        mock_response = MagicMock()
        mock_response.text = '{"categoría": "SISTEMAS", "confianza": 0.9}'

        mock_models = AsyncMock(return_value=mock_response)
        monkeypatch.setattr(
            classifier_with_mock._client.aio.models,
            "generate_content",
            mock_models,
        )

        result = await classifier_with_mock.classify("El servidor de base de datos no responde")
        assert result.etapa == "fallback"
        assert result.confianza == 0.0
        assert result.requiere_revision_humana is True
