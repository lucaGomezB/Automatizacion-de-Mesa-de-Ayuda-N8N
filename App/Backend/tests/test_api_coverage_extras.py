"""
Tests de cobertura complementarios para ramas no alcanzables vía HTTP puro.

Propósito:
    Cubrir los métodos del BaseRepository (get_or_none, list_all, delete)
    que no tienen un endpoint HTTP directo pero son parte del contrato
    público de la capa de repositorios.

    También cubre ramas de lógica de servicio no ejercitadas por los
    tests de API principal.

Decisión (documentada en design.md):
    Se opta por tests de repositorio directo (no HTTP) para las ramas
    de BaseRepository que no tienen route asociado. Estos tests son
    menos costosos que crear endpoints adicionales solo para coverage.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from unittest.mock import AsyncMock, patch

from app.core.exceptions import EntityNotFoundError
from app.models.catalog import Sector, Estado, CanalOrigen
from app.repositories.base import BaseRepository
from app.repositories.sector_repository import SectorRepository
from app.schemas.clasificacion import ClasificacionResult


# ═══════════════════════════════════════════════════════════════════════════════
# Tests directos de BaseRepository — métodos no expuestos por HTTP
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_base_repository_get_or_none_existente(engine, seed_catalogs):
    """
    get_or_none devuelve la instancia cuando el ID existe.
    Cubre base.py línea 95 (get_or_none).
    """
    sector_id = seed_catalogs["sector_sistemas"].id
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repo = SectorRepository(session)
        # Act
        result = await repo.get_or_none(sector_id)
    assert result is not None
    assert result.id == sector_id


@pytest.mark.asyncio
async def test_base_repository_get_or_none_inexistente(engine, seed_catalogs):
    """
    get_or_none devuelve None cuando el ID no existe (no lanza excepción).
    Cubre la rama de retorno None en base.py línea 95.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repo = SectorRepository(session)
        result = await repo.get_or_none(999999)
    assert result is None


@pytest.mark.asyncio
async def test_base_repository_list_all(engine, seed_catalogs):
    """
    list_all devuelve todos los registros de la tabla.
    Cubre base.py líneas 112-115.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repo = SectorRepository(session)
        result = await repo.list_all()
    # Debe incluir los tres sectores sembrados por seed_catalogs
    assert len(result) >= 3


@pytest.mark.asyncio
async def test_base_repository_get_by_id_not_found_raises(engine, seed_catalogs):
    """
    get_by_id lanza EntityNotFoundError cuando el ID no existe.
    Cubre base.py línea 79.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        repo = SectorRepository(session)
        with pytest.raises(EntityNotFoundError):
            await repo.get_by_id(999999)


@pytest.mark.asyncio
async def test_base_repository_delete(engine, seed_catalogs):
    """
    delete elimina un registro existente sin errores.
    Cubre base.py líneas 149-151.
    Nota: usamos un sector nuevo para no afectar los datos de seed_catalogs.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        # Crear un sector temporal
        nuevo_sector = Sector(nombre="SectorTemporal", descripcion="Para test de delete")
        session.add(nuevo_sector)
        await session.commit()
        nuevo_id = nuevo_sector.id

    async with factory() as session:
        repo = SectorRepository(session)
        # Act: eliminar el sector temporal
        await repo.delete(nuevo_id)
        await session.commit()

    # Verify: el sector ya no existe
    async with factory() as session:
        repo = SectorRepository(session)
        result = await repo.get_or_none(nuevo_id)
    assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# Tests de cobertura — ramas de servicio
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_incidente_clasificacion_sector_desconocido(
    seed_catalogs, make_client_with_classifier
):
    """
    Cuando el clasificador devuelve una categoría que no existe en la BD,
    sector_id queda como None (no lanza excepción, cubre línea 308 de incidente_service).
    """
    # Arrange: clasificador que predice una categoría no existente en catálogos
    result = ClasificacionResult(
        categoria="CategoríaInexistente",
        confianza=0.85,
        etapa="gemini",
        requiere_revision_humana=False,
        respuesta_raw=None,
    )

    async with make_client_with_classifier(result) as client:
        response = await client.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": "Falla en el sistema de correo del área contable.",
                "prioridad": "media",
            },
        )

    # El incidente se crea pero sin sector asignado (sector=None)
    assert response.status_code == 201
    body = response.json()
    assert body["sector"] is None
