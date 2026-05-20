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
    engine:     Motor SQLite en memoria (scope=session): compartido por todos los tests.
    db_session: Sesión con rollback automático tras cada test (scope=function).
    client:     Cliente HTTP asíncrono (ASGI) con la base de datos de test inyectada.

Estrategia de aislamiento:
    Cada test que usa db_session obtiene una sesión que se revierte al finalizar,
    garantizando que los datos de un test no afecten a los siguientes.
    El fixture 'client' sobrescribe la dependencia get_db_session con una función
    que usa la misma base de datos de test, asegurando consistencia.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db_session
from app.main import create_app

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

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
