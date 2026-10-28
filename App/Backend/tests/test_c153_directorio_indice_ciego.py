"""
Tests del indice ciego determinista del directorio (c-153, Tema B).

Cubren DIR-011 (delta): el email y el telefono se buscan por un indice ciego
determinista (`email_bidx`, `telefono_bidx`) derivado con HMAC-SHA-256 y una
clave dedicada (`directory_blind_index_key`). Como Fernet no es determinista, la
igualdad SQL sobre el ciphertext no sirve: el repositorio resuelve por el indice.

Estrategia:
    - La derivacion pura se prueba de forma aislada (determinismo, dependencia de
      clave y ausencia de colisiones).
    - La persistencia y la busqueda se prueban contra la base SQLite de la suite
      offline (`db_session`).
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.utils.blind_index import (
    derivar_indice_ciego,
    email_blind_index,
    indice_ciego_email,
    indice_ciego_telefono,
    telefono_blind_index,
)

_TABLE = "directorio_empleado"

_CLAVE_A = "clave-de-indice-ciego-a"
_CLAVE_B = "clave-de-indice-ciego-b"


async def _crear_empleado(
    session,
    *,
    legajo: str,
    email: str,
    telefono: str | None = None,
) -> Empleado:
    empleado = Empleado(
        legajo=legajo,
        nombre=f"Sintetico {legajo}",
        email=email,
        telefono=telefono,
        rol=RolEmpleado.usuario_final,
        activo=True,
    )
    session.add(empleado)
    await session.flush()
    return empleado


async def _indices_crudos(session, empleado_id: int) -> tuple[str | None, str | None]:
    """Lee email_bidx/telefono_bidx SIN pasar por el ORM."""
    row = (
        await session.execute(
            text(
                f"SELECT email_bidx, telefono_bidx FROM {_TABLE} WHERE id = :id"
            ),
            {"id": empleado_id},
        )
    ).one()
    return row[0], row[1]


# ── 3.1 RED: esquema/columnas ────────────────────────────────────────────────


def test_modelo_expone_columnas_de_indice_ciego():
    """El modelo declara email_bidx (unico) y telefono_bidx (nullable, no unico)."""
    columnas = set(Empleado.__table__.columns.keys())

    assert {"email_bidx", "telefono_bidx"} <= columnas

    email_bidx = Empleado.__table__.c.email_bidx
    assert email_bidx.unique is True
    assert email_bidx.index is True

    telefono_bidx = Empleado.__table__.c.telefono_bidx
    assert telefono_bidx.unique is not True
    assert telefono_bidx.index is True


# ── 3.4 TRIANGULATE: determinismo, dependencia de clave, colisiones ──────────


def test_derivacion_determinista():
    """Mismo valor y misma clave -> mismo digest (siempre)."""
    valor = "persona@example.test"

    primero = derivar_indice_ciego(valor, _CLAVE_A)
    segundo = derivar_indice_ciego(valor, _CLAVE_A)

    assert primero == segundo
    # SHA-256 en hexadecimal: 64 caracteres.
    assert len(primero) == 64
    assert primero == primero.lower()


def test_derivacion_depende_de_la_clave():
    """Clave distinta -> digest distinto para el mismo valor."""
    valor = "persona@example.test"

    con_a = derivar_indice_ciego(valor, _CLAVE_A)
    con_b = derivar_indice_ciego(valor, _CLAVE_B)

    assert con_a != con_b


def test_sin_colisiones_en_el_conjunto_de_prueba():
    """Valores distintos producen digests distintos (sin colisiones)."""
    valores = [f"persona{i}@example.test" for i in range(50)]

    digests = {derivar_indice_ciego(valor, _CLAVE_A) for valor in valores}

    assert len(digests) == len(valores)


def test_indice_email_normaliza_mayusculas_y_espacios():
    """La forma normalizada hace que variantes del mismo email colisionen."""
    canonical = indice_ciego_email("persona@example.test", _CLAVE_A)
    variante = indice_ciego_email("  Persona@Example.Test ", _CLAVE_A)

    assert canonical == variante


def test_indice_telefono_normaliza_separadores():
    """El telefono se normaliza a E.164 antes de derivar el indice."""
    canonical = indice_ciego_telefono("+5491100000002", _CLAVE_A)
    variante = indice_ciego_telefono("+54 9 11 0000-0002", _CLAVE_A)

    assert canonical == variante


# ── 3.2 GREEN: derivacion al persistir y busqueda por indice ─────────────────


@pytest.mark.asyncio
async def test_persistencia_deriva_los_indices_ciegos(db_session):
    """Al persistir, la fila guarda el HMAC del contacto normalizado."""
    email = "derivado@example.test"
    telefono = "+5491100011001"

    empleado = await _crear_empleado(
        db_session, legajo="BIDX-1", email=email, telefono=telefono
    )

    raw_email_bidx, raw_tel_bidx = await _indices_crudos(db_session, empleado.id)

    assert raw_email_bidx == email_blind_index(email)
    assert raw_tel_bidx == telefono_blind_index(telefono)
    # El indice NO revela el valor en claro.
    assert raw_email_bidx != email
    assert raw_tel_bidx != telefono
    assert len(raw_email_bidx) == 64
    assert raw_tel_bidx is not None and len(raw_tel_bidx) == 64


@pytest.mark.asyncio
async def test_empleado_sin_telefono_no_deriva_indice(db_session):
    """Sin telefono, `telefono_bidx` queda nulo; `email_bidx` se deriva igual."""
    empleado = await _crear_empleado(
        db_session, legajo="BIDX-2", email="sin.tel@example.test"
    )

    raw_email_bidx, raw_tel_bidx = await _indices_crudos(db_session, empleado.id)

    assert raw_tel_bidx is None
    assert raw_email_bidx == email_blind_index("sin.tel@example.test")


@pytest.mark.asyncio
async def test_busqueda_por_email_usa_el_indice(db_session):
    """La busqueda resuelve por email aunque el valor difiera en caja/espacios."""
    repo = EmpleadoRepository(db_session)
    await _crear_empleado(
        db_session, legajo="BIDX-3", email="Mayusculas@Example.Test"
    )

    encontrados = await repo.listar_por_email("  mayusculas@example.test ")

    assert [e.legajo for e in encontrados] == ["BIDX-3"]


@pytest.mark.asyncio
async def test_busqueda_por_telefono_devuelve_coincidencias(db_session):
    """El telefono repetible devuelve todas las filas activas con ese indice."""
    repo = EmpleadoRepository(db_session)
    await _crear_empleado(
        db_session,
        legajo="BIDX-4",
        email="cuatro@example.test",
        telefono="+5491100011004",
    )
    await _crear_empleado(
        db_session,
        legajo="BIDX-5",
        email="cinco@example.test",
        telefono="+5491100011004",
    )

    encontrados = await repo.listar_por_telefono("+5491100011004")
    ausentes = await repo.listar_por_telefono("+5491100099999")

    assert {e.legajo for e in encontrados} == {"BIDX-4", "BIDX-5"}
    assert ausentes == []


# ── 3.3 Unicidad del email sobre el indice determinista ──────────────────────


@pytest.mark.asyncio
async def test_email_duplicado_rechazado_por_el_indice(db_session):
    """Dos empleados con el mismo email violan la unicidad de `email_bidx`."""
    await _crear_empleado(db_session, legajo="BIDX-6", email="duplicado@example.test")

    with pytest.raises(IntegrityError):
        await _crear_empleado(
            db_session, legajo="BIDX-7", email="duplicado@example.test"
        )

    await db_session.rollback()


@pytest.mark.asyncio
async def test_telefono_repetido_permitido_por_el_indice(db_session):
    """Dos empleados con el mismo telefono se persisten (`telefono_bidx` no unico)."""
    primero = await _crear_empleado(
        db_session,
        legajo="BIDX-8",
        email="ocho@example.test",
        telefono="+5491100011008",
    )
    segundo = await _crear_empleado(
        db_session,
        legajo="BIDX-9",
        email="nueve@example.test",
        telefono="+5491100011008",
    )

    assert primero.id != segundo.id
    assert telefono_blind_index("+5491100011008") is not None