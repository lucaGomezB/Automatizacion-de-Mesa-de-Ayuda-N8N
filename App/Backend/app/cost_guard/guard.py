"""
Fachada de la guarda de costo en runtime.

Orquesta la reserva atomica en el almacen, la decision pura, el commit/rollback
y la observabilidad estructurada. El almacen y el reloj se inyectan, de modo que
la guarda es determinista y evaluable offline.

Flujo de una evaluacion:
    1. Si la guarda esta deshabilitada, permite sin tocar el almacen.
    2. Calcula las ventanas (presupuesto, tasa global y tasa por origen) y arma
       las reservas: bolsa global, tasa global, superficie y (si hay) caller.
    3. Reserva en el almacen (transaccion propia). Ante error: aplica
       `store_failure_policy` (default `fail_closed`; `fail_open` permite la
       llamada sin tope) y emite el evento mas la notificacion externa opcional.
    4. Evalua la decision pura sobre los contadores resultantes.
    5. Commit si permite; rollback si deniega (la reserva no cuenta).
    6. Purga las ventanas vencidas del contador de origen.
"""

from datetime import datetime
from decimal import Decimal

from app.core.logging import get_logger
from app.cost_guard.alerts import AlertNotifier
from app.cost_guard.config import CostGuardConfig
from app.cost_guard.constants import (
    AMBITO_CALLER,
    AMBITO_GLOBAL,
    AMBITO_SURFACE,
    CAUSE_BUDGET,
    CAUSE_CALLER_RATE,
    CAUSE_RATE,
    CAUSE_STORE_UNAVAILABLE,
    EVENT_COST_GUARD_STORE_UNAVAILABLE,
    EVENT_COST_GUARD_TRIPPED,
)
from app.cost_guard.decision import (
    GuardCounters,
    GuardDecision,
    evaluate_counters,
    window_start,
)
from app.cost_guard.protocols import (
    Clock,
    CounterKey,
    CounterSnapshot,
    CounterStore,
    Reservation,
)

logger = get_logger(__name__)

_ZERO = Decimal("0")

# Rol de cada reserva dentro de la evaluacion (alineado con el orden de armado).
_ROLE_BUDGET = "budget"
_ROLE_RATE = "rate"
_ROLE_SURFACE = "surface"
_ROLE_CALLER = "caller"

# Politica de fallo del almacen. Cualquier valor distinto de fail_open se trata
# como fail_closed (el default seguro documentado).
_POLICY_FAIL_OPEN = "fail_open"


