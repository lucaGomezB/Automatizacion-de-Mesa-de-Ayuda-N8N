"""Tests del permiso de borrado logico en el registro de politica de rol (c-87, RP-005).

Cubren que `can_delete_incident` es verdadero SOLO para `administrador_directorio`,
que todos los roles lo declaran explicitamente como booleano y que la derivacion
`roles_con_borrado_incidentes()` coincide con el registro (fuente unica).
"""

from app.models.empleado import RolEmpleado


def test_can_delete_incident_solo_administrador_directorio():
    """Solo `administrador_directorio` puede borrar logicamente incidentes."""
    from app.services.role_policy import ROLE_POLICY

    assert ROLE_POLICY[RolEmpleado.administrador_directorio].can_delete_incident is True
    assert ROLE_POLICY[RolEmpleado.usuario_final].can_delete_incident is False
    assert ROLE_POLICY[RolEmpleado.mesa_de_ayuda].can_delete_incident is False
    assert ROLE_POLICY[RolEmpleado.gestion_incidentes].can_delete_incident is False


def test_todos_los_roles_declaran_can_delete_incident_booleano():
    """Cada entrada del registro declara `can_delete_incident` como booleano."""
    from app.services.role_policy import ROLE_POLICY

    for rol, politica in ROLE_POLICY.items():
        assert isinstance(politica.can_delete_incident, bool), rol


def test_roles_con_borrado_incidentes_deriva_del_registro():
    """La derivacion coincide con el registro (unico origen de la decision)."""
    from app.services.role_policy import roles_con_borrado_incidentes

    assert roles_con_borrado_incidentes() == {"administrador_directorio"}


def test_politica_de_rol_expone_can_delete_incident():
    """`politica_de_rol` normaliza enum y string al mismo permiso."""
    from app.services.role_policy import politica_de_rol

    assert politica_de_rol("administrador_directorio").can_delete_incident is True
    assert politica_de_rol(RolEmpleado.mesa_de_ayuda).can_delete_incident is False
