"""Tests de API del borrado logico (c-87, SD-002/VIS-009).

Cubren, en la capa HTTP y con la derivacion REAL de rol/alcance:
    - `administrador_directorio` borra un incidente visible y recibe 204 sin cuerpo.
    - `mesa_de_ayuda` y `usuario_final` reciben 403 sin modificar filas.
    - Una cuenta sin empleado vinculado recibe 403.
    - Un incidente inexistente o ya borrado responde 404 sin revelar existencia.
    - Sin token responde 401.
    - La fila persiste tras el 204 (no es borrado fisico).
    - Un administrador no ve el incidente borrado en el listado ni en el detalle.
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
async def c87_api_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="Sistemas", descripcion="A")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector, estado])
        await s.flush()

        u_admin = User(username="c87-admin", hashed_password="x", is_active=True)
        u_mesa = User(username="c87-mesa", hashed_password="x", is_active=True)
        u_final = User(username="c87-final", hashed_password="x", is_active=True)
        u_norol = User(username="c87-norol", hashed_password="x", is_active=True)
        s.add_all([u_admin, u_mesa, u_final, u_norol])
        await s.flush()

        e_admin = Empleado(
            legajo="C87-ADM", nombre="Admin", email="c87.admin@example.test",
            sector_id=sector.id, rol=RolEmpleado.administrador_directorio,
            user_id=u_admin.id,
        )
        e_mesa = Empleado(
            legajo="C87-MESA", nombre="Mesa", email="c87.mesa@example.test",
            sector_id=sector.id, rol=RolEmpleado.mesa_de_ayuda, user_id=u_mesa.id,
        )
        e_final = Empleado(
            legajo="C87-FIN", nombre="Final", email="c87.final@example.test",
            sector_id=sector.id, rol=RolEmpleado.usuario_final, user_id=u_final.id,
        )
        s.add_all([e_admin, e_mesa, e_final])
        await s.flush()

        base = dict(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector.id,
        )
        ia = Incidente(**base, origen_message_id="c87-A")
        ib = Incidente(**base, origen_message_id="c87-B")
        s.add_all([ia, ib])
        await s.commit()

        ids = {
            "u_admin": u_admin.id,
            "u_mesa": u_mesa.id,
            "u_final": u_final.id,
            "u_norol": u_norol.id,
            "actor_admin": e_admin.id,
            "ia": ia.id,
            "ib": ib.id,
        }
    yield ids

    async with factory() as s:
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


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


async def _leer_incidente(engine, incidente_id: int) -> Incidente | None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        return await s.get(Incidente, incidente_id)


# ── Autorizacion ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_borra_204_sin_cuerpo(engine, c87_api_env):
    """El administrador borra un incidente visible y recibe 204 sin cuerpo."""
    async with _client(engine, c87_api_env["u_admin"]) as c:
        resp = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert resp.status_code == 204, resp.text
    assert resp.content == b""

    fila = await _leer_incidente(engine, c87_api_env["ia"])
    assert fila is not None
    assert fila.deleted_at is not None
    assert fila.deleted_by == c87_api_env["actor_admin"]


@pytest.mark.asyncio
async def test_mesa_de_ayuda_rechazado_403(engine, c87_api_env):
    """`mesa_de_ayuda` recibe 403 y no se modifica ninguna fila."""
    async with _client(engine, c87_api_env["u_mesa"]) as c:
        resp = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert resp.status_code == 403
    fila = await _leer_incidente(engine, c87_api_env["ia"])
    assert fila.deleted_at is None


@pytest.mark.asyncio
async def test_usuario_final_rechazado_403(engine, c87_api_env):
    """`usuario_final` recibe 403."""
    async with _client(engine, c87_api_env["u_final"]) as c:
        resp = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_rechazado_403(engine, c87_api_env):
    """Una cuenta autenticada sin empleado vinculado recibe 403 (SD-001)."""
    async with _client(engine, c87_api_env["u_norol"]) as c:
        resp = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert resp.status_code == 403
    fila = await _leer_incidente(engine, c87_api_env["ia"])
    assert fila.deleted_at is None


@pytest.mark.asyncio
async def test_anonimo_rechazado_401(engine, c87_api_env):
    """Sin autenticacion el endpoint responde 401."""
    async with _client(engine, None) as c:
        resp = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert resp.status_code == 401


# ── Semantica 404 ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_incidente_inexistente_404(engine, c87_api_env):
    """Un incidente inexistente responde 404 sin revelar existencia."""
    async with _client(engine, c87_api_env["u_admin"]) as c:
        resp = await c.delete("/api/v1/incidentes/999999")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_segundo_borrado_404(engine, c87_api_env):
    """Un incidente ya borrado responde 404 y no altera el marcador."""
    async with _client(engine, c87_api_env["u_admin"]) as c:
        primero = await c.delete(f"/api/v1/incidentes/{c87_api_env['ib']}")
        segundo = await c.delete(f"/api/v1/incidentes/{c87_api_env['ib']}")

    assert primero.status_code == 204
    assert segundo.status_code == 404


# ── Exclusión de las superficies de lectura (VIS-009) ─────────────────────────


@pytest.mark.asyncio
async def test_borrado_desaparece_del_listado_y_detalle(engine, c87_api_env):
    """Tras borrar, el incidente no aparece en el listado y el detalle da 404."""
    async with _client(engine, c87_api_env["u_admin"]) as c:
        borrado = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")
        listado = await c.get("/api/v1/incidentes/")
        detalle = await c.get(f"/api/v1/incidentes/{c87_api_env['ia']}")

    assert borrado.status_code == 204
    assert listado.status_code == 200
    ids = {i["id"] for i in listado.json()}
    assert c87_api_env["ia"] not in ids
    assert c87_api_env["ib"] in ids
    assert detalle.status_code == 404


@pytest.mark.asyncio
async def test_patch_sobre_borrado_404(engine, c87_api_env):
    """Un PATCH sobre un incidente borrado responde 404 y no modifica la fila."""
    async with _client(engine, c87_api_env["u_admin"]) as c:
        borrado = await c.delete(f"/api/v1/incidentes/{c87_api_env['ia']}")
        patch = await c.patch(
            f"/api/v1/incidentes/{c87_api_env['ia']}", json={"prioridad": "baja"}
        )

    assert borrado.status_code == 204
    assert patch.status_code == 404
    fila = await _leer_incidente(engine, c87_api_env["ia"])
    assert fila.prioridad == PrioridadEnum.media  # sin cambios
