"""
Tests del seed dev-only del directorio (c-54, seccion 6.6).

Verifican que el seed es IDEMPOTENTE, crea AMBAS filas (`users` login +
`directorio_empleado` enlazadas por `user_id`) para un usuario sintetico por rol
y deja un administrador operativo, sin PII real.
"""

import pytest
from sqlalchemy import select

from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User
from scripts.seed_directorio import PERSONAS_SINTETICAS, seed_directorio


async def _seed_sector(session) -> Sector:
    sector = Sector(nombre="Sistemas", descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


@pytest.mark.asyncio
async def test_seed_idempotente_crea_un_usuario_por_rol(db_session):
    """Ejecutar el seed dos veces no duplica filas ni cuentas."""
    await _seed_sector(db_session)

    await seed_directorio(db_session)
    await seed_directorio(db_session)

    legajos = {p["legajo"] for p in PERSONAS_SINTETICAS}
    empleados = (
        await db_session.execute(
            select(Empleado).where(Empleado.legajo.in_(legajos))
        )
    ).scalars().all()

    assert len(empleados) == len(PERSONAS_SINTETICAS)
    assert {e.rol for e in empleados} == {
        RolEmpleado.usuario_final,
        RolEmpleado.operador,
        RolEmpleado.administrador_directorio,
    }


@pytest.mark.asyncio
async def test_seed_enlaza_users_y_empleado_y_deja_admin_operativo(db_session):
    """Cada empleado sintetico tiene una cuenta vinculada; el admin es operable."""
    await _seed_sector(db_session)

    await seed_directorio(db_session)

    admin = (
        await db_session.execute(
            select(Empleado).where(
                Empleado.rol == RolEmpleado.administrador_directorio
            )
        )
    ).scalar_one()

    assert admin.sector_id is None, "El administrador no debe tener sector"
    assert admin.activo is True
    assert admin.user_id is not None

    user = await db_session.get(User, admin.user_id)
    assert user is not None
    assert user.is_active is True
    assert user.username == admin_user_username()


def admin_user_username() -> str:
    return next(
        p["username"]
        for p in PERSONAS_SINTETICAS
        if p["rol"] == "administrador_directorio"
    )


@pytest.mark.asyncio
async def test_seed_usa_datos_sinteticos(db_session):
    """El contacto sembrado es claramente sintetico (dominio .test)."""
    await _seed_sector(db_session)
    await seed_directorio(db_session)

    emails = (
        await db_session.execute(select(Empleado.email))
    ).scalars().all()
    for email in emails:
        assert email.endswith(".test") or email.endswith("@example.test")
