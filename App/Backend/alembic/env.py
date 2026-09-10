"""
Entorno de ejecución de migraciones de Alembic.

Responsabilidad:
    Configura Alembic para ejecutar migraciones de esquema de forma asíncrona,
    compatible con el motor asyncpg utilizado en producción. La URL de la
    base de datos se toma de Settings (y por ende del archivo .env), evitando
    la necesidad de duplicar la configuración en alembic.ini.

    Soporta dos modos de ejecución:
        - Offline: genera scripts SQL sin conexión activa (útil para revisión de migraciones).
        - Online: ejecuta las migraciones directamente contra la base de datos.

    La importación de app.models.Base garantiza que todos los modelos ORM
    estén registrados en el metadata antes de que Alembic compare el
    esquema actual con el esquema objetivo para detectar diferencias.

Comandos habituales de Alembic:
    alembic upgrade head          → Aplica todas las migraciones pendientes.
    alembic downgrade -1          → Revierte la última migración aplicada.
    alembic revision --autogenerate -m "descripcion"  → Genera nueva migración.
    alembic current               → Muestra la revisión actual de la base de datos.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config.settings import get_settings

# Importación crítica: registra todos los modelos ORM en Base.metadata
# para que Alembic pueda detectar cambios de esquema automáticamente.
from app.models import Base  # noqa: F401

config = context.config
settings = get_settings()

# Inyectar la URL de la base de datos desde Settings, sobreescribiendo
# el placeholder de alembic.ini. Esto mantiene una única fuente de verdad.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configurar el logging de Alembic según el archivo alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de todos los modelos ORM; Alembic usa esto como esquema objetivo
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecuta migraciones en modo offline (sin conexión activa).

    Genera scripts SQL que pueden ser revisados antes de aplicarlos,
    útil para auditoría en entornos de producción con acceso restringido.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,        # Genera SQL con valores literales
        dialect_opts={"paramstyle": "named"},
        compare_type=True,         # Detecta cambios de tipo de columna
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Ejecuta las migraciones sobre la conexión activa proporcionada.

    Esta función es llamada por run_async_migrations() dentro del
    contexto de la conexión asíncrona.

    Args:
        connection: Conexión síncrona de SQLAlchemy (requerida por Alembic).
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detecta cambios de tipo de columna en --autogenerate
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Crea un motor asíncrono temporal y ejecuta las migraciones en modo online.

    Usa NullPool para evitar que las conexiones del pool queden abiertas
    tras la ejecución del comando alembic, lo que podría bloquear el servidor.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Sin pool: cada migración usa su propia conexión
    )
    async with connectable.connect() as connection:
        # Alembic requiere una API síncrona; run_sync() adapta la conexión async
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Punto de entrada para la ejecución online de migraciones.

    Ejecuta el coroutine de migraciones en un event loop nuevo,
    independientemente del event loop de la aplicación FastAPI.
    """
    asyncio.run(run_async_migrations())


# Punto de decisión: Alembic determina el modo según el contexto de ejecución
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
