"""
Servicio de aplicacion de la guarda de costo.

Adapta la guarda de dominio (`CostGuard`) al consumo de la capa de rutas. Si no
hay guarda inyectada (tests o guarda deshabilitada por composicion), permite la
llamada sin tocar el almacen.
"""

from decimal import Decimal

from app.cost_guard.decision import GuardDecision
from app.cost_guard.guard import CostGuard


class CostGuardService:
    """Punto de acceso de la capa de servicio a la guarda de costo."""

    def __init__(self, guard: CostGuard | None = None) -> None:
        self._guard = guard

    async def reserve(
        self,
        provider: str,
        caller: str | None = None,
        amount: Decimal | int = Decimal("1"),
    ) -> GuardDecision:
        """
        Evalua la guarda antes de una llamada paga.

        Args:
            provider: superficie paga.
            caller: numero de origen CRUDO cuando esta disponible.
            amount: cantidad de unidades del costo unitario a reservar
                (c-52: `backend_stt` estima por duracion acotada).

        Returns:
            GuardDecision permitida o denegada con causa.
        """
        if self._guard is None:
            return GuardDecision(allowed=True, cause=None)
        return await self._guard.evaluate(provider, caller=caller, amount=amount)


__all__ = ["CostGuardService"]
