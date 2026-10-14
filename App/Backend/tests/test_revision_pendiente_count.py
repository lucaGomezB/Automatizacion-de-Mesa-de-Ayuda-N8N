"""
Tests del conteo de la cola de revision pendiente (c-85, VIS-006 / FRH-008).

Cubre las tres capas del recurso de conteo:
    Repositorio  — `ClasificacionRepository.count_pending_review` usa EXACTAMENTE
                   los mismos filtros de "pendiente" que `list_pending_review`
                   (`requiere_revision_humana == True` Y `sector_id_validado IS NULL`),
                   con el filtro opcional por reportante del incidente.
    Servicio     — `ClasificacionService.count_pending_review(alcance)` reutiliza la
                   derivacion de alcance del listado (D4): GLOBAL -> cola completa,
                   PROPIO -> solo lo reportado, VACIO -> 0 sin tocar el repositorio.
    API          — `GET /api/v1/clasificaciones/revision-pendiente/count` responde
                   `{"total": N}` y coincide con el listado sin paginar.

La suite es OFFLINE (SQLite en memoria); no contacta Gemini ni N8N.
"""

import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.main import create_app
from app.repositories.clasificacion_repository import ClasificacionRepository
from app.schemas.clasificacion import ClasificacionResult
from app.services.clasificacion_service import ClasificacionService
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance


# ── Fixture comun: mezcla de filas pendientes y no pendientes ────────────────


@pytest_asyncio.fixture
async def count_env(db_session):
    """Siembra dos reportantes y una mezcla de logs pendientes/no pendientes.

    Poblacion:
        - log_e1_pend       → reportante E1, revision=True,  validado=None  CUENTA
        - log_e2_pend       → reportante E2, revision=True,  validado=None  CUENTA
        - log_e1_validado   → reportante E1, revision=True,  validado=Sector CUENTA=NO
        - log_e1_alta       → reportante E1, revision=False, validado=None  CUENTA=NO

    Totales esperados: global=2, E1=1, E2=1, desconocido=0.
    """
    from app.models.catalog import Estado, Sector
    from app.models.clasificacion_log import ClasificacionLog
    from app.models.empleado import Empleado, RolEmpleado
    from app.models.incidente import Incidente, PrioridadEnum
    from app.models.user import User

    sector_a = Sector(nombre="Sistemas", descripcion="Infraestructura")
    sector_b = Sector(nombre="Bases de Datos", descripcion="Motores")
    estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
    db_session.add_all([sector_a, sector_b, estado])
    await db_session.flush()

    user_e1 = User(username="cnt-e1", hashed_password="x", is_active=True)
    user_e2 = User(username="cnt-e2", hashed_password="x", is_active=True)
    db_session.add_all([user_e1, user_e2])
    await db_session.flush()

    e1 = Empleado(
        legajo="CNT-E1", nombre="Reportante E1", email="cnt.e1@example.test",
        rol=RolEmpleado.usuario_final, user_id=user_e1.id, sector_id=sector_a.id,
    )
    e2 = Empleado(
        legajo="CNT-E2", nombre="Reportante E2", email="cnt.e2@example.test",
        rol=RolEmpleado.usuario_final, user_id=user_e2.id, sector_id=sector_b.id,
    )
    db_session.add_all([e1, e2])
    await db_session.flush()

    def _incidente(reportante_id: int, revision: bool) -> Incidente:
        return Incidente(
            descripcion_original="caso de conteo",
            descripcion_pseudonimizada="caso de conteo",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector_a.id,
            reportante_empleado_id=reportante_id,
            requiere_revision_humana=revision,
        )

    inc_e1 = _incidente(e1.id, True)
    inc_e2 = _incidente(e2.id, True)
    inc_e1_plain = _incidente(e1.id, False)
    db_session.add_all([inc_e1, inc_e2, inc_e1_plain])
    await db_session.flush()

    log_e1_pend = ClasificacionLog(
        incidente_id=inc_e1.id, sector_id_predicho=sector_a.id, confianza=0.55,
        etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
    )
    log_e2_pend = ClasificacionLog(
        incidente_id=inc_e2.id, sector_id_predicho=sector_b.id, confianza=0.55,
        etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
    )
    log_e1_validado = ClasificacionLog(
        incidente_id=inc_e1.id, sector_id_predicho=sector_a.id, confianza=0.55,
        etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        sector_id_validado=sector_a.id,
    )
    log_e1_alta = ClasificacionLog(
        incidente_id=inc_e1_plain.id, sector_id_predicho=sector_a.id, confianza=0.95,
        etapa="deterministic", requiere_revision_humana=False, respuesta_raw=None,
    )
    db_session.add_all([log_e1_pend, log_e2_pend, log_e1_validado, log_e1_alta])
    await db_session.flush()

    return {"e1_id": e1.id, "e2_id": e2.id}


