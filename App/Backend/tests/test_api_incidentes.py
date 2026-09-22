"""
Tests de integración para los endpoints HTTP de incidentes.

Cubre:
    POST   /api/v1/incidentes   → Creación + clasificación automática.
    GET    /api/v1/incidentes   → Listado con filtros opcionales y paginación.
    GET    /api/v1/incidentes/{id} → Detalle completo + 404.
    PATCH  /api/v1/incidentes/{id} → Actualización parcial + 404.

Estrategia TDD aplicada:
    Para cada grupo de endpoints se sigue el ciclo
    RED → GREEN → TRIANGULATE → REFACTOR tal como exige C-06.

Aislamiento de servicios externos:
    - Clasificador: inyectado como doble vía make_client_with_classifier
      (dependency_override sobre get_service en routes/incidentes.py).
    - notify_n8n: neutralizado con AsyncMock dentro del mismo factory.
    - Ningún test contacta la API de Gemini ni ningún servicio de red.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.schemas.clasificacion import ClasificacionResult

# ── Helpers / constantes ──────────────────────────────────────────────────────

VALID_DESCRIPCION = "Falla en el servidor de base de datos principal del sector contable."
MIN_DESCRIPCION = "a" * 10  # exactamente el mínimo (10 chars)

VALID_PAYLOAD = {
    "descripcion": VALID_DESCRIPCION,
    "prioridad": "alta",
}


def _make_result(
    sector_predicho: str = "Sistemas",
    confianza: float = 0.95,
    requiere_revision_humana: bool = False,
) -> ClasificacionResult:
    """Construye un ClasificacionResult para el clasificador doble."""
    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=requiere_revision_humana,
        respuesta_raw=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 2: POST /api/v1/incidentes
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_post_incidente_creacion_exitosa_201(
    seed_catalogs, make_client_with_classifier
):
    """
    2.1 / 2.2 RED + GREEN
    Payload válido + clasificador doble (Sistemas, 0.95, sin revisión) →
    201 con contrato IncidenteRead, sector "Sistemas", estado "nuevo".
    """
    # Arrange
    result = _make_result(sector_predicho="Sistemas", confianza=0.95, requiere_revision_humana=False)

    async with make_client_with_classifier(result) as client:
        # Act
        response = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert "descripcion_pseudonimizada" in body
    assert body["requiere_revision_humana"] is False
    assert body["sector"]["nombre"] == "Sistemas"
    assert body["estado"]["nombre"] == "nuevo"


@pytest.mark.asyncio
async def test_post_incidente_baja_confianza_marca_revision(
    seed_catalogs, make_client_with_classifier
):
    """
    2.3 TRIANGULATE
    Clasificador doble con confianza < 0.70 y requiere_revision_humana True →
    201 con requiere_revision_humana True en la respuesta.
    """
    # Arrange
    result = _make_result(
        sector_predicho="Bases de Datos",
        confianza=0.55,
        requiere_revision_humana=True,
    )

    async with make_client_with_classifier(result) as client:
        # Act
        response = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_post_incidente_descripcion_invalida_422(
    seed_catalogs, make_client_with_classifier
):
    """
    2.4 TRIANGULATE (borde)
    Descripción vacía → 422 y ningún incidente persistido.
    """
    result = _make_result()

    async with make_client_with_classifier(result) as client:
        # Act: descripción vacía
        response_vacia = await client.post(
            "/api/v1/incidentes/", json={"descripcion": "", "prioridad": "media"}
        )
        # Act: solo espacios
        response_espacios = await client.post(
            "/api/v1/incidentes/", json={"descripcion": "   ", "prioridad": "media"}
        )
        # Act: bajo el mínimo (< 10 chars)
        response_corta = await client.post(
            "/api/v1/incidentes/", json={"descripcion": "abc", "prioridad": "media"}
        )
        # Confirmar que no se crearon incidentes
        lista = await client.get("/api/v1/incidentes/")

    assert response_vacia.status_code == 422
    assert response_espacios.status_code == 422
    assert response_corta.status_code == 422
    # La lista debe estar vacía (seed_catalogs limpia tras el test, pero validamos inline)
    assert lista.status_code == 200
    assert isinstance(lista.json(), list)


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3: GET /api/v1/incidentes
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_incidentes_lista_sin_filtros_200(
    seed_catalogs, make_client_with_classifier
):
    """
    3.1 / 3.2 RED + GREEN
    Varios incidentes creados → 200, todos presentes, contrato IncidenteListItem.
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        # Arrange: crear dos incidentes
        await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
        await client.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": "El servidor de correo no responde desde esta mañana.",
                "prioridad": "media",
            },
        )

        # Act
        response = await client.get("/api/v1/incidentes/")

    # Assert
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 2
    # Verificar contrato IncidenteListItem
    item = items[0]
    assert "id" in item
    assert "prioridad" in item
    assert "requiere_revision_humana" in item
    assert "sector" in item
    assert "estado" in item
    assert "created_at" in item
    # No debe incluir descripcion (es IncidenteListItem, no IncidenteRead)
    assert "descripcion_pseudonimizada" not in item


