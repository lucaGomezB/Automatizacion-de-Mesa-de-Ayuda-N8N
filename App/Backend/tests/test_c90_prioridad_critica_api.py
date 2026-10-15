"""Tests de API del guard de prioridad critica (c-90, RP-006).

Cubren, en la capa HTTP y con la derivacion REAL de rol (via `directorio_empleado`):
    - `mesa_de_ayuda` y `administrador_directorio` crean/editan con `critica` (201/200).
    - Un rol sin permiso que envia `critica` en el alta recibe 403 y NO persiste.
    - Un rol sin permiso que intenta fijar `critica` en la edicion recibe 403 sin
      modificar la fila.
    - Las prioridades `baja|media|alta` siguen sin restriccion.
    - Un PATCH que NO toca `prioridad` sobre un incidente ya `critica` es aceptado (D3).
    - Un llamante no interactivo sin permiso que envia `critica` recibe 403 (D5) y el
      envelope es el estandar FORBIDDEN de core/error_handlers.py.
"""

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import Estado, Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.models.user import User
from app.routes.incidentes import get_service as get_incidente_service
from app.schemas.clasificacion import ClasificacionResult
from app.services.incidente_service import IncidenteService

DESCRIPCION = "El servidor de base de datos principal no responde desde esta manana."


def _result() -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho="Sistemas",
        confianza=0.95,
        etapa="deterministic",
        requiere_revision_humana=False,
        respuesta_raw=None,
    )


@pytest_asyncio.fixture
async def c90_api_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="Sistemas", descripcion="A")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector, estado])
        await s.flush()

        u_mesa = User(username="c90-mesa", hashed_password="x", is_active=True)
        u_admin = User(username="c90-admin", hashed_password="x", is_active=True)
        u_final = User(username="c90-final", hashed_password="x", is_active=True)
        u_gestion = User(username="c90-gestion", hashed_password="x", is_active=True)
        u_norol = User(username="c90-norol", hashed_password="x", is_active=True)
        s.add_all([u_mesa, u_admin, u_final, u_gestion, u_norol])
        await s.flush()

        e_mesa = Empleado(
            legajo="C90-MESA", nombre="Mesa", email="c90.mesa@example.test",
            sector_id=sector.id, rol=RolEmpleado.mesa_de_ayuda, user_id=u_mesa.id,
        )
        e_admin = Empleado(
            legajo="C90-ADM", nombre="Admin", email="c90.admin@example.test",
            sector_id=sector.id, rol=RolEmpleado.administrador_directorio,
            user_id=u_admin.id,
        )
        e_final = Empleado(
            legajo="C90-FIN", nombre="Final", email="c90.final@example.test",
            sector_id=sector.id, rol=RolEmpleado.usuario_final, user_id=u_final.id,
        )
        e_gestion = Empleado(
            legajo="C90-GES", nombre="Gestion", email="c90.gestion@example.test",
            sector_id=sector.id, rol=RolEmpleado.gestion_incidentes,
            user_id=u_gestion.id,
        )
        s.add_all([e_mesa, e_admin, e_final, e_gestion])
        await s.flush()

        base = dict(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            estado_id=estado.id,
            sector_id=sector.id,
        )
        i_media = Incidente(**base, prioridad=PrioridadEnum.media, origen_message_id="c90-media")
        i_critica = Incidente(
            **base, prioridad=PrioridadEnum.critica, origen_message_id="c90-critica"
        )
        s.add_all([i_media, i_critica])
        await s.commit()

        ids = {
            "u_mesa": u_mesa.id,
            "u_admin": u_admin.id,
            "u_final": u_final.id,
            "u_gestion": u_gestion.id,
            "u_norol": u_norol.id,
            "i_media": i_media.id,
            "i_critica": i_critica.id,
        }
    yield ids

    async with factory() as s:
        from app.models.asociaciones import (
            clasificacion_sector_predicho,
            clasificacion_sector_validado,
            incidente_sector_adicional,
        )
        from app.models.clasificacion_log import ClasificacionLog

        await s.execute(delete(clasificacion_sector_predicho))
        await s.execute(delete(clasificacion_sector_validado))
        await s.execute(delete(incidente_sector_adicional))
        await s.execute(delete(ClasificacionLog))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@asynccontextmanager
