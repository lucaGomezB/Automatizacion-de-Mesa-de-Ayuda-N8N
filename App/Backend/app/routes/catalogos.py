"""
Endpoints HTTP de catálogos de referencia (C-27).

Rutas expuestas (prefijo /api/v1/catalogos):
    GET /sectores → Lista de solo lectura [{ id, nombre }] de los 5 sectores.

El frontend consume este endpoint en runtime para construir las opciones de
sector sin depender de IDs numéricos fijos (design.md D4).
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.catalog import SectorCatalogoRead
from app.services.catalogo_service import CatalogoService

router = APIRouter(prefix="/catalogos", tags=["Catalogos"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_service(session: SessionDep) -> CatalogoService:
    return CatalogoService(session)


ServiceDep = Annotated[CatalogoService, Depends(get_service)]


@router.get(
    "/sectores",
    response_model=list[SectorCatalogoRead],
    summary="Listar el catálogo de sectores",
)
async def list_sectores(
    service: ServiceDep,
    current_user: User = Depends(get_current_user),
) -> list[SectorCatalogoRead]:
    """
    Retorna los sectores del catálogo como pares { id, nombre }.

    Solo lectura: los catálogos son datos de referencia inmutables en runtime.
    El orden respeta el vocabulario canónico.
    """
    sectores = await service.list_sectores()
    return [SectorCatalogoRead.model_validate(s) for s in sectores]
