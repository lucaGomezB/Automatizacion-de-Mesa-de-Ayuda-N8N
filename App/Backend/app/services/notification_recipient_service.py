"""
Servicio de resolucion de destinatarios de notificacion (c-56).

Responsabilidad:
    Resolver los destinatarios de la notificacion de revision humana a partir
    del directorio de empleados (c-54): empleados ACTIVOS con rol `operador`
    cuyo sector coincide con el sector predicho principal del incidente.

Diseno (design.md D1, D5, D6):
    - Reutiliza el directorio y su seam de resolucion (c-54) SIN duplicar la
      logica de resolucion de identidad: la enumeracion por rol/sector es una
      consulta nueva (`EmpleadoRepository.listar_operadores_por_sector`).
    - Es in-process: no expone contactos por HTTP, no envia notificaciones.
    - Un fallo del repositorio o un directorio vacio NO es fatal: degrada a
      lista vacia (NR-002, NR-007); N8N aplica el respaldo `OPERATOR_EMAIL`.
    - Normaliza cada email con `normalizar_email` y descarta los invalidos.

Privacidad (NR-006 / c-54 DIR-006 / RES-006):
    La trazabilidad registra el sector y la CANTIDAD de destinatarios, NUNCA
    los emails en claro.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.empleado_repository import EmpleadoRepository
from app.utils.contactos import normalizar_email

logger = get_logger(__name__)


class NotificationRecipientService:
    """Resolucion in-process de destinatarios de notificacion por rol y sector."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = EmpleadoRepository(session)

    async def resolver_destinatarios_revision(
        self, sector_id: int | None
    ) -> list[str]:
        """
        Devuelve los emails normalizados de los operadores activos del sector.

        Args:
            sector_id: ID del sector predicho principal del incidente, o None.

        Returns:
            Lista de emails (posiblemente vacia). Nunca lanza excepcion: ante un
            sector nulo, un directorio vacio o un fallo de acceso, devuelve [].
        """
        if sector_id is None:
            self._log(sector_id=None, cantidad=0)
            return []

        try:
            operadores = await self._repo.listar_operadores_por_sector(sector_id)
        except Exception:  # noqa: BLE001 - degradacion explicita (NR-007)
            logger.warning("destinatarios_revision_error", sector_id=sector_id)
            return []

        destinatarios: list[str] = []
        for empleado in operadores:
            try:
                destinatarios.append(normalizar_email(empleado.email))
            except ValueError:
                # Un email invalido en el directorio no rompe la resolucion.
                logger.warning(
                    "destinatario_revision_email_invalido", sector_id=sector_id
                )

        self._log(sector_id=sector_id, cantidad=len(destinatarios))
        return destinatarios

    @staticmethod
    def _log(*, sector_id: int | None, cantidad: int) -> None:
        """Emite la trazabilidad SIN emails en claro (NR-006)."""
        logger.info(
            "destinatarios_revision_resueltos",
            sector_id=sector_id,
            cantidad=cantidad,
        )
