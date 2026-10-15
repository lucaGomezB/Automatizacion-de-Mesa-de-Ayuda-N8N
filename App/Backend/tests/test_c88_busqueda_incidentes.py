"""
Tests de busqueda por texto libre de incidentes (c-88).

Cubre el requisito IS-001 (busqueda parcial case-insensitive contra
`descripcion_pseudonimizada`, coincidencia exacta por `id` cuando `q` es
numerico, combinacion AND con los filtros existentes, termino corto ignorado y
comodines tratados como literales) y el IS-002 (la busqueda respeta el alcance
de visibilidad y nunca consulta `descripcion_original`).

Niveles:
    - Repositorio (SQLite unidad): `IncidenteRepository.list_filtered(q=...)`.
    - API (SQLite unidad): `GET /api/v1/incidentes/?q=...` con derivacion real
      del alcance por rol mediante override de la dependencia.
"""

from contextlib import asynccontextmanager

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
from app.repositories.incidente_repository import IncidenteRepository
from app.routes.incidentes import get_alcance_incidentes
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance


def _inc(**kwargs) -> dict:
    """Cuerpo base de un incidente para los tests del repositorio."""
    base = {
        "descripcion_original": "original sin termino buscado",
        "descripcion_pseudonimizada": "descripcion generica",
        "prioridad": PrioridadEnum.media,
    }
    base.update(kwargs)
    return base


async def _seed_estado(db_session, nombre: str = "c88-nuevo") -> Estado:
    estado = Estado(nombre=nombre, descripcion="n", es_terminal=False)
    db_session.add(estado)
    await db_session.flush()
    return estado


# ── IS-001: repositorio (SQLite unidad) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_list_filtered_busqueda_parcial_descripcion(db_session):
    """El `q` que es subcadena de la descripcion pseudonimizada devuelve la fila."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    a = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="El servidor de correo no responde",
            origen_message_id="c88-repo-a",
        ),
    )
    await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="Impresora sin toner",
            origen_message_id="c88-repo-b",
        ),
    )

    resultado = await repo.list_filtered(q="correo")

    assert [i.id for i in resultado] == [a.id]


@pytest.mark.asyncio
async def test_list_filtered_busqueda_case_insensitive(db_session):
    """La coincidencia ignora la capitalizacion del termino."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    a = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="Servidor Caido de Red",
            origen_message_id="c88-repo-ci",
        ),
    )

    resultado = await repo.list_filtered(q="SERVIDOR")

    assert [i.id for i in resultado] == [a.id]


@pytest.mark.asyncio
async def test_list_filtered_busqueda_por_id_numerico_combina_or(db_session):
    """Un `q` solo-digitos coincide por `id` OR por descripcion."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    por_id = await repo.create(
        id=4242,
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="texto sin el numero",
            origen_message_id="c88-repo-num",
        ),
    )
    por_descripcion = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="ticket 4242 abierto en red",
            origen_message_id="c88-repo-desc",
        ),
    )

    resultado = await repo.list_filtered(q="4242")

    assert {i.id for i in resultado} == {por_id.id, por_descripcion.id}


@pytest.mark.asyncio
async def test_list_filtered_combinacion_and_con_sector(db_session):
    """`q` se combina con AND con los filtros existentes (aqui, sector)."""
    estado = await _seed_estado(db_session)
    sector_a = Sector(nombre="Sistemas", descripcion="A")
    sector_b = Sector(nombre="Bases de Datos", descripcion="B")
    db_session.add_all([sector_a, sector_b])
    await db_session.flush()
    repo = IncidenteRepository(db_session)
    a = await repo.create(
        estado_id=estado.id,
        sector_id=sector_a.id,
        **_inc(
            descripcion_pseudonimizada="error de correo en el nodo",
            origen_message_id="c88-repo-sa",
        ),
    )
    await repo.create(
        estado_id=estado.id,
        sector_id=sector_b.id,
        **_inc(
            descripcion_pseudonimizada="error de correo en el nodo",
            origen_message_id="c88-repo-sb",
        ),
    )

    resultado = await repo.list_filtered(q="correo", sector_id=sector_a.id)

    assert [i.id for i in resultado] == [a.id]


@pytest.mark.asyncio
async def test_list_filtered_combinacion_and_con_prioridad(db_session):
    """`q` se combina con AND con el filtro de prioridad."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    a = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="error de correo",
            prioridad=PrioridadEnum.alta,
            origen_message_id="c88-repo-pa",
        ),
    )
    await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="error de correo",
            prioridad=PrioridadEnum.baja,
            origen_message_id="c88-repo-pb",
        ),
    )

    resultado = await repo.list_filtered(q="correo", prioridad=PrioridadEnum.alta)

    assert [i.id for i in resultado] == [a.id]


