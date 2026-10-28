"""
Tests de cifrado at-rest del contacto del directorio (c-153, Tema A).

Cubren DIR-011 (delta): el email y el telefono de `directorio_empleado` se
almacenan CIFRADOS at-rest con `EncryptedText` (Fernet). El valor en la fila
cruda de la base es ciphertext, NO texto plano; el ORM sigue devolviendo el
valor en claro (descifrado transparente).

Estrategia: se escribe la fila con el ORM y se la relee con SQL textual (que NO
pasa por el TypeDecorator) para inspeccionar el valor realmente persistido.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select, text

from app.models.empleado import Empleado, RolEmpleado

_TABLE = "directorio_empleado"


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


async def _fila_cruda(session, empleado_id: int) -> tuple[str | None, str | None]:
    """Lee email/telefono SIN pasar por el TypeDecorator (SQL textual)."""
    row = (
        await session.execute(
            text(f"SELECT email, telefono FROM {_TABLE} WHERE id = :id"),
            {"id": empleado_id},
        )
    ).one()
    return row[0], row[1]


@pytest.mark.asyncio
async def test_email_y_telefono_se_almacenan_cifrados(db_session):
    """RED (2.2): la fila cruda guarda ciphertext, no el contacto en claro."""
    email = "cifrado.uno@example.test"
    telefono = "+5491100001001"
    empleado = await _crear_empleado(
        db_session, legajo="C153-1", email=email, telefono=telefono
    )

    raw_email, raw_tel = await _fila_cruda(db_session, empleado.id)

    # El valor persistido NO es el texto plano.
    assert raw_email != email, "El email se lee en claro en la fila del directorio"
    assert raw_tel != telefono, "El telefono se lee en claro en la fila del directorio"
    # Marcador del token Fernet (base64 urlsafe, version 0x80 -> "gAAAA").
    assert raw_email.startswith("gAAAA"), raw_email
    assert raw_tel.startswith("gAAAA"), raw_tel
    # El ORM sigue descifrando de forma transparente.
    assert empleado.email == email
    assert empleado.telefono == telefono


@pytest.mark.asyncio
async def test_empleado_sin_telefono(db_session):
    """TRIANGULATE (2.6): sin telefono, el email se cifra y el telefono es None."""
    empleado = await _crear_empleado(
        db_session, legajo="C153-2", email="sin.telefono@example.test"
    )

    raw_email, raw_tel = await _fila_cruda(db_session, empleado.id)

    assert raw_tel is None
    assert raw_email.startswith("gAAAA")
    assert empleado.telefono is None


@pytest.mark.asyncio
async def test_ciphertext_por_fila_es_distinto(db_session):
    """TRIANGULATE (2.6): el mismo telefono en filas distintas da ciphertext distinto.

    Propiedad de Fernet: el IV es aleatorio por operacion, de modo que el
    ciphertext NO es determinista. Dos telefono iguales (repetible) no producen
    el mismo valor cifrado.
    """
    telefono = "+5491100003003"
    primero = await _crear_empleado(
        db_session, legajo="C153-3", email="fila.tres@example.test", telefono=telefono
    )
    segundo = await _crear_empleado(
        db_session, legajo="C153-4", email="fila.cuatro@example.test", telefono=telefono
    )

    raw_uno, _ = await _fila_cruda(db_session, primero.id)
    raw_dos, raw_tel_dos = await _fila_cruda(db_session, segundo.id)

    assert raw_uno != raw_dos
    assert raw_tel_dos.startswith("gAAAA")
    assert raw_tel_dos != telefono


@pytest.mark.asyncio
async def test_relectura_orm_descifra_varias_filas(db_session):
    """TRIANGULATE (2.6): releer con el ORM descifra todas las filas."""
    await _crear_empleado(
        db_session, legajo="C153-5", email="cinco@example.test", telefono="+5491100005005"
    )
    await _crear_empleado(
        db_session, legajo="C153-6", email="seis@example.test"
    )

    filas = (
        (await db_session.execute(select(Empleado).order_by(Empleado.id)))
        .scalars()
        .all()
    )
    por_legajo = {e.legajo: e for e in filas}
    assert por_legajo["C153-5"].email == "cinco@example.test"
    assert por_legajo["C153-5"].telefono == "+5491100005005"
    assert por_legajo["C153-6"].email == "seis@example.test"
    assert por_legajo["C153-6"].telefono is None

