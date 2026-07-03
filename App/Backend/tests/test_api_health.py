"""
Tests de integración para los endpoints de salud del sistema.

Cubre:
    GET /api/v1/health    → Liveness probe: proceso activo, sin tocar la BD.
    GET /api/v1/health/db → Readiness probe: base de datos alcanzable.

No requiere seed_catalogs ni clasificador doble: los endpoints de salud
no dependen de datos de negocio.
"""

import pytest
import pytest_asyncio

from app.config.settings import get_settings


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 8: GET /api/v1/health
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_health_liveness_200(client):
    """
    8.1 / 8.2 RED + GREEN
    GET /api/v1/health → 200 con status "ok" y la versión de la app.
    """
    # Act
    response = await client.get("/api/v1/health")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    # La versión debe coincidir con la configurada en Settings
    settings = get_settings()
    assert body["version"] == settings.app_version


@pytest.mark.asyncio
async def test_get_health_db_readiness_200(client):
    """
    8.3 TRIANGULATE
    GET /api/v1/health/db con la base de test disponible →
    200 indicando base alcanzable.
    """
    # Act
    response = await client.get("/api/v1/health/db")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "reachable"
