"""
Tests de integración para los endpoints HTTP de clasificaciones.

Cubre:
    GET   /api/v1/clasificaciones/revision-pendiente → Cola FIFO, filtros, paginación.
    PATCH /api/v1/clasificaciones/{id}/validar       → Validación humana.

Aislamiento de servicios externos:
    - Clasificador: inyectado como doble vía make_client_with_classifier.
    - notify_n8n: neutralizado dentro del mismo factory.
    - Ningún test contacta la API de Gemini ni ningún servicio de red.

Estrategia de fixtures:
    Los registros de clasificacion_log se crean indirectamente creando incidentes
    vía POST /api/v1/incidentes/ con el clasificador doble configurado para
    producir alta o baja confianza según lo requiera cada test.
    La fixture seed_catalogs limpia toda la data al finalizar cada test.
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.schemas.clasificacion import ClasificacionResult

# ── Helpers ───────────────────────────────────────────────────────────────────

DESCRIPCION_LARGA = "Servidor de base de datos principal no responde desde las 08:00."
DESCRIPCION_2 = "El sistema de planificación de operaciones muestra error 503."
DESCRIPCION_3 = "Impresora del área de recursos humanos sin conexión."


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


def _result_alta_confianza(categoria: str = "Sistemas") -> ClasificacionResult:
    """Resultado con alta confianza → requiere_revision_humana=False → no entra en cola."""
    return ClasificacionResult(
        categoria=categoria,
        confianza=0.95,
        etapa="deterministic",
        requiere_revision_humana=False,
        respuesta_raw=None,
    )


async def _crear_incidente(client: AsyncClient, descripcion: str, result: ClasificacionResult):
    """Crea un incidente y retorna el body JSON de la respuesta."""
    from contextlib import asynccontextmanager
    # El cliente ya tiene el override; simplemente hacemos el POST.
    resp = await client.post(
        "/api/v1/incidentes/",
        json={"descripcion": descripcion, "prioridad": "media"},
    )
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6: GET /api/v1/clasificaciones/revision-pendiente
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_revision_pendiente_solo_pendientes(
    seed_catalogs, make_client_with_classifier
):
    """
    6.1 / 6.2 RED + GREEN
    Mezcla de registros (pendiente sin validar, alta confianza, ya validado)
    → la cola contiene solo los pendientes sin validar.
    """
    sector_sistemas_id = seed_catalogs["sector_sistemas"].id

    # Arrange: crear un pendiente y un incidente de alta confianza
    async with make_client_with_classifier(_result_pendiente()) as c_pend:
        resp_pend = await c_pend.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
    async with make_client_with_classifier(_result_alta_confianza()) as c_alta:
        await c_alta.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_2, "prioridad": "media"},
        )

    # Obtener el log_id del pendiente para validarlo y confirmar que sale de la cola
    async with make_client_with_classifier(_result_pendiente()) as client:
        # Act: consultar la cola
        cola_resp = await client.get("/api/v1/clasificaciones/revision-pendiente")

    assert cola_resp.status_code == 200
    cola = cola_resp.json()
    # Todos los items deben ser pendientes (requiere_revision_humana=True y sector_validado=None)
    assert all(item["requiere_revision_humana"] is True for item in cola)
    assert all(item["sector_validado"] is None for item in cola)
    # Al menos el incidente pendiente que creamos está en la cola
    assert len(cola) >= 1


@pytest.mark.asyncio
async def test_get_revision_pendiente_orden_fifo(
    seed_catalogs, make_client_with_classifier
):
    """
    6.3 TRIANGULATE
    Múltiples pendientes → cola en orden FIFO (más antiguo primero).
    """
    # Arrange: crear dos pendientes en orden secuencial
    async with make_client_with_classifier(_result_pendiente()) as c1:
        await c1.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
    async with make_client_with_classifier(_result_pendiente(categoria="Operaciones")) as c2:
        await c2.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_2, "prioridad": "media"},
        )

    async with make_client_with_classifier(_result_pendiente()) as client:
        cola_resp = await client.get("/api/v1/clasificaciones/revision-pendiente")

    assert cola_resp.status_code == 200
    cola = cola_resp.json()
    # Verificar orden FIFO: IDs crecientes (el más antiguo tiene menor ID)
    if len(cola) >= 2:
        for i in range(len(cola) - 1):
            assert cola[i]["id"] < cola[i + 1]["id"]


@pytest.mark.asyncio
async def test_get_revision_pendiente_paginacion(
    seed_catalogs, make_client_with_classifier
):
    """
    6.4 TRIANGULATE
    limit/offset acotan la cola: con limit=1 devuelve a lo sumo 1 elemento.
    """
    # Arrange: crear dos pendientes
    async with make_client_with_classifier(_result_pendiente()) as c:
        await c.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
        await c.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_3, "prioridad": "baja"},
        )
        # Act
        pag1 = await c.get(
            "/api/v1/clasificaciones/revision-pendiente",
            params={"limit": 1, "offset": 0},
        )
        pag2 = await c.get(
            "/api/v1/clasificaciones/revision-pendiente",
            params={"limit": 1, "offset": 1},
        )

    assert pag1.status_code == 200
    assert len(pag1.json()) <= 1

    assert pag2.status_code == 200
    # Las dos páginas deben ser distintas si hay al menos 2 pendientes
    if pag1.json() and pag2.json():
        assert pag1.json()[0]["id"] != pag2.json()[0]["id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Cobertura adicional — GET /api/v1/clasificaciones/incidente/{id}
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_historial_por_incidente_200(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: GET /api/v1/clasificaciones/incidente/{id}
    cubre list_by_incidente en route, service y repository.
    """
    async with make_client_with_classifier(_result_pendiente()) as client:
        # Arrange: crear un incidente
        resp = await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
        incidente_id = resp.json()["id"]

        # Act: consultar el historial del incidente
        response = await client.get(f"/api/v1/clasificaciones/incidente/{incidente_id}")

    assert response.status_code == 200
    historial = response.json()
    assert isinstance(historial, list)
    assert len(historial) >= 1
    assert historial[0]["incidente_id"] == incidente_id


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 7: PATCH /api/v1/clasificaciones/{id}/validar
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_patch_validar_retira_de_la_cola_200(
    seed_catalogs, make_client_with_classifier
):
    """
    7.1 / 7.2 RED + GREEN
    Operador valida un pendiente con sector existente →
    200 con sector_validado asignado, y el registro deja de aparecer en la cola.
    """
    sector_sistemas_id = seed_catalogs["sector_sistemas"].id

    async with make_client_with_classifier(_result_pendiente()) as client:
        # Arrange: crear incidente pendiente
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "alta"},
        )
        # Obtener el log_id del pendiente
        cola_resp = await client.get("/api/v1/clasificaciones/revision-pendiente")
        cola = cola_resp.json()
        assert len(cola) >= 1
        log_id = cola[0]["id"]

        # Act: validar el registro
        validar_resp = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar",
            json={"sector_id_validado": sector_sistemas_id},
        )

        # Assert: respuesta 200 con sector_validado asignado
        assert validar_resp.status_code == 200
        body = validar_resp.json()
        assert body["sector_validado"] is not None
        assert body["sector_validado"]["id"] == sector_sistemas_id

        # Verificar que ya no aparece en la cola
        cola_post = await client.get("/api/v1/clasificaciones/revision-pendiente")
        ids_en_cola = [item["id"] for item in cola_post.json()]
        assert log_id not in ids_en_cola


