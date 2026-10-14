"""
Repositorio para la entidad Estado.

Responsabilidad:
    Extiende BaseRepository con la consulta especializada que resuelve el
    nombre de un estado del ciclo de vida (por ejemplo "nuevo") al registro
    correspondiente del catalogo. Es el unico acceso especifico de dominio
    que la capa de servicio necesita para inicializar un incidente.

    La existencia de este repositorio permite que IncidenteService deje de
    consultar el ORM directamente a traves de la sesion (regla de disciplina
    de capas del proyecto, ERR-004).
"""

from sqlalchemy import select

from app.models.catalog import Estado
from app.repositories.base import BaseRepository


class EstadoRepository(BaseRepository[Estado]):
    """Repositorio de acceso a datos para la entidad Estado."""

    model = Estado

    async def get_by_nombre(self, nombre: str) -> Estado | None:
        """
        Busca un estado por su nombre exacto.

        Args:
            nombre: Nombre exacto del estado (ej. "nuevo").

        Returns:
            Instancia de Estado o None si no existe ningun estado con ese nombre.
        """
        result = await self._session.execute(
            select(Estado).where(Estado.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def get_terminal(self) -> Estado | None:
        """
        Devuelve el estado TERMINAL del ciclo de vida (c-86).

        Es el estado con `es_terminal=True` (hoy `cerrado`). Se resuelve por el
        flag y no por el nombre hardcodeado, de modo que el modelo de cierre no
        dependa de una cadena (D3/D12).
        """
        result = await self._session.execute(
            select(Estado).where(Estado.es_terminal.is_(True)).order_by(Estado.id)
        )
        return result.scalars().first()
