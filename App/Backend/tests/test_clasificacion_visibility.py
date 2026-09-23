"""
Tests de visibilidad de clasificaciones por rol (c-54, NIT-1).

VIS-001 extendido a los endpoints de clasificaciones:
    - `administrador_directorio` accede a las clasificaciones de CUALQUIER sector.
    - `usuario_final`/`operador` con sector S solo accede a las clasificaciones
      de incidentes del sector S.
    - Acceso fuera de alcance => 404 (NOT_FOUND), sin revelar la existencia.
    - Cuenta sin empleado/sector (alcance VACIO) => 404.
    - Anonimo => 401.
    - El PATCH de validacion NUNCA muta una fila fuera de alcance.

La regla reutiliza el servicio/dependencia `incident_visibility` (AlcanceIncidentes);
no duplica logica.
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
from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User


@pytest_asyncio.fixture
async def clasif_vis_env(engine):
    """Siembra sectores, cuentas/empleados por rol, dos incidentes y sus logs."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector_a = Sector(nombre="Sistemas", descripcion="A")
        sector_b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector_a, sector_b, estado])
        await s.flush()

        admin_user = User(username="clv-admin", hashed_password="x", is_active=True)
        oper_a_user = User(username="clv-oper-a", hashed_password="x", is_active=True)
        s.add_all([admin_user, oper_a_user])
        await s.flush()

        s.add_all(
            [
                Empleado(
                    legajo="CLV-ADM", nombre="Admin", email="clv.admin@example.test",
                    rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
                ),
                Empleado(
                    legajo="CLV-OPE-A", nombre="Oper A", email="clv.oper.a@example.test",
                    sector_id=sector_a.id, rol=RolEmpleado.operador,
                    user_id=oper_a_user.id,
                ),
            ]
        )
        await s.flush()

        inc_a = Incidente(
            descripcion_original="incidente A",
            descripcion_pseudonimizada="incidente A",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_a.id,
            requiere_revision_humana=True,
        )
        inc_b = Incidente(
            descripcion_original="incidente B",
            descripcion_pseudonimizada="incidente B",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_b.id,
            requiere_revision_humana=True,
        )
        s.add_all([inc_a, inc_b])
        await s.flush()

        log_a = ClasificacionLog(
            incidente_id=inc_a.id, sector_id_predicho=sector_a.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        )
        log_b = ClasificacionLog(
            incidente_id=inc_b.id, sector_id_predicho=sector_b.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        )
        s.add_all([log_a, log_b])
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "oper_a_user": oper_a_user.id,
            "sin_empleado_user": 888888,
            "incidente_a": inc_a.id,
            "incidente_b": inc_b.id,
            "log_a": log_a.id,
            "log_b": log_b.id,
            "sector_a": sector_a.id,
            "sector_b": sector_b.id,
        }

    yield ids

    async with factory() as s:
        await s.execute(delete(ClasificacionLog))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


def _override_db(engine):
    async def override_db():
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return override_db


@asynccontextmanager
async def _client(engine, user_id: int):
    """Cliente autenticado con el alcance derivado realmente de la BD (sin override)."""
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_db(engine)

    async def override_auth():
        return User(id=user_id, username=f"u{user_id}", hashed_password="", is_active=True)

    app.dependency_overrides[get_current_user] = override_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@asynccontextmanager
async def _anon_client(engine):
    """Cliente sin autenticacion: solo se sustituye la base de datos."""
    app = create_app()
    app.dependency_overrides[get_db_session] = _override_db(engine)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


