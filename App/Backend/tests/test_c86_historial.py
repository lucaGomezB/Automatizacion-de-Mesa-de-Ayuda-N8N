"""Tests del historial de incidentes cerrados (c-86, VIS-008).

Cubren el filtrado por alcance del historial:
    - GLOBAL: incidentes en estado global `cerrado`.
    - SECTOR: incidentes con un cierre por sector para SU sector (incluidos los
      cerrados solo por su sector, aun no globalmente).
    - PROPIO: los propios incidentes cerrados.

Y el contrato de la ruta `GET /incidentes/historial-cerrados` (declarada antes
de `GET /{id}`), incluido el 401 anonimo.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import (
    Incidente,
    IncidenteCierreSector,
    PrioridadEnum,
)
from app.models.user import User
from app.services.incidente_service import IncidenteService
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance


@pytest_asyncio.fixture
async def historial_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        cerrado = Estado(nombre="cerrado", descripcion="c", es_terminal=True)
        s.add_all([a, b, estado, cerrado])
        await s.flush()

        u1 = User(username="h-e1", hashed_password="x", is_active=True)
        u2 = User(username="h-e2", hashed_password="x", is_active=True)
        s.add_all([u1, u2])
        await s.flush()

        e1 = Empleado(
            legajo="HE1", nombre="E1", email="he1@example.test",
            sector_id=a.id, rol=RolEmpleado.usuario_final, user_id=u1.id,
        )
        e2 = Empleado(
            legajo="HE2", nombre="E2", email="he2@example.test",
            sector_id=b.id, rol=RolEmpleado.usuario_final, user_id=u2.id,
        )
        s.add_all([e1, e2])
        await s.flush()

        base = dict(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
        )
        global_cerrado = Incidente(**base, estado_id=cerrado.id, sector_id=a.id)
        activo = Incidente(**base, estado_id=estado.id, sector_id=a.id)
        sector_a_cerrado = Incidente(**base, estado_id=estado.id, sector_id=a.id)
        propio_cerrado = Incidente(
            **base, estado_id=cerrado.id, sector_id=a.id, reportante_empleado_id=e1.id
        )
        otro_propio = Incidente(
            **base, estado_id=cerrado.id, sector_id=b.id, reportante_empleado_id=e2.id
        )
        s.add_all(
            [global_cerrado, activo, sector_a_cerrado, propio_cerrado, otro_propio]
        )
        await s.flush()

        s.add(
            IncidenteCierreSector(
                incidente_id=sector_a_cerrado.id,
                sector_id=a.id,
                cerrado_en=datetime.now(timezone.utc),
            )
        )
        await s.commit()

        ids = {
            "e1": e1.id, "e2": e2.id, "sector_a": a.id, "sector_b": b.id,
            "u1": u1.id, "u2": u2.id,
            "global_cerrado": global_cerrado.id,
            "activo": activo.id,
            "sector_a_cerrado": sector_a_cerrado.id,
            "propio_cerrado": propio_cerrado.id,
            "otro_propio": otro_propio.id,
        }
    yield ids

    async with factory() as s:
        await s.execute(delete(IncidenteCierreSector))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@pytest.mark.asyncio
async def test_historial_global_solo_cerrados(engine, historial_env):
    """GLOBAL ve los incidentes en estado global `cerrado`."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = IncidenteService(s)
        historial = await service.list_historial_cerrados(
            alcance=AlcanceIncidentes(ModoAlcance.GLOBAL), limit=100
        )
        ids = {i.id for i in historial}
        assert historial_env["global_cerrado"] in ids
        assert historial_env["propio_cerrado"] in ids
        assert historial_env["otro_propio"] in ids
        assert historial_env["activo"] not in ids
        assert historial_env["sector_a_cerrado"] not in ids
        await s.rollback()


@pytest.mark.asyncio
async def test_historial_sector_incluye_cierre_parcial(engine, historial_env):
    """SECTOR ve los incidentes con cierre de su sector (aun no globales)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = IncidenteService(s)
        alcance_a = AlcanceIncidentes(
            ModoAlcance.SECTOR, sector_id=historial_env["sector_a"]
        )
        ids = {
            i.id
            for i in await service.list_historial_cerrados(alcance=alcance_a, limit=100)
        }
        assert historial_env["sector_a_cerrado"] in ids
        assert historial_env["activo"] not in ids

        alcance_b = AlcanceIncidentes(
            ModoAlcance.SECTOR, sector_id=historial_env["sector_b"]
        )
        ids_b = {
            i.id
            for i in await service.list_historial_cerrados(alcance=alcance_b, limit=100)
        }
        assert historial_env["sector_a_cerrado"] not in ids_b
        await s.rollback()


@pytest.mark.asyncio
async def test_historial_propio_solo_los_propios(engine, historial_env):
    """PROPIO ve unicamente los incidentes cerrados que reporto."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = IncidenteService(s)
        alcance = AlcanceIncidentes(
            ModoAlcance.PROPIO, reportante_empleado_id=historial_env["e1"]
        )
        ids = {
            i.id
            for i in await service.list_historial_cerrados(alcance=alcance, limit=100)
        }
        assert ids == {historial_env["propio_cerrado"]}
        await s.rollback()


@pytest.mark.asyncio
async def test_historial_alcance_vacio(engine, historial_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = IncidenteService(s)
        assert await service.list_historial_cerrados(alcance=AlcanceIncidentes()) == []
        await s.rollback()


# ── API ───────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def _client(engine, user_id: int | None):
    app = create_app()

    async def override_db():
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db
    if user_id is not None:
        async def override_auth():
            return User(id=user_id, username=f"u{user_id}", hashed_password="", is_active=True)
        app.dependency_overrides[get_current_user] = override_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_api_historial_propio(engine, historial_env):
    """`usuario_final` ve su historial propio (y no el de otros)."""
    async with _client(engine, historial_env["u1"]) as c:
        resp = await c.get("/api/v1/incidentes/historial-cerrados")
    assert resp.status_code == 200, resp.text
    ids = {i["id"] for i in resp.json()}
    assert ids == {historial_env["propio_cerrado"]}


@pytest.mark.asyncio
async def test_api_historial_sector_no_cruza(engine, historial_env):
    """El historial de un sector no incluye el cierre de otro sector."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="hg-a", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = Empleado(
            legajo="HGA", nombre="GA", email="hga@example.test",
            sector_id=historial_env["sector_a"], rol=RolEmpleado.gestion_incidentes,
            user_id=user.id,
        )
        s.add(emp)
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        resp = await c.get("/api/v1/incidentes/historial-cerrados")
    assert resp.status_code == 200, resp.text
    ids = {i["id"] for i in resp.json()}
    assert historial_env["sector_a_cerrado"] in ids
    assert historial_env["activo"] not in ids


@pytest.mark.asyncio
async def test_api_historial_anonimo_401(engine, historial_env):
    async with _client(engine, None) as c:
        resp = await c.get("/api/v1/incidentes/historial-cerrados")
    assert resp.status_code == 401
