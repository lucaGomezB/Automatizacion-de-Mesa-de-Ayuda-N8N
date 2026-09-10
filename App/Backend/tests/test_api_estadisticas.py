"""
Tests de integracion para los endpoints HTTP de estadisticas y analitica.

Cubre:
    GET /api/v1/estadisticas/tendencias → Serie temporal agrupada por dia/mes.
    GET /api/v1/estadisticas/resumen    → KPIs agregados con distribuciones.
    PATCH bloqueo 409 en cerrados.

Estrategia TDD (C-06):
    RED → GREEN → TRIANGULATE → REFACTOR.

Aislamiento:
    - Clasificador: doble via make_client_with_classifier.
    - notify_n8n: AsyncMock dentro del factory.
"""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.schemas.clasificacion import ClasificacionResult


# ── Helpers ────────────────────────────────────────────────────────────────────

VALID_DESCRIPCION = "Falla en el servidor de base de datos principal del sector contable."


def _make_result(
    categoria: str = "Sistemas",
    confianza: float = 0.95,
    requiere_revision_humana: bool = False,
) -> ClasificacionResult:
    """Construye un ClasificacionResult para el clasificador doble."""
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=requiere_revision_humana,
        respuesta_raw=None,
    )


async def _create_incidentes(
    client: AsyncClient,
    count: int = 5,
    descripcion: str = VALID_DESCRIPCION,
    prioridad: str = "media",
    canal_origen_id: int | None = None,
) -> list[dict]:
    """Helper: crea N incidentes y retorna la lista de respuestas."""
    results = []
    for _ in range(count):
        payload: dict = {
            "descripcion": descripcion,
            "prioridad": prioridad,
        }
        if canal_origen_id is not None:
            payload["canal_origen_id"] = canal_origen_id
        response = await client.post("/api/v1/incidentes/", json=payload)
        assert response.status_code == 201
        results.append(response.json())
    return results


def _today() -> date:
    return date.today()