# ═══════════════════════════════════════════════════════════════════════════════
# Repositorio: ClasificacionRepository.count_pending_review
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_count_pending_review_cuenta_solo_pendientes(db_session, count_env):
    """RED/GREEN — solo cuenta los logs con revision=True y sin validar.

    Excluye la fila ya validada y la de alta confianza (revision=False).
    """
    repo = ClasificacionRepository(db_session)

    total = await repo.count_pending_review(reportante_empleado_id=None)

    assert total == 2


@pytest.mark.asyncio
async def test_count_pending_review_respeta_filtro_reportante(db_session, count_env):
    """TRIANGULATE — el filtro por reportante acota el conteo a un empleado."""
    repo = ClasificacionRepository(db_session)

    total_e1 = await repo.count_pending_review(
        reportante_empleado_id=count_env["e1_id"]
    )
    total_e2 = await repo.count_pending_review(
        reportante_empleado_id=count_env["e2_id"]
    )
    total_otro = await repo.count_pending_review(reportante_empleado_id=999999)

    assert total_e1 == 1
    assert total_e2 == 1
    assert total_otro == 0


@pytest.mark.asyncio
async def test_count_pending_review_coincide_con_listado(db_session, count_env):
    """TRIANGULATE (VIS-006) — el conteo == len(listado sin paginar) por alcance."""
    repo = ClasificacionRepository(db_session)

    for reportante in (None, count_env["e1_id"], count_env["e2_id"]):
        total = await repo.count_pending_review(reportante_empleado_id=reportante)
        listado = await repo.list_pending_review(
            limit=500, offset=0, reportante_empleado_id=reportante
        )
        assert total == len(listado)


# ═══════════════════════════════════════════════════════════════════════════════
# Servicio: ClasificacionService.count_pending_review(alcance)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_service_count_global_devuelve_cola_completa(db_session, count_env):
    """RED/GREEN — alcance GLOBAL cuenta toda la cola."""
    service = ClasificacionService(db_session)

    total = await service.count_pending_review(
        AlcanceIncidentes(ModoAlcance.GLOBAL)
    )

    assert total == 2


@pytest.mark.asyncio
async def test_service_count_propio_solo_del_reportante(db_session, count_env):
    """TRIANGULATE — alcance PROPIO cuenta solo lo reportado por el empleado."""
    service = ClasificacionService(db_session)

    total = await service.count_pending_review(
        AlcanceIncidentes(ModoAlcance.PROPIO, count_env["e1_id"])
    )

    assert total == 1


@pytest.mark.asyncio
async def test_service_count_vacio_es_cero_sin_tocar_repositorio(db_session):
    """TRIANGULATE — alcance VACIO devuelve 0 SIN consultar el repositorio."""
    service = ClasificacionService(db_session)
    # Espia: si el servicio consulta el repositorio, el test falla.
    service._repo.count_pending_review = AsyncMock(
        side_effect=AssertionError("VACIO no debe tocar el repositorio")
    )

    total = await service.count_pending_review(AlcanceIncidentes(ModoAlcance.VACIO))

    assert total == 0
    service._repo.count_pending_review.assert_not_called()


