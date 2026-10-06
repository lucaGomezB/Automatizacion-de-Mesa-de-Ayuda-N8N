"""
Regla de visibilidad de incidentes por rol (c-54 VIS-001/D7; c-60 D3).

Responsabilidad:
    Derivar el ALCANCE de incidentes de la cuenta autenticada a partir de su
    empleado en el directorio (`directorio_empleado.user_id -> rol/sector_id`).

Modelo de modos (c-60 D3):
    - `GLOBAL`   (administrador_directorio): ve TODOS los incidentes.
    - `SECTOR`   (usuario_final / operador con sector): ve solo su sector.
    - `REVISION` (mesa_de_ayuda): ve los incidentes SIN sector o que requieren
                 revision humana. Es el minimo necesario para revisar la cola,
                 no el universo completo.
    - `VACIO`    (cuenta sin empleado o empleado sin sector): no ve incidentes
                 por esta via.

Decision de implementacion (governance HIGH, documentada):
    El sector efectivo se deriva del directorio via `user_id`. Se conserva
    `permite_sector` por compatibilidad con los call sites de c-54 que verifican
    por sector; donde la decision depende del incidente completo (REVISION), los
    call sites usan `permite_incidente`.

    Este modulo vive en la capa de servicio y es consumido por la API de
    incidentes y de clasificaciones; NO toca el clasificador ni las notificaciones.
"""

from dataclasses import dataclass
from enum import Enum as PyEnum
from typing import Protocol

from app.models.empleado import Empleado, RolEmpleado


class ModoAlcance(str, PyEnum):
    """Modos de alcance de incidentes por rol (c-60 D3)."""

    GLOBAL = "GLOBAL"
    SECTOR = "SECTOR"
    REVISION = "REVISION"
    VACIO = "VACIO"


class IncidenteVisible(Protocol):
    """Contrato minimo que `permite_incidente` necesita de un incidente."""

    sector_id: int | None
    requiere_revision_humana: bool


@dataclass(frozen=True)
class AlcanceIncidentes:
    """
    Alcance de lectura de incidentes de una cuenta autenticada.

    Los campos `ver_todos`/`sector_id` conservan la firma de c-54; `revision`
    incorpora el modo de la cola de revision (c-60). El `modo` se deriva de
    ellos para que la representacion sea unica.
    """

    ver_todos: bool = False
    sector_id: int | None = None
    revision: bool = False

    @property
    def modo(self) -> ModoAlcance:
        if self.ver_todos:
            return ModoAlcance.GLOBAL
        if self.revision:
            return ModoAlcance.REVISION
        if self.sector_id is not None:
            return ModoAlcance.SECTOR
        return ModoAlcance.VACIO

    @property
    def vacio(self) -> bool:
        return self.modo is ModoAlcance.VACIO

    def permite_sector(self, sector_id: int | None) -> bool:
        """Compatibilidad c-54: decision por sector (no aplica en REVISION)."""
        if self.ver_todos:
            return True
        return self.modo is ModoAlcance.SECTOR and sector_id == self.sector_id

    def permite_incidente(self, incidente: IncidenteVisible) -> bool:
        """Decision de visibilidad segun el modo, con el incidente completo."""
        modo = self.modo
        if modo is ModoAlcance.GLOBAL:
            return True
        if modo is ModoAlcance.SECTOR:
            return incidente.sector_id == self.sector_id
        if modo is ModoAlcance.REVISION:
            return incidente.sector_id is None or bool(
                incidente.requiere_revision_humana
            )
        return False


def alcance_desde_empleado(empleado: Empleado | None) -> AlcanceIncidentes:
    """Deriva el alcance de incidentes del empleado vinculado (o vacio si None)."""
    if empleado is None:
        return AlcanceIncidentes()
    if empleado.rol == RolEmpleado.administrador_directorio:
        return AlcanceIncidentes(ver_todos=True)
    if empleado.rol == RolEmpleado.mesa_de_ayuda:
        return AlcanceIncidentes(revision=True)
    if empleado.sector_id is None:
        return AlcanceIncidentes()
    return AlcanceIncidentes(sector_id=empleado.sector_id)