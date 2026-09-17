"""
Tests unitarios de la logica de validacion de respuestas de Gemini (C-27).

El contrato JSON crudo de Gemini conserva el campo "categoría"; lo que cambia
es el conjunto canonico de valores validos (5 sectores sin tildes).

Strict TDD:
    3.4 RED -> exige los cinco sectores en la validacion.
    3.5 GREEN -> gemini_classifier._VALID_CATEGORIES actualizado.
"""

import pytest

from app.classifiers.gemini_classifier import _validate_gemini_response
from app.core.exceptions import GeminiResponseInvalidError


def test_valid_response_sistemas() -> None:
    data = _validate_gemini_response('{"categoría": "Sistemas", "confianza": 0.95}')
    assert data["categoría"] == "Sistemas"
    assert data["confianza"] == 0.95


def test_valid_response_soporte_hardware() -> None:
    data = _validate_gemini_response(
        '{"categoría": "Soporte Tecnico Hardware", "confianza": 0.82}'
    )
    assert data["categoría"] == "Soporte Tecnico Hardware"


def test_valid_response_bases_de_datos() -> None:
    data = _validate_gemini_response('{"categoría": "Bases de Datos", "confianza": 0.7}')
    assert data["categoría"] == "Bases de Datos"


def test_invalid_json_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="JSON inválido"):
        _validate_gemini_response("not json at all")


def test_missing_categoria_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="categoría"):
        _validate_gemini_response('{"confianza": 0.9}')


def test_invalid_categoria_value_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
        _validate_gemini_response('{"categoría": "Hardware", "confianza": 0.9}')


def test_operaciones_ya_no_es_valida() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
        _validate_gemini_response('{"categoría": "Operaciones", "confianza": 0.9}')


def test_variante_con_tilde_es_invalida() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
        _validate_gemini_response(
            '{"categoría": "Soporte Técnico Hardware", "confianza": 0.9}'
        )


def test_missing_confianza_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="confianza"):
        _validate_gemini_response('{"categoría": "Sistemas"}')


def test_confianza_out_of_range_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError, match="Confianza inválida"):
        _validate_gemini_response('{"categoría": "Sistemas", "confianza": 1.5}')


def test_confianza_as_integer_is_valid() -> None:
    data = _validate_gemini_response('{"categoría": "Bases de Datos", "confianza": 1}')
    assert data["confianza"] == 1.0


def test_confianza_booleana_es_invalida() -> None:
    """
    Un booleano JSON (`true`/`false`) NO es una confianza válida. En Python
    `bool` es subclase de `int`, por lo que `isinstance(x, (int, float))` lo
    aceptaría; el validador debe rechazarlo explícitamente.
    """
    for raw in (
        '{"categoría": "Sistemas", "confianza": true}',
        '{"categoría": "Sistemas", "confianza": false}',
    ):
        with pytest.raises(GeminiResponseInvalidError, match="Confianza inválida"):
            _validate_gemini_response(raw)


def test_markdown_wrapped_json_raises() -> None:
    with pytest.raises(GeminiResponseInvalidError):
        _validate_gemini_response('```json\n{"categoría": "Sistemas", "confianza": 0.9}\n```')