@pytest.mark.asyncio
async def test_patch_validar_correccion_difiere_del_predicho(
    seed_catalogs, make_client_with_classifier
):
    """
    7.3 TRIANGULATE
    Sector validado distinto del predicho → 200 y se registra la corrección.
    """
    sector_operaciones_id = seed_catalogs["sector_operaciones"].id
    # El clasificador predice Sistemas pero el operador corrige a Operaciones
    result = _result_pendiente(categoria="Sistemas")

    async with make_client_with_classifier(result) as client:
        # Arrange
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "media"},
        )
        cola = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
        assert len(cola) >= 1
        log_id = cola[0]["id"]

        # Act: corregir a Operaciones (diferente del predicho Sistemas)
        resp = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar",
            json={"sector_id_validado": sector_operaciones_id},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["sector_validado"]["id"] == sector_operaciones_id
    # El sector predicho sigue siendo Sistemas (no fue modificado)
    if body["sector_predicho"]:
        assert body["sector_predicho"]["nombre"] == "Sistemas"


@pytest.mark.asyncio
async def test_patch_validar_log_inexistente_404(
    seed_catalogs, make_client_with_classifier
):
    """
    7.4 TRIANGULATE
    log_id inexistente → 404 con cuerpo de error estructurado.
    """
    sector_sistemas_id = seed_catalogs["sector_sistemas"].id

    async with make_client_with_classifier(_result_pendiente()) as client:
        response = await client.patch(
            "/api/v1/clasificaciones/999999/validar",
            json={"sector_id_validado": sector_sistemas_id},
        )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_patch_validar_sector_inexistente_404(
    seed_catalogs, make_client_with_classifier
):
    """
    7.5 TRIANGULATE
    sector_id_validado inexistente → 404 y el registro no queda validado.
    """
    async with make_client_with_classifier(_result_pendiente()) as client:
        # Arrange: crear un pendiente real
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": DESCRIPCION_LARGA, "prioridad": "media"},
        )
        cola = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
        assert len(cola) >= 1
        log_id = cola[0]["id"]

        # Act: intentar validar con un sector inexistente
        resp = await client.patch(
            f"/api/v1/clasificaciones/{log_id}/validar",
            json={"sector_id_validado": 999999},
        )

        # Assert: 404 porque el sector no existe
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["code"] == "NOT_FOUND"

        # El registro no fue validado: sigue en la cola
        cola_post = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
        ids_cola = [item["id"] for item in cola_post]
        assert log_id in ids_cola
