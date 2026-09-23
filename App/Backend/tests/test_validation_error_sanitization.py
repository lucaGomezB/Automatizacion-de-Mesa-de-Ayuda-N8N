"""
Tests de sanitizacion de errores de validacion (c-54, W1 / DIR-006).

El handler global de `RequestValidationError` serializaba `exc.errors()`, que
incluye el valor enviado (`input`) y `ctx`. Un 422 con un telefono/email
invalido devolvia el dato en claro. Estos tests exigen que la respuesta de
validacion conserve SOLO `loc`, `msg` y `type`, de forma GLOBAL (no solo en el
directorio).

W1 (completitud): sanear `input`/`ctx` no alcanza si el propio validador
interpola el valor enviado DENTRO del mensaje (`msg`), porque Pydantic lo
conserva. Estos tests exigen que NINGUN validador personalizado refleje el valor
sometido en el cuerpo del 422, ni por `input`, ni por `ctx`, ni por `msg`.
"""

import pytest

from app.core.error_handlers import _sanitize_validation_errors

_PII_TELEFONO = "+5491100000111111111111111111111111111111"

# Valor "con forma de PII" reutilizado por todos los casos: un email/telefono
# improbable que debe desaparecer por completo del cuerpo del 422.
_PII_SOMETIDO = "pii.leak+5491100000111@example.test"


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


def _assert_no_echo(resp, campo: str) -> None:
    """Invariante: 422 sin eco del valor y con el campo identificable en `loc`."""
    assert resp.status_code == 422, resp.text
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert _PII_SOMETIDO not in resp.text, (
        "El 422 no debe reflejar el valor sometido (ni por input, ni por ctx, "
        f"ni por msg); campo: {campo}"
    )
    assert campo in resp.text, "El `loc` debe conservarse para identificar el campo"


@pytest.mark.asyncio
async def test_422_origen_evento_custom_validator_no_refleja_el_valor(client):
    """Validador custom de `origen_evento` (incidente): sin eco en `msg`."""
    resp = await client.post(
        "/api/v1/incidentes/",
        json={
            "descripcion": "incidente valido con descripcion suficiente",
            "origen_evento": _PII_SOMETIDO,
        },
    )
    _assert_no_echo(resp, "origen_evento")


@pytest.mark.asyncio
async def test_422_sector_predicho_custom_validator_no_refleja_el_valor(client):
    """Validador custom de `clasificacion.sector_predicho`: sin eco en `msg`."""
    resp = await client.post(
        "/api/v1/incidentes/",
        json={
            "descripcion": "incidente valido con descripcion suficiente",
            "clasificacion": {"sector_predicho": _PII_SOMETIDO},
        },
    )
    _assert_no_echo(resp, "sector_predicho")


@pytest.mark.asyncio
async def test_422_sectores_adicionales_custom_validator_no_refleja_el_valor(client):
    """Validador custom de `sectores_adicionales` (lista): sin eco en `msg`."""
    resp = await client.post(
        "/api/v1/incidentes/",
        json={
            "descripcion": "incidente valido con descripcion suficiente",
            "clasificacion": {"sectores_adicionales": [_PII_SOMETIDO]},
        },
    )
    _assert_no_echo(resp, "sectores_adicionales")


@pytest.mark.asyncio
async def test_422_sector_validado_custom_validator_no_refleja_el_valor(client):
    """Validador custom de `sector_validado` (validar): sin eco en `msg`."""
    resp = await client.patch(
        "/api/v1/clasificaciones/999999/validar",
        json={"sector_validado": _PII_SOMETIDO},
    )
    _assert_no_echo(resp, "sector_validado")


@pytest.mark.asyncio
async def test_422_sectores_adicionales_validar_no_refleja_el_valor(client):
    """Validador custom de `sectores_adicionales` (validar): sin eco en `msg`."""
    resp = await client.patch(
        "/api/v1/clasificaciones/999999/validar",
        json={
            "sector_id_validado": 1,
            "sectores_adicionales": [_PII_SOMETIDO],
        },
    )
    _assert_no_echo(resp, "sectores_adicionales")
