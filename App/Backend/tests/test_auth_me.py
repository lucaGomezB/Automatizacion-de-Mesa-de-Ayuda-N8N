"""
Tests del endpoint aditivo de identidad y alcance (c-81, IAH-012).

`GET /api/v1/auth/me` devuelve la identidad efectiva de la sesion y su alcance
de incidentes DERIVADO por request desde el directorio, reutilizando
`EmpleadoRepository.get_by_user_id` + `alcance_desde_empleado` (que lee el
registro unico de politica de rol). NO duplica el mapeo rol -> alcance.

Modelo de modos (c-82): PROPIO | GLOBAL | VACIO, sin sector ni `ver_todos`.

Patron: espejo de `tests/test_incident_visibility.py` (override de
`get_db_session` y `get_current_user`). El caso anonimo NO sobrescribe
`get_current_user`, de modo que el middleware JWT real responda 401 con el
envelope estandar.
"""

from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User


@pytest_asyncio.fixture
async def me_env(engine):
    """Siembra cuentas y empleados por rol, mas una cuenta sin empleado."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        admin_user = User(username="me-admin", hashed_password="x", is_active=True)
        mesa_user = User(username="me-mesa", hashed_password="x", is_active=True)
        final_user = User(username="me-final", hashed_password="x", is_active=True)
        huerfano_user = User(username="me-huerfano", hashed_password="x", is_active=True)
        s.add_all([admin_user, mesa_user, final_user, huerfano_user])
        await s.flush()

        admin = Empleado(
            legajo="ME-ADM", nombre="Admin", email="me.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        mesa = Empleado(
            legajo="ME-MESA", nombre="Mesa", email="me.mesa@example.test",
            rol=RolEmpleado.mesa_de_ayuda, user_id=mesa_user.id,
        )
        final = Empleado(
            legajo="ME-FIN", nombre="Final", email="me.final@example.test",
            rol=RolEmpleado.usuario_final, user_id=final_user.id,
        )
        s.add_all([admin, mesa, final])
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "mesa_user": mesa_user.id,
            "final_user": final_user.id,
            "huerfano_user": huerfano_user.id,
            "admin_empleado": admin.id,
            "username_admin": admin_user.username,
            "username_mesa": mesa_user.username,
            "username_final": final_user.username,
        }

    yield ids

    async with factory() as s:
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.commit()


@asynccontextmanager
async def _client(engine, user_id: int | None, username: str = "anon"):
    """Cliente ASGI con la DB de test; autentica al usuario indicado (o anonimo)."""
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
            return User(
                id=user_id, username=username, hashed_password="", is_active=True
            )

        app.dependency_overrides[get_current_user] = override_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


# ── IAH-012: identidad y alcance derivados por rol ────────────────────────────


@pytest.mark.asyncio
async def test_admin_directorio_obtiene_global(engine, me_env):
    """`administrador_directorio` con empleado activo -> rol + alcance GLOBAL."""
    async with _client(engine, me_env["admin_user"], me_env["username_admin"]) as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == me_env["username_admin"]
    assert body["rol"] == "administrador_directorio"
    assert body["alcance"] == {"modo": "GLOBAL"}


@pytest.mark.asyncio
async def test_mesa_de_ayuda_obtiene_global(engine, me_env):
    """`mesa_de_ayuda` -> alcance GLOBAL."""
    async with _client(engine, me_env["mesa_user"], me_env["username_mesa"]) as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == me_env["username_mesa"]
    assert body["rol"] == "mesa_de_ayuda"
    assert body["alcance"] == {"modo": "GLOBAL"}


@pytest.mark.asyncio
async def test_usuario_final_obtiene_propio(engine, me_env):
    """`usuario_final` -> alcance PROPIO."""
    async with _client(engine, me_env["final_user"], me_env["username_final"]) as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == me_env["username_final"]
    assert body["rol"] == "usuario_final"
    assert body["alcance"] == {"modo": "PROPIO"}


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_obtiene_rol_nulo_y_vacio(engine, me_env):
    """Cuenta autenticada sin empleado activo -> rol nulo + alcance VACIO."""
    async with _client(engine, me_env["huerfano_user"]) as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["rol"] is None
    assert body["alcance"] == {"modo": "VACIO"}


@pytest.mark.asyncio
async def test_anonimo_obtiene_401_con_envelope(engine, me_env):
    """Sin autenticacion -> 401 con el envelope estandar y sin datos de identidad."""
    async with _client(engine, None) as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code == 401
    body = resp.json()
    assert "detail" not in body
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "username" not in body
    assert "rol" not in body


# ── IAH-012: recomputo por request y ausencia del modelo anterior ─────────────


@pytest.mark.asyncio
async def test_alcance_se_recomputa_al_cambiar_el_rol_sin_relogin(engine, me_env):
    """Cambiar el rol del empleado recomputa el modo en la siguiente consulta."""
    async with _client(engine, me_env["admin_user"], me_env["username_admin"]) as c:
        primero = await c.get("/api/v1/auth/me")
    assert primero.json()["alcance"] == {"modo": "GLOBAL"}

    # El directorio cambia el rol del empleado vinculado (sin tocar la sesion).
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        await s.execute(
            update(Empleado)
            .where(Empleado.id == me_env["admin_empleado"])
            .values(rol=RolEmpleado.usuario_final.value)
        )
        await s.commit()

    async with _client(engine, me_env["admin_user"], me_env["username_admin"]) as c:
        segundo = await c.get("/api/v1/auth/me")
    assert segundo.status_code == 200
    assert segundo.json()["rol"] == "usuario_final"
    assert segundo.json()["alcance"] == {"modo": "PROPIO"}


@pytest.mark.asyncio
async def test_respuesta_no_expone_el_modelo_rbac_anterior(engine, me_env):
    """La respuesta expone solo username/rol/alcance.modo, sin sector/ver_todos/revision."""
    async with _client(engine, me_env["admin_user"], me_env["username_admin"]) as c:
        resp = await c.get("/api/v1/auth/me")
    body = resp.json()
    assert set(body.keys()) == {"username", "rol", "alcance"}
    assert set(body["alcance"].keys()) == {"modo"}
    for legacy in ("sector", "sector_id", "ver_todos", "revision"):
        assert legacy not in body
        assert legacy not in body["alcance"]
