"""
Tests del control de acceso del directorio (c-153, Tema C, DIR-006 delta).

Cubren, en estricto RED -> GREEN -> TRIANGULATE -> REFACTOR:
    - 4.1 RED: el acceso por sujeto y la denegacion por defecto no estan
      formalizados en el registro unico de politica de rol.
    - 4.2 GREEN: la politica de lectura queda en `role_policy.py`:
      `administrador_directorio` y `mesa_de_ayuda` leen todo; `usuario_final`
      lee UNICAMENTE su propia fila; `gestion_incidentes` no lee.
    - 4.3 GREEN: limitacion de tasa y anti-enumeracion en los endpoints de
      lectura del directorio.
    - 4.4 TRIANGULATE (VIS-001/VIS-002): test NEGATIVO de aislamiento entre
      sectores: un `usuario_final` no accede a filas ajenas ni a incidentes
      fuera de su alcance.

Decision de contrato: el LISTADO es una enumeracion global del directorio y
queda reservado a los roles con lectura GLOBAL; el acceso a la PROPIA fila se
sirve por el endpoint de DETALLE (`GET /directorio/empleados/{id}`), donde el
`usuario_final` solo alcanza su id. Leer otra fila se responde 404 (no revela
existencia), coherente con el resto de la API.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

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
from app.utils.directorio_rate_limit import RateLimiterDirectorio

_ENDPOINT = "/api/v1/directorio/empleados"


@pytest_asyncio.fixture
async def acceso_env(engine):
    """Siembra sectores, cuentas/empleados por rol y dos incidentes (uno por E1)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector_a = Sector(nombre="Sistemas", descripcion="A")
        sector_b = Sector(nombre="Bases de Datos", descripcion="B")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector_a, sector_b, estado])
        await s.flush()

        admin_user = User(username="ac-admin", hashed_password="x", is_active=True)
        mesa_user = User(username="ac-mesa", hashed_password="x", is_active=True)
        e1_user = User(username="ac-e1", hashed_password="x", is_active=True)
        e2_user = User(username="ac-e2", hashed_password="x", is_active=True)
        ges_user = User(username="ac-ges", hashed_password="x", is_active=True)
        s.add_all([admin_user, mesa_user, e1_user, e2_user, ges_user])
        await s.flush()

        admin = Empleado(
            legajo="AC-ADM", nombre="Admin Sintetico", email="ac.admin@example.test",
            rol=RolEmpleado.administrador_directorio, user_id=admin_user.id,
        )
        mesa = Empleado(
            legajo="AC-MESA", nombre="Mesa Sintetica", email="ac.mesa@example.test",
            sector_id=sector_a.id, rol=RolEmpleado.mesa_de_ayuda, user_id=mesa_user.id,
        )
        e1 = Empleado(
            legajo="AC-E1", nombre="Final Uno", email="ac.e1@example.test",
            sector_id=sector_a.id, rol=RolEmpleado.usuario_final, user_id=e1_user.id,
        )
        e2 = Empleado(
            legajo="AC-E2", nombre="Final Dos", email="ac.e2@example.test",
            sector_id=sector_b.id, rol=RolEmpleado.usuario_final, user_id=e2_user.id,
        )
        ges = Empleado(
            legajo="AC-GES", nombre="Gestion", email="ac.ges@example.test",
            sector_id=sector_a.id, rol=RolEmpleado.gestion_incidentes, user_id=ges_user.id,
        )
        s.add_all([admin, mesa, e1, e2, ges])
        await s.flush()

        s.add_all(
            [
                Incidente(
                    descripcion_original="incidente propio de E1",
                    descripcion_pseudonimizada="incidente propio de E1",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_a.id,
                    reportante_empleado_id=e1.id,
                    origen_message_id="ac-propio",
                ),
                Incidente(
                    descripcion_original="incidente ajeno de E2",
                    descripcion_pseudonimizada="incidente ajeno de E2",
                    prioridad=PrioridadEnum.media,
                    estado_id=estado.id,
                    sector_id=sector_b.id,
                    reportante_empleado_id=e2.id,
                    origen_message_id="ac-ajeno",
                ),
            ]
        )
        await s.commit()
        ids = {
            "admin_user": admin_user.id,
            "mesa_user": mesa_user.id,
            "e1_user": e1_user.id,
            "e2_user": e2_user.id,
            "ges_user": ges_user.id,
            "admin_empleado": admin.id,
            "mesa_empleado": mesa.id,
            "e1_empleado": e1.id,
            "e2_empleado": e2.id,
            "ges_empleado": ges.id,
            "sector_a": sector_a.id,
            "sector_b": sector_b.id,
        }
        filas = (await s.execute(select(Incidente))).scalars().all()
        por_origen = {f.origen_message_id: f.id for f in filas}
        ids["incidente_propio"] = por_origen["ac-propio"]
        ids["incidente_ajeno"] = por_origen["ac-ajeno"]

    yield ids

    async with factory() as s:
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@asynccontextmanager
async def _client(engine, user_id: int | None, limiter: RateLimiterDirectorio | None = None):
    """Cliente ASGI; opcionalmente fija el limitador de tasa en `app.state`."""
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

    if limiter is not None:
        app.state.directorio_rate_limiter = limiter

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


