"""
Tests de integracion PostgreSQL del contacto cifrado del directorio (c-153, Tema A).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican, contra el motor real, que el
email y el telefono del directorio NO quedan en claro: el valor persistido es un
token Fernet (`EncryptedText`), y el ORM lo descifra de forma transparente.
"""

import pytest
from sqlalchemy import select, text

from app.models.empleado import Empleado, RolEmpleado

pytestmark = pytest.mark.integration

_TABLE = "directorio_empleado"


async def _crear_empleado(session, **kwargs) -> Empleado:
    valores = {
        "legajo": "PG-C153-1",
        "nombre": "Empleado PG Cifrado",
        "email": "pg.cifrado@example.test",
        "telefono": "+5491100009109",
        "rol": RolEmpleado.usuario_final,
        **kwargs,
    }
    empleado = Empleado(**valores)
    session.add(empleado)
    await session.flush()
    return empleado


async def _fila_cruda(session, legajo: str) -> tuple[str | None, str | None]:
    row = (
        await session.execute(
            text(f"SELECT email, telefono FROM {_TABLE} WHERE legajo = :l"),
            {"l": legajo},
        )
    ).one()
    return row[0], row[1]


@pytest.mark.asyncio
async def test_contacto_cifrado_en_postgres(pg_session, seed_pg_catalogs):
    """(2.4) El contacto se persiste cifrado en PostgreSQL, no en claro."""
    email = "pg.cifrado@example.test"
    telefono = "+5491100009109"
    await _crear_empleado(pg_session, email=email, telefono=telefono)

    raw_email, raw_tel = await _fila_cruda(pg_session, "PG-C153-1")

    assert raw_email != email and raw_email.startswith("gAAAA"), raw_email
    assert raw_tel != telefono and raw_tel.startswith("gAAAA"), raw_tel


@pytest.mark.asyncio
async def test_no_queda_contacto_en_claro(pg_session, seed_pg_catalogs):
    """(2.4) Ningun valor almacenado contiene el contacto en claro."""
    email = "pg.otro@example.test"
    telefono = "+5491100009210"
    await _crear_empleado(
        pg_session, legajo="PG-C153-2", email=email, telefono=telefono
    )

    filas = (
        await pg_session.execute(
            text(f"SELECT email, telefono FROM {_TABLE} WHERE legajo = :l"),
            {"l": "PG-C153-2"},
        )
    ).all()
    for raw_email, raw_tel in filas:
        assert email not in (raw_email or "")
        assert telefono not in (raw_tel or "")
        assert ".test" not in (raw_email or "")

    # El ORM sigue devolviendo el valor en claro (descifrado transparente).
    empleado = (
        await pg_session.execute(
            select(Empleado).where(Empleado.legajo == "PG-C153-2")
        )
    ).scalar_one()
    assert empleado.email == email
    assert empleado.telefono == telefono
