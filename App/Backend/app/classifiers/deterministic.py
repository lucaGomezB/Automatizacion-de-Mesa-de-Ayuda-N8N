"""
Etapa 1 del clasificador híbrido: filtro determinístico basado en reglas.

Responsabilidad:
    Implementa la primera etapa del pipeline de clasificación. Opera aplicando
    expresiones regulares del diccionario de palabras clave (keywords.py) sobre
    la descripción del incidente y calculando una puntuación normalizada por
    categoría. Si la confianza resultante supera el umbral configurado (0.90),
    el resultado se devuelve directamente sin invocar a Gemini, reduciendo
    la latencia y el costo de inferencia del LLM.

Fórmula de confianza:
    La confianza se calcula como:

        score(cat) = cantidad de patrones distintos que hicieron match
        confianza  = score(ganador) / (score(ganador) + score(segundo) + ε)

    El denominador incluye al segundo candidato para penalizar los casos
    ambiguos (donde múltiples categorías tienen scores similares). El término
    ε = 1e-6 previene la división por cero cuando no hay ningún match.

    Esta fórmula produce valores en (0.0, 1.0) que reflejan qué tan
    dominante es la categoría ganadora respecto a la segunda opción.

Optimización:
    Los patrones regex se compilan una sola vez al inicio de la aplicación
    mediante lru_cache y se reutilizan en todas las clasificaciones posteriores,
    evitando el costo de compilación en cada solicitud.
"""

import re
from functools import lru_cache

from app.classifiers.base import BaseClassifier
from app.classifiers.keywords import KEYWORD_MAP
from app.config.settings import get_settings
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)

# Lista de categorías válidas derivada del diccionario de palabras clave
CATEGORIES = list(KEYWORD_MAP.keys())


@lru_cache(maxsize=1)
def _compile_patterns() -> dict[str, list[re.Pattern[str]]]:
    """
    Compila todos los patrones regex del diccionario de palabras clave.

    Se invoca una sola vez gracias al decorador lru_cache. Los flags
    re.IGNORECASE y re.UNICODE garantizan que los patrones funcionen
    correctamente con el español rioplatense, incluyendo tildes y la ñ.

    Returns:
        Diccionario de categoría → lista de patrones compilados listos
        para ejecutar Pattern.search() sin recompilación.
    """
    return {
        category: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]
        for category, patterns in KEYWORD_MAP.items()
    }


class DeterministicClassifier(BaseClassifier):
    """
    Clasificador basado en conteo de matches de expresiones regulares.

    Implementa la Etapa 1 del pipeline híbrido. Es determinístico en el
    sentido de que ante la misma entrada produce siempre la misma salida,
    sin variabilidad estocástica ni llamadas a servicios externos.

    Ventajas sobre el clasificador LLM para los casos de alta confianza:
        - Latencia < 1 ms (sin E/S de red).
        - Sin costo de API por token procesado.
        - Totalmente predecible y auditable.
        - No requiere conexión a internet.

    Limitación: no comprende contexto semántico ni sinónimos no incluidos
    explícitamente en el diccionario. Para esos casos, el pipeline escala
    la clasificación a Gemini.
    """

    # Pequeña constante para evitar división por cero cuando no hay ningún match
    _EPS = 1e-6

    def __init__(self) -> None:
        """
        Inicializa el clasificador cargando los patrones compilados y el umbral
        de confianza configurado en Settings.
        """
        self._patterns = _compile_patterns()
        self._threshold = get_settings().deterministic_confidence_threshold

    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Clasifica la descripción mediante conteo de matches de patrones regex.

        Proceso:
            1. Calcula el score de cada categoría (matches sobre descripcion).
            2. Ordena las categorías de mayor a menor score.
            3. Calcula la confianza normalizada usando la fórmula ganador/(ganador+segundo+ε).
            4. Retorna el resultado con etapa="deterministic".

        El campo requiere_revision_humana siempre es False en esta etapa;
        la evaluación de revisión humana la realiza el HybridClassifier
        según el umbral de confianza de 0.70.

        Args:
            descripcion: Texto del incidente a clasificar.

        Returns:
            ClasificacionResult con la categoría dominante y su confianza.
        """
        scores = self._score(descripcion)

        # Ordenar de mayor a menor score para identificar ganador y segundo lugar
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        winner, winner_score = sorted_cats[0]
        runner_up_score = sorted_cats[1][1] if len(sorted_cats) > 1 else 0

        # Fórmula de confianza normalizada: penaliza los casos con ambigüedad
        confidence = winner_score / (winner_score + runner_up_score + self._EPS)

        # Acotamiento a 1.0 para absorber posible ruido de punto flotante
        confidence = min(confidence, 1.0)

        logger.debug(
            "deterministic_scores",
            scores=scores,
            winner=winner,
            confidence=round(confidence, 4),
        )

        return ClasificacionResult(
            categoria=winner,
            confianza=confidence,
            etapa="deterministic",
            requiere_revision_humana=False,  # Evaluado por el HybridClassifier
            respuesta_raw=None,              # Sin respuesta raw en etapa determinística
        )

    def _score(self, text: str) -> dict[str, float]:
        """
        Calcula la puntuación bruta de cada categoría sobre el texto dado.

        Cuenta cuántos patrones distintos hacen match en el texto para
        cada categoría. No contabiliza la cantidad de veces que un mismo
        patrón hace match, sino la cantidad de patrones distintos que
        al menos una vez coinciden, para evitar sesgo por repetición.

        Args:
            text: Texto del incidente a evaluar.

        Returns:
            Diccionario de categoría → cantidad de patrones con match.
        """
        return {
            category: float(
                sum(1 for pattern in patterns if pattern.search(text))
            )
            for category, patterns in self._patterns.items()
        }

    def is_confident(self, result: ClasificacionResult) -> bool:
        """
        Indica si el resultado alcanza el umbral de confianza para cortocircuitar Gemini.

        Args:
            result: Resultado producido por classify().

        Returns:
            True si la confianza supera o iguala el umbral configurado (0.90 por defecto).
        """
        return result.confianza >= self._threshold
