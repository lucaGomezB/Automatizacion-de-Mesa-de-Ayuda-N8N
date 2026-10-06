"""
Tests de la guardia de entorno acotada al seed del directorio (c-60, 6.1/6.3 / DIR-008).

El seed dev-only MUST rechazar la ejecucion (sin tocar la base) cuando el entorno
no es de desarrollo/prueba (`development`/`local`/`test`), y MUST proceder en los
entornos permitidos. La guardia vive UNICAMENTE en el seed: el runtime normal
(servicio/rutas) NO consulta el entorno para autorizar ni alterar su comportamiento.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.config.settings import get_settings
from app.models.catalog import Sector
from app.models.empleado import Empleado
from app.models.user import User
from app.services.directorio_service import DirectorioService
from scripts.seed_directorio import (
    ENTORNOS_PERMITIDOS_SEED,
    PERSONAS_SINTETICAS,
    SeedEnvironmentError,
    seed_directorio,
    verificar_entorno_seed,
)

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


async def _seed_sector(session) -> Sector:
    sector = Sector(nombre="Sistemas", descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


async def _contar(session, modelo) -> int:
    return (await session.execute(select(func.count()).select_from(modelo))).scalar_one()


def test_conjunto_de_entornos_permitidos():
    """El conjunto permitido es exactamente development/local/test (OQ4)."""
    assert ENTORNOS_PERMITIDOS_SEED == {"development", "local", "test"}


def test_verificar_entorno_rechaza_production_y_acepta_dev():
    """La verificacion pura rechaza produccion y acepta un entorno dev."""
    with pytest.raises(SeedEnvironmentError):
        verificar_entorno_seed("production")
    assert verificar_entorno_seed("development") == "development"


@pytest.mark.asyncio
async def test_seed_rechaza_production_sin_tocar_la_base(db_session):
    """Con environment=production el seed aborta y no escribe filas."""
    await _seed_sector(db_session)

    with pytest.raises(SeedEnvironmentError):
        await seed_directorio(db_session, environment="production")

    assert await _contar(db_session, Empleado) == 0
    assert await _contar(db_session, User) == 0


@pytest.mark.parametrize("entorno", ["development", "local", "test"])
@pytest.mark.asyncio
async def test_seed_procede_en_entornos_permitidos(db_session, entorno):
    """En development/local/test el seed crea un sintetico por rol."""
    await _seed_sector(db_session)

    resultado = await seed_directorio(db_session, environment=entorno)

    assert resultado["creados"] == len(PERSONAS_SINTETICAS)
    assert await _contar(db_session, Empleado) == len(PERSONAS_SINTETICAS)


@pytest.mark.asyncio
async def test_runtime_no_se_gatea_con_environment_production(db_session, monkeypatch):
    """Con environment=production la operacion normal del directorio sigue igual."""
    monkeypatch.setattr(get_settings(), "environment", "production")

    sector = await _seed_sector(db_session)
    svc = DirectorioService(db_session)
    empleado = await svc.crear_empleado(
        legajo="RT-1", nombre="Runtime Sintetico", email="runtime@example.test",
        sector_id=sector.id, rol="usuario_final",
    )

    assert empleado.activo is True
    assert (await svc.obtener(empleado.id)).email == "runtime@example.test"


def test_rutas_y_servicio_no_consultan_el_entorno():
    """La guardia no debe filtrarse al runtime: ni rutas ni servicio la consultan."""
    for relativo in ("app/routes/directorio.py", "app/services/directorio_service.py"):
        fuente = (_BACKEND_ROOT / relativo).read_text(encoding="utf-8")
        assert "environment" not in fuente
        assert "get_settings" not in fuente
