"""
Regla de visibilidad de incidentes por rol (c-54, VIS-001 / D7).

Responsabilidad:
    Derivar el ALCANCE de incidentes de la cuenta autenticada a partir de su
    empleado en el directorio (`directorio_empleado.user_id -> rol/sector_id`).

Decision de implementacion (governance HIGH, documentada):
    El sector efectivo se deriva del directorio via `user_id`.
    - `administrador_directorio`: ve TODOS los incidentes (ver_todos=True).
    - `usuario_final` / `operador` con sector: ve solo los de su sector.
    - Cuenta sin empleado vinculado o sin sector: alcance VACIO (ver_todos=False
      y sector_id=None), es decir no ve incidentes por esta via.

    Este modulo vive en la capa de servicio y es consumido por la API de
    incidentes; NO toca el clasificador ni las notificaciones.
"""

from dataclasses import dataclass

from app.models.empleado import Empleado, RolEmpleado


@dataclass(frozen=True)
class AlcanceIncidentes:
    """
    Alcance de lectura de incidentes de una cuenta autenticada.

    `ver_todos=True` significa acceso global (administrador). En caso contrario,
    `sector_id` restringe la lectura a ese sector; `sector_id=None` con
    `ver_todos=False` representa un alcance VACIO.
    """

    ver_todos: bool
    sector_id: int | None

    @property
    def vacio(self) -> bool:
        return not self.ver_todos and self.sector_id is None

    def permite_sector(self, sector_id: int | None) -> bool:
        if self.ver_todos:
            return True
        return self.sector_id is not None and sector_id == self.sector_id


def alcance_desde_empleado(empleado: Empleado | None) -> AlcanceIncidentes:
    """Deriva el alcance de incidentes del empleado vinculado (o vacio si None)."""
    if empleado is None:
        return AlcanceIncidentes(ver_todos=False, sector_id=None)
    if empleado.rol == RolEmpleado.administrador_directorio:
        return AlcanceIncidentes(ver_todos=True, sector_id=None)
    if empleado.sector_id is None:
        return AlcanceIncidentes(ver_todos=False, sector_id=None)
    return AlcanceIncidentes(ver_todos=False, sector_id=empleado.sector_id)