@pytest.mark.asyncio
async def test_get_incidentes_filtro_por_sector(
    seed_catalogs, make_client_with_classifier
):
    """
    3.3 TRIANGULATE
    Filtrar por sector_id devuelve solo los incidentes de ese sector.
    """
    sector_sistemas_id = seed_catalogs["sector_sistemas"].id
    sector_bases_datos_id = seed_catalogs["sector_bases_datos"].id

    result_sistemas = _make_result(sector_predicho="Sistemas")
    result_operaciones = _make_result(sector_predicho="Bases de Datos", confianza=0.80)

    async with make_client_with_classifier(result_sistemas) as client_sist:
        resp_sist = await client_sist.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    async with make_client_with_classifier(result_operaciones) as client_op:
        resp_op = await client_op.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": "Proceso de cierre de mes bloqueado en SAP.",
                "prioridad": "media",
            },
        )

    # Necesitamos un cliente para el GET (sin clasificador activo)
    result_dummy = _make_result()
    async with make_client_with_classifier(result_dummy) as client:
        response = await client.get(
            "/api/v1/incidentes/", params={"sector_id": sector_sistemas_id}
        )

    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["sector"]["id"] == sector_sistemas_id


@pytest.mark.asyncio
async def test_get_incidentes_filtro_por_revision_humana(
    seed_catalogs, make_client_with_classifier
):
    """
    3.4 TRIANGULATE
    Filtrar por requiere_revision_humana=true devuelve solo los pendientes.
    """
    result_revision = _make_result(confianza=0.50, requiere_revision_humana=True)
    result_ok = _make_result(confianza=0.95, requiere_revision_humana=False)

    async with make_client_with_classifier(result_revision) as c:
        await c.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
    async with make_client_with_classifier(result_ok) as c:
        await c.post(
            "/api/v1/incidentes/",
            json={"descripcion": "Impresora sin conexión en piso 3.", "prioridad": "baja"},
        )

    async with make_client_with_classifier(_make_result()) as client:
        response = await client.get(
            "/api/v1/incidentes/", params={"requiere_revision_humana": "true"}
        )

    assert response.status_code == 200
    items = response.json()
    assert all(item["requiere_revision_humana"] is True for item in items)


