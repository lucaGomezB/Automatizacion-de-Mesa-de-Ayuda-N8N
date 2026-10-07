"""
Orquestador del pipeline de clasificación híbrido.

Responsabilidad:
    Coordina la ejecución secuencial de las dos etapas de clasificación
    (determinística y Gemini) según el flujo de decisión especificado
    en el Anexo H de la tesis. Determina cuándo cada etapa es suficiente
    y cuándo escalar al siguiente nivel.

Flujo de decisión (Anexo H, c-74):
    1. Ejecutar DeterministicClassifier sobre la descripción.
    2. Si senal dominante y score de correctitud >= punto de operacion
       (Settings) → retornar resultado determinístico (omitir Gemini).
    3. Si ausencia de predicción, ambigüedad o score insuficiente → invocar
       GeminiClassifier.
    4. Si confianza de Gemini < 0.70 → marcar para revisión humana.
    5. Si Gemini falla (timeout / no disponible) → retornar fallback
       preservando la mejor estimación determinística (o su ausencia) con
       confianza=0.0, sin fabricar un sector.

    c-74 (ASG-010/OQ4): la seleccion del cortocircuito se gobierna por el score
    de correctitud (ordena la correctitud esperada; NO es una probabilidad
    calibrada), NO por la `confianza` (fuerza de senal) ni por un gate de
    cantidad minima de matches.

Principio de diseño:
    El HybridClassifier no conoce los detalles de implementación de ninguna
    de las dos etapas; solo depende del contrato BaseClassifier. Esto permite
    sustituir o mockear cualquiera de las etapas sin modificar el orquestador,
    facilitando el testing y la evolución futura del sistema.
"""

from typing import TYPE_CHECKING

from app.classifiers.base import BaseClassifier
from app.classifiers.deterministic import DeterministicClassifier
from app.classifiers.gemini_classifier import GeminiClassifier
from app.config.settings import get_settings
from app.constants import HYBRID_CACHE_VERSION
from app.core.exceptions import (
    CostGuardTrippedError,
    GeminiTimeoutError,
    GeminiUnavailableError,
)
from app.core.logging import get_logger
from app.cost_guard.constants import CAUSE_BUDGET, PROVIDER_BACKEND_GEMINI
from app.schemas.clasificacion import ClasificacionResult

if TYPE_CHECKING:
    from app.cost_guard.guard import CostGuard

logger = get_logger(__name__)


