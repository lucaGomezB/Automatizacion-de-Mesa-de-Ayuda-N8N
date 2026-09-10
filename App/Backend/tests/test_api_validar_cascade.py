"""
Tests de integración del efecto cascada de la validación humana sobre el incidente.

Regression: ISSUE-002 — la validación humana registraba el veredicto en
clasificacion_log (sector_id_validado) pero el incidente conservaba el sector
predicho erróneo y requiere_revision_humana=True para siempre: el ticket quedaba
ruteado al sector equivocado y la lista de administración mostraba el indicador
de revisión pendiente aunque la cola ya estuviera vacía.
Found by /qa on 2026-06-12.
Report: .gstack/qa-reports/qa-report-localhost-2026-06-12.md

Comportamiento esperado (cascada en la misma transacción):
    PATCH /api/v1/clasificaciones/{id}/validar
        → asigna sector_id_validado en el log (auditoría, ya cubierto en
          test_api_clasificaciones.py)
        → actualiza incidente.sector_id al sector validado
        → limpia incidente.requiere_revision_humana

La auditoría NO se altera: sector_predicho del log conserva la predicción
original, que es la etiqueta que alimenta las métricas de la tesis.

Aislamiento de servicios externos:
    - Clasificador: inyectado como doble vía make_client_with_classifier.
    - Ningún test contacta la API de Gemini ni ningún servicio de red.
"""

import pytest

from app.schemas.clasificacion import ClasificacionResult

DESCRIPCION_LARGA = "Servidor de base de datos principal no responde desde las 08:00."


def _result_pendiente(
    categoria: str = "Sistemas",
    confianza: float = 0.55,
) -> ClasificacionResult:
    """Resultado con baja confianza → requiere_revision_humana=True → entra en cola."""
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw='{"categoría": "Sistemas", "confianza": 0.55}',
    )


@pytest.mark.asyncio
async def test_patch_validar_correccion_actualiza_incidente(
    seed_catalogs, make_client_with_classifier
):
    """
    Corrección humana (sector validado ≠ predicho) →
    el incidente queda asignado al sector validado y sin flag de revisión,
    mientras el log conserva la predicción original para auditoría.
    """
    sector_operaciones_id = seed_catalogs["sector_operaciones"].id

    async with make_client_with_classifier(_result_pendiente(categoria="Sistemas")) as client:
        # Arrange: incidente pendiente predicho como Sistemas
        crear_resp = await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "media"},
        )
        incidente_id = crear_resp.json()["id"]
        cola = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
        log_id = cola[0]["id"]

        # Act: el operador corrige a Operaciones
        validar_resp = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar",
            json={"sector_id_validado": sector_operaciones_id},
        )
        assert validar_resp.status_code == 200

        # Assert: el incidente refleja la corrección
        detalle = (await client.get(f"/api/v1/incidentes/{incidente_id}")).json()
        assert detalle["sector"]["id"] == sector_operaciones_id
        assert detalle["requiere_revision_humana"] is False

        # Assert: la auditoría conserva la predicción original
        historial = (
            await client.get(f"/api/v1/clasificaciones/incidente/{incidente_id}")
        ).json()
        assert historial[0]["sector_predicho"]["nombre"] == "Sistemas"
        assert historial[0]["sector_validado"]["id"] == sector_operaciones_id


@pytest.mark.asyncio
async def test_patch_validar_confirmacion_limpia_flag_revision(
    seed_catalogs, make_client_with_classifier
):
    """
    Confirmación humana (sector validado == predicho) →
    el incidente conserva el sector predicho pero el flag de revisión se limpia.
    """
    sector_sistemas_id = seed_catalogs["sector_sistemas"].id

    async with make_client_with_classifier(_result_pendiente(categoria="Sistemas")) as client:
        crear_resp = await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
        incidente_id = crear_resp.json()["id"]
        cola = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
        log_id = cola[0]["id"]

        # Act: el operador confirma la predicción
        validar_resp = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar",
            json={"sector_id_validado": sector_sistemas_id},
        )
        assert validar_resp.status_code == 200

        # Assert: mismo sector, flag de revisión limpio
        detalle = (await client.get(f"/api/v1/incidentes/{incidente_id}")).json()
        assert detalle["sector"]["id"] == sector_sistemas_id
        assert detalle["requiere_revision_humana"] is False