# ═══════════════════════════════════════════════════════════════════════════════
# 4.1 RED — Registro unico de politica: alcance de lectura y denegacion por defecto
# ═══════════════════════════════════════════════════════════════════════════════


def test_politica_alcance_lectura_directorio_por_rol():
    """4.2: el alcance de lectura del directorio se declara por rol."""
    from app.services.role_policy import AlcanceLecturaDirectorio, alcance_lectura_directorio

    assert (
        alcance_lectura_directorio("administrador_directorio")
        is AlcanceLecturaDirectorio.GLOBAL
    )
    assert (
        alcance_lectura_directorio("mesa_de_ayuda")
        is AlcanceLecturaDirectorio.GLOBAL
    )
    assert (
        alcance_lectura_directorio("usuario_final")
        is AlcanceLecturaDirectorio.PROPIO
    )
    assert (
        alcance_lectura_directorio("gestion_incidentes")
        is AlcanceLecturaDirectorio.NINGUNO
    )


def test_politica_deniega_por_defecto():
    """4.2: un rol desconocido o nulo no obtiene alcance de lectura (NINGUNO)."""
    from app.services.role_policy import AlcanceLecturaDirectorio, alcance_lectura_directorio

    assert alcance_lectura_directorio("operador") is AlcanceLecturaDirectorio.NINGUNO
    assert alcance_lectura_directorio(None) is AlcanceLecturaDirectorio.NINGUNO


def test_politica_predicados_de_lectura():
    """4.2: predicados de lectura global y de la propia fila."""
    from app.services.role_policy import (
        puede_leer_directorio,
        puede_leer_su_propia_fila_directorio,
    )

    assert puede_leer_directorio("administrador_directorio") is True
    assert puede_leer_directorio("mesa_de_ayuda") is True
    assert puede_leer_directorio("usuario_final") is False
    assert puede_leer_directorio("gestion_incidentes") is False
    assert puede_leer_directorio("rol-inexistente") is False

    assert puede_leer_su_propia_fila_directorio("usuario_final") is True
    assert puede_leer_su_propia_fila_directorio("mesa_de_ayuda") is False
    assert puede_leer_su_propia_fila_directorio("administrador_directorio") is False
    assert puede_leer_su_propia_fila_directorio("gestion_incidentes") is False


