"""
Concurrencia real del reclamo atomico de reintento de telefonia (c-52, W-CONC).

Escenario del spec "Solo un reintento concurrente reclama el ingreso": dos
reintentos del mismo `CallSid` intentan reclamar un ingreso en estado terminal de
error de forma concurrente; solo uno gana el UPDATE atomico y el otro resuelve
como no-op.

Requiere PostgreSQL: la garantia se apoya en el locking de fila de READ COMMITTED
(el segundo UPDATE bloquea hasta que el primero confirma y luego reevalua el
WHERE, afectando 0 filas). SQLite no implementa ese bloqueo, por eso este modulo
es `integration`.
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.telefonia_ingreso import TelefoniaIngreso, TranscripcionEstado
from app.repositories.telefonia_ingreso_repository import TelefoniaIngresoRepository

# Se importa el conjunto REAL de estados terminales elegibles para reintento
# para que el test no pueda divergir de la definicion de produccion.
from app.services.telefonia_service import _TERMINAL_ERROR_STATES

pytestmark = pytest.mark.integration

# Ventana en la que B debe permanecer bloqueado mientras A retiene el lock. No
# mide una carrera: una B bloqueada por el row lock NUNCA puede completar antes
# de que A confirme, de modo que este assert no produce falsos negativos. Una
# implementacion sin locking completaria en milisegundos.
_BLOCK_OBSERVATION_SECONDS = 0.5


async def _seed_error_ingreso(engine, call_sid: str) -> None:
    """Inserta (y confirma) un ingreso elegible para reintento."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(
            TelefoniaIngreso(
                call_sid=call_sid,
                transcripcion_estado=TranscripcionEstado.error_stt.value,
            )
        )
        await session.commit()


async def test_claim_for_retry_solo_un_concurrente_gana(pg_engine):
    """Dos reclamos concurrentes sobre PostgreSQL: exactamente uno gana.

    Secuenciacion deterministica con `asyncio.Event`:
        1. A ejecuta su UPDATE y retiene la transaccion abierta (lock de fila).
        2. B arranca su UPDATE; PostgreSQL lo bloquea en el lock de fila.
        3. A confirma; B desbloquea, reevalua el WHERE (el estado ya no es
           terminal) y su UPDATE afecta 0 filas.
    """
    call_sid = "CA-PG-CONC-1"
    await _seed_error_ingreso(pg_engine, call_sid)

    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    session_a = factory()
    session_b = factory()

    a_locked = asyncio.Event()      # A ya ejecuto su UPDATE y retiene el lock
    b_attempting = asyncio.Event()  # B esta por ejecutar su UPDATE
    a_release = asyncio.Event()     # habilita el commit de A

    async def _claim_a() -> bool:
        claimed = await TelefoniaIngresoRepository(session_a).claim_for_retry(
            call_sid, _TERMINAL_ERROR_STATES
        )
        a_locked.set()
        await a_release.wait()
        await session_a.commit()
        return claimed

    async def _claim_b() -> bool:
        await a_locked.wait()
        b_attempting.set()
        claimed = await TelefoniaIngresoRepository(session_b).claim_for_retry(
            call_sid, _TERMINAL_ERROR_STATES
        )
        await session_b.commit()
        return claimed

    task_a = asyncio.create_task(_claim_a())
    task_b = asyncio.create_task(_claim_b())

    try:
        await b_attempting.wait()
        done, _pending = await asyncio.wait(
            {task_b}, timeout=_BLOCK_OBSERVATION_SECONDS
        )
        assert not done, (
            "El segundo reclamo completo mientras el primero retenia el lock de "
            "fila: no hubo bloqueo (la atomicidad del reclamo depende de el)."
        )

        a_release.set()
        claimed_a = await task_a
        claimed_b = await task_b
    finally:
        await session_a.close()
        await session_b.close()

    assert claimed_a is True, "El primer reclamo debio ganar el UPDATE."
    assert claimed_b is False, "El segundo reclamo debio afectar 0 filas."
    assert {claimed_a, claimed_b} == {True, False}

    # Lectura con una conexion fresca: el estado final confirmado es `pendiente`.
    async with factory() as session:
        fila = (
            await session.execute(
                select(TelefoniaIngreso).where(
                    TelefoniaIngreso.call_sid == call_sid
                )
            )
        ).scalar_one()
        assert fila.transcripcion_estado == TranscripcionEstado.pendiente.value
        assert fila.error_detalle is None
