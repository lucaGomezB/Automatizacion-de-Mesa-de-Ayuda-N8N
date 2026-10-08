"""
Tests de resolucion de destinatarios de notificacion (c-56, notification-routing).

Cubren, en estricto RED -> GREEN -> TRIANGULATE -> REFACTOR:
    - 2.x: `EmpleadoRepository.listar_operadores_por_sector` (solo activos,
      solo rol operador, sector nulo/inexistente sin excepcion, sin duplicados).
    - 3.x: `NotificationRecipientService.resolver_destinatarios_revision`
      (normaliza emails, lista vacia ante 0 coincidencias o sector nulo, sin
      emails en claro en el log, sin propagar fallos del repositorio).
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
    rol: RolEmpleado = RolEmpleado.operador,
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
# Grupo 2 — EmpleadoRepository.listar_operadores_por_sector (2.1/2.3)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_2_1_listar_operadores_por_sector_solo_activos_operador(db_session):
    """
    RED/GREEN (2.1): devuelve SOLO empleados activos con rol operador del sector.
    """
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-1", email="op1@example.test", sector_id=sector.id
    )

    encontrados = await repo.listar_operadores_por_sector(sector.id)

    assert [e.legajo for e in encontrados] == ["OP-1"]
    # El sector quedo eager-loaded (no lazy-load en async).
    assert "sector" not in sa_inspect(encontrados[0]).unloaded


@pytest.mark.asyncio
async def test_2_3_excluye_inactivos_y_otros_roles(db_session):
    """
    TRIANGULATE (2.3b/c): un operador inactivo y empleados de otros roles del
    mismo sector NO son destinatarios.
    """
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-ACT", email="op-act@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session,
        legajo="OP-INACT",
        email="op-inact@example.test",
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

    encontrados = await repo.listar_operadores_por_sector(sector.id)

    assert [e.legajo for e in encontrados] == ["OP-ACT"]


@pytest.mark.asyncio
async def test_2_3_sector_nulo_o_inexistente_devuelve_vacio(db_session):
    """
    TRIANGULATE (2.3d): un sector None o inexistente devuelve lista vacia sin
    lanzar excepcion.
    """
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-1", email="op1@example.test", sector_id=sector.id
    )

    assert await repo.listar_operadores_por_sector(None) == []
    assert await repo.listar_operadores_por_sector(999999) == []


@pytest.mark.asyncio
async def test_2_3_varios_operadores_sin_duplicados(db_session):
    """
    TRIANGULATE (2.3a/e): con varios operadores devuelve cada uno una sola vez,
    en orden deterministico por id.
    """
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-1", email="op1@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session, legajo="OP-2", email="op2@example.test", sector_id=sector.id
    )

    encontrados = await repo.listar_operadores_por_sector(sector.id)

    assert [e.legajo for e in encontrados] == ["OP-1", "OP-2"]
    assert len({e.id for e in encontrados}) == len(encontrados)


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3 — NotificationRecipientService.resolver_destinatarios_revision (3.1/3.3)
# ═══════════════════════════════════════════════════════════════════════════════


def _svc(session):
    # Import diferido: permite que los tests del repositorio (grupo 2) vayan
    # RED/GREEN con independencia de que el servicio exista todavia.
    from app.services.notification_recipient_service import NotificationRecipientService

    return NotificationRecipientService(session)


@pytest.mark.asyncio
async def test_3_1_resuelve_y_normaliza_emails_de_operadores(db_session):
    """
    RED/GREEN (3.1): devuelve los emails de los operadores activos del sector,
    normalizados (minusculas/trim).
    """
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session,
        legajo="OP-1",
        email="Operador.Uno@Example.TEST",
        sector_id=sector.id,
    )

    destinatarios = await _svc(db_session).resolver_destinatarios_revision(sector.id)

    assert destinatarios == ["operador.uno@example.test"]


@pytest.mark.asyncio
async def test_3_3_sector_nulo_o_sin_operadores_devuelve_vacio_sin_excepcion(db_session):
    """
    TRIANGULATE (3.3): sector None, directorio vacio o sector sin operador
    devuelven lista vacia (NR-002, NR-007: no fatal).
    """
    svc = _svc(db_session)
    assert await svc.resolver_destinatarios_revision(None) == []

    sector = await _crear_sector(db_session)
    assert await svc.resolver_destinatarios_revision(sector.id) == []


@pytest.mark.asyncio
async def test_3_3_varios_destinatarios(db_session):
    """
    TRIANGULATE (3.3): con N operadores devuelve los N destinatarios.
    """
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-1", email="op1@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session, legajo="OP-2", email="op2@example.test", sector_id=sector.id
    )

    destinatarios = await _svc(db_session).resolver_destinatarios_revision(sector.id)

    assert destinatarios == ["op1@example.test", "op2@example.test"]


@pytest.mark.asyncio
async def test_3_3_email_invalido_en_directorio_no_rompe(db_session):
    """
    TRIANGULATE (3.3): un email con formato invalido en el directorio se omite
    sin propagar el ValueError de normalizacion.
    """
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-OK", email="op-ok@example.test", sector_id=sector.id
    )
    await _crear_empleado(
        db_session, legajo="OP-BAD", email="no-es-email", sector_id=sector.id
    )

    destinatarios = await _svc(db_session).resolver_destinatarios_revision(sector.id)

    assert destinatarios == ["op-ok@example.test"]


@pytest.mark.asyncio
async def test_3_3_trazabilidad_sin_emails_en_claro(db_session):
    """
    TRIANGULATE (3.3, NR-006): el log estructurado indica sector y cantidad,
    SIN emails en claro.
    """
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session, legajo="OP-1", email="op1@example.test", sector_id=sector.id
    )

    with capture_logs() as logs:
        await _svc(db_session).resolver_destinatarios_revision(sector.id)

    eventos = [
        e for e in logs if e.get("event") == "destinatarios_revision_resueltos"
    ]
    assert eventos, "Debe registrarse la trazabilidad de la resolucion"
    assert eventos[-1].get("sector_id") == sector.id
    assert eventos[-1].get("cantidad") == 1

    serializado = repr(logs)
    assert "op1@example.test" not in serializado


@pytest.mark.asyncio
async def test_3_3_fallo_del_repositorio_no_propaga(db_session):
    """
    TRIANGULATE (3.3, NR-007): un fallo del repositorio no propaga excepcion;
    el servicio degrada a lista vacia.
    """

    class _RepoQueFalla:
        async def listar_operadores_por_sector(self, sector_id):  # noqa: ANN001
            raise RuntimeError("directorio no disponible")

    svc = _svc(db_session)
    svc._repo = _RepoQueFalla()

    assert await svc.resolver_destinatarios_revision(1) == []


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4 — Contrato de alta: destinatarios_revision SOLO en la respuesta POST
#          (4.1/4.2/4.3/4.4)
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
async def operadores_sector(engine, seed_catalogs):
    """
    Siembra operadores ACTIVOS y filas de control (inactivo, otro rol) en el
    sector "Sistemas", visibles para el cliente ASGI (engine compartido).
    Limpia las filas ANTES del teardown de `seed_catalogs` (orden de finalizacion
    inverso) para no violar la FK a `sector`.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    sector = seed_catalogs["sector_sistemas"]
    async with factory() as session:
        session.add_all(
            [
                Empleado(
                    legajo="OP-1",
                    nombre="Operador Uno",
                    email="op1@example.test",
                    sector_id=sector.id,
                    rol=RolEmpleado.operador,
                    activo=True,
                ),
                Empleado(
                    legajo="OP-2",
                    nombre="Operador Dos",
                    email="op2@example.test",
                    sector_id=sector.id,
                    rol=RolEmpleado.operador,
                    activo=True,
                ),
                Empleado(
                    legajo="OP-INACT",
                    nombre="Operador Inactivo",
                    email="op-inact@example.test",
                    sector_id=sector.id,
                    rol=RolEmpleado.operador,
                    activo=False,
                ),
                Empleado(
                    legajo="UF-SIS",
                    nombre="Usuario Final",
                    email="uf-sis@example.test",
                    sector_id=sector.id,
                    rol=RolEmpleado.usuario_final,
                    activo=True,
                ),
            ]
        )
        await session.commit()
    yield {"sector_sistemas": sector}
    async with factory() as session:
        await session.execute(
            delete(Empleado).where(
                Empleado.legajo.in_(["OP-1", "OP-2", "OP-INACT", "UF-SIS"])
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_4_1_alta_con_revision_incluye_operadores_del_sector(
    seed_catalogs, operadores_sector, make_client_with_classifier
):
    """
    RED/GREEN (4.1): con revision humana, la respuesta de alta expone los
    operadores ACTIVOS del sector (normalizados), excluyendo inactivos y otros
    roles.
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
        "op1@example.test",
        "op2@example.test",
    ]


@pytest.mark.asyncio
async def test_4_4_alta_sin_revision_no_incluye_destinatarios(
    seed_catalogs, operadores_sector, make_client_with_classifier
):
    """
    TRIANGULATE (4.4b): sin revision humana la lista queda vacia, aunque el
    directorio tenga operadores del sector.
    """
    result = _result(
        sector_predicho="Sistemas", confianza=0.95, requiere_revision_humana=False
    )
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=_PAYLOAD)

    assert response.status_code == 201, response.text
    assert response.json()["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_4_3_alta_revision_sin_operadores_lista_vacia(
    seed_catalogs, make_client_with_classifier
):
    """
    RED/GREEN (4.3): directorio sin operador del sector => 201 con lista vacia
    (sin excepcion; N8N aplica el respaldo).
    """
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
    """
    TRIANGULATE (4.3): un incidente sin sector resuelto (revision forzada) no
    rompe el alta y devuelve lista vacia.
    """
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
async def test_4_4_alta_revision_de_otro_sector_no_usa_operadores_ajenos(
    seed_catalogs, operadores_sector, make_client_with_classifier
):
    """
    TRIANGULATE (4.4a): un incidente de OTRO sector no recibe los operadores de
    "Sistemas" (se enruta por el sector principal, D7).
    """
    result = _result(
        sector_predicho="Bases de Datos",
        confianza=0.5,
        requiere_revision_humana=True,
    )
    async with make_client_with_classifier(result) as client:
        response = await client.post("/api/v1/incidentes/", json=_PAYLOAD)

    assert response.status_code == 201, response.text
    assert response.json()["destinatarios_revision"] == []


@pytest.mark.asyncio
async def test_4_1_get_no_expone_destinatarios_revision(
    seed_catalogs, operadores_sector, make_client_with_classifier
):
    """
    RED/GREEN (4.1, NR-006): `destinatarios_revision` NO se agrega a las
    respuestas de consulta (detalle GET /{id} ni listado GET /).
    """
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
