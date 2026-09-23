"""
Tests de visibilidad de incidentes por rol (c-54, seccion 6.4).

VIS-001:
    - `administrador_directorio` ve incidentes de todos los sectores.
    - `usuario_final`/`operador` con sector S ven solo los de S.
    - Una cuenta sin empleado vinculado tiene alcance vacio.
    - El acceso puntual a un incidente fuera de sector responde 404.

El filtrado se aplica en la capa de API/servicio; el frontend se difiere.
"""

from contextlib import asynccontextmanager

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
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User


@pytest_asyncio.fixture
async def vis_env(engine):
    """Siembra sectores, estado, cuentas/empleados por rol y dos incidentes."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector_a = Sector(nombre="Sistemas", descripcion="A")
        sector_b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector_a, sector_b, estado])
        await s.flush()

        admin_user = User(username="vis-admin", hashed_password="x", is_active=True)
        oper_a_user = User(username="vis-oper-a", hashed_password="x", is_active=True)
        s.add_all([admin_user, oper_a_user])
        await s.flush()

        s.add_all(
            [
                Empleado(
                    legajo="V-ADM", nombre="Admin", email="v.admin@example.test",
                    rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
                ),
                Empleado(
                    legajo="V-OPE-A", nombre="Oper A", email="v.oper.a@example.test",
                    sector_id=sector_a.id, rol=RolEmpleado.operador,
                    user_id=oper_a_user.id,
                ),
                Incidente(
                    descripcion_original="incidente A",
                    descripcion_pseudonimizada="incidente A",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                ),
                Incidente(
                    descripcion_original="incidente B",
                    descripcion_pseudonimizada="incidente B",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_b.id,
                ),
            ]
        )
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "oper_a_user": oper_a_user.id,
            "sin_empleado_user": 888888,
        }

        # Identificar los incidentes por sector para las asserts.
        from sqlalchemy import select

        filas = (await s.execute(select(Incidente))).scalars().all()
        ids["incidente_a"] = next(
            f.id for f in filas if f.sector_id == sector_a.id
        )
        ids["incidente_b"] = next(
            f.id for f in filas if f.sector_id == sector_b.id
        )

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
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_admin_ve_todos_los_incidentes(engine, vis_env):
    """El administrador lista incidentes de todos los sectores."""
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    sectores = {i["sector"]["id"] for i in resp.json() if i["sector"]}
    assert len(sectores) >= 2


@pytest.mark.asyncio
async def test_no_admin_ve_solo_su_sector(engine, vis_env):
    """El operador del sector A solo ve los incidentes de A."""
    async with _client(engine, vis_env["oper_a_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert vis_env["incidente_a"] in ids
    assert vis_env["incidente_b"] not in ids


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_alcance_vacio(engine, vis_env):
    """Una cuenta sin empleado vinculado no ve incidentes."""
    async with _client(engine, vis_env["sin_empleado_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_acceso_puntual_fuera_de_sector_404(engine, vis_env):
    """Un no administrador no puede leer un incidente fuera de su sector."""
    async with _client(engine, vis_env["oper_a_user"]) as c:
        propio = await c.get(f"/api/v1/incidentes/{vis_env['incidente_a']}")
        ajeno = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert propio.status_code == 200
    assert ajeno.status_code == 404
    assert ajeno.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_admin_accede_puntual_a_cualquier_sector(engine, vis_env):
    """El administrador si puede leer el incidente ajeno."""
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert resp.status_code == 200
