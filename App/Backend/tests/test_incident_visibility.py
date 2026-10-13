"""
Tests de visibilidad de incidentes por alcance (c-82, VIS-001/VIS-002).

Modelo PROPIO/GLOBAL/VACIO (sin aislamiento por sector):
    - `administrador_directorio` y `mesa_de_ayuda`: alcance GLOBAL (ven todo).
    - `usuario_final`: alcance PROPIO (solo lo que reporto, via
      `reportante_empleado_id`).
    - Cuenta sin empleado: alcance VACIO (no ve nada).
    - El sector NO acota la visibilidad.

El filtrado se aplica en la capa de API/servicio; el frontend se difiere.
"""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

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
from app.services.incident_visibility import (
    AlcanceIncidentes,
    ModoAlcance,
    alcance_desde_empleado,
)
from app.services.incidente_service import IncidenteService


@pytest_asyncio.fixture
async def vis_env(engine):
    """Siembra sectores, estado, cuentas/empleados por rol y cuatro incidentes."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector_a = Sector(nombre="Sistemas", descripcion="A")
        sector_b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector_a, sector_b, estado])
        await s.flush()

        admin_user = User(username="vis-admin", hashed_password="x", is_active=True)
        mesa_user = User(username="vis-mesa", hashed_password="x", is_active=True)
        e1_user = User(username="vis-e1", hashed_password="x", is_active=True)
        e2_user = User(username="vis-e2", hashed_password="x", is_active=True)
        s.add_all([admin_user, mesa_user, e1_user, e2_user])
        await s.flush()

        admin = Empleado(
            legajo="V-ADM", nombre="Admin", email="v.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        mesa = Empleado(
            legajo="V-MESA", nombre="Mesa de ayuda", email="v.mesa@example.test",
            rol=RolEmpleado.mesa_de_ayuda, user_id=mesa_user.id,
        )
        e1 = Empleado(
            legajo="V-E1", nombre="Reportante E1", email="v.e1@example.test",
            sector_id=sector_a.id, rol=RolEmpleado.usuario_final, user_id=e1_user.id,
        )
        e2 = Empleado(
            legajo="V-E2", nombre="Reportante E2", email="v.e2@example.test",
            sector_id=sector_b.id, rol=RolEmpleado.usuario_final, user_id=e2_user.id,
        )
        s.add_all([admin, mesa, e1, e2])
        await s.flush()

        s.add_all(
            [
                # Reportado por E1 aunque es del sector A.
                Incidente(
                    descripcion_original="incidente A de E1",
                    descripcion_pseudonimizada="incidente A de E1",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                    reportante_empleado_id=e1.id,
                    origen_message_id="corpus-A",
                ),
                # Reportado por E2, del sector B.
                Incidente(
                    descripcion_original="incidente B de E2",
                    descripcion_pseudonimizada="incidente B de E2",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_b.id,
                    reportante_empleado_id=e2.id,
                    origen_message_id="corpus-B",
                ),
                # Sin reportante (legacy / no identificado), sin sector.
                Incidente(
                    descripcion_original="incidente sin reportante",
                    descripcion_pseudonimizada="incidente sin reportante",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=None,
                    reportante_empleado_id=None,
                    origen_message_id="corpus-SIN",
                ),
                # Reportado por E1 y en revision humana.
                Incidente(
                    descripcion_original="incidente en revision de E1",
                    descripcion_pseudonimizada="incidente en revision de E1",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                    reportante_empleado_id=e1.id,
                    requiere_revision_humana=True,
                    origen_message_id="corpus-REV",
                ),
            ]
        )
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "mesa_user": mesa_user.id,
            "e1_user": e1_user.id,
            "e2_user": e2_user.id,
            "sin_empleado_user": 888888,
            "e1_empleado": e1.id,
            "e2_empleado": e2.id,
            "sector_a": sector_a.id,
            "sector_b": sector_b.id,
        }

        filas = (await s.execute(select(Incidente))).scalars().all()
        por_origen = {f.origen_message_id: f.id for f in filas}
        ids["incidente_a"] = por_origen["corpus-A"]
        ids["incidente_b"] = por_origen["corpus-B"]
        ids["incidente_sin"] = por_origen["corpus-SIN"]
        ids["incidente_revision"] = por_origen["corpus-REV"]

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


# ── API: listado y acceso puntual ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_ve_todos_los_incidentes(engine, vis_env):
    """El administrador lista incidentes de todos los sectores y reportantes."""
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert {
        vis_env["incidente_a"],
        vis_env["incidente_b"],
        vis_env["incidente_sin"],
        vis_env["incidente_revision"],
    } <= ids


@pytest.mark.asyncio
async def test_mesa_de_ayuda_ve_todos_los_incidentes(engine, vis_env):
    """`mesa_de_ayuda` lista incidentes de todos los sectores."""
    async with _client(engine, vis_env["mesa_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    sectores = {i["sector"]["id"] for i in resp.json() if i["sector"]}
    assert len(sectores) >= 2


@pytest.mark.asyncio
async def test_usuario_final_ve_solo_lo_que_reporto(engine, vis_env):
    """`usuario_final` de E1 ve unicamente los incidentes reportados por E1."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert ids == {vis_env["incidente_a"], vis_env["incidente_revision"]}


