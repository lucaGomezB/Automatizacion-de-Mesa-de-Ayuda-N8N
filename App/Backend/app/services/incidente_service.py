"""
Servicio de gestión de incidentes.

Responsabilidad:
    Implementa la lógica de negocio relacionada con la creación, clasificación
    y actualización de incidentes. Es la capa que orquesta la interacción entre
    repositorios, el clasificador híbrido y las reglas de dominio del sistema.

    Las reglas de negocio aplicadas en esta capa (y no en repositorios o rutas):
        - Todo incidente nuevo se inicializa con estado "nuevo".
        - La clasificación se ejecuta inmediatamente después de la persistencia.
        - La asignación de sector y la creación del log de auditoría ocurren
          de forma atómica dentro de la misma transacción de base de datos.
        - El campo requiere_revision_humana del incidente refleja el resultado
          del clasificador sin intervención del operador.

Patrón de diseño:
    El servicio recibe la sesión de base de datos por inyección y construye
    los repositorios internamente, garantizando que todas las operaciones
    de escritura de una solicitud compartan la misma transacción.
"""

import asyncio
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.classifiers.hybrid import HybridClassifier
from app.config.settings import get_settings
from app.utils.n8n_webhook import notify_n8n
from app.utils.pseudonymizer import pseudonymize
from app.core.exceptions import (
    CanalOrigenNotFoundError,
    EntityNotFoundError,
    EstadoNotFoundError,
    IncidenteCerradoError,
    SectorNotFoundError,
)
from app.core.logging import get_logger
from app.models.base import utcnow
from app.models.catalog import CanalOrigen, Estado
from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.canal_origen_repository import CanalOrigenRepository
from app.repositories.clasificacion_repository import ClasificacionRepository
from app.repositories.estado_repository import EstadoRepository
from app.repositories.incidente_repository import IncidenteRepository
from app.repositories.sector_repository import SectorRepository
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import ClasificacionPrecalculada, IncidenteCreate, IncidenteUpdate

logger = get_logger(__name__)

# Nombre del estado inicial de todo incidente recién creado.
# Debe coincidir exactamente con el valor sembrado en la migración 001.
_ESTADO_NUEVO = "nuevo"

# Referencias retenidas de las tareas fire-and-forget de notificación a N8N.
# Un `asyncio.create_task` sin referencia puede ser recolectado por el GC antes
# de completarse; el set mantiene viva cada tarea hasta que termina, y el
# done_callback la descarta para no acumular memoria (BE B6 / D10).
_notification_tasks: set[asyncio.Task] = set()


def _dispatch_notification(incidente_id: int, result: ClasificacionResult) -> None:
    """
    Programa la notificación fire-and-forget a N8N conservando su referencia.

    Args:
        incidente_id: ID del incidente recién clasificado.
        result:       Resultado del clasificador híbrido.
    """
    task = asyncio.create_task(notify_n8n(incidente_id, result))
    _notification_tasks.add(task)
    task.add_done_callback(_notification_tasks.discard)


