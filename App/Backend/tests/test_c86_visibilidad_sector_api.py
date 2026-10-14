"""Tests de API del alcance SECTOR (c-86, VIS-001/VIS-007).

Cubren, en la capa HTTP y con la derivacion REAL de alcance (sin override de
`get_alcance_incidentes`):
    - `gestion_incidentes` ve solo los incidentes de su sector (principal o
      adicional) que no estan cerrados para su sector.
    - El acceso puntual a un incidente de otro sector responde 404.
    - Un `gestion_incidentes` sin sector tiene alcance VACIO.
    - Los endpoints de clasificaciones por incidente reutilizan la misma regla.
"""

from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User


@pytest_asyncio.fixture
async def sector_api_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([a, b, estado])
        await s.flush()

        ua = User(username="gest-a", hashed_password="x", is_active=True)
        ub = User(username="gest-b", hashed_password="x", is_active=True)
        un = User(username="gest-n", hashed_password="x", is_active=True)
        s.add_all([ua, ub, un])
        await s.flush()

        ga = Empleado(
            legajo="GA", nombre="Gestion A", email="ga@example.test",
            sector_id=a.id, rol=RolEmpleado.gestion_incidentes, user_id=ua.id,
        )
        gb = Empleado(
            legajo="GB", nombre="Gestion B", email="gb@example.test",
            sector_id=b.id, rol=RolEmpleado.gestion_incidentes, user_id=ub.id,
        )
        gn = Empleado(
            legajo="GN", nombre="Gestion sin sector", email="gn@example.test",
            sector_id=None, rol=RolEmpleado.gestion_incidentes, user_id=un.id,
        )
        s.add_all([ga, gb, gn])
        await s.flush()

        base = dict(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
        )
        ia = Incidente(**base, sector_id=a.id, origen_message_id="sec-A")
        ib = Incidente(**base, sector_id=b.id, origen_message_id="sec-B")
        iab = Incidente(
            **base, sector_id=b.id, sectores_adicionales=[a],
            origen_message_id="sec-AB",
        )
        s.add_all([ia, ib, iab])
        await s.commit()

        ids = {
            "ua": ua.id, "ub": ub.id, "un": un.id,
            "sector_a": a.id, "sector_b": b.id,
        }
        filas = (await s.execute(select(Incidente))).scalars().all()
        por = {f.origen_message_id: f.id for f in filas}
        ids["ia"] = por["sec-A"]
        ids["ib"] = por["sec-B"]
        ids["iab"] = por["sec-AB"]

    yield ids

    async with factory() as s:
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@asynccontextmanager
async def _client(engine, user_id: int):
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

    async def override_auth():
        return User(id=user_id, username=f"u{user_id}", hashed_password="", is_active=True)

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_gestion_ve_solo_su_sector(engine, sector_api_env):
    """`gestion_incidentes` del sector A ve los incidentes con A, no otros."""
    async with _client(engine, sector_api_env["ua"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert ids == {sector_api_env["ia"], sector_api_env["iab"]}


@pytest.mark.asyncio
async def test_gestion_no_ve_otro_sector_404(engine, sector_api_env):
    """El acceso puntual a un incidente de otro sector responde 404."""
    async with _client(engine, sector_api_env["ua"]) as c:
        propio = await c.get(f"/api/v1/incidentes/{sector_api_env['ia']}")
        ajeno = await c.get(f"/api/v1/incidentes/{sector_api_env['ib']}")
    assert propio.status_code == 200
    assert ajeno.status_code == 404
    assert ajeno.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_gestion_sin_sector_alcance_vacio(engine, sector_api_env):
    """Un `gestion_incidentes` sin sector no ve ningun incidente."""
    async with _client(engine, sector_api_env["un"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_clasificaciones_por_incidente_respeta_sector(engine, sector_api_env):
    """El historial de clasificaciones reutiliza el alcance SECTOR (404 fuera)."""
    async with _client(engine, sector_api_env["ua"]) as c:
        propio = await c.get(
            f"/api/v1/clasificaciones/incidente/{sector_api_env['ia']}"
        )
        ajeno = await c.get(
            f"/api/v1/clasificaciones/incidente/{sector_api_env['ib']}"
        )
    assert propio.status_code == 200
    assert ajeno.status_code == 404
