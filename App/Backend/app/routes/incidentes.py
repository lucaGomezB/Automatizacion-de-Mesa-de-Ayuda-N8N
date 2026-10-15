"""
Endpoints HTTP para la gestión de incidentes.

Responsabilidad:
    Define las rutas de la API REST para las operaciones CRUD sobre incidentes.
    Esta capa es responsable exclusivamente de:
        - Recibir y deserializar el payload HTTP.
        - Delegar la lógica de negocio al IncidenteService.
        - Serializar y retornar la respuesta HTTP con el schema correcto.

    Ninguna regla de negocio debe residir en esta capa. Toda la lógica
    (validación de dominio, clasificación, resolución de catálogos)
    se delega al servicio correspondiente.

Rutas expuestas (prefijo /api/v1/incidentes):
    POST   /            → Crear un nuevo incidente y clasificarlo automáticamente.
    GET    /            → Listar incidentes con filtros opcionales y paginación.
    GET    /{id}        → Obtener el detalle completo de un incidente por ID.
    PATCH  /{id}        → Actualizar parcialmente los campos de un incidente.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import es_canal_correo, es_canal_telefonia
from app.core.database import get_db_session
from app.core.security import get_current_user
from app.cost_guard.dependencies import get_cost_guard
from app.cost_guard.guard import CostGuard
from app.models.incidente import PrioridadEnum
from app.models.empleado import Empleado
from app.models.user import User
from app.repositories.canal_origen_repository import CanalOrigenRepository
from app.repositories.empleado_repository import EmpleadoRepository
from app.schemas.comentario import ComentarioCreate, ComentarioRead
from app.schemas.incidente import (
    IncidenteCreate,
    IncidenteCreateResponse,
    IncidenteEstadoUpdate,
    IncidenteListItem,
    IncidenteRead,
    IncidenteUpdate,
)
from app.services.ciclo_incidente_service import CicloIncidenteService
from app.services.comentario_service import ComentarioService
from app.services.contact_resolution_service import ContactResolutionService
from app.services.incident_visibility import (
    AlcanceIncidentes,
    alcance_desde_empleado,
)
from app.services.incidente_service import IncidenteService
from app.services.role_policy import politica_de_rol

# Prefijo /incidentes; el prefijo /api/v1 lo agrega register_routes() en routes/__init__.py
router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

# Alias de tipo para inyección de sesión de base de datos vía FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_service(
    session: SessionDep,
    cost_guard: Annotated[CostGuard | None, Depends(get_cost_guard)] = None,
) -> IncidenteService:
    """
    Función de fábrica del servicio para la inyección de dependencias de FastAPI.

    Construye el IncidenteService con la sesión de la solicitud actual,
    garantizando que todos los repositorios internos del servicio compartan
    la misma transacción de base de datos. La guarda de costo se inyecta para
    enforcar el gasto pago antes de invocar a Gemini.
    """
    return IncidenteService(session, cost_guard=cost_guard)


# Alias de tipo para inyección del servicio como dependencia
ServiceDep = Annotated[IncidenteService, Depends(get_service)]


async def get_alcance_incidentes(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> AlcanceIncidentes:
    """
    Dependencia que deriva el alcance de incidentes por rol (VIS-001).

    El sector efectivo se deriva del directorio via `user_id`. Una cuenta sin
    empleado vinculado (o sin sector) obtiene un alcance VACIO.
    """
    empleado = await EmpleadoRepository(session).get_by_user_id(current_user.id)
    return alcance_desde_empleado(empleado)


# Alias de tipo para inyección del alcance como dependencia
AlcanceDep = Annotated[AlcanceIncidentes, Depends(get_alcance_incidentes)]


async def get_empleado_actual(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> Empleado | None:
    """
    Resuelve el empleado vinculado a la cuenta autenticada (c-86).

    Es el ACTOR de las operaciones de ciclo de vida. Devuelve None cuando la
    cuenta no tiene empleado activo vinculado; el servicio de ciclo lo trata
    como rol desconocido y responde 403.
    """
    return await EmpleadoRepository(session).get_by_user_id(current_user.id)


# Alias de tipo para inyección del actor como dependencia
EmpleadoDep = Annotated[Empleado | None, Depends(get_empleado_actual)]


def exigir_permiso_prioridad_critica(
    empleado: Empleado | None, prioridad: PrioridadEnum | None
) -> None:
    """
    Guard de asignacion de la prioridad `critica` (c-90, RP-006).

    El permiso se DERIVA del registro canonico de politica de rol
    (`puede_asignar_prioridad_critica`): `mesa_de_ayuda` y
    `administrador_directorio` lo declaran verdadero; el resto, no. No existe
    lista de roles duplicada en la ruta.

    Dispara UNICAMENTE cuando el payload pide EXPLICITAMENTE `critica` (D3): un
    alta con el default `media` o un PATCH que no toca la prioridad nunca es
    rechazado por este guard, aunque el incidente ya este en `critica`. Un rol
    sin permiso, un rol desconocido o una cuenta sin empleado vinculado reciben
    403 (envelope FORBIDDEN), sin persistir ningun cambio.
    """
    if prioridad != PrioridadEnum.critica:
        return
    politica = politica_de_rol(empleado.rol) if empleado is not None else None
    if politica is None or not politica.puede_asignar_prioridad_critica:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere un rol autorizado para asignar la prioridad critica.",
        )


async def require_prioridad_critica_create(
    payload: IncidenteCreate,
    empleado: EmpleadoDep,
) -> None:
    """Guard del alta: rechaza `critica` sin permiso antes de clasificar (c-90)."""
    exigir_permiso_prioridad_critica(empleado, payload.prioridad)


async def require_prioridad_critica_update(
    payload: IncidenteUpdate,
    empleado: EmpleadoDep,
) -> None:
    """Guard de la edicion: rechaza fijar/cambiar a `critica` sin permiso (c-90)."""
    exigir_permiso_prioridad_critica(empleado, payload.prioridad)


# Alias de tipo para inyección de los guards de prioridad critica
GuardPrioridadCriticaCreate = Annotated[None, Depends(require_prioridad_critica_create)]
GuardPrioridadCriticaUpdate = Annotated[None, Depends(require_prioridad_critica_update)]


async def require_borrado_incidentes(empleado: EmpleadoDep) -> Empleado:
    """
    Exige un empleado vinculado autorizado al borrado logico de incidentes (c-87, RP-005).

    El permiso se DERIVA del registro canonico de politica de rol
    (`can_delete_incident`): unicamente `administrador_directorio` lo declara
    verdadero. Un rol no autorizado o una cuenta sin empleado vinculado recibe
    403. No existe lista de roles duplicada en la ruta.
    """
    politica = politica_de_rol(empleado.rol) if empleado is not None else None
    if politica is None or not politica.can_delete_incident:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol administrador_directorio.",
        )
    return empleado


# Alias de tipo para inyección del actor autorizado al borrado logico
BorradoDep = Annotated[Empleado, Depends(require_borrado_incidentes)]


def get_ciclo_service(session: SessionDep) -> CicloIncidenteService:
    """Fábrica del servicio de ciclo de cierre para la inyección de dependencias."""
    return CicloIncidenteService(session)


# Alias de tipo para inyección del servicio de ciclo como dependencia
CicloServiceDep = Annotated[CicloIncidenteService, Depends(get_ciclo_service)]


def get_comentario_service(session: SessionDep) -> ComentarioService:
    """Fábrica del servicio de comentarios para la inyección de dependencias."""
    return ComentarioService(session)


# Alias de tipo para inyección del servicio de comentarios
ComentarioServiceDep = Annotated[ComentarioService, Depends(get_comentario_service)]


async def resolver_reportante(
    payload: IncidenteCreate, current_user: User, session: AsyncSession
) -> int | None:
    """
    Resuelve el `reportante_empleado_id` segun el canal de ingreso (c-82, VIS-004).

    La ruta solo orquesta la dependencia (no ejecuta reglas de negocio): resuelve
    el contacto IMPLICITO del canal y delega en `ContactResolutionService`,
    reutilizando el servicio de resolucion existente. El contacto nunca lo tipea
    el usuario final.

    - Formulario web (o canal ausente/desconocido): la cuenta autenticada
      (`resolver_por_usuario`); si no tiene empleado vinculado, no se identifica.
    - Correo: el email del remitente (`reportante_email`).
    - Telefonia: el telefono del llamante (`reportante_telefono`).

    Devuelve el id del empleado cuando la resolucion es ENCONTRADO; NULL ante
    NO ENCONTRADO, AMBIGUO o contacto de canal ausente. Nunca lanza ni bloquea el
    alta (VIS-005).
    """
    canal = None
    if payload.canal_origen_id is not None:
        canal = await CanalOrigenRepository(session).get_or_none(
            payload.canal_origen_id
        )
    canal_nombre = canal.nombre if canal is not None else None

    resolucion = ContactResolutionService(session)
    if es_canal_telefonia(canal_nombre):
        resultado = await resolucion.resolver_por_telefono(payload.reportante_telefono)
    elif es_canal_correo(canal_nombre):
        resultado = await resolucion.resolver_por_email(payload.reportante_email)
    else:
        resultado = await resolucion.resolver_por_usuario(current_user.id)

    return resultado.empleado.id if resultado.encontrado else None


@router.post(
    "/",
    response_model=IncidenteCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear y clasificar un incidente",
)
async def create_incidente(
    payload: IncidenteCreate,
    service: ServiceDep,
    session: SessionDep,
    _guard: GuardPrioridadCriticaCreate,
    current_user: User = Depends(get_current_user),
) -> IncidenteCreateResponse:
    """
    Crea un nuevo incidente y ejecuta la clasificación automática.

    Invocado por N8N tras recibir un correo electrónico en Outlook o una
    transcripción de llamada de Twilio, o directamente desde un cliente HTTP.

    El incidente se persiste en estado "nuevo" y es clasificado inmediatamente
    por el pipeline híbrido (determinístico + Gemini). El resultado incluye
    el sector asignado, la confianza de la clasificación y el indicador
    de revisión humana si la confianza fue insuficiente.

    El VINCULO DE REPORTANTE (VIS-003/VIS-004) se resuelve por canal antes de
    crear: la ruta orquesta la resolucion y le pasa el id al servicio. Un
    reportante no identificado persiste NULL y deriva a revision humana (VIS-005).

    Args:
        payload: Descripción pseudonimizada del incidente, prioridad y canal.

    Returns:
        Representación completa del incidente creado y clasificado (HTTP 201).
    """
    reportante_empleado_id = await resolver_reportante(payload, current_user, session)
    incidente = await service.create_and_classify(
        payload, reportante_empleado_id=reportante_empleado_id
    )
    return IncidenteCreateResponse.model_validate(incidente)


@router.get(
    "/",
    response_model=list[IncidenteListItem],
    summary="Listar incidentes con filtros opcionales",
)
async def list_incidentes(
    service: ServiceDep,
    alcance: AlcanceDep,
    current_user: User = Depends(get_current_user),
    sector_id: int | None = Query(None, description="Filtrar por sector responsable"),
    estado_id: int | None = Query(None, description="Filtrar por estado del ciclo de vida"),
    prioridad: PrioridadEnum | None = Query(None, description="Filtrar por nivel de prioridad"),
    requiere_revision_humana: bool | None = Query(
        None, description="Filtrar por indicador de revisión pendiente"
    ),
    desde: datetime | None = Query(None, description="Fecha de creación mínima (ISO 8601)"),
    hasta: datetime | None = Query(None, description="Fecha de creación máxima (ISO 8601)"),
    origen_message_id: str | None = Query(
        None,
        max_length=255,
        description="Filtrar por identificador de origen (coincidencia exacta)",
    ),
    q: str | None = Query(
        None,
        max_length=200,
        description=(
            "Buscar por texto libre en la descripcion, o por numero de incidente "
            "cuando el termino es numerico"
        ),
    ),
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
) -> list[IncidenteListItem]:
    """
    Lista incidentes con filtros combinables y paginación.

    Todos los parámetros de filtro son opcionales y se combinan con AND lógico.
    El resultado se ordena por fecha de creación descendente (más reciente primero).
    Retorna la proyección ligera IncidenteListItem (sin texto de descripción)
    para optimizar el tamaño de la respuesta en consultas masivas.
    """
    incidentes = await service.list_incidentes(
        sector_id=sector_id,
        estado_id=estado_id,
        prioridad=prioridad,
        requiere_revision_humana=requiere_revision_humana,
        desde=desde,
        hasta=hasta,
        origen_message_id=origen_message_id,
        q=q,
        limit=limit,
        offset=offset,
        alcance=alcance,
    )
    return [IncidenteListItem.model_validate(i) for i in incidentes]


@router.get(
    "/historial-cerrados",
    response_model=list[IncidenteListItem],
    summary="Historial de incidentes cerrados acotado por alcance",
)
async def list_historial_cerrados(
    service: ServiceDep,
    alcance: AlcanceDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
) -> list[IncidenteListItem]:
    """
    Lista el historial de incidentes cerrados acotado por el alcance (VIS-008).

    Declarada ANTES de `GET /{incidente_id}` para evitar el conflicto de path
    (D10). GLOBAL ve los globalmente cerrados; SECTOR ve los incidentes con un
    cierre de su sector (incluidos los cerrados solo por su sector); PROPIO ve
    los propios cerrados. Excluye los incidentes eliminados.
    """
    incidentes = await service.list_historial_cerrados(
        alcance=alcance, limit=limit, offset=offset
    )
    return [IncidenteListItem.model_validate(i) for i in incidentes]


@router.get(
    "/{incidente_id}",
    response_model=IncidenteRead,
    summary="Obtener el detalle completo de un incidente",
)
async def get_incidente(
    incidente_id: int,
    service: ServiceDep,
    alcance: AlcanceDep,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Retorna la representación completa de un incidente, incluyendo relaciones.

    A diferencia del listado, esta respuesta incluye la descripción completa
    del incidente y los objetos de catálogo completos (sector, estado, canal).

    Args:
        incidente_id: ID del incidente a recuperar.

    Returns:
        Detalle completo del incidente (HTTP 200) o error 404 si no existe.
    """
    incidente = await service.get_by_id(incidente_id, alcance=alcance)
    return IncidenteRead.model_validate(incidente)


