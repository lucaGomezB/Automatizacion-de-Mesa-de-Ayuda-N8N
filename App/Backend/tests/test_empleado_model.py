"""
Tests del modelo ORM del directorio de empleados (c-54, seccion 3).

Verifican que la tabla `directorio_empleado` tiene EXACTAMENTE los campos
minimizados (DIR-002/D6b), los tipos/restricciones esperados, que el contacto
se guarda en TEXTO PLANO (DIR-005) y que el vocabulario de roles es el minimo
de tres valores (DIR-003).
"""

import pytest

from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User

_COLUMNAS_ESPERADAS = {
    "id",
    "legajo",
    "nombre",
    "email",
    "telefono",
    "sector_id",
    "rol",
    "activo",
    "user_id",
    "fecha_baja",
    "created_at",
    "updated_at",
}


def test_nombre_de_tabla():
    """El ORM mapea la tabla `directorio_empleado` (separada de `users`)."""
    assert Empleado.__tablename__ == "directorio_empleado"


def test_columnas_exactas_sin_datos_extra():
    """El esquema tiene exactamente las columnas minimizadas, ni una mas."""
    assert set(Empleado.__table__.columns.keys()) == _COLUMNAS_ESPERADAS


def test_sin_columnas_cifradas_ni_hash_ciego():
    """No existe columna de cifrado ni de hash ciego (DIR-005)."""
    for nombre in Empleado.__table__.columns.keys():
        assert "hash" not in nombre.lower()
        assert "cifrado" not in nombre.lower()
        assert "blind" not in nombre.lower()


def test_restricciones_de_legajo_y_email():
    """legajo es NOT NULL y UNIQUE; email es NOT NULL, UNIQUE e indexado."""
    tabla = Empleado.__table__
    assert tabla.c.legajo.nullable is False
    assert tabla.c.legajo.unique is True
    assert tabla.c.email.nullable is False
    assert tabla.c.email.unique is True
    assert tabla.c.email.index is True


def test_telefono_opcional_indexado_y_repetible():
    """telefono es NULL, indexado y NO unico (puede repetirse)."""
    col = Empleado.__table__.c.telefono
    assert col.nullable is True
    assert col.unique is not True
    assert col.index is True


def test_foreign_keys():
    """sector_id referencia sector; user_id referencia users con ON DELETE SET NULL."""
    tabla = Empleado.__table__

    fk_sector = list(tabla.c.sector_id.foreign_keys)[0]
    assert fk_sector.column.table.name == "sector"
    assert tabla.c.sector_id.nullable is True

    fk_user = list(tabla.c.user_id.foreign_keys)[0]
    assert fk_user.column.table.name == "users"
    assert fk_user.ondelete == "SET NULL"
    assert tabla.c.user_id.nullable is True


def test_activo_por_defecto_verdadero():
    """El indicador `activo` existe y no es obligatorio explicito (default True)."""
    col = Empleado.__table__.c.activo
    assert col.nullable is False
    assert col.server_default is not None or col.default is not None


def test_fecha_baja_nullable_para_retencion():
    """`fecha_baja` existe, es nullable y almacena un timestamp (DIR-007)."""
    col = Empleado.__table__.c.fecha_baja
    assert col.nullable is True
    assert col.type.timezone is True


def test_vocabulario_de_roles_minimo():
    """El rol admite exactamente usuario_final, operador y administrador_directorio."""
    assert {r.value for r in RolEmpleado} == {
        "usuario_final",
        "operador",
        "administrador_directorio",
    }


@pytest.mark.asyncio
async def test_persistencia_texto_plano_y_vinculo_opcional(db_session):
    """Una fila se persiste con contacto legible y sin user_id (DIR-001/DIR-005)."""
    sector = Sector(nombre="Sistemas", descripcion="Infraestructura")
    db_session.add(sector)
    await db_session.flush()

    empleado = Empleado(
        legajo="A-001",
        nombre="Empleado Sintetico",
        email="empleado.sintetico@example.test",
        telefono="+5491100000001",
        sector_id=sector.id,
        rol=RolEmpleado.usuario_final,
    )
    db_session.add(empleado)
    await db_session.flush()

    # El contacto se lee en claro (texto plano) y sin cifrado de aplicacion.
    assert empleado.email == "empleado.sintetico@example.test"
    assert empleado.telefono == "+5491100000001"
    assert empleado.user_id is None
    assert empleado.activo is True

    # Vinculo opcional con una cuenta de autenticacion.
    user = User(username="u-directorio", hashed_password="x", is_active=True)
    db_session.add(user)
    await db_session.flush()
    empleado.user_id = user.id
    await db_session.flush()

    # Recargar la fila desde la base para confirmar el valor persistido en claro.
    await db_session.refresh(empleado)
    assert empleado.email == "empleado.sintetico@example.test"
    assert empleado.user_id == user.id