class CostGuard:
    """Enforcement de costo con almacen y reloj inyectables."""

    def __init__(
        self,
        store: CounterStore,
        clock: Clock,
        config: CostGuardConfig,
        alert_notifier: AlertNotifier | None = None,
    ) -> None:
        self._store = store
        self._clock = clock
        self._config = config
        self._alert_notifier = alert_notifier

    # ── API publica ──────────────────────────────────────────────────────────

    async def evaluate(
        self, provider: str, caller: str | None = None
    ) -> GuardDecision:
        """
        Evalua la guarda antes de una llamada paga.

        Args:
            provider: superficie paga (una de `PAID_PROVIDERS`).
            caller: numero de origen CRUDO cuando esta disponible (telefonia).

        Returns:
            GuardDecision permitida o denegada con causa.
        """
        if not self._config.enabled:
            return GuardDecision(allowed=True, cause=None)

        now = self._clock.now()
        unit_cost = self._config.unit_cost(provider)
        reservations, roles, windows = self._build_reservations(
            provider, caller, now, unit_cost
        )

        try:
            snapshots = await self._store.reserve_many(reservations)
        except Exception as exc:  # politica configurable; default fail-closed
            await self._safe_rollback()
            self._log_store_unavailable(provider, caller, windows, exc)
            await self._notify_store_unavailable(provider, windows, exc)
            if self._config.store_failure_policy == _POLICY_FAIL_OPEN:
                return GuardDecision(allowed=True, cause=None)
            return GuardDecision(allowed=False, cause=CAUSE_STORE_UNAVAILABLE)

        counters = self._extract_counters(snapshots, roles)
        decision = evaluate_counters(counters, self._config.limits())

        if decision.allowed:
            await self._store.commit()
        else:
            await self._store.rollback()
            self._log_tripped(decision.cause, provider, caller, windows)

        await self._purge_expired_windows(now)
        return decision

    # ── Armado de reservas ───────────────────────────────────────────────────

    def _build_reservations(
        self,
        provider: str,
        caller: str | None,
        now: datetime,
        unit_cost: Decimal,
    ) -> tuple[list[Reservation], list[str], dict[str, datetime]]:
        budget_window = window_start(now, self._config.budget_window_seconds)
        rate_window = window_start(now, self._config.rate_window_seconds)
        caller_window = window_start(now, self._config.caller_rate_window_seconds)

        reservations = [
            Reservation(
                key=CounterKey(AMBITO_GLOBAL, "budget", budget_window),
                calls_delta=1,
                cost_delta=unit_cost,
            ),
            Reservation(
                key=CounterKey(AMBITO_GLOBAL, "rate", rate_window),
                calls_delta=1,
                cost_delta=_ZERO,
            ),
            Reservation(
                key=CounterKey(AMBITO_SURFACE, provider, budget_window),
                calls_delta=1,
                cost_delta=unit_cost,
            ),
        ]
        roles = [_ROLE_BUDGET, _ROLE_RATE, _ROLE_SURFACE]

        if caller:
            reservations.append(
                Reservation(
                    key=CounterKey(AMBITO_CALLER, caller, caller_window),
                    calls_delta=1,
                    cost_delta=_ZERO,
                )
            )
            roles.append(_ROLE_CALLER)

        windows = {
            "budget": budget_window,
            "rate": rate_window,
            "caller_rate": caller_window,
        }
        return reservations, roles, windows

    @staticmethod
    def _extract_counters(
        snapshots: list[CounterSnapshot], roles: list[str]
    ) -> GuardCounters:
        by_role = dict(zip(roles, snapshots))
        budget = by_role[_ROLE_BUDGET]
        rate = by_role[_ROLE_RATE]
        caller_snapshot = by_role.get(_ROLE_CALLER)
        return GuardCounters(
            budget_cost_usd=budget.costo_usd,
            rate_calls=rate.llamadas,
            caller_calls=caller_snapshot.llamadas if caller_snapshot else None,
        )

    # ── Purga de ventanas vencidas ───────────────────────────────────────────

    async def _purge_expired_windows(self, now: datetime) -> None:
        """
        Purga los contadores de origen de ventanas vencidas.

        Acota la retencion del numero de origen CRUDO a la ventana del rate por
        origen. Es best-effort: un fallo de purga nunca altera la decision.
        """
        before = window_start(now, self._config.caller_rate_window_seconds)
        try:
            await self._store.purge_expired(AMBITO_CALLER, before)
        except Exception as exc:  # pragma: no cover - defensa
            logger.warning("cost_guard_purge_failed", error_class=type(exc).__name__)

    async def _safe_rollback(self) -> None:
        try:
            await self._store.rollback()
        except Exception:  # pragma: no cover - defensa
            pass

    # ── Observabilidad ───────────────────────────────────────────────────────

    def _log_tripped(
        self,
        cause: str | None,
        provider: str,
        caller: str | None,
        windows: dict[str, datetime],
    ) -> None:
        limit, window = self._limit_and_window(cause, windows)
        logger.warning(
            EVENT_COST_GUARD_TRIPPED,
            cause=cause,
            provider=provider,
            window=window.isoformat(),
            limit=limit,
            caller=caller,
        )

    def _log_store_unavailable(
        self,
        provider: str,
        caller: str | None,
        windows: dict[str, datetime],
        exc: Exception,
    ) -> None:
        logger.error(
            EVENT_COST_GUARD_STORE_UNAVAILABLE,
            cause=CAUSE_STORE_UNAVAILABLE,
            provider=provider,
            window=windows["budget"].isoformat(),
            limit=str(self._config.budget_usd),
            caller=caller,
            error_class=type(exc).__name__,
        )

    async def _notify_store_unavailable(
        self,
        provider: str,
        windows: dict[str, datetime],
        exc: Exception,
    ) -> None:
        """
        Emite la notificacion EXTERNA del almacen caido (best-effort).

        El evento estructurado `cost_guard_store_unavailable` se emite siempre
        (requisito de observabilidad); esta notificacion es adicional y queda
        controlada por `cost_guard_alert_enabled`. Su fallo nunca altera la
        decision de la guarda.
        """
        if not self._config.alert_enabled or self._alert_notifier is None:
            return
        try:
            await self._alert_notifier.notify(
                EVENT_COST_GUARD_STORE_UNAVAILABLE,
                cause=CAUSE_STORE_UNAVAILABLE,
                provider=provider,
                window=windows["budget"].isoformat(),
                limit=str(self._config.budget_usd),
                error_class=type(exc).__name__,
            )
        except Exception as alert_exc:  # best-effort: nunca propaga
            logger.warning(
                "cost_guard_alert_failed",
                error_class=type(alert_exc).__name__,
            )

    def _limit_and_window(
        self, cause: str | None, windows: dict[str, datetime]
    ) -> tuple[str, datetime]:
        if cause == CAUSE_BUDGET:
            return str(self._config.budget_usd), windows["budget"]
        if cause == CAUSE_RATE:
            return str(self._config.rate_limit_calls), windows["rate"]
        if cause == CAUSE_CALLER_RATE:
            return str(self._config.caller_rate_limit_calls), windows["caller_rate"]
        return str(self._config.budget_usd), windows["budget"]


__all__ = ["CostGuard"]
