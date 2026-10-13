"""
Tests de visibilidad de clasificaciones por alcance (c-82, VIS-001/VIS-002).

VIS-001 extendido a los endpoints de clasificaciones:
    - `administrador_directorio` y `mesa_de_ayuda` (GLOBAL) acceden a las
      clasificaciones de CUALQUIER incidente.
    - `usuario_final` (PROPIO) solo accede a las clasificaciones de los
      incidentes que reportó (`reportante_empleado_id`).
    - Acceso fuera de alcance => 404 (NOT_FOUND), sin revelar la existencia.
    - Cuenta sin empleado (alcance VACIO) => 404.
    - Anonimo => 401.
    - El PATCH de validacion NUNCA muta una fila fuera de alcance.

La regla reutiliza el servicio/dependencia `incident_visibility` (AlcanceIncidentes);
no duplica logica.
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
from app.models.catalog import Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User


@pytest_asyncio.fixture
async def clasif_vis_env(engine):
    """Siembra sectores, cuentas/empleados por rol, tres incidentes y sus logs."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector_a = Sector(nombre="Sistemas", descripcion="A")
        sector_b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector_a, sector_b, estado])
        await s.flush()

        admin_user = User(username="clv-admin", hashed_password="x", is_active=True)
        mesa_user = User(username="clv-mesa", hashed_password="x", is_active=True)
        e1_user = User(username="clv-e1", hashed_password="x", is_active=True)
        e2_user = User(username="clv-e2", hashed_password="x", is_active=True)
        s.add_all([admin_user, mesa_user, e1_user, e2_user])
        await s.flush()

        admin = Empleado(
            legajo="CLV-ADM", nombre="Admin", email="clv.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        mesa = Empleado(
            legajo="CLV-MESA", nombre="Mesa", email="clv.mesa@example.test",
            rol=RolEmpleado.mesa_de_ayuda, user_id=mesa_user.id,
        )
        e1 = Empleado(
            legajo="CLV-E1", nombre="Reportante E1", email="clv.e1@example.test",
            sector_id=sector_a.id, rol=RolEmpleado.usuario_final, user_id=e1_user.id,
        )
        e2 = Empleado(
            legajo="CLV-E2", nombre="Reportante E2", email="clv.e2@example.test",
            sector_id=sector_b.id, rol=RolEmpleado.usuario_final, user_id=e2_user.id,
        )
        s.add_all([admin, mesa, e1, e2])
        await s.flush()

        inc_a = Incidente(
            descripcion_original="incidente A",
            descripcion_pseudonimizada="incidente A",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_a.id,
            reportante_empleado_id=e1.id,
            requiere_revision_humana=True,
        )
        inc_b = Incidente(
            descripcion_original="incidente B",
            descripcion_pseudonimizada="incidente B",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_b.id,
            reportante_empleado_id=e2.id,
            requiere_revision_humana=True,
        )
        # Incidente de E1 SIN revision humana: control negativo para la cola.
        inc_plain = Incidente(
            descripcion_original="incidente plain",
            descripcion_pseudonimizada="incidente plain",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_a.id,
            reportante_empleado_id=e1.id,
            requiere_revision_humana=False,
        )
        s.add_all([inc_a, inc_b, inc_plain])
        await s.flush()

        log_a = ClasificacionLog(
            incidente_id=inc_a.id, sector_id_predicho=sector_a.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        )
        log_b = ClasificacionLog(
            incidente_id=inc_b.id, sector_id_predicho=sector_b.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        )
        # El log del incidente plano NO requiere revision: nunca entra a la cola.
        log_plain = ClasificacionLog(
            incidente_id=inc_plain.id, sector_id_predicho=sector_a.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=False, respuesta_raw="{}",
        )
        # FIFO determinista: log_a es mas antiguo que log_b.
        _ahora = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)
        log_a.created_at = _ahora - timedelta(hours=2)
        log_b.created_at = _ahora - timedelta(hours=1)
        log_plain.created_at = _ahora
        s.add_all([log_a, log_b, log_plain])
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "mesa_user": mesa_user.id,
            "e1_user": e1_user.id,
            "e2_user": e2_user.id,
            "sin_empleado_user": 888888,
            "incidente_a": inc_a.id,
            "incidente_b": inc_b.id,
            "incidente_plain": inc_plain.id,
            "log_a": log_a.id,
            "log_b": log_b.id,
            "log_plain": log_plain.id,
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
    """El administrador lee el historial de un incidente ajeno."""
    async with _client(engine, clasif_vis_env["admin_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_b']}"
        )
    assert resp.status_code == 200
    assert any(item["id"] == clasif_vis_env["log_b"] for item in resp.json())


@pytest.mark.asyncio
async def test_mesa_de_ayuda_lee_cualquier_incidente(engine, clasif_vis_env):
    """`mesa_de_ayuda` (GLOBAL) lee el historial de cualquier incidente."""
    async with _client(engine, clasif_vis_env["mesa_user"]) as c:
        en_revision = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
        plain = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_plain']}"
        )
    assert en_revision.status_code == 200, en_revision.text
    assert plain.status_code == 200, plain.text


