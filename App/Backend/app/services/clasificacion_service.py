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

from app.core.exceptions import EntityNotFoundError
from app.core.logging import get_logger
from app.models.clasificacion_log import ClasificacionLog
from app.repositories.clasificacion_repository import ClasificacionRepository
from app.repositories.incidente_repository import IncidenteRepository
from app.repositories.sector_repository import SectorRepository
from app.services.incident_visibility import AlcanceIncidentes, ModoAlcance
from app.services.notification_recipient_service import NotificationRecipientService
from app.utils.n8n_webhook import notify_n8n_post_revision

logger = get_logger(__name__)

# Tareas fire-and-forget del aviso post-revision; se retienen hasta completar
# (un `asyncio.create_task` sin referencia puede ser recolectado por el GC).
_post_revision_tasks: set = set()


def _dispatch_post_revision(
    incidente_id: int, sectores: list[int], destinatarios: list[str]
) -> None:
    """Programa el aviso post-revision fire-and-forget conservando su referencia."""
    import asyncio

    task = asyncio.create_task(
        notify_n8n_post_revision(incidente_id, sectores, destinatarios)
    )
    _post_revision_tasks.add(task)
    task.add_done_callback(_post_revision_tasks.discard)


class _AlcanceVacio:
    """Sentinela de alcance VACIO para `_reportante_filtro` (D4).

    Distingue "cola completa" (None, alcance GLOBAL) de "cola vacia por alcance"
    (esta sentinela). Sin ella, un None ambiguo no permitiria decidir si el
    servicio debe devolver una lista vacia/0 sin consultar la base.
    """


