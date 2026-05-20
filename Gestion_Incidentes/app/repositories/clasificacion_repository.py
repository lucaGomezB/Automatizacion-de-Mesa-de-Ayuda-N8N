"""
Repositorio para la entidad ClasificacionLog.

Responsabilidad:
    Implementa las consultas específicas para gestionar el registro de
    auditoría de clasificaciones. Provee dos funcionalidades de negocio
    diferenciadas:
        1. Historial de clasificaciones de un incidente específico.
        2. Cola de revisión pendiente: registros que requieren validación humana
           y que aún no han sido corregidos (sector_id_validado es NULL).

    Este repositorio es central para la evaluación experimental de la tesis:
    los registros aquí almacenados, una vez validados, forman el corpus de
    200 casos etiquetados utilizado para calcular accuracy y F1 por categoría.
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.clasificacion_log import ClasificacionLog
from app.repositories.base import BaseRepository


class ClasificacionRepository(BaseRepository[ClasificacionLog]):
    """
    Repositorio de acceso a datos para la entidad ClasificacionLog.

    Extiende el CRUD genérico con consultas orientadas a los dos flujos
    principales de uso: auditoría de un incidente y revisión humana en cola.
    """

    model = ClasificacionLog

    async def list_by_incidente(self, incidente_id: int) -> list[ClasificacionLog]:
        """
        Recupera el historial completo de clasificaciones de un incidente.

        Ordena los resultados de más reciente a más antiguo para que
        el operador vea primero la clasificación más actual. Carga las
        relaciones sector_predicho y sector_validado para evitar N+1 queries
        al serializar la respuesta.

        Args:
            incidente_id: ID del incidente cuyo historial se desea consultar.

        Returns:
            Lista de registros de auditoría ordenados por fecha descendente.
        """
        result = await self._session.execute(
            select(ClasificacionLog)
            .where(ClasificacionLog.incidente_id == incidente_id)
            .options(
                selectinload(ClasificacionLog.sector_predicho),
                selectinload(ClasificacionLog.sector_validado),
            )
            .order_by(ClasificacionLog.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_pending_review(
        self, limit: int = 50, offset: int = 0
    ) -> list[ClasificacionLog]:
        """
        Lista las clasificaciones que requieren revisión humana y aún no fueron validadas.

        Un registro está "pendiente de revisión" cuando:
            - requiere_revision_humana == True (el clasificador no tuvo confianza suficiente).
            - sector_id_validado IS NULL (el operador aún no corrigió la categoría).

        El orden ascendente por created_at implementa la política FIFO:
        los incidentes más antiguos tienen mayor prioridad de atención.

        Args:
            limit:  Cantidad máxima de registros a retornar.
            offset: Desplazamiento para paginación.

        Returns:
            Lista de registros pendientes de revisión ordenados por antigüedad.
        """
        result = await self._session.execute(
            select(ClasificacionLog)
            # Filtro 1: el clasificador marcó el caso como de baja confianza
            .where(ClasificacionLog.requiere_revision_humana == True)  # noqa: E712
            # Filtro 2: el operador aún no validó la categoría
            .where(ClasificacionLog.sector_id_validado == None)  # noqa: E711
            .options(
                selectinload(ClasificacionLog.sector_predicho),
                selectinload(ClasificacionLog.incidente),
            )
            .order_by(ClasificacionLog.created_at.asc())  # FIFO: más antiguo primero
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def set_validated_sector(
        self, log_id: int, sector_id: int
    ) -> ClasificacionLog:
        """
        Registra la categoría validada manualmente por el operador humano.

        Este método cierra el ciclo de revisión humana: al asignar sector_id_validado,
        el registro deja de aparecer en la cola de revisión pendiente y pasa a
        ser parte del corpus de evaluación con etiqueta de verdad confirmada.

        Args:
            log_id:    ID del registro de auditoría a validar.
            sector_id: ID del sector correcto según el criterio del operador.

        Returns:
            Instancia actualizada del ClasificacionLog.

        Raises:
            EntityNotFoundError: Si no existe el registro con ese ID.
        """
        instance = await self.get_by_id(log_id)
        instance.sector_id_validado = sector_id  # Asignar la etiqueta de verdad
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance
