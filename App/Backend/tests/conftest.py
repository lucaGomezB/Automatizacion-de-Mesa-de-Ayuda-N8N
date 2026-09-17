"""
Configuración global de fixtures para la suite de tests.

Responsabilidad:
    Define los fixtures de pytest compartidos por todos los módulos de test.
    Utiliza una base de datos SQLite en memoria (vía aiosqlite) para garantizar
    que los tests sean rápidos, autocontenidos y no dependan de un servidor
    PostgreSQL externo.

    El esquema se crea directamente desde los metadatos de SQLAlchemy
    (no mediante Alembic) para simplificar el ciclo de vida del test
    y reducir el tiempo de ejecución de la suite.

Fixtures disponibles:
    engine:          Motor SQLite en memoria (scope=session): compartido por todos los tests.
    db_session:      Sesión con rollback automático tras cada test (scope=function).
    client:          Cliente HTTP asíncrono (ASGI) con la base de datos de test inyectada.
    seed_catalogs:   Siembra registros de catálogo mínimos vía el engine compartido
                     (Estado "nuevo", cinco Sector, tres CanalOrigen). Limpia al finalizar.
    make_client_with_classifier: Factory que devuelve un AsyncClient con el clasificador
                     inyectado como doble de prueba (dependency_override de get_service).

    ── PostgreSQL Integration Fixtures (C-19) ──
    pg_engine:       Motor PostgreSQL (function scope). Crea todas las tablas.
                     Falla ruidosamente si PostgreSQL no está disponible
                     (sin skip silencioso). Ver design.md D1/D2.
    pg_session:      Sesión PostgreSQL con rollback por test (function scope).
    pg_client:       Cliente HTTP asíncrono con PostgreSQL (function scope).

Estrategia de aislamiento:
    Cada test que usa db_session obtiene una sesión que se revierte al finalizar,
    garantizando que los datos de un test no afecten a los siguientes.
    El fixture 'client' sobrescribe la dependencia get_db_session con una función
    que usa la misma base de datos de test, asegurando consistencia.

    seed_catalogs usa el engine directamente (con commit explícito), ya que el
    cliente ASGI abre su propia sesión por request. Limpia las filas sembradas
    al finalizar para evitar filtración entre tests.
"""

import asyncio
import os
import warnings
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, event, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db_session
from app.core.security import get_current_user
from app.main import create_app
from app.models.catalog import CanalOrigen, Estado, Sector
from app.models.user import User
from app.routes.incidentes import get_service as get_incidente_service
from app.schemas.clasificacion import ClasificacionResult
from app.services.incidente_service import IncidenteService

# Importación de todos los modelos para que SQLAlchemy los registre en Base.metadata
# antes de llamar a create_all(). Sin esto, las tablas no serían creadas.
from app.models import *  # noqa: F401,F403

# URL de base de datos SQLite en memoria: no requiere instalación ni configuración.
# aiosqlite provee el driver asíncrono compatible con el motor de la aplicación.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ── PostgreSQL Integration Test Helpers (C-19, c-32) ───────────────────────

# Disposable test database used by the integration suite (c-32). It is
# physically separate from the application database so destructive DDL never
# reaches the development/production data.
DEFAULT_TEST_PG_URL = (
    "postgresql+asyncpg://mesa:mesa@localhost:5433/mesa_de_ayuda_test"
)

# Explicit opt-in required to allow a test target whose database NAME matches
# the application database. It is never enabled automatically.
ALLOW_APP_DB_ENV = "TEST_PG_ALLOW_APP_DB"


class UnsafeTestDatabaseError(RuntimeError):
    """Raised when the suite would run destructive DDL on the application DB."""


def _database_name(url: str) -> str | None:
    """Return the database name component of a SQLAlchemy URL."""
    return make_url(url).database


def _app_database_name() -> str | None:
    """Return the application database name derived from DATABASE_URL, if set."""
    app_url = os.environ.get("DATABASE_URL")
    if not app_url:
        return None
    return _database_name(app_url)


def _get_pg_url() -> str:
    """Return the PostgreSQL connection URL for integration tests.

    Uses TEST_PG_URL if set; otherwise resolves to the disposable test database
    derived from the development credentials. NO code path resolves to the
    application database (c-32 D2).
    """
    return os.environ.get("TEST_PG_URL", DEFAULT_TEST_PG_URL)


