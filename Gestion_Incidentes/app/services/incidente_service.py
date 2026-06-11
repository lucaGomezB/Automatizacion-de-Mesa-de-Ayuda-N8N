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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.classifiers.hybrid import HybridClassifier
from app.config.settings import get_settings
from app.utils.n8n_webhook import notify_n8n
from app.utils.pseudonymizer import pseudonymize
from app.core.exceptions import (
    CanalOrigenNotFoundError,
    EntityNotFoundError,
    EstadoNotFoundError,
)
from app.core.logging import get_logger
from app.models.catalog import CanalOrigen, Estado
from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.clasificacion_repository import ClasificacionRepository
from app.repositories.incidente_repository import IncidenteRepository
from app.repositories.sector_repository import SectorRepository
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import IncidenteCreate, IncidenteUpdate

logger = get_logger(__name__)

# Nombre del estado inicial de todo incidente recién creado.
# Debe coincidir exactamente con el valor sembrado en la migración 001.
_ESTADO_NUEVO = "nuevo"


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
        self._session = session
        # Los repositorios comparten la misma sesión para garantizar atomicidad
        self._incidente_repo = IncidenteRepository(session)
        self._sector_repo = SectorRepository(session)
        self._clasificacion_repo = ClasificacionRepository(session)
        self._classifier = classifier or HybridClassifier()

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

        # Paso 4: Crear el registro del incidente con doble representación
        incidente = await self._incidente_repo.create(
            descripcion_original=payload.descripcion,        # cifrada at-rest por EncryptedText
            descripcion_pseudonimizada=resultado_pseudo.texto,  # en claro, operativa
            prioridad=payload.prioridad,
            estado_id=estado_nuevo.id,
            canal_origen_id=canal.id if canal else None,
            requiere_revision_humana=False,  # Se actualizará tras la clasificación
        )

        logger.info("incidente_created", incidente_id=incidente.id)

        # Pasos 5-7: Clasificar sobre la pseudonimizada y persistir el resultado
        result = await self._classifier.classify(resultado_pseudo.texto)
        await self._apply_classification(incidente, result)

        # Paso 7: Retornar el incidente completo con todas las relaciones
        return await self._incidente_repo.get_with_relations(incidente.id)  # type: ignore[return-value]

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
        # Verificar existencia antes de intentar la actualización
        await self._incidente_repo.get_by_id(incidente_id)
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
        # Resolver categoría (string) → sector (registro ORM con ID)
        sector = await self._sector_repo.get_by_nombre(result.categoria)
        sector_id = sector.id if sector else None

        # Actualizar el incidente con el sector asignado y la bandera de revisión
        await self._incidente_repo.update_fields(
            incidente.id,
            sector_id=sector_id,
            requiere_revision_humana=result.requiere_revision_humana,
        )

        # Crear el registro de auditoría con todos los detalles de la clasificación
        await self._clasificacion_repo.create(
            incidente_id=incidente.id,
            sector_id_predicho=sector_id,
            confianza=result.confianza,
            etapa=result.etapa,
            requiere_revision_humana=result.requiere_revision_humana,
            respuesta_raw=result.respuesta_raw,
        )

        logger.info(
            "incidente_classified",
            incidente_id=incidente.id,
            categoria=result.categoria,
            confianza=result.confianza,
            etapa=result.etapa,
            requiere_revision_humana=result.requiere_revision_humana,
        )

        # Notificar a N8N de forma fire-and-forget: no bloquea la respuesta HTTP
        # ni propaga fallos (notify_n8n ya envuelve toda excepción en try/except).
        asyncio.create_task(notify_n8n(incidente.id, result))

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
        result = await self._session.execute(
            select(Estado).where(Estado.nombre == nombre)
        )
        estado = result.scalar_one_or_none()
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
        result = await self._session.get(CanalOrigen, canal_id)
        if result is None:
            raise CanalOrigenNotFoundError(
                f"CanalOrigen con id={canal_id} no encontrado en el catálogo."
            )
        return result
