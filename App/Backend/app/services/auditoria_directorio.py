"""
Helper compartido de emision de eventos de auditoria del directorio (c-153, D).

Responsabilidad:
    Unifica la emision de la auditoria del directorio en un solo punto: persiste
    la fila en la traza durable (`directorio_auditoria`) y emite el evento
    estructurado equivalente. Lo consumen tanto `DirectorioService` (operaciones
    de gestion) como `ContactResolutionService` (canales de resolucion), sin
    duplicar la logica de emision.

Privacidad (DIR-013):
    El helper SOLO acepta identificadores internos, operacion, resultado, canal e
    instante. No acepta ni registra email, telefono ni nombre; los llamadores no
    deben pasar valores de contacto. El evento estructurado conserva el nombre
    historico de cada canal para no romper las trazas existentes.

Contrato:
    Comparte la transaccion de la sesion recibida (flush, sin commit) y devuelve
    la fila durable creada.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.directorio_auditoria import DirectorioAuditoria
from app.repositories.directorio_auditoria_repository import (
    DirectorioAuditoriaRepository,
)

logger = get_logger(__name__)

# Nombre del evento estructurado de gestion del directorio (se conserva por
# compatibilidad con las trazas y tests existentes).
EVENTO_AUDITORIA = "directorio_auditoria"

# Evento estructurado de los canales de resolucion de contacto (RES-006).
EVENTO_RESOLUCION = "resolucion_contacto"

__all__ = [
    "EVENTO_AUDITORIA",
    "EVENTO_RESOLUCION",
    "registrar_evento_auditoria",
]


async def registrar_evento_auditoria(
    session: AsyncSession,
    *,
    operacion: str,
    resultado: str,
    empleado_id: int | None = None,
    actor_id: int | None = None,
    canal: str | None = None,
    evento: str = EVENTO_AUDITORIA,
) -> DirectorioAuditoria:
    """
    Registra un evento de auditoria SIN PII en la traza durable y en structlog.

    Args:
        session:     Sesion activa de la solicitud (comparte la transaccion).
        operacion:   Operacion auditada (`alta`, `edicion`, `resolucion_contacto`...).
        resultado:   Resultado de la operacion (`ok`, `encontrado`...).
        empleado_id: Identificador interno del sujeto (nullable).
        actor_id:    Identificador interno del actor (nullable).
        canal:       Canal de resolucion (`email`, `telefono`, `usuario`); NULL en
                     operaciones de gestion.
        evento:      Nombre del evento estructurado a emitir. Por defecto el de
                     gestion del directorio; la resolucion usa el suyo historico.

    Returns:
        La fila durable creada.
    """
    repo = DirectorioAuditoriaRepository(session)
    registro = await repo.registrar(
        operacion=operacion,
        resultado=resultado,
        empleado_id=empleado_id,
        actor_empleado_id=actor_id,
        canal=canal,
    )

    campos: dict[str, object] = {
        "operacion": operacion,
        "resultado": resultado,
        "empleado_id": empleado_id,
        "actor_id": actor_id,
    }
    if canal is not None:
        campos["canal"] = canal
    logger.info(evento, **campos)
    return registro
