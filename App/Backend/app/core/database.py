"""
Módulo de infraestructura de base de datos.

Responsabilidad:
    Configura y expone el motor asíncrono de SQLAlchemy, la fábrica de sesiones
    y la clase base declarativa que comparten todos los modelos ORM del sistema.
    También provee la dependencia de inyección get_db_session(), que gestiona
    el ciclo de vida de cada sesión de base de datos dentro de una solicitud HTTP.

Decisiones de diseño:
    - Se utiliza asyncpg como driver para PostgreSQL, lo que permite operaciones
      de E/S no bloqueantes compatibles con el event loop de FastAPI/uvicorn.
    - expire_on_commit=False evita consultas adicionales de refresco automático
      luego de cada commit, reduciendo la latencia de respuesta.
    - El manejo de commit/rollback se centraliza en get_db_session() y no en
      los repositorios, preservando la separación de responsabilidades.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import get_settings

# Se accede a settings una sola vez a nivel de módulo para reutilizar
# la instancia cacheada y evitar lecturas repetidas del archivo .env.
settings = get_settings()

# Motor asíncrono principal de la aplicación.
# El pool de conexiones está dimensionado según los parámetros de Settings
# para soportar carga concurrente sin agotar recursos del servidor PostgreSQL.
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,   # Activa el log SQL en modo debug
    future=True,              # Activa la API de SQLAlchemy 2.0
)

# Fábrica de sesiones asíncronas reutilizable en toda la aplicación.
# autoflush=False y autocommit=False delegan el control transaccional
# explícitamente a la dependencia get_db_session().
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita lazy-load automático tras commit
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """
    Clase base declarativa de SQLAlchemy compartida por todos los modelos ORM.

    Todos los modelos del sistema heredan de esta clase para que Alembic
    pueda detectar automáticamente los cambios de esquema y generar
    las migraciones correspondientes.
    """
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia de FastAPI que provee una sesión de base de datos por solicitud.

    Implementa el patrón Unit of Work:
        1. Abre una sesión vinculada a la transacción actual.
        2. Hace yield para que el handler de la ruta ejecute su lógica.
        3. Si no hubo excepción, confirma la transacción con commit.
        4. Si ocurrió una excepción, revierte todos los cambios con rollback.
        5. En ambos casos, cierra la sesión y devuelve la conexión al pool.

    Este diseño garantiza que cada solicitud HTTP opere con una transacción
    atómica y que los recursos de base de datos sean liberados correctamente.

    IMPORTANTE — Por qué el rollback tiene su propio try/except:
        Si la excepción original proviene de un fallo de conectividad con
        PostgreSQL (p. ej. DB caída, AmbiguousForeignKeysError de SQLAlchemy),
        el rollback intentaría usar la misma conexión rota y lanzaría una
        SEGUNDA excepción. Python encadenaría ambas (exception chaining) y
        la segunda propagaría hacia arriba, confundiendo al unhandled_handler
        y potencialmente causando que la excepción escapara de ExceptionMiddleware
        sin que CORSMiddleware agregara los headers de Access-Control-Allow-Origin.
        El try/except interno silencia el error de rollback y garantiza que solo
        la excepción original suba hasta los exception handlers de FastAPI.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            # Revertir cualquier operación pendiente ante fallo inesperado.
            # Si el rollback mismo falla (conexión caída, mapper roto), se ignora:
            # la excepción original ya está en el contexto de Python y es la que
            # FastAPI debe procesar para generar la respuesta de error correcta.
            try:
                await session.rollback()
            except Exception:
                pass
            raise
        finally:
            # Liberar la conexión al pool independientemente del resultado.
            # close() sobre una conexión ya rota es seguro: asyncpg lo maneja.
            await session.close()