@router.patch(
    "/{incidente_id}",
    response_model=IncidenteRead,
    summary="Actualizar parcialmente un incidente",
)
async def update_incidente(
    incidente_id: int,
    payload: IncidenteUpdate,
    service: ServiceDep,
    alcance: AlcanceDep,
    _guard: GuardPrioridadCriticaUpdate,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Actualiza uno o más campos de un incidente existente (PATCH semántico).

    Solo se modifican los campos incluidos en el payload con valor distinto
    de None. Casos de uso típicos: cambio de estado por el operador,
    reasignación de sector tras revisión manual, o modificación de prioridad.

    El alcance de visibilidad por rol (VIS-001) se aplica también a la ESCRITURA:
    un incidente fuera del alcance del usuario se comporta como no encontrado
    (404), igual que en la lectura, y NUNCA se modifica.

    Los incidentes en estado terminal (cerrado, es_terminal=true) son de solo
    lectura. Cualquier intento de PATCH sobre un incidente cerrado retorna
    HTTP 409 Conflict con código INCIDENTE_CERRADO.

    Args:
        incidente_id: ID del incidente a modificar.
        payload:      Campos a actualizar (todos opcionales).

    Returns:
        Representación actualizada del incidente (HTTP 200).
        HTTP 404 si el incidente no existe o está fuera del alcance.
        HTTP 409 si el incidente está cerrado (solo lectura).
    """
    incidente = await service.update_incidente(incidente_id, payload, alcance=alcance)
    return IncidenteRead.model_validate(incidente)


@router.delete(
    "/{incidente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Borrado lógico de un incidente (administrador del directorio)",
)
async def borrar_incidente(
    incidente_id: int,
    service: ServiceDep,
    alcance: AlcanceDep,
    actor: BorradoDep,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Ejecuta el borrado LOGICO de un incidente (c-87, SD-002).

    Autorizacion: solo el rol con `can_delete_incident` (administrador del
    directorio); 403 en otro caso. Un incidente fuera del alcance del llamante,
    inexistente o ya borrado responde 404 sin revelar su existencia. La fila y
    sus relaciones persisten; solo se setean `deleted_at`/`deleted_by` (SD-001).
    """
    await service.soft_delete_incidente(
        incidente_id, actor_empleado_id=actor.id, alcance=alcance
    )


@router.post(
    "/{incidente_id}/cierre-sector",
    response_model=IncidenteRead,
    summary="Cerrar el incidente para el sector del gestion",
)
async def cerrar_sector(
    incidente_id: int,
    service: CicloServiceDep,
    alcance: AlcanceDep,
    actor: EmpleadoDep,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Cierra el incidente para el PROPIO sector del actor `gestion_incidentes`.

    Idempotente por el par (incidente, sector). Tras el cierre, si todos los
    sectores del incidente cerraron, el incidente pasa al estado terminal
    `cerrado` (ILC-001/ILC-003).

    Autorizacion: el rol debe tener `cierra_sector` (403 si no). El incidente
    debe estar dentro del alcance SECTOR del actor (404 si no).
    """
    incidente = await service.cerrar_sector(incidente_id, actor, alcance)
    return IncidenteRead.model_validate(incidente)


@router.post(
    "/{incidente_id}/cierre-global",
    response_model=IncidenteRead,
    summary="Cerrar globalmente el incidente (mesa de ayuda)",
)
async def cerrar_global(
    incidente_id: int,
    service: CicloServiceDep,
    alcance: AlcanceDep,
    actor: EmpleadoDep,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Cierra GLOBALMENTE el incidente: registra el cierre de TODOS sus sectores y
    lo lleva al estado terminal `cerrado` (ILC-002). Idempotente.

    Autorizacion: solo el rol con `cierra_global` (mesa de ayuda); 403 en otro caso.
    """
    incidente = await service.cerrar_global(incidente_id, actor, alcance)
    return IncidenteRead.model_validate(incidente)


@router.post(
    "/{incidente_id}/rehabilitar",
    response_model=IncidenteRead,
    summary="Rehabilitar (reabrir) un incidente cerrado",
)
async def rehabilitar_incidente(
    incidente_id: int,
    service: CicloServiceDep,
    alcance: AlcanceDep,
    actor: EmpleadoDep,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Rehabilita un incidente cerrado (ILC-004): limpia sus cierres por sector, lo
    devuelve a `en proceso` y registra el evento de reapertura.

    Autorizacion: solo el rol con `reabre` (mesa de ayuda); 403 en otro caso.
    Reabrir un incidente no cerrado produce 422.
    """
    incidente = await service.rehabilitar(incidente_id, actor, alcance)
    return IncidenteRead.model_validate(incidente)


@router.patch(
    "/{incidente_id}/estado",
    response_model=IncidenteRead,
    summary="Editar el estado no terminal del incidente",
)
async def editar_estado_incidente(
    incidente_id: int,
    payload: IncidenteEstadoUpdate,
    service: CicloServiceDep,
    alcance: AlcanceDep,
    actor: EmpleadoDep,
    current_user: User = Depends(get_current_user),
) -> IncidenteRead:
    """
    Fija el estado del incidente entre `en proceso`, `en espera` y `resuelto`
    (ILC-005). `cerrado` se rechaza con 422 (el estado terminal solo se alcanza
    por el modelo de cierre).

    Autorizacion: rol con `edita_estado` (403 si no); el incidente debe estar
    dentro del alcance del actor (gestion: su sector; 404 si no).
    """
    incidente = await service.editar_estado(
        incidente_id, payload.estado, actor, alcance
    )
    return IncidenteRead.model_validate(incidente)


@router.get(
    "/{incidente_id}/comentarios",
    response_model=list[ComentarioRead],
    summary="Listar los comentarios de un incidente",
)
async def listar_comentarios(
    incidente_id: int,
    service: ComentarioServiceDep,
    alcance: AlcanceDep,
    current_user: User = Depends(get_current_user),
) -> list[ComentarioRead]:
    """
    Devuelve las entradas de comentario en orden cronologico ascendente (ICM-003).

    Permiso derivado de la visibilidad (ICM-002): un incidente fuera del alcance
    del usuario responde 404, sin revelar su existencia ni sus comentarios.
    """
    comentarios = await service.listar(incidente_id, alcance)
    return [ComentarioRead.model_validate(c) for c in comentarios]


@router.post(
    "/{incidente_id}/comentarios",
    response_model=ComentarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar un comentario append-only a un incidente",
)
async def agregar_comentario(
    incidente_id: int,
    payload: ComentarioCreate,
    service: ComentarioServiceDep,
    alcance: AlcanceDep,
    actor: EmpleadoDep,
    current_user: User = Depends(get_current_user),
) -> ComentarioRead:
    """
    Persiste un comentario del actor autenticado sobre el incidente (ICM-001).

    Permiso derivado de la visibilidad (ICM-002): un incidente fuera del alcance
    responde 404. No existe edicion ni borrado de entradas.
    """
    comentario = await service.agregar(incidente_id, payload.texto, actor, alcance)
    return ComentarioRead.model_validate(comentario)