class HybridClassifier(BaseClassifier):
    """
    Clasificador híbrido que orquesta el pipeline de dos etapas.

    Combina la velocidad y el costo cero del filtro determinístico
    para los casos de alta confianza, con la comprensión semántica
    del LLM Gemini 3.6 Flash para los casos ambiguos.

    Permite inyección de dependencias de las sub-etapas para testing:
        classifier = HybridClassifier(
            deterministic=MockDeterministicClassifier(),
            gemini=MockGeminiClassifier(),
        )
    """

    # Clave de version del clasificador usada por el cache de predicciones de la
    # evaluacion (C-34). Se incrementa cuando cambia la logica de clasificacion
    # de forma que invalide las predicciones persistidas. La fuente de verdad es
    # app.constants.HYBRID_CACHE_VERSION (W-3), para que el runner la lea sin
    # construir el clasificador.
    CACHE_VERSION = HYBRID_CACHE_VERSION

    def __init__(
        self,
        deterministic: DeterministicClassifier | None = None,
        gemini: GeminiClassifier | None = None,
        cost_guard: "CostGuard | None" = None,
        degradation_policy: str | None = None,
    ) -> None:
        """
        Inicializa el pipeline con las instancias de cada etapa.

        Si no se inyectan dependencias, crea las instancias reales.
        Este patrón permite usar mocks en tests sin modificar la lógica
        de orquestación del clasificador.

        Args:
            deterministic: Instancia del clasificador determinístico (opcional).
            gemini:        Instancia del clasificador Gemini (opcional).
            cost_guard:    Guarda de costo en runtime (opcional). Se evalua
                           ANTES de invocar a Gemini; si deniega, no se invoca
                           al proveedor pago y se degrada de forma segura.
            degradation_policy: politica al dispararse la guarda. `deterministic_review`
                           (default) degrada a deterministico + revision humana;
                           `hard_block` propaga `CostGuardTrippedError` como senal
                           explicita. En NINGUN caso se invoca al proveedor pago.
        """
        self._deterministic = deterministic or DeterministicClassifier()
        self._gemini = gemini or GeminiClassifier()
        self._cost_guard = cost_guard
        self._degradation_policy = (
            degradation_policy
            if degradation_policy is not None
            else get_settings().cost_guard_degradation_policy
        )
        # Umbrales leídos de Settings para permitir ajuste sin recompilación.
        # c-74: el cortocircuito se gobierna por el score de correctitud
        # (ordena la correctitud esperada; NO es una probabilidad calibrada)
        # (ASG-010), no por la confianza (fuerza de senal).
        self._score_threshold = get_settings().deterministic_score_threshold
        self._human_threshold = get_settings().human_review_threshold
        # c-58 (D4): la reserva de la superficie backend_gemini se dimensiona al
        # PEOR CASO de intentos de UNA clasificacion (max_retries + 1) y se evalua
        # UNA sola vez antes de invocar al proveedor. Los reintentos del
        # GeminiClassifier NO re-evaluán la guarda ni reservan de nuevo.
        self._gemini_max_attempts = get_settings().gemini_max_retries + 1


    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Ejecuta el pipeline de clasificación híbrido sobre la descripción dada.

        Implementa el flujo de decisión de dos etapas documentado en el Anexo H:

        Etapa 1 – Filtro determinístico:
            Si la senal es dominante (sin ausencia ni ambiguedad) y su score
            de correctitud alcanza el punto de operacion (Settings,
            c-74), el resultado se retorna directamente sin llamar a Gemini.
            Esto "cortocircuita" el pipeline para los casos mas evidentes,
            reduciendo latencia y consumo de tokens de la API. La `confianza`
            (fuerza de senal) NO es criterio de seleccion.

        Etapa 2 – Clasificación con Gemini:
            Se invoca únicamente cuando el filtro determinístico no alcanzó
            el punto de operación. Si Gemini falla (timeout o no disponible), se retorna
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

        # c-71/c-74: una ausencia de prediccion o un empate NUNCA cortocircuitan,
        # con independencia del score (ASG-007/ASG-008/OQ5). El cortocircuito solo
        # ocurre con una senal dominante y un score de correctitud suficiente.
        causa_escalamiento: str | None = None
        if det_result.sin_prediccion:
            causa_escalamiento = "sin_prediccion"
        elif det_result.ambiguo:
            causa_escalamiento = "ambiguo"

        if causa_escalamiento is None and det_result.score_correctitud >= self._score_threshold:
            # Cortocircuito: score de correctitud suficiente para omitir Gemini
            logger.info(
                "classifier_short_circuit",
                stage="deterministic",
                sector_predicho=det_result.sector_predicho,
                confianza=det_result.confianza,
                score_correctitud=det_result.score_correctitud,
                punto_operacion=self._score_threshold,
            )
            return det_result

        # Score insuficiente (o estado de ausencia/ambiguedad): escalar a Gemini
        logger.info(
            "classifier_escalate_to_gemini",
            causa=causa_escalamiento,
            det_confianza=det_result.confianza,
            det_score_correctitud=det_result.score_correctitud,
            punto_operacion=self._score_threshold,
            det_sector_predicho=det_result.sector_predicho,
        )

        # ── Etapa 2: Clasificador Gemini ──────────────────────────────────────
        try:
            # Guarda de costo en runtime (c-45): se evalua ANTES de invocar al
            # proveedor pago. El cortocircuito determinista de arriba nunca
            # llega aqui, por lo que NO consume presupuesto ni tasa.
            if self._cost_guard is not None:
                decision = await self._cost_guard.evaluate(
                    provider=PROVIDER_BACKEND_GEMINI,
                    amount=self._gemini_max_attempts,
                )
                if not decision.allowed:
                    raise CostGuardTrippedError(
                        decision.cause or CAUSE_BUDGET, PROVIDER_BACKEND_GEMINI
                    )
            gemini_result = await self._gemini.classify(descripcion)
        except CostGuardTrippedError as exc:
            # Politica de bloqueo duro: propagar la senal explicita sin invocar
            # al proveedor pago (el llamador decide rechazar/diferir).
            if self._degradation_policy == "hard_block":
                logger.warning(
                    "cost_guard_hard_block",
                    cause=exc.cause,
                    provider=exc.provider,
                )
                raise
            # Politica por defecto: degradar a deterministico + revision humana.
            logger.warning(
                "gemini_fallback_triggered",
                reason=type(exc).__name__,
                message=exc.message,
            )
            return ClasificacionResult(
                sector_predicho=det_result.sector_predicho,  # Mejor estimación disponible (o None)
                sectores_adicionales=det_result.sectores_adicionales,
                confianza=0.0,                   # Señal explícita de fallo
                etapa="fallback",
                requiere_revision_humana=True,
                respuesta_raw=None,
                sin_prediccion=det_result.sin_prediccion,  # c-71: no se fabrica sector
                ambiguo=det_result.ambiguo,                # c-71: se preserva la ambiguedad
            )
        except (GeminiTimeoutError, GeminiUnavailableError) as exc:
            # Falla de Gemini: retornar fallback con la categoría del determinístico
            # como mejor aproximación disponible, pero marcando revisión humana.
            logger.warning(
                "gemini_fallback_triggered",
                reason=type(exc).__name__,
                message=exc.message,
            )
            return ClasificacionResult(
                sector_predicho=det_result.sector_predicho,  # Mejor estimación disponible (o None)
                sectores_adicionales=det_result.sectores_adicionales,
                confianza=0.0,                   # Señal explícita de fallo
                etapa="fallback",
                requiere_revision_humana=True,
                respuesta_raw=None,
                sin_prediccion=det_result.sin_prediccion,  # c-71: no se fabrica sector
                ambiguo=det_result.ambiguo,                # c-71: se preserva la ambiguedad
            )

        # Segunda línea de defensa: garantizar que confianza baja active revisión humana
        # (GeminiClassifier lo maneja internamente, pero se verifica aquí por claridad)
        if gemini_result.confianza < self._human_threshold:
            gemini_result = gemini_result.model_copy(
                update={"requiere_revision_humana": True}
            )

        return gemini_result
