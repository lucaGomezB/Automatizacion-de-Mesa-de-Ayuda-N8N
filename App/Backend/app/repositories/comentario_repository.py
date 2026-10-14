"""
Repositorio de comentarios de incidente (c-86, D7).

Append-only: expone el alta y el listado ordenado cronologicamente ascendente.
No existe operacion de edicion ni de borrado de una entrada.
"""

from sqlalchemy import select

from app.models.incidente import IncidenteComentario
from app.repositories.base import BaseRepository


class IncidenteComentarioRepository(BaseRepository[IncidenteComentario]):
    """Acceso a datos de los comentarios de un incidente."""

    model = IncidenteComentario

    async def listar_por_incidente(self, incidente_id: int) -> list[IncidenteComentario]:
        """Devuelve las entradas en orden cronologico ascendente (mas antigua primero)."""
        result = await self._session.execute(
            select(IncidenteComentario)
            .where(IncidenteComentario.incidente_id == incidente_id)
            .order_by(IncidenteComentario.created_at.asc(), IncidenteComentario.id.asc())
        )
        return list(result.scalars().all())

    async def crear(
        self,
        *,
        incidente_id: int,
        autor_empleado_id: int | None,
        texto: str,
    ) -> IncidenteComentario:
        """Persiste una nueva entrada append-only con autor y fecha."""
        return await self.create(
            incidente_id=incidente_id,
            autor_empleado_id=autor_empleado_id,
            texto=texto,
        )
