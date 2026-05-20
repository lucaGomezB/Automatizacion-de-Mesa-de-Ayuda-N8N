"""
Utilidad de notificación hacia N8N por webhook.

Responsabilidad:
    Implementa la comunicación de retorno desde esta API hacia N8N:
    luego de clasificar un incidente, notifica el resultado al webhook
    configurado en N8N para que el flujo de automatización continúe
    (por ejemplo, enviando confirmación al usuario o actualizando MTM-SRU).

Diseño fire-and-forget:
    Las fallas de esta notificación nunca se propagan al llamador.
    La integración con N8N es aditiva: si el webhook falla, el incidente
    ya fue creado y clasificado correctamente en la base de datos.
    Este diseño evita que la indisponibilidad temporal de N8N afecte
    la operación principal del sistema de clasificación.

Autenticación:
    Si N8N_WEBHOOK_SECRET está configurado, se envía como header
    X-N8N-Secret, permitiendo que el webhook de N8N verifique la
    autenticidad de la solicitud.
"""

import httpx

from app.config.settings import get_settings
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)


async def notify_n8n(incidente_id: int, result: ClasificacionResult) -> None:
    """
    Notifica el resultado de clasificación al webhook de N8N (fire-and-forget).

    Si N8N_WEBHOOK_URL no está configurado, retorna silenciosamente sin
    realizar ninguna llamada HTTP. Esto permite que el sistema funcione
    correctamente en entornos donde N8N no está disponible (por ejemplo,
    durante el desarrollo o los tests).

    El payload incluye los campos mínimos necesarios para que N8N
    pueda actualizar el sistema MTM-SRU con la categoría asignada:
        - incidente_id:           ID del incidente en la base de datos.
        - categoria:              Nombre del sector predicho.
        - confianza:              Nivel de certeza de la clasificación.
        - etapa:                  Qué componente del pipeline clasificó.
        - requiere_revision_humana: Si el operador debe revisar el caso.

    Args:
        incidente_id: ID del incidente recién clasificado.
        result:       Resultado del clasificador híbrido.
    """
    settings = get_settings()

    # Si no hay URL configurada, la integración con N8N está deshabilitada
    if not settings.n8n_webhook_url:
        return

    # Payload con los datos de clasificación para el flujo de N8N
    payload = {
        "incidente_id": incidente_id,
        "categoria": result.categoria,
        "confianza": result.confianza,
        "etapa": result.etapa,
        "requiere_revision_humana": result.requiere_revision_humana,
    }

    # Cabecera de autenticación para el webhook de N8N (opcional)
    headers = {}
    if settings.n8n_webhook_secret:
        headers["X-N8N-Secret"] = settings.n8n_webhook_secret

    try:
        # Timeout de 5 segundos: la notificación no debe bloquear la respuesta HTTP principal
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                settings.n8n_webhook_url, json=payload, headers=headers
            )
            response.raise_for_status()
            logger.info(
                "n8n_notified",
                incidente_id=incidente_id,
                status_code=response.status_code,
            )
    except Exception as exc:
        # Las fallas de notificación se registran como advertencia, no como error crítico
        logger.warning(
            "n8n_notification_failed",
            incidente_id=incidente_id,
            exc_info=exc,
        )
