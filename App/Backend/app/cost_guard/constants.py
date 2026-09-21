"""
Constantes canonicas de la guarda de costo en runtime.

Centraliza los nombres de superficies pagas, causas de disparo, ambitos de
contadores y nombres de eventos estructurados, para que la decision pura, el
adaptador de almacen y los endpoints compartan el mismo vocabulario estable.
"""

from typing import Final

# ── Superficies pagas ────────────────────────────────────────────────────────
PROVIDER_BACKEND_GEMINI: Final[str] = "backend_gemini"
PROVIDER_N8N_GEMINI: Final[str] = "n8n_gemini"
PROVIDER_TWILIO: Final[str] = "twilio"

PAID_PROVIDERS: Final[tuple[str, ...]] = (
    PROVIDER_BACKEND_GEMINI,
    PROVIDER_N8N_GEMINI,
    PROVIDER_TWILIO,
)

# ── Causas de disparo / denegacion ───────────────────────────────────────────
CAUSE_BUDGET: Final[str] = "budget"
CAUSE_RATE: Final[str] = "rate"
CAUSE_CALLER_RATE: Final[str] = "caller_rate"
CAUSE_STORE_UNAVAILABLE: Final[str] = "store_unavailable"

# ── Ambitos de contador ──────────────────────────────────────────────────────
AMBITO_GLOBAL: Final[str] = "global"
AMBITO_SURFACE: Final[str] = "surface"
AMBITO_CALLER: Final[str] = "caller"

# ── Eventos estructurados ────────────────────────────────────────────────────
EVENT_COST_GUARD_TRIPPED: Final[str] = "cost_guard_tripped"
EVENT_COST_GUARD_STORE_UNAVAILABLE: Final[str] = "cost_guard_store_unavailable"
EVENT_COST_GUARD_POSTURE: Final[str] = "cost_guard_posture"
EVENT_COST_GUARD_SECRET_MISSING: Final[str] = "cost_guard_secret_missing"
EVENT_COST_GUARD_TWILIO_TOKEN_MISSING: Final[str] = "cost_guard_twilio_token_missing"

__all__ = [
    "PROVIDER_BACKEND_GEMINI",
    "PROVIDER_N8N_GEMINI",
    "PROVIDER_TWILIO",
    "PAID_PROVIDERS",
    "CAUSE_BUDGET",
    "CAUSE_RATE",
    "CAUSE_CALLER_RATE",
    "CAUSE_STORE_UNAVAILABLE",
    "AMBITO_GLOBAL",
    "AMBITO_SURFACE",
    "AMBITO_CALLER",
    "EVENT_COST_GUARD_TRIPPED",
    "EVENT_COST_GUARD_STORE_UNAVAILABLE",
    "EVENT_COST_GUARD_POSTURE",
    "EVENT_COST_GUARD_SECRET_MISSING",
    "EVENT_COST_GUARD_TWILIO_TOKEN_MISSING",
]