@pytest.mark.asyncio
async def test_list_filtered_sin_coincidencias_devuelve_vacio(db_session):
    """Un `q` sin coincidencias devuelve lista vacia, sin error."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="impresora sin toner",
            origen_message_id="c88-repo-vacio",
        ),
    )

    assert await repo.list_filtered(q="inexistente") == []


@pytest.mark.asyncio
async def test_list_filtered_termino_corto_o_vacio_se_ignora(db_session):
    """`q` vacio, de solo espacios o de un caracter se comporta como sin filtro."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    a = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="alfa",
            origen_message_id="c88-repo-corto-a",
        ),
    )
    b = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="beta",
            origen_message_id="c88-repo-corto-b",
        ),
    )
    sin_filtro = {i.id for i in await repo.list_filtered()}
    assert sin_filtro == {a.id, b.id}

    for q in ("", "   ", "a", "z"):
        assert {i.id for i in await repo.list_filtered(q=q)} == sin_filtro


@pytest.mark.asyncio
async def test_list_filtered_comodines_porcentaje_son_literales(db_session):
    """El `%` se busca como caracter literal, no como comodin."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    literal = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="porcentaje 100% real",
            origen_message_id="c88-repo-pct",
        ),
    )
    await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="porcentaje 1000 real",
            origen_message_id="c88-repo-pct2",
        ),
    )

    resultado = await repo.list_filtered(q="100%")

    assert [i.id for i in resultado] == [literal.id]


@pytest.mark.asyncio
async def test_list_filtered_comodines_underscore_son_literales(db_session):
    """El `_` se busca como caracter literal, no como comodin."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    literal = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="variable _privada",
            origen_message_id="c88-repo-us",
        ),
    )
    await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="variable xprivada",
            origen_message_id="c88-repo-us2",
        ),
    )

    resultado = await repo.list_filtered(q="_privada")

    assert [i.id for i in resultado] == [literal.id]


@pytest.mark.asyncio
async def test_list_filtered_backslash_es_literal(db_session):
    """El caracter de escape se duplica y se busca como literal."""
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    literal = await repo.create(
        estado_id=estado.id,
        **_inc(
            descripcion_pseudonimizada="ruta c:\\temp\\log",
            origen_message_id="c88-repo-bs",
        ),
    )

    resultado = await repo.list_filtered(q="c:\\temp")

    assert [i.id for i in resultado] == [literal.id]


# ── IS-001 / IS-002: API (SQLite unidad) ─────────────────────────────────────


