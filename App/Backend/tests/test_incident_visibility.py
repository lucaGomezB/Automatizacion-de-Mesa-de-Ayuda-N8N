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
from unittest.mock import AsyncMock

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
from app.services.incident_visibility import (
    AlcanceIncidentes,
    ModoAlcance,
    alcance_desde_empleado,
)
from app.services.incidente_service import IncidenteService


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
        mesa_user = User(username="vis-mesa", hashed_password="x", is_active=True)
        s.add_all([admin_user, oper_a_user, mesa_user])
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
                Empleado(
                    legajo="V-MESA", nombre="Mesa de ayuda", email="v.mesa@example.test",
                    rol=RolEmpleado.mesa_de_ayuda, user_id=mesa_user.id,
                ),
                Incidente(
                    descripcion_original="incidente A",
                    descripcion_pseudonimizada="incidente A",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                    origen_message_id="corpus-A",
                ),
                Incidente(
                    descripcion_original="incidente B",
                    descripcion_pseudonimizada="incidente B",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_b.id,
                    origen_message_id="corpus-B",
                ),
                # c-60 (3.1): incidente SIN sector, visible para `mesa_de_ayuda`.
                Incidente(
                    descripcion_original="incidente sin sector",
                    descripcion_pseudonimizada="incidente sin sector",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=None,
                    origen_message_id="corpus-SIN",
                ),
                # c-60 (3.1): incidente CON sector que requiere revision humana.
                Incidente(
                    descripcion_original="incidente en revision",
                    descripcion_pseudonimizada="incidente en revision",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                    requiere_revision_humana=True,
                    origen_message_id="corpus-REV",
                ),
            ]
        )
        await s.commit()

        ids = {
            "admin_user": admin_user.id,
            "oper_a_user": oper_a_user.id,
            "mesa_user": mesa_user.id,
            "sin_empleado_user": 888888,
            "sector_a": sector_a.id,
            "sector_b": sector_b.id,
        }

        # Identificar los incidentes por su origen_message_id (inequivoco).
        from sqlalchemy import select

        filas = (await s.execute(select(Incidente))).scalars().all()
        por_origen = {f.origen_message_id: f.id for f in filas}
        ids["incidente_a"] = por_origen["corpus-A"]
        ids["incidente_b"] = por_origen["corpus-B"]
        ids["incidente_sin_sector"] = por_origen["corpus-SIN"]
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


