"""
Repositorio para la entidad Sector.

Responsabilidad:
    Extiende BaseRepository con una consulta especializada para resolver
    el nombre de categoría producido por el clasificador (ej. "Sistemas")
    al registro correspondiente en la tabla de catálogo. Esta operación
    es el puente entre la salida del clasificador y la capa de persistencia.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Sector
from app.repositories.base import BaseRepository


class SectorRepository(BaseRepository[Sector]):
    """
    Repositorio de acceso a datos para la entidad Sector.

    Hereda las operaciones CRUD genéricas de BaseRepository y agrega
    el método get_by_nombre(), que es el único acceso específico de dominio
    necesario para esta entidad: la resolución de nombre de categoría → registro.
    """

    model = Sector

    async def get_by_nombre(self, nombre: str) -> Sector | None:
        """
        Busca un sector por su nombre exacto.

        Utilizado por la capa de servicio para convertir la categoría predicha
        por el clasificador (cadena de texto) en el ID del sector correspondiente,
        que luego se almacena como FK en la tabla incidente.

        La comparación es exacta e incluye sensibilidad a mayúsculas, lo cual
        es intencional dado que los nombres del catálogo tienen capitalización
        específica definida en la tesis: "Sistemas", "Operaciones", "Soporte Técnico".

        Args:
            nombre: Nombre exacto del sector a buscar.

        Returns:
            Instancia de Sector o None si no existe ningún sector con ese nombre.
        """
        result = await self._session.execute(
            select(Sector).where(Sector.nombre == nombre)
        )
        return result.scalar_one_or_none()
