"""
Regla de visibilidad de incidentes por alcance (c-82, VIS-001/VIS-002; c-86 VIS-007).

Responsabilidad:
    Derivar el ALCANCE de incidentes de la cuenta autenticada a partir de su
    empleado en el directorio (`directorio_empleado.user_id -> rol`) y del
    registro unico de politica de rol (`app.services.role_policy`).

Modelo de modos (c-82 D1; c-86 D1):
    - `GLOBAL` (administrador_directorio / mesa_de_ayuda): ve TODOS los incidentes.
    - `PROPIO` (usuario_final): ve solo los incidentes cuyo `reportante_empleado_id`
                es su propio empleado.
    - `SECTOR` (gestion_incidentes): ve solo los incidentes cuyo conjunto de
                sectores incluye su sector y que NO estan cerrados para su sector
                (VIS-007). Si el empleado no tiene sector, el alcance es VACIO.
    - `VACIO`  (cuenta sin empleado): no ve incidentes.

    El sector NO acota los alcances PROPIO y GLOBAL; para SECTOR SI es frontera.

    Este modulo vive en la capa de servicio y es consumido por la API de
    incidentes y de clasificaciones; NO toca el clasificador ni las notificaciones.
"""

from dataclasses import dataclass
from typing import AbstractSet, Protocol, Sequence

from app.models.empleado import Empleado
from app.services.role_policy import ModoAlcance, politica_de_rol

__all__ = [
    "AlcanceIncidentes",
    "IncidenteVisible",
    "ModoAlcance",
    "alcance_desde_empleado",
]


class SectorRef(Protocol):
    """Contrato minimo de un sector dentro del conjunto del incidente."""

    id: int


class IncidenteVisible(Protocol):
    """Contrato minimo que `permite_incidente` necesita de un incidente.

    Los alcances PROPIO/GLOBAL solo leen `reportante_empleado_id`; el alcance
    SECTOR ademas lee el conjunto de sectores (`sector_id` + `sectores_adicionales`)
    y los sectores ya cerrados (`sectores_cerrados`) para decidir sin queries
    ocultas (c-86, D2).
    """

    reportante_empleado_id: int | None
    sector_id: int | None
    sectores_adicionales: Sequence[SectorRef]
    sectores_cerrados: AbstractSet[int]


@dataclass(frozen=True)
class AlcanceIncidentes:
    """
    Alcance de lectura de incidentes de una cuenta autenticada (c-82 D1; c-86 D2).

    `modo` es el modo PROPIO/GLOBAL/SECTOR/VACIO; `reportante_empleado_id` es el
    id del empleado cuyo reporte define el alcance PROPIO; `sector_id` es el
    sector del empleado que define el alcance SECTOR.
    """

    modo: ModoAlcance = ModoAlcance.VACIO
    reportante_empleado_id: int | None = None
    sector_id: int | None = None

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
        if self.modo is ModoAlcance.SECTOR:
            if self.sector_id is None:
                return False
            conjunto = {s.id for s in incidente.sectores_adicionales}
            if incidente.sector_id is not None:
                conjunto.add(incidente.sector_id)
            if self.sector_id not in conjunto:
                return False
            return self.sector_id not in incidente.sectores_cerrados
        return False


def alcance_desde_empleado(empleado: Empleado | None) -> AlcanceIncidentes:
    """Deriva el alcance de incidentes del empleado vinculado (o vacio si None).

    El modo se lee del registro unico de politica de rol (RP-002): no se duplica
    el mapeo rol -> alcance. Una cuenta sin empleado o con un rol desconocido
    obtiene un alcance VACIO. Un `gestion_incidentes` sin sector asignado
    (requiere sector) tambien obtiene VACIO (c-86, D2/VIS-007).
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
    if politica.visibilidad is ModoAlcance.SECTOR:
        if empleado.sector_id is None:
            return AlcanceIncidentes()
        return AlcanceIncidentes(ModoAlcance.SECTOR, sector_id=empleado.sector_id)
    return AlcanceIncidentes()
