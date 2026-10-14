"""
Servicio de comentarios de incidente (c-86, incident-comments).

Responsabilidad:
    Alta y listado APPEND-ONLY de comentarios sobre un incidente. El permiso se
    deriva de la misma regla de visibilidad que la lectura (ICM-002): un
    incidente fuera del alcance del usuario se comporta como no encontrado (404).
    No existe edicion ni borrado de entradas.
"""

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.empleado import Empleado
from app.models.incidente import IncidenteComentario
from app.repositories.comentario_repository import IncidenteComentarioRepository
from app.repositories.incidente_repository import IncidenteRepository

if TYPE_CHECKING:
    from app.services.incident_visibility import AlcanceIncidentes

__all__ = ["ComentarioService"]


class ComentarioService:
    """Logica de negocio de los comentarios append-only del incidente."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = IncidenteComentarioRepository(session)
        self._incidente_repo = IncidenteRepository(session)

    async def listar(
        self,
        incidente_id: int,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> list[IncidenteComentario]:
        """Lista las entradas del incidente; 404 si esta fuera del alcance."""
        await self._verificar_alcance(incidente_id, alcance)
        return await self._repo.listar_por_incidente(incidente_id)

    async def agregar(
        self,
        incidente_id: int,
        texto: str,
        actor: Empleado | None,
        alcance: "AlcanceIncidentes | None" = None,
    ) -> IncidenteComentario:
        """Persiste una nueva entrada; 404 si el incidente esta fuera del alcance."""
        await self._verificar_alcance(incidente_id, alcance)
        autor_id = actor.id if actor is not None else None
        return await self._repo.crear(
            incidente_id=incidente_id,
            autor_empleado_id=autor_id,
            texto=texto,
        )

    async def _verificar_alcance(
        self, incidente_id: int, alcance: "AlcanceIncidentes | None"
    ) -> None:
        """Verifica que el incidente exista y este dentro del alcance (misma regla que la lectura)."""
        incidente = await self._incidente_repo.get_with_relations(incidente_id)
        if incidente is None or (
            alcance is not None and not alcance.permite_incidente(incidente)
        ):
            raise EntityNotFoundError("Incidente", incidente_id)