@pytest.mark.asyncio
async def test_service_count_coincide_con_list_pending_review(db_session, count_env):
    """TRIANGULATE — el conteo y el listado del servicio coinciden por alcance.

    De paso verifica que la extraccion del helper de alcance (D4) no altero el
    comportamiento de list_pending_review.
    """
    service = ClasificacionService(db_session)

    for alcance in (
        AlcanceIncidentes(ModoAlcance.GLOBAL),
        AlcanceIncidentes(ModoAlcance.PROPIO, count_env["e1_id"]),
        AlcanceIncidentes(ModoAlcance.PROPIO, count_env["e2_id"]),
        AlcanceIncidentes(ModoAlcance.VACIO),
    ):
        total = await service.count_pending_review(alcance)
        listado = await service.list_pending_review(limit=500, offset=0, alcance=alcance)
        assert total == len(listado)


# ═══════════════════════════════════════════════════════════════════════════════
# API: GET /api/v1/clasificaciones/revision-pendiente/count
# ═══════════════════════════════════════════════════════════════════════════════


def _result_pendiente(sector: str = "Sistemas") -> ClasificacionResult:
    """Clasificacion de baja confianza → el incidente entra en la cola."""
    return ClasificacionResult(
        sector_predicho=sector,
        confianza=0.55,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw='{"sector_predicho": "Sistemas", "confianza": 0.55}',
    )


async def _crear_pendientes(client: AsyncClient, cantidad: int) -> None:
    """Crea `cantidad` incidentes pendientes via la API (clasificador doble)."""
    for i in range(cantidad):
        await client.post(
            "/api/v1/incidentes/",
            json={
                "descripcion": f"Servidor de base de datos {i} no responde desde las 08:00.",
                "prioridad": "media",
            },
        )


@asynccontextmanager
async def _anon_client(engine):
    """Cliente sin autenticacion: solo se sustituye la base de datos."""
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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_api_count_coincide_con_listado_sin_paginar(
    seed_catalogs, make_client_with_classifier
):
    """RED/GREEN — GET .../count responde {"total": N} == len(listado sin paginar)."""
    async with make_client_with_classifier(_result_pendiente()) as c:
        await _crear_pendientes(c, 3)

        count_resp = await c.get("/api/v1/clasificaciones/revision-pendiente/count")
        listado_resp = await c.get(
            "/api/v1/clasificaciones/revision-pendiente", params={"limit": 200}
        )

    assert count_resp.status_code == 200, count_resp.text
    assert count_resp.json() == {"total": 3}
    assert count_resp.json()["total"] == len(listado_resp.json())


@pytest.mark.asyncio
async def test_api_count_no_se_topea_al_tamano_de_pagina(
    seed_catalogs, make_client_with_classifier
):
    """TRIANGULATE — con >50 pendientes el total no queda acotado a 50."""
    async with make_client_with_classifier(_result_pendiente()) as c:
        await _crear_pendientes(c, 51)

        count_resp = await c.get("/api/v1/clasificaciones/revision-pendiente/count")
        listado_default = await c.get("/api/v1/clasificaciones/revision-pendiente")

    assert count_resp.status_code == 200, count_resp.text
    assert count_resp.json()["total"] == 51
    # El listado SIN params sigue topeado a 50: el conteo es su complemento exacto.
    assert len(listado_default.json()) == 50


@pytest.mark.asyncio
async def test_api_count_anonimo_401(engine, seed_catalogs):
    """TRIANGULATE — sin autenticacion el conteo responde 401."""
    async with _anon_client(engine) as c:
        resp = await c.get("/api/v1/clasificaciones/revision-pendiente/count")
    assert resp.status_code == 401