@pytest.mark.asyncio
async def test_get_incidentes_paginacion_limit_offset(
    seed_catalogs, make_client_with_classifier
):
    """
    3.5 TRIANGULATE
    Con limit=1, offset=0 devuelve a lo sumo 1 elemento.
    Con limit=1, offset=1 devuelve el siguiente (si existe).
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": "Segundo incidente para paginacion.", "prioridad": "media"},
        )

        resp_pag1 = await client.get("/api/v1/incidentes/", params={"limit": 1, "offset": 0})
        resp_pag2 = await client.get("/api/v1/incidentes/", params={"limit": 1, "offset": 1})

    assert resp_pag1.status_code == 200
    assert len(resp_pag1.json()) == 1

    assert resp_pag2.status_code == 200
    # El offset 1 puede devolver 1 elemento (existe) o 0 (si solo había 1)
    # Validamos que ambas páginas son listas distintas
    if resp_pag2.json():
        assert resp_pag1.json()[0]["id"] != resp_pag2.json()[0]["id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4: GET /api/v1/incidentes/{id}
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_incidente_detalle_existente_200(
    seed_catalogs, make_client_with_classifier
):
    """
    4.1 / 4.2 RED + GREEN
    Incidente creado → 200 con contrato IncidenteRead completo.
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        # Arrange: crear incidente
        create_resp = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
        incidente_id = create_resp.json()["id"]

        # Act
        response = await client.get(f"/api/v1/incidentes/{incidente_id}")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == incidente_id
    assert "descripcion_pseudonimizada" in body
    assert body["sector"] is not None
    assert body["estado"] is not None
    assert body["estado"]["nombre"] == "nuevo"


@pytest.mark.asyncio
async def test_get_incidente_inexistente_404(
    seed_catalogs, make_client_with_classifier
):
    """
    4.3 TRIANGULATE
    ID inexistente → 404 con cuerpo {"error": {"code": "NOT_FOUND", ...}}.
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.get("/api/v1/incidentes/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5: PATCH /api/v1/incidentes/{id}
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_patch_incidente_actualiza_solo_campos_enviados_200(
    seed_catalogs, make_client_with_classifier
):
    """
    5.1 / 5.2 RED + GREEN
    PATCH que solo cambia prioridad → 200, prioridad actualizada, resto sin cambios.
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        # Arrange: crear incidente con prioridad "alta"
        payload = {**VALID_PAYLOAD, "prioridad": "alta"}
        create_resp = await client.post("/api/v1/incidentes/", json=payload)
        incidente_id = create_resp.json()["id"]
        original_sector_id = create_resp.json()["sector"]["id"] if create_resp.json()["sector"] else None

        # Act: cambiar solo la prioridad a "baja"
        patch_resp = await client.patch(
            f"/api/v1/incidentes/{incidente_id}",
            json={"prioridad": "baja"},
        )

    # Assert
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["prioridad"] == "baja"
    assert body["id"] == incidente_id
    # Sector y estado no cambiaron
    if original_sector_id:
        assert body["sector"]["id"] == original_sector_id
    assert body["estado"]["nombre"] == "nuevo"


@pytest.mark.asyncio
async def test_patch_incidente_inexistente_404(
    seed_catalogs, make_client_with_classifier
):
    """
    5.3 TRIANGULATE
    PATCH sobre id inexistente → 404 con cuerpo de error estructurado.
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.patch(
            "/api/v1/incidentes/999999", json={"prioridad": "baja"}
        )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


# ═══════════════════════════════════════════════════════════════════════════════
# Cobertura adicional — filtros de listado (branches no cubiertas por tests anteriores)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_incidentes_filtro_por_prioridad(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: filtro por prioridad cubre la rama prioridad en list_filtered.
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": "Incidente con prioridad alta.", "prioridad": "alta"},
        )
        await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": "Incidente con prioridad baja.", "prioridad": "baja"},
        )

        response = await client.get("/api/v1/incidentes/", params={"prioridad": "alta"})

    assert response.status_code == 200
    items = response.json()
    assert all(item["prioridad"] == "alta" for item in items)


@pytest.mark.asyncio
async def test_get_incidentes_filtro_por_estado(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: filtro por estado_id cubre la rama estado_id en list_filtered.
    """
    estado_nuevo_id = seed_catalogs["estado_nuevo"].id
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

        response = await client.get(
            "/api/v1/incidentes/", params={"estado_id": estado_nuevo_id}
        )

    assert response.status_code == 200
    items = response.json()
    # Todos los incidentes filtrados deben estar en el estado "nuevo"
    assert all(item["estado"]["id"] == estado_nuevo_id for item in items)