@pytest_asyncio.fixture
async def c88_api_env(engine):
    """Siembra catalogo, dos empleados y cuatro incidentes con descripciones fijas."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="c88-sector", descripcion="A")
        estado = Estado(nombre="c88-nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector, estado])
        await s.flush()

        e1 = Empleado(
            legajo="C88-E1",
            nombre="Uno",
            email="c88.e1@example.test",
            sector_id=sector.id,
            rol=RolEmpleado.usuario_final,
        )
        e2 = Empleado(
            legajo="C88-E2",
            nombre="Dos",
            email="c88.e2@example.test",
            sector_id=sector.id,
            rol=RolEmpleado.usuario_final,
        )
        s.add_all([e1, e2])
        await s.flush()

        base = dict(
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=sector.id,
        )
        a = Incidente(
            descripcion_original="secreto-a",
            descripcion_pseudonimizada="correo del servidor caido",
            reportante_empleado_id=e1.id,
            origen_message_id="c88-api-a",
            **base,
        )
        b = Incidente(
            descripcion_original="secreto-b",
            descripcion_pseudonimizada="correo del servidor lento",
            reportante_empleado_id=e2.id,
            origen_message_id="c88-api-b",
            **base,
        )
        c = Incidente(
            descripcion_original="secreto-c",
            descripcion_pseudonimizada="impresora trabada",
            reportante_empleado_id=e1.id,
            origen_message_id="c88-api-c",
            **base,
        )
        d = Incidente(
            descripcion_original="termino-secreto-original",
            descripcion_pseudonimizada="texto sin la palabra reservada",
            reportante_empleado_id=e1.id,
            origen_message_id="c88-api-d",
            **base,
        )
        s.add_all([a, b, c, d])
        await s.commit()
        ids = {
            "a": a.id,
            "b": b.id,
            "c": c.id,
            "d": d.id,
            "e1": e1.id,
            "e2": e2.id,
        }
    yield ids
    async with factory() as s:
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@asynccontextmanager
async def _client(engine, alcance: AlcanceIncidentes, user_id: int = 1):
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

    async def override_auth():
        return User(id=user_id, username="c88", hashed_password="", is_active=True)

    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[get_alcance_incidentes] = lambda: alcance

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_api_busqueda_filtra_y_sin_q_no_cambia(engine, c88_api_env):
    """`GET /incidentes/?q=...` filtra; sin `q` la lista no cambia."""
    global_ = AlcanceIncidentes(ModoAlcance.GLOBAL)
    async with _client(engine, global_) as c:
        sin_q = await c.get("/api/v1/incidentes/")
        con_q = await c.get("/api/v1/incidentes/", params={"q": "correo"})

    assert sin_q.status_code == 200
    assert con_q.status_code == 200
    assert {i["id"] for i in sin_q.json()} == {
        c88_api_env["a"],
        c88_api_env["b"],
        c88_api_env["c"],
        c88_api_env["d"],
    }
    assert {i["id"] for i in con_q.json()} == {c88_api_env["a"], c88_api_env["b"]}


@pytest.mark.asyncio
async def test_api_busqueda_termino_corto_se_ignora(engine, c88_api_env):
    """Un termino de 1 caracter equivale a sin filtro en la API."""
    global_ = AlcanceIncidentes(ModoAlcance.GLOBAL)
    async with _client(engine, global_) as c:
        respuesta = await c.get("/api/v1/incidentes/", params={"q": "c"})

    assert len(respuesta.json()) == 4


@pytest.mark.asyncio
async def test_api_busqueda_sin_coincidencias_200_vacio(engine, c88_api_env):
    """Un `q` sin coincidencias devuelve 200 con lista vacia."""
    global_ = AlcanceIncidentes(ModoAlcance.GLOBAL)
    async with _client(engine, global_) as c:
        respuesta = await c.get(
            "/api/v1/incidentes/", params={"q": "no-existe-jamas"}
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.asyncio
async def test_api_busqueda_alcance_propio_no_ve_ajenos(engine, c88_api_env):
    """IS-002: un alcance PROPIO no ve el incidente ajeno aunque el `q` coincida."""
    propio = AlcanceIncidentes(
        ModoAlcance.PROPIO, reportante_empleado_id=c88_api_env["e1"]
    )
    async with _client(engine, propio) as c:
        respuesta = await c.get("/api/v1/incidentes/", params={"q": "correo"})

    assert {i["id"] for i in respuesta.json()} == {c88_api_env["a"]}


@pytest.mark.asyncio
async def test_api_busqueda_alcance_vacio_no_ve_nada(engine, c88_api_env):
    """IS-002: una cuenta de alcance VACIO obtiene lista vacia con cualquier `q`."""
    vacio = AlcanceIncidentes(ModoAlcance.VACIO)
    async with _client(engine, vacio) as c:
        respuesta = await c.get("/api/v1/incidentes/", params={"q": "correo"})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.asyncio
async def test_api_busqueda_no_expone_descripcion_original(engine, c88_api_env):
    """IS-002: un termino presente solo en `descripcion_original` no devuelve la fila."""
    global_ = AlcanceIncidentes(ModoAlcance.GLOBAL)
    async with _client(engine, global_) as c:
        respuesta = await c.get(
            "/api/v1/incidentes/", params={"q": "termino-secreto"}
        )

    assert respuesta.status_code == 200
    assert c88_api_env["d"] not in {i["id"] for i in respuesta.json()}
    assert "termino-secreto-original" not in respuesta.text
