"""
Protocolos de la guarda de costo: almacen de contadores y fuente de tiempo.

La guarda depende de estas abstracciones (no de implementaciones concretas),
lo que permite inyectar un almacen en memoria y un reloj controlado en las
pruebas offline, sin red ni PostgreSQL.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol, Sequence, runtime_checkable


@dataclass(frozen=True)
class CounterKey:
    """Clave de un contador: ambito, clave logica y ventana (bucket tumbling)."""

    ambito: str
    clave: str
    ventana_inicio: datetime


@dataclass(frozen=True)
class Reservation:
    """Incremento atomico a aplicar sobre un contador."""

    key: CounterKey
    calls_delta: int
    cost_delta: Decimal


@dataclass(frozen=True)
class CounterSnapshot:
    """Valores resultantes de un contador tras aplicar una reserva."""

    llamadas: int
    costo_usd: Decimal


@runtime_checkable
class CounterStore(Protocol):
    """
    Almacen de contadores de la guarda.

    Contrato transaccional: `reserve_many` aplica los incrementos en una
    transaccion propia (fuera de la transaccion del incidente) y devuelve los
    valores resultantes; `commit` la confirma y `rollback` la descarta. El
    llamador decide segun la funcion de decision pura.
    """

    async def reserve_many(
        self, reservations: Sequence[Reservation]
    ) -> list[CounterSnapshot]:
        """Aplica las reservas y devuelve los snapshots resultantes, en orden."""
        ...

    async def commit(self) -> None:
        """Confirma la transaccion de reserva."""
        ...

    async def rollback(self) -> None:
        """Descarta la transaccion de reserva."""
        ...

    async def purge_expired(self, ambito: str, before: datetime) -> int:
        """Elimina contadores del ambito cuya ventana inicio es anterior a `before`."""
        ...


@runtime_checkable
class Clock(Protocol):
    """Fuente de tiempo inyectable."""

    def now(self) -> datetime:
        """Instante actual con zona horaria (UTC)."""
        ...


__all__ = [
    "CounterKey",
    "Reservation",
    "CounterSnapshot",
    "CounterStore",
    "Clock",
]
