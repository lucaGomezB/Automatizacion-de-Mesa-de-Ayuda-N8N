"""
Tests de resolucion de destinatarios de notificacion (c-82, notification-routing).

Cubren, en estricto RED -> GREEN -> TRIANGULATE -> REFACTOR:
    - 2.x: `EmpleadoRepository.listar_mesa_de_ayuda_activos` (solo activos, solo
      rol mesa_de_ayuda, sin filtro de sector, sin duplicados).
    - 3.x: `NotificationRecipientService.resolver_destinatarios_revision` (sin
      parametro de sector; normaliza emails, lista vacia ante 0 coincidencias,
      sin emails en claro en el log, sin propagar fallos del repositorio).
    - 4.x: la respuesta de alta `POST /api/v1/incidentes` expone
      `destinatarios_revision` SOLO con `requiere_revision_humana=true` y NO en
      las respuestas de consulta (`GET` detalle / listado).

Sin PII real: todos los emails usan el dominio reservado `example.test`.
"""

import pytest
import pytest_asyncio
from sqlalchemy import delete, inspect as sa_inspect
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog.testing import capture_logs

from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository

# ── Helpers ───────────────────────────────────────────────────────────────────


async def _crear_sector(session, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


async def _crear_empleado(
    session,
    *,
    legajo: str,
    email: str,
    sector_id: int | None = None,
    rol: RolEmpleado = RolEmpleado.mesa_de_ayuda,
    activo: bool = True,
) -> Empleado:
    empleado = Empleado(
        legajo=legajo,
        nombre=f"Empleado {legajo}",
        email=email,
        sector_id=sector_id,
        rol=rol,
        activo=activo,
    )
    session.add(empleado)
    await session.flush()
    return empleado


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 2 — EmpleadoRepository.listar_mesa_de_ayuda_activos
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_2_1_listar_mesa_de_ayuda_activos_solo_activos_del_rol(db_session):
    """RED/GREEN: devuelve SOLO empleados activos con rol mesa_de_ayuda."""
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="MDA-1", email="mda1@example.test", sector_id=sector.id
    )

    encontrados = await repo.listar_mesa_de_ayuda_activos()

    assert [e.legajo for e in encontrados] == ["MDA-1"]
    # El sector quedo eager-loaded (no lazy-load en async).
    assert "sector" not in sa_inspect(encontrados[0]).unloaded


@pytest.mark.asyncio
async def test_2_3_excluye_inactivos_y_otros_roles(db_session):
    """TRIANGULATE: inactivos y otros roles NO son destinatarios."""
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="MDA-ACT", email="mda-act@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session,
        legajo="MDA-INACT",
        email="mda-inact@example.test",
        sector_id=sector.id,
        activo=False,
    )
    await _crear_empleado(
        db_session,
        legajo="UF-1",
        email="uf1@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.usuario_final,
    )
    await _crear_empleado(
        db_session,
        legajo="ADM-1",
        email="adm1@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.administrador_directorio,
    )

    encontrados = await repo.listar_mesa_de_ayuda_activos()

    assert [e.legajo for e in encontrados] == ["MDA-ACT"]


@pytest.mark.asyncio
async def test_2_3_el_sector_no_acota_los_destinatarios(db_session):
    """TRIANGULATE: mesa_de_ayuda de distintos sectores o sin sector, todos."""
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="MDA-SIS", email="mda-sis@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session, legajo="MDA-SIN", email="mda-sin@example.test", sector_id=None
    )

    encontrados = await repo.listar_mesa_de_ayuda_activos()

    assert [e.legajo for e in encontrados] == ["MDA-SIS", "MDA-SIN"]


@pytest.mark.asyncio
async def test_2_3_varios_sin_duplicados(db_session):
    """TRIANGULATE: con varios mesa_de_ayuda devuelve cada uno una sola vez."""
    repo = EmpleadoRepository(db_session)
    await _crear_empleado(db_session, legajo="MDA-1", email="mda1@example.test")
    await _crear_empleado(db_session, legajo="MDA-2", email="mda2@example.test")

    encontrados = await repo.listar_mesa_de_ayuda_activos()

    assert [e.legajo for e in encontrados] == ["MDA-1", "MDA-2"]
    assert len({e.id for e in encontrados}) == len(encontrados)


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3 — NotificationRecipientService.resolver_destinatarios_revision
# ═══════════════════════════════════════════════════════════════════════════════


def _svc(session):
    from app.services.notification_recipient_service import NotificationRecipientService

    return NotificationRecipientService(session)


