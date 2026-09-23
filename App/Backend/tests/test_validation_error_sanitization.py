"""
Tests de sanitizacion de errores de validacion (c-54, W1 / DIR-006).

El handler global de `RequestValidationError` serializaba `exc.errors()`, que
incluye el valor enviado (`input`) y `ctx`. Un 422 con un telefono/email
invalido devolvia el dato en claro. Estos tests exigen que la respuesta de
validacion conserve SOLO `loc`, `msg` y `type`, de forma GLOBAL (no solo en el
directorio).
"""

import pytest

from app.core.error_handlers import _sanitize_validation_errors

_PII_TELEFONO = "+5491100000111111111111111111111111111111"


def test_sanitize_descarta_input_ctx_y_url():
    """La lista saneada conserva loc/msg/type y descarta input/ctx/url."""
    errors = [
        {
            "type": "string_too_long",
            "loc": ("body", "telefono"),
            "msg": "String should have at most 20 characters",
            "input": _PII_TELEFONO,
            "ctx": {"max_length": 20},
            "url": "https://errors.pydantic.dev/2.5/v/string_too_long",
        }
    ]

    limpio = _sanitize_validation_errors(errors)

    assert limpio == [
        {
            "loc": ["body", "telefono"],
            "msg": "String should have at most 20 characters",
            "type": "string_too_long",
        }
    ]
    assert _PII_TELEFONO not in repr(limpio)


@pytest.mark.asyncio
async def test_422_global_no_refleja_el_valor_enviado(client):
    """Un 422 de otro recurso tampoco devuelve el valor enviado (global)."""
    pii = "pii-leak-directorio@example.test"
    resp = await client.post(
        "/api/v1/incidentes/",
        json={
            "descripcion": "incidente valido con descripcion suficiente",
            "origen_message_id": pii + ("x" * 300),
        },
    )

    assert resp.status_code == 422, resp.text
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert pii not in resp.text, "El 422 no debe reflejar el valor enviado"
    # El `loc` si se conserva para que el cliente sepa que campo fallo.
    assert "origen_message_id" in resp.text
