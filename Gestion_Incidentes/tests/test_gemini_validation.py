"""
Tests unitarios de la lógica de validación de respuestas de Gemini.

Responsabilidad:
    Verifica el comportamiento de la función _validate_gemini_response()
    ante los distintos formatos de respuesta que puede devolver la API
    de Gemini 2.5 Flash. Los tests cubren tanto el camino feliz (respuestas
    válidas) como los casos de error más frecuentes detectados durante el
    diseño del clasificador híbrido.

    Todos los tests son síncronos y no realizan llamadas de red: la función
    validada opera exclusivamente sobre el string raw devuelto por Gemini,
    por lo que la suite es completamente aislada del entorno de despliegue.

Casos de test documentados:
    - Respuestas JSON válidas para las tres categorías del dominio.
    - JSON malformado que no puede ser parseado.
    - JSON válido pero con campos obligatorios ausentes.
    - Categoría fuera del conjunto permitido {Sistemas, Operaciones, Soporte Técnico}.
    - Confianza fuera del rango normalizado [0.0, 1.0].
    - Confianza expresada como entero (edge case permitido por el estándar JSON).
    - Respuesta envuelta en bloque de código Markdown (incompatible con json.loads).
"""

import pytest

from app.classifiers.gemini_classifier import _validate_gemini_response
from app.core.exceptions import GeminiResponseInvalidError


def test_valid_response_sistemas() -> None:
    """
    Verifica que una respuesta JSON bien formada para la categoría Sistemas
    sea aceptada y retorne un diccionario con los campos esperados.

    El valor de confianza 0.95 está en el rango válido [0.0, 1.0],
    y la categoría pertenece al conjunto canónico del dominio.
    """
    data = _validate_gemini_response('{"categoría": "Sistemas", "confianza": 0.95}')
    assert data["categoría"] == "Sistemas"
    assert data["confianza"] == 0.95


def test_valid_response_soporte_tecnico() -> None:
    """
    Verifica que la categoría 'Soporte Técnico' (con tilde) sea reconocida
    como válida por el validador.

    Este caso es especialmente relevante ya que la tilde en 'Técnico' podría
    causar problemas de encoding en validadores que usen comparación byte a byte.
    """
    data = _validate_gemini_response('{"categoría": "Soporte Técnico", "confianza": 0.82}')
    assert data["categoría"] == "Soporte Técnico"


def test_invalid_json_raises() -> None:
    """
    Verifica que una cadena que no es JSON válido eleva GeminiResponseInvalidError
    con el mensaje descriptivo 'JSON inválido'.

    Este caso ocurre cuando Gemini devuelve texto libre en lugar de JSON
    estructurado, situación documentada en la especificación de Gemini 2.5 Flash.
    """
    with pytest.raises(GeminiResponseInvalidError, match="JSON inválido"):
        _validate_gemini_response("not json at all")


def test_missing_categoria_raises() -> None:
    """
    Verifica que un JSON sin el campo 'categoría' eleva GeminiResponseInvalidError.

    El campo 'categoría' es obligatorio en el contrato del prompt documentado
    en docs/prompt_gemini.txt. Su ausencia implica que Gemini no siguió
    el formato de salida especificado.
    """
    with pytest.raises(GeminiResponseInvalidError, match="categoría"):
        _validate_gemini_response('{"confianza": 0.9}')


def test_invalid_categoria_value_raises() -> None:
    """
    Verifica que una categoría fuera del conjunto válido eleva GeminiResponseInvalidError
    con el mensaje 'Categoría inválida'.

    El conjunto de categorías permitidas es exactamente:
    {"Sistemas", "Operaciones", "Soporte Técnico"}.
    Cualquier otro valor (e.g., "Hardware") es rechazado para evitar
    que registros con categorías incorrectas contaminen la base de datos.
    """
    with pytest.raises(GeminiResponseInvalidError, match="Categoría inválida"):
        _validate_gemini_response('{"categoría": "Hardware", "confianza": 0.9}')


def test_missing_confianza_raises() -> None:
    """
    Verifica que un JSON sin el campo 'confianza' eleva GeminiResponseInvalidError.

    El campo 'confianza' es necesario para que el clasificador híbrido pueda
    determinar si el resultado requiere revisión humana (confianza < 0.70).
    """
    with pytest.raises(GeminiResponseInvalidError, match="confianza"):
        _validate_gemini_response('{"categoría": "Sistemas"}')


def test_confianza_out_of_range_raises() -> None:
    """
    Verifica que una confianza fuera del rango [0.0, 1.0] eleva GeminiResponseInvalidError
    con el mensaje 'Confianza inválida'.

    Un valor como 1.5 indicaría que Gemini no siguió el formato solicitado,
    y permitirlo podría romper la invariante del schema ClasificacionResult
    (Field ge=0.0, le=1.0).
    """
    with pytest.raises(GeminiResponseInvalidError, match="Confianza inválida"):
        _validate_gemini_response('{"categoría": "Sistemas", "confianza": 1.5}')


def test_confianza_as_integer_is_valid() -> None:
    """
    Verifica que una confianza expresada como entero (1 en lugar de 1.0)
    sea aceptada por el validador.

    El estándar JSON no distingue entre 1 y 1.0 para valores numéricos,
    y Python los trata como equivalentes. Este caso cubre la situación donde
    Gemini omite el punto decimal al expresar certeza máxima.
    """
    data = _validate_gemini_response('{"categoría": "Operaciones", "confianza": 1}')
    assert data["confianza"] == 1.0


def test_markdown_wrapped_json_raises() -> None:
    """
    Verifica que un JSON envuelto en bloque de código Markdown eleva GeminiResponseInvalidError.

    Gemini puede devolver su respuesta formateada como:
        ```json
        {"categoría": "Sistemas", "confianza": 0.9}
        ```
    Esta respuesta no puede ser parseada directamente con json.loads(), por lo que
    debe ser rechazada. El clasificador registra este caso y activa el fallback.
    """
    with pytest.raises(GeminiResponseInvalidError):
        _validate_gemini_response('```json\n{"categoría": "Sistemas", "confianza": 0.9}\n```')