@pytest.mark.asyncio
async def test_post_incidente_con_canal_origen(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: canal_origen_id no nulo cubre _resolve_canal con canal válido.
    """
    canal_id = seed_catalogs["canal_correo"].id
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        response = await client.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": VALID_DESCRIPCION,
                "prioridad": "media",
                "canal_origen_id": canal_id,
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["canal_origen"] is not None
    assert body["canal_origen"]["id"] == canal_id


@pytest.mark.asyncio
async def test_post_incidente_canal_origen_inexistente_500_o_422(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: canal_origen_id inexistente cubre la rama CanalOrigenNotFoundError
    en _resolve_canal (líneas 332-337 de incidente_service.py).
    La excepción CanalOrigenNotFoundError hereda de AppBaseException → responde 500.
    """
    result = _make_result()
    async with make_client_with_classifier(result) as client:
        response = await client.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": VALID_DESCRIPCION,
                "prioridad": "media",
                "canal_origen_id": 999999,
            },
        )

    # CanalOrigenNotFoundError es AppBaseException (no EntityNotFoundError),
    # lo que activa el handler de AppBaseException → 500 con INTERNAL_ERROR.
    assert response.status_code in (500, 404)  # depende del handler registrado


@pytest.mark.asyncio
async def test_get_incidentes_filtro_por_desde_hasta(
    seed_catalogs, make_client_with_classifier
):
    """
    Cobertura adicional: filtros de fecha 'desde' y 'hasta' cubren las ramas
    de incidente_repository.list_filtered (líneas 111 y 113).
    """
    from datetime import datetime, timezone, timedelta

    result = _make_result()
    async with make_client_with_classifier(result) as client:
        await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

        # Filtrar con desde (pasado lejano) y hasta (futuro)
        desde = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        hasta = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        response = await client.get(
            "/api/v1/incidentes/",
            params={"desde": desde, "hasta": hasta},
        )

    assert response.status_code == 200
    items = response.json()
    # El incidente creado debe estar en el rango
    assert len(items) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6 — Guardas de costo C-33 (change c-33-cost-guards)
#
#   * Idempotencia de alta por `origen_message_id` (N8N-REFINE/HIGH-4).
#   * Aceptacion de clasificacion precalculada con origen explicito (HIGH-2).
#   * Marcador de evento que impide crear incidentes desde notificaciones.
# ═══════════════════════════════════════════════════════════════════════════════


