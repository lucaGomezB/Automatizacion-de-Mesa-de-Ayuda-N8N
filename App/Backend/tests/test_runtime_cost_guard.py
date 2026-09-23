"""
Tests offline de la guarda de costo en runtime (c-45-runtime-cost-guard).

Responsabilidad:
    Verifica, sin red y sin PostgreSQL, el comportamiento de la guarda:
    presupuesto global compartido, costo unitario por superficie, ventanas
    (presupuesto, tasa global y tasa por origen), fail-closed ante almacen
    no disponible, observabilidad estructurada, postura al arranque,
    enforcement en el clasificador hibrido, endpoint de reserva para n8n,
    webhook de voz pre-llamada de Twilio y registro del numero de origen crudo
    excluido del corpus de evaluacion.

Estrategia:
    El almacen de contadores y el reloj se inyectan como dependencias: se usa
    `InMemoryCounterStore` (fake sin red) y `FrozenClock`. Ninguna prueba abre
    conexiones ni requiere servicios externos.

Strict TDD: este modulo se escribe ANTES de la implementacion.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import logging
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from xml.etree import ElementTree

import pytest
import yaml
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.classifiers.hybrid import HybridClassifier
from app.config.settings import Settings
from app.core.exceptions import CostGuardTrippedError
from app.cost_guard.clock import FrozenClock, SystemClock
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.constants import (
    AMBITO_CALLER,
    AMBITO_GLOBAL,
    CAUSE_BUDGET,
    CAUSE_CALLER_RATE,
    CAUSE_RATE,
    CAUSE_STORE_UNAVAILABLE,
    EVENT_COST_GUARD_POSTURE,
    EVENT_COST_GUARD_SECRET_MISSING,
    EVENT_COST_GUARD_STORE_UNAVAILABLE,
    EVENT_COST_GUARD_TRIPPED,
    EVENT_COST_GUARD_TWILIO_TOKEN_MISSING,
    PROVIDER_BACKEND_GEMINI,
    PROVIDER_BACKEND_STT,
    PROVIDER_N8N_GEMINI,
    PROVIDER_TWILIO,
)
from app.cost_guard.decision import (
    GuardCounters,
    GuardLimits,
    evaluate_counters,
    window_start,
)
from app.cost_guard.guard import CostGuard
from app.cost_guard.posture import log_cost_guard_posture
from app.cost_guard.protocols import CounterKey, CounterSnapshot, Reservation
from app.cost_guard.store_fake import InMemoryCounterStore
from app.cost_guard.twilio_signature import compute_signature
from app.main import create_app
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import IncidenteCreate
from app.cost_guard.dependencies import get_cost_guard
from app.services.incidente_service import IncidenteService

# ── Constantes de prueba ────────────────────────────────────────────────────

_UNIT_BACKEND = Decimal("0.0005")
_UNIT_N8N = Decimal("0.0015")
_UNIT_TWILIO = Decimal("0.05")
_BUDGET = Decimal("10")
_WINDOW_BUDGET = 604800
_WINDOW_RATE = 3600
_WINDOW_CALLER = 3600
_RATE_LIMIT = 30
_CALLER_RATE_LIMIT = 3

_NOW = datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc)


def make_config(**overrides: Any) -> CostGuardConfig:
    """Construye una configuracion de guarda determinista para los tests."""
    base: dict[str, Any] = dict(
        enabled=True,
        budget_usd=_BUDGET,
        budget_window_seconds=_WINDOW_BUDGET,
        rate_limit_calls=_RATE_LIMIT,
        rate_window_seconds=_WINDOW_RATE,
        caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        caller_rate_window_seconds=_WINDOW_CALLER,
        unit_costs_usd={
            PROVIDER_BACKEND_GEMINI: _UNIT_BACKEND,
            PROVIDER_N8N_GEMINI: _UNIT_N8N,
            PROVIDER_TWILIO: _UNIT_TWILIO,
        },
        degradation_policy="deterministic_review",
        store_failure_policy="fail_closed",
    )
    base.update(overrides)
    return CostGuardConfig(**base)


def make_guard(
    store: InMemoryCounterStore | None = None,
    clock: FrozenClock | None = None,
    alert_notifier: object | None = None,
    **overrides: Any,
) -> CostGuard:
    return CostGuard(
        store=store or InMemoryCounterStore(),
        clock=clock or FrozenClock(_NOW),
        config=make_config(**overrides),
        alert_notifier=alert_notifier,
    )


def budget_key(now: datetime = _NOW) -> CounterKey:
    return CounterKey(
        ambito=AMBITO_GLOBAL,
        clave="budget",
        ventana_inicio=window_start(now, _WINDOW_BUDGET),
    )


def rate_key(now: datetime = _NOW) -> CounterKey:
    return CounterKey(
        ambito=AMBITO_GLOBAL,
        clave="rate",
        ventana_inicio=window_start(now, _WINDOW_RATE),
    )


def caller_key(caller: str, now: datetime = _NOW) -> CounterKey:
    return CounterKey(
        ambito=AMBITO_CALLER,
        clave=caller,
        ventana_inicio=window_start(now, _WINDOW_CALLER),
    )


class _UnavailableStore:
    """Almacen que siempre falla: ejercita la politica fail-closed."""

    def __init__(self) -> None:
        self.commit_called = False
        self.rollback_called = False

    async def reserve_many(self, reservations: list[Reservation]) -> list[CounterSnapshot]:
        raise RuntimeError("postgres inalcanzable")

    async def commit(self) -> None:  # pragma: no cover - no debe llamarse
        self.commit_called = True

    async def rollback(self) -> None:
        self.rollback_called = True

    async def purge_expired(self, ambito: str, before: datetime) -> int:
        return 0


# ── 1.2-1.7 / 4.2 — Decision pura y ventanas ────────────────────────────────


def test_decision_permite_por_debajo_del_presupuesto():
    """1.2: con gasto global por debajo del presupuesto, permite."""
    decision = evaluate_counters(
        GuardCounters(budget_cost_usd=Decimal("5.0"), rate_calls=1),
        GuardLimits(
            budget_usd=_BUDGET,
            rate_limit_calls=_RATE_LIMIT,
            caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        ),
    )
    assert decision.allowed is True
    assert decision.cause is None


def test_decision_deniega_presupuesto_agotado():
    """1.3: gasto acumulado que supera el presupuesto deniega con causa budget."""
    decision = evaluate_counters(
        GuardCounters(budget_cost_usd=Decimal("10.05"), rate_calls=1),
        GuardLimits(
            budget_usd=_BUDGET,
            rate_limit_calls=_RATE_LIMIT,
            caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        ),
    )
    assert decision.allowed is False
    assert decision.cause == CAUSE_BUDGET


def test_decision_deniega_rate_global():
    """1.6: cantidad de llamadas por encima del limite deniega con causa rate."""
    decision = evaluate_counters(
        GuardCounters(budget_cost_usd=Decimal("0.1"), rate_calls=31),
        GuardLimits(
            budget_usd=_BUDGET,
            rate_limit_calls=_RATE_LIMIT,
            caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        ),
    )
    assert decision.allowed is False
    assert decision.cause == CAUSE_RATE


def test_decision_deniega_caller_rate():
    """1.7: origen excedido deniega con causa caller_rate."""
    decision = evaluate_counters(
        GuardCounters(budget_cost_usd=Decimal("0.1"), rate_calls=1, caller_calls=4),
        GuardLimits(
            budget_usd=_BUDGET,
            rate_limit_calls=_RATE_LIMIT,
            caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        ),
    )
    assert decision.allowed is False
    assert decision.cause == CAUSE_CALLER_RATE


def test_decision_no_deniega_caller_ausente():
    """13.x: sin caller disponible, la tasa por origen no aplica."""
    decision = evaluate_counters(
        GuardCounters(budget_cost_usd=Decimal("0.1"), rate_calls=1, caller_calls=None),
        GuardLimits(
            budget_usd=_BUDGET,
            rate_limit_calls=_RATE_LIMIT,
            caller_rate_limit_calls=_CALLER_RATE_LIMIT,
        ),
    )
    assert decision.allowed is True


def test_window_start_es_bucket_tumbling_anclado_a_epoch():
    now = datetime(2026, 3, 10, 12, 34, 56, tzinfo=timezone.utc)
    start = window_start(now, 3600)
    assert start.minute == 0 and start.second == 0
    assert start <= now < start + timedelta(seconds=3600)
    assert window_start(start, 3600) == start


def test_window_start_ventana_semanal():
    now = datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc)
    start = window_start(now, 604800)
    assert (now - start).total_seconds() < 604800
    assert window_start(start, 604800) == start


# ── 4.x / 5.3 — Fake en memoria y reserva atomica ───────────────────────────


async def test_fake_commit_aplica_reserva():
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is True
    snap = store.snapshot(budget_key())
    assert snap.llamadas == 1
    assert snap.costo_usd == _UNIT_BACKEND


async def test_fake_rollback_descarta_reserva():
    store = InMemoryCounterStore()
    store.seed(budget_key(), llamadas=200, costo_usd=Decimal("10.0"))
    guard = make_guard(store=store)
    decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is False
    # La reserva denegada no cuenta: el contador queda intacto.
    snap = store.snapshot(budget_key())
    assert snap.llamadas == 200
    assert snap.costo_usd == Decimal("10.0")


# ── 1.4 — Costo unitario por superficie con bolsa compartida ────────────────


async def test_superficies_distintas_comparten_bolsa_global():
    """1.4: dos superficies con costos distintos descuentan de la misma bolsa."""
    store = InMemoryCounterStore()
    guard = make_guard(store=store)

    await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    after_backend = store.snapshot(budget_key()).costo_usd
    assert after_backend == _UNIT_BACKEND

    await guard.evaluate(PROVIDER_N8N_GEMINI)
    after_n8n = store.snapshot(budget_key()).costo_usd
    assert after_n8n == _UNIT_BACKEND + _UNIT_N8N


async def test_gasto_de_una_superficie_afecta_la_evaluacion_de_otra():
    """13.6: la bolsa es compartida entre superficies."""
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    # La superficie backend ya consumio casi todo el presupuesto.
    store.seed(budget_key(), llamadas=1, costo_usd=Decimal("9.999"))
    decision = await guard.evaluate(PROVIDER_TWILIO)
    assert decision.allowed is False
    assert decision.cause == CAUSE_BUDGET


# ── 1.5 / 13.4 — Reinicio de ventanas con reloj inyectado ───────────────────


async def test_ventana_de_presupuesto_se_reinicia():
    """1.5: al avanzar el reloj mas alla de la ventana, el gasto se reinicia."""
    store = InMemoryCounterStore()
    clock = FrozenClock(_NOW)
    guard = make_guard(store=store, clock=clock)
    store.seed(budget_key(_NOW), llamadas=100, costo_usd=Decimal("10.0"))

    denied = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert denied.allowed is False

    clock.advance(_WINDOW_BUDGET + 10)
    allowed = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert allowed.allowed is True
    assert store.snapshot(budget_key(clock.now())).costo_usd == _UNIT_BACKEND


async def test_ventana_de_rate_global_se_reinicia():
    """13.4: el contador de tasa global se reinicia al vencer su ventana."""
    store = InMemoryCounterStore()
    clock = FrozenClock(_NOW)
    guard = make_guard(store=store, clock=clock)
    store.seed(rate_key(_NOW), llamadas=_RATE_LIMIT + 1)

    assert (await guard.evaluate(PROVIDER_BACKEND_GEMINI)).allowed is False
    clock.advance(_WINDOW_RATE + 10)
    assert (await guard.evaluate(PROVIDER_BACKEND_GEMINI)).allowed is True


async def test_ventana_por_origen_se_reinicia():
    """13.4: el contador por origen se reinicia al vencer su ventana."""
    store = InMemoryCounterStore()
    clock = FrozenClock(_NOW)
    guard = make_guard(store=store, clock=clock)
    caller = "+5492615551234"
    store.seed(caller_key(caller, _NOW), llamadas=_CALLER_RATE_LIMIT + 1)

    assert (await guard.evaluate(PROVIDER_TWILIO, caller=caller)).allowed is False
    clock.advance(_WINDOW_CALLER + 10)
    assert (await guard.evaluate(PROVIDER_TWILIO, caller=caller)).allowed is True


# ── 1.7 — Tasa por origen aislada por numero ────────────────────────────────


async def test_origen_excedido_no_bloquea_a_otros_origenes():
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    abusivo = "+5492615550000"
    store.seed(caller_key(abusivo), llamadas=_CALLER_RATE_LIMIT + 1)

    assert (await guard.evaluate(PROVIDER_TWILIO, caller=abusivo)).allowed is False
    assert (await guard.evaluate(PROVIDER_TWILIO, caller="+5492615559999")).allowed is True


# ── 1.8 / 10.x — Fail-closed y notificacion estructurada ────────────────────


async def test_store_inalcanzable_fail_closed_y_notificacion():
    """1.8 / 10.1 / 10.2: ante store caido, deniega y emite el evento ERROR."""
    store = _UnavailableStore()
    guard = make_guard(store=store)  # type: ignore[arg-type]
    with patch("app.cost_guard.guard.logger") as mock_logger:
        decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI, caller="+5492615551234")

    assert decision.allowed is False
    assert decision.cause == CAUSE_STORE_UNAVAILABLE
    assert store.rollback_called is True
    assert store.commit_called is False

    asserted = [c for c in mock_logger.error.call_args_list if c.args and c.args[0] == EVENT_COST_GUARD_STORE_UNAVAILABLE]
    assert asserted, "debe emitirse cost_guard_store_unavailable"
    kwargs = asserted[0].kwargs
    assert kwargs["cause"] == CAUSE_STORE_UNAVAILABLE
    assert kwargs["provider"] == PROVIDER_BACKEND_GEMINI
    assert kwargs["caller"] == "+5492615551234"
    assert kwargs["error_class"] == "RuntimeError"
    assert "secret" not in json.dumps(kwargs, default=str).lower()


async def test_politica_fail_closed_es_explicita():
    """10.1: el default configurado aplica fail-closed sin ambiguedad."""
    config = make_config()
    assert config.store_failure_policy == "fail_closed"


async def test_fail_closed_permite_reintentar_cuando_el_store_vuelve():
    store = InMemoryCounterStore()
    guarding = make_guard(store=store)
    fallando = _UnavailableStore()
    guard_unavailable = make_guard(store=fallando)  # type: ignore[arg-type]

    assert (await guard_unavailable.evaluate(PROVIDER_BACKEND_GEMINI)).allowed is False
    assert (await guarding.evaluate(PROVIDER_BACKEND_GEMINI)).allowed is True


# ── 11.1 / 1.x — Observabilidad del disparo ─────────────────────────────────


async def test_disparo_emite_evento_estructurado():
    store = InMemoryCounterStore()
    store.seed(budget_key(), llamadas=1, costo_usd=Decimal("10.0"))
    guard = make_guard(store=store)
    with patch("app.cost_guard.guard.logger") as mock_logger:
        decision = await guard.evaluate(PROVIDER_N8N_GEMINI, caller="+5492615551234")

    assert decision.allowed is False and decision.cause == CAUSE_BUDGET
    asserted = [c for c in mock_logger.warning.call_args_list if c.args and c.args[0] == EVENT_COST_GUARD_TRIPPED]
    assert asserted, "debe emitirse cost_guard_tripped"
    kwargs = asserted[0].kwargs
    assert kwargs["cause"] == CAUSE_BUDGET
    assert kwargs["provider"] == PROVIDER_N8N_GEMINI
    assert kwargs["caller"] == "+5492615551234"
    assert kwargs["window"] and kwargs["limit"] is not None


async def test_llamada_permitida_no_emite_evento_de_disparo():
    """11.1 / 13.5: una llamada permitida no emite cost_guard_tripped."""
    guard = make_guard()
    with patch("app.cost_guard.guard.logger") as mock_logger:
        decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)

    assert decision.allowed is True
    tripped = [c for c in mock_logger.warning.call_args_list if c.args and c.args[0] == EVENT_COST_GUARD_TRIPPED]
    assert tripped == []


# ── 9.3 — Purga de la ventana por origen ────────────────────────────────────


async def test_purga_ventanas_vencidas_de_caller():
    """9.3: los contadores de origen de ventanas vencidas se purgan."""
    store = InMemoryCounterStore()
    caller = "+5492615551234"
    old_key = CounterKey(
        ambito=AMBITO_CALLER,
        clave=caller,
        ventana_inicio=window_start(_NOW, _WINDOW_CALLER) - timedelta(seconds=_WINDOW_CALLER),
    )
    store.seed(old_key, llamadas=2)
    guard = make_guard(store=store)

    await guard.evaluate(PROVIDER_TWILIO, caller=caller)

    assert store.snapshot(old_key).llamadas == 0
    current = store.snapshot(caller_key(caller))
    assert current.llamadas == 1


# ── 11.2 / 11.3 — Postura al arranque y config invalida ─────────────────────


def test_postura_registra_estado_efectivo():
    """11.2: el arranque registra la postura efectiva."""
    config = make_config()
    # El log se emite con structlog module logger; se parchea para capturarlo.
    with patch("app.cost_guard.posture.logger") as mock_logger:
        log_cost_guard_posture(config)

    asserted = [
        c for c in mock_logger.info.call_args_list
        if c.args and c.args[0] == EVENT_COST_GUARD_POSTURE
    ]
    assert asserted, "debe emitirse cost_guard_posture"
    kwargs = asserted[0].kwargs
    assert kwargs["enabled"] is True
    assert Decimal(str(kwargs["budget_usd"])) == _BUDGET
    assert kwargs["budget_window_seconds"] == _WINDOW_BUDGET
    assert kwargs["rate_limit_calls"] == _RATE_LIMIT
    assert kwargs["caller_rate_limit_calls"] == _CALLER_RATE_LIMIT
    assert kwargs["degradation_policy"] == "deterministic_review"
    assert kwargs["store_failure_policy"] == "fail_closed"
    assert PROVIDER_BACKEND_GEMINI in kwargs["unit_costs_usd"]
    assert kwargs["twilio_auth_token_configured"] is False


def test_settings_defaults_conservadores():
    """2.1 / 13.3: sin configuracion, la guarda arranca habilitada y conservadora."""
    settings = _settings()
    config = CostGuardConfig.from_settings(settings)
    assert config.enabled is True
    assert config.budget_usd == _BUDGET
    assert config.budget_window_seconds == _WINDOW_BUDGET
    assert config.store_failure_policy == "fail_closed"
    assert config.degradation_policy == "deterministic_review"
    assert config.unit_costs_usd[PROVIDER_BACKEND_GEMINI] == _UNIT_BACKEND
    assert config.unit_costs_usd[PROVIDER_N8N_GEMINI] == _UNIT_N8N
    # c-52: twilio re-estimado (ya no representa una transcripcion) y la STT del
    # backend es una superficie propia con su propio costo.
    assert config.unit_costs_usd[PROVIDER_TWILIO] == Decimal("0.0075")
    assert config.unit_costs_usd[PROVIDER_BACKEND_STT] == Decimal("0.0038")


def test_settings_default_es_estable_entre_instanciaciones():
    """13.3: el default es identico en dos instanciaciones sin configuracion."""
    c1 = CostGuardConfig.from_settings(_settings())
    c2 = CostGuardConfig.from_settings(_settings())
    assert c1 == c2


def test_settings_configuracion_invalida_falla_explicito():
    """11.3: un monto no numerico no arranca silenciosamente."""
    with pytest.raises(ValidationError):
        _settings(cost_guard_budget_usd="no-es-un-numero")


def test_settings_override_por_entorno():
    """13.x: la configuracion de entorno sobrescribe el default."""
    settings = _settings(cost_guard_budget_usd=2.5, cost_guard_enabled=False)
    config = CostGuardConfig.from_settings(settings)
    assert config.budget_usd == Decimal("2.5")
    assert config.enabled is False


# ── 1.9 / 6.x — Enforcement en el clasificador hibrido ──────────────────────


async def test_guarda_disparada_no_invoca_al_proveedor_y_degrada():
    """1.9 / 6.1 / 6.2: con la guarda disparada no se llama a Gemini y hay revision."""
    store = InMemoryCounterStore()
    store.seed(budget_key(), llamadas=1, costo_usd=Decimal("10.0"))
    guard = make_guard(store=store)

    deterministic = AsyncMock()
    deterministic.classify = AsyncMock(
        return_value=ClasificacionResult(
            sector_predicho="Sistemas",
            confianza=0.55,
            etapa="deterministic",
            requiere_revision_humana=False,
        )
    )
    gemini = AsyncMock()
    gemini.classify = AsyncMock()

    classifier = HybridClassifier(
        deterministic=deterministic, gemini=gemini, cost_guard=guard
    )
    result = await classifier.classify("descripcion ambigua")

    gemini.classify.assert_not_called()
    assert result.etapa == "fallback"
    assert result.confianza == 0.0
    assert result.requiere_revision_humana is True
    assert result.sector_predicho == "Sistemas"


async def test_guarda_permite_y_gemini_se_invoca():
    """7.x / 6.1: con la guarda permitiendo, Gemini se invoca normalmente."""
    gemini = AsyncMock()
    gemini.classify = AsyncMock(
        return_value=ClasificacionResult(
            sector_predicho="Sistemas",
            confianza=0.9,
            etapa="gemini",
            requiere_revision_humana=False,
        )
    )
    deterministic = AsyncMock()
    deterministic.classify = AsyncMock(
        return_value=ClasificacionResult(
            sector_predicho="Bases de Datos",
            confianza=0.4,
            etapa="deterministic",
            requiere_revision_humana=False,
        )
    )
    classifier = HybridClassifier(
        deterministic=deterministic, gemini=gemini, cost_guard=make_guard()
    )
    result = await classifier.classify("descripcion ambigua")
    gemini.classify.assert_called_once()
    assert result.etapa == "gemini"


async def test_cortocircuito_deterministico_no_consume_presupuesto():
    """6.3 / 13.2: el cortocircuito determinista no consulta la guarda."""
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    deterministic = AsyncMock()
    deterministic.classify = AsyncMock(
        return_value=ClasificacionResult(
            sector_predicho="Sistemas",
            confianza=0.98,
            etapa="deterministic",
            requiere_revision_humana=False,
        )
    )
    gemini = AsyncMock()
    gemini.classify = AsyncMock()

    classifier = HybridClassifier(
        deterministic=deterministic, gemini=gemini, cost_guard=guard
    )
    result = await classifier.classify("se cayo el servidor")

    assert result.etapa == "deterministic"
    gemini.classify.assert_not_called()
    assert store.committed == {}, "el cortocircuito no debe reservar contadores"


async def test_excepcion_cost_guard_tripped_es_de_clasificacion():
    assert issubclass(CostGuardTrippedError, Exception)


async def test_politica_hard_block_no_invoca_al_proveedor_y_propaga_senal():
    """Spec: bloqueo duro propaga senal explicita sin invocar al proveedor pago."""
    store = InMemoryCounterStore()
    store.seed(budget_key(), llamadas=1, costo_usd=Decimal("10.0"))
    guard = make_guard(store=store)

    deterministic = AsyncMock()
    deterministic.classify = AsyncMock(
        return_value=ClasificacionResult(
            sector_predicho="Sistemas",
            confianza=0.4,
            etapa="deterministic",
            requiere_revision_humana=False,
        )
    )
    gemini = AsyncMock()
    gemini.classify = AsyncMock()

    classifier = HybridClassifier(
        deterministic=deterministic,
        gemini=gemini,
        cost_guard=guard,
        degradation_policy="hard_block",
    )
    with pytest.raises(CostGuardTrippedError) as excinfo:
        await classifier.classify("descripcion ambigua")

    gemini.classify.assert_not_called()
    assert excinfo.value.cause == CAUSE_BUDGET


# ── 6.3 / 13.1 — Clasificacion precalculada no consulta la guarda ───────────


async def test_clasificacion_precalculada_no_consume_presupuesto(
    db_session, seed_catalogs
):
    """6.3 / 13.1: la clasificacion precalculada omite la guarda por completo."""
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    classifier = AsyncMock()
    classifier.classify = AsyncMock()

    service = IncidenteService(
        session=db_session, classifier=classifier, cost_guard=guard
    )
    payload = IncidenteCreate(
        descripcion="Detectamos phishing con enlaces maliciosos",
        clasificacion={
            "sector_predicho": "Seguridad Informatica",
            "confianza": 0.95,
            "origen": "n8n",
        },
    )
    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock):
        incidente = await service.create_and_classify(payload)

    classifier.classify.assert_not_called()
    assert store.committed == {}, "la precalculada no debe reservar contadores"
    assert incidente.id is not None


# ── 1.10 / 7.1 — Endpoint de guarda para n8n ────────────────────────────────


async def test_endpoint_reserva_n8n_permite():
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI, "caller": "+5492615551234"},
            headers=_guard_headers(),
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["allowed"] is True
    assert body["provider"] == PROVIDER_N8N_GEMINI


async def test_endpoint_reserva_n8n_deniega():
    store = InMemoryCounterStore()
    store.seed(budget_key(), llamadas=1, costo_usd=Decimal("10.0"))
    guard = make_guard(store=store)
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
            headers=_guard_headers(),
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["allowed"] is False
    assert body["cause"] == CAUSE_BUDGET


async def test_endpoint_reserva_n8n_store_caido_fail_closed():
    guard = make_guard(store=_UnavailableStore())  # type: ignore[arg-type]
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
            headers=_guard_headers(),
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["allowed"] is False
    assert body["cause"] == CAUSE_STORE_UNAVAILABLE


# ── 1.11 / 8.x — Webhook de voz pre-llamada de Twilio ───────────────────────


async def test_webhook_twilio_permite_devuelve_record_mono_con_callbacks():
    """c-52: la rama admitida graba en mono con callbacks y SIN transcripcion."""
    guard = make_guard()
    params = {
        "From": "+5492615551234",
        "To": "+5492615550000",
        "CallSid": "CA123",
        "AccountSid": "AC123",
        "CallStatus": "ringing",
        "Direction": "inbound",
    }
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")
    root = ElementTree.fromstring(resp.text)
    assert root.tag == "Response"
    record = root.find("Record")
    assert record is not None
    # c-52: sin transcripcion embebida de Twilio; con callbacks de estado y fin.
    assert "transcribe" not in record.attrib
    assert record.attrib.get("maxLength") == "45"
    assert record.attrib.get("recordingStatusCallback", "").endswith(
        "/api/v1/telefonia/recording-status"
    )
    assert record.attrib.get("action", "").endswith(
        "/api/v1/telefonia/record-complete"
    )
    # El XML debe ser parseable como TwiML valido
    assert root.find("Say") is not None


async def test_webhook_twilio_deniega_devuelve_say_y_hangup():
    store = InMemoryCounterStore()
    store.seed(caller_key("+5492615551234"), llamadas=_CALLER_RATE_LIMIT + 1)
    guard = make_guard(store=store)
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")
    root = ElementTree.fromstring(resp.text)
    assert root.find("Hangup") is not None
    assert root.find("Record") is None
    assert root.find("Say") is not None


async def test_webhook_twilio_reserva_una_unidad_por_llamada():
    """8.3: se reserva exactamente un costo unitario de transcripcion por llamada."""
    store = InMemoryCounterStore()
    guard = make_guard(store=store)
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
        await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
    assert store.snapshot(budget_key()).costo_usd == _UNIT_TWILIO * 2
    assert store.snapshot(caller_key("+5492615551234")).llamadas == 2


# ── 1.12 / 9.x — Numero de origen crudo y exclusion del corpus ──────────────


async def test_caller_crudo_aparece_en_eventos_de_guarda():
    """1.12 / 9.1: el numero crudo se emite en los eventos de la guarda."""
    store = InMemoryCounterStore()
    store.seed(caller_key("+5492615551234"), llamadas=_CALLER_RATE_LIMIT + 1)
    guard = make_guard(store=store)
    with patch("app.cost_guard.guard.logger") as mock_logger:
        await guard.evaluate(PROVIDER_TWILIO, caller="+5492615551234")

    asserted = [c for c in mock_logger.warning.call_args_list if c.args and c.args[0] == EVENT_COST_GUARD_TRIPPED]
    assert asserted
    assert asserted[0].kwargs["caller"] == "+5492615551234"
    assert asserted[0].kwargs["cause"] == CAUSE_CALLER_RATE


def test_corpus_de_evaluacion_no_incorpora_el_caller():
    """1.12 / 9.2: el corpus de evaluacion NO consume el numero de origen."""
    corpus_path = Path(__file__).resolve().parents[3] / "evaluation" / "corpus.py"
    spec = importlib.util.spec_from_file_location("corpus_guard_check", corpus_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registrar en sys.modules: con `from __future__ import annotations` el
    # decorador @dataclass necesita resolver las anotaciones string via el modulo.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    fields = {f.name for f in dataclasses.fields(module.CasoEvaluacion)}
    prohibidos = {"caller", "telefono", "phone", "numero_origen", "from_number"}
    assert not (fields & prohibidos), (
        f"El corpus de evaluacion no debe incorporar el caller crudo: {fields & prohibidos}"
    )


# ── 5.4 — Construccion perezosa del adaptador PostgreSQL ────────────────────


def test_postgres_store_no_abre_conexion_al_construir():
    """5.4: construir el adaptador no resuelve la fabrica ni abre conexion."""
    from app.cost_guard.store_postgres import PostgresCounterStore

    store = PostgresCounterStore()
    assert store._session is None
    assert store._session_factory is None


# ── 11.2 — Postura registrada en el arranque (lifespan) ─────────────────────


async def test_lifespan_registra_postura_de_la_guarda():
    """11.2: el arranque de FastAPI registra la postura efectiva."""
    app = create_app()
    with patch("app.main.log_cost_guard_posture") as mock_posture:
        async with app.router.lifespan_context(app):
            pass
    mock_posture.assert_called_once()


# ── 7.3 / 8.4 / 15.5 — Workflow n8n y twiml.xml ─────────────────────────────


def _load_workflow() -> dict:
    path = Path(__file__).resolve().parents[3] / "n8n" / "workflow.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def test_workflow_json_parsea_y_conexiones_referencian_nodos_existentes():
    """7.3: el JSON parsea y ninguna conexion apunta a un nodo inexistente."""
    wf = _load_workflow()
    names = {n["name"] for n in wf["nodes"]}
    for source, outputs in wf["connections"].items():
        assert source in names, f"Origen de conexion inexistente: {source!r}"
        for branch in outputs.get("main", []):
            for edge in branch:
                assert edge["node"] in names, (
                    f"Conexion {source!r} -> {edge['node']!r} apunta a un nodo inexistente"
                )


def test_workflow_guarda_de_costo_entrega_al_ai_agent_y_deriva_al_denegar():
    """7.2/7.3: la guarda se interpone entre el sello y el AI Agent."""
    wf = _load_workflow()
    conns = wf["connections"]

    def successors(node: str) -> list[str]:
        result = []
        for branch in conns.get(node, {}).get("main", []):
            for edge in branch:
                result.append(edge["node"])
        return result

    assert "Guard de costo" in successors("Sellar ingreso telefonia")
    # C-47: el nodo 'Restaurar item telefonia' se intercala entre la guarda y el
    # IF para devolver el item sellado con la decision `allowed` re-inyectada.
    # La guarda sigue alcanzando 'Guard permite?' a traves de ese nodo.
    guard_successors = successors("Guard de costo")
    assert "Guard permite?" in guard_successors or (
        "Restaurar item telefonia" in guard_successors
        and "Guard permite?" in successors("Restaurar item telefonia")
    )
    guard_if_outputs = conns["Guard permite?"]["main"]
    assert "AI Agent" in [e["node"] for e in guard_if_outputs[0]]
    assert "Derivar a revision humana" in [e["node"] for e in guard_if_outputs[1]]


def test_workflow_nodo_guarda_apunta_al_endpoint_de_reserva():
    wf = _load_workflow()
    node = next(n for n in wf["nodes"] if n["name"] == "Guard de costo")
    url = node["parameters"]["url"]
    assert "/api/v1/cost-guard/reserve" in url
    assert node["parameters"]["body"]["provider"] == "n8n_gemini"


def test_twiml_xml_es_valido_y_graba_mono_con_callbacks():
    """c-52: el twiml.xml de referencia es XML valido, mono y sin transcripcion."""
    path = Path(__file__).resolve().parents[3] / "n8n" / "twilio" / "twiml.xml"
    root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
    assert root.tag == "Response"
    record = root.find("Record")
    assert record is not None
    assert "transcribe" not in record.attrib
    assert record.attrib.get("channels") == "mono"
    assert record.attrib.get("recordingStatusCallback", "").endswith(
        "/api/v1/telefonia/recording-status"
    )
    assert record.attrib.get("action", "").endswith(
        "/api/v1/telefonia/record-complete"
    )


# ── 17. Fix post-verify: cableado del secreto compartido de n8n (B2) ─────────
#
# B2: el nodo 'Guard de costo' envia X-Cost-Guard-Secret con
# `$env.COST_GUARD_SHARED_SECRET`, pero esa variable no estaba definida para el
# servicio n8n. Estos tests estructurales impiden que el cableado vuelva a
# regresar en silencio: exigen que el workflow la referencie y que
# docker-compose la inyecte en n8n desde la MISMA fuente que el backend.


_COMPOSE_FILE = Path(__file__).resolve().parents[3] / "docker-compose.yml"


def test_workflow_nodo_guarda_envia_el_secreto_compartido_desde_env():
    """B2: el nodo 'Guard de costo' toma el secreto de $env.COST_GUARD_SHARED_SECRET."""
    wf = _load_workflow()
    node = next(n for n in wf["nodes"] if n["name"] == "Guard de costo")
    params = node["parameters"]["headerParameters"]["parameters"]
    header = next(p for p in params if p["name"] == "X-Cost-Guard-Secret")
    assert "$env.COST_GUARD_SHARED_SECRET" in header["value"]


def test_compose_n8n_define_el_secreto_compartido():
    """B2: docker-compose inyecta COST_GUARD_SHARED_SECRET en el servicio n8n."""
    compose = yaml.safe_load(_COMPOSE_FILE.read_text(encoding="utf-8"))
    n8n_env = compose["services"]["n8n"]["environment"]
    assert "COST_GUARD_SHARED_SECRET" in n8n_env, (
        "el servicio n8n debe definir COST_GUARD_SHARED_SECRET: el nodo "
        "'Guard de costo' lo resuelve como $env.COST_GUARD_SHARED_SECRET"
    )
    assert "COST_GUARD_SHARED_SECRET" in str(n8n_env["COST_GUARD_SHARED_SECRET"])


def test_compose_backend_y_n8n_comparten_la_misma_fuente_del_secreto():
    """B2: backend y n8n toman el secreto de la MISMA variable de la raiz .env.

    Es la garantia de fuente unica: ambos servicios interpolan
    `${COST_GUARD_SHARED_SECRET:-}`, de modo que no pueden divergir.
    """
    compose = yaml.safe_load(_COMPOSE_FILE.read_text(encoding="utf-8"))
    backend_val = str(
        compose["services"]["backend"]["environment"]["COST_GUARD_SHARED_SECRET"]
    )
    n8n_val = str(
        compose["services"]["n8n"]["environment"]["COST_GUARD_SHARED_SECRET"]
    )
    assert backend_val == n8n_val == "${COST_GUARD_SHARED_SECRET:-}", (
        "backend y n8n deben interpolar la misma variable de la raiz .env; "
        f"backend={backend_val!r}, n8n={n8n_val!r}"
    )


# ── 16. Hardening post-verify (c-45) ────────────────────────────────────────
#
# Correcciones posteriores a la verificacion independiente:
#   16.1 Warning 1: los endpoints exigen secreto compartido por HEADER; sin
#        secreto configurado quedan cerrados (fail-closed) y se advierte al
#        arrancar. La via por query queda prohibida.
#   16.2 Warning 2: `store_failure_policy=fail_open` y `alert_enabled` dejan de
#        ser documentacion muerta: `fail_open` permite (no recomendado) y
#        `alert_enabled` controla la notificacion externa, sin suprimir el
#        evento estructurado obligatorio.
#   16.3 Warning 3: validacion de `X-Twilio-Signature` (HMAC-SHA1) exigida
#        cuando hay token de Twilio configurado; sin token se omite la firma
#        pero el secreto compartido sigue siendo obligatorio.

_GUARD_SECRET = "test-guard-secret"
_TWILIO_TOKEN = "twilio-auth-token-de-prueba"  # gitleaks:allow
_TWILIO_VOICE_URL = "http://test/api/v1/cost-guard/twilio/voice"


def _guard_headers(secret: str = _GUARD_SECRET) -> dict[str, str]:
    return {"X-Cost-Guard-Secret": secret}


def _twilio_headers(
    params: dict[str, str], token: str = _TWILIO_TOKEN
) -> dict[str, str]:
    """Headers de una peticion legitima de Twilio: solo `X-Twilio-Signature`.

    Twilio NO puede adjuntar headers personalizados a su webhook de voz; su
    unico mecanismo documentado es la firma. Estos headers demuestran que el
    webhook de Twilio no depende del secreto compartido.
    """
    signature = compute_signature(token, _TWILIO_VOICE_URL, params)
    return {"X-Twilio-Signature": signature}


# ── 16.1 — Autenticacion obligatoria de los endpoints (Warning 1) ───────────


async def test_endpoint_reserva_rechaza_sin_secreto():
    guard = make_guard()
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
        )
    assert resp.status_code == 401, resp.text
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


async def test_endpoint_reserva_rechaza_secreto_incorrecto():
    guard = make_guard()
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
            headers=_guard_headers("otro-secreto"),
        )
    assert resp.status_code == 401, resp.text


async def test_endpoint_reserva_acepta_secreto_correcto():
    guard = make_guard()
    async with _client_with_guard(guard) as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
            headers=_guard_headers(),
        )
    assert resp.status_code == 200, resp.text


async def test_endpoint_reserva_sin_secreto_configurado_queda_cerrado():
    """Sin secreto configurado no existe configuracion con endpoints abiertos."""
    guard = make_guard()
    async with _client_with_guard(guard, secret="") as client:
        resp = await client.post(
            "/api/v1/cost-guard/reserve",
            json={"provider": PROVIDER_N8N_GEMINI},
            headers=_guard_headers(),
        )
    assert resp.status_code == 401, resp.text
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


async def test_endpoint_twilio_no_acepta_secreto_por_query():
    """El secreto por query no autentica a Twilio (que no puede enviarlo)."""
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            f"/api/v1/cost-guard/twilio/voice?secret={_GUARD_SECRET}",
            data=params,
        )
    assert resp.status_code == 401, resp.text


async def test_endpoint_twilio_acepta_firma_valida_sin_secreto():
    """B1: Twilio no puede enviar X-Cost-Guard-Secret; la firma basta."""
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")


def test_postura_advierte_si_falta_el_secreto_compartido():
    config = make_config(shared_secret_configured=False)
    with patch("app.cost_guard.posture.logger") as mock_logger:
        log_cost_guard_posture(config)

    warned = [
        c for c in mock_logger.warning.call_args_list
        if c.args and c.args[0] == EVENT_COST_GUARD_SECRET_MISSING
    ]
    assert warned, "debe advertirse que falta el secreto compartido"


def test_postura_advierte_si_falta_el_token_de_twilio():
    """B1: sin TWILIO_AUTH_TOKEN el webhook de voz queda cerrado; se advierte."""
    config = make_config(twilio_auth_token_configured=False)
    with patch("app.cost_guard.posture.logger") as mock_logger:
        log_cost_guard_posture(config)

    warned = [
        c for c in mock_logger.warning.call_args_list
        if c.args and c.args[0] == EVENT_COST_GUARD_TWILIO_TOKEN_MISSING
    ]
    assert warned, "debe advertirse que falta el token de Twilio"


# ── 16.2 — fail_open y alert_enabled reales (Warning 2) ─────────────────────


async def test_store_caido_fail_open_permite_la_llamada():
    guard = make_guard(
        store=_UnavailableStore(),  # type: ignore[arg-type]
        store_failure_policy="fail_open",
    )
    with patch("app.cost_guard.guard.logger"):
        decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is True


async def test_store_caido_fail_closed_sigue_siendo_el_default():
    guard = make_guard(store=_UnavailableStore())  # type: ignore[arg-type]
    with patch("app.cost_guard.guard.logger"):
        decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is False
    assert decision.cause == CAUSE_STORE_UNAVAILABLE


async def test_alert_enabled_controla_la_notificacion_externa():
    notifier = AsyncMock()
    notifier.notify = AsyncMock()
    guard = make_guard(
        store=_UnavailableStore(),  # type: ignore[arg-type]
        alert_notifier=notifier,
    )
    with patch("app.cost_guard.guard.logger"):
        await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    notifier.notify.assert_awaited_once()


async def test_alert_disabled_no_emite_notificacion_externa():
    notifier = AsyncMock()
    notifier.notify = AsyncMock()
    guard = make_guard(
        store=_UnavailableStore(),  # type: ignore[arg-type]
        alert_notifier=notifier,
        alert_enabled=False,
    )
    with patch("app.cost_guard.guard.logger"):
        await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    notifier.notify.assert_not_awaited()


async def test_notificacion_externa_no_altera_la_decision_si_falla():
    notifier = AsyncMock()
    notifier.notify = AsyncMock(side_effect=RuntimeError("webhook caido"))
    guard = make_guard(
        store=_UnavailableStore(),  # type: ignore[arg-type]
        alert_notifier=notifier,
    )
    with patch("app.cost_guard.guard.logger"):
        decision = await guard.evaluate(PROVIDER_BACKEND_GEMINI)
    assert decision.allowed is False
    assert decision.cause == CAUSE_STORE_UNAVAILABLE


# ── 16.3 — Firma de Twilio (Warning 3) ──────────────────────────────────────


def test_compute_signature_coincide_con_vector_de_twilio():
    """Vector oficial del SDK twilio-python (tests/unit/test_request_validator)."""
    token = "12345"
    uri = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {
        "CallSid": "CA1234567890ABCDE",
        "Digits": "1234",
        "From": "+14158675309",
        "To": "+18005551212",
        "Caller": "+14158675309",
    }
    assert compute_signature(token, uri, params) == "RSOYDt4T1cUTdK1PDd93/VVr8B8="


async def test_twilio_webhook_rechaza_firma_invalida():
    guard = make_guard()
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data={"From": "+5492615551234", "To": "+5492615550000"},
            headers={"X-Twilio-Signature": "firma-invalida"},
        )
    assert resp.status_code == 401, resp.text


async def test_twilio_webhook_acepta_firma_valida():
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_twilio_headers(params),
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")


async def test_twilio_webhook_sin_token_queda_cerrado():
    """B1: sin TWILIO_AUTH_TOKEN el webhook no queda abierto (fail-closed).

    Antes de cargar la credencial Twilio no esta configurado para llamar al
    endpoint, por lo que rechazar con 401 no rompe el flujo; al cargar
    `TWILIO_AUTH_TOKEN` la validacion de firma se activa sin otro cambio.
    """
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    async with _client_with_guard(guard, twilio_auth_token="") as client:
        con_secreto = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers=_guard_headers(),
        )
        sin_headers = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
        )
    assert con_secreto.status_code == 401, con_secreto.text
    assert sin_headers.status_code == 401, sin_headers.text


async def test_twilio_webhook_rechaza_firma_de_otra_url():
    """Triangulacion B1: una firma valida de OTRA URL no autentica.

    Cubre el caveat de proxy: si la URL reconstruida no coincide con la URL
    publica configurada en Twilio, la firma no valida y la peticion es 401.
    """
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    firma_ajena = compute_signature(
        _TWILIO_TOKEN,
        "https://otro-host.example/api/v1/cost-guard/twilio/voice",
        params,
    )
    async with _client_with_guard(guard, twilio_auth_token=_TWILIO_TOKEN) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers={"X-Twilio-Signature": firma_ajena},
        )
    assert resp.status_code == 401, resp.text


# ── Helpers de test ─────────────────────────────────────────────────────────


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


@asynccontextmanager
async def _client_with_guard(
    guard: CostGuard,
    secret: str = _GUARD_SECRET,
    twilio_auth_token: str = "",
    proxy_trusted_hosts: str | None = None,
):
    app = create_app()
    app.dependency_overrides[get_cost_guard] = lambda: guard
    asgi_app: Any = app
    if proxy_trusted_hosts is not None:
        # Reproduce el middleware con el que Uvicorn honra X-Forwarded-Proto
        # cuando FORWARDED_ALLOW_IPS incluye al cliente que reenvia (W1).
        asgi_app = ProxyHeadersMiddleware(app, trusted_hosts=proxy_trusted_hosts)
    settings = _settings(
        cost_guard_shared_secret=secret,
        twilio_auth_token=twilio_auth_token,
    )
    with patch("app.routes.cost_guard.get_settings", return_value=settings):
        async with AsyncClient(
            transport=ASGITransport(app=asgi_app), base_url="http://test"
        ) as client:
            yield client


# ── 18. Cierre W1/W2 (post post-verify) ─────────────────────────────────────
#
# W1: el backend reconstruia `request.url` con esquema http detras del Nginx del
#     stack Docker (Uvicorn no confiaba en X-Forwarded-Proto, que llega desde
#     una IP del bridge). El fix es que Uvicorn confie en los headers reenviados
#     (FORWARDED_ALLOW_IPS); es seguro porque el puerto 8000 NO se publica y
#     Nginx sobreescribe X-Forwarded-Proto con $scheme. Los tests derivan el
#     valor de confianza de docker-compose.yml y lo aplican con el MISMO
#     middleware de Uvicorn, de modo que prueban el cableado real.
#
# W2: el OpenAPI generado declaraba application/json para el 200 de TwiML y
#     omitia el 401 de ambos endpoints de guarda.

_PUBLIC_TWILIO_URL = "https://test/api/v1/cost-guard/twilio/voice"


def _backend_forwarded_allow_ips() -> str:
    """Valor de confianza del proxy resuelto desde docker-compose.yml.

    Soporta tanto el literal (`*`) como la interpolacion con default
    (`${FORWARDED_ALLOW_IPS:-*}`); en este ultimo caso devuelve el default.
    """
    compose = yaml.safe_load(_COMPOSE_FILE.read_text(encoding="utf-8"))
    env = compose["services"]["backend"]["environment"]
    assert "FORWARDED_ALLOW_IPS" in env, (
        "el servicio backend debe definir FORWARDED_ALLOW_IPS para que Uvicorn "
        "confie en X-Forwarded-Proto del proxy Nginx"
    )
    raw = str(env["FORWARDED_ALLOW_IPS"])
    match = re.fullmatch(r"\$\{[A-Z_]+:-([^}]*)\}", raw)
    return match.group(1) if match else raw


def test_compose_backend_confia_en_los_headers_del_proxy():
    """W1: el backend confia en los headers reenviados por el proxy del compose."""
    trusted = _backend_forwarded_allow_ips()
    assert trusted == "*", (
        "el backend no publica el puerto 8000 (solo Nginx expone 80/443) y Nginx "
        "sobreescribe X-Forwarded-Proto; confiar en '*' es seguro y necesario "
        f"para reconstruir https. Valor actual: {trusted!r}"
    )


async def test_twilio_firma_https_valida_con_headers_del_proxy():
    """W1: con X-Forwarded-Proto=https confiable, la firma sobre la URL publica valida."""
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    trusted = _backend_forwarded_allow_ips()
    firma = compute_signature(_TWILIO_TOKEN, _PUBLIC_TWILIO_URL, params)
    async with _client_with_guard(
        guard,
        twilio_auth_token=_TWILIO_TOKEN,
        proxy_trusted_hosts=trusted,
    ) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers={
                "X-Twilio-Signature": firma,
                "X-Forwarded-Proto": "https",
            },
        )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/xml")


async def test_twilio_firma_http_no_valida_cuando_el_proxy_declara_https():
    """W1 (triangulacion): la firma sobre http:// NO valida si el proxy declara https.

    Demuestra que el esquema reconstruido es el que determina la firma: una URL
    http no autentica cuando la URL publica real es https.
    """
    guard = make_guard()
    params = {"From": "+5492615551234", "To": "+5492615550000"}
    trusted = _backend_forwarded_allow_ips()
    firma_http = compute_signature(
        _TWILIO_TOKEN, "http://test/api/v1/cost-guard/twilio/voice", params
    )
    async with _client_with_guard(
        guard,
        twilio_auth_token=_TWILIO_TOKEN,
        proxy_trusted_hosts=trusted,
    ) as client:
        resp = await client.post(
            "/api/v1/cost-guard/twilio/voice",
            data=params,
            headers={
                "X-Twilio-Signature": firma_http,
                "X-Forwarded-Proto": "https",
            },
        )
    assert resp.status_code == 401, resp.text


# W2 — OpenAPI generado


def _cost_guard_openapi() -> dict:
    app = create_app()
    app.openapi_schema = None
    return app.openapi()


def test_openapi_twilio_voice_200_declara_text_xml():
    """W2: el 200 del webhook TwiML se documenta con el media type real."""
    schema = _cost_guard_openapi()
    op = schema["paths"]["/api/v1/cost-guard/twilio/voice"]["post"]
    content = op["responses"]["200"]["content"]
    assert "text/xml" in content, (
        f"el 200 del webhook de Twilio debe declarar text/xml; actual: {list(content)}"
    )
    assert "application/json" not in content, (
        "el webhook de Twilio NO devuelve JSON; no debe declarar application/json"
    )


def test_openapi_endpoints_de_guarda_declaran_401():
    """W2: ambos endpoints de guarda declaran el 401 que realmente pueden devolver."""
    schema = _cost_guard_openapi()
    for path in (
        "/api/v1/cost-guard/reserve",
        "/api/v1/cost-guard/twilio/voice",
    ):
        op = schema["paths"][path]["post"]
        assert "401" in op["responses"], (
            f"{path} debe declarar la respuesta 401 (auth fallida o no configurada)"
        )