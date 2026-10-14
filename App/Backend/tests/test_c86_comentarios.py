"""Tests de comentarios append-only (c-86, incident-comments ICM-001..003).

Cubren el alta y listado append-only (orden cronologico, sin numeracion), el
permiso derivado de la visibilidad (fuera de alcance -> 404), el formato de
presentacion `HH:MM:SS DD/MM/AAAA : {texto}` en America/Argentina/Buenos_Aires y
la ausencia de endpoints de edicion/borrado.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.exceptions import EntityNotFoundError
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, IncidenteComentario, PrioridadEnum
from app.models.user import User
from app.services.comentario_service import ComentarioService
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance
from app.utils.business_time import formatear_comentario, formatear_hilo_comentarios


# ── Formato de presentacion (ICM-003) ─────────────────────────────────────────


def test_formatear_comentario_formato_y_zona():
    """El formato es `HH:MM:SS DD/MM/AAAA : {texto}` en hora de Argentina."""
    # 12:05:03 UTC == 09:05:03 en America/Argentina/Buenos_Aires (UTC-3).
    instante = datetime(2026, 10, 14, 12, 5, 3, tzinfo=timezone.utc)
    assert formatear_comentario(instante, "hola") == "09:05:03 14/10/2026 : hola"


def test_formatear_hilo_comentarios_separador():
    """Dos o mas entradas se separan con una linea `----------`, en orden."""
    uno = (datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc), "primero")
    dos = (datetime(2026, 10, 14, 12, 5, 3, tzinfo=timezone.utc), "segundo")
    hilo = formatear_hilo_comentarios([uno, dos])
    assert hilo == (
        "09:00:00 14/10/2026 : primero\n"
        "----------\n"
        "09:05:03 14/10/2026 : segundo"
    )


# ── Servicio: alta, listado y permiso ─────────────────────────────────────────


@pytest_asyncio.fixture
async def comentarios_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([a, b, estado])
        await s.flush()

        e1_user = User(username="com-e1", hashed_password="x", is_active=True)
        e2_user = User(username="com-e2", hashed_password="x", is_active=True)
        s.add_all([e1_user, e2_user])
        await s.flush()

        e1 = Empleado(
            legajo="CE1", nombre="E1", email="ce1@example.test",
            sector_id=a.id, rol=RolEmpleado.usuario_final, user_id=e1_user.id,
        )
        e2 = Empleado(
            legajo="CE2", nombre="E2", email="ce2@example.test",
            sector_id=b.id, rol=RolEmpleado.usuario_final, user_id=e2_user.id,
        )
        s.add_all([e1, e2])
        await s.flush()

        propio = Incidente(
            descripcion_original="incidente propio",
            descripcion_pseudonimizada="incidente propio",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=a.id,
            reportante_empleado_id=e1.id,
        )
        ajeno = Incidente(
            descripcion_original="incidente ajeno",
            descripcion_pseudonimizada="incidente ajeno",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=b.id,
            reportante_empleado_id=e2.id,
        )
        s.add_all([propio, ajeno])
        await s.commit()

        ids = {
            "e1_user": e1_user.id, "e2_user": e2_user.id,
            "e1": e1.id, "e2": e2.id,
            "propio": propio.id, "ajeno": ajeno.id,
        }
    yield ids

    async with factory() as s:
        await s.execute(delete(IncidenteComentario))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


def _alcance_propio(env):
    return AlcanceIncidentes(ModoAlcance.PROPIO, reportante_empleado_id=env["e1"])


@pytest.mark.asyncio
async def test_agregar_y_listar_append_only(engine, comentarios_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = ComentarioService(s)
        actor = await s.get(Empleado, comentarios_env["e1"])
        await service.agregar(
            comentarios_env["propio"], "primero", actor, _alcance_propio(comentarios_env)
        )
        await service.agregar(
            comentarios_env["propio"], "segundo", actor, _alcance_propio(comentarios_env)
        )
        comentarios = await service.listar(
            comentarios_env["propio"], _alcance_propio(comentarios_env)
        )
        assert [c.texto for c in comentarios] == ["primero", "segundo"]
        assert all(c.created_at is not None for c in comentarios)
        await s.rollback()


@pytest.mark.asyncio
async def test_comentario_fuera_de_alcance_404(engine, comentarios_env):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = ComentarioService(s)
        with pytest.raises(EntityNotFoundError):
            await service.listar(comentarios_env["ajeno"], _alcance_propio(comentarios_env))
        with pytest.raises(EntityNotFoundError):
            await service.agregar(
                comentarios_env["ajeno"], "no permitido",
                comentarios_env["e1"], _alcance_propio(comentarios_env),
            )
        await s.rollback()


# ── API ───────────────────────────────────────────────────────────────────────


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
async def test_api_comentarios_usuario_final_propio_y_ajeno(engine, comentarios_env):
    """`usuario_final` comenta su incidente (200) y no el ajeno (404)."""
    async with _client(engine, comentarios_env["e1_user"]) as c:
        alta = await c.post(
            f"/api/v1/incidentes/{comentarios_env['propio']}/comentarios",
            json={"texto": "hola"},
        )
        listado = await c.get(
            f"/api/v1/incidentes/{comentarios_env['propio']}/comentarios"
        )
        ajeno = await c.get(
            f"/api/v1/incidentes/{comentarios_env['ajeno']}/comentarios"
        )
    assert alta.status_code == 201, alta.text
    assert listado.status_code == 200
    assert [c["texto"] for c in listado.json()] == ["hola"]
    assert ajeno.status_code == 404


@pytest.mark.asyncio
async def test_api_comentarios_anonimo_401(engine, comentarios_env):
    async with _client(engine, None) as c:
        resp = await c.get(
            f"/api/v1/incidentes/{comentarios_env['propio']}/comentarios"
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_api_no_existe_edicion_ni_borrado_de_comentarios(engine, comentarios_env):
    """No hay endpoints de edicion ni borrado de comentarios (append-only)."""
    async with _client(engine, comentarios_env["e1_user"]) as c:
        alta = await c.post(
            f"/api/v1/incidentes/{comentarios_env['propio']}/comentarios",
            json={"texto": "x"},
        )
    assert alta.status_code == 201
    comentario_id = alta.json()["id"]

    app = create_app()
    rutas = {
        (r.path, tuple(sorted(getattr(r, "methods", set()) or [])))
        for r in app.routes
    }
    assert not any(
        path.endswith(f"/comentarios/{comentario_id}") for path, _ in rutas
    )