@pytest.mark.asyncio
async def test_no_admin_patch_fuera_de_sector_404_y_no_modifica(engine, vis_env):
    """Un no administrador no puede mutar un incidente fuera de su sector (W3)."""
    async with _client(engine, vis_env["oper_a_user"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_b']}",
            json={"prioridad": "alta"},
        )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"

    # El incidente NO debe haberse modificado (verificado con alcance admin).
    async with _client(engine, vis_env["admin_user"]) as c:
        detalle = await c.get(f"/api/v1/incidentes/{vis_env['incidente_b']}")
    assert detalle.status_code == 200
    assert detalle.json()["prioridad"] == "media"


@pytest.mark.asyncio
async def test_no_admin_patch_dentro_de_sector_200(engine, vis_env):
    """El control positivo: un no administrador si muta un incidente de su sector."""
    async with _client(engine, vis_env["oper_a_user"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_a']}",
            json={"prioridad": "alta"},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["prioridad"] == "alta"


@pytest.mark.asyncio
async def test_admin_patch_fuera_de_sector_200(engine, vis_env):
    """El administrador si puede mutar un incidente de cualquier sector."""
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_b']}",
            json={"prioridad": "alta"},
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["prioridad"] == "alta"


@pytest.mark.asyncio
async def test_acceso_puntual_sin_empleado_404(engine, vis_env):
    """Una cuenta con alcance vacio no accede por ID ni muta (N1)."""
    async with _client(engine, vis_env["sin_empleado_user"]) as c:
        detalle = await c.get(f"/api/v1/incidentes/{vis_env['incidente_a']}")
        patch = await c.patch(
            f"/api/v1/incidentes/{vis_env['incidente_a']}",
            json={"prioridad": "alta"},
        )
    assert detalle.status_code == 404
    assert patch.status_code == 404
    assert patch.json()["error"]["code"] == "NOT_FOUND"


# ── c-69: filtro exacto por origen_message_id respetando el alcance por rol ──


@pytest.mark.asyncio
async def test_no_admin_filtra_origen_fuera_de_sector_no_lo_ve(engine, vis_env):
    """
    c-69 (2.4/2.7 RED): un no administrador que filtra por el identificador de
    un incidente fuera de su sector obtiene lista vacia (VIS-001).
    """
    async with _client(engine, vis_env["oper_a_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-B"}
        )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_no_admin_filtra_origen_dentro_de_su_sector(engine, vis_env):
    """El control positivo: un no administrador si ve el id de su sector."""
    async with _client(engine, vis_env["oper_a_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-A"}
        )
    assert resp.status_code == 200
    assert [i["id"] for i in resp.json()] == [vis_env["incidente_a"]]


@pytest.mark.asyncio
async def test_admin_filtra_origen_de_cualquier_sector(engine, vis_env):
    """
    c-69 (2.6 TRIANGULATE): el administrador ve el id de cualquier sector.
    """
    async with _client(engine, vis_env["admin_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-B"}
        )
    assert resp.status_code == 200
    assert [i["id"] for i in resp.json()] == [vis_env["incidente_b"]]


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_filtro_origen_vacio(engine, vis_env):
    """
    c-69 (2.6 TRIANGULATE): una cuenta sin empleado devuelve vacio antes de
    consultar, aun con un identificador existente.
    """
    async with _client(engine, vis_env["sin_empleado_user"]) as c:
        resp = await c.get(
            "/api/v1/incidentes/", params={"origen_message_id": "corpus-A"}
        )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_service_list_incidentes_propaga_origen_y_alcance(engine, vis_env):
    """
    c-69 (2.4 RED → 2.5 GREEN): `IncidenteService.list_incidentes` propaga el
    parametro `origen_message_id` al repositorio sin romper el alcance por rol.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        service = IncidenteService(session, classifier=AsyncMock())

        admin = AlcanceIncidentes(ver_todos=True, sector_id=None)
        encontrados = await service.list_incidentes(
            origen_message_id="corpus-A", alcance=admin
        )
        assert [i.id for i in encontrados] == [vis_env["incidente_a"]]

        oper = AlcanceIncidentes(ver_todos=False, sector_id=vis_env["sector_a"])
        fuera = await service.list_incidentes(
            origen_message_id="corpus-B", alcance=oper
        )
        assert fuera == []

        dentro = await service.list_incidentes(
            origen_message_id="corpus-A", alcance=oper
        )
        assert [i.id for i in dentro] == [vis_env["incidente_a"]]


# ── c-60 (3.1/3.4): modos de alcance y `permite_incidente` ────────────────────


class _IncidenteStub:
    """Stub minimo: `permite_incidente` solo lee sector_id y requiere_revision_humana."""

    def __init__(self, sector_id, requiere_revision_humana=False):
        self.sector_id = sector_id
        self.requiere_revision_humana = requiere_revision_humana


def _empleado(rol, sector_id=None):
    return Empleado(
        legajo=f"E-{rol}", nombre="Sintetico", email=f"{rol}@example.test",
        rol=rol, sector_id=sector_id,
    )


def test_alcance_desde_empleado_mapea_los_cuatro_modos():
    """`alcance_desde_empleado` deriva GLOBAL/SECTOR/REVISION/VACIO por rol."""
    assert alcance_desde_empleado(None).modo is ModoAlcance.VACIO
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.administrador_directorio)).modo
        is ModoAlcance.GLOBAL
    )
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.mesa_de_ayuda)).modo
        is ModoAlcance.REVISION
    )
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.operador, sector_id=7)).modo
        is ModoAlcance.SECTOR
    )
    assert (
        alcance_desde_empleado(_empleado(RolEmpleado.usuario_final)).modo
        is ModoAlcance.VACIO
    )


def test_permite_incidente_revision_acepta_sin_sector_o_en_revision():
    """En REVISION, `permite_incidente` acepta sin sector o con revision humana."""
    revision = AlcanceIncidentes(revision=True)
    assert revision.modo is ModoAlcance.REVISION
    assert revision.permite_incidente(_IncidenteStub(None, False)) is True
    assert revision.permite_incidente(_IncidenteStub(1, True)) is True
    assert revision.permite_incidente(_IncidenteStub(1, False)) is False


def test_permite_incidente_global_sector_y_vacio():
    """GLOBAL permite todo; SECTOR solo su sector; VACIO nada."""
    assert (
        AlcanceIncidentes(ver_todos=True).permite_incidente(_IncidenteStub(1, False))
        is True
    )
    sector = AlcanceIncidentes(sector_id=7)
    assert sector.modo is ModoAlcance.SECTOR
    assert sector.permite_incidente(_IncidenteStub(7, False)) is True
    assert sector.permite_incidente(_IncidenteStub(8, False)) is False
    vacio = AlcanceIncidentes()
    assert vacio.modo is ModoAlcance.VACIO
    assert vacio.permite_incidente(_IncidenteStub(None, True)) is False


@pytest.mark.asyncio
async def test_mesa_de_ayuda_ve_sin_sector_y_en_revision(engine, vis_env):
    """`mesa_de_ayuda` lista solo incidentes sin sector o que requieren revision."""
    async with _client(engine, vis_env["mesa_user"]) as c:
        resp = await c.get("/api/v1/incidentes/")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert vis_env["incidente_sin_sector"] in ids
    assert vis_env["incidente_revision"] in ids
    assert vis_env["incidente_a"] not in ids
    assert vis_env["incidente_b"] not in ids


@pytest.mark.asyncio
async def test_mesa_de_ayuda_acceso_puntual_respeta_revision(engine, vis_env):
    """`mesa_de_ayuda` accede por ID solo a sin-sector/revision; 404 si ya asignado."""
    async with _client(engine, vis_env["mesa_user"]) as c:
        sin_sector = await c.get(
            f"/api/v1/incidentes/{vis_env['incidente_sin_sector']}"
        )
        en_revision = await c.get(
            f"/api/v1/incidentes/{vis_env['incidente_revision']}"
        )
        asignado = await c.get(f"/api/v1/incidentes/{vis_env['incidente_a']}")
    assert sin_sector.status_code == 200
    assert en_revision.status_code == 200
    assert asignado.status_code == 404
    assert asignado.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_service_list_revision_filtra_el_conjunto_exacto(engine, vis_env):
    """El servicio con alcance REVISION devuelve exactamente sin-sector + revision."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        service = IncidenteService(session, classifier=AsyncMock())
        encontrados = await service.list_incidentes(
            alcance=AlcanceIncidentes(revision=True)
        )
    ids = {i.id for i in encontrados}
    assert ids == {
        vis_env["incidente_sin_sector"],
        vis_env["incidente_revision"],
    }