async def _client(engine, user_id: int | None, result: ClasificacionResult | None = None):
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
    if result is not None:
        async def _service_override(session: AsyncSession = Depends(get_db_session)):
            fake = AsyncMock()
            fake.classify = AsyncMock(return_value=result)
            return IncidenteService(session, classifier=fake)
        app.dependency_overrides[get_incidente_service] = _service_override

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
            await asyncio.sleep(0)


async def _leer_incidente(engine, incidente_id: int) -> Incidente | None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        return await s.get(Incidente, incidente_id)


async def _contar_incidentes(engine) -> int:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        return await s.scalar(select(func.count()).select_from(Incidente))


# ── Roles autorizados: `critica` aceptada ──────────────────────────────────────


@pytest.mark.asyncio
async def test_mesa_de_ayuda_crea_con_critica(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_mesa"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "critica"}
        )

    assert resp.status_code == 201, resp.text
    assert resp.json()["prioridad"] == "critica"


@pytest.mark.asyncio
async def test_administrador_directorio_crea_con_critica(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_admin"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "critica"}
        )

    assert resp.status_code == 201, resp.text
    assert resp.json()["prioridad"] == "critica"


@pytest.mark.asyncio
async def test_mesa_de_ayuda_edita_a_critica(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_mesa"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{c90_api_env['i_media']}", json={"prioridad": "critica"}
        )

    assert resp.status_code == 200, resp.text
    assert resp.json()["prioridad"] == "critica"
    fila = await _leer_incidente(engine, c90_api_env["i_media"])
    assert fila.prioridad == PrioridadEnum.critica


# ── Roles sin permiso: `critica` rechazada (403) ───────────────────────────────


@pytest.mark.asyncio
async def test_usuario_final_critica_en_alta_403_y_no_persiste(engine, c90_api_env):
    antes = await _contar_incidentes(engine)
    async with _client(engine, c90_api_env["u_final"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "critica"}
        )

    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["code"] == "FORBIDDEN"
    assert (await _contar_incidentes(engine)) == antes


@pytest.mark.asyncio
async def test_gestion_incidentes_critica_en_edicion_403_sin_cambios(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_gestion"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{c90_api_env['i_media']}", json={"prioridad": "critica"}
        )

    assert resp.status_code == 403, resp.text
    fila = await _leer_incidente(engine, c90_api_env["i_media"])
    assert fila.prioridad == PrioridadEnum.media


@pytest.mark.asyncio
async def test_usuario_final_critica_en_edicion_403(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_final"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{c90_api_env['i_media']}", json={"prioridad": "critica"}
        )

    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["code"] == "FORBIDDEN"


# ── Prioridades no criticas: sin restriccion ───────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize("prioridad", ["baja", "media", "alta"])
async def test_usuario_final_prioridad_no_critica_aceptada(engine, c90_api_env, prioridad):
    async with _client(engine, c90_api_env["u_final"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": prioridad}
        )

    assert resp.status_code == 201, resp.text
    assert resp.json()["prioridad"] == prioridad


@pytest.mark.asyncio
async def test_patch_sin_tocar_prioridad_sobre_critica_aceptado(engine, c90_api_env):
    """D3: un PATCH que no pide `critica` no dispara el guard aunque ya sea critica."""
    async with _client(engine, c90_api_env["u_gestion"]) as c:
        resp = await c.patch(
            f"/api/v1/incidentes/{c90_api_env['i_critica']}",
            json={"requiere_revision_humana": True},
        )

    assert resp.status_code == 200, resp.text
    assert resp.json()["prioridad"] == "critica"


# ── Llamante no interactivo sin permiso (D5) ───────────────────────────────────


@pytest.mark.asyncio
async def test_llamante_sin_empleado_critica_403(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_norol"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "critica"}
        )

    assert resp.status_code == 403, resp.text
    assert resp.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_llamante_sin_empleado_prioridad_media_inalterada(engine, c90_api_env):
    async with _client(engine, c90_api_env["u_norol"], _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "media"}
        )

    assert resp.status_code == 201, resp.text


# ── Sin autenticacion ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_anonimo_critica_401_no_403(engine, c90_api_env):
    """Sin token la autenticacion precede al guard: 401, no 403."""
    async with _client(engine, None, _result()) as c:
        resp = await c.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "critica"}
        )

    assert resp.status_code == 401, resp.text
