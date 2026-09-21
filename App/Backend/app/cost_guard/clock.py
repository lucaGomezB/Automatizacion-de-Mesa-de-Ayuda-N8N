"""
Fuentes de tiempo de la guarda de costo.

`SystemClock` es la implementacion de produccion; `FrozenClock` es un reloj
controlado para pruebas (permite avanzar el tiempo sin dormir el proceso).
"""

from datetime import datetime, timedelta, timezone


class SystemClock:
    """Reloj de sistema en UTC con zona horaria."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenClock:
    """
    Reloj controlado para pruebas.

    El instante se congela en `now` y solo cambia con `advance`/`set`, de modo
    que las pruebas de reinicio de ventana son deterministas.
    """

    def __init__(self, now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("FrozenClock requiere un datetime con zona horaria")
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> datetime:
        """Avanza el reloj la cantidad de segundos indicada."""
        self._now = self._now + timedelta(seconds=seconds)
        return self._now

    def set(self, now: datetime) -> None:
        """Fija el instante actual."""
        self._now = now


__all__ = ["SystemClock", "FrozenClock"]
