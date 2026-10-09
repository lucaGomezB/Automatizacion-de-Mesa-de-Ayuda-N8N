"""Servicio de materializacion del privilegio de identidad (c-63b, IAH-005).

Responsabilidad:
    Concentra la logica del flag `User.is_privileged`: el catalogo de roles
    privilegiados, la sincronizacion al crear/actualizar/desvincular un
    `Empleado` (OQ-B1 = persistir + sincronizar + derivacion defensiva) y la
    derivacion defensiva usada por el chequeo de MFA.

Decisiones (design.md OQ-B1):
    - Roles privilegiados: `operador`, `administrador_directorio` y
      `mesa_de_ayuda`. `usuario_final` no lo es.
    - Al vincular/actualizar un empleado privilegiado, el flag del usuario se
      enciende; al desvincular (`user_id = NULL`) o degradar a `usuario_final`,
      se apaga.
    - El seed `admin` (sembrado por la migracion 003) NUNCA se degrada por esta
      sincronizacion: conserva el privilegio aunque se lo vincule a un empleado
      no privilegiado.
    - El chequeo de autenticacion combina el flag persistido con una derivacion
      defensiva (flag OR vinculo activo privilegiado).
"""

from app.core.logging import get_logger
from app.models.empleado import RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)

# Roles del directorio que confieren privilegio a la cuenta vinculada (IAH-005).
PRIVILEGED_ROLE_VALUES = frozenset(
    {
        RolEmpleado.operador.value,
        RolEmpleado.administrador_directorio.value,
        RolEmpleado.mesa_de_ayuda.value,
    }
)

# Username del seed sembrado por la migracion 003: nunca se degrada.
SEEDED_PRIVILEGED_USERNAME = "admin"


def _role_value(rol: str | RolEmpleado | None) -> str | None:
    """Normaliza un rol (enum o str) a su valor textual."""
    if rol is None:
        return None
    if isinstance(rol, RolEmpleado):
        return rol.value
    return str(rol)


def is_privileged_role(rol: str | RolEmpleado | None) -> bool:
    """True si el rol pertenece al catalogo de roles privilegiados."""
    return _role_value(rol) in PRIVILEGED_ROLE_VALUES


async def sync_user_privilege(
    session,
    *,
    user_id: int | None,
    rol: str | RolEmpleado | None = None,
    linked: bool = True,
) -> None:
    """Sincroniza `User.is_privileged` con el vinculo/rol indicado.

    Args:
        session:  Sesion activa (comparte la transaccion del servicio llamador).
        user_id:  Cuenta a sincronizar; None no hace nada (desvinculacion total).
        rol:      Rol del `Empleado` vinculado (ignorado si `linked` es False).
        linked:   False cuando el vinculo se rompe (`user_id = NULL`).

    El seed `admin` conserva el privilegio: la sincronizacion nunca lo apaga.
    """
    if user_id is None:
        return

    user = await UserRepository(session).get_or_none(user_id)
    if user is None:
        return

    desired = bool(linked) and is_privileged_role(rol)
    if not desired and user.username == SEEDED_PRIVILEGED_USERNAME:
        # El admin sembrado es privilegiado por migracion y no se degrada aqui.
        return

    if user.is_privileged != desired:
        user.is_privileged = desired
        await session.flush()
        logger.info(
            "identity_privilege_synced",
            user_id=user.id,
            is_privileged=desired,
            linked=linked,
        )


async def user_is_privileged(session, user) -> bool:
    """Deriva si la cuenta es privilegiada (flag persistido OR vinculo activo).

    Derivacion defensiva (OQ-B1): si el flag no se materializo (por un alta
    directa en datos), el vinculo activo privilegiado alcanza para exigir MFA.
    """
    if user is None:
        return False
    if user.is_privileged:
        return True

    empleado = await EmpleadoRepository(session).get_by_user_id(user.id)
    return empleado is not None and is_privileged_role(empleado.rol)
