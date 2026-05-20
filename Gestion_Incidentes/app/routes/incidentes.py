"""
Endpoints HTTP para la gestión de incidentes.

Responsabilidad:
    Define las rutas de la API REST para las operaciones CRUD sobre incidentes.
    Esta capa es responsable exclusivamente de:
        - Recibir y deserializar el payload HTTP.
        - Delegar la lógica de negocio al IncidenteService.
        - Serializar y retornar la respuesta HTTP con el schema correcto.

    Ninguna regla de negocio debe residir en esta capa. Toda la lógica
    (validación de dominio, clasificación, resolución de catálogos)
    se delega al servicio correspondiente.

Rutas expuestas (prefijo /api/v1/incidentes):
    POST   /            → Crear un nuevo incidente y clasificarlo automáticamente.
    GET    /            → Listar incidentes con filtros opcionales y paginación.
    GET    /{id}        → Obtener el detalle completo de un incidente por ID.
    PATCH  /{id}        → Actualizar parcialmente los campos de un incidente.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.incidente import PrioridadEnum
from app.schemas.incidente import (
    IncidenteCreate,
    IncidenteListItem,
    IncidenteRead,
    IncidenteUpdate,
)
from app.services.incidente_service import IncidenteService

# Prefijo /incidentes; el prefijo /api/v1 lo agrega register_routes() en routes/__init__.py
router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

# Alias de tipo para inyección de sesión de base de datos vía FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_service(session: SessionDep) -> IncidenteService:
    """
    Función de fábrica del servicio para la inyección de dependencias de FastAPI.

    Construye el IncidenteService con la sesión de la solicitud actual,
    garantizando que todos los repositorios internos del servicio compartan
    la misma transacción de base de datos.
    """
    return IncidenteService(session)


# Alias de tipo para inyección del servicio como dependencia
ServiceDep = Annotated[IncidenteService, Depends(get_service)]


@router.post(
    "/",
    response_model=IncidenteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear y clasificar un incidente",
)
async def create_incidente(
    payload: IncidenteCreate, service: ServiceDep
) -> IncidenteRead:
    """
    Crea un nuevo incidente y ejecuta la clasificación automática.

    Invocado por N8N tras recibir un correo electrónico en Outlook o una
    transcripción de llamada de Twilio, o directamente desde un cliente HTTP.

    El incidente se persiste en estado "nuevo" y es clasificado inmediatamente
    por el pipeline híbrido (determinístico + Gemini). El resultado incluye
    el sector asignado, la confianza de la clasificación y el indicador
    de revisión humana si la confianza fue insuficiente.

    Args:
        payload: Descripción pseudonimizada del incidente, prioridad y canal.

    Returns:
        Representación completa del incidente creado y clasificado (HTTP 201).
    """
    incidente = await service.create_and_classify(payload)
    return IncidenteRead.model_validate(incidente)


@router.get(
    "/",
    response_model=list[IncidenteListItem],
    summary="Listar incidentes con filtros opcionales",
)
async def list_incidentes(
    service: ServiceDep,
    sector_id: int | None = Query(None, description="Filtrar por sector responsable"),
    estado_id: int | None = Query(None, description="Filtrar por estado del ciclo de vida"),
    prioridad: PrioridadEnum | None = Query(None, description="Filtrar por nivel de prioridad"),
    requiere_revision_humana: bool | None = Query(
        None, description="Filtrar por indicador de revisión pendiente"
    ),
    desde: datetime | None = Query(None, description="Fecha de creación mínima (ISO 8601)"),
    hasta: datetime | None = Query(None, description="Fecha de creación máxima (ISO 8601)"),
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
) -> list[IncidenteListItem]:
    """
    Lista incidentes con filtros combinables y paginación.

    Todos los parámetros de filtro son opcionales y se combinan con AND lógico.
    El resultado se ordena por fecha de creación descendente (más reciente primero).
    Retorna la proyección ligera IncidenteListItem (sin texto de descripción)
    para optimizar el tamaño de la respuesta en consultas masivas.
    """
    incidentes = await service.list_incidentes(
        sector_id=sector_id,
        estado_id=estado_id,
        prioridad=prioridad,
        requiere_revision_humana=requiere_revision_humana,
        desde=desde,
        hasta=hasta,
        limit=limit,
        offset=offset,
    )
    return [IncidenteListItem.model_validate(i) for i in incidentes]


@router.get(
    "/{incidente_id}",
    response_model=IncidenteRead,
    summary="Obtener el detalle completo de un incidente",
)
async def get_incidente(
    incidente_id: int, service: ServiceDep
) -> IncidenteRead:
    """
    Retorna la representación completa de un incidente, incluyendo relaciones.

    A diferencia del listado, esta respuesta incluye la descripción completa
    del incidente y los objetos de catálogo completos (sector, estado, canal).

    Args:
        incidente_id: ID del incidente a recuperar.

    Returns:
        Detalle completo del incidente (HTTP 200) o error 404 si no existe.
    """
    incidente = await service.get_by_id(incidente_id)
    return IncidenteRead.model_validate(incidente)


@router.patch(
    "/{incidente_id}",
    response_model=IncidenteRead,
    summary="Actualizar parcialmente un incidente",
)
async def update_incidente(
    incidente_id: int, payload: IncidenteUpdate, service: ServiceDep
) -> IncidenteRead:
    """
    Actualiza uno o más campos de un incidente existente (PATCH semántico).

    Solo se modifican los campos incluidos en el payload con valor distinto
    de None. Casos de uso típicos: cambio de estado por el operador,
    reasignación de sector tras revisión manual, o modificación de prioridad.

    Args:
        incidente_id: ID del incidente a modificar.
        payload:      Campos a actualizar (todos opcionales).

    Returns:
        Representación actualizada del incidente (HTTP 200) o 404 si no existe.
    """
    incidente = await service.update_incidente(incidente_id, payload)
    return IncidenteRead.model_validate(incidente)
