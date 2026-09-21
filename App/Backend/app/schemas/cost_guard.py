"""
Schemas Pydantic de la guarda de costo en runtime (c-45).

Contratos HTTP del endpoint de reserva que consume n8n antes de invocar al
AI Agent. El proveedor esta restringido a las superficies pagas conocidas.
"""

from typing import Literal

from pydantic import BaseModel, Field


class CostGuardReserveRequest(BaseModel):
    """Solicitud de reserva de una llamada paga de la superficie n8n."""

    provider: Literal["n8n_gemini"] = "n8n_gemini"
    caller: str | None = Field(
        default=None,
        max_length=32,
        description="Numero de origen CRUDO cuando esta disponible (telefonia).",
    )


class CostGuardReserveResponse(BaseModel):
    """Decision de la guarda: permitir o denegar con causa."""

    allowed: bool
    cause: str | None = None
    provider: str


__all__ = ["CostGuardReserveRequest", "CostGuardReserveResponse"]