@pytest.mark.asyncio
async def test_usuario_final_lee_su_incidente(engine, clasif_vis_env):
    """El `usuario_final` de E1 lee el historial de un incidente que reporto."""
    async with _client(engine, clasif_vis_env["e1_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
    assert resp.status_code == 200
    assert any(item["id"] == clasif_vis_env["log_a"] for item in resp.json())


@pytest.mark.asyncio
async def test_usuario_final_lee_ajeno_404(engine, clasif_vis_env):
    """Un `usuario_final` lee un incidente ajeno: 404 (no 403)."""
    async with _client(engine, clasif_vis_env["e1_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_b']}"
        )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_alcance_vacio_lee_404(engine, clasif_vis_env):
    """Una cuenta sin empleado no lee clasificaciones (404)."""
    async with _client(engine, clasif_vis_env["sin_empleado_user"]) as c:
        resp = await c.get(
            f"/api/v1/clasificaciones/incidente/{clasif_vis_env['incidente_a']}"
        )
    assert resp.status_code == 404


# ── VALIDATE: PATCH /clasificaciones/{log_id}/validar ────────────────────────


@pytest.mark.asyncio
async def test_admin_valida_cualquier_log(engine, clasif_vis_env):
    """El administrador valida un log de un incidente ajeno."""
    async with _client(engine, clasif_vis_env["admin_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_b']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_b"]},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["sector_validado"]["id"] == clasif_vis_env["sector_b"]


@pytest.mark.asyncio
async def test_usuario_final_valida_su_incidente_200(engine, clasif_vis_env):
    """El `usuario_final` de E1 valida un log de un incidente que reporto."""
    async with _client(engine, clasif_vis_env["e1_user"]) as c:
        resp = await c.patch(
            f"/api/v1/clasificaciones/{clasif_vis_env['log_a']}/validar",
            json={"sector_id_validado": clasif_vis_env["sector_a"]},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["sector_validado"]["id"] == clasif_vis_env["sector_a"]

    filas = await _leer_filas(
        engine, clasif_vis_env["incidente_a"], clasif_vis_env["log_a"]
    )
    assert filas["sector_id_validado"] == clasif_vis_env["sector_a"]
    assert filas["requiere_revision_humana"] is False


@pytest.mark.asyncio
async def test_usuario_final_valida_ajeno_404_y_no_muta(engine, clasif_vis_env):
    """Fuera de alcance: 404 y la fila NO se modifica (incidente ni log)."""
    async with _client(engine, clasif_vis_env["e1_user"]) as c:
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


# ── Cola `revision-pendiente` acotada por alcance (VIS-002) ───────────────────


@pytest.mark.asyncio
async def test_revision_pendiente_admin_ve_cola_completa(engine, clasif_vis_env):
    """El administrador ve los pendientes de todos los sectores, en FIFO."""
    async with _client(engine, clasif_vis_env["admin_user"]) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente")
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()]
    assert ids == [clasif_vis_env["log_a"], clasif_vis_env["log_b"]]


@pytest.mark.asyncio
async def test_revision_pendiente_mesa_de_ayuda_ve_cola_completa(engine, clasif_vis_env):
    """`mesa_de_ayuda` ve la cola completa (es la poblacion que debe revisar)."""
    async with _client(engine, clasif_vis_env["mesa_user"]) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente")
    assert resp.status_code == 200
    ids = {item["id"] for item in resp.json()}
    assert ids == {clasif_vis_env["log_a"], clasif_vis_env["log_b"]}


@pytest.mark.asyncio
async def test_revision_pendiente_usuario_final_ve_solo_sus_pendientes(
    engine, clasif_vis_env
):
    """Un `usuario_final` de E1 solo ve el pendiente de un incidente que reporto."""
    async with _client(engine, clasif_vis_env["e1_user"]) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente")
    assert resp.status_code == 200
    ids = {item["id"] for item in resp.json()}
    assert ids == {clasif_vis_env["log_a"]}
    assert clasif_vis_env["log_b"] not in ids


@pytest.mark.asyncio
async def test_revision_pendiente_alcance_vacio_ve_lista_vacia(engine, clasif_vis_env):
    """Una cuenta sin empleado ve una lista vacia (no la cola global)."""
    async with _client(engine, clasif_vis_env["sin_empleado_user"]) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_revision_pendiente_anonimo_401(engine, clasif_vis_env):
    """Sin autenticacion la cola responde 401 (sin cambios)."""
    async with _anon_client(engine) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente")
    assert resp.status_code == 401