class IncidenteService:
    """
    Servicio que centraliza la lógica de negocio de la entidad Incidente.

    Actúa como coordinador entre el clasificador híbrido y los repositorios
    de persistencia. Garantiza que la clasificación y el registro de auditoría
    sean consistentes con el estado del incidente en la base de datos.
    """

    def __init__(
        self,
        session: AsyncSession,
        classifier: HybridClassifier | None = None,
    ) -> None:
        """
        Inicializa el servicio con sus dependencias.

        El parámetro classifier permite inyectar un mock durante los tests,
        evitando llamadas reales a la API de Gemini en el conjunto de pruebas.

        Args:
            session:    Sesión de base de datos activa para la solicitud actual.
            classifier: Instancia del clasificador híbrido (opcional; usa la real por defecto).
        """
        self._incidente_repo = IncidenteRepository(session)
        self._sector_repo = SectorRepository(session)
        self._estado_repo = EstadoRepository(session)
        self._canal_repo = CanalOrigenRepository(session)
        self._clasificacion_repo = ClasificacionRepository(session)
        self._classifier = classifier or HybridClassifier()
        # Referencia a la sesión para resolver colisiones de unicidad
        # (IntegrityError) en la idempotencia del alta (C-33, D4).
        self._session = session

    # ── Operaciones de Lectura ────────────────────────────────────────────────

    async def get_by_id(self, incidente_id: int) -> Incidente:
        """
        Recupera un incidente completo con todas sus relaciones cargadas.

        Args:
            incidente_id: Identificador del incidente a recuperar.

        Returns:
            Instancia de Incidente con relaciones eager-loaded.

        Raises:
            EntityNotFoundError: Si no existe un incidente con ese ID.
        """
        instance = await self._incidente_repo.get_with_relations(incidente_id)
        if instance is None:
            raise EntityNotFoundError("Incidente", incidente_id)
        return instance

    async def list_incidentes(
        self,
        sector_id: int | None = None,
        estado_id: int | None = None,
        prioridad: PrioridadEnum | None = None,
        requiere_revision_humana: bool | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Incidente]:
        """
        Lista incidentes aplicando filtros opcionales con soporte de paginación.

        Delega la construcción de la consulta al repositorio, que maneja
        la combinación dinámica de condiciones.

        Args:
            sector_id:               Filtrar por sector responsable.
            estado_id:               Filtrar por estado del ciclo de vida.
            prioridad:               Filtrar por nivel de prioridad.
            requiere_revision_humana: Filtrar por indicador de revisión pendiente.
            desde:                   Límite inferior de fecha de creación.
            hasta:                   Límite superior de fecha de creación.
            limit:                   Cantidad máxima de resultados.
            offset:                  Desplazamiento para paginación.

        Returns:
            Lista de incidentes que cumplen los criterios de filtrado.
        """
        return await self._incidente_repo.list_filtered(
            sector_id=sector_id,
            estado_id=estado_id,
            prioridad=prioridad,
            requiere_revision_humana=requiere_revision_humana,
            desde=desde,
            hasta=hasta,
            limit=limit,
            offset=offset,
        )

    # ── Operaciones de Escritura ──────────────────────────────────────────────

    async def create_and_classify(self, payload: IncidenteCreate) -> Incidente:
        """
        Crea un nuevo incidente y ejecuta la clasificación automática.

        Flujo de ejecución (C-03 doble representación — Ley 25.326):
            1. Resolver el estado "nuevo" del catálogo.
            2. Resolver el canal de origen si fue especificado.
            3. Pseudonimizar la descripción (punto canónico único) → doble repr.
            4. Persistir el incidente con descripcion_original (cifrada) y
               descripcion_pseudonimizada (en claro).
            5. Invocar el clasificador híbrido SOLO sobre la pseudonimizada.
            6. Actualizar el incidente con el sector asignado.
            7. Crear el registro de auditoría en clasificacion_log.
            8. Retornar el incidente completo con relaciones cargadas.

        Los pasos 4-7 ocurren dentro de la misma transacción de base de datos,
        garantizando que no queden incidentes sin log de clasificación ni
        logs de clasificación sin incidente asociado.

        Args:
            payload: Datos del incidente a crear (descripción, prioridad, canal).

        Returns:
            Instancia completa del incidente creado y clasificado.

        Raises:
            EstadoNotFoundError:     Si el estado "nuevo" no está en la base de datos.
            CanalOrigenNotFoundError: Si el canal_origen_id especificado no existe.
        """
        # Paso 0 (C-33, HIGH-4): cortocircuito idempotente por Message-ID.
        # Se resuelve ANTES de pseudonimizar y clasificar: un reintento del mismo
        # mensaje devuelve el incidente existente sin reclasificar ni notificar.
        if payload.origen_message_id is not None:
            existente = await self._incidente_repo.get_by_origen_message_id(
                payload.origen_message_id
            )
            if existente is not None:
                logger.info(
                    "incidente_idempotente",
                    origen_message_id=payload.origen_message_id,
                    incidente_id=existente.id,
                )
                return existente

        # Paso 1: Resolver el estado inicial desde el catálogo
        estado_nuevo = await self._resolve_estado(_ESTADO_NUEVO)

        # Paso 2: Resolver canal de origen (puede ser None si no se especificó)
        canal = await self._resolve_canal(payload.canal_origen_id)

        # Paso 3 (C-03): Pseudonimizar la descripción antes de persistir.
        # Punto canónico único: la pseudonimización ocurre aquí y nunca más.
        # El clasificador recibe SOLO la versión pseudonimizada.
        settings = get_settings()
        resultado_pseudo = pseudonymize(
            payload.descripcion,
            settings.pseudonymization_internal_domains,
        )
        logger.debug(
            "pseudonimizacion_cobertura",
            **resultado_pseudo.conteos,  # conteos por categoría, sin PII
        )

        # Paso 4: Crear el registro del incidente con doble representación.
        # La restricción UNIQUE de `origen_message_id` protege contra la carrera
        # de dos peticiones concurrentes con el mismo identificador (C-33, D4).
        try:
            incidente = await self._incidente_repo.create(
                descripcion_original=payload.descripcion,        # cifrada at-rest por EncryptedText
                descripcion_pseudonimizada=resultado_pseudo.texto,  # en claro, operativa
                prioridad=payload.prioridad,
                estado_id=estado_nuevo.id,
                canal_origen_id=canal.id if canal else None,
                origen_message_id=payload.origen_message_id,
                origen_evento=payload.origen_evento,
                ingresado_en=payload.ingresado_en,  # C-39: instante de ingreso al sistema
                requiere_revision_humana=False,  # Se actualizará tras la clasificación
            )
        except IntegrityError:
            # Colisión de unicidad por carrera: otra petición ya persistió el
            # mismo `origen_message_id`. Se re-consulta y se devuelve el ganador.
            await self._session.rollback()
            existente = await self._incidente_repo.get_by_origen_message_id(
                payload.origen_message_id
            )
            if existente is None:
                raise
            logger.info(
                "incidente_idempotente_carrera",
                origen_message_id=payload.origen_message_id,
                incidente_id=existente.id,
            )
            return existente

        logger.info("incidente_created", incidente_id=incidente.id)

        # Pasos 5-7: Clasificar sobre la pseudonimizada y persistir el resultado.
        # La clasificación precalculada, si viene, omite el clasificador pago.
        result = await self._resolve_classification(payload, resultado_pseudo.texto)
        await self._apply_classification(incidente, result)

        # C-39 (D2): sellar `persistido_en` UNA sola vez, dentro de la transaccion
        # de alta y clasificacion, en el punto en que finalizan las escrituras del
        # incidente y su log — inmediatamente antes del commit. Es inmutable: no
        # usa onupdate ni figura en IncidenteUpdate, por lo que un PATCH posterior
        # no lo sobrescribe (a diferencia de updated_at).
        incidente.persistido_en = utcnow()
        await self._session.flush()

        # Paso 7: Retornar el incidente completo con todas las relaciones
        return await self._incidente_repo.get_with_relations(incidente.id)  # type: ignore[return-value]

    async def _resolve_classification(
        self, payload: IncidenteCreate, texto_pseudonimizado: str
    ) -> ClasificacionResult:
        """
        Resuelve el resultado de clasificación del alta (C-33, D5).

        Si el payload trae un bloque `clasificacion` precalculado, se construye
        el resultado a partir de él SIN invocar al clasificador híbrido (evita la
        llamada paga). En caso contrario se conserva la clasificación
        server-side como hasta ahora.
        """
        if payload.clasificacion is not None:
            return self._result_from_precalculated(payload.clasificacion)
        return await self._classifier.classify(texto_pseudonimizado)

    @staticmethod
    def _result_from_precalculated(
        clasificacion: ClasificacionPrecalculada,
    ) -> ClasificacionResult:
        """
        Construye un `ClasificacionResult` a partir de la clasificación provista.

        El sector ausente se representa con cadena vacía y se persiste como
        `sector_id` nulo. El marcador de revisión humana explícito tiene
        prioridad; si no viene, se deriva del umbral sobre la confianza. El
        `origen` del emisor se conserva en `respuesta_raw` para auditoría.
        """
        confianza = clasificacion.confianza if clasificacion.confianza is not None else 0.0
        if clasificacion.requiere_revision_humana is not None:
            requiere_revision = clasificacion.requiere_revision_humana
        elif clasificacion.confianza is not None:
            requiere_revision = clasificacion.confianza < 0.70
        else:
            requiere_revision = False

        return ClasificacionResult(
            sector_predicho=clasificacion.sector_predicho or "",
            sectores_adicionales=list(clasificacion.sectores_adicionales),
            confianza=confianza,
            etapa="precalculada",
            requiere_revision_humana=requiere_revision,
            respuesta_raw=clasificacion.origen,
        )

    async def update_incidente(
        self, incidente_id: int, payload: IncidenteUpdate
    ) -> Incidente:
        """
        Actualiza parcialmente un incidente existente.

        Verifica la existencia del incidente antes de intentar la actualización
        para retornar un error 404 claro en lugar de una actualización silenciosa
        de cero filas. Solo se aplican los campos con valor distinto de None.

        Args:
            incidente_id: ID del incidente a actualizar.
            payload:      Campos a modificar (todos opcionales).

        Returns:
            Instancia actualizada del incidente con relaciones cargadas.

        Raises:
            EntityNotFoundError: Si no existe el incidente con ese ID.
        """
        # Verificar existencia antes de intentar la actualización.
        # get_by_id carga relaciones con selectinload, incluyendo estado.
        incidente = await self.get_by_id(incidente_id)

        # Bloquear escritura si el incidente está en estado terminal (cerrado).
        if incidente.estado.es_terminal:
            raise IncidenteCerradoError(incidente_id)

        # Verificar la existencia de las FKs de catálogo antes de persistir
        # (ERR-002). Sin esta validación, PostgreSQL rechaza el UPDATE con una
        # violación de integridad que el handler genérico traduce a 500, y en
        # motores sin enforcement la operación corrompe silenciosamente la
        # referencia.
        if payload.estado_id is not None:
            estado = await self._estado_repo.get_or_none(payload.estado_id)
            if estado is None:
                raise EstadoNotFoundError(
                    f"Estado con id={payload.estado_id} no encontrado en el catálogo."
                )

        if payload.sector_id is not None:
            sector = await self._sector_repo.get_or_none(payload.sector_id)
            if sector is None:
                raise SectorNotFoundError(
                    f"Sector con id={payload.sector_id} no encontrado en el catálogo."
                )

        updates = payload.model_dump(exclude_none=True)  # Solo campos no nulos
        await self._incidente_repo.update_fields(incidente_id, **updates)
        return await self.get_by_id(incidente_id)

    # ── Métodos Auxiliares Privados ───────────────────────────────────────────

    async def _apply_classification(
        self, incidente: Incidente, result: ClasificacionResult
    ) -> None:
        """
        Aplica el resultado del clasificador al incidente y crea el log de auditoría.

        Resuelve el nombre de categoría a un ID de sector, actualiza el incidente
        y crea el registro de clasificacion_log dentro de la misma transacción.

        Args:
            incidente: Instancia del incidente recién creado.
            result:    Resultado producido por el clasificador híbrido.
        """
        # Resolver sector principal (string) → sector (registro ORM con ID).
        # Un sector ausente (clasificación precalculada forzada a revisión) se
        # persiste como `sector_id` nulo (C-33, D5).
        sector = None
        if result.sector_predicho:
            sector = await self._sector_repo.get_by_nombre(result.sector_predicho)
        sector_id = sector.id if sector else None

        # Resolver el conjunto de sectores adicionales predichos (N-a-N).
        adicionales = await self._sector_repo.get_by_nombres(
            result.sectores_adicionales
        )
        adicionales_objs = list(adicionales.values())

        # Actualizar el incidente: sector principal + adicionales + bandera de revisión
        await self._incidente_repo.apply_classification(
            incidente,
            sector_id=sector_id,
            sectores_adicionales=adicionales_objs,
            requiere_revision_humana=result.requiere_revision_humana,
        )

        # Crear el registro de auditoría con todos los detalles de la clasificación
        log = await self._clasificacion_repo.create(
            incidente_id=incidente.id,
            sector_id_predicho=sector_id,
            confianza=result.confianza,
            etapa=result.etapa,
            requiere_revision_humana=result.requiere_revision_humana,
            respuesta_raw=result.respuesta_raw,
        )
        # Conjunto predicho adicional (el principal vive en sector_id_predicho)
        await self._clasificacion_repo.set_sectores_predichos(log, adicionales_objs)

        logger.info(
            "incidente_classified",
            incidente_id=incidente.id,
            sector_predicho=result.sector_predicho,
            sectores_adicionales=result.sectores_adicionales,
            confianza=result.confianza,
            etapa=result.etapa,
            requiere_revision_humana=result.requiere_revision_humana,
        )

        # Notificar a N8N de forma fire-and-forget: no bloquea la respuesta HTTP
        # ni propaga fallos (notify_n8n ya envuelve toda excepción en try/except).
        # La tarea conserva una referencia retenida hasta completar (BE B6).
        _dispatch_notification(incidente.id, result)

    async def _resolve_estado(self, nombre: str) -> Estado:
        """
        Resuelve el nombre de un estado al registro correspondiente del catálogo.

        Args:
            nombre: Nombre exacto del estado (ej. "nuevo").

        Returns:
            Instancia de Estado del catálogo.

        Raises:
            EstadoNotFoundError: Si el estado no existe (probable error de seed).
        """
        estado = await self._estado_repo.get_by_nombre(nombre)
        if estado is None:
            raise EstadoNotFoundError(
                f"Estado '{nombre}' no encontrado en el catálogo. "
                f"Verificar que la migración de seed fue ejecutada correctamente."
            )
        return estado

    async def _resolve_canal(self, canal_id: int | None) -> CanalOrigen | None:
        """
        Resuelve el ID de canal de origen al registro correspondiente del catálogo.

        Si canal_id es None, retorna None sin consultar la base de datos,
        lo que resulta en un incidente sin canal de origen especificado.

        Args:
            canal_id: ID del canal de origen, o None si no fue especificado.

        Returns:
            Instancia de CanalOrigen o None.

        Raises:
            CanalOrigenNotFoundError: Si el canal_id es no nulo pero no existe.
        """
        if canal_id is None:
            return None
        canal = await self._canal_repo.get_or_none(canal_id)
        if canal is None:
            raise CanalOrigenNotFoundError(
                f"CanalOrigen con id={canal_id} no encontrado en el catálogo."
            )
        return canal
