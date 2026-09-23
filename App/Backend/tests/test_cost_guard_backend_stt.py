"""
Tests de la superficie paga `backend_stt` de la guarda de costo (c-52).

TDD: se escriben ANTES de agregar la constante y el costo unitario.

Cubren:
    - `PROVIDER_BACKEND_STT` declarada y presente en `PAID_PROVIDERS`.
    - El mapa de costos de `CostGuardConfig.from_settings` incluye la superficie
      con su costo unitario configurable.
    - La guarda reserva la superficie con ese costo sobre la bolsa global.
    - Triangulacion: el costo de `twilio` queda re-estimado (ya no representa
      una transcripcion) y `backend_stt` es una superficie DISTINTA con su
      propio costo.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.config.settings import Settings
from app.cost_guard import constants
from app.cost_guard.clock import FrozenClock
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.decision import window_start
from app.cost_guard.guard import CostGuard
from app.cost_guard.protocols import CounterKey
from app.cost_guard.store_fake import InMemoryCounterStore

_NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
_BUDGET_WINDOW = 604800
_BACKEND_STT_DEFAULT = Decimal("0.0038")
_TWILIO_REESTIMADO = Decimal("0.0075")


def _settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = dict(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="test-key",
        pseudonymization_encryption_key="test-fernet-key",
        jwt_secret_key="test-jwt-secret",
        _env_file=None,
    )
    base.update(overrides)
    return Settings(**base)


def _provider() -> str:
    provider = getattr(constants, "PROVIDER_BACKEND_STT", None)
    assert provider is not None, "debe existir PROVIDER_BACKEND_STT en constants"
    return provider


def budget_key() -> CounterKey:
    return CounterKey(
        ambito=constants.AMBITO_GLOBAL,
        clave="budget",
        ventana_inicio=window_start(_NOW, _BUDGET_WINDOW),
    )


# ── 2.4 RED — Superficie declarada ──────────────────────────────────────────


def test_backend_stt_es_superficie_paga_declarada():
    provider = _provider()
    assert provider == "backend_stt"
    assert provider in constants.PAID_PROVIDERS


def test_config_incluye_backend_stt_con_su_costo_unitario():
    config = CostGuardConfig.from_settings(_settings())
    provider = _provider()
    assert provider in config.unit_costs_usd
    assert config.unit_costs_usd[provider] == _BACKEND_STT_DEFAULT


# ── 2.5 GREEN — Override configurable ───────────────────────────────────────


def test_config_acepta_override_del_costo_backend_stt():
    config = CostGuardConfig.from_settings(
        _settings(cost_guard_unit_cost_backend_stt_usd=0.01)
    )
    assert config.unit_costs_usd[_provider()] == Decimal("0.01")


async def test_guarda_reserva_backend_stt_con_su_costo():
    """La reserva de backend_stt descuenta su costo unitario de la bolsa global."""
    store = InMemoryCounterStore()
    config = CostGuardConfig.from_settings(_settings())
    guard = CostGuard(store=store, clock=FrozenClock(_NOW), config=config)

    decision = await guard.evaluate(_provider())

    assert decision.allowed is True
    assert store.snapshot(budget_key()).costo_usd == _BACKEND_STT_DEFAULT


# ── 2.6 TRIANGULATE — twilio re-estimado y superficies distintas ─────────────


def test_twilio_reestimado_ya_no_representa_la_transcripcion():
    config = CostGuardConfig.from_settings(_settings())
    twilio = config.unit_costs_usd[constants.PROVIDER_TWILIO]
    assert twilio == _TWILIO_REESTIMADO
    assert twilio != Decimal("0.05")


def test_backend_stt_y_twilio_son_superficies_distintas():
    config = CostGuardConfig.from_settings(_settings())
    stt = config.unit_costs_usd[_provider()]
    twilio = config.unit_costs_usd[constants.PROVIDER_TWILIO]
    assert _provider() != constants.PROVIDER_TWILIO
    assert stt != twilio


async def test_guarda_reserva_twilio_y_backend_stt_en_la_misma_bolsa():
    store = InMemoryCounterStore()
    config = CostGuardConfig.from_settings(_settings())
    guard = CostGuard(store=store, clock=FrozenClock(_NOW), config=config)

    await guard.evaluate(constants.PROVIDER_TWILIO)
    await guard.evaluate(_provider())

    expected = _TWILIO_REESTIMADO + _BACKEND_STT_DEFAULT
    assert store.snapshot(budget_key()).costo_usd == expected