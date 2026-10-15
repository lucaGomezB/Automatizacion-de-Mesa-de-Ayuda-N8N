"""Integration: guard de prioridad critica deniega por defecto (c-90, RP-006).

Requiere PostgreSQL (marker `integration`). Confirma contra la base descartable
que una cuenta autenticada SIN empleado vinculado recibe 403 al enviar `critica`
(denegacion por defecto, D5), sin invocar al clasificador: el guard corre como
dependencia de la ruta, antes del servicio.
"""

import pytest

DESCRIPCION = "El servidor de base de datos principal no responde desde esta manana."


@pytest.mark.integration
async def test_cuenta_sin_empleado_critica_403(pg_client):
    resp = await pg_client.post(
        "/api/v1/incidentes/",
        json={"descripcion": DESCRIPCION, "prioridad": "critica"},
    )

    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["code"] == "FORBIDDEN"
