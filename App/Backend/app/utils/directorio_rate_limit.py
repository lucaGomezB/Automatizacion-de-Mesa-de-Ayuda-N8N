"""
Limitacion de tasa en memoria para la lectura del directorio (c-153, DIR-006).

Responsabilidad:
    Acotar la FRECUENCIA de las peticiones de lectura del directorio por actor,
    como control de anti-enumeracion: peticiones repetidas o masivas dejan de
    revelar filas fuera de alcance cuando superan el umbral. El contador vive en
    memoria del proceso (sin Redis desde c-62); es una defensa DELIBERADA y
    acotada, no una garantia distribuida entre instancias.

Diseno:
    Ventana FIJA por clave (actor): el primer acceso abre la ventana y los
    accesos siguientes cuentan dentro de ella; al vencer, la ventana se reinicia.
    El reloj es inyectable para pruebas deterministas. La clase es una unidad
    pura de conteo: no conoce HTTP ni la capa de rutas.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class RateLimiterDirectorio:
    """Limitador de tasa de ventana fija, por clave (actor), en memoria."""

    def __init__(
        self,
        *,
        max_peticiones: int,
        ventana_segundos: float,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_peticiones < 1:
            raise ValueError("max_peticiones debe ser >= 1")
        if ventana_segundos <= 0:
            raise ValueError("ventana_segundos debe ser > 0")
        self._max = max_peticiones
        self._ventana = ventana_segundos
        self._reloj = reloj
        self._inicio: dict[int, float] = {}
        self._conteo: dict[int, int] = {}

    def permitir(self, clave: int) -> bool:
        """
        Registra un acceso y devuelve si queda dentro del limite.

        El primer acceso de una ventana siempre se permite; los siguientes
        cuentan hasta `max_peticiones`. Devuelve False a partir del exceso.
        """
        ahora = self._reloj()
        inicio = self._inicio.get(clave)
        if inicio is None or (ahora - inicio) >= self._ventana:
            self._inicio[clave] = ahora
            self._conteo[clave] = 1
            return True
        conteo = self._conteo.get(clave, 0) + 1
        self._conteo[clave] = conteo
        return conteo <= self._max

    def reiniciar(self, clave: int | None = None) -> None:
        """Olvida el estado de una clave (o de todas si `clave` es None)."""
        if clave is None:
            self._inicio.clear()
            self._conteo.clear()
        else:
            self._inicio.pop(clave, None)
            self._conteo.pop(clave, None)


def crear_rate_limiter_directorio() -> RateLimiterDirectorio:
    """
    Construye el limitador a partir de la configuracion.

    La lectura de `Settings` vive AQUI (no en la capa de rutas) para que las
    rutas del directorio no consulten el entorno directamente (guardia de
    runtime, DIR-008 / c-60).
    """
    from app.config.settings import get_settings

    settings = get_settings()
    return RateLimiterDirectorio(
        max_peticiones=settings.directorio_rate_limit_reads,
        ventana_segundos=settings.directorio_rate_window_seconds,
    )


__all__ = ["RateLimiterDirectorio", "crear_rate_limiter_directorio"]
