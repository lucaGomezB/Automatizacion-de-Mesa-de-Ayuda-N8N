"""
Funcion de decision PURA de la guarda de costo.

Sin efectos secundarios ni acceso a red: recibe los contadores resultantes de
la reserva, los limites configurados y el instante, y decide permitir o denegar
con una causa estable. Es el nucleo determinista y offline-testeable de la
guarda.

Semantica de tope: la reserva se aplica ANTES de decidir; se deniega cuando el
valor resultante EXCEDE el limite. Asi, el gasto/llamada que alcanza exactamente
el limite se concede y los ADICIONALES se bloquean, que es la semantica de tope
("no gastar mas de X" / "impedir llamadas adicionales").
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from app.cost_guard.constants import (
    CAUSE_BUDGET,
    CAUSE_CALLER_RATE,
    CAUSE_RATE,
)


@dataclass(frozen=True)
class GuardCounters:
    """Contadores resultantes de una reserva, en la unidad de cada limite."""

    budget_cost_usd: Decimal
    rate_calls: int
    caller_calls: int | None = None


@dataclass(frozen=True)
class GuardLimits:
    """Limites configurados que la decision pura evalua."""

    budget_usd: Decimal
    rate_limit_calls: int
    caller_rate_limit_calls: int


@dataclass(frozen=True)
class GuardDecision:
    """Resultado de la decision: permitir o denegar con causa."""

    allowed: bool
    cause: str | None = None


def window_start(now: datetime, window_seconds: int) -> datetime:
    """
    Inicio del bucket tumbling que contiene a `now`.

    El bucket esta anclado a epoch y tiene la duracion indicada, de modo que el
    calculo es determinista y reproducible con un reloj inyectado.

    Args:
        now: instante con zona horaria (UTC).
        window_seconds: duracion de la ventana en segundos (> 0).

    Returns:
        Inicio de la ventana como datetime UTC con zona horaria.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds debe ser mayor que cero")
    if now.tzinfo is None:
        raise ValueError("now debe tener zona horaria (UTC)")
    epoch_seconds = int(now.timestamp())
    start = epoch_seconds - (epoch_seconds % window_seconds)
    return datetime.fromtimestamp(start, tz=timezone.utc)


def evaluate_counters(counters: GuardCounters, limits: GuardLimits) -> GuardDecision:
    """
    Decide si una llamada paga puede proceder a partir de los contadores.

    Orden de evaluacion (la primera causa que excede gana): presupuesto global,
    tasa global de llamadas y tasa por numero de origen.

    Args:
        counters: contadores resultantes de la reserva (post-incremento).
        limits: limites configurados.

    Returns:
        GuardDecision permitida, o denegada con la causa del disparo.
    """
    if counters.budget_cost_usd > limits.budget_usd:
        return GuardDecision(allowed=False, cause=CAUSE_BUDGET)
    if counters.rate_calls > limits.rate_limit_calls:
        return GuardDecision(allowed=False, cause=CAUSE_RATE)
    if (
        counters.caller_calls is not None
        and counters.caller_calls > limits.caller_rate_limit_calls
    ):
        return GuardDecision(allowed=False, cause=CAUSE_CALLER_RATE)
    return GuardDecision(allowed=True, cause=None)


__all__ = [
    "GuardCounters",
    "GuardLimits",
    "GuardDecision",
    "window_start",
    "evaluate_counters",
]
