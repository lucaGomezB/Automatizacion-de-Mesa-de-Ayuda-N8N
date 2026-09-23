"""
Endpoints HTTP de gestion del directorio de empleados (c-54).

Responsabilidad:
    Exponer la API de gestion del directorio. La capa de rutas es responsable de
    autenticar/autorizar (por rol del empleado vinculado) y de delegar la logica
    al `DirectorioService`.

Autorizacion (DIR-006):
    - Escritura (alta/edicion/desactivacion/borrado ARCO): rol `administrador_directorio`.
    - Consulta (listado/detalle): roles `operador` o `administrador_directorio`.
    - Sin token: 401. Con token sin empleado vinculado: 403.

Privacidad:
    La auditoria de las consultas registra solo el actor y la operacion; NUNCA
    datos personales en claro.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User
from app.repositories.empleado_repository import EmpleadoRepository
from app.schemas.directorio import EmpleadoCreate, EmpleadoRead, EmpleadoUpdate
from app.services.directorio_service import DirectorioService

logger = get_logger(__name__)

router = APIRouter(prefix="/directorio", tags=["Directorio"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_empleado_actual(
    current_user: CurrentUserDep, session: SessionDep
) -> Empleado | None:
    """
    Resuelve el empleado del directorio vinculado a la cuenta autenticada.

    Deriva la identidad efectiva via `directorio_empleado.user_id`. Una cuenta
    sin empleado vinculado devuelve None (el control de acceso lo rechaza).
    """
    return await EmpleadoRepository(session).get_by_user_id(current_user.id)


EmpleadoActualDep = Annotated[Empleado | None, Depends(get_empleado_actual)]


async def require_directorio_admin(empleado: EmpleadoActualDep) -> Empleado:
    """Exige un empleado vinculado con rol `administrador_directorio`."""
    if empleado is None or empleado.rol != RolEmpleado.administrador_directorio:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol administrador_directorio.",
        )
    return empleado


async def require_directorio_lectura(empleado: EmpleadoActualDep) -> Empleado:
    """Exige un empleado vinculado con rol `operador` o `administrador_directorio`."""
    if empleado is None or empleado.rol == RolEmpleado.usuario_final:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado para consultar el directorio.",
        )
    return empleado


AdminDep = Annotated[Empleado, Depends(require_directorio_admin)]
LecturaDep = Annotated[Empleado, Depends(require_directorio_lectura)]


@router.post(
    "/empleados",
    response_model=EmpleadoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Alta de un empleado del directorio (administrador)",
)
async def crear_empleado(
    payload: EmpleadoCreate, session: SessionDep, actor: AdminDep
) -> EmpleadoRead:
    """Crea un empleado del directorio. Requiere rol administrador."""
    empleado = await DirectorioService(session).crear_empleado(
        legajo=payload.legajo,
        nombre=payload.nombre,
        email=payload.email,
        telefono=payload.telefono,
        sector_id=payload.sector_id,
        rol=payload.rol,
        user_id=payload.user_id,
        actor_id=actor.id,
    )
    return EmpleadoRead.model_validate(empleado)


@router.get(
    "/empleados",
    response_model=list[EmpleadoRead],
    summary="Listar el directorio (operador/administrador)",
)
async def listar_empleados(
    session: SessionDep,
    actor: LecturaDep,
    solo_activos: bool = False,
) -> list[EmpleadoRead]:
    """Lista los empleados del directorio. Requiere rol autorizado."""
    empleados = await DirectorioService(session).listar(solo_activos=solo_activos)
    # Auditoria de consulta sin PII.
    logger.info(
        "directorio_consulta",
        operacion="listado",
        actor_id=actor.id,
        resultados=len(empleados),
    )
    return [EmpleadoRead.model_validate(e) for e in empleados]


@router.get(
    "/empleados/{empleado_id}",
    response_model=EmpleadoRead,
    summary="Detalle de un empleado del directorio (operador/administrador)",
)
async def obtener_empleado(
    empleado_id: int, session: SessionDep, actor: LecturaDep
) -> EmpleadoRead:
    """Recupera un empleado por id. Requiere rol autorizado."""
    empleado = await DirectorioService(session).obtener(empleado_id)
    logger.info(
        "directorio_consulta",
        operacion="detalle",
        actor_id=actor.id,
        empleado_id=empleado_id,
    )
    return EmpleadoRead.model_validate(empleado)


@router.patch(
    "/empleados/{empleado_id}",
    response_model=EmpleadoRead,
    summary="Editar/activar/desactivar un empleado (administrador)",
)
async def actualizar_empleado(
    empleado_id: int,
    payload: EmpleadoUpdate,
    session: SessionDep,
    actor: AdminDep,
) -> EmpleadoRead:
    """Edita parcialmente un empleado; `activo` alterna su estado."""
    service = DirectorioService(session)
    cambios = payload.model_dump(exclude_unset=True)
    activo = cambios.pop("activo", None)

    empleado = await service.actualizar_empleado(
        empleado_id, actor_id=actor.id, **cambios
    )
    if activo is True:
        empleado = await service.reactivar_empleado(empleado_id, actor_id=actor.id)
    elif activo is False:
        empleado = await service.desactivar_empleado(empleado_id, actor_id=actor.id)

    return EmpleadoRead.model_validate(empleado)


@router.delete(
    "/empleados/{empleado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Borrado ARCO de un empleado (administrador)",
)
async def borrar_empleado(
    empleado_id: int, session: SessionDep, actor: AdminDep
) -> None:
    """Ejecuta el borrado fisico por solicitud ARCO. Requiere administrador."""
    await DirectorioService(session).borrar_empleado_arco(
        empleado_id, actor_id=actor.id
    )