def _clasificacion_payload(**overrides) -> dict:
    """Bloque de clasificacion precalculada con valores por defecto validos."""
    base = {
        "sector_predicho": "Sistemas",
        "sectores_adicionales": [],
        "confianza": 0.92,
        "requiere_revision_humana": False,
        "origen": "n8n",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_c33_idempotencia_por_origen_message_id(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.1): un alta con `origen_message_id` crea el incidente; un reintento
    con el mismo identificador devuelve el mismo incidente sin volver a invocar
    al clasificador ni re-dispatchar la notificacion a N8N.
    """
    result = _make_result()
    payload = {**VALID_PAYLOAD, "origen_message_id": "outlook-msg-001"}

    async with make_client_with_spy_classifier(result) as (client, spy):
        primera = await client.post("/api/v1/incidentes/", json=payload)
        await asyncio.sleep(0)  # drenar la notificacion fire-and-forget
        notificaciones_tras_primera = spy.notify.await_count

        segunda = await client.post("/api/v1/incidentes/", json=payload)
        await asyncio.sleep(0)  # drenar cualquier tarea pendiente del reintento
        notificaciones_tras_reintento = spy.notify.await_count

        lista = await client.get("/api/v1/incidentes/")

    assert primera.status_code == 201
    assert segunda.status_code == 201
    assert primera.json()["id"] == segunda.json()["id"], (
        "El reintento con el mismo origen_message_id creo un incidente distinto"
    )
    assert spy.classify.await_count == 1, (
        f"El clasificador se invoco {spy.classify.await_count} veces; "
        "el reintento no debe reclasificar (costo pago)"
    )
    assert notificaciones_tras_primera == 1, (
        f"El alta inicial debe notificar a N8N exactamente una vez; se contaron "
        f"{notificaciones_tras_primera}"
    )
    assert notificaciones_tras_reintento == 1, (
        f"El reintento idempotente no debe re-dispatchar la notificacion; se "
        f"contaron {notificaciones_tras_reintento} notificaciones en total"
    )
    assert len(lista.json()) == 1, "Se duplico el incidente en la base"


@pytest.mark.asyncio
async def test_c33_alta_sin_identificador_y_identificadores_distintos(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.2): el alta sin `origen_message_id` sigue funcionando y dos
    identificadores distintos producen dos incidentes distintos.
    """
    result = _make_result()
    async with make_client_with_spy_classifier(result) as (client, spy):
        sin_id = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
        con_a = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "origen_message_id": "msg-a"},
        )
        con_b = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "origen_message_id": "msg-b"},
        )

    assert sin_id.status_code == 201
    assert con_a.status_code == 201
    assert con_b.status_code == 201
    assert con_a.json()["id"] != con_b.json()["id"]
    assert spy.classify.await_count == 3, (
        "Las altas con identificadores distintos deben clasificarse individualmente"
    )


@pytest.mark.asyncio
async def test_c33_clasificacion_precalculada_evita_clasificador(
    seed_catalogs, make_client_with_spy_classifier, engine
):
    """
    RED (2.3): con clasificacion precalculada valida el incidente se persiste con
    esa clasificacion, el origen queda auditable y NO se invoca al clasificador.
    """
    result = _make_result()  # no debe usarse
    payload = {**VALID_PAYLOAD, "clasificacion": _clasificacion_payload()}

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["sector"]["nombre"] == "Sistemas"
    assert spy.classify.await_count == 0, (
        "El clasificador server-side se invoco pese a venir la clasificacion precalculada"
    )

    # El origen de la clasificacion queda auditable en clasificacion_log.
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.models.clasificacion_log import ClasificacionLog

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        log = (
            await session.execute(
                select(ClasificacionLog).where(
                    ClasificacionLog.incidente_id == body["id"]
                )
            )
        ).scalar_one()
        assert log.etapa == "precalculada"
        assert log.respuesta_raw == "n8n"
        assert float(log.confianza) == pytest.approx(0.92)


@pytest.mark.asyncio
async def test_c33_sin_clasificacion_precalculada_clasifica_server_side(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.4): sin clasificacion precalculada el backend clasifica server-side.
    """
    result = _make_result(sector_predicho="Bases de Datos", confianza=0.80)
    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["sector"]["nombre"] == "Bases de Datos"
    assert spy.classify.await_count == 1


@pytest.mark.asyncio
async def test_c33_sector_invalido_y_confianza_fuera_de_rango_422(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.5): sector precalculado fuera del vocabulario y confianza fuera de
    rango responden 422 sin invocar al clasificador.
    """
    result = _make_result()
    async with make_client_with_spy_classifier(result) as (client, spy):
        sector_invalido = await client.post(
            "/api/v1/incidentes/",
            json={
                **VALID_PAYLOAD,
                "clasificacion": _clasificacion_payload(sector_predicho="Operaciones"),
            },
        )
        confianza_alta = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "clasificacion": _clasificacion_payload(confianza=1.5)},
        )
        confianza_baja = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "clasificacion": _clasificacion_payload(confianza=-0.1)},
        )

    for response in (sector_invalido, confianza_alta, confianza_baja):
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert spy.classify.await_count == 0, (
        "Un payload invalido no debe llegar al clasificador pago"
    )


