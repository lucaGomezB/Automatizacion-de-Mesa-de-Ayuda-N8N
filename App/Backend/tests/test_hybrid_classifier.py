"""
Tests unitarios del clasificador híbrido (pipeline determinístico + Gemini).

C-27: el DTO expone `sector_predicho` (+ `sectores_adicionales`) en lugar de
`categoria`.

Casos cubiertos:
    - Cortocircuito: confianza determinística >= 0.90 → Gemini no es invocado.
    - Escalada: confianza determinística < 0.90 → Gemini es consultado.
    - Fallback: Gemini lanza GeminiUnavailableError → resultado de emergencia.
    - Revisión humana: confianza de Gemini < 0.70 → requiere_revision_humana=True.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.classifiers.hybrid import HybridClassifier
from app.constants import SECTORES_CANONICOS
from app.core.exceptions import GeminiUnavailableError
from app.schemas.clasificacion import ClasificacionResult


def _det_result(sector_predicho: str, confianza: float) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=False,
    )


def _gemini_result(sector_predicho: str, confianza: float) -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa="gemini",
        requiere_revision_humana=confianza < 0.70,
        respuesta_raw=f'{{"categoría": "{sector_predicho}", "confianza": {confianza}}}',
    )


@pytest.mark.asyncio
async def test_short_circuit_when_deterministic_confident() -> None:
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 0.95),
    ), patch.object(
        classifier._gemini, "classify", new_callable=AsyncMock
    ) as mock_gemini:
        result = await classifier.classify("Se cayó el servidor de red")
        assert result.etapa == "deterministic"
        assert result.sector_predicho == "Sistemas"
        mock_gemini.assert_not_called()


@pytest.mark.asyncio
async def test_escalates_to_gemini_when_low_confidence() -> None:
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Bases de Datos", 0.55),
    ), patch.object(
        classifier._gemini,
        "classify",
        new_callable=AsyncMock,
        return_value=_gemini_result("Sistemas", 0.88),
    ):
        result = await classifier.classify("Descripción ambigua")
        assert result.etapa == "gemini"
        assert result.sector_predicho == "Sistemas"
        assert result.requiere_revision_humana is False


@pytest.mark.asyncio
async def test_fallback_on_gemini_unavailable() -> None:
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Soporte Tecnico Hardware", 0.60),
    ), patch.object(
        classifier._gemini,
        "classify",
        side_effect=GeminiUnavailableError("API down"),
    ):
        result = await classifier.classify("Descripción ambigua")
        assert result.etapa == "fallback"
        assert result.confianza == 0.0
        assert result.requiere_revision_humana is True
        assert result.sector_predicho in SECTORES_CANONICOS


@pytest.mark.asyncio
async def test_human_review_flagged_when_gemini_low_confidence() -> None:
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Seguridad Informatica", 0.50),
    ), patch.object(
        classifier._gemini,
        "classify",
        new_callable=AsyncMock,
        return_value=_gemini_result("Seguridad Informatica", 0.55),
    ):
        result = await classifier.classify("Descripción poco clara")
        assert result.requiere_revision_humana is True


def test_cache_version_es_unica_fuente_compartida() -> None:
    """W-3: la version del cache vive en app.constants y HybridClassifier la reusa.

    El runner de evaluacion lee esta constante sin importar app.classifiers
    (que arrastra get_settings); la unicidad evita que la version derive.
    """
    from app.constants import HYBRID_CACHE_VERSION

    assert isinstance(HYBRID_CACHE_VERSION, str) and HYBRID_CACHE_VERSION
    assert HybridClassifier.CACHE_VERSION == HYBRID_CACHE_VERSION


# ---------------------------------------------------------------------------
# c-58 — Politica de reserva: una sola evaluacion dimensionada al peor caso
# ---------------------------------------------------------------------------
class _RecordingGuard:
    """Guarda de costo falsa que registra cada evaluacion (provider + amount)."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def evaluate(self, provider, caller=None, amount=1):
        from app.cost_guard.decision import GuardDecision

        self.calls.append({"provider": provider, "caller": caller, "amount": amount})
        return GuardDecision(allowed=True, cause=None)


@pytest.mark.asyncio
async def test_guarda_recibe_amount_del_peor_caso_y_una_sola_evaluacion() -> None:
    """
    c-58 (D4): al escalar a Gemini, la guarda recibe `amount == gemini_max_retries + 1`
    y se evalua UNA sola vez por clasificacion. Los reintentos no reservan de nuevo.
    """
    from app.config.settings import get_settings

    guard = _RecordingGuard()
    classifier = HybridClassifier(
        deterministic=None,
        gemini=None,
        cost_guard=guard,
    )
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
        result = await classifier.classify("Descripcion ambigua")

    assert result.etapa == "gemini"
    assert len(guard.calls) == 1, "la guarda debe evaluarse una sola vez"
    assert guard.calls[0]["amount"] == get_settings().gemini_max_retries + 1


@pytest.mark.asyncio
async def test_guarda_no_reserva_en_el_cortocircuito_deterministico() -> None:
    """c-58: el cortocircuito determinista no consulta la guarda (sin reserva)."""
    guard = _RecordingGuard()
    classifier = HybridClassifier(gemini=None, cost_guard=guard)
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 0.98),
    ):
        result = await classifier.classify("Se cayo el servidor")

    assert result.etapa == "deterministic"
    assert guard.calls == []
