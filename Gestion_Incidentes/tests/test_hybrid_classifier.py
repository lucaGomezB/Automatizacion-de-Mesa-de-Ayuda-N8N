"""
Tests unitarios del clasificador híbrido (pipeline determinístico + Gemini).

Responsabilidad:
    Verifica el comportamiento del HybridClassifier ante los cuatro escenarios
    principales del pipeline de clasificación: cortocircuito por alta confianza
    determinística, escalada a Gemini, fallback por error de Gemini, y marcado
    de revisión humana por baja confianza semántica.

    El clasificador de Gemini es reemplazado por un mock (AsyncMock/side_effect)
    para garantizar que los tests sean deterministas, rápidos y no dependan
    de conectividad de red ni de créditos de API. El clasificador determinístico
    también es mockeado para controlar con precisión su confianza de salida.

    La combinación de ambos mocks permite aislar exclusivamente la lógica
    de orquestación del HybridClassifier, que es el objeto bajo prueba.

Casos de test documentados:
    - Cortocircuito: confianza determinística >= 0.90 → Gemini no es invocado.
    - Escalada: confianza determinística < 0.90 → Gemini es consultado.
    - Fallback: Gemini lanza GeminiUnavailableError → resultado de emergencia.
    - Revisión humana: confianza de Gemini < 0.70 → requiere_revision_humana=True.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.classifiers.hybrid import HybridClassifier
from app.core.exceptions import GeminiUnavailableError
from app.schemas.clasificacion import ClasificacionResult


def _det_result(categoria: str, confianza: float) -> ClasificacionResult:
    """
    Construye un ClasificacionResult simulando la salida del clasificador determinístico.

    Función auxiliar de test: centraliza la creación del DTO para evitar
    repetición de código y hacer los tests más legibles.

    Args:
        categoria: Una de las tres categorías válidas del dominio.
        confianza: Valor entre 0.0 y 1.0 a inyectar como resultado del mock.

    Returns:
        ClasificacionResult con etapa="deterministic" y requiere_revision_humana=False.
    """
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa="deterministic",
        requiere_revision_humana=False,
    )


def _gemini_result(categoria: str, confianza: float) -> ClasificacionResult:
    """
    Construye un ClasificacionResult simulando la salida del clasificador de Gemini.

    Incluye el campo respuesta_raw para reproducir fielmente la estructura
    que devuelve GeminiClassifier.classify() en producción.

    Args:
        categoria: Categoría predicha por Gemini.
        confianza: Valor de confianza retornado por Gemini en el JSON de respuesta.

    Returns:
        ClasificacionResult con etapa="gemini" y requiere_revision_humana derivado
        del umbral de revisión humana (confianza < 0.70).
    """
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa="gemini",
        requiere_revision_humana=confianza < 0.70,
        respuesta_raw=f'{{"categoría": "{categoria}", "confianza": {confianza}}}',
    )


@pytest.mark.asyncio
async def test_short_circuit_when_deterministic_confident() -> None:
    """
    Verifica el comportamiento de cortocircuito cuando la confianza determinística
    supera el umbral mínimo de 0.90.

    Cuando el clasificador determinístico devuelve confianza >= 0.90,
    el HybridClassifier debe retornar ese resultado directamente sin invocar
    a Gemini. Este comportamiento es crítico para minimizar el uso de la API
    externa y reducir la latencia en los casos de alta señal de keywords.

    El mock de Gemini permite verificar que classify() no fue invocado
    mediante assert_not_called().
    """
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Sistemas", 0.95),
    ) as mock_det, patch.object(
        classifier._gemini, "classify", new_callable=AsyncMock
    ) as mock_gemini:
        result = await classifier.classify("Se cayó el servidor de red")
        # El resultado debe provenir del clasificador determinístico
        assert result.etapa == "deterministic"
        assert result.categoria == "Sistemas"
        # Gemini no debe haber sido consultado en ningún momento
        mock_gemini.assert_not_called()


@pytest.mark.asyncio
async def test_escalates_to_gemini_when_low_confidence() -> None:
    """
    Verifica que el clasificador híbrido escala a Gemini cuando la confianza
    determinística es insuficiente (por debajo del umbral de 0.90).

    En este escenario el clasificador determinístico retorna 0.55, lo que activa
    la segunda etapa del pipeline. Gemini devuelve 0.88, suficiente para no
    marcar el incidente como de revisión humana (umbral: 0.70).

    El resultado final debe reflejar la etapa y categoría de Gemini.
    """
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Operaciones", 0.55),
    ), patch.object(
        classifier._gemini,
        "classify",
        new_callable=AsyncMock,
        return_value=_gemini_result("Sistemas", 0.88),
    ):
        result = await classifier.classify("Descripción ambigua")
        # El resultado final corresponde a la etapa de Gemini
        assert result.etapa == "gemini"
        assert result.categoria == "Sistemas"
        # Con confianza 0.88 no se activa la revisión humana
        assert result.requiere_revision_humana is False


@pytest.mark.asyncio
async def test_fallback_on_gemini_unavailable() -> None:
    """
    Verifica el comportamiento de emergencia cuando Gemini no está disponible.

    Cuando GeminiClassifier lanza GeminiUnavailableError (por timeout o error
    de red), el HybridClassifier debe capturar la excepción y retornar un
    resultado de fallback con:
        - etapa="fallback"
        - confianza=0.0 (sin señal confiable)
        - requiere_revision_humana=True (para que el incidente sea revisado por un humano)

    Este comportamiento garantiza que el sistema nunca pierde un incidente
    aunque la API de Gemini esté temporalmente inaccesible.
    """
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Soporte Técnico", 0.60),
    ), patch.object(
        classifier._gemini,
        "classify",
        side_effect=GeminiUnavailableError("API down"),
    ):
        result = await classifier.classify("Descripción ambigua")
        # El resultado de fallback debe tener etapa y confianza específicos
        assert result.etapa == "fallback"
        assert result.confianza == 0.0
        # El incidente debe quedar en cola de revisión humana
        assert result.requiere_revision_humana is True


@pytest.mark.asyncio
async def test_human_review_flagged_when_gemini_low_confidence() -> None:
    """
    Verifica que el flag de revisión humana se activa cuando Gemini devuelve
    una confianza inferior al umbral definido (0.70).

    La confianza de 0.55 retornada por Gemini está por debajo del umbral de
    revisión humana. El HybridClassifier debe marcar requiere_revision_humana=True
    para que el incidente sea encolado en la vista de revisión pendiente
    (endpoint GET /api/v1/clasificaciones/revision-pendiente).

    Este mecanismo es la red de seguridad del sistema: cualquier clasificación
    con baja confianza semántica es derivada a un operador humano antes de
    asignarse definitivamente al sector correspondiente.
    """
    classifier = HybridClassifier()
    with patch.object(
        classifier._deterministic,
        "classify",
        new_callable=AsyncMock,
        return_value=_det_result("Operaciones", 0.50),
    ), patch.object(
        classifier._gemini,
        "classify",
        new_callable=AsyncMock,
        return_value=_gemini_result("Operaciones", 0.55),
    ):
        result = await classifier.classify("Descripción poco clara")
        # La confianza de Gemini (0.55) < 0.70 activa la revisión humana
        assert result.requiere_revision_humana is True
