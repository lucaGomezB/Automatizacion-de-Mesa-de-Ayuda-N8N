"""Tests del ciclo de cierre de incidentes (c-86, ILC-001/002/003).

Cubren el cierre por sector (idempotente, con actor, saca de la vista activa), el
cierre global (todos los sectores + estado terminal, incluido el incidente sin
sector) y la transicion terminal (todos los sectores cerrados -> `cerrado`), en
estricto RED->GREEN->TRIANGULATE.
"""

from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.exceptions import PermisoDenegadoError
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import (
    Incidente,
    IncidenteCierreSector,
    IncidenteEvento,
    PrioridadEnum,
)
from app.models.user import User
from app.repositories.incidente_repository import IncidenteRepository
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance
from app.services.ciclo_incidente_service import CicloIncidenteService


@pytest_asyncio.fixture
async def ciclo_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        e_nuevo = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        e_proceso = Estado(nombre="en proceso", descripcion="p", es_terminal=False)
        e_espera = Estado(nombre="en espera", descripcion="e", es_terminal=False)
        e_resuelto = Estado(nombre="resuelto", descripcion="r", es_terminal=False)
        e_cerrado = Estado(nombre="cerrado", descripcion="c", es_terminal=True)
        s.add_all([a, b, e_nuevo, e_proceso, e_espera, e_resuelto, e_cerrado])
        await s.flush()

        actor_a = Empleado(
            legajo="GA", nombre="Gestion A", email="ga@example.test",
            sector_id=a.id, rol=RolEmpleado.gestion_incidentes,
        )
        actor_b = Empleado(
            legajo="GB", nombre="Gestion B", email="gb@example.test",
            sector_id=b.id, rol=RolEmpleado.gestion_incidentes,
        )
        mesa = Empleado(
            legajo="MDA", nombre="Mesa", email="mda@example.test",
            sector_id=None, rol=RolEmpleado.mesa_de_ayuda,
        )
        final = Empleado(
            legajo="UF", nombre="Final", email="uf@example.test",
            sector_id=None, rol=RolEmpleado.usuario_final,
        )
        s.add_all([actor_a, actor_b, mesa, final])
        await s.flush()

        base = dict(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
            estado_id=e_nuevo.id,
        )
        solo_a = Incidente(**base, sector_id=a.id)
        multi = Incidente(**base, sector_id=b.id, sectores_adicionales=[a])
        sin_sector = Incidente(**base, sector_id=None)
        s.add_all([solo_a, multi, sin_sector])
        await s.commit()

        ids = {
            "sector_a": a.id, "sector_b": b.id,
            "actor_a": actor_a.id, "actor_b": actor_b.id,
            "mesa": mesa.id, "final": final.id,
            "e_cerrado": e_cerrado.id,
        }
        for nombre, obj in (("solo_a", solo_a), ("multi", multi), ("sin_sector", sin_sector)):
            ids[nombre] = obj.id
        ids["actor_a_obj"] = actor_a
        ids["actor_b_obj"] = actor_b
        ids["mesa_obj"] = mesa
        ids["final_obj"] = final

    yield ids

    async with factory() as s:
        await s.execute(delete(IncidenteEvento))
        await s.execute(delete(IncidenteCierreSector))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


def _alcance(env, sector_key="sector_a"):
    return AlcanceIncidentes(ModoAlcance.SECTOR, sector_id=env[sector_key])