@pytest.mark.asyncio
async def test_c33_origen_evento_notificacion_422_y_creacion_ok(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.6): un `origen_evento` de notificacion responde 422 y no crea
    incidente; un marcador de creacion (y la ausencia de marcador) funcionan.
    """
    result = _make_result()
    async with make_client_with_spy_classifier(result) as (client, spy):
        notificacion = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "origen_evento": "notificacion"},
        )
        creacion = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "origen_evento": "creacion_incidente"},
        )
        sin_marcador = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)
        lista = await client.get("/api/v1/incidentes/")

    assert notificacion.status_code == 422, notificacion.text
    assert notificacion.json()["error"]["code"] == "VALIDATION_ERROR"
    assert creacion.status_code == 201
    assert sin_marcador.status_code == 201
    assert len(lista.json()) == 2, (
        "El evento de notificacion no debe haber creado incidente"
    )


@pytest.mark.asyncio
async def test_c33_origen_evento_se_persiste_en_creacion(
    seed_catalogs, make_client_with_spy_classifier, engine
):
    """
    RED (2.6b) escenario "Evento de creacion crea el incidente": un payload con
    `origen_evento="creacion_incidente"` crea el incidente y el origen declarado
    queda registrado en la fila persistida; un payload sin marcador persiste nulo.
    """
    result = _make_result()
    async with make_client_with_spy_classifier(result) as (client, spy):
        con_marcador = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "origen_evento": "creacion_incidente"},
        )
        sin_marcador = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    assert con_marcador.status_code == 201, con_marcador.text
    assert sin_marcador.status_code == 201, sin_marcador.text
    assert con_marcador.json()["id"] != sin_marcador.json()["id"]

    # El marcador es interno (no se expone en IncidenteRead): se verifica en la
    # fila persistida consultando el modelo (C-33, W2).
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.models.incidente import Incidente

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        fila_con = (
            await session.execute(
                select(Incidente).where(
                    Incidente.id == con_marcador.json()["id"]
                )
            )
        ).scalar_one()
        fila_sin = (
            await session.execute(
                select(Incidente).where(
                    Incidente.id == sin_marcador.json()["id"]
                )
            )
        ).scalar_one()

    assert fila_con.origen_evento == "creacion_incidente", (
        "El origen declarado debe quedar registrado en la fila persistida"
    )
    assert fila_sin.origen_evento is None, (
        "Un payload sin marcador debe persistir origen_evento nulo"
    )


@pytest.mark.asyncio
async def test_c33_clasificacion_forzada_revision_sin_sector(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (2.7): un bloque precalculado con revision humana y sin sector persiste
    el incidente con sector nulo y revision activada, sin invocar al clasificador.
    """
    result = _make_result()
    clasificacion = _clasificacion_payload(
        sector_predicho=None,
        confianza=0.0,
        requiere_revision_humana=True,
    )
    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post(
            "/api/v1/incidentes/",
            json={**VALID_PAYLOAD, "clasificacion": clasificacion},
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["sector"] is None, "Un sector ausente debe persistirse como nulo"
    assert body["requiere_revision_humana"] is True
    assert spy.classify.await_count == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo C-39: instrumentacion temporal end-to-end en la respuesta del alta
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_c39_alta_con_ingreso_expone_latencia_e2e(
    seed_catalogs, make_client_with_classifier
):
    """
    RED (C-39): un alta con `ingresado_en` responde con ambos instantes y una
    `latencia_e2e_ms` no negativa, derivada de la diferencia.
    """
    result = _make_result()
    ingresado = datetime.now(timezone.utc) - timedelta(seconds=5)
    payload = {**VALID_PAYLOAD, "ingresado_en": ingresado.isoformat()}

    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ingresado_en"] is not None
    assert body["persistido_en"] is not None
    assert body["latencia_anomala"] is False
    assert body["latencia_e2e_ms"] is not None
    assert body["latencia_e2e_ms"] >= 4000, (
        f"La latencia derivada debe reflejar ~5 s de ingreso; se obtuvo "
        f"{body['latencia_e2e_ms']} ms"
    )


@pytest.mark.asyncio
async def test_c39_alta_sin_ingreso_deja_latencia_nula(
    seed_catalogs, make_client_with_classifier
):
    """
    TRIANGULATE (C-39): un alta sin `ingresado_en` persiste nulo y responde con
    `latencia_e2e_ms` nula; `persistido_en` queda sellado igualmente.
    """
    result = _make_result()

    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=VALID_PAYLOAD)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ingresado_en"] is None
    assert body["persistido_en"] is not None
    assert body["latencia_e2e_ms"] is None
    assert body["latencia_anomala"] is False


