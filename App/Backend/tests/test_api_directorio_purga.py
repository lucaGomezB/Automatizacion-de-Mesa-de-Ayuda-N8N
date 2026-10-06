"""
Tests de la API del disparador MANUAL de purga por retencion (c-60, 5.3 / DIR-007).

`POST /api/v1/directorio/purga` es el trigger humano explicito del borrado fisico
por retencion. Requiere rol `administrador_directorio`; devuelve el conteo y los
ids de las filas eliminadas (sin PII). Otros roles reciben 403 y el acceso anonimo
401. NO se dispara por cron/scheduler: solo por invocacion explicita.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User

_ENDPOINT = "/api/v1/directorio/purga"
_AHORA = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)


@pytest_asyncio.fixture
async def purga_env(engine):
    """Siembra un admin, un operador y una baja vencida (commit explicito)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="Sistemas", descripcion="d")
        s.add(sector)
        await s.flush()

        admin_user = User(username="pur-admin", hashed_password="x", is_active=True)
        oper_user = User(username="pur-oper", hashed_password="x", is_active=True)
        s.add_all([admin_user, oper_user])
        await s.flush()

        admin = Empleado(
            legajo="PUR-ADM", nombre="Admin Sintetico", email="pur.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        oper = Empleado(
            legajo="PUR-OPE", nombre="Oper Sintetico", email="pur.oper@example.test",
            sector_id=sector.id, rol=RolEmpleado.operador, user_id=oper_user.id,
        )
        viejo = Empleado(
            legajo="PUR-VIE", nombre="Viejo Sintetico", email="pur.viejo@example.test",
            sector_id=sector.id, rol=RolEmpleado.usuario_final,
            activo=False, fecha_baja=_AHORA - timedelta(days=400),
        )
        s.add_all([admin, oper, viejo])
        await s.commit()
        ids = {
            "admin_user": admin_user.id,
            "oper_user": oper_user.id,
            "viejo_id": viejo.id,
        }

    yield ids

    async with factory() as s:
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Sector))
        await s.commit()


@asynccontextmanager
async def _client(engine, user_id: int | None):
    """Cliente ASGI; si user_id es None no autentica (anonimo)."""
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
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_admin_dispara_la_purga_y_recibe_ids(engine, purga_env):
    """Un administrador purga la baja vencida y recibe {purgados, ids}."""
    async with _client(engine, purga_env["admin_user"]) as c:
        resp = await c.post(_ENDPOINT)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["purgados"] == 1
    assert body["ids"] == [purga_env["viejo_id"]]

    # Idempotencia: una segunda invocacion no vuelve a borrar nada.
    async with _client(engine, purga_env["admin_user"]) as c:
        segunda = await c.post(_ENDPOINT)
    assert segunda.status_code == 200
    assert segunda.json() == {"purgados": 0, "ids": []}


@pytest.mark.asyncio
async def test_otro_rol_no_puede_purgar_403(engine, purga_env):
    """Un rol distinto de administrador no puede disparar la purga (403)."""
    async with _client(engine, purga_env["oper_user"]) as c:
        resp = await c.post(_ENDPOINT)

    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_purga_anonima_401(engine, purga_env):
    """Sin token valido, el trigger de purga es rechazado (401)."""
    async with _client(engine, None) as c:
        resp = await c.post(_ENDPOINT)

    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"
