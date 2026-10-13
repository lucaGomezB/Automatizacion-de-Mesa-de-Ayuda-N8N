"""
Tests del registro canonico de politica de rol (c-82, role-policy).

Cubren, en estricto RED -> GREEN -> TRIANGULATE -> REFACTOR:
    - RP-001: el registro define EXACTAMENTE los tres roles y, para cada uno,
      sus atributos (requires_sector, visibilidad, privileged, manages_directory,
      can_read_directory, notification_recipient).
    - RP-003: coherencia verificable entre el vocabulario del CHECK, el enum y
      el registro; aparece un rol fuera de los tres canonicos => falla.
    - RP-002/RP-004: los consumidores consumen el registro y no duplican listas.

Sin PII: ningun valor de contacto interviene.
"""

import pytest
from sqlalchemy import CheckConstraint

from app.models.empleado import Empleado, RolEmpleado


# ── Helpers ────────────────────────────────────────────────────────────────────


def _policy():
    from app.services.role_policy import ROLE_POLICY

    return ROLE_POLICY


def _modo():
    from app.services.role_policy import ModoAlcance

    return ModoAlcance


# ═══════════════════════════════════════════════════════════════════════════════
# RP-001 — Registro canonico de roles y politica
# ═══════════════════════════════════════════════════════════════════════════════


def test_rp_001_el_registro_define_exactamente_los_tres_roles():
    """El registro contiene exactamente los tres roles canonicos."""
    from app.services.role_policy import ROLE_POLICY

    assert set(ROLE_POLICY.keys()) == {
        RolEmpleado.usuario_final,
        RolEmpleado.mesa_de_ayuda,
        RolEmpleado.administrador_directorio,
    }


def test_rp_001_todos_los_roles_tienen_politica_completa():
    """Cada entrada declara visibilidad, privilegio, gestion y destinatario."""
    for rol, politica in _policy().items():
        assert politica.visibilidad is not None, rol
        assert isinstance(politica.privileged, bool), rol
        assert isinstance(politica.manages_directory, bool), rol
        assert isinstance(politica.can_read_directory, bool), rol
        assert isinstance(politica.notification_recipient, bool), rol


def test_rp_001_sectores_no_requeridos():
    """`requires_sector` es falso para los tres roles."""
    assert all(politica.requires_sector is False for politica in _policy().values())


def test_rp_001_modos_de_visibilidad_acotados():
    """`usuario_final` es PROPIO; `mesa_de_ayuda` y admin son GLOBAL."""
    ModoAlcance = _modo()
    politicas = _policy()
    assert politicas[RolEmpleado.usuario_final].visibilidad is ModoAlcance.PROPIO
    assert politicas[RolEmpleado.mesa_de_ayuda].visibilidad is ModoAlcance.GLOBAL
    assert (
        politicas[RolEmpleado.administrador_directorio].visibilidad
        is ModoAlcance.GLOBAL
    )


def test_rp_001_atributos_por_rol():
    """Privilegio, gestion de directorio y destinatario por rol."""
    p = _policy()

    final = p[RolEmpleado.usuario_final]
    assert final.privileged is False
    assert final.manages_directory is False
    assert final.can_read_directory is False
    assert final.notification_recipient is False

    mesa = p[RolEmpleado.mesa_de_ayuda]
    assert mesa.privileged is True
    assert mesa.can_read_directory is True
    assert mesa.manages_directory is False
    assert mesa.notification_recipient is True

    admin = p[RolEmpleado.administrador_directorio]
    assert admin.privileged is True
    assert admin.can_read_directory is True
    assert admin.manages_directory is True
    assert admin.notification_recipient is False


def test_rp_001_los_modos_validos_son_solo_propio_global_y_vacio():
    """No existen SECTOR ni REVISION como modos de visibilidad."""
    ModoAlcance = _modo()
    assert {m.value for m in ModoAlcance} == {"PROPIO", "GLOBAL", "VACIO"}


# ═══════════════════════════════════════════════════════════════════════════════
# RP-002 / RP-004 — Derivacion desde el registro
# ═══════════════════════════════════════════════════════════════════════════════


def test_rp_002_roles_privilegiados_derivan_del_registro():
    """El catalogo privilegiado se deriva del registro (mesa + admin)."""
    from app.services.role_policy import roles_privilegiados

    assert roles_privilegiados() == {
        "mesa_de_ayuda",
        "administrador_directorio",
    }


def test_rp_004_roles_con_lectura_directorio():
    """`can_read_directory`: mesa_de_ayuda y admin si; usuario_final no."""
    from app.services.role_policy import roles_con_lectura_directorio

    assert roles_con_lectura_directorio() == {
        "mesa_de_ayuda",
        "administrador_directorio",
    }


def test_rp_004_roles_que_gestionan_directorio():
    """`manages_directory` es exclusivo de administrador_directorio."""
    from app.services.role_policy import roles_gestion_directorio

    assert roles_gestion_directorio() == {"administrador_directorio"}


def test_rol_destinatario_de_notificacion_es_mesa_de_ayuda():
    """El unico rol destinatario de la notificacion de revision es mesa_de_ayuda."""
    from app.services.role_policy import rol_destinatario_notificacion

    assert rol_destinatario_notificacion() == "mesa_de_ayuda"


# ═══════════════════════════════════════════════════════════════════════════════
# RP-003 — Coherencia verificable del vocabulario
# ═══════════════════════════════════════════════════════════════════════════════


def _check_rol_sqltext() -> str:
    checks = [
        c
        for c in Empleado.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_directorio_empleado_rol"
    ]
    assert checks, "Falta el CHECK ck_directorio_empleado_rol"
    return str(checks[0].sqltext)


def test_rp_003_roles_validos_son_exactamente_tres():
    """`ROLES_VALIDOS` coincide con el vocabulario de tres valores."""
    from app.services.role_policy import ROLES_VALIDOS

    assert set(ROLES_VALIDOS) == {
        "usuario_final",
        "mesa_de_ayuda",
        "administrador_directorio",
    }
    assert "operador" not in ROLES_VALIDOS


def test_rp_003_enum_registro_y_check_coinciden():
    """El enum, el registro y el CHECK de la base declaran los mismos valores."""
    from app.services.role_policy import ROLES_VALIDOS

    valores_enum = {r.value for r in RolEmpleado}
    valores_registro = {r.value for r in _policy().keys()}
    assert valores_enum == set(ROLES_VALIDOS)
    assert valores_registro == set(ROLES_VALIDOS)

    sqltext = _check_rol_sqltext()
    for valor in ROLES_VALIDOS:
        assert f"'{valor}'" in sqltext, f"El CHECK no incluye {valor!r}"
    assert "'operador'" not in sqltext


def test_rp_003_rol_fuera_del_registro_detectado():
    """Un rol fuera de los tres canonicos no tiene politica (divergencia)."""
    from app.services.role_policy import politica_de_rol

    assert politica_de_rol("operador") is None
    assert politica_de_rol("supervisor") is None


@pytest.mark.parametrize(
    "rol, esperado",
    [
        ("usuario_final", "PROPIO"),
        ("mesa_de_ayuda", "GLOBAL"),
        ("administrador_directorio", "GLOBAL"),
    ],
)
def test_politica_de_rol_acepta_enum_y_string(rol, esperado):
    """`politica_de_rol` normaliza enum y string al mismo resultado."""
    from app.services.role_policy import politica_de_rol

    assert politica_de_rol(rol).visibilidad.value == esperado
    assert politica_de_rol(RolEmpleado(rol)).visibilidad.value == esperado
