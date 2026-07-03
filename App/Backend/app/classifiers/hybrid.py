"""
Orquestador del pipeline de clasificación híbrido.

Responsabilidad:
    Coordina la ejecución secuencial de las dos etapas de clasificación
    (determinística y Gemini) según el flujo de decisión especificado
    en el Anexo H de la tesis. Determina cuándo cada etapa es suficiente
    y cuándo escalar al siguiente nivel.

Flujo de decisión (Anexo H):
    1. Ejecutar DeterministicClassifier sobre la descripción.
    2. Si confianza >= 0.90 → retornar resultado determinístico (omitir Gemini).
    3. Si confianza <  0.90 → invocar GeminiClassifier.
    4. Si confianza de Gemini < 0.70 → marcar para revisión humana.
    5. Si Gemini falla (timeout / no disponible) → retornar fallback
       preservando la categoría determinística pero con confianza=0.0.

Principio de diseño:
    El HybridClassifier no conoce los detalles de implementación de ninguna
    de las dos etapas; solo depende del contrato BaseClassifier. Esto permite
    sustituir o mockear cualquiera de las etapas sin modificar el orquestador,
    facilitando el testing y la evolución futura del sistema.
"""

from app.classifiers.base import BaseClassifier
from app.classifiers.deterministic import DeterministicClassifier
from app.classifiers.gemini_classifier import GeminiClassifier
from app.config.settings import get_settings
from app.core.exceptions import GeminiTimeoutError, GeminiUnavailableError
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)


class HybridClassifier(BaseClassifier):
    """
    Clasificador híbrido que orquesta el pipeline de dos etapas.

    Combina la velocidad y el costo cero del filtro determinístico
    para los casos de alta confianza, con la comprensión semántica
    del LLM Gemini 2.5 Flash para los casos ambiguos.

    Permite inyección de dependencias de las sub-etapas para testing:
        classifier = HybridClassifier(
            deterministic=MockDeterministicClassifier(),
            gemini=MockGeminiClassifier(),
        )
    """

    def __init__(
        self,
        deterministic: DeterministicClassifier | None = None,
        gemini: GeminiClassifier | None = None,
    ) -> None:
        """
        Inicializa el pipeline con las instancias de cada etapa.

        Si no se inyectan dependencias, crea las instancias reales.
        Este patrón permite usar mocks en tests sin modificar la lógica
        de orquestación del clasificador.

        Args:
            deterministic: Instancia del clasificador determinístico (opcional).
            gemini:        Instancia del clasificador Gemini (opcional).
        """
        self._deterministic = deterministic or DeterministicClassifier()
        self._gemini = gemini or GeminiClassifier()
        # Umbrales leídos de Settings para permitir ajuste sin recompilación
        self._det_threshold = get_settings().deterministic_confidence_threshold
        self._human_threshold = get_settings().human_review_threshold

    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Ejecuta el pipeline de clasificación híbrido sobre la descripción dada.

        Implementa el flujo de decisión de dos etapas documentado en el Anexo H:

        Etapa 1 – Filtro determinístico:
            Si la confianza supera el umbral configurado (0.90 por defecto),
            el resultado se retorna directamente sin llamar a Gemini.
            Esto "cortocircuita" el pipeline para los casos más evidentes,
            reduciendo latencia y consumo de tokens de la API.

        Etapa 2 – Clasificación con Gemini:
            Se invoca únicamente cuando el filtro determinístico no alcanzó
            el umbral. Si Gemini falla (timeout o no disponible), se retorna
            un resultado de fallback con confianza=0.0 preservando la categoría
            que había estimado el clasificador determinístico.

        Revisión humana:
            Se activa cuando la confianza final (de cualquier etapa) es inferior
            al umbral de revisión humana (0.70 por defecto). Se verifica
            explícitamente aquí como segunda línea de defensa, aunque
            GeminiClassifier ya lo maneja internamente.

        Args:
            descripcion: Texto pseudonimizado del incidente a clasificar.

        Returns:
            ClasificacionResult con la categoría final, la confianza y
            el indicador de revisión humana.
        """
        # ── Etapa 1: Clasificador determinístico ──────────────────────────────
        det_result = await self._deterministic.classify(descripcion)

        if det_result.confianza >= self._det_threshold:
            # Cortocircuito: confianza suficiente para omitir Gemini
            logger.info(
                "classifier_short_circuit",
                stage="deterministic",
                categoria=det_result.categoria,
                confianza=det_result.confianza,
            )
            return det_result

        # Confianza insuficiente: escalar al clasificador semántico
        logger.info(
            "classifier_escalate_to_gemini",
            det_confianza=det_result.confianza,
            det_categoria=det_result.categoria,
        )

        # ── Etapa 2: Clasificador Gemini ──────────────────────────────────────
        try:
            gemini_result = await self._gemini.classify(descripcion)
        except (GeminiTimeoutError, GeminiUnavailableError) as exc:
            # Falla de Gemini: retornar fallback con la categoría del determinístico
            # como mejor aproximación disponible, pero marcando revisión humana.
            logger.warning(
                "gemini_fallback_triggered",
                reason=type(exc).__name__,
                message=exc.message,
            )
            return ClasificacionResult(
                categoria=det_result.categoria,  # Mejor estimación disponible
                confianza=0.0,                   # Señal explícita de fallo
                etapa="fallback",
                requiere_revision_humana=True,
                respuesta_raw=None,
            )

        # Segunda línea de defensa: garantizar que confianza baja active revisión humana
        # (GeminiClassifier lo maneja internamente, pero se verifica aquí por claridad)
        if gemini_result.confianza < self._human_threshold:
            gemini_result = gemini_result.model_copy(
                update={"requiere_revision_humana": True}
            )

        return gemini_result
