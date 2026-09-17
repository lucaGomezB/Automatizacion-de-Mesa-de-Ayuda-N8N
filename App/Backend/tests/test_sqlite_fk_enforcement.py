"""Verificacion del enforcement de claves foraneas en el engine SQLite (C-29 §4).

Contexto: el engine SQLite de tests tenia `PRAGMA foreign_keys` en OFF (default
de SQLite), por lo que las violaciones de integridad referencial quedaban
ocultas. `conftest.py` ahora registra un listener sobre el evento `connect` que
ejecuta `PRAGMA foreign_keys=ON` en cada conexion nueva. Estos tests verifican
que el enforcement esta activo tanto en el engine compartido como en la conexion
que abre el cliente ASGI por request.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.incidente import Incidente, PrioridadEnum


async def test_sqlite_engine_enforces_foreign_keys(engine):
    """`PRAGMA foreign_keys` devuelve 1 sobre una conexion del engine compartido."""
    async with engine.connect() as conn:
        value = (await conn.execute(text("PRAGMA foreign_keys"))).scalar()
    assert value == 1, (
        "El engine SQLite de tests debe tener PRAGMA foreign_keys=ON; "
        f"se obtuvo {value!r}"
    )


async def test_sqlite_fk_violation_is_rejected(db_session):
    """Insertar un incidente con FK inexistente falla por integridad referencial.

    Con PRAGMA foreign_keys=OFF (comportamiento previo) el INSERT se persistia y
    la violacion quedaba oculta. Con el enforcement activo debe lanzar
    IntegrityError.
    """
    incidente = Incidente(
        descripcion_original="FK violation",
        descripcion_pseudonimizada="FK violation",
        prioridad=PrioridadEnum.media,
        estado_id=99999,
        sector_id=99999,
    )
    db_session.add(incidente)

    with pytest.raises(IntegrityError):
        await db_session.flush()
