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
                     (Estado "nuevo", tres Sector, tres CanalOrigen). Limpia al finalizar.
    make_client_with_classifier: Factory que devuelve un AsyncClient con el clasificador
                     inyectado como doble de prueba (dependency_override de get_service).

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
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
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


@pytest_asyncio.fixture(scope="session")
async def engine():
    """
    Motor SQLite en memoria compartido por toda la sesión de testing.

    Se crea una sola vez y se reutiliza en todos los tests para evitar
    el overhead de recrear el esquema en cada función de test. El esquema
    se genera al inicio mediante create_all() y se elimina al finalizar
    cuando el motor es descartado.

    Scope session: el motor persiste durante toda la ejecución de pytest.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
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
      - Sector (×3)      → Sistemas, Operaciones, Soporte Técnico.
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
        estado_nuevo = Estado(nombre="nuevo", descripcion="Incidente recibido, sin asignar", es_terminal=False)
        sector_sistemas = Sector(nombre="Sistemas", descripcion="Infraestructura y redes")
        sector_operaciones = Sector(nombre="Operaciones", descripcion="Procesos operativos")
        sector_soporte = Sector(nombre="Soporte Técnico", descripcion="Equipamiento de usuarios")
        canal_correo = CanalOrigen(nombre="correo electrónico", descripcion="Vía Outlook")
        canal_formulario = CanalOrigen(nombre="formulario web", descripcion="API REST directa")
        canal_llamada = CanalOrigen(nombre="llamada telefónica", descripcion="Vía Twilio")

        session.add_all([
            estado_nuevo,
            sector_sistemas, sector_operaciones, sector_soporte,
            canal_correo, canal_formulario, canal_llamada,
        ])
        await session.commit()

        # Refrescar para obtener IDs asignados
        for obj in [estado_nuevo, sector_sistemas, sector_operaciones, sector_soporte,
                    canal_correo, canal_formulario, canal_llamada]:
            await session.refresh(obj)

        catalog = {
            "estado_nuevo": estado_nuevo,
            "sector_sistemas": sector_sistemas,
            "sector_operaciones": sector_operaciones,
            "sector_soporte": sector_soporte,
            "canal_correo": canal_correo,
            "canal_formulario": canal_formulario,
            "canal_llamada": canal_llamada,
        }

    yield catalog

    # ── Teardown: limpiar incidentes/logs y luego catálogos ───────────────────
    # El orden importa por las FK: primero limpiar tablas dependientes.
    async with factory() as session:
        # Importar modelos aquí para evitar importación circular en el módulo
        from app.models.clasificacion_log import ClasificacionLog
        from app.models.incidente import Incidente

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