def _maintenance_url(pg_url: str) -> str:
    """Return a URL to the ``postgres`` maintenance database on the same server.

    Keeps host, port and credentials of the target and only swaps the database
    name, so CREATE/DROP DATABASE is issued from a connection that is not the
    target itself.
    """
    return (
        make_url(pg_url)
        .set(database="postgres")
        .render_as_string(hide_password=False)
    )


def _assert_safe_pg_target(pg_url: str) -> None:
    """Abort if the resolved test target is the application database.

    The comparison is by database NAME (not host/port): a copied TEST_PG_URL can
    point anywhere while still naming the app database. The only way to proceed
    is an explicit TEST_PG_ALLOW_APP_DB=1 (c-32 D3). This runs BEFORE any
    destructive DDL.
    """
    if os.environ.get(ALLOW_APP_DB_ENV) == "1":
        return

    target = _database_name(pg_url)
    app_db = _app_database_name()
    if app_db is not None and target == app_db:
        raise UnsafeTestDatabaseError(
            f"Unsafe test database target: '{target}' is the application "
            f"database declared by DATABASE_URL. Refusing to run destructive "
            f"DDL against it. Point TEST_PG_URL at a disposable database "
            f"(for example 'mesa_de_ayuda_test') or, only for dedicated "
            f"ephemeral environments, set {ALLOW_APP_DB_ENV}=1 to acknowledge "
            f"the risk explicitly."
        )


def _should_provision_disposable_database() -> bool:
    """True only when TEST_PG_URL was not explicitly provided (c-32 D4)."""
    return not os.environ.get("TEST_PG_URL")


async def _ensure_database_async(pg_url: str) -> None:
    """CREATE the disposable database if missing via a maintenance connection."""
    db_name = _database_name(pg_url)
    engine = create_async_engine(
        _maintenance_url(pg_url), isolation_level="AUTOCOMMIT"
    )
    try:
        async with engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if exists is None:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await engine.dispose()


async def _drop_database_async(pg_url: str) -> None:
    """DROP the disposable database, forcing out any lingering connection."""
    db_name = _database_name(pg_url)
    engine = create_async_engine(
        _maintenance_url(pg_url), isolation_level="AUTOCOMMIT"
    )
    try:
        async with engine.connect() as conn:
            await conn.execute(
                text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)')
            )
    finally:
        await engine.dispose()


def _provision_disposable_database(pg_url: str) -> bool:
    """Best-effort CREATE DATABASE. Returns False (with a warning) on fallback.

    Never aborts: the caller already applied the safety guard, so a failed
    provisioning only degrades to the schema lifecycle on the resolved target
    (c-32 D4 fallback).
    """
    try:
        asyncio.run(_ensure_database_async(pg_url))
        return True
    except Exception as exc:
        warnings.warn(
            f"Could not provision the disposable database "
            f"'{_database_name(pg_url)}' via a maintenance connection to "
            f"'postgres'. Continuing with the schema lifecycle on the resolved "
            f"target. Reason: {exc}",
            stacklevel=2,
        )
        return False


def _drop_disposable_database(pg_url: str) -> None:
    """Best-effort DROP DATABASE with a visible warning if it cannot be removed."""
    try:
        asyncio.run(_drop_database_async(pg_url))
    except Exception as exc:
        db_name = _database_name(pg_url)
        warnings.warn(
            f"Could not drop the disposable database '{db_name}'. Remove it "
            f'manually with: DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE);. '
            f"Reason: {exc}",
            stacklevel=2,
        )