def _days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5: GET /api/v1/estadisticas/tendencias
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_tendencias_daily_7_days(
    seed_catalogs, make_client_with_classifier
):
    """
    5.2: Agrupar por dia en rango de 7 dias → 7 entradas en series.
    """
    result = _make_result(categoria="Sistemas", confianza=0.95)

    async with make_client_with_classifier(result) as client:
        await _create_incidentes(client, count=3)
        await _create_incidentes(client, count=2)

        desde = _days_ago(6)
        hasta = _today()

        response = await client.get(
            "/api/v1/estadisticas/tendencias",
            params={
                "agrupar_por": "dia",
                "desde": desde.isoformat(),
                "hasta": hasta.isoformat(),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["periodo"]["agrupar_por"] == "dia"
    assert len(body["series"]) == 7
    for entry in body["series"]:
        assert "total" in entry
        assert "por_sector" in entry
        assert isinstance(entry["total"], int)
        assert isinstance(entry["por_sector"], dict)


@pytest.mark.asyncio
async def test_tendencias_monthly_with_sector_filter(
    seed_catalogs, make_client_with_classifier
):
    """
    5.3: Agrupar por mes con filtro de sector.
    """
    result_sistemas = _make_result(categoria="Sistemas", confianza=0.95)

    async with make_client_with_classifier(result_sistemas) as client:
        await _create_incidentes(client, count=4)

        response = await client.get(
            "/api/v1/estadisticas/tendencias",
            params={
                "agrupar_por": "mes",
                "desde": "2026-01-01",
                "hasta": "2026-12-31",
                "sector_id": seed_catalogs["sector_sistemas"].id,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["periodo"]["agrupar_por"] == "mes"
    for entry in body["series"]:
        if entry["total"] > 0:
            assert "Sistemas" in entry["por_sector"]


@pytest.mark.asyncio
async def test_tendencias_missing_desde_hasta_422(
    seed_catalogs, make_client_with_classifier
):
    """
    5.4: Sin desde/hasta → 422.
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.get(
            "/api/v1/estadisticas/tendencias",
            params={"agrupar_por": "mes"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tendencias_invalid_agrupar_por_422(
    seed_catalogs, make_client_with_classifier
):
    """
    5.5: agrupar_por invalido → 422.
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.get(
            "/api/v1/estadisticas/tendencias",
            params={
                "agrupar_por": "semana",
                "desde": "2026-01-01",
                "hasta": "2026-01-31",
            },
        )

    assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5: GET /api/v1/estadisticas/resumen
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_resumen_default_30_days(
    seed_catalogs, make_client_with_classifier
):
    """
    5.6: Sin parametros → resumen para ultimos 30 dias.
    """
    result = _make_result(categoria="Sistemas", confianza=0.95)

    async with make_client_with_classifier(result) as client:
        await _create_incidentes(client, count=5)

        response = await client.get("/api/v1/estadisticas/resumen")

    assert response.status_code == 200
    body = response.json()
    assert "total_incidentes" in body
    assert "promedio_diario" in body
    assert "distribucion_sectores" in body
    assert "distribucion_estados" in body
    assert "tasa_revision_humana" in body
    assert body["total_incidentes"] == 5
    assert isinstance(body["promedio_diario"], (int, float))
    assert isinstance(body["tasa_revision_humana"], (int, float))


@pytest.mark.asyncio
async def test_resumen_explicit_date_range(
    seed_catalogs, make_client_with_classifier
):
    """
    5.7: Rango explicito ano completo → resumen.
    """
    result = _make_result(categoria="Operaciones", confianza=0.90)

    async with make_client_with_classifier(result) as client:
        await _create_incidentes(client, count=3)

        response = await client.get(
            "/api/v1/estadisticas/resumen",
            params={"desde": "2026-01-01", "hasta": "2026-12-31"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_incidentes"] == 3


@pytest.mark.asyncio
async def test_resumen_empty_range_returns_zeros(
    seed_catalogs, make_client_with_classifier
):
    """
    5.8: Rango sin incidentes → totales 0, sin error.
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.get(
            "/api/v1/estadisticas/resumen",
            params={"desde": "2026-07-01", "hasta": "2026-07-01"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_incidentes"] == 0
    assert body["promedio_diario"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5: Authentication required
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_tendencias_unauthenticated_401():
    """
    5.9: Sin token → 401 en tendencias.
    """
    from httpx import ASGITransport
    from app.main import create_app

    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/estadisticas/tendencias",
            params={
                "agrupar_por": "dia",
                "desde": "2026-01-01",
                "hasta": "2026-01-31",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resumen_unauthenticated_401():
    """
    5.9: Sin token → 401 en resumen.
    """
    from httpx import ASGITransport
    from app.main import create_app

    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/estadisticas/resumen")

    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6: Bloqueo de escritura en incidentes cerrados (409)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_patch_incidente_cerrado_409(
    seed_catalogs, make_client_with_classifier, engine
):
    """
    6.1: PATCH sobre un incidente cerrado → 409 INCIDENTE_CERRADO.

    Crea un incidente, lo mueve manualmente a estado "cerrado" via la
    base de datos (porque el PATCH regular no permite cambiar a cerrado),
    y luego verifica que un PATCH posterior retorna 409.
    """
    from sqlalchemy import update
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from app.models.incidente import Incidente

    result = _make_result(categoria="Sistemas", confianza=0.95)

    async with make_client_with_classifier(result) as client:
        # Crear incidente fresco (estado "nuevo")
        r = await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": VALID_DESCRIPCION, "prioridad": "media"},
        )
        assert r.status_code == 201
        incidente_id = r.json()["id"]

        # Mover el incidente a estado "cerrado" directamente en la BD
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            cerrado_id = seed_catalogs["estado_cerrado"].id
            await session.execute(
                update(Incidente)
                .where(Incidente.id == incidente_id)
                .values(estado_id=cerrado_id)
            )
            await session.commit()

        # Act: intentar PATCH sobre el incidente cerrado
        response = await client.patch(
            f"/api/v1/incidentes/{incidente_id}",
            json={"prioridad": "alta"},
        )

    # Assert
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "INCIDENTE_CERRADO"
    assert "solo lectura" in body["error"]["message"].lower()


@pytest.mark.asyncio
async def test_patch_non_terminal_incidente_200(
    seed_catalogs, make_client_with_classifier
):
    """
    6.2: PATCH sobre incidente no terminal (nuevo) → 200 OK.
    """
    result = _make_result(categoria="Sistemas", confianza=0.95)

    async with make_client_with_classifier(result) as client:
        r = await client.post(
            "/api/v1/incidentes/",
            json={"descripcion": VALID_DESCRIPCION, "prioridad": "media"},
        )
        assert r.status_code == 201
        incidente_id = r.json()["id"]

        # Act: actualizar prioridad sobre incidente no terminal
        response = await client.patch(
            f"/api/v1/incidentes/{incidente_id}",
            json={"prioridad": "alta"},
        )

    assert response.status_code == 200
    assert response.json()["prioridad"] == "alta"


@pytest.mark.asyncio
async def test_patch_nonexistent_incidente_404(
    seed_catalogs, make_client_with_classifier
):
    """
    6.3: PATCH sobre incidente inexistente → 404 (precede al chequeo de estado).
    """
    async with make_client_with_classifier(_make_result()) as client:
        response = await client.patch(
            "/api/v1/incidentes/99999",
            json={"prioridad": "alta"},
        )

    assert response.status_code == 404
