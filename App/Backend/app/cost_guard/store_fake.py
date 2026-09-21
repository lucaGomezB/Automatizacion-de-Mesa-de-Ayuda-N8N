"""
Almacen de contadores en memoria (fake inyectable, sin red).

Implementa el protocolo `CounterStore` con estado en un diccionario y una
transaccion de staging: `reserve_many` calcula los valores pendientes,
`commit` los consolida y `rollback` los descarta. Es la dependencia que usan
las pruebas offline y las validaciones deterministas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Sequence

from app.cost_guard.protocols import (
    CounterKey,
    CounterSnapshot,
    Reservation,
)

_ZERO = Decimal("0")


class InMemoryCounterStore:
    """Almacen de contadores en memoria con transaccion de staging."""

    def __init__(self) -> None:
        self._committed: dict[CounterKey, CounterSnapshot] = {}
        self._pending: dict[CounterKey, CounterSnapshot] | None = None

    # ── Utilidades de inspeccion / siembra ───────────────────────────────────

    def seed(
        self,
        key: CounterKey,
        llamadas: int = 0,
        costo_usd: Decimal = _ZERO,
    ) -> None:
        """Fija el valor de un contador consolidado (uso en pruebas)."""
        self._committed[key] = CounterSnapshot(
            llamadas=llamadas, costo_usd=Decimal(costo_usd)
        )

    def snapshot(self, key: CounterKey) -> CounterSnapshot:
        """Valor consolidado de un contador (cero si no existe)."""
        return self._committed.get(key, CounterSnapshot(llamadas=0, costo_usd=_ZERO))

    @property
    def committed(self) -> dict[CounterKey, CounterSnapshot]:
        """Copia del estado consolidado (solo lectura)."""
        return dict(self._committed)

    # ── Protocolo CounterStore ───────────────────────────────────────────────

    async def reserve_many(
        self, reservations: Sequence[Reservation]
    ) -> list[CounterSnapshot]:
        pending = dict(self._committed)
        result: list[CounterSnapshot] = []
        for reservation in reservations:
            current = pending.get(
                reservation.key, CounterSnapshot(llamadas=0, costo_usd=_ZERO)
            )
            updated = CounterSnapshot(
                llamadas=current.llamadas + reservation.calls_delta,
                costo_usd=current.costo_usd + reservation.cost_delta,
            )
            pending[reservation.key] = updated
            result.append(updated)
        self._pending = pending
        return result

    async def commit(self) -> None:
        if self._pending is not None:
            self._committed = self._pending
        self._pending = None

    async def rollback(self) -> None:
        self._pending = None

    async def purge_expired(self, ambito: str, before: datetime) -> int:
        expired = [
            key
            for key in self._committed
            if key.ambito == ambito and key.ventana_inicio < before
        ]
        for key in expired:
            del self._committed[key]
        return len(expired)


__all__ = ["InMemoryCounterStore"]
