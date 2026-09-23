"""
Tests del repositorio del directorio de empleados (c-54, seccion 3).

Cubren:
    - Busqueda por email y por telefono (en texto plano, igualdad exacta).
    - Busqueda por `user_id` (vinculo con la cuenta de autenticacion).
    - Exclusividad de empleados activos en las busquedas de contacto.
    - Multiples coincidencias por telefono (ambiguedad, telefono repetible).
    - Carga eager de `sector` (selectinload) para serializacion async.
"""

import pytest
from sqlalchemy import inspect as sa_inspect

from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User
from app.repositories.empleado_repository import EmpleadoRepository


async def _crear_sector(session, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


async def _crear_empleado(
    session,
    *,
    legajo: str,
    email: str,
    telefono: str | None = None,
    sector_id: int | None = None,
    rol: RolEmpleado = RolEmpleado.usuario_final,
    activo: bool = True,
    user_id: int | None = None,
) -> Empleado:
    empleado = Empleado(
        legajo=legajo,
        nombre=f"Empleado {legajo}",
        email=email,
        telefono=telefono,
        sector_id=sector_id,
        rol=rol,
        activo=activo,
        user_id=user_id,
    )
    session.add(empleado)
    await session.flush()
    return empleado


@pytest.mark.asyncio
async def test_busqueda_por_email_activo(db_session):
    """Un email coincide con exactamente el empleado activo y carga su sector."""
    repo = EmpleadoRepository(db_session)
    sector = await _crear_sector(db_session)
    await _crear_empleado(
        db_session,
        legajo="E-1",
        email="uno@example.test",
        sector_id=sector.id,
    )

    encontrados = await repo.listar_por_email("uno@example.test")

    assert len(encontrados) == 1
    assert encontrados[0].legajo == "E-1"
    # El sector quedo eager-loaded (no lazy-load en async).
    assert "sector" not in sa_inspect(encontrados[0]).unloaded
    assert encontrados[0].sector is not None


@pytest.mark.asyncio
async def test_busqueda_por_telefono_y_user_id(db_session):
    """El telefono y el user_id resuelven al empleado activo."""
    repo = EmpleadoRepository(db_session)
    user = User(username="u1", hashed_password="x", is_active=True)
    db_session.add(user)
    await db_session.flush()
    await _crear_empleado(
        db_session,
        legajo="E-2",
        email="dos@example.test",
        telefono="+5491100000002",
        user_id=user.id,
    )

    por_tel = await repo.listar_por_telefono("+5491100000002")
    por_user = await repo.get_by_user_id(user.id)

    assert [e.legajo for e in por_tel] == ["E-2"]
    assert por_user is not None and por_user.legajo == "E-2"


@pytest.mark.asyncio
async def test_empleado_inactivo_excluido(db_session):
    """Los empleados inactivos no aparecen en las busquedas de contacto."""
    repo = EmpleadoRepository(db_session)
    await _crear_empleado(
        db_session,
        legajo="E-3",
        email="tres@example.test",
        telefono="+5491100000003",
        activo=False,
    )

    assert await repo.listar_por_email("tres@example.test") == []
    assert await repo.listar_por_telefono("+5491100000003") == []
    # get_by_legajo (gestion) si lo encuentra, para poder reactivarlo.
    assert (await repo.get_by_legajo("E-3")) is not None


@pytest.mark.asyncio
async def test_multiples_coincidencias_por_telefono(db_session):
    """Un telefono repetido devuelve multiples empleados activos (ambiguedad)."""
    repo = EmpleadoRepository(db_session)
    await _crear_empleado(
        db_session, legajo="E-4", email="cuatro@example.test",
        telefono="+5491100000004",
    )
    await _crear_empleado(
        db_session, legajo="E-5", email="cinco@example.test",
        telefono="+5491100000004",
    )

    encontrados = await repo.listar_por_telefono("+5491100000004")

    assert {e.legajo for e in encontrados} == {"E-4", "E-5"}


@pytest.mark.asyncio
async def test_sector_nulo_serializa_sin_lazy_load(db_session):
    """Un empleado sin sector (administrador) se lista sin lazy-load."""
    repo = EmpleadoRepository(db_session)
    admin = await _crear_empleado(
        db_session,
        legajo="ADM-1",
        email="admin@example.test",
        rol=RolEmpleado.administrador_directorio,
    )

    listado = await repo.listar()
    fila = next(e for e in listado if e.legajo == "ADM-1")

    assert admin.sector_id is None
    assert "sector" not in sa_inspect(fila).unloaded
    assert fila.sector is None