@pytest.mark.asyncio
async def test_usuario_final_no_ve_lo_de_otros(engine, vis_env):
    """`usuario_final` de E1 no accede al incidente reportado por E2 (404)."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_alcance_vacio(engine, vis_env):
    """Una cuenta sin empleado vinculado no ve incidentes."""
    async with _client(engine, vis_env["sin_empleado_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_incidente_sin_reportante_no_visible_para_usuario_final(engine, vis_env):
    """Un incidente sin reportante no es visible para ningun `usuario_final`."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.get(f"/api/v1/incidentes/{vis_env['incidente_sin']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_el_sector_no_acota_la_visibilidad(engine, vis_env):
    """`mesa_de_ayuda` ve incidentes de cualquier sector (sin filtro de sector)."""
    async with _client(engine, vis_env["mesa_user"]) as c:
        resp = await c.get("/api/v1/incidentes/", params={"sector_id": vis_env["sector_a"]})
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    # El filtro por sector es organizacional, no una frontera: sin sector pedido
    # ve igual todo; aun con sector pedido el alcance del rol no se reduce.
    assert vis_env["incidente_a"] in ids


@pytest.mark.asyncio
async def test_acceso_puntual_fuera_de_alcance_404(engine, vis_env):
    """Un `usuario_final` no lee un incidente ajeno (404, sin revelar existencia)."""
    async with _client(engine, vis_env["e1_user"]) as c:
        propio = await c.get(f"/api/v1/incidentes/{vis_env['incidente_a']}")
        ajeno = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert propio.status_code == 200
    assert ajeno.status_code == 404
    assert ajeno.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_patch_fuera_de_alcance_404_y_no_modifica(engine, vis_env):
    """Un `usuario_final` no muta un incidente ajeno (404) y no se modifica."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_b']}",
            json={"prioridad": "alta"},
        )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"

    async with _client(engine, vis_env["admin_user"]) as c:
        detalle = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert detalle.status_code == 200
    assert detalle.json()["prioridad"] == "media"


@pytest.mark.asyncio
async def test_patch_dentro_de_alcance_200(engine, vis_env):
    """El control positivo: un `usuario_final` si muta un incidente que reporto."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_a']}",
            json={"prioridad": "alta"},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["prioridad"] == "alta"


# ── Unidad: derivacion de alcance ─────────────────────────────────────────────


class _IncidenteStub:
    """Stub minimo: `permite_incidente` solo lee `reportante_empleado_id`."""

    def __init__(self, reportante_empleado_id):
        self.reportante_empleado_id = reportante_empleado_id


def _empleado(rol, empleado_id=None):
    e = Empleado(
        legajo=f"E-{rol}", nombre="Sintetico", email=f"{rol}@example.test",
        rol=rol, sector_id=None,
    )
    if empleado_id is not None:
        e.id = empleado_id
    return e


def test_alcance_desde_empleado_mapea_propio_global_y_vacio():
    """`alcance_desde_empleado` deriva PROPIO/GLOBAL/VACIO por rol."""
    assert alcance_desde_empleado(None).modo is ModoAlcance.VACIO
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.administrador_directorio)).modo
        is ModoAlcance.GLOBAL
    )
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.mesa_de_ayuda)).modo
        is ModoAlcance.GLOBAL
    )
    propio = alcance_desde_empleado(_empleado(RolEmpleado.usuario_final, empleado_id=7))
    assert propio.modo is ModoAlcance.PROPIO
    assert propio.reportante_empleado_id == 7


def test_permite_incidente_global_propio_y_vacio():
    """GLOBAL permite todo; PROPIO solo lo reportado; VACIO nada."""
    assert (
        AlcanceIncidentes(ModoAlcance.GLOBAL).permite_incidente(_IncidenteStub(9))
        is True
    )
    propio = AlcanceIncidentes(ModoAlcance.PROPIO, reportante_empleado_id=7)
    assert propio.permite_incidente(_IncidenteStub(7)) is True
    assert propio.permite_incidente(_IncidenteStub(8)) is False
    assert propio.permite_incidente(_IncidenteStub(None)) is False
    vacio = AlcanceIncidentes()
    assert vacio.modo is ModoAlcance.VACIO
    assert vacio.permite_incidente(_IncidenteStub(7)) is False


@pytest.mark.asyncio
async def test_service_list_incidentes_propio_filtra_por_reportante(engine, vis_env):
    """El servicio acota el listado al reportante del alcance PROPIO."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        service = IncidenteService(session, classifier=AsyncMock())

        global_ = AlcanceIncidentes(ModoAlcance.GLOBAL)
        todos = await service.list_incidentes(alcance=global_)
        assert len(todos) >= 4

        propio = AlcanceIncidentes(
            ModoAlcance.PROPIO, reportante_empleado_id=vis_env["e1_empleado"]
        )
        propios = await service.list_incidentes(alcance=propio)
        assert {i.id for i in propios} == {
            vis_env["incidente_a"],
            vis_env["incidente_revision"],
        }


# ── c-69: filtro exacto por origen_message_id respetando el alcance ──────────


@pytest.mark.asyncio
async def test_usuario_final_filtra_origen_ajeno_no_lo_ve(engine, vis_env):
    """Un `usuario_final` que filtra por el id de un incidente ajeno ve vacio."""
    async with _client(engine, vis_env["e1_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-B"}
        )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_admin_filtra_origen_de_cualquier_sector(engine, vis_env):
    """El administrador ve el id de cualquier sector."""
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-B"}
        )
    assert resp.status_code == 200
    assert [i["id"] for i in resp.json()] == [vis_env["incidente_b"]]
