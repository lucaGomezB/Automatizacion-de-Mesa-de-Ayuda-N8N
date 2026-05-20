"""
Endpoints de verificación de salud del sistema.

Responsabilidad:
    Expone dos endpoints estándar de monitoreo que permiten a orquestadores
    de contenedores (Docker, Kubernetes) y sistemas de monitoreo (Grafana,
    Uptime Robot) verificar el estado del servicio:

        GET /health    → Liveness probe: ¿el proceso está corriendo?
        GET /health/db → Readiness probe: ¿la base de datos es alcanzable?

    La distinción entre liveness y readiness es importante en entornos
    containerizados: un pod puede estar vivo pero no listo para recibir
    tráfico si la base de datos aún no está disponible.

    En el docker-compose.yml, el servicio 'api' usa /health/db como condición
    de salud antes de comenzar a servir solicitudes de clasificación.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session

router = APIRouter(tags=["Health"])

# Alias de tipo para la inyección de sesión de base de datos
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    """
    Verificación de actividad del proceso (liveness probe).

    Retorna inmediatamente sin acceder a ningún recurso externo.
    Confirma únicamente que el proceso uvicorn está corriendo y
    que la aplicación FastAPI fue inicializada correctamente.

    Returns:
        JSON con estado "ok" y la versión actual de la aplicación.
    """
    settings = get_settings()
    return {"status": "ok", "version": settings.app_version}


@router.get("/health/db", summary="Database readiness probe")
async def health_db(session: SessionDep) -> dict:
    """
    Verificación de conectividad con la base de datos (readiness probe).

    Ejecuta una consulta mínima (SELECT 1) para confirmar que la conexión
    a PostgreSQL está establecida y operativa. Si la base de datos no es
    alcanzable, SQLAlchemy lanzará una excepción que el manejador global
    convertirá en una respuesta 500.

    Utilizado por el healthcheck del servicio 'api' en docker-compose.yml
    para evitar que el API comience a servir solicitudes antes de que
    la base de datos esté lista.

    Returns:
        JSON con estado "ok" y confirmación de conectividad.
    """
    # Consulta mínima que no accede a ninguna tabla; solo valida la conexión
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
