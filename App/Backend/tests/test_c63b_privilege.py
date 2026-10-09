"""IAH-005: rol privilegiado a nivel de identidad (c-63b, Fase B).

Cubren el flag `User.is_privileged`, su default falso, la materializacion al
crear/actualizar/desvincular un `Empleado` (OQ-B1 = persistir + sincronizar +
derivacion defensiva) y la derivacion defensiva en el chequeo.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Sector
from app.models.empleado import RolEmpleado
from app.models.user import User
from app.services.directorio_service import DirectorioService
from app.services.privilege_service import is_privileged_role, user_is_privileged


async def _make_user(
    session: AsyncSession, username: str, *, is_privileged: bool = False
) -> User:
    user = User(
        username=username,
        hashed_password="not-a-real-hash",
        is_active=True,
        is_privileged=is_privileged,
    )
    session.add(user)
    await session.flush()
    return user


async def _make_sector(session: AsyncSession, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="Infraestructura")
    session.add(sector)
    await session.flush()
    return sector


# ── Requisito: default y catalogo de roles privilegiados ─────────────────────


def test_privileged_role_catalog():
    """Solo operador, administrador_directorio y mesa_de_ayuda son privilegiados."""
    assert is_privileged_role(RolEmpleado.operador) is True
    assert is_privileged_role(RolEmpleado.administrador_directorio) is True
    assert is_privileged_role(RolEmpleado.mesa_de_ayuda) is True
    assert is_privileged_role(RolEmpleado.usuario_final) is False
    assert is_privileged_role("usuario_final") is False
    assert is_privileged_role("operador") is True


async def test_new_user_defaults_to_not_privileged(db_session: AsyncSession):
    """Escenario: cuenta nueva sin vinculo tiene el valor por defecto (falso)."""
    user = await _make_user(db_session, "nuevo_default")

    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is False


# ── Requisito: materializacion del privilegio al vincular ────────────────────


async def test_linking_privileged_role_marks_user_privileged(db_session: AsyncSession):
    """Escenario: cuenta vinculada a empleado privilegiado queda privilegiada."""
    user = await _make_user(db_session, "operador_user")
    sector = await _make_sector(db_session, "Sistemas")

    service = DirectorioService(db_session)
    empleado = await service.crear_empleado(
        legajo="LEG-100",
        nombre="Operador Uno",
        email="operador1@example.com",
        rol=RolEmpleado.operador,
        sector_id=sector.id,
        user_id=user.id,
    )

    assert empleado.user_id == user.id
    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is True


async def test_linking_usuario_final_does_not_mark_privileged(
    db_session: AsyncSession,
):
    """Escenario: cuenta de usuario final no es privilegiada."""
    user = await _make_user(db_session, "final_user")
    sector = await _make_sector(db_session, "Bases de Datos")

    service = DirectorioService(db_session)
    await service.crear_empleado(
        legajo="LEG-101",
        nombre="Final Uno",
        email="final1@example.com",
        rol=RolEmpleado.usuario_final,
        sector_id=sector.id,
        user_id=user.id,
    )

    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is False


# ── Triangulacion: degradacion y desvinculacion ──────────────────────────────


async def test_degrade_role_to_usuario_final_clears_flag(db_session: AsyncSession):
    """Al degradar un rol privilegiado a usuario_final, el flag se apaga."""
    user = await _make_user(db_session, "degrade_user")
    sector = await _make_sector(db_session, "Soporte Tecnico Software")

    service = DirectorioService(db_session)
    empleado = await service.crear_empleado(
        legajo="LEG-102",
        nombre="Degradado",
        email="degradado@example.com",
        rol=RolEmpleado.operador,
        sector_id=sector.id,
        user_id=user.id,
    )
    assert (await db_session.get(User, user.id)).is_privileged is True

    await service.actualizar_empleado(empleado.id, rol=RolEmpleado.usuario_final)

    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is False


async def test_unlink_clears_flag(db_session: AsyncSession):
    """Al desvincular (user_id = NULL) el flag se apaga."""
    user = await _make_user(db_session, "unlink_user")
    sector = await _make_sector(db_session, "Seguridad Informatica")

    service = DirectorioService(db_session)
    empleado = await service.crear_empleado(
        legajo="LEG-103",
        nombre="Desvinculado",
        email="desvinculado@example.com",
        rol=RolEmpleado.administrador_directorio,
        sector_id=None,
        user_id=user.id,
    )
    assert (await db_session.get(User, user.id)).is_privileged is True

    await service.actualizar_empleado(empleado.id, user_id=None)

    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is False


async def test_relink_moves_privilege_between_users(db_session: AsyncSession):
    """Re-vincular traslada el privilegio del usuario anterior al nuevo."""
    old_user = await _make_user(db_session, "relink_old")
    new_user = await _make_user(db_session, "relink_new")
    sector = await _make_sector(db_session, "Sistemas")

    service = DirectorioService(db_session)
    empleado = await service.crear_empleado(
        legajo="LEG-104",
        nombre="Relink",
        email="relink@example.com",
        rol=RolEmpleado.mesa_de_ayuda,
        sector_id=None,
        user_id=old_user.id,
    )
    assert (await db_session.get(User, old_user.id)).is_privileged is True

    await service.actualizar_empleado(empleado.id, user_id=new_user.id)

    assert (await db_session.get(User, old_user.id)).is_privileged is False
    assert (await db_session.get(User, new_user.id)).is_privileged is True


# ── Derivacion defensiva ─────────────────────────────────────────────────────


async def test_defensive_derivation_uses_linked_empleado(db_session: AsyncSession):
    """Si el flag esta apagado pero hay vinculo privilegiado, se deriva true."""
    user = await _make_user(db_session, "defensive_user", is_privileged=False)
    sector = await _make_sector(db_session, "Sistemas")

    # Vinculo creado por fuera del servicio: el flag NO se materializa.
    service = DirectorioService(db_session)
    await service._repo.create(  # noqa: SLF001 — intencional para el caso defensivo
        legajo="LEG-105",
        nombre="Defensivo",
        email="defensivo@example.com",
        telefono=None,
        sector_id=sector.id,
        rol=RolEmpleado.operador,
        user_id=user.id,
        activo=True,
    )
    stored = await db_session.get(User, user.id)
    assert stored.is_privileged is False

    assert await user_is_privileged(db_session, stored) is True


async def test_defensive_derivation_false_without_link(db_session: AsyncSession):
    """Sin vinculo ni flag, la derivacion es falsa."""
    user = await _make_user(db_session, "lonely_user", is_privileged=False)
    assert await user_is_privileged(db_session, user) is False


async def test_flag_true_short_circuits_derivation(db_session: AsyncSession):
    """Con el flag encendido la derivacion es verdadera aunque no haya vinculo."""
    user = await _make_user(db_session, "flagged_user", is_privileged=True)
    assert await user_is_privileged(db_session, user) is True


async def test_persisted_flag_is_readable_via_query(db_session: AsyncSession):
    """Triangulacion: el flag persistido sobrevive a una lectura nueva."""
    user = await _make_user(db_session, "query_user", is_privileged=True)
    await db_session.flush()

    result = await db_session.execute(
        select(User.is_privileged).where(User.id == user.id)
    )
    assert result.scalar_one() is True
