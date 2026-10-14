"""
Servicio de resolucion de destinatarios de notificacion (c-82, NR-002).

Responsabilidad:
    Resolver los destinatarios de la notificacion de revision humana a partir
    del directorio de empleados: TODOS los empleados ACTIVOS con rol
    `mesa_de_ayuda`, con independencia del sector (c-82 D4).

Diseno:
    - El rol destinatario se deriva del registro unico de politica de rol
      (RP-002); la consulta concreta la hace
      `EmpleadoRepository.listar_mesa_de_ayuda_activos` (sin filtro de sector).
    - Es in-process: no expone contactos por HTTP, no envia notificaciones.
    - Un fallo del repositorio o un directorio vacio NO es fatal: degrada a
      lista vacia (NR-002, NR-007); N8N aplica el respaldo `OPERATOR_EMAIL`.
    - Normaliza cada email con `normalizar_email` y descarta los invalidos.

Privacidad (NR-006):
    La trazabilidad registra la CANTIDAD de destinatarios, NUNCA los emails en
    claro.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.empleado_repository import EmpleadoRepository
from app.services.role_policy import (
    rol_destinatario_notificacion,
    rol_destinatario_post_revision,
)
from app.utils.contactos import normalizar_email

logger = get_logger(__name__)


class NotificationRecipientService:
    """Resolucion in-process de destinatarios de notificacion (rol mesa_de_ayuda)."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = EmpleadoRepository(session)

    async def resolver_destinatarios_revision(self) -> list[str]:
        """
        Devuelve los emails normalizados de los `mesa_de_ayuda` activos.

        El rol destinatario se DERIVA del registro unico de politica de rol
        (RP-002), sin duplicar el criterio.

        Returns:
            Lista de emails (posiblemente vacia). Nunca lanza excepcion: ante un
            directorio vacio o un fallo de acceso, devuelve [].
        """
        rol = rol_destinatario_notificacion()
        if rol is None:
            self._log(cantidad=0)
            return []

        try:
            mesas = await self._repo.listar_activos_por_rol(rol)
        except Exception:  # noqa: BLE001 - degradacion explicita (NR-007)
            logger.warning("destinatarios_revision_error")
            return []

        destinatarios: list[str] = []
        for empleado in mesas:
            try:
                destinatarios.append(normalizar_email(empleado.email))
            except ValueError:
                # Un email invalido en el directorio no rompe la resolucion.
                logger.warning("destinatario_revision_email_invalido")

        self._log(cantidad=len(destinatarios))
        return destinatarios

    async def resolver_destinatarios_gestion(
        self, sector_ids: list[int]
    ) -> list[str]:
        """
        Resuelve los destinatarios del aviso post-revision (c-86, NR-008).

        Son los empleados ACTIVOS con rol `gestion_incidentes` cuyo sector
        pertenece al CONJUNTO de sectores validados. El rol destinatario se
        DERIVA del registro unico de politica de rol (RP-002), sin listas fijas.

        Returns:
            Lista de emails (posiblemente vacia), SIN duplicados. Nunca lanza:
            un directorio vacio o un fallo de acceso degrada a lista vacia.
        """
        rol = rol_destinatario_post_revision()
        if rol is None:
            self._log_post_revision(cantidad=0)
            return []

        try:
            empleados = await self._repo.listar_activos_por_rol_y_sectores(
                rol, list(sector_ids or [])
            )
        except Exception:  # noqa: BLE001 - degradacion explicita (NR-008)
            logger.warning("destinatarios_post_revision_error")
            return []

        destinatarios: list[str] = []
        vistos: set[str] = set()
        for empleado in empleados:
            try:
                email = normalizar_email(empleado.email)
            except ValueError:
                logger.warning("destinatario_post_revision_email_invalido")
                continue
            if email in vistos:
                continue
            vistos.add(email)
            destinatarios.append(email)

        self._log_post_revision(cantidad=len(destinatarios))
        return destinatarios

    @staticmethod
    def _log(*, cantidad: int) -> None:
        """Emite la trazabilidad SIN emails en claro (NR-006)."""
        logger.info(
            "destinatarios_revision_resueltos",
            cantidad=cantidad,
        )

    @staticmethod
    def _log_post_revision(*, cantidad: int) -> None:
        """Trazabilidad del aviso post-revision SIN emails en claro (NR-008)."""
        logger.info(
            "destinatarios_post_revision_resueltos",
            cantidad=cantidad,
        )
