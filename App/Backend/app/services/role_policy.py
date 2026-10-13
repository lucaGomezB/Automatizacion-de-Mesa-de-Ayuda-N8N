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
    """Modos de alcance de incidentes por rol (c-82, D1)."""

    PROPIO = "PROPIO"
    GLOBAL = "GLOBAL"
    VACIO = "VACIO"


@dataclass(frozen=True)
class PoliticaRol:
    """
    Politica de autorizacion/visibilidad de un rol (RP-001).

    Atributos:
        requires_sector:         si el rol exige un sector (falso para todos).
        visibilidad:             modo de alcance de incidentes (PROPIO/GLOBAL).
        privileged:              si confiere privilegio de identidad (MFA).
        manages_directory:       si puede gestionar (escribir) el directorio.
        can_read_directory:      si puede consultar el directorio.
        notification_recipient:  si es destinatario de la notificacion de revision.
    """

    requires_sector: bool
    visibilidad: ModoAlcance
    privileged: bool
    manages_directory: bool
    can_read_directory: bool
    notification_recipient: bool


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
    ),
    RolEmpleado.mesa_de_ayuda: PoliticaRol(
        requires_sector=False,
        visibilidad=ModoAlcance.GLOBAL,
        privileged=True,
        manages_directory=False,
        can_read_directory=True,
        notification_recipient=True,
    ),
    RolEmpleado.administrador_directorio: PoliticaRol(
        requires_sector=False,
        visibilidad=ModoAlcance.GLOBAL,
        privileged=True,
        manages_directory=True,
        can_read_directory=True,
        notification_recipient=False,
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
]
