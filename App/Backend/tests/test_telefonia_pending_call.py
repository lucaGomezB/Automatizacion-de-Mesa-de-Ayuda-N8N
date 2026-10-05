"""
Tests del store de correlacion `telefonia_pending_call` (c-70, D2).

Strict TDD: se escriben ANTES del modelo/repositorio/servicio.

Cubren (tareas 2.2, 2.3, 2.4):
    - `upsert(call_sid -> corpus_case_id)` persiste y es idempotente.
    - `get_by_call_sid` devuelve la fila o None.
    - `delete_by_call_sid` borra y es idempotente (no falla si no existe).
    - `purge_expired` purga las filas vencidas y respeta las vigentes.
    - El servicio NO escribe nada cuando el `corpus_case_id` es None
      (retrocompatible con produccion) y resuelve+borra al resolver.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

_NOW = datetime(2026, 10, 5, 12, 0, 0, tzinfo=timezone.utc)
_TTL = 1800


def _repo(session):
    from app.repositories.telefonia_pending_call_repository import (
        TelefoniaPendingCallRepository,
    )

    return TelefoniaPendingCallRepository(session)


def _service(session, clock=None):
    from app.services.telefonia_pending_call_service import (
        TelefoniaPendingCallService,
    )

    return TelefoniaPendingCallService(session, clock=clock)


class _FrozenClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


# ── 2.2 RED — El repositorio persiste el mapeo ──────────────────────────────


async def test_upsert_persiste_el_mapeo(db_session):
    repo = _repo(db_session)

    fila = await repo.upsert("CA-PEND-1", "CASO-1")

    assert fila.call_sid == "CA-PEND-1"
    assert fila.corpus_case_id == "CASO-1"
    encontrado = await repo.get_by_call_sid("CA-PEND-1")
    assert encontrado is not None
    assert encontrado.corpus_case_id == "CASO-1"


async def test_get_by_call_sid_none_si_no_existe(db_session):
    repo = _repo(db_session)
    assert await repo.get_by_call_sid("CA-NO-EXISTE") is None


# ── 2.4 TRIANGULATE — Idempotencia, caracteres especiales, borrado y purga ──


async def test_upsert_es_idempotente_por_call_sid(db_session):
    from sqlalchemy import func, select

    from app.models.telefonia_pending_call import TelefoniaPendingCall

    repo = _repo(db_session)
    await repo.upsert("CA-PEND-2", "CASO-VIEJO")
    await repo.upsert("CA-PEND-2", "CASO-NUEVO")

    encontrado = await repo.get_by_call_sid("CA-PEND-2")
    assert encontrado is not None
    assert encontrado.corpus_case_id == "CASO-NUEVO"

    total = await db_session.scalar(
        select(func.count()).select_from(TelefoniaPendingCall)
    )
    assert total == 1


async def test_upsert_acepta_caracteres_especiales(db_session):
    repo = _repo(db_session)
    caso = "caso 2026/telefono #7 ñ"
    await repo.upsert("CA-PEND-ESP", caso)

    encontrado = await repo.get_by_call_sid("CA-PEND-ESP")
    assert encontrado is not None
    assert encontrado.corpus_case_id == caso


async def test_delete_by_call_sid_borra_y_es_idempotente(db_session):
    repo = _repo(db_session)
    await repo.upsert("CA-PEND-3", "CASO-3")

    assert await repo.delete_by_call_sid("CA-PEND-3") is True
    assert await repo.get_by_call_sid("CA-PEND-3") is None
    # Segundo borrado: no-op sin excepcion.
    assert await repo.delete_by_call_sid("CA-PEND-3") is False


async def test_purge_expired_purga_vencidas_y_respeta_vigentes(db_session):
    from app.models.telefonia_pending_call import TelefoniaPendingCall

    db_session.add_all(
        [
            TelefoniaPendingCall(
                call_sid="CA-VENCIDA",
                corpus_case_id="CASO-A",
                created_at=_NOW - timedelta(seconds=_TTL + 1),
            ),
            TelefoniaPendingCall(
                call_sid="CA-VIGENTE",
                corpus_case_id="CASO-B",
                created_at=_NOW - timedelta(seconds=60),
            ),
        ]
    )
    await db_session.flush()

    repo = _repo(db_session)
    purgadas = await repo.purge_expired(_NOW, ttl_seconds=_TTL)

    assert purgadas == 1
    assert await repo.get_by_call_sid("CA-VENCIDA") is None
    assert await repo.get_by_call_sid("CA-VIGENTE") is not None


async def test_purge_expired_no_purga_nada_si_todo_esta_vigente(db_session):
    repo = _repo(db_session)
    await repo.upsert("CA-RECIENTE", "CASO-C")

    purgadas = await repo.purge_expired(_NOW, ttl_seconds=_TTL)

    assert purgadas == 0
    assert await repo.get_by_call_sid("CA-RECIENTE") is not None


# ── 2.2 / 2.4 — Servicio: retrocompatible y resuelve+borra ──────────────────


async def test_servicio_no_escribe_si_corpus_case_id_es_none(db_session):
    servicio = _service(db_session, clock=_FrozenClock(_NOW))

    resultado = await servicio.registrar("CA-SIN-PARAM", None)

    assert resultado is None
    repo = _repo(db_session)
    assert await repo.get_by_call_sid("CA-SIN-PARAM") is None


async def test_servicio_registrar_escribe_el_mapeo(db_session):
    servicio = _service(db_session, clock=_FrozenClock(_NOW))

    await servicio.registrar("CA-CON-PARAM", "CASO-OK")

    repo = _repo(db_session)
    fila = await repo.get_by_call_sid("CA-CON-PARAM")
    assert fila is not None
    assert fila.corpus_case_id == "CASO-OK"


async def test_servicio_resolver_y_borrar_devuelve_y_elimina(db_session):
    repo = _repo(db_session)
    await repo.upsert("CA-RESOLVER", "CASO-RES")
    servicio = _service(db_session, clock=_FrozenClock(_NOW))

    valor = await servicio.resolver_y_borrar("CA-RESOLVER")

    assert valor == "CASO-RES"
    assert await repo.get_by_call_sid("CA-RESOLVER") is None


async def test_servicio_resolver_y_borrar_miss_devuelve_none(db_session):
    servicio = _service(db_session, clock=_FrozenClock(_NOW))
    assert await servicio.resolver_y_borrar("CA-MISS") is None


async def test_servicio_purgar_vencidas_usa_el_reloj(db_session):
    from app.models.telefonia_pending_call import TelefoniaPendingCall

    db_session.add(
        TelefoniaPendingCall(
            call_sid="CA-OLD",
            corpus_case_id="CASO-OLD",
            created_at=_NOW - timedelta(seconds=_TTL + 10),
        )
    )
    await db_session.flush()

    servicio = _service(db_session, clock=_FrozenClock(_NOW))
    purgadas = await servicio.purgar_vencidas()

    assert purgadas == 1