@pytest.mark.asyncio
async def test_3_1_resuelve_y_normaliza_emails(db_session):
    """RED/GREEN: devuelve los emails de los mesa_de_ayuda activos, normalizados."""
    await _crear_empleado(
        db_session,
        legajo="MDA-1",
        email="Mesa.Uno@Example.TEST",
    )

    destinatarios = await _svc(db_session).resolver_destinatarios_revision()

    assert destinatarios == ["mesa.uno@example.test"]


@pytest.mark.asyncio
async def test_3_3_directorio_vacio_devuelve_vacio_sin_excepcion(db_session):
    """TRIANGULATE: directorio vacio devuelve lista vacia (NR-002, NR-007)."""
    assert await _svc(db_session).resolver_destinatarios_revision() == []


@pytest.mark.asyncio
async def test_3_3_varios_destinatarios(db_session):
    """TRIANGULATE: con N mesa_de_ayuda devuelve los N destinatarios."""
    await _crear_empleado(db_session, legajo="MDA-1", email="mda1@example.test")
    await _crear_empleado(db_session, legajo="MDA-2", email="mda2@example.test")

    destinatarios = await _svc(db_session).resolver_destinatarios_revision()

    assert destinatarios == ["mda1@example.test", "mda2@example.test"]


@pytest.mark.asyncio
async def test_3_3_email_invalido_en_directorio_no_rompe(db_session):
    """TRIANGULATE: un email invalido en el directorio se omite sin romper."""
    await _crear_empleado(db_session, legajo="MDA-OK", email="mda-ok@example.test")
    await _crear_empleado(db_session, legajo="MDA-BAD", email="no-es-email")

    destinatarios = await _svc(db_session).resolver_destinatarios_revision()

    assert destinatarios == ["mda-ok@example.test"]


@pytest.mark.asyncio
async def test_3_3_trazabilidad_sin_emails_en_claro(db_session):
    """TRIANGULATE (NR-006): el log indica la cantidad, SIN emails en claro."""
    await _crear_empleado(db_session, legajo="MDA-1", email="mda1@example.test")

    with capture_logs() as logs:
        await _svc(db_session).resolver_destinatarios_revision()

    eventos = [
        e for e in logs if e.get("event") == "destinatarios_revision_resueltos"
    ]
    assert eventos, "Debe registrarse la trazabilidad de la resolucion"
    assert eventos[-1].get("cantidad") == 1

    serializado = repr(logs)
    assert "mda1@example.test" not in serializado


@pytest.mark.asyncio
async def test_3_3_fallo_del_repositorio_no_propaga(db_session):
    """TRIANGULATE (NR-007): un fallo del repositorio degrada a lista vacia."""

    class _RepoQueFalla:
        async def listar_activos_por_rol(self, rol):
            raise RuntimeError("directorio no disponible")

    svc = _svc(db_session)
    svc._repo = _RepoQueFalla()

    assert await svc.resolver_destinatarios_revision() == []


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4 — Contrato de alta: destinatarios_revision SOLO en la respuesta POST
# ═══════════════════════════════════════════════════════════════════════════════

_DESCRIPCION = "Falla en el servidor de base de datos principal del sector contable."
_PAYLOAD = {"descripcion": _DESCRIPCION, "prioridad": "alta"}


def _result(
    sector_predicho: str = "Sistemas",
    confianza: float = 0.95,
    requiere_revision_humana: bool = False,
):
    from app.schemas.clasificacion import ClasificacionResult

    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=requiere_revision_humana,
        respuesta_raw=None,
    )


