"""
Configuracion derivada de la guarda de costo.

`CostGuardConfig` es un objeto inmutable con los valores ya normalizados
(Decimal para montos, mapa de costos unitarios por superficie) que consume la
guarda. `from_settings` lo deriva de `Settings`, manteniendo los defaults
conservadores documentados en un unico lugar canonico.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from app.cost_guard.constants import (
    PROVIDER_BACKEND_GEMINI,
    PROVIDER_BACKEND_STT,
    PROVIDER_N8N_GEMINI,
    PROVIDER_TWILIO,
)
from app.cost_guard.decision import GuardLimits


@dataclass(frozen=True)
class CostGuardConfig:
    """
    Parametros efectivos de la guarda.

    Los costos unitarios son ESTIMACIONES configurables, no contabilidad exacta:
    el objetivo es acotar el gasto con un tope determinista, no medir tokens ni
    duraciones reales.
    """

    enabled: bool
    budget_usd: Decimal
    budget_window_seconds: int
    rate_limit_calls: int
    rate_window_seconds: int
    caller_rate_limit_calls: int
    caller_rate_window_seconds: int
    unit_costs_usd: Mapping[str, Decimal]
    degradation_policy: str
    store_failure_policy: str
    alert_enabled: bool = True
    shared_secret_configured: bool = False
    twilio_auth_token_configured: bool = False

    def unit_cost(self, provider: str) -> Decimal:
        """Costo unitario configurado para la superficie paga indicada."""
        try:
            return self.unit_costs_usd[provider]
        except KeyError as exc:
            raise ValueError(f"Superficie paga desconocida: {provider!r}") from exc

    def limits(self) -> GuardLimits:
        """Limites evaluados por la funcion de decision pura."""
        return GuardLimits(
            budget_usd=self.budget_usd,
            rate_limit_calls=self.rate_limit_calls,
            caller_rate_limit_calls=self.caller_rate_limit_calls,
        )

    @classmethod
    def from_settings(cls, settings: object) -> "CostGuardConfig":
        """Deriva la configuracion efectiva desde `Settings`."""
        return cls(
            enabled=getattr(settings, "cost_guard_enabled"),
            budget_usd=Decimal(str(getattr(settings, "cost_guard_budget_usd"))),
            budget_window_seconds=int(
                getattr(settings, "cost_guard_budget_window_seconds")
            ),
            rate_limit_calls=int(getattr(settings, "cost_guard_rate_limit_calls")),
            rate_window_seconds=int(
                getattr(settings, "cost_guard_rate_window_seconds")
            ),
            caller_rate_limit_calls=int(
                getattr(settings, "cost_guard_caller_rate_limit_calls")
            ),
            caller_rate_window_seconds=int(
                getattr(settings, "cost_guard_caller_rate_window_seconds")
            ),
            unit_costs_usd={
                PROVIDER_BACKEND_GEMINI: Decimal(
                    str(getattr(settings, "cost_guard_unit_cost_backend_gemini_usd"))
                ),
                PROVIDER_N8N_GEMINI: Decimal(
                    str(getattr(settings, "cost_guard_unit_cost_n8n_gemini_usd"))
                ),
                PROVIDER_TWILIO: Decimal(
                    str(
                        getattr(
                            settings,
                            "cost_guard_unit_cost_twilio_transcription_usd",
                        )
                    )
                ),
                PROVIDER_BACKEND_STT: Decimal(
                    str(getattr(settings, "cost_guard_unit_cost_backend_stt_usd"))
                ),
            },
            degradation_policy=str(
                getattr(settings, "cost_guard_degradation_policy")
            ),
            store_failure_policy=str(
                getattr(settings, "cost_guard_store_failure_policy")
            ),
            alert_enabled=bool(getattr(settings, "cost_guard_alert_enabled")),
            shared_secret_configured=bool(
                getattr(settings, "cost_guard_shared_secret")
            ),
            twilio_auth_token_configured=bool(
                getattr(settings, "twilio_auth_token")
            ),
        )


__all__ = ["CostGuardConfig"]