# Instancia unica del sentinela: la comparacion es por identidad.
_VACIO = _AlcanceVacio()



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
        # IncidenteRepository para propagar la validación al incidente (misma transacción)
        self._incidente_repo = IncidenteRepository(session)
        # Sesión retenida: la resolucion de destinatarios post-revision (NR-008)
        # construye su servicio con la misma sesion/transaccion.
        self._session = session

    async def list_by_incidente(
        self, incidente_id: int, alcance: AlcanceIncidentes | None = None
    ) -> list[ClasificacionLog]:
        """
        Retorna el historial completo de clasificaciones de un incidente.

        Útil para que el operador pueda ver el registro de todas las decisiones
        tomadas por el sistema (incluyendo reintentos o correcciones anteriores)
        antes de emitir su validación.

        Si se provee `alcance` (VIS-001 extendido a clasificaciones), se aplica
        la misma regla de visibilidad por rol que en los incidentes: un incidente
        fuera del alcance del usuario se comporta como no encontrado (404), sin
        revelar su existencia ni su historial de clasificaciones.

        Args:
            incidente_id: ID del incidente cuyo historial se consulta.
            alcance:      Alcance de visibilidad por rol (opcional).

        Returns:
            Lista de registros de auditoría ordenados de más reciente a más antiguo.

        Raises:
            EntityNotFoundError: Si el incidente no existe o queda fuera del alcance.
        """
        if alcance is not None:
            await self._verificar_alcance_incidente(incidente_id, alcance)
        return await self._repo.list_by_incidente(incidente_id)

    async def list_pending_review(
        self,
        limit: int = 50,
        offset: int = 0,
        alcance: AlcanceIncidentes | None = None,
    ) -> list[ClasificacionLog]:
        """
        Retorna la cola de clasificaciones que requieren revisión humana.

        Un registro aparece en esta cola cuando:
            - El clasificador marcó el caso como de baja confianza (< 0.70).
            - El operador aún no ha registrado su validación.

        El orden FIFO garantiza que los incidentes más antiguos reciban
        atención prioritaria, evitando inanición en la cola de revisión.

        Si se provee `alcance` (VIS-002), la cola se acota por alcance:
            - GLOBAL: cola completa (administrador / mesa_de_ayuda).
            - PROPIO: solo los pendientes cuyo incidente reportó el empleado.
            - VACIO: lista vacía.

        Args:
            limit:   Cantidad máxima de resultados para paginación.
            offset:  Desplazamiento para paginación.
            alcance: Alcance de visibilidad por rol (opcional).

        Returns:
            Lista de registros pendientes ordenados por antigüedad (FIFO).
        """
        reportante_filtro = self._reportante_filtro(alcance)
        if reportante_filtro is _VACIO:
            return []
        return await self._repo.list_pending_review(
            limit=limit, offset=offset, reportante_empleado_id=reportante_filtro
        )

    async def count_pending_review(
        self, alcance: AlcanceIncidentes | None = None
    ) -> int:
        """
        Cuenta la cola de clasificaciones que requieren revisión humana (VIS-006).

        Reutiliza la MISMA derivación de alcance que `list_pending_review` (D4):
            - GLOBAL: cuenta toda la cola.
            - PROPIO: cuenta solo los pendientes cuyo incidente reportó el empleado.
            - VACIO:  devuelve 0 SIN consultar la base de datos.

        El total coincide con la cantidad de elementos del listado equivalente
        sin paginar, porque repositorio, listado y conteo comparten la definición
        de "pendiente" (requiere_revision_humana == True Y sector_id_validado IS NULL).

        Args:
            alcance: Alcance de visibilidad por rol (opcional).

        Returns:
            Cantidad total de registros pendientes dentro del alcance.
        """
        reportante_filtro = self._reportante_filtro(alcance)
        if reportante_filtro is _VACIO:
            return 0
        return await self._repo.count_pending_review(
            reportante_empleado_id=reportante_filtro
        )

    def _reportante_filtro(
        self, alcance: AlcanceIncidentes | None
    ) -> int | None | _AlcanceVacio:
        """
        Traduce el alcance a un filtro `reportante_empleado_id` (D4).

        Compartido por `list_pending_review` y `count_pending_review` para que
        listado y conteo NO divergan. La derivación rol -> alcance vive en
        `incident_visibility` (VIS-002); este método solo la proyecta:

            - None         → sin filtro (alcance GLOBAL o ausente): cola completa.
            - int          → alcance PROPIO: solo lo reportado por ese empleado.
            - _VACIO       → alcance VACIO (o PROPIO sin empleado): sin resultados.
        """
        if alcance is None:
            return None
        if alcance.modo is ModoAlcance.VACIO:
            return _VACIO
        if alcance.modo is ModoAlcance.PROPIO:
            if alcance.reportante_empleado_id is None:
                return _VACIO
            return alcance.reportante_empleado_id
        return None

    async def validate(
        self,
        log_id: int,
        sector_id: int,
        sectores_adicionales: list[str] | None = None,
        alcance: AlcanceIncidentes | None = None,
    ) -> ClasificacionLog:
        """
        Registra la validación humana de una clasificación.

        El operador indica cuál es el sector principal correcto para el incidente
        y, opcionalmente, el conjunto de sectores adicionales validados. Si el
        clasificador acertó, sector_id coincidirá con sector_id_predicho.

        La verificación de los sectores antes de la asignación previene que un
        sector inexistente quede registrado como etiqueta de verdad.

        Si se provee `alcance` (VIS-001 extendido a clasificaciones), se verifica
        el alcance del incidente ANTES de cualquier mutación: un log cuyo incidente
        queda fuera del alcance del usuario responde como no encontrado (404) y
        NUNCA modifica el log ni el incidente.

        Args:
            log_id:                 ID del registro de clasificación a validar.
            sector_id:              ID del sector principal correcto.
            sectores_adicionales:   Nombres canónicos de los sectores secundarios validados.
            alcance:                Alcance de visibilidad por rol (opcional).

        Returns:
            Instancia actualizada del ClasificacionLog con todas sus relaciones.

        Raises:
            EntityNotFoundError: Si el log_id, el sector principal, un adicional
                                 no existen, o el incidente queda fuera de alcance.
        """
        # Verificar el alcance ANTES de mutar (misma regla que la lectura).
        if alcance is not None:
            log_previo = await self._repo.get_by_id(log_id)
            await self._verificar_alcance_incidente(log_previo.incidente_id, alcance)

        # Verificar que el sector de validación existe antes de asignarlo
        await self._sector_repo.get_by_id(sector_id)

        log = await self._repo.set_validated_sector(log_id, sector_id)

        # Persistir el conjunto validado adicional (N-a-N)
        if sectores_adicionales:
            adjuntos = await self._sector_repo.get_by_nombres(sectores_adicionales)
            faltantes = [n for n in sectores_adicionales if n not in adjuntos]
            if faltantes:
                raise EntityNotFoundError("Sector", ", ".join(faltantes))
            await self._repo.set_sectores_validados(log, list(adjuntos.values()))
            log = await self._repo.get_with_relations(log_id)

        # Propagar el veredicto al incidente en la misma transacción: el ticket
        # queda asignado al sector validado y sale del estado "requiere revisión".
        # La auditoría no se altera: el log conserva sector_id_predicho intacto.
        await self._incidente_repo.update_fields(
            log.incidente_id,
            sector_id=sector_id,
            requiere_revision_humana=False,
        )

        # c-86 (NR-008): una vez que el incidente paso la revision humana, se
        # resuelve y avisa (fire-and-forget) a los `gestion_incidentes` ACTIVOS
        # de los sectores validados. No bloquea ni altera la respuesta.
        sector_ids = {sector_id}
        if sectores_adicionales:
            sector_ids |= {s.id for s in adjuntos.values()}
        destinatarios = await NotificationRecipientService(
            self._session
        ).resolver_destinatarios_gestion(sorted(sector_ids))
        _dispatch_post_revision(
            log.incidente_id, sorted(sector_ids), destinatarios
        )

        logger.info(
            "clasificacion_validated",
            log_id=log_id,
            incidente_id=log.incidente_id,
            sector_id_validado=sector_id,
            sectores_adicionales=sectores_adicionales or [],
        )
        return log

    async def validate_payload(
        self, log_id: int, payload, alcance: AlcanceIncidentes | None = None
    ) -> ClasificacionLog:
        """
        Resuelve el payload de validación (id o nombre) y delega en validate().

        Acepta `sector_id_validado` (compatibilidad) o `sector_validado` (nombre
        canónico) y propaga los `sectores_adicionales` validados.

        Raises:
            EntityNotFoundError: Si el nombre de sector no existe en el catálogo,
                                 o el incidente queda fuera del alcance.
        """
        sector_id = payload.sector_id_validado
        if sector_id is None:
            sector = await self._sector_repo.get_by_nombre(payload.sector_validado)
            if sector is None:
                raise EntityNotFoundError("Sector", str(payload.sector_validado))
            sector_id = sector.id
        return await self.validate(
            log_id, sector_id, payload.sectores_adicionales, alcance=alcance
        )

    async def _verificar_alcance_incidente(
        self, incidente_id: int, alcance: AlcanceIncidentes
    ) -> None:
        """
        Verifica que el incidente exista y esté dentro del alcance del usuario.

        Reutiliza la regla de `incident_visibility` (AlcanceIncidentes) para no
        duplicar la lógica; la ausencia o el fuera-de-alcance se reportan ambos
        como no encontrado (404), sin revelar la existencia.

        Raises:
            EntityNotFoundError: Si el incidente no existe o queda fuera del alcance.
        """
        incidente = await self._incidente_repo.get_with_relations(incidente_id)
        if incidente is None or not alcance.permite_incidente(incidente):
            raise EntityNotFoundError("Incidente", incidente_id)