@pytest.fixture(scope="session")
def pg_schema():
    """Crea (una sola vez por sesión) el esquema PostgreSQL de integración.

    Fixture SINCRÓNICO con su propio event loop (`asyncio.run`) para que el DDL
    no dependa del loop de pytest-asyncio. Con el motor en scope `function`
    (D1), hacer create_all/drop_all por test provocaba que `drop_all` —que
    requiere un lock ACCESS EXCLUSIVE— quedara bloqueado por un lock dejado por
    un test anterior (cuelgue observado en el 5º test de integración, que en
    aislamiento pasa en 1.26 s). Acá el esquema se recrea UNA vez: drop_all +
    create_all, arrancando de una base limpia sin depender de restos de
    corridas previas.

    Si PostgreSQL no está disponible, FALLA RUIDOSAMENTE (D2), nunca skip.

    c-32: el DDL destructivo corre contra una base DESCARTABLE. Antes de tocar
    nada, `_assert_safe_pg_target` aborta si el destino nombra la base de la
    aplicación. Cuando `TEST_PG_URL` no está definida, la base descartable se
    crea vía conexión de mantenimiento y se elimina al finalizar la sesión; con
    `TEST_PG_URL` explícita (CI) se usa tal cual, sin crear ni eliminar.
    """
    pg_url = _get_pg_url()

    # Safety guard (c-32 D3): abort BEFORE any destructive DDL if the resolved
    # target names the application database. Runs before provisioning too.
    _assert_safe_pg_target(pg_url)

    # Disposable provisioning (c-32 D4): only when TEST_PG_URL was not set.
    # With an explicit TEST_PG_URL (CI), the provided database is used as-is.
    provisioned = False
    if _should_provision_disposable_database():
        provisioned = _provision_disposable_database(pg_url)

    async def _reset() -> None:
        engine = create_async_engine(pg_url, echo=False)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Catalogo de referencia: se siembra UNA vez por sesion. Sembrarlo y
            # borrarlo por test producia un deadlock: el DELETE de catalogo del
            # teardown de seed_pg_catalogs quedaba bloqueado por la transaccion
            # idle-in-transaction de pg_session (diagnosticado via pg_stat_activity).
            factory = async_sessionmaker(engine, expire_on_commit=False)
            async with factory() as session:
                session.add_all(
                    [
                        Estado(
                            nombre="nuevo",
                            descripcion="Incidente recibido, sin asignar",
                            es_terminal=False,
                        ),
                        Sector(nombre="Seguridad Informatica", descripcion="Ciberseguridad"),
                        Sector(nombre="Soporte Tecnico Hardware", descripcion="Equipos y perifericos"),
                        Sector(nombre="Soporte Tecnico Software", descripcion="Aplicaciones de escritorio"),
                        Sector(nombre="Bases de Datos", descripcion="Motores y consultas"),
                        Sector(nombre="Sistemas", descripcion="Infraestructura y redes"),
                        CanalOrigen(nombre="correo electrónico", descripcion="Vía Outlook"),
                        CanalOrigen(nombre="formulario web", descripcion="API REST directa"),
                        CanalOrigen(nombre="llamada telefónica", descripcion="Vía Twilio"),
                    ]
                )
                await session.commit()
        finally:
            await engine.dispose()

    try:
        asyncio.run(_reset())
    except Exception as e:
        pytest.fail(
            f"PostgreSQL no disponible en {pg_url}. "
            "Levantá el servicio con 'docker compose up -d postgres' antes de "
            "correr la suite de integración (pytest -m integration). "
            f"Error original: {e}"
        )

    yield

    async def _drop() -> None:
        engine = create_async_engine(pg_url, echo=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        finally:
            await engine.dispose()

    asyncio.run(_drop())

    # Dispose of the disposable database itself (c-32 D4 teardown). Only when
    # this session provisioned it; an explicit TEST_PG_URL is left untouched.
    if provisioned:
        _drop_disposable_database(pg_url)


@pytest_asyncio.fixture
async def pg_engine(pg_schema):
    """Motor PostgreSQL async por test, SIN DDL (el esquema lo maneja pg_schema).

    Scope function (D1): con `asyncio_default_fixture_loop_scope = function`,
    este fixture y cada test consumidor corren en el MISMO event loop. asyncpg
    ata cada conexión al loop que la creó; un motor de scope sesión consumido
    por tests de función producía `RuntimeError: ... attached to a different
    loop`. `loop_scope="session"` NO resuelve esto con asyncpg (verificado).

    No ejecuta create_all/drop_all: eso se movió a `pg_schema`, una vez por
    sesión, para evitar el bloqueo de locks entre tests.
    """
    engine = create_async_engine(_get_pg_url(), echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def pg_session(pg_engine):
    """PostgreSQL session with transaction rollback isolation (C-19).

    Scope function: a new session per test, rolled back at teardown.
    Mirrors the db_session fixture pattern for SQLite.
    """
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        # Rollback explicito (no `session.begin()` que hace commit al salir):
        # un test cuyo flush falla a proposito (p. ej. IntegrityError esperado)
        # deja la transaccion en estado fallido; commitearla al salir fallaba y
        # dejaba locks colgados. El rollback libera siempre.
        await session.rollback()


@pytest_asyncio.fixture
async def pg_client(pg_engine):
    """Async HTTP client backed by PostgreSQL (C-19).

    Overrides get_db_session to use the PostgreSQL engine instead of
    the default SQLite engine. Authentication is bypassed with the
    same test_user mock used by the SQLite client fixture.

    Fire-and-forget webhook calls are mocked to avoid external HTTP.
    """
    app = create_app()

    async def override_db():
        """Override get_db_session to use the PostgreSQL engine."""
        factory = async_sessionmaker(pg_engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db

    # Bypass authentication — same mock as in SQLite client fixture
    async def override_auth():
        return User(id=1, username="test_user", hashed_password="", is_active=True)
    app.dependency_overrides[get_current_user] = override_auth

    # Mock N8N webhook to avoid external HTTP calls
    with patch(
        "app.services.incidente_service.notify_n8n",
        new_callable=AsyncMock,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac
            # Drain pending fire-and-forget tasks
            await asyncio.sleep(0)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine():
    """
    Motor SQLite en memoria compartido por toda la sesión de testing.

    Se crea una sola vez y se reutiliza en todos los tests para evitar
    el overhead de recrear el esquema en cada función de test. El esquema
    se genera al inicio mediante create_all() y se elimina al finalizar
    cuando el motor es descartado.

    Scope session: el motor persiste durante toda la ejecución de pytest.
    Loop scope session explícito: con `asyncio_default_fixture_loop_scope`
    declarado en pytest.ini, este fixture debe fijar su propio loop para
    conservar el comportamiento previo (ver design.md D1).

    FK enforcement (design.md D3): se registra un listener sobre el evento
    'connect' del engine para ejecutar `PRAGMA foreign_keys=ON` en cada
    conexión nueva. SQLite lo tiene OFF por defecto, por lo que sin este
    listener las violaciones de integridad referencial quedan ocultas.
    El listener aplica al engine compartido, que es el mismo que consumen
    db_session, client, make_client_with_classifier y seed_catalogs, incluida
    la conexión que abre el cliente ASGI por request.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        """Habilita el enforcement de claves foráneas en cada conexión SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        # Crear todas las tablas definidas en los modelos ORM
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Liberar recursos al finalizar todos los tests
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """
    Sesión de base de datos con rollback automático tras cada test.

    Garantiza el aislamiento entre tests: cualquier dato insertado o
    modificado durante la ejecución de un test es revertido al finalizar,
    dejando la base de datos en el mismo estado para el siguiente test.

    Scope function (default): una nueva sesión por función de test.

    Args:
        engine: Motor compartido de la sesión de testing.

    Yields:
        Sesión de SQLAlchemy lista para usar dentro del test.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()  # Revertir cambios del test para aislamiento


@pytest_asyncio.fixture
async def client(engine):
    """
    Cliente HTTP asíncrono con la dependencia de base de datos reemplazada.

    Utiliza ASGITransport de httpx para ejecutar la aplicación FastAPI
    directamente en memoria, sin levantar un servidor HTTP real. La
    dependencia get_db_session es sobrescrita con una versión que usa
    la base de datos SQLite de test en lugar de PostgreSQL.

    Args:
        engine: Motor compartido de la sesión de testing.

    Yields:
        Cliente HTTP asíncrono listo para realizar solicitudes a la API.
    """
    app = create_app()

    async def override_db():
        """Versión de get_db_session que usa la base de datos de test."""
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Reemplazar la dependencia de producción con la versión de test
    app.dependency_overrides[get_db_session] = override_db

    # Bypass de autenticacion: todos los tests heredados usan un usuario mock.
    # Los tests de auth usan su propio fixture que no tiene este override.
    async def override_auth():
        return User(id=1, username="test_user", hashed_password="", is_active=True)
    app.dependency_overrides[get_current_user] = override_auth

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def seed_catalogs(engine):
    """
    Siembra registros de catálogo mínimos necesarios para los tests de integración.

    IncidenteService.create_and_classify resuelve por nombre:
      - Estado "nuevo"   → requerido para inicializar todo incidente.
      - Sector (×5)      → vocabulario canonico C-27 (sin tildes).
      - CanalOrigen (×3) → correo electrónico, formulario web, llamada telefónica.

    Estrategia de aislamiento:
        Usa el engine directamente con commit explícito (no db_session que hace
        rollback), porque el cliente ASGI abre su propia sesión por request.
        Limpia las filas sembradas (y los incidentes/logs asociados) al finalizar
        el test, previniendo filtración de datos entre tests.

    Yields:
        dict con los objetos sembrados organizados por tipo para referencia en tests.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)

    # ── Arrange: sembrar catálogos ────────────────────────────────────────────
    async with factory() as session:
        # Todos los estados del ciclo de vida (cerrado es el unico terminal)
        estado_nuevo = Estado(nombre="nuevo", descripcion="Incidente recibido, sin asignar", es_terminal=False)
        estado_en_proceso = Estado(nombre="en proceso", descripcion="Asignado y en atencion", es_terminal=False)
        estado_en_espera = Estado(nombre="en espera", descripcion="Bloqueado esperando respuesta", es_terminal=False)
        estado_resuelto = Estado(nombre="resuelto", descripcion="Solucion aplicada", es_terminal=False)
        estado_cerrado = Estado(nombre="cerrado", descripcion="Finalizado", es_terminal=True)

        sector_seguridad = Sector(nombre="Seguridad Informatica", descripcion="Ciberseguridad")
        sector_hardware = Sector(nombre="Soporte Tecnico Hardware", descripcion="Equipos y perifericos")
        sector_software = Sector(nombre="Soporte Tecnico Software", descripcion="Aplicaciones de escritorio")
        sector_bases_datos = Sector(nombre="Bases de Datos", descripcion="Motores y consultas")
        sector_sistemas = Sector(nombre="Sistemas", descripcion="Infraestructura y redes")
        canal_correo = CanalOrigen(nombre="correo electrónico", descripcion="Vía Outlook")
        canal_formulario = CanalOrigen(nombre="formulario web", descripcion="API REST directa")
        canal_llamada = CanalOrigen(nombre="llamada telefónica", descripcion="Vía Twilio")

        session.add_all([
            estado_nuevo, estado_en_proceso, estado_en_espera, estado_resuelto, estado_cerrado,
            sector_seguridad, sector_hardware, sector_software, sector_bases_datos, sector_sistemas,
            canal_correo, canal_formulario, canal_llamada,
        ])
        await session.commit()

        # Refrescar para obtener IDs asignados
        for obj in [estado_nuevo, estado_en_proceso, estado_en_espera, estado_resuelto, estado_cerrado,
                    sector_seguridad, sector_hardware, sector_software, sector_bases_datos, sector_sistemas,
                    canal_correo, canal_formulario, canal_llamada]:
            await session.refresh(obj)

        catalog = {
            "estado_nuevo": estado_nuevo,
            "estado_en_proceso": estado_en_proceso,
            "estado_en_espera": estado_en_espera,
            "estado_resuelto": estado_resuelto,
            "estado_cerrado": estado_cerrado,
            "sector_seguridad": sector_seguridad,
            "sector_hardware": sector_hardware,
            "sector_software": sector_software,
            "sector_bases_datos": sector_bases_datos,
            "sector_sistemas": sector_sistemas,
            "canal_correo": canal_correo,
            "canal_formulario": canal_formulario,
            "canal_llamada": canal_llamada,
        }

    yield catalog

    # ── Teardown: limpiar incidentes/logs y luego catálogos ───────────────────
    # El orden importa por las FK: primero limpiar tablas dependientes.
    async with factory() as session:
        # Importar modelos aquí para evitar importación circular en el módulo
        from app.models.asociaciones import (
            clasificacion_sector_predicho,
            clasificacion_sector_validado,
            incidente_sector_adicional,
        )
        from app.models.clasificacion_log import ClasificacionLog
        from app.models.incidente import Incidente

        await session.execute(delete(clasificacion_sector_predicho))
        await session.execute(delete(clasificacion_sector_validado))
        await session.execute(delete(incidente_sector_adicional))
        await session.execute(delete(ClasificacionLog))
        await session.execute(delete(Incidente))
        await session.execute(delete(CanalOrigen))
        await session.execute(delete(Estado))
        await session.execute(delete(Sector))
        await session.commit()


@pytest.fixture
def make_client_with_classifier(engine):
    """
    Factory de clientes HTTP con clasificador inyectado como doble de prueba.

    Retorna una función asíncrona que construye un AsyncClient con:
      - La dependencia get_db_session sobrescrita para usar la base de test.
      - La dependencia get_service (incidentes) sobrescrita para usar un
        IncidenteService con un AsyncMock.classify que devuelve el
        ClasificacionResult dado.

    Uso en tests:
        async with make_client_with_classifier(result) as c:
            response = await c.post(...)

    Args:
        result: ClasificacionResult que el clasificador doble debe devolver.

    Returns:
        AsyncContextManager que provee el cliente listo para usar.
    """
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _make(result: ClasificacionResult):
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

        def _build_service_override(classification_result: ClasificacionResult):
            """Crea el factory de servicio con el clasificador doble."""
            async def _factory(session: AsyncSession = Depends(get_db_session)):
                fake_classifier = AsyncMock()
                fake_classifier.classify = AsyncMock(return_value=classification_result)
                return IncidenteService(session, classifier=fake_classifier)
            return _factory

        app.dependency_overrides[get_db_session] = override_db
        app.dependency_overrides[get_incidente_service] = _build_service_override(result)

        # Bypass de autenticacion — mismo mock que en el fixture client
        async def override_auth():
            return User(id=1, username="test_user", hashed_password="", is_active=True)
        app.dependency_overrides[get_current_user] = override_auth

        with patch(
            "app.services.incidente_service.notify_n8n",
            new_callable=AsyncMock,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as ac:
                yield ac
                # Drenar tareas fire-and-forget pendientes
                await asyncio.sleep(0)

    return _make


# ── PostgreSQL Integration Fixtures (C-19) ──────────────────────────────────


@pytest_asyncio.fixture
async def seed_pg_catalogs(pg_engine):
    """Devuelve el catalogo de referencia ya sembrado por `pg_schema`.

    SOLO LECTURA. Antes este fixture insertaba y borraba los catalogos en cada
    test; su teardown (`DELETE FROM canal_origen`, etc.) quedaba bloqueado por
    la transaccion idle-in-transaction de `pg_session`, produciendo un deadlock
    (cuelgue del 5º test de integracion, diagnosticado con `pg_stat_activity`:
    un DELETE esperando un `Lock: transactionid` mientras otro backend estaba
    `idle in transaction`). El sembrado ahora ocurre UNA vez por sesion en
    `pg_schema`; aca solo se consulta y se arma el mismo diccionario que
    consumen los tests, de modo que la interfaz del fixture no cambia.

    El catalogo sembrado replica `seed_catalogs` (SQLite):
      - Estado "nuevo"
      - Sector (x5): vocabulario canonico C-27 (sin tildes)
      - CanalOrigen (x3): correo electronico, formulario web, llamada telefonica
    """
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    async with factory() as session:
        sectores = {s.nombre: s for s in (await session.scalars(select(Sector))).all()}
        canales = {
            c.nombre: c for c in (await session.scalars(select(CanalOrigen))).all()
        }
        estado_nuevo = (
            await session.scalars(select(Estado).where(Estado.nombre == "nuevo"))
        ).one()

        yield {
            "estado_nuevo": estado_nuevo,
            "sector_seguridad": sectores["Seguridad Informatica"],
            "sector_hardware": sectores["Soporte Tecnico Hardware"],
            "sector_software": sectores["Soporte Tecnico Software"],
            "sector_bases_datos": sectores["Bases de Datos"],
            "sector_sistemas": sectores["Sistemas"],
            "canal_correo": canales["correo electrónico"],
            "canal_formulario": canales["formulario web"],
            "canal_llamada": canales["llamada telefónica"],
        }
