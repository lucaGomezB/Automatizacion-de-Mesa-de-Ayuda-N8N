"""
Endpoints HTTP para estadisticas y analitica del dashboard.

Responsabilidad:
    Define las rutas de la API REST para consultas agregadas de incidentes.
    Esta capa es responsable de:
        - Recibir y validar los query params.
        - Delegar la logica de agregacion al EstadisticasService.
        - Serializar y retornar la respuesta HTTP.

Rutas expuestas (prefijo /api/v1/estadisticas):
    GET /tendencias → Serie temporal agrupada por dia/mes con filtros.
    GET /resumen    → KPIs agregados con distribuciones.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.estadisticas import (
    AgruparPorEnum,
    ResumenResponse,
    TendenciasRequest,
    TendenciasResponse,
)
from app.services.estadisticas_service import EstadisticasService

router = APIRouter(prefix="/estadisticas", tags=["Estadisticas"])

# Alias de tipo para inyeccion de dependencias
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_service(session: SessionDep) -> EstadisticasService:
    """Fabrica del servicio de estadisticas con la sesion de la request actual."""
    return EstadisticasService(session)


ServiceDep = Annotated[EstadisticasService, Depends(get_service)]


@router.get(
    "/tendencias",
    response_model=TendenciasResponse,
    summary="Obtener tendencias de incidentes agrupadas por dia o mes",
)
async def get_tendencias(
    agrupar_por: Annotated[
        AgruparPorEnum,
        Query(description="Granularidad de agrupacion: 'dia' o 'mes'"),
    ],
    desde: Annotated[date, Query(description="Fecha de inicio del rango (YYYY-MM-DD)")],
    hasta: Annotated[date, Query(description="Fecha de fin del rango (YYYY-MM-DD)")],
    sector_id: Annotated[
        int | None,
        Query(description="Filtrar por sector responsable (opcional)"),
    ] = None,
    service: ServiceDep = None,
    current_user: User = Depends(get_current_user),
) -> TendenciasResponse:
    """
    Retorna una serie temporal con la cantidad de incidentes por periodo
    (dia o mes) dentro del rango de fechas especificado.

    Incluye desglose por sector y distribucion de estados para el rango completo.
    """
    data = await service.get_tendencias(
        agrupar_por=agrupar_por.value,
        desde=desde,
        hasta=hasta,
        sector_id=sector_id,
    )
    return TendenciasResponse(**data)


@router.get(
    "/resumen",
    response_model=ResumenResponse,
    summary="Obtener resumen de KPIs del dashboard",
)
async def get_resumen(
    desde: Annotated[
        date | None,
        Query(description="Fecha de inicio del rango. Default: 30 dias atras."),
    ] = None,
    hasta: Annotated[
        date | None,
        Query(description="Fecha de fin del rango. Default: hoy."),
    ] = None,
    service: ServiceDep = None,
    current_user: User = Depends(get_current_user),
) -> ResumenResponse:
    """
    Retorna KPIs agregados: total de incidentes, promedio diario,
    distribucion por sector y estado, y tasa de revision humana.

    Si no se especifican fechas, se usa el rango de los ultimos 30 dias.
    """
    data = await service.get_resumen(desde=desde, hasta=hasta)
    return ResumenResponse(**data)
