"""
Test de integracion del delta de sector antes/despues (c-165, ASG-005; tarea 2.10).

El delta no necesita columnas nuevas: se reconstruye comparando lo PREDICHO
(`sector_id_predicho` + `sectores_predichos`) con lo VALIDADO (`sector_id_validado` +
`sectores_validados`) del mismo log. Se ejerce el flujo completo: alta de un incidente
con clasificador doble (que persiste el conjunto predicho), validacion humana y lectura
del historial por la API.
"""

import pytest

from app.schemas.clasificacion import ClasificacionResult
from app.services.intervencion_estado import hubo_cambio_de_sector

DESCRIPCION = "Servidor de base de datos principal no responde desde las 08:00."


def _prediccion() -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho="Sistemas",
        sectores_adicionales=["Bases de Datos"],
        confianza=0.55,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw="{}",
    )


async def _alta_y_validacion(make_client_with_classifier, payload_validar):
    async with make_client_with_classifier(_prediccion()) as client:
        alta = await client.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "media"}
        )
        assert alta.status_code == 201, alta.text
        incidente_id = alta.json()["id"]
        log_id = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()[0]["id"]
        validar = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar", json=payload_validar
        )
        assert validar.status_code == 200, validar.text
        historial = (await client.get(f"/api/v1/clasificaciones/incidente/{incidente_id}")).json()
    assert len(historial) == 1
    return historial[0]


def _conjunto(principal, adicionales) -> tuple[str | None, frozenset[str]]:
    nombre = principal["nombre"] if principal else None
    return nombre, frozenset(s["nombre"] for s in adicionales)


@pytest.mark.asyncio
async def test_la_correccion_deja_reconstruible_el_conjunto_antes_y_despues(
    seed_catalogs, make_client_with_classifier
):
    log = await _alta_y_validacion(
        make_client_with_classifier,
        {"sector_validado": "Soporte Tecnico Software", "sectores_adicionales": ["Sistemas"]},
    )

    antes = _conjunto(log["sector_predicho"], log["sectores_predichos"])
    despues = _conjunto(log["sector_validado"], log["sectores_validados"])

    assert antes == ("Sistemas", frozenset({"Bases de Datos"}))
    assert despues == ("Soporte Tecnico Software", frozenset({"Sistemas"}))
    assert hubo_cambio_de_sector(log["sector_predicho"]["id"], log["sector_validado"]["id"])
    # El log conserva la prediccion original: la validacion no la sobrescribe.
    assert log["etapa"] == "gemini"
    assert log["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_la_confirmacion_conserva_el_principal_y_registra_el_delta_de_adicionales(
    seed_catalogs, make_client_with_classifier
):
    log = await _alta_y_validacion(
        make_client_with_classifier,
        {"sector_validado": "Sistemas", "sectores_adicionales": []},
    )

    antes = _conjunto(log["sector_predicho"], log["sectores_predichos"])
    despues = _conjunto(log["sector_validado"], log["sectores_validados"])

    assert antes == ("Sistemas", frozenset({"Bases de Datos"}))
    assert despues == ("Sistemas", frozenset())
    # Mismo principal: no hay cambio de sector aunque el operador quitara un adicional.
    assert not hubo_cambio_de_sector(log["sector_predicho"]["id"], log["sector_validado"]["id"])
    assert log["validado_en"] is not None
    assert log["origen_intervencion"] == "gate"