@pytest.mark.asyncio
async def test_cierre_por_sector_registra_actor_y_fecha(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_sector(
            ciclo_env["solo_a"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        fila = (
            await s.execute(
                select(IncidenteCierreSector).where(
                    IncidenteCierreSector.incidente_id == ciclo_env["solo_a"]
                )
            )
        ).scalar_one()
        assert fila.sector_id == ciclo_env["sector_a"]
        assert fila.cerrado_por == ciclo_env["actor_a"]
        assert fila.cerrado_en is not None
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_por_sector_idempotente(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        filas = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteCierreSector)
                .where(IncidenteCierreSector.incidente_id == ciclo_env["multi"])
            )
        ).scalar_one()
        eventos = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteEvento)
                .where(
                    IncidenteEvento.incidente_id == ciclo_env["multi"],
                    IncidenteEvento.tipo == "cierre_sector",
                )
            )
        ).scalar_one()
        assert filas == 1
        assert eventos == 1
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_por_sector_saca_de_la_vista_activa(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        repo = IncidenteRepository(s)
        vista_a = {
            i.id
            for i in await repo.list_filtered(
                sector_scope_id=ciclo_env["sector_a"], limit=100
            )
        }
        assert ciclo_env["multi"] not in vista_a
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_parcial_no_es_terminal(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        incidente = await s.get(Incidente, ciclo_env["multi"])
        assert incidente.estado_id != ciclo_env["e_cerrado"]
        await s.rollback()


@pytest.mark.asyncio
async def test_ultimo_sector_transiciona_a_cerrado(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        # solo_a tiene un unico sector (A): su cierre lo lleva a terminal.
        await service.cerrar_sector(
            ciclo_env["solo_a"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        incidente = await s.get(Incidente, ciclo_env["solo_a"])
        assert incidente.estado_id == ciclo_env["e_cerrado"]
        await s.rollback()


@pytest.mark.asyncio
async def test_multi_sector_cierra_ambos_y_terminal(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        await service.cerrar_sector(
            ciclo_env["multi"], ciclo_env["actor_b_obj"], _alcance(ciclo_env, "sector_b")
        )
        incidente = await s.get(Incidente, ciclo_env["multi"])
        assert incidente.estado_id == ciclo_env["e_cerrado"]
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_global_cierra_todos_los_sectores(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_global(ciclo_env["multi"], ciclo_env["mesa_obj"])
        sectores = {
            c.sector_id
            for c in (
                await s.execute(
                    select(IncidenteCierreSector).where(
                        IncidenteCierreSector.incidente_id == ciclo_env["multi"]
                    )
                )
            ).scalars().all()
        }
        assert sectores == {ciclo_env["sector_a"], ciclo_env["sector_b"]}
        incidente = await s.get(Incidente, ciclo_env["multi"])
        assert incidente.estado_id == ciclo_env["e_cerrado"]
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_global_incidente_sin_sector(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_global(ciclo_env["sin_sector"], ciclo_env["mesa_obj"])
        incidente = await s.get(Incidente, ciclo_env["sin_sector"])
        assert incidente.estado_id == ciclo_env["e_cerrado"]
        filas = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteCierreSector)
                .where(IncidenteCierreSector.incidente_id == ciclo_env["sin_sector"])
            )
        ).scalar_one()
        assert filas == 0
        await s.rollback()


@pytest.mark.asyncio
async def test_cierre_global_idempotente(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_global(ciclo_env["multi"], ciclo_env["mesa_obj"])
        await service.cerrar_global(ciclo_env["multi"], ciclo_env["mesa_obj"])
        eventos = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteEvento)
                .where(
                    IncidenteEvento.incidente_id == ciclo_env["multi"],
                    IncidenteEvento.tipo == "cierre_global",
                )
            )
        ).scalar_one()
        assert eventos == 1
        await s.rollback()


@pytest.mark.asyncio
async def test_permiso_denegado_sin_permiso_de_cierre(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        with pytest.raises(PermisoDenegadoError):
            await service.cerrar_sector(
                ciclo_env["solo_a"],
                ciclo_env["final_obj"],
                _alcance(ciclo_env),
            )
        with pytest.raises(PermisoDenegadoError):
            await service.cerrar_global(ciclo_env["multi"], ciclo_env["final_obj"])
        await s.rollback()


@pytest.mark.asyncio
async def test_gestion_no_cierra_fuera_de_su_alcance(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        from app.core.exceptions import EntityNotFoundError

        with pytest.raises(EntityNotFoundError):
            # actor_b (sector B) intenta cerrar solo_a (solo sector A).
            await service.cerrar_sector(
                ciclo_env["solo_a"],
                ciclo_env["actor_b_obj"],
                _alcance(ciclo_env, "sector_b"),
            )
        await s.rollback()


# ── API: autorizacion del ciclo de cierre ─────────────────────────────────────


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


@pytest.mark.asyncio
async def test_api_gestion_no_cierra_global(engine, ciclo_env):
    """`gestion_incidentes` no puede cerrar globalmente (403)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="ga-user", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = await s.get(Empleado, ciclo_env["actor_a"])
        emp.user_id = user.id
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        resp = await c.post(f"/api/v1/incidentes/{ciclo_env['multi']}/cierre-global")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_api_mesa_cierra_global(engine, ciclo_env):
    """`mesa_de_ayuda` cierra globalmente (200) y deja el incidente cerrado."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="mda-user", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = await s.get(Empleado, ciclo_env["mesa"])
        emp.user_id = user.id
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        resp = await c.post(f"/api/v1/incidentes/{ciclo_env['multi']}/cierre-global")
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"]["nombre"] == "cerrado"


@pytest.mark.asyncio
async def test_api_gestion_fuera_de_sector_404(engine, ciclo_env):
    """`gestion` de B no cierra un incidente solo de A (404)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="gb-user", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = await s.get(Empleado, ciclo_env["actor_b"])
        emp.user_id = user.id
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        resp = await c.post(f"/api/v1/incidentes/{ciclo_env['solo_a']}/cierre-sector")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_api_anonimo_401(engine, ciclo_env):
    """Sin autenticacion, el cierre responde 401."""
    async with _client(engine, None) as c:
        resp = await c.post(f"/api/v1/incidentes/{ciclo_env['solo_a']}/cierre-sector")
    assert resp.status_code == 401


# ── Reapertura (ILC-004) y edicion de estado (ILC-005) ────────────────────────


@pytest.mark.asyncio
async def test_rehabilitar_limpia_cierres_y_vuelve_a_en_proceso(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_global(ciclo_env["multi"], ciclo_env["mesa_obj"])
        incidente = await service.rehabilitar(
            ciclo_env["multi"], ciclo_env["mesa_obj"]
        )
        assert incidente.estado.nombre == "en proceso"
        filas = (
            await s.execute(
                select(func.count())
                .select_from(IncidenteCierreSector)
                .where(IncidenteCierreSector.incidente_id == ciclo_env["multi"])
            )
        ).scalar_one()
        assert filas == 0
        evento = (
            await s.execute(
                select(IncidenteEvento).where(
                    IncidenteEvento.incidente_id == ciclo_env["multi"],
                    IncidenteEvento.tipo == "reapertura",
                )
            )
        ).scalar_one()
        assert evento.estado_anterior == "cerrado"
        assert evento.estado_nuevo == "en proceso"
        await s.rollback()


@pytest.mark.asyncio
async def test_rehabilitar_rechaza_no_cerrado(engine, ciclo_env):
    """Reabrir un incidente no cerrado se rechaza."""
    from app.core.exceptions import IncidentValidationError

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        with pytest.raises(IncidentValidationError):
            await service.rehabilitar(ciclo_env["solo_a"], ciclo_env["mesa_obj"])
        await s.rollback()


@pytest.mark.asyncio
async def test_rehabilitar_solo_mesa(engine, ciclo_env):
    """Un rol sin `reabre` no puede rehabilitar (403) y no muta nada."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        with pytest.raises(PermisoDenegadoError):
            await service.rehabilitar(ciclo_env["multi"], ciclo_env["actor_a_obj"])
        await s.rollback()


@pytest.mark.asyncio
async def test_rehabilitar_devuelve_a_la_vista_activa(engine, ciclo_env):
    """Tras reabrir, el incidente vuelve a la vista activa del sector."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        await service.cerrar_global(ciclo_env["multi"], ciclo_env["mesa_obj"])
        repo = IncidenteRepository(s)
        antes = {
            i.id
            for i in await repo.list_filtered(
                sector_scope_id=ciclo_env["sector_a"], limit=100
            )
        }
        assert ciclo_env["multi"] not in antes
        await service.rehabilitar(ciclo_env["multi"], ciclo_env["mesa_obj"])
        despues = {
            i.id
            for i in await repo.list_filtered(
                sector_scope_id=ciclo_env["sector_a"], limit=100
            )
        }
        assert ciclo_env["multi"] in despues
        await s.rollback()


@pytest.mark.asyncio
async def test_editar_estado_actualiza_y_registra_evento(engine, ciclo_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        incidente = await service.editar_estado(
            ciclo_env["solo_a"], "en espera", ciclo_env["actor_a_obj"], _alcance(ciclo_env)
        )
        assert incidente.estado.nombre == "en espera"
        evento = (
            await s.execute(
                select(IncidenteEvento).where(
                    IncidenteEvento.incidente_id == ciclo_env["solo_a"],
                    IncidenteEvento.tipo == "cambio_estado",
                )
            )
        ).scalar_one()
        assert evento.estado_nuevo == "en espera"
        await s.rollback()


@pytest.mark.asyncio
async def test_editar_estado_cerrado_rechazado(engine, ciclo_env):
    """`cerrado` no se acepta en la edicion de estado (ILC-005)."""
    from app.core.exceptions import IncidentValidationError

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        with pytest.raises(IncidentValidationError):
            await service.editar_estado(
                ciclo_env["solo_a"], "cerrado", ciclo_env["actor_a_obj"], _alcance(ciclo_env)
            )
        await s.rollback()


@pytest.mark.asyncio
async def test_editar_estado_rol_no_editor(engine, ciclo_env):
    """`usuario_final` y admin no editan el estado (403)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = CicloIncidenteService(s)
        with pytest.raises(PermisoDenegadoError):
            await service.editar_estado(
                ciclo_env["solo_a"], "resuelto", ciclo_env["final_obj"], _alcance(ciclo_env)
            )
        await s.rollback()


@pytest.mark.asyncio
async def test_api_patch_estado_y_rehabilitar(engine, ciclo_env):
    """API: mesa edita estado (200), `cerrado` (422), reabre (200)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="mda-user2", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = await s.get(Empleado, ciclo_env["mesa"])
        emp.user_id = user.id
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        r1 = await c.patch(
            f"/api/v1/incidentes/{ciclo_env['multi']}/estado", json={"estado": "resuelto"}
        )
        r2 = await c.patch(
            f"/api/v1/incidentes/{ciclo_env['multi']}/estado", json={"estado": "cerrado"}
        )
        cierre = await c.post(f"/api/v1/incidentes/{ciclo_env['multi']}/cierre-global")
        reabrir = await c.post(f"/api/v1/incidentes/{ciclo_env['multi']}/rehabilitar")
    assert r1.status_code == 200, r1.text
    assert r1.json()["estado"]["nombre"] == "resuelto"
    assert r2.status_code == 422
    assert cierre.status_code == 200
    assert reabrir.status_code == 200, reabrir.text
    assert reabrir.json()["estado"]["nombre"] == "en proceso"


@pytest.mark.asyncio
async def test_api_gestion_no_reabre(engine, ciclo_env):
    """`gestion_incidentes` no reabre (403)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        user = User(username="ga-user2", hashed_password="x", is_active=True)
        s.add(user)
        await s.flush()
        emp = await s.get(Empleado, ciclo_env["actor_a"])
        emp.user_id = user.id
        await s.commit()
        uid = user.id

    async with _client(engine, uid) as c:
        resp = await c.post(f"/api/v1/incidentes/{ciclo_env['multi']}/rehabilitar")
    assert resp.status_code == 403
