"""
Postura efectiva de la guarda al arranque.

Registra, en un unico evento estructurado, el estado efectivo de la guarda
(habilitada, presupuesto, ventanas, costos unitarios por superficie, tasas y
politicas) para que un operador pueda verificarla sin inspeccionar el codigo.
"""

from app.core.logging import get_logger
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.constants import (
    EVENT_COST_GUARD_POSTURE,
    EVENT_COST_GUARD_SECRET_MISSING,
    EVENT_COST_GUARD_TWILIO_TOKEN_MISSING,
)

logger = get_logger(__name__)


def log_cost_guard_posture(config: CostGuardConfig) -> None:
    """
    Emite la postura efectiva de la guarda.

    Args:
        config: configuracion derivada de `Settings`.
    """
    logger.info(
        EVENT_COST_GUARD_POSTURE,
        enabled=config.enabled,
        budget_usd=str(config.budget_usd),
        budget_window_seconds=config.budget_window_seconds,
        unit_costs_usd={
            provider: str(cost) for provider, cost in config.unit_costs_usd.items()
        },
        rate_limit_calls=config.rate_limit_calls,
        rate_window_seconds=config.rate_window_seconds,
        caller_rate_limit_calls=config.caller_rate_limit_calls,
        caller_rate_window_seconds=config.caller_rate_window_seconds,
        degradation_policy=config.degradation_policy,
        store_failure_policy=config.store_failure_policy,
        alert_enabled=config.alert_enabled,
        shared_secret_configured=config.shared_secret_configured,
        twilio_auth_token_configured=config.twilio_auth_token_configured,
    )

    # Postura de borde: con la guarda habilitada y sin secreto compartido los
    # endpoints de guarda quedan cerrados (rechazan con 401). Se advierte de
    # forma explicita para que la misconfiguracion no pase silenciosa.
    if config.enabled and not config.shared_secret_configured:
        logger.warning(
            EVENT_COST_GUARD_SECRET_MISSING,
            detail=(
                "COST_GUARD_SHARED_SECRET no esta configurado: los endpoints "
                "de guarda rechazaran toda peticion con HTTP 401."
            ),
        )

    # Postura de borde del webhook de voz de Twilio: sin TWILIO_AUTH_TOKEN no
    # hay firma que validar y el endpoint rechaza con 401 (fail-closed). Al
    # cargar el token la validacion de firma se activa sin otro cambio.
    if config.enabled and not config.twilio_auth_token_configured:
        logger.warning(
            EVENT_COST_GUARD_TWILIO_TOKEN_MISSING,
            detail=(
                "TWILIO_AUTH_TOKEN no esta configurado: el webhook de voz de "
                "Twilio rechazara toda peticion con HTTP 401 hasta que se "
                "cargue el token."
            ),
        )


__all__ = ["log_cost_guard_posture"]
