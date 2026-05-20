"""
Endpoints HTTP para auditoría y revisión humana de clasificaciones.

Responsabilidad:
    Expone las rutas de la API REST para consultar el historial de clasificaciones
    y para que los operadores humanos validen o corrijan las predicciones del
    sistema. Estas rutas son el punto de interacción del operador con la cola
    de revisión pendiente.

    La distinción entre estos endpoints y los de incidentes es intencional:
    la clasificación es un proceso independiente del ciclo de vida del incidente.
    Un incidente puede tener múltiples registros de clasificación a lo largo del
    tiempo (por ejemplo, si fue reclasificado manualmente).

Rutas expuestas (prefijo /api/v1/clasificaciones):
    GET   /revision-pendiente          → Cola de clasificaciones sin revisar (FIFO).
    GET   /incidente/{id}              → Historial de clasificaciones de un incidente.
    PATCH /{log_id}/validar            → Registrar la decisión del operador humano.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.clasificacion import ClasificacionLogRead, ClasificacionValidar
from app.services.clasificacion_service import ClasificacionService

# Prefijo /clasificaciones; el prefijo /api/v1 lo agrega register_routes()
router = APIRouter(prefix="/clasificaciones", tags=["Clasificaciones"])

# Alias de tipo para inyección de sesión vía FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_service(session: SessionDep) -> ClasificacionService:
    """
    Función de fábrica del servicio para la inyección de dependencias de FastAPI.

    Construye el ClasificacionService con la sesión activa de la solicitud.
    """
    return ClasificacionService(session)


# Alias de tipo para inyección del servicio
ServiceDep = Annotated[ClasificacionService, Depends(get_service)]


@router.get(
    "/revision-pendiente",
    response_model=list[ClasificacionLogRead],
    summary="Listar clasificaciones que requieren revisión humana",
)
async def list_pending_review(
    service: ServiceDep,
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
) -> list[ClasificacionLogRead]:
    """
    Retorna la cola de clasificaciones pendientes de revisión humana.

    Un registro aparece en esta cola cuando el clasificador emitió
    una confianza inferior al umbral (0.70) y el operador aún no registró
    su validación. El orden FIFO (más antiguo primero) garantiza que
    ningún incidente quede en espera indefinidamente.

    Returns:
        Lista de registros de auditoría pendientes, ordenados por antigüedad.
    """
    logs = await service.list_pending_review(limit=limit, offset=offset)
    return [ClasificacionLogRead.model_validate(log) for log in logs]


@router.get(
    "/incidente/{incidente_id}",
    response_model=list[ClasificacionLogRead],
    summary="Historial de clasificaciones de un incidente",
)
async def list_by_incidente(
    incidente_id: int, service: ServiceDep
) -> list[ClasificacionLogRead]:
    """
    Retorna el historial completo de clasificaciones de un incidente específico.

    Permite al operador ver todas las decisiones tomadas por el sistema
    para un incidente (incluyendo el registro de la etapa utilizada,
    la confianza, y la respuesta raw de Gemini si corresponde).

    Args:
        incidente_id: ID del incidente cuyo historial se desea consultar.

    Returns:
        Lista de registros de auditoría ordenados del más reciente al más antiguo.
    """
    logs = await service.list_by_incidente(incidente_id)
    return [ClasificacionLogRead.model_validate(log) for log in logs]


@router.patch(
    "/{log_id}/validar",
    response_model=ClasificacionLogRead,
    summary="Registrar la validación humana de una clasificación",
)
async def validar_clasificacion(
    log_id: int, payload: ClasificacionValidar, service: ServiceDep
) -> ClasificacionLogRead:
    """
    Registra la decisión del operador humano sobre la categoría correcta.

    Este endpoint cierra el ciclo de revisión: el operador indica cuál es
    el sector correcto para el incidente, lo que actualiza el campo
    sector_id_validado en el registro de auditoría. A partir de ese momento,
    el registro deja de aparecer en la cola de revisión pendiente y
    pasa a formar parte del corpus de evaluación con etiqueta confirmada.

    Si el sector validado coincide con el predicho, confirma la exactitud
    del clasificador. Si difiere, registra un caso de error para el análisis
    de métricas de la tesis.

    Args:
        log_id:  ID del registro de auditoría a validar.
        payload: ID del sector correcto según el criterio del operador.

    Returns:
        Representación actualizada del registro de auditoría (HTTP 200).
    """
    log = await service.validate(log_id, payload.sector_id_validado)
    return ClasificacionLogRead.model_validate(log)
