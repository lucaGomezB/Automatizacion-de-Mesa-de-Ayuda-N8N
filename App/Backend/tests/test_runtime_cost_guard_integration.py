"""
Tests de integracion PostgreSQL de la guarda de costo (c-45).

Requieren un PostgreSQL alcanzable (base descartable provista por los fixtures
de `conftest.py`) y se ejecutan con `pytest -m integration`. Verifican la
reserva atomica real contra la tabla `costo_guarda_contador`: la carrera
chequear-y-actualizar no puede exceder el conteo bajo concurrencia.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.cost_guard.clock import SystemClock
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.constants import (
    AMBITO_GLOBAL,
    PROVIDER_BACKEND_GEMINI,
)
from app.cost_guard.decision import window_start
from app.cost_guard.guard import CostGuard
from app.cost_guard.protocols import CounterKey, Reservation
from app.cost_guard.store_postgres import PostgresCounterStore
from app.models.costo_guarda_contador import CostoGuardaContador

pytestmark = pytest.mark.integration


def _key(clave: str) -> CounterKey:
    return CounterKey(
        ambito=AMBITO_GLOBAL,
        clave=clave,
        ventana_inicio=window_start(datetime.now(timezone.utc), 3600),
    )


async def test_reserva_atomica_concurrente_no_excede(pg_engine):
    """5.3: N reservas concurrentes incrementan exactamente N veces."""
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    clave = f"rate-concurrente-{uuid.uuid4().hex[:12]}"
    key = _key(clave)

    async def reserve_once() -> None:
        store = PostgresCounterStore(session_factory=factory)
        await store.reserve_many([Reservation(key, calls_delta=1, cost_delta=Decimal("0"))])
        await store.commit()

    await asyncio.gather(*[reserve_once() for _ in range(10)])

    async with factory() as session:
        row = await session.scalar(
            select(CostoGuardaContador).where(
                CostoGuardaContador.ambito == AMBITO_GLOBAL,
                CostoGuardaContador.clave == clave,
                CostoGuardaContador.ventana_inicio == key.ventana_inicio,
            )
        )
    assert row is not None
    assert row.llamadas == 10, (
        "La reserva atomica no debe perder incrementos bajo concurrencia"
    )


async def test_rollback_no_consolida_la_reserva(pg_engine):
    """El rollback de la reserva denegada no deja contadores consolidados."""
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    clave = f"rollback-{uuid.uuid4().hex[:12]}"
    key = _key(clave)

    store = PostgresCounterStore(session_factory=factory)
    await store.reserve_many([Reservation(key, calls_delta=1, cost_delta=Decimal("0.05"))])
    await store.rollback()

    async with factory() as session:
        row = await session.scalar(
            select(CostoGuardaContador).where(
                CostoGuardaContador.clave == clave,
                CostoGuardaContador.ventana_inicio == key.ventana_inicio,
            )
        )
    assert row is None, "El rollback no debe consolidar la reserva"


async def test_guarda_contra_postgresql_permite_y_reserva(pg_engine):
    """La guarda completa reserva la bolsa global contra PostgreSQL."""
    factory = async_sessionmaker(pg_engine, expire_on_commit=False)
    config = CostGuardConfig(
        enabled=True,
        budget_usd=Decimal("10"),
        budget_window_seconds=604800,
        rate_limit_calls=30,
        rate_window_seconds=3600,
        caller_rate_limit_calls=3,
        caller_rate_window_seconds=3600,
        unit_costs_usd={PROVIDER_BACKEND_GEMINI: Decimal("0.0005")},
        degradation_policy="deterministic_review",
        store_failure_policy="fail_closed",
    )
    guard = CostGuard(
        store=PostgresCounterStore(session_factory=factory),
        clock=SystemClock(),
        config=config,
    )
    decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is True

    async with factory() as session:
        row = await session.scalar(
            select(CostoGuardaContador).where(
                CostoGuardaContador.ambito == AMBITO_GLOBAL,
                CostoGuardaContador.clave == "budget",
            )
        )
    assert row is not None and row.llamadas >= 1
