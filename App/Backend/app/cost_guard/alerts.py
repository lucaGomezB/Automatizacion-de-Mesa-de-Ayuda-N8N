"""
Notificacion externa de la guarda de costo.

`cost_guard_alert_enabled` controla si, ademas del evento estructurado
OBLIGATORIO `cost_guard_store_unavailable`, la guarda dispara una notificacion
externa al webhook de N8N configurado (`N8N_WEBHOOK_URL`). El evento
estructurado siempre se emite (requisito de observabilidad); esta notificacion
es ADICIONAL y best-effort: su fallo nunca altera la decision de la guarda.

El notificador se define como protocolo inyectable para que la guarda siga
siendo evaluable offline (los tests inyectan un doble sin red).
"""

from typing import Protocol

import httpx

from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertNotifier(Protocol):
    """Sink de notificacion externa de la guarda (implementacion inyectable)."""

    async def notify(self, event: str, **fields: object) -> None:
        """Envia una notificacion del evento indicado; best-effort."""
        ...


class WebhookAlertNotifier:
    """Envia la alerta al webhook de N8N configurado; no-op si no hay URL."""

    async def notify(self, event: str, **fields: object) -> None:
        settings = get_settings()
        url = settings.n8n_webhook_url
        if not url:
            return

        headers: dict[str, str] = {}
        if settings.n8n_webhook_secret:
            headers["X-N8N-Secret"] = settings.n8n_webhook_secret

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json={"evento": event, **fields},
                    headers=headers,
                )
                response.raise_for_status()
        except Exception as exc:  # best-effort: nunca propaga
            logger.warning(
                "cost_guard_alert_failed",
                event=event,
                error_class=type(exc).__name__,
            )


__all__ = ["AlertNotifier", "WebhookAlertNotifier"]