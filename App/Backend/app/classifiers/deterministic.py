"""
Etapa 1 del clasificador híbrido: filtro determinístico basado en reglas.

Responsabilidad:
    Implementa la primera etapa del pipeline de clasificación. Opera aplicando
    expresiones regulares del diccionario de palabras clave (keywords.py) sobre
    la descripción del incidente y calculando una puntuación normalizada por
    categoría. Si la confianza resultante supera el umbral configurado (0.90),
    el resultado se devuelve directamente sin invocar a Gemini, reduciendo
    la latencia y el costo de inferencia del LLM.

Fórmula de confianza (c-71 ASG-009):
    La confianza deja de ser degenerada (1.0 con un unico match). Combina:

        min_matches      = cantidad minima de patrones que debe matchear el ganador
        margin_ratio     = (winner - runner) / (winner + runner)
        sufficiency      = min(1.0, winner / (min_matches + 2))
        confianza        = 0.0 si winner < min_matches, hay empate o no hay senal
                         = min(1.0, margin_ratio * sufficiency) en caso contrario

    Un unico match (winner < min_matches) o cualquier empate (margin 0) produce
    confianza 0.0 y jamas alcanza el cortocircuito. El umbral concreto se
    calibra offline contra el corpus (curva precision/cobertura, piso >= 0.90).

No-match y empate (c-71 ASG-007/ASG-008):
    Sin ningun match (`winner_score == 0`) el resultado senala `sin_prediccion=True`
    con `sector_predicho=None` (NO la primera clave del mapa). Con dos o mas
    sectores empatados en el puntaje maximo se marca `ambiguo=True`, sin elegir
    ganador por el orden del mapa. Ambos estados escalan a la etapa semantica.

Optimización:
    Los patrones regex se compilan una sola vez al inicio de la aplicación
    mediante lru_cache y se reutilizan en todas las clasificaciones posteriores,
    evitando el costo de compilación en cada solicitud.

Score de correctitud (c-74 ASG-010, OQ1/OQ4):
    La `confianza` mide FUERZA DE SENAL, no correctitud. El cortocircuito se
    gobierna por un `score_correctitud` acotado a [0,1], derivado de features
    observables en runtime (score del ganador, runner-up, margen, cantidad de
    matches, longitud del texto y senales por sector). El score ORDENA la
    correctitud esperada (mayor = mas evidencia de acierto); NO es una
    probabilidad calibrada de acierto. Es puramente deterministico y a-priori:
    su punto de operacion se calibra OFFLINE out-of-fold en
    `evaluation/deterministic_measurement.py`. `min_matches` interviene como
    FEATURE (denominador de la evidencia), NO como gate binario (OQ4): un unico
    match conserva un score no nulo.
"""

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping

from app.classifiers.base import BaseClassifier
from app.classifiers.keywords import KEYWORD_MAP
from app.config.settings import get_settings
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)

# Lista de categorías válidas derivada del diccionario de palabras clave
CATEGORIES = list(KEYWORD_MAP.keys())


@dataclass(frozen=True)
class FeaturesDeterministas:
    """
    Features observables en runtime que alimentan el score de correctitud (ASG-010).

    Se derivan SOLO de la descripcion y el vocabulario: no usan informacion no
    disponible en runtime ni servicios externos (D7).
    """

    winner_score: float        # cantidad de patrones distintos que matchea el ganador
    runner_up_score: float     # mayor puntaje entre los sectores no ganadores
    margin: float              # winner_score - runner_up_score
    margin_ratio: float        # margin / (winner + runner), en [0, 1]
    total_matches: float       # suma de matches de todos los sectores
    text_length: int           # longitud de la descripcion en caracteres
    sectores_con_senal: int    # cantidad de sectores con al menos un match
    min_matches: int           # parametro (c-74 OQ4): feature, no gate


@dataclass(frozen=True)
class PesosScore:
    """Pesos a-priori y longitud de referencia del score de correctitud (ASG-010)."""

    w_margin: float = 0.5
    w_evidence: float = 0.3
    w_density: float = 0.2
    length_reference: float = 200.0


def extraer_features(
    scores: Mapping[str, float],
    text_length: int,
    min_matches: int,
) -> FeaturesDeterministas:
    """
    Deriva las features observables del determinista a partir del mapa de scores.

    Funcion pura: no hace I/O, no depende de servicios externos y no muta la
    entrada. Ante ausencia de senal (todos los scores en 0) devuelve features
    nulas sin dividir por cero.
    """
    valores = list(scores.values())
    winner_score = max(valores) if valores else 0.0
    runner_up_score = max((v for v in valores if v < winner_score), default=0.0)
    margin = winner_score - runner_up_score
    denominador = winner_score + runner_up_score
    margin_ratio = margin / denominador if denominador > 0 else 0.0
    return FeaturesDeterministas(
        winner_score=winner_score,
        runner_up_score=runner_up_score,
        margin=margin,
        margin_ratio=margin_ratio,
        total_matches=float(sum(valores)),
        text_length=text_length,
        sectores_con_senal=sum(1 for v in valores if v > 0),
        min_matches=min_matches,
    )


def score_correctitud(
    features: FeaturesDeterministas,
    pesos: PesosScore,
) -> float:
    """
    Combina las features en un score acotado a [0.0, 1.0] (ASG-010).

    El score crece con la evidencia del ganador y con el margen sobre el segundo,
    y decrece con la longitud del texto (densidad de senal). ORDENA la correctitud
    esperada; NO es una probabilidad calibrada. Es una funcion pura: misma
    entrada, misma salida; sin proveedores pagos. `min_matches` entra como
    denominador de la evidencia, de modo que NO anula el score (OQ4).
    """
    if features.winner_score <= 0.0:
        return 0.0

    evidence = features.winner_score / (
        features.winner_score + features.min_matches
    )
    density = min(1.0, pesos.length_reference / max(features.text_length, 1))
    peso_total = pesos.w_margin + pesos.w_evidence + pesos.w_density
    if peso_total <= 0.0:
        return 0.0

    crudo = (
        pesos.w_margin * features.margin_ratio
        + pesos.w_evidence * evidence
        + pesos.w_density * density
    ) / peso_total
    return max(0.0, min(1.0, crudo))



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
        Inicializa el clasificador cargando los patrones compilados, el umbral
        de confianza y el conteo minimo de matches configurados en Settings.
        """
        self._patterns = _compile_patterns()
        settings = get_settings()
        self._threshold = settings.deterministic_confidence_threshold
        self._min_matches = settings.deterministic_min_matches
        # c-74: pesos a-priori del score de correctitud (ASG-010).
        self._pesos = PesosScore(
            w_margin=settings.deterministic_score_weight_margin,
            w_evidence=settings.deterministic_score_weight_evidence,
            w_density=settings.deterministic_score_weight_density,
            length_reference=settings.deterministic_score_length_reference,
        )

    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Clasifica la descripción mediante conteo de matches de patrones regex.

        Proceso:
            1. Calcula el score de cada categoría (matches sobre descripcion).
            2. Detecta ausencia de senal (score maximo == 0) -> sin_prediccion.
            3. Detecta empate en el puntaje maximo -> ambiguo, sin ganador arbitrario.
            4. Calcula la confianza con conteo minimo y margen sobre el segundo.
            5. Retorna el resultado con etapa="deterministic".

        El campo requiere_revision_humana siempre es False en esta etapa;
        la evaluación de revisión humana la realiza el HybridClassifier
        según el umbral de confianza.

        Args:
            descripcion: Texto del incidente a clasificar.

        Returns:
            ClasificacionResult con el sector dominante y su confianza, o el
            estado explicito de ausencia/ambiguedad cuando no hay senal unica.
        """
        scores = self._score(descripcion)
        max_score = max(scores.values()) if scores else 0.0

        # ── Ausencia de senal: no se inventa un sector (ASG-007) ──────────────
        if max_score <= 0.0:
            logger.debug("deterministic_no_match", scores=scores)
            return ClasificacionResult(
                sector_predicho=None,
                sectores_adicionales=[],
                confianza=0.0,
                etapa="deterministic",
                requiere_revision_humana=False,
                respuesta_raw=None,
                sin_prediccion=True,
                ambiguo=False,
            )

        # ── Empate en el puntaje maximo: ambiguo, sin ganador por orden ───────
        winners = [cat for cat, score in scores.items() if score == max_score]
        ambiguo = len(winners) > 1
        winner = winners[0] if not ambiguo else None

        # Features observables y score de correctitud (c-74 ASG-010). Se derivan
        # una sola vez desde `scores`; el runner-up sale de las features.
        features = extraer_features(
            scores, text_length=len(descripcion), min_matches=self._min_matches
        )

        # Sectores secundarios con alguna señal (conjunto multietiqueta).
        sectores_adicionales = [
            categoria
            for categoria, score in scores.items()
            if score > 0 and categoria != winner
        ]

        confidence = self._confidence(
            features.winner_score, features.runner_up_score, ambiguo
        )

        # Un empate no tiene ganador unico: su score es 0.0 (escala de todos modos).
        score = 0.0 if ambiguo else score_correctitud(features, self._pesos)

        logger.debug(
            "deterministic_scores",
            scores=scores,
            winner=winner,
            ambiguo=ambiguo,
            confidence=round(confidence, 4),
            score_correctitud=round(score, 4),
        )

        return ClasificacionResult(
            sector_predicho=winner,
            sectores_adicionales=sectores_adicionales,
            confianza=confidence,
            etapa="deterministic",
            requiere_revision_humana=False,  # Evaluado por el HybridClassifier
            respuesta_raw=None,              # Sin respuesta raw en etapa determinística
            sin_prediccion=False,
            ambiguo=ambiguo,
            score_correctitud=score,
        )

    def _confidence(
        self,
        winner_score: float,
        runner_up_score: float,
        ambiguo: bool,
    ) -> float:
        """
        Calcula la confianza deterministica (c-71 ASG-009).

        Un unico match (winner_score < min_matches) o un empate producen 0.0.
        En caso contrario combina el margen sobre el segundo con un factor de
        suficiencia creciente con la cantidad de matches del ganador. El valor
        queda acotado a [0.0, 1.0].
        """
        if ambiguo or winner_score <= 0.0:
            return 0.0
        if winner_score < self._min_matches:
            return 0.0

        margin_ratio = (winner_score - runner_up_score) / (
            winner_score + runner_up_score
        )
        sufficiency = min(1.0, winner_score / (self._min_matches + 2))
        return min(1.0, margin_ratio * sufficiency)


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
            True si la confianza supera o iguala el umbral calibrado en Settings
            (c-71; documentado en docs/deterministic_calibration.md).
        """
        return result.confianza >= self._threshold
