"""
Regla de visibilidad de incidentes por alcance (c-82, VIS-001/VIS-002).

Responsabilidad:
    Derivar el ALCANCE de incidentes de la cuenta autenticada a partir de su
    empleado en el directorio (`directorio_empleado.user_id -> rol`) y del
    registro unico de politica de rol (`app.services.role_policy`).

Modelo de modos (c-82 D1):
    - `GLOBAL` (administrador_directorio / mesa_de_ayuda): ve TODOS los incidentes.
    - `PROPIO` (usuario_final): ve solo los incidentes cuyo `reportante_empleado_id`
                es su propio empleado.
    - `VACIO`  (cuenta sin empleado): no ve incidentes.

    El sector deja de ser frontera de acceso: NO se acota por `sector_id`.

    Este modulo vive en la capa de servicio y es consumido por la API de
    incidentes y de clasificaciones; NO toca el clasificador ni las notificaciones.
"""

from dataclasses import dataclass
from typing import Protocol

from app.models.empleado import Empleado
from app.services.role_policy import ModoAlcance, politica_de_rol

__all__ = [
    "AlcanceIncidentes",
    "IncidenteVisible",
    "ModoAlcance",
    "alcance_desde_empleado",
]


class IncidenteVisible(Protocol):
    """Contrato minimo que `permite_incidente` necesita de un incidente."""

    reportante_empleado_id: int | None


@dataclass(frozen=True)
class AlcanceIncidentes:
    """
    Alcance de lectura de incidentes de una cuenta autenticada (c-82 D1).

    `modo` es el modo PROPIO/GLOBAL/VACIO; `reportante_empleado_id` es el id del
    empleado cuyo reporte define el alcance PROPIO.
    """

    modo: ModoAlcance = ModoAlcance.VACIO
    reportante_empleado_id: int | None = None

    @property
    def vacio(self) -> bool:
        return self.modo is ModoAlcance.VACIO

    @property
    def ver_todos(self) -> bool:
        return self.modo is ModoAlcance.GLOBAL

    def permite_incidente(self, incidente: IncidenteVisible) -> bool:
        """Decision de visibilidad segun el modo, con el incidente completo."""
        if self.modo is ModoAlcance.GLOBAL:
            return True
        if self.modo is ModoAlcance.PROPIO:
            return (
                self.reportante_empleado_id is not None
                and incidente.reportante_empleado_id == self.reportante_empleado_id
            )
        return False


def alcance_desde_empleado(empleado: Empleado | None) -> AlcanceIncidentes:
    """Deriva el alcance de incidentes del empleado vinculado (o vacio si None).

    El modo se lee del registro unico de politica de rol (RP-002): no se duplica
    el mapeo rol -> alcance. Una cuenta sin empleado o con un rol desconocido
    obtiene un alcance VACIO.
    """
    if empleado is None:
        return AlcanceIncidentes()
    politica = politica_de_rol(empleado.rol)
    if politica is None:
        return AlcanceIncidentes()
    if politica.visibilidad is ModoAlcance.GLOBAL:
        return AlcanceIncidentes(ModoAlcance.GLOBAL)
    if politica.visibilidad is ModoAlcance.PROPIO:
        return AlcanceIncidentes(ModoAlcance.PROPIO, empleado.id)
    return AlcanceIncidentes()
