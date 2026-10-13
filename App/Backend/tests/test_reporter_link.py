"""
Tests del vinculo de reportante y su resolucion por canal (c-82, VIS-003/004/005).

Cubren:
    - Resolucion por canal: web (sesion), correo (remitente), telefonia (llamante).
    - No encontrado / ambiguo => reportante NULL, sin bloquear el alta.
    - Derivacion a revision humana cuando el reportante no se identifica (OR con
      el clasificador).

Sin PII real: dominio reservado `example.test` y telefonos sinteticos.
"""

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente
from app.models.user import User
from app.routes.incidentes import get_service as get_incidente_service
from app.schemas.clasificacion import ClasificacionResult
from app.services.incidente_service import IncidenteService

_WEB_USER_ID = 990001
_DESCRIPCION = "Falla en el servidor de base de datos principal del area contable."


def _result(confianza: float = 0.95, requiere_revision_humana: bool = False) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho="Sistemas",
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=requiere_revision_humana,
        respuesta_raw=None,
    )


@pytest_asyncio.fixture
async def reporter_env(engine, seed_catalogs):
    """Siembra una cuenta web y empleados resolubles por cada canal."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        web_user = User(
            id=_WEB_USER_ID, username="rep-web", hashed_password="x", is_active=True
        )
        s.add(web_user)
        await s.flush()

        e_web = Empleado(
            legajo="REP-WEB", nombre="Web", email="rep.web@example.test",
            rol=RolEmpleado.usuario_final, user_id=web_user.id,
        )
        e_mail = Empleado(
            legajo="REP-MAIL", nombre="Mail", email="rep.mail@example.test",
            rol=RolEmpleado.usuario_final,
        )
        e_phone = Empleado(
            legajo="REP-PHONE", nombre="Phone", email="rep.phone@example.test",
            telefono="+5491100000123", rol=RolEmpleado.usuario_final,
        )
        e_dup_1 = Empleado(
            legajo="REP-DUP-1", nombre="Dup Uno", email="rep.dup1@example.test",
            telefono="+5491100000999", rol=RolEmpleado.usuario_final,
        )
        e_dup_2 = Empleado(
            legajo="REP-DUP-2", nombre="Dup Dos", email="rep.dup2@example.test",
            telefono="+5491100000999", rol=RolEmpleado.usuario_final,
        )
        s.add_all([e_web, e_mail, e_phone, e_dup_1, e_dup_2])
        await s.commit()

        ids = {
            "web_user": web_user.id,
            "e_web": e_web.id,
            "e_mail": e_mail.id,
            "e_phone": e_phone.id,
            "canal_correo": seed_catalogs["canal_correo"].id,
            "canal_web": seed_catalogs["canal_formulario"].id,
            "canal_llamada": seed_catalogs["canal_llamada"].id,
        }

    yield ids

    async with factory() as s:
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(User).where(User.id == _WEB_USER_ID))
        await s.commit()


@asynccontextmanager
async def _client(engine, result: ClasificacionResult, user_id: int):
    """Cliente ASGI con clasificador doble y usuario autenticado configurable."""
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

    from fastapi import Depends

    async def service_override(session=Depends(get_db_session)):
        fake = AsyncMock()
        fake.classify = AsyncMock(return_value=result)
        return IncidenteService(session, classifier=fake)

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_incidente_service] = service_override

    async def override_auth():
        return User(id=user_id, username="rep-user", hashed_password="", is_active=True)

    app.dependency_overrides[get_current_user] = override_auth

    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test",
            follow_redirects=True,
        ) as ac:
            yield ac
            await asyncio.sleep(0)


def _payload(**overrides) -> dict:
    base = {"descripcion": _DESCRIPCION, "prioridad": "alta"}
    base.update(overrides)
    return base


# ── VIS-004: resolucion por canal ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_web_reportante_desde_la_sesion(engine, reporter_env):
    """Web: el reportante es el empleado de la cuenta autenticada."""
    async with _client(engine, _result(), reporter_env["web_user"]) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_web"]),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["reportante_empleado_id"] == reporter_env["e_web"]


@pytest.mark.asyncio
async def test_correo_reportante_por_remitente(engine, reporter_env):
    """Correo: el reportante es el empleado del email del remitente."""
    async with _client(engine, _result(), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(
                canal_origen_id=reporter_env["canal_correo"],
                reportante_email="rep.mail@example.test",
            ),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["reportante_empleado_id"] == reporter_env["e_mail"]


@pytest.mark.asyncio
async def test_telefonia_reportante_por_llamante(engine, reporter_env):
    """Telefonia: el reportante es el empleado del telefono del llamante."""
    async with _client(engine, _result(), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(
                canal_origen_id=reporter_env["canal_llamada"],
                reportante_telefono="+5491100000123",
            ),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["reportante_empleado_id"] == reporter_env["e_phone"]


@pytest.mark.asyncio
async def test_reportante_no_encontrado_persiste_nulo_y_no_bloquea(engine, reporter_env):
    """Correo sin coincidencia: reportante nulo, alta normal (201)."""
    async with _client(engine, _result(), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(
                canal_origen_id=reporter_env["canal_correo"],
                reportante_email="nadie@example.test",
            ),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["reportante_empleado_id"] is None


@pytest.mark.asyncio
async def test_reportante_ambiguo_no_se_elige_arbitrariamente(engine, reporter_env):
    """Telefono compartido: reportante nulo (no se elige arbitrariamente)."""
    async with _client(engine, _result(), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(
                canal_origen_id=reporter_env["canal_llamada"],
                reportante_telefono="+5491100000999",
            ),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["reportante_empleado_id"] is None


# ── VIS-003: el reportante no altera la clasificacion (TRIANGULATE) ───────────


@pytest.mark.asyncio
async def test_el_reportante_no_altera_la_clasificacion(engine, reporter_env):
    """El sector/confianza no dependen del reportante identificado."""
    async with _client(engine, _result(confianza=0.88), reporter_env["web_user"]) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_web"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["sector"]["nombre"] == "Sistemas"
    assert body["reportante_empleado_id"] == reporter_env["e_web"]


# ── VIS-005: derivacion a revision humana por reportante no identificado ──────


@pytest.mark.asyncio
async def test_sin_contacto_de_canal_deriva_a_revision(engine, reporter_env):
    """Correo sin contacto del remitente => reportante NULL y revision True."""
    async with _client(engine, _result(confianza=0.95), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_correo"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["reportante_empleado_id"] is None
    assert body["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_contacto_no_resoluble_deriva_a_revision(engine, reporter_env):
    """Contacto de canal que no resuelve => revision True."""
    async with _client(engine, _result(confianza=0.95), 12345) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(
                canal_origen_id=reporter_env["canal_correo"],
                reportante_email="fantasma@example.test",
            ),
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_cuenta_web_sin_empleado_deriva_a_revision(engine, reporter_env):
    """Cuenta web sin empleado vinculado => revision True."""
    async with _client(engine, _result(confianza=0.95), 424242) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_web"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["reportante_empleado_id"] is None
    assert body["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_la_derivacion_no_quita_una_revision_ya_marcada(engine, reporter_env):
    """El OR preserva una revision marcada por el clasificador."""
    async with _client(
        engine, _result(confianza=0.4, requiere_revision_humana=True),
        reporter_env["web_user"],
    ) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_web"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["reportante_empleado_id"] == reporter_env["e_web"]
    assert body["requiere_revision_humana"] is True


@pytest.mark.asyncio
async def test_reportante_identificado_no_fuerza_revision(engine, reporter_env):
    """Reportante identificado + clasificador sin revision => revision False."""
    async with _client(engine, _result(confianza=0.95), reporter_env["web_user"]) as c:
        resp = await c.post(
            "/api/v1/incidentes/",
            json=_payload(canal_origen_id=reporter_env["canal_web"]),
        )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["reportante_empleado_id"] == reporter_env["e_web"]
    assert body["requiere_revision_humana"] is False