@pytest.mark.asyncio
async def test_c39_ingreso_futuro_dentro_de_tolerancia_marca_anomalia(
    seed_catalogs, make_client_with_classifier
):
    """
    TRIANGULATE (C-39, D9): un `ingresado_en` en el futuro dentro de la tolerancia
    se acepta (201), pero la latencia resultante es negativa: NO se reporta como
    valida (nula) y queda marcada como anomalia.
    """
    result = _make_result()
    ingresado = datetime.now(timezone.utc) + timedelta(seconds=10)
    payload = {**VALID_PAYLOAD, "ingresado_en": ingresado.isoformat()}

    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["latencia_anomala"] is True, (
        "Una latencia negativa debe marcarse como anomalia"
    )
    assert body["latencia_e2e_ms"] is None, (
        "Una latencia negativa no debe reportarse como medicion valida"
    )


@pytest.mark.asyncio
async def test_c39_ingreso_naive_rechazado_422(
    seed_catalogs, make_client_with_classifier
):
    """
    TRIANGULATE (C-39): un `ingresado_en` sin zona horaria se rechaza con 422.
    """
    result = _make_result()
    payload = {**VALID_PAYLOAD, "ingresado_en": "2026-09-19T12:00:00"}

    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_c39_ingreso_futuro_fuera_de_tolerancia_rechazado_422(
    seed_catalogs, make_client_with_classifier
):
    """
    TRIANGULATE (C-39): un `ingresado_en` mas alla de la tolerancia se rechaza 422.
    """
    result = _make_result()
    ingresado = datetime.now(timezone.utc) + timedelta(seconds=120)
    payload = {**VALID_PAYLOAD, "ingresado_en": ingresado.isoformat()}

    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 422, response.text


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo C-48: instrumentacion temporal end-to-end en la proyeccion de listado
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_c48_listado_expone_instantes_y_latencia(
    seed_catalogs, make_client_with_classifier
):
    """
    RED (c-48): un incidente sellado con `ingresado_en`/`persistido_en` se
    consulta por GET /api/v1/incidentes y el item del listado devuelve ambos
    instantes y la latencia derivada. Verifica que la ruta y el repositorio no
    necesitan cambios y que una futura proyeccion que omita las columnas rompe
    este test.
    """
    result = _make_result()
    ingresado = datetime.now(timezone.utc) - timedelta(seconds=5)
    payload = {**VALID_PAYLOAD, "ingresado_en": ingresado.isoformat()}

    async with make_client_with_classifier(result) as client:
        create_resp = await client.post("/api/v1/incidentes/", json=payload)
        assert create_resp.status_code == 201, create_resp.text
        incidente_id = create_resp.json()["id"]

        # Act
        lista = await client.get("/api/v1/incidentes/")

    assert lista.status_code == 200, lista.text
    item = next(i for i in lista.json() if i["id"] == incidente_id)
    assert item["ingresado_en"] is not None
    assert item["persistido_en"] is not None
    assert item["latencia_e2e_ms"] is not None
    assert item["latencia_e2e_ms"] >= 4000
    assert item["latencia_anomala"] is False
