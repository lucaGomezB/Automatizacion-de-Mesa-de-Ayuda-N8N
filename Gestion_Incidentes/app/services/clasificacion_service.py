"""
Servicio para el flujo de revisión humana de clasificaciones.

Responsabilidad:
    Implementa la lógica de negocio del proceso de validación manual:
    consultar la cola de clasificaciones pendientes y registrar la decisión
    del operador humano sobre la categoría correcta.

    Este servicio es clave para la evaluación experimental de la tesis:
    las validaciones registradas aquí conforman las etiquetas de verdad
    del corpus de 200 casos utilizados para medir exactitud y F1 por categoría.

    La separación de este servicio respecto a IncidenteService sigue el
    principio de responsabilidad única: uno gestiona el ciclo de vida del
    incidente; el otro gestiona el flujo de auditoría y revisión.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.clasificacion_log import ClasificacionLog
from app.repositories.clasificacion_repository import ClasificacionRepository
from app.repositories.sector_repository import SectorRepository

logger = get_logger(__name__)


class ClasificacionService:
    """
    Servicio de lógica de negocio para la gestión de registros de clasificación.

    Coordina las operaciones de consulta y validación de registros de auditoría,
    actuando como intermediario entre los endpoints HTTP y los repositorios
    de persistencia.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa el servicio con sus repositorios dependientes.

        Ambos repositorios comparten la misma sesión para garantizar que
        las operaciones de validación ocurran en la misma transacción.

        Args:
            session: Sesión de base de datos activa para la solicitud actual.
        """
        self._repo = ClasificacionRepository(session)
        # SectorRepository para verificar que el sector de validación existe
        self._sector_repo = SectorRepository(session)

    async def list_by_incidente(self, incidente_id: int) -> list[ClasificacionLog]:
        """
        Retorna el historial completo de clasificaciones de un incidente.

        Útil para que el operador pueda ver el registro de todas las decisiones
        tomadas por el sistema (incluyendo reintentos o correcciones anteriores)
        antes de emitir su validación.

        Args:
            incidente_id: ID del incidente cuyo historial se consulta.

        Returns:
            Lista de registros de auditoría ordenados de más reciente a más antiguo.
        """
        return await self._repo.list_by_incidente(incidente_id)

    async def list_pending_review(
        self, limit: int = 50, offset: int = 0
    ) -> list[ClasificacionLog]:
        """
        Retorna la cola de clasificaciones que requieren revisión humana.

        Un registro aparece en esta cola cuando:
            - El clasificador marcó el caso como de baja confianza (< 0.70).
            - El operador aún no ha registrado su validación.

        El orden FIFO garantiza que los incidentes más antiguos reciban
        atención prioritaria, evitando inanición en la cola de revisión.

        Args:
            limit:  Cantidad máxima de resultados para paginación.
            offset: Desplazamiento para paginación.

        Returns:
            Lista de registros pendientes ordenados por antigüedad (FIFO).
        """
        return await self._repo.list_pending_review(limit=limit, offset=offset)

    async def validate(self, log_id: int, sector_id: int) -> ClasificacionLog:
        """
        Registra la validación humana de una clasificación.

        El operador indica cuál es el sector correcto para el incidente.
        Si el clasificador acertó, sector_id coincidirá con sector_id_predicho;
        si erró, será diferente. Ambos casos son igualmente valiosos para
        el análisis de métricas de la tesis.

        La verificación del sector antes de la asignación previene que un
        sector inexistente quede registrado como etiqueta de verdad, lo cual
        corrompería las métricas del corpus de evaluación.

        Args:
            log_id:    ID del registro de clasificación a validar.
            sector_id: ID del sector correcto según el criterio del operador.

        Returns:
            Instancia actualizada del ClasificacionLog con sector_id_validado asignado.

        Raises:
            EntityNotFoundError: Si el log_id o el sector_id no existen.
        """
        # Verificar que el sector de validación existe antes de asignarlo
        await self._sector_repo.get_by_id(sector_id)

        log = await self._repo.set_validated_sector(log_id, sector_id)

        logger.info(
            "clasificacion_validated",
            log_id=log_id,
            sector_id_validado=sector_id,
        )
        return log
