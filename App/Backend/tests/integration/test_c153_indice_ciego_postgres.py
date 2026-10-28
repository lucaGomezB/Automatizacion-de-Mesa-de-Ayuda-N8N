"""
Tests de integracion PostgreSQL del indice ciego del directorio (c-153, Tema B).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican, contra el motor real, que:
    - `email_bidx` es UNICO (unicidad del email sobre el indice determinista).
    - `telefono_bidx` es repetible (sin unique).
    - El indice persistido es el HMAC-SHA-256 del contacto normalizado, no el
      contacto en claro.
    - La busqueda del repositorio resuelve por el indice ciego.
"""

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.utils.blind_index import email_blind_index, telefono_blind_index

pytestmark = pytest.mark.integration

_TABLE = "directorio_empleado"


async def _crear_empleado(session, **kwargs) -> Empleado:
    valores = {
        "legajo": "PG-BIDX-1",
        "nombre": "Empleado PG Indice",
        "email": "pg.bidx@example.test",
        "telefono": "+5491100008101",
        "rol": RolEmpleado.usuario_final,
        **kwargs,
    }
    empleado = Empleado(**valores)
    session.add(empleado)
    await session.flush()
    return empleado


async def _indices_crudos(
    session, legajo: str
) -> tuple[str | None, str | None]:
    row = (
        await session.execute(
            text(
                f"SELECT email_bidx, telefono_bidx FROM {_TABLE} WHERE legajo = :l"
            ),
            {"l": legajo},
        )
    ).one()
    return row[0], row[1]


@pytest.mark.asyncio
async def test_indice_derivado_en_postgres(pg_session, seed_pg_catalogs):
    """El indice persistido es el HMAC del contacto normalizado, no el claro."""
    email = "pg.derivado@example.test"
    telefono = "+5491100008102"
    await _crear_empleado(
        pg_session, legajo="PG-BIDX-2", email=email, telefono=telefono
    )

    email_bidx, telefono_bidx = await _indices_crudos(pg_session, "PG-BIDX-2")

    assert email_bidx == email_blind_index(email)
    assert telefono_bidx == telefono_blind_index(telefono)
    assert email_bidx != email and len(email_bidx) == 64
    assert telefono_bidx != telefono and len(telefono_bidx) == 64


@pytest.mark.asyncio
async def test_email_bidx_unico_en_postgres(pg_session, seed_pg_catalogs):
    """Dos empleados con el mismo email violan la unicidad de `email_bidx`."""
    await _crear_empleado(
        pg_session, legajo="PG-BIDX-3", email="pg.unico@example.test"
    )

    with pytest.raises(IntegrityError):
        await _crear_empleado(
            pg_session, legajo="PG-BIDX-4", email="pg.unico@example.test"
        )
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_telefono_bidx_repetible_en_postgres(pg_session, seed_pg_catalogs):
    """Dos empleados comparten telefono: `telefono_bidx` sin unique lo permite."""
    telefono = "+5491100008105"
    await _crear_empleado(
        pg_session, legajo="PG-BIDX-5", email="pg.cinco@example.test", telefono=telefono
    )
    await _crear_empleado(
        pg_session,
        legajo="PG-BIDX-6",
        email="pg.seis@example.test",
        telefono=telefono,
    )

    coincidencias = (
        await pg_session.execute(
            select(Empleado).where(Empleado.telefono_bidx == telefono_blind_index(telefono))
        )
    ).scalars().all()

    assert {e.legajo for e in coincidencias} >= {"PG-BIDX-5", "PG-BIDX-6"}


@pytest.mark.asyncio
async def test_busqueda_por_indice_en_postgres(pg_session, seed_pg_catalogs):
    """El repositorio resuelve por email y telefono via el indice ciego."""
    repo = EmpleadoRepository(pg_session)
    await _crear_empleado(
        pg_session,
        legajo="PG-BIDX-7",
        email="pg.siete@example.test",
        telefono="+5491100008107",
    )

    por_email = await repo.listar_por_email("pg.siete@example.test")
    por_telefono = await repo.listar_por_telefono("+5491100008107")
    sin_resultado = await repo.listar_por_telefono("+5491100099999")

    assert [e.legajo for e in por_email] == ["PG-BIDX-7"]
    assert [e.legajo for e in por_telefono] == ["PG-BIDX-7"]
    assert sin_resultado == []