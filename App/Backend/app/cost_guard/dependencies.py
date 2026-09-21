"""
Dependencias de FastAPI para la guarda de costo.

Construye la guarda de produccion (almacen PostgreSQL y reloj de sistema) a
partir de `Settings`. Los tests pueden sobrescribir `get_cost_guard` para
inyectar un almacen falso o deshabilitar el enforcement.
"""

from app.config.settings import get_settings
from app.cost_guard.alerts import WebhookAlertNotifier
from app.cost_guard.clock import SystemClock
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.guard import CostGuard
from app.cost_guard.protocols import Clock, CounterStore
from app.cost_guard.store_postgres import PostgresCounterStore


def build_cost_guard(
    store: CounterStore | None = None,
    clock: Clock | None = None,
    config: CostGuardConfig | None = None,
) -> CostGuard:
    """
    Construye una guarda con dependencias inyectables.

    Args:
        store: almacen de contadores (por defecto, PostgreSQL).
        clock: fuente de tiempo (por defecto, reloj de sistema).
        config: configuracion efectiva (por defecto, derivada de Settings).
    """
    settings = get_settings()
    return CostGuard(
        store=store or PostgresCounterStore(),
        clock=clock or SystemClock(),
        config=config or CostGuardConfig.from_settings(settings),
        alert_notifier=WebhookAlertNotifier(),
    )


def get_cost_guard() -> CostGuard:
    """Dependencia de FastAPI que provee la guarda de costo de produccion."""
    return build_cost_guard()


__all__ = ["build_cost_guard", "get_cost_guard"]