# ═══════════════════════════════════════════════════════════════════════════════
# 4.2/4.3 — API: acceso por sujeto, anti-enumeracion y limitacion de tasa
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_usuario_final_lee_su_propia_fila(engine, acceso_env):
    """4.2: `usuario_final` accede a su propia fila (200)."""
    async with _client(engine, acceso_env["e1_user"]) as c:
        resp = await c.get(f"{_ENDPOINT}/{acceso_env['e1_empleado']}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == acceso_env["e1_empleado"]


@pytest.mark.asyncio
async def test_usuario_final_no_lee_fila_ajena_ni_revela_existencia(engine, acceso_env):
    """4.3: leer otra fila responde 404, igual que una fila inexistente."""
    async with _client(engine, acceso_env["e1_user"]) as c:
        ajeno = await c.get(f"{_ENDPOINT}/{acceso_env['e2_empleado']}")
        de_otro_sector = await c.get(f"{_ENDPOINT}/{acceso_env['mesa_empleado']}")
        inexistente = await c.get(f"{_ENDPOINT}/999999")

    assert ajeno.status_code == 404
    assert ajeno.json()["error"]["code"] == "NOT_FOUND"
    assert de_otro_sector.status_code == 404
    assert inexistente.status_code == 404
    # Misma forma de respuesta: no se distingue "ajeno" de "no existe".
    assert ajeno.json()["error"]["code"] == inexistente.json()["error"]["code"]


@pytest.mark.asyncio
async def test_usuario_final_no_lista_el_directorio(engine, acceso_env):
    """4.2: el listado es enumeracion global; `usuario_final` no lo obtiene (403)."""
    async with _client(engine, acceso_env["e1_user"]) as c:
        resp = await c.get(_ENDPOINT)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_gestion_incidentes_no_lee_el_directorio(engine, acceso_env):
    """4.2: `gestion_incidentes` no lee ni el listado ni el detalle (403)."""
    async with _client(engine, acceso_env["ges_user"]) as c:
        listado = await c.get(_ENDPOINT)
        detalle = await c.get(f"{_ENDPOINT}/{acceso_env['e1_empleado']}")
    assert listado.status_code == 403
    assert detalle.status_code == 403


@pytest.mark.asyncio
async def test_admin_y_mesa_leen_cualquier_fila(engine, acceso_env):
    """4.2 (control): los roles con lectura GLOBAL acceden a cualquier detalle."""
    for usuario in ("admin_user", "mesa_user"):
        async with _client(engine, acceso_env[usuario]) as c:
            resp = await c.get(f"{_ENDPOINT}/{acceso_env['e2_empleado']}")
        assert resp.status_code == 200, resp.text
        assert resp.json()["id"] == acceso_env["e2_empleado"]


@pytest.mark.asyncio
async def test_lectura_del_directorio_limitada_por_tasa(engine, acceso_env):
    """4.3: peticiones repetidas se acotan con 429."""
    limiter = RateLimiterDirectorio(max_peticiones=2, ventana_segundos=60)
    async with _client(engine, acceso_env["admin_user"], limiter=limiter) as c:
        primera = await c.get(_ENDPOINT)
        segunda = await c.get(_ENDPOINT)
        tercera = await c.get(_ENDPOINT)

    assert primera.status_code == 200, primera.text
    assert segunda.status_code == 200, segunda.text
    assert tercera.status_code == 429
    assert tercera.json()["error"]["code"] == "RATE_LIMITED"


# ═══════════════════════════════════════════════════════════════════════════════
# 4.4 TRIANGULATE — Aislamiento entre sectores (VIS-001/VIS-002), test NEGATIVO
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_negativo_usuario_final_aislamiento_entre_sectores(engine, acceso_env):
    """4.4: E1 no accede a filas ajenas ni a incidentes fuera de su alcance."""
    async with _client(engine, acceso_env["e1_user"]) as c:
        # Directorio: propia fila si, filas de otros sectores/roles no.
        propia = await c.get(f"{_ENDPOINT}/{acceso_env['e1_empleado']}")
        ajena_otro_final = await c.get(f"{_ENDPOINT}/{acceso_env['e2_empleado']}")
        ajena_admin = await c.get(f"{_ENDPOINT}/{acceso_env['admin_empleado']}")

        # Incidentes: reportado por E1 si, reportado por E2 (otro sector) no.
        incidente_propio = await c.get(
            f"/api/v1/incidentes/{acceso_env['incidente_propio']}"
        )
        incidente_ajeno = await c.get(
            f"/api/v1/incidentes/{acceso_env['incidente_ajeno']}"
        )

    assert propia.status_code == 200
    assert ajena_otro_final.status_code == 404
    assert ajena_admin.status_code == 404
    assert incidente_propio.status_code == 200
    assert incidente_ajeno.status_code == 404
    assert incidente_ajeno.json()["error"]["code"] == "NOT_FOUND"
