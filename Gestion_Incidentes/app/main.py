"""
Punto de entrada principal de la aplicación FastAPI.

Responsabilidad:
    Define la función de fábrica create_app() que construye y configura la
    instancia de FastAPI de forma programática. Este patrón de fábrica
    facilita la creación de instancias independientes para testing sin
    afectar la instancia de producción.

    La función lifespan() gestiona el ciclo de vida de la aplicación:
    inicializa el logging al arranque y libera el pool de conexiones al cierre,
    garantizando un shutdown limpio en entornos containerizados.

Convenciones:
    - La documentación interactiva (/docs, /redoc) solo se habilita en modo debug
      para evitar exposición de la API en entornos de producción.
    - El CORS está configurado permisivo por defecto; restringirlo según el
      entorno de despliegue antes de producción.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.database import engine
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging
from app.routes import register_routes


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Contexto de ciclo de vida de la aplicación (startup / shutdown).

    FastAPI ejecuta el bloque anterior al yield al iniciar el servidor
    y el bloque posterior al yield cuando el servidor se cierra.

    Acciones al inicio:
        - Configura el sistema de logging estructurado antes de que
          cualquier componente emita su primer evento.

    Acciones al cierre:
        - Libera todas las conexiones del pool de SQLAlchemy para
          evitar conexiones huérfanas en la base de datos PostgreSQL.
    """
    # ── Startup ───────────────────────────────────────────────────────────────
    configure_logging()
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Fábrica de la aplicación FastAPI.

    Construye y configura la instancia con todos sus componentes:
    middleware de CORS, manejadores de errores y rutas de la API.
    Al centralizar la creación en una función, los tests pueden
    invocarla independientemente para obtener instancias aisladas.

    Returns:
        Instancia configurada y lista para servir solicitudes HTTP.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        # La documentación interactiva solo se expone en modo debug
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── Middleware de CORS ─────────────────────────────────────────────────────
    # Configuración permisiva apropiada para un entorno de desarrollo y tesis.
    # En producción, limitar allow_origins al dominio del frontend o de N8N.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Registro de componentes ───────────────────────────────────────────────
    register_error_handlers(app)  # Manejadores de excepción → respuestas HTTP
    register_routes(app)          # Rutas de la API bajo /api/v1 y /health

    return app


# Instancia global utilizada por uvicorn al ejecutar:
#   uvicorn app.main:app --host 0.0.0.0 --port 8000
app = create_app()