@pytest_asyncio.fixture
async def mesas_de_ayuda(engine, seed_catalogs):
    """
    Siembra mesa_de_ayuda ACTIVOS y filas de control (inactivo, otro rol),
    visibles para el cliente ASGI (engine compartido).
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    sector = seed_catalogs["sector_sistemas"]
    async with factory() as session:
        session.add_all(
            [
                Empleado(
                    legajo="MDA-1", nombre="Mesa Uno", email="mda1@example.test",
                    sector_id=sector.id, rol=RolEmpleado.mesa_de_ayuda, activo=True,
                ),
                Empleado(
                    legajo="MDA-2", nombre="Mesa Dos", email="mda2@example.test",
                    sector_id=None, rol=RolEmpleado.mesa_de_ayuda, activo=True,
                ),
                Empleado(
                    legajo="MDA-INACT", nombre="Mesa Inactivo",
                    email="mda-inact@example.test", sector_id=sector.id,
                    rol=RolEmpleado.mesa_de_ayuda, activo=False,
                ),
                Empleado(
                    legajo="UF-SIS", nombre="Usuario Final",
                    email="uf-sis@example.test", sector_id=sector.id,
                    rol=RolEmpleado.usuario_final, activo=True,
                ),
                Empleado(
                    legajo="ADM-1", nombre="Admin", email="adm1@example.test",
                    sector_id=None, rol=RolEmpleado.administrador_directorio, activo=True,
                ),
                Empleado(
                    legajo="REP-ID", nombre="Reportante Identificado",
                    email="rep-ident@example.test", sector_id=None,
                    rol=RolEmpleado.usuario_final, activo=True,
                ),
            ]
        )
        await session.commit()
    yield {"sector_sistemas": sector, "canal_correo": seed_catalogs["canal_correo"].id}
    async with factory() as session:
        await session.execute(
            delete(Empleado).where(
                Empleado.legajo.in_(
                    ["MDA-1", "MDA-2", "MDA-INACT", "UF-SIS", "ADM-1", "REP-ID"]
                )
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_4_1_alta_con_revision_incluye_todos_los_mesa_de_ayuda(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """
    RED/GREEN: con revision humana, la respuesta de alta expone los
    mesa_de_ayuda ACTIVOS (normalizados), excluyendo inactivos y otros roles.
    """
    result = _result(
        sector_predicho="Sistemas", confianza=0.5, requiere_revision_humana=True
    )
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=_PAYLOAD)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["requiere_revision_humana"] is True
    assert sorted(body["destinatarios_revision"]) == [
        "mda1@example.test",
        "mda2@example.test",
    ]


@pytest.mark.asyncio
async def test_4_4_alta_sin_revision_no_incluye_destinatarios(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """TRIANGULATE: reportante identificado + sin revision => lista vacia."""
    result = _result(
        sector_predicho="Sistemas", confianza=0.95, requiere_revision_humana=False
    )
    payload = {
        **_PAYLOAD,
        "canal_origen_id": mesas_de_ayuda["canal_correo"],
        "reportante_email": "rep-ident@example.test",
    }
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["requiere_revision_humana"] is False
    assert body["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_4_3_alta_revision_sin_mesa_de_ayuda_lista_vacia(
    seed_catalogs, make_client_with_classifier
):
    """RED/GREEN: sin mesa_de_ayuda activo => 201 con lista vacia (sin excepcion)."""
    result = _result(
        sector_predicho="Sistemas", confianza=0.5, requiere_revision_humana=True
    )
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=_PAYLOAD)

    assert response.status_code == 201, response.text
    assert response.json()["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_4_3_alta_revision_sector_nulo_lista_vacia(
    seed_catalogs, make_client_with_classifier
):
    """TRIANGULATE: un incidente sin sector resuelto no rompe el alta."""
    payload = {
        **_PAYLOAD,
        "clasificacion": {
            "sector_predicho": None,
            "sectores_adicionales": [],
            "confianza": 0.0,
            "requiere_revision_humana": True,
            "origen": "n8n",
        },
    }
    async with make_client_with_classifier(_result()) as client:
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["sector"] is None
    assert body["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_4_4_el_sector_del_incidente_no_acota_los_destinatarios(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """TRIANGULATE: el sector del incidente NO filtra los mesa_de_ayuda."""
    result = _result(
        sector_predicho="Bases de Datos",
        confianza=0.5,
        requiere_revision_humana=True,
    )
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=_PAYLOAD)

    assert response.status_code == 201, response.text
    assert sorted(response.json()["destinatarios_revision"]) == [
        "mda1@example.test",
        "mda2@example.test",
    ]


@pytest.mark.asyncio
async def test_4_1_get_no_expone_destinatarios_revision(
    seed_catalogs, mesas_de_ayuda, make_client_with_classifier
):
    """RED/GREEN (NR-006): `destinatarios_revision` NO se agrega a las consultas."""
    result = _result(
        sector_predicho="Sistemas", confianza=0.5, requiere_revision_humana=True
    )
    async with make_client_with_classifier(result) as client:
        creado = await client.post("/api/v1/incidentes/", json=_PAYLOAD)
        assert creado.status_code == 201, creado.text
        incidente_id = creado.json()["id"]

        detalle = await client.get(f"/api/v1/incidentes/{incidente_id}")
        listado = await client.get("/api/v1/incidentes/")
    assert detalle.status_code == 200, detalle.text
    assert "destinatarios_revision" not in detalle.json()
    assert listado.status_code == 200, listado.text
    for item in listado.json():
        assert "destinatarios_revision" not in item
