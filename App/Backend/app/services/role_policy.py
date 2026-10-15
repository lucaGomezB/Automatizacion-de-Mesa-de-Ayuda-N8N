"""
Registro canonico de politica de rol (c-82, capability `role-policy`).

Responsabilidad:
    Concentra en un UNICO lugar el mapeo rol -> politica (RP-001) y expone
    derivaciones que consumen los demas modulos (RP-002/RP-004): el catalogo de
    roles privilegiados, la derivacion rol -> alcance de visibilidad, los guards
    de las rutas del directorio y el criterio de destinatarios de notificacion.

    Es la fuente unica de verdad del conocimiento de rol. Ningun modulo debe
    repetir el mapeo rol -> atributo con listas o cadenas de rol duplicadas.
    El enum del modelo y el CHECK de la base siguen existiendo (la base no lee
    codigo); el test de coherencia (RP-003) verifica que coincidan con
    `ROLES_VALIDOS`.

Modos de visibilidad (RP-001):
    - PROPIO: solo los incidentes reportados por el propio empleado.
    - GLOBAL: todos los incidentes.
    - VACIO:  ninguno (cuenta sin empleado vinculado).
    El aislamiento por sector y el antiguo modo de revision por sector NO
    existen.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum as PyEnum
from typing import Final, Mapping

from app.models.empleado import RolEmpleado


class ModoAlcance(str, PyEnum):
    """Modos de alcance de incidentes por rol (c-82 D1; c-86 D1)."""

    PROPIO = "PROPIO"
    GLOBAL = "GLOBAL"
    SECTOR = "SECTOR"
    VACIO = "VACIO"


@dataclass(frozen=True)
class PoliticaRol:
    """
    Politica de autorizacion/visibilidad de un rol (RP-001).

    Atributos:
        requires_sector:         si el rol exige un sector (c-86: solo gestion).
        visibilidad:             modo de alcance (PROPIO/GLOBAL/SECTOR/VACIO).
        privileged:              si confiere privilegio de identidad (MFA).
        manages_directory:       si puede gestionar (escribir) el directorio.
        can_read_directory:      si puede consultar el directorio.
        notification_recipient:  si es destinatario de la notificacion de revision.
        post_review_recipient:   si es destinatario del aviso post-revision (c-86).
        edita_estado:            si puede editar el estado no terminal (c-86, ILC-005).
        cierra_sector:           si puede cerrar por su sector (c-86, ILC-001).
        cierra_global:           si puede cerrar globalmente (c-86, ILC-002).
        reabre:                  si puede rehabilitar un incidente cerrado (c-86, ILC-004).
        can_delete_incident:     si puede borrar logicamente un incidente (c-87, RP-005).
        puede_asignar_prioridad_critica: si puede asignar/fijar la prioridad
                                 `critica` de un incidente (c-90, RP-006).
    """

    requires_sector: bool
    visibilidad: ModoAlcance
    privileged: bool
    manages_directory: bool
    can_read_directory: bool
    notification_recipient: bool
    post_review_recipient: bool = False
    edita_estado: bool = False
    cierra_sector: bool = False
    cierra_global: bool = False
    reabre: bool = False
    can_delete_incident: bool = False
    puede_asignar_prioridad_critica: bool = False


#: Vocabulario canonico del rol, derivado del enum (RP-002). El CHECK de la base
#: enumera los mismos valores y un test de coherencia lo verifica (RP-003).
ROLES_VALIDOS: Final[tuple[str, ...]] = tuple(r.value for r in RolEmpleado)

#: Registro canonico rol -> politica (fuente unica de verdad, RP-001).
ROLE_POLICY: Final[Mapping[RolEmpleado, PoliticaRol]] = {
    RolEmpleado.usuario_final: PoliticaRol(
        requires_sector=False,
        visibilidad=ModoAlcance.PROPIO,
        privileged=False,
        manages_directory=False,
        can_read_directory=False,
        notification_recipient=False,
        can_delete_incident=False,
        # c-90 (RP-006): el usuario final NO puede asignar la prioridad `critica`.
        puede_asignar_prioridad_critica=False,
    ),
    RolEmpleado.mesa_de_ayuda: PoliticaRol(
        requires_sector=False,
        visibilidad=ModoAlcance.GLOBAL,
        privileged=True,
        manages_directory=False,
        can_read_directory=True,
        notification_recipient=True,
        # c-86 (D1): mesa de ayuda edita el estado, cierra globalmente y reabre.
        edita_estado=True,
        cierra_global=True,
        reabre=True,
        can_delete_incident=False,
        # c-90 (RP-006): puede asignar/fijar la prioridad `critica`.
        puede_asignar_prioridad_critica=True,
    ),
    RolEmpleado.administrador_directorio: PoliticaRol(
        requires_sector=False,
        visibilidad=ModoAlcance.GLOBAL,
        privileged=True,
        manages_directory=True,
        can_read_directory=True,
        notification_recipient=False,
        # c-87 (RP-005): unico rol autorizado al borrado logico de incidentes.
        can_delete_incident=True,
        # c-90 (RP-006): el administrador del directorio tambien asigna `critica`.
        puede_asignar_prioridad_critica=True,
    ),
    RolEmpleado.gestion_incidentes: PoliticaRol(
        # c-86 (D1): rol operativo por sector. Exige sector, alcance SECTOR, NO
        # privilegiado, NO accede al directorio; cierra por sector, edita el
        # estado y es destinatario del aviso post-revision.
        requires_sector=True,
        visibilidad=ModoAlcance.SECTOR,
        privileged=False,
        manages_directory=False,
        can_read_directory=False,
        notification_recipient=False,
        post_review_recipient=True,
        edita_estado=True,
        cierra_sector=True,
        can_delete_incident=False,
        # c-90 (RP-006): gestion_incidentes NO puede asignar la prioridad `critica`.
        puede_asignar_prioridad_critica=False,
    ),
}


def politica_de_rol(rol: str | RolEmpleado | None) -> PoliticaRol | None:
    """
    Devuelve la politica del rol, normalizando enum o string.

    Un rol desconocido (fuera del vocabulario canonico) devuelve None: es la
    senal de divergencia que consumen los guards (deniegan por defecto).
    """
    if rol is None:
        return None
    if isinstance(rol, RolEmpleado):
        return ROLE_POLICY.get(rol)
    try:
        return ROLE_POLICY.get(RolEmpleado(str(rol)))
    except ValueError:
        return None


def roles_privilegiados() -> frozenset[str]:
    """Valores de rol que confieren privilegio de identidad (IAH-005)."""
    return frozenset(r.value for r, p in ROLE_POLICY.items() if p.privileged)


def roles_con_lectura_directorio() -> frozenset[str]:
    """Valores de rol autorizados a LEER el directorio (RP-004)."""
    return frozenset(
        r.value for r, p in ROLE_POLICY.items() if p.can_read_directory
    )


def roles_gestion_directorio() -> frozenset[str]:
    """Valores de rol autorizados a GESTIONAR el directorio."""
    return frozenset(
        r.value for r, p in ROLE_POLICY.items() if p.manages_directory
    )


def rol_destinatario_notificacion() -> str | None:
    """Valor del rol destinatario de la notificacion de revision (o None)."""
    for rol, politica in ROLE_POLICY.items():
        if politica.notification_recipient:
            return rol.value
    return None


def rol_destinatario_post_revision() -> str | None:
    """Valor del rol destinatario del aviso post-revision (o None, c-86 NR-008)."""
    for rol, politica in ROLE_POLICY.items():
        if politica.post_review_recipient:
            return rol.value
    return None


def roles_con_visibilidad_sector() -> frozenset[str]:
    """Valores de rol cuyo alcance de incidentes es SECTOR (c-86, VIS-007)."""
    return frozenset(
        r.value
        for r, p in ROLE_POLICY.items()
        if p.visibilidad is ModoAlcance.SECTOR
    )


def roles_que_cierran_sector() -> frozenset[str]:
    """Valores de rol autorizados a cerrar por su sector (c-86, ILC-001)."""
    return frozenset(r.value for r, p in ROLE_POLICY.items() if p.cierra_sector)


def roles_que_cierran_global() -> frozenset[str]:
    """Valores de rol autorizados a cerrar globalmente (c-86, ILC-002)."""
    return frozenset(r.value for r, p in ROLE_POLICY.items() if p.cierra_global)


def roles_que_reabren() -> frozenset[str]:
    """Valores de rol autorizados a rehabilitar un incidente (c-86, ILC-004)."""
    return frozenset(r.value for r, p in ROLE_POLICY.items() if p.reabre)


def roles_que_editan_estado() -> frozenset[str]:
    """Valores de rol autorizados a editar el estado (c-86, ILC-005)."""
    return frozenset(r.value for r, p in ROLE_POLICY.items() if p.edita_estado)


def roles_con_borrado_incidentes() -> frozenset[str]:
    """Valores de rol autorizados al borrado logico de incidentes (c-87, RP-005)."""
    return frozenset(
        r.value for r, p in ROLE_POLICY.items() if p.can_delete_incident
    )


def roles_con_asignacion_prioridad_critica() -> frozenset[str]:
    """Valores de rol autorizados a asignar la prioridad `critica` (c-90, RP-006)."""
    return frozenset(
        r.value for r, p in ROLE_POLICY.items() if p.puede_asignar_prioridad_critica
    )


def puede_asignar_prioridad_critica(rol: str | RolEmpleado | None) -> bool:
    """
    Indica si un rol puede asignar/fijar la prioridad `critica` (c-90, RP-006).

    Normaliza enum o string y DENIEGA POR DEFECTO: un rol desconocido, fuera del
    registro, o nulo devuelve False. Es el unico predicado que consumen los
    guards de las rutas; ninguna lista de rol se duplica.
    """
    politica = politica_de_rol(rol)
    return bool(politica is not None and politica.puede_asignar_prioridad_critica)


__all__ = [
    "ModoAlcance",
    "PoliticaRol",
    "ROLE_POLICY",
    "ROLES_VALIDOS",
    "politica_de_rol",
    "roles_privilegiados",
    "roles_con_lectura_directorio",
    "roles_gestion_directorio",
    "rol_destinatario_notificacion",
    "rol_destinatario_post_revision",
    "roles_con_visibilidad_sector",
    "roles_que_cierran_sector",
    "roles_que_cierran_global",
    "roles_que_reabren",
    "roles_que_editan_estado",
    "roles_con_borrado_incidentes",
    "roles_con_asignacion_prioridad_critica",
    "puede_asignar_prioridad_critica",
]
