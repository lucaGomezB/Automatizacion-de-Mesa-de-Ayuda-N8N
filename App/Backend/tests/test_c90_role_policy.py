"""Tests del permiso de asignacion de prioridad critica (c-90, RP-006).

Cubren que `puede_asignar_prioridad_critica` es verdadero para `mesa_de_ayuda` y
`administrador_directorio`, falso para `usuario_final` y `gestion_incidentes`, que
cada entrada del registro lo declara como booleano, que la derivacion
`roles_con_asignacion_prioridad_critica()` coincide con el registro (fuente unica)
y que el helper `puede_asignar_prioridad_critica` deniega por defecto ante un rol
desconocido o nulo.
"""

from app.models.empleado import RolEmpleado


def test_puede_asignar_prioridad_critica_por_rol():
    """Solo `mesa_de_ayuda` y `administrador_directorio` pueden asignar `critica`."""
    from app.services.role_policy import ROLE_POLICY

    assert ROLE_POLICY[RolEmpleado.mesa_de_ayuda].puede_asignar_prioridad_critica is True
    assert (
        ROLE_POLICY[RolEmpleado.administrador_directorio].puede_asignar_prioridad_critica
        is True
    )
    assert ROLE_POLICY[RolEmpleado.usuario_final].puede_asignar_prioridad_critica is False
    assert (
        ROLE_POLICY[RolEmpleado.gestion_incidentes].puede_asignar_prioridad_critica
        is False
    )


def test_todos_los_roles_declaran_el_atributo_booleano():
    """Cada entrada del registro declara `puede_asignar_prioridad_critica` como booleano."""
    from app.services.role_policy import ROLE_POLICY

    for rol, politica in ROLE_POLICY.items():
        assert isinstance(politica.puede_asignar_prioridad_critica, bool), rol


def test_roles_con_asignacion_prioridad_critica_deriva_del_registro():
    """La derivacion coincide con el registro (unico origen de la decision)."""
    from app.services.role_policy import roles_con_asignacion_prioridad_critica

    assert roles_con_asignacion_prioridad_critica() == {
        "mesa_de_ayuda",
        "administrador_directorio",
    }


def test_politica_de_rol_expone_el_permiso():
    """`politica_de_rol` normaliza enum y string al mismo permiso."""
    from app.services.role_policy import politica_de_rol

    assert politica_de_rol("mesa_de_ayuda").puede_asignar_prioridad_critica is True
    assert politica_de_rol(RolEmpleado.usuario_final).puede_asignar_prioridad_critica is False
    assert (
        politica_de_rol("administrador_directorio").puede_asignar_prioridad_critica is True
    )


# ── TRIANGULATE: denegacion por defecto ante rol desconocido o nulo ────────────


def test_helper_deniega_ante_rol_desconocido_o_nulo():
    """El helper deniega por defecto cualquier rol fuera del registro o nulo."""
    from app.services.role_policy import puede_asignar_prioridad_critica

    assert puede_asignar_prioridad_critica("mesa_de_ayuda") is True
    assert puede_asignar_prioridad_critica(RolEmpleado.administrador_directorio) is True
    assert puede_asignar_prioridad_critica("usuario_final") is False
    assert puede_asignar_prioridad_critica("gestion_incidentes") is False
    assert puede_asignar_prioridad_critica("operador") is False
    assert puede_asignar_prioridad_critica(None) is False


def test_roles_con_asignacion_no_incluye_roles_desconocidos():
    """La derivacion no habilita roles fuera del vocabulario canonico."""
    from app.services.role_policy import roles_con_asignacion_prioridad_critica

    habilitados = roles_con_asignacion_prioridad_critica()
    assert "usuario_final" not in habilitados
    assert "gestion_incidentes" not in habilitados
    assert "operador" not in habilitados
