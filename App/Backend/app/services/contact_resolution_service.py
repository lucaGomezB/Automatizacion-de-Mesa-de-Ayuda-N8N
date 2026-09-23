"""
Servicio de resolucion de contactos (c-54, seam c-53 / RES-001..RES-006).

Responsabilidad:
    Resolver la identidad de un empleado a partir del identificador disponible
    en cada canal: telefono (E.164), email (minusculas) o usuario autenticado
    (`user_id`). Es un servicio IN-PROCESS, sin borde HTTP ni token (D5): c-53 lo
    consume como estrategia opcional sin cambiar su contrato de entrega.

Contrato:
    Cada metodo devuelve un `ResultadoResolucion` que distingue
    encontrado / no encontrado / ambiguo. NUNCA lanza excepcion por datos
    ausentes o malformados: un directorio vacio no es un error.

Privacidad (RES-006):
    Opera sobre el identificador minimo y registra trazabilidad (canal +
    resultado) SIN el telefono ni el email en claro. NO envia notificaciones.
"""

from dataclasses import dataclass
from enum import Enum as PyEnum

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.empleado import Empleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.utils.contactos import normalizar_email, normalizar_telefono

logger = get_logger(__name__)


class EstadoResolucion(str, PyEnum):
    """Estados posibles de una resolucion de contacto (RES-004)."""

    ENCONTRADO = "encontrado"
    NO_ENCONTRADO = "no_encontrado"
    AMBIGUO = "ambiguo"


@dataclass(frozen=True)
class ResultadoResolucion:
    """
    Resultado unificado de una resolucion de contacto.

    `empleado` solo esta presente cuando el estado es ENCONTRADO. El campo
    `canal` identifica el origen de la resolucion (telefono/email/usuario) para
    la trazabilidad. Un estado NO_ENCONTRADO o AMBIGUO es representable de forma
    explicita y distinguible de un error.
    """

    estado: EstadoResolucion
    empleado: Empleado | None = None
    canal: str | None = None

    @property
    def encontrado(self) -> bool:
        return self.estado == EstadoResolucion.ENCONTRADO


class ContactResolutionService:
    """Servicio in-process de resolucion de contactos del directorio."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = EmpleadoRepository(session)

    async def resolver_por_telefono(self, telefono: str | None) -> ResultadoResolucion:
        """Resuelve por telefono normalizado a E.164 (igualdad exacta)."""
        try:
            normalizado = normalizar_telefono(telefono)
        except ValueError:
            return self._resultado(
                EstadoResolucion.NO_ENCONTRADO, None, "telefono"
            )

        coincidencias = await self._repo.listar_por_telefono(normalizado)
        return self._resultado(
            self._clasificar(coincidencias), coincidencias, "telefono"
        )

    async def resolver_por_email(self, email: str | None) -> ResultadoResolucion:
        """Resuelve por email normalizado a minusculas (igualdad exacta)."""
        try:
            normalizado = normalizar_email(email)
        except ValueError:
            return self._resultado(
                EstadoResolucion.NO_ENCONTRADO, None, "email"
            )

        coincidencias = await self._repo.listar_por_email(normalizado)
        return self._resultado(
            self._clasificar(coincidencias), coincidencias, "email"
        )

    async def resolver_por_usuario(self, user_id: int | None) -> ResultadoResolucion:
        """Resuelve por identidad autenticada siguiendo el vinculo `user_id`."""
        if user_id is None:
            return self._resultado(
                EstadoResolucion.NO_ENCONTRADO, None, "usuario"
            )
        empleado = await self._repo.get_by_user_id(user_id)
        if empleado is None:
            return self._resultado(
                EstadoResolucion.NO_ENCONTRADO, None, "usuario"
            )
        return self._resultado(EstadoResolucion.ENCONTRADO, [empleado], "usuario")

    # ── Auxiliares ────────────────────────────────────────────────────────────

    @staticmethod
    def _clasificar(coincidencias: list[Empleado]) -> EstadoResolucion:
        """Traduce la lista de coincidencias al estado de resolucion (RES-004)."""
        if not coincidencias:
            return EstadoResolucion.NO_ENCONTRADO
        if len(coincidencias) > 1:
            return EstadoResolucion.AMBIGUO
        return EstadoResolucion.ENCONTRADO

    def _resultado(
        self,
        estado: EstadoResolucion,
        coincidencias: list[Empleado] | None,
        canal: str,
    ) -> ResultadoResolucion:
        """Construye el resultado y emite la trazabilidad sin PII."""
        empleado = (
            coincidencias[0]
            if estado == EstadoResolucion.ENCONTRADO and coincidencias
            else None
        )
        logger.info(
            "resolucion_contacto",
            canal=canal,
            resultado=estado.value,
        )
        return ResultadoResolucion(estado=estado, empleado=empleado, canal=canal)
