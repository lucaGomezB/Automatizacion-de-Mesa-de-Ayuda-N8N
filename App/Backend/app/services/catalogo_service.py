"""
Servicio de catálogos de solo lectura (C-27).

Responsabilidad:
    Expone los catálogos de referencia que el frontend consume en runtime.
    En este cambio se limita a los sectores, ordenados según el vocabulario
    canónico de `app.constants.SECTORES_CANONICOS`.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import SECTORES_CANONICOS
from app.models.catalog import Sector
from app.repositories.sector_repository import SectorRepository

_ORDEN_CANONICO = {nombre: i for i, nombre in enumerate(SECTORES_CANONICOS)}


class CatalogoService:
    """Servicio de lectura para catálogos de referencia."""

    def __init__(self, session: AsyncSession) -> None:
        self._sector_repo = SectorRepository(session)

    async def list_sectores(self) -> list[Sector]:
        """
        Retorna los sectores del catálogo ordenados de forma canónica.

        Los sectores desconocidos (no canónicos) se ordenan al final para no
        romper la respuesta ante datos legacy.
        """
        sectores = await self._sector_repo.list_all(limit=100)
        return sorted(
            sectores,
            key=lambda s: (_ORDEN_CANONICO.get(s.nombre, len(_ORDEN_CANONICO)), s.nombre),
        )
