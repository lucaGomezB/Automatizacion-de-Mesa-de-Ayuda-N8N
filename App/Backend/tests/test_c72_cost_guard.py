"""
Tests c-72 (Section 4): traslado de la superficie de costo.

Contratos (design D5, spec runtime-cost-guard, OQ2=A):
    - La clasificacion telefonica NO reserva la superficie `n8n_gemini`: el
      workflow no invoca la guarda de costo para clasificar telefonia.
    - Cuando la cascada del backend escala a la semantica, la reserva es
      `backend_gemini` conforme al enforcement vigente.
    - Guarda denegando: fallback con revision humana, sin invocar al proveedor.

Estructura TDD:
    - 4.1 RED: telefonia no reserva n8n_gemini + escalacion reserva backend_gemini.
    - 4.2 GREEN: se retira la reserva n8n_gemini del workflow.
    - 4.3 TRIANGULATE: cortocircuito (sin reserva), escalacion permitida
      (backend_gemini) y guarda denegando (fallback con revision humana).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.classifiers.hybrid import HybridClassifier
from app.cost_guard.constants import PROVIDER_BACKEND_GEMINI
from app.cost_guard.decision import GuardDecision
from app.schemas.clasificacion import ClasificacionResult

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"

COST_GUARD_RESERVE_PATH = "/api/v1/cost-guard/reserve"
N8N_GEMINI = "n8n_gemini"


def load_workflow() -> dict:
    with WORKFLOW_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _det_result(sector: str, confianza: float) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho=sector,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=False,
    )


def _gemini_result(sector: str, confianza: float) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho=sector,
        confianza=confianza,
        etapa="gemini",
        requiere_revision_humana=confianza < 0.70,
        respuesta_raw=f'{{"categoría": "{sector}", "confianza": {confianza}}}',
    )


class _RecordingGuard:
    """Guarda falsa que registra cada evaluacion (provider + amount)."""

    def __init__(self, allowed: bool = True, cause: str | None = None) -> None:
        self.calls: list[dict] = []
        self._allowed = allowed
        self._cause = cause

    async def evaluate(self, provider, caller=None, amount=1):
        self.calls.append({"provider": provider, "caller": caller, "amount": amount})
        return GuardDecision(allowed=self._allowed, cause=self._cause)


# ---------------------------------------------------------------------------
# 4.1 RED — el workflow no reserva n8n_gemini
# ---------------------------------------------------------------------------


def test_4_1_workflow_no_reserva_n8n_gemini():
    """
    Ningun nodo del workflow reserva la superficie `n8n_gemini`: la clasificacion
    telefonica dejo de pasar por la guarda de n8n.
    """
    wf = load_workflow()
    blob = json.dumps(wf, ensure_ascii=False)
    assert N8N_GEMINI not in blob, (
        "El workflow todavia referencia 'n8n_gemini': la telefonia reservaria la "
        "superficie paga de n8n"
    )
    offenders = [
        node["name"]
        for node in wf["nodes"]
        if COST_GUARD_RESERVE_PATH in str(node.get("parameters", {}).get("url", ""))
    ]
    assert offenders == [], (
        f"Nodos que invocan la guarda de costo en n8n: {offenders}. La clasificacion "
        "telefonica no debe reservar n8n_gemini."
    )


# ---------------------------------------------------------------------------
# 4.1/4.3 — la escalacion del backend reserva backend_gemini
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_4_1_escalacion_reserva_backend_gemini():
    """La cascada que escala a la semantica reserva la superficie `backend_gemini`."""
    guard = _RecordingGuard(allowed=True)
    classifier = HybridClassifier(gemini=None, cost_guard=guard)
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 0.55),
    ), patch.object(
        classifier._gemini,
        "classify",
        new_callable=AsyncMock,
        return_value=_gemini_result("Sistemas", 0.88),
    ):
        result = await classifier.classify("Descripcion ambigua de telefonia")

    assert result.etapa == "gemini"
    assert len(guard.calls) == 1
    assert guard.calls[0]["provider"] == PROVIDER_BACKEND_GEMINI, (
        f"La escalacion reservo {guard.calls[0]['provider']!r} en vez de backend_gemini"
    )


@pytest.mark.asyncio
async def test_4_3_cortocircuito_deterministico_no_reserva():
    """El cortocircuito determinista de telefonia no reserva ninguna superficie."""
    guard = _RecordingGuard(allowed=True)
    classifier = HybridClassifier(gemini=None, cost_guard=guard)
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 1.0),
    ):
        result = await classifier.classify("Se cayo el servidor")

    assert result.etapa == "deterministic"
    assert guard.calls == [], (
        "El cortocircuito deterministico no debe reservar presupuesto"
    )


@pytest.mark.asyncio
async def test_4_3_guarda_deniega_degrada_a_fallback_con_revision_humana():
    """
    Si la guarda deniega la reserva `backend_gemini`, la cascada degrada a
    fallback con revision humana sin invocar al proveedor pago.
    """
    guard = _RecordingGuard(allowed=False, cause="budget")
    classifier = HybridClassifier(gemini=None, cost_guard=guard)
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 0.55),
    ), patch.object(
        classifier._gemini, "classify", new_callable=AsyncMock
    ) as mock_gemini:
        result = await classifier.classify("Descripcion ambigua")

    assert guard.calls[0]["provider"] == PROVIDER_BACKEND_GEMINI
    assert result.etapa == "fallback"
    assert result.requiere_revision_humana is True
    mock_gemini.assert_not_called()