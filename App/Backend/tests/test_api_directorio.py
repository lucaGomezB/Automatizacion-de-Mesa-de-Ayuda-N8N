"""
Tests de la API de gestion del directorio (c-54, seccion 6.1/6.3).

Cubren autorizacion (escritura admin, 403 para otros roles, 401 anonimo),
lectura autorizada y que respuestas/errores/auditoria no expongan PII.
"""

from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog.testing import capture_logs

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User

_ENDPOINT = "/api/v1/directorio/empleados"


@pytest_asyncio.fixture
async def directorio_env(engine):
    """Siembra sectores y cuentas/empleados de los tres roles (commit explicito)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="Sistemas", descripcion="d")
        s.add(sector)
        await s.flush()

        admin_user = User(username="dir-admin", hashed_password="x", is_active=True)
        oper_user = User(username="dir-oper", hashed_password="x", is_active=True)
        final_user = User(username="dir-final", hashed_password="x", is_active=True)
        s.add_all([admin_user, oper_user, final_user])
        await s.flush()

        admin = Empleado(
            legajo="DIR-ADM", nombre="Admin Sintetico", email="dir.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        oper = Empleado(
            legajo="DIR-OPE", nombre="Oper Sintetico", email="dir.oper@example.test",
            sector_id=sector.id, rol=RolEmpleado.operador, user_id=oper_user.id,
        )
        final = Empleado(
            legajo="DIR-FIN", nombre="Final Sintetico", email="dir.final@example.test",
            sector_id=sector.id, rol=RolEmpleado.usuario_final, user_id=final_user.id,
        )
        s.add_all([admin, oper, final])
        await s.commit()
        ids = {
            "sector_id": sector.id,
            "admin_user": admin_user.id,
            "oper_user": oper_user.id,
            "final_user": final_user.id,
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


def _payload(**overrides) -> dict:
    base = {
        "legajo": "NUEVO-1",
        "nombre": "Nuevo Empleado Sintetico",
        "email": "nuevo@example.test",
        "telefono": "+5491100003000",
        "rol": "usuario_final",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_escritura_admin_crea_201(engine, directorio_env):
    """Un administrador puede crear empleados (201)."""
    async with _client(engine, directorio_env["admin_user"]) as c:
        resp = await c.post(
            _ENDPOINT,
            json=_payload(sector_id=directorio_env["sector_id"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["legajo"] == "NUEVO-1"
    assert body["email"] == "nuevo@example.test"


@pytest.mark.asyncio
async def test_escritura_otro_rol_403(engine, directorio_env):
    """Un rol distinto de administrador no puede escribir (403)."""
    async with _client(engine, directorio_env["oper_user"]) as c:
        resp = await c.post(
            _ENDPOINT,
            json=_payload(sector_id=directorio_env["sector_id"]),
        )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_acceso_anonimo_401(engine, directorio_env):
    """Sin token valido, el acceso es rechazado (401)."""
    async with _client(engine, None) as c:
        resp = await c.post(
            _ENDPOINT, json=_payload(sector_id=directorio_env["sector_id"])
        )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_lectura_autorizada_admin_y_operador(engine, directorio_env):
    """Administrador y operador pueden listar el directorio (200)."""
    async with _client(engine, directorio_env["admin_user"]) as c:
        assert (await c.get(_ENDPOINT)).status_code == 200
    async with _client(engine, directorio_env["oper_user"]) as c:
        resp = await c.get(_ENDPOINT)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_usuario_final_no_puede_leer_403(engine, directorio_env):
    """Un usuario_final no esta autorizado a consultar el directorio (403)."""
    async with _client(engine, directorio_env["final_user"]) as c:
        resp = await c.get(_ENDPOINT)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_403(engine, directorio_env):
    """Una cuenta autenticada sin empleado vinculado no accede (403)."""
    async with _client(engine, 999999) as c:
        resp = await c.get(_ENDPOINT)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_error_y_auditoria_sin_pii(engine, directorio_env):
    """Los errores no reflejan el email y la auditoria de lectura no lleva PII."""
    email = "duplicado@example.test"
    async with _client(engine, directorio_env["admin_user"]) as c:
        creado = await c.post(
            _ENDPOINT,
            json=_payload(
                legajo="DUP-1", email=email, sector_id=directorio_env["sector_id"]
            ),
        )
        assert creado.status_code == 201, creado.text

        with capture_logs() as logs:
            duplicado = await c.post(
                _ENDPOINT,
                json=_payload(
                    legajo="DUP-2", email=email, sector_id=directorio_env["sector_id"]
                ),
            )
            listado = await c.get(_ENDPOINT)

    assert duplicado.status_code == 422
    assert email not in duplicado.text, "El error no debe reflejar el email"
    assert listado.status_code == 200

    eventos = [e for e in logs if e.get("event") == "directorio_consulta"]
    assert eventos, "La lectura debe quedar auditada"
    assert email not in repr(logs)