async def _leer_filas(engine, incidente_id: int, log_id: int):
    """Re-lectura directa de la BD: sector del incidente y estado del log."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        inc = await s.get(Incidente, incidente_id)
        log = await s.get(ClasificacionLog, log_id)
        return {
            "sector_id": inc.sector_id,
            "requiere_revision_humana": inc.requiere_revision_humana,
            "sector_id_validado": log.sector_id_validado,
        }


# ── READ: GET /clasificaciones/incidente/{id} ────────────────────────────────


@pytest.mark.asyncio
async def test_admin_lee_clasificaciones_de_cualquier_sector(engine, clasif_vis_env):
    """El administrador lee el historial de un incidente ajeno (sector B)."""
    async with _client(engine, clasif_vis_env["admin_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_b']}"
        )
    assert resp.status_code == 200
    assert any(item["id"] == clasif_vis_env["log_b"] for item in resp.json())


@pytest.mark.asyncio
async def test_no_admin_lee_clasificaciones_de_su_sector(engine, clasif_vis_env):
    """El operador del sector A lee el historial de un incidente de A."""
    async with _client(engine, clasif_vis_env["oper_a_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
    assert resp.status_code == 200
    assert any(item["id"] == clasif_vis_env["log_a"] for item in resp.json())


@pytest.mark.asyncio
async def test_no_admin_lee_fuera_de_sector_404(engine, clasif_vis_env):
    """Un no administrador lee un incidente fuera de su sector: 404 (no 403)."""
    async with _client(engine, clasif_vis_env["oper_a_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_b']}"
        )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_alcance_vacio_lee_404(engine, clasif_vis_env):
    """Una cuenta sin empleado/sector no lee clasificaciones (404)."""
    async with _client(engine, clasif_vis_env["sin_empleado_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
    assert resp.status_code == 404


# ── VALIDATE: PATCH /clasificaciones/{log_id}/validar ────────────────────────


@pytest.mark.asyncio
async def test_admin_valida_cualquier_log(engine, clasif_vis_env):
    """El administrador valida un log de un incidente ajeno (sector B)."""
    async with _client(engine, clasif_vis_env["admin_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_b']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_b"]},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["sector_validado"]["id"] == clasif_vis_env["sector_b"]


@pytest.mark.asyncio
async def test_no_admin_valida_dentro_de_sector_200(engine, clasif_vis_env):
    """El operador del sector A valida un log de un incidente de A."""
    async with _client(engine, clasif_vis_env["oper_a_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_a']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_a"]},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["sector_validado"]["id"] == clasif_vis_env["sector_a"]

    # Triangulacion: dentro de alcance la mutacion SI se aplica (log + incidente).
    filas = await _leer_filas(
        engine, clasif_vis_env["incidente_a"], clasif_vis_env["log_a"]
    )
    assert filas["sector_id_validado"] == clasif_vis_env["sector_a"]
    assert filas["requiere_revision_humana"] is False


@pytest.mark.asyncio
async def test_no_admin_valida_fuera_de_sector_404_y_no_muta(engine, clasif_vis_env):
    """Fuera de alcance: 404 y la fila NO se modifica (incidente ni log)."""
    async with _client(engine, clasif_vis_env["oper_a_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_b']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_a"]},
        )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"

    filas = await _leer_filas(
        engine, clasif_vis_env["incidente_b"], clasif_vis_env["log_b"]
    )
    assert filas["sector_id_validado"] is None
    assert filas["sector_id"] == clasif_vis_env["sector_b"]
    assert filas["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_alcance_vacio_valida_404(engine, clasif_vis_env):
    """Una cuenta con alcance vacio no valida (404) y no muta."""
    async with _client(engine, clasif_vis_env["sin_empleado_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_b']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_a"]},
        )
    assert resp.status_code == 404
    filas = await _leer_filas(
        engine, clasif_vis_env["incidente_b"], clasif_vis_env["log_b"]
    )
    assert filas["sector_id_validado"] is None


# ── ANONYMOUS ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_anonimo_401(engine, clasif_vis_env):
    """Sin autenticacion: 401 en ambos endpoints (sin cambios)."""
    async with _anon_client(engine) as c:
        lectura = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
        validar = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_a']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_a"]},
        )
    assert lectura.status_code == 401
    assert validar.status_code == 401