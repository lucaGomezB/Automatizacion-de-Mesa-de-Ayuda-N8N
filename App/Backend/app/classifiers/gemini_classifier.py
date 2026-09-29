"""
Etapa 2 del clasificador híbrido: clasificación semántica con Gemini 3.6 Flash.

Responsabilidad:
    Implementa la segunda etapa del pipeline híbrido. Invoca la API de
    Google Gemini 3.6 Flash con los parámetros exactos documentados en:
        - docs/parameters_gemini.md
        - docs/prompt_gemini.txt
        - Anexo H de la tesis (docs/anexo_h_prompt_gemini.md)

    Esta etapa solo se activa cuando el clasificador determinístico no
    supera el umbral de confianza de 0.90. Aprovecha la comprensión
    semántica del LLM para resolver casos ambiguos que el diccionario
    de palabras clave no puede discriminar.

Estrategia de resiliencia:
    Ante cualquier falla (timeout, respuesta inválida, API no disponible),
    el clasificador retorna un resultado de fallback con confianza=0.0 y
    requiere_revision_humana=True, garantizando que el sistema no se
    detenga ante indisponibilidad del servicio externo.

Validación de respuestas (Anexo H §H.3):
    Toda respuesta de Gemini es validada exhaustivamente antes de ser
    aceptada. Los cuatro controles son:
        1. Sintaxis JSON válida.
        2. Presencia de los campos "categoría" y "confianza".
        3. Valor de "categoría" dentro del conjunto canónico de 5 sectores
           (app.constants.SECTORES_CANONICOS).
        4. Valor de "confianza" numérico en el rango [0.0, 1.0].
"""

import asyncio
import json
import random
import time
from pathlib import Path
from typing import Awaitable, Callable

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.classifiers.base import BaseClassifier
from app.config.settings import get_settings
from app.constants import SECTORES_CANONICOS
from app.core.exceptions import (
    GeminiResponseInvalidError,
    GeminiTimeoutError,
    GeminiUnavailableError,
)
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)

# Cliente de Gemini compartido a nivel de proceso (BE B7 / D11).
# Antes se instanciaba un `genai.Client` por cada clasificador (es decir, por
# request) y nunca se cerraba: fuga de recursos y overhead en el camino caliente.
# Ahora se crea una sola vez de forma perezosa (lazy) y se cierra en el shutdown
# de la aplicacion mediante `close_genai_client()`.
_genai_client: genai.Client | None = None

# Opciones HTTP del cliente compartido: se desactiva explicitamente el
# auto-retry del SDK para que UNA sola capa (el bucle de `GeminiClassifier`)
# gobierne los reintentos. En google-genai 2.25.0 el default ya es un unico
# intento (`stop_after_attempt(1)`), pero se declara de forma explicita para no
# depender de un default que puede cambiar entre versiones (c-58 D1).
_GENAI_HTTP_OPTIONS = genai_types.HttpOptions(
    retry_options=genai_types.HttpRetryOptions(attempts=1)
)

# Estados HTTP del proveedor considerados TRANSITORIOS y elegibles para reintento.
# Los demas errores de cliente (400/401/403/404) son terminales (c-58 D2).
TRANSIENT_HTTP_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def get_genai_client() -> genai.Client:
    """
    Devuelve el cliente de Gemini compartido, creandolo en el primer uso.

    Returns:
        Instancia unica de `genai.Client` para todo el proceso.
    """
    global _genai_client
    if _genai_client is None:
        settings = get_settings()
        _genai_client = genai.Client(  # gitleaks:allow
            api_key=settings.gemini_api_key,  # gitleaks:allow
            http_options=_GENAI_HTTP_OPTIONS,
        )
    return _genai_client


def _is_transient_error(exc: BaseException) -> bool:
    """
    Clasifica una excepcion del proveedor como transitoria o terminal (helper puro).

    Transitorias (elegibles para reintento): timeouts, errores de servidor (5xx,
    incluido 503) y limites de tasa (429). Terminales (sin reintento): el resto
    de los errores de cliente 4xx (400/401/403/404) y cualquier otra excepcion.

    Args:
        exc: excepcion capturada al invocar al proveedor.

    Returns:
        True si la falla es transitoria y admite reintento.
    """
    if isinstance(exc, TimeoutError):
        return True
    if isinstance(exc, genai_errors.ServerError):
        return True
    if isinstance(exc, genai_errors.APIError):
        code = getattr(exc, "code", None)
        try:
            return int(code) in TRANSIENT_HTTP_STATUS_CODES
        except (TypeError, ValueError):
            return False
    return False



async def close_genai_client() -> None:
    """
    Cierra el cliente de Gemini compartido y libera su pool HTTP.

    Se invoca en el shutdown de la aplicacion (lifespan). Es idempotente: si no
    hay cliente creado, no hace nada. Nunca propaga excepciones de cierre para
    no impedir el resto del shutdown.
    """
    global _genai_client
    client = _genai_client
    _genai_client = None
    if client is not None:
        try:
            await client.aio.aclose()
        except Exception as exc:  # pragma: no cover - defensa de shutdown
            logger.warning("genai_client_close_failed", exc_info=exc)

# Conjunto de categorías válidas. Debe coincidir exactamente con los valores
# definidos en el prompt (docs/prompt_gemini.txt) y en app.constants.
_VALID_CATEGORIES = frozenset(SECTORES_CANONICOS)

# Ruta default al prompt documentado en la tesis, anclada a la RAÍZ del repositorio
# (no al cwd ni a Backend/): classifiers → app → Backend → App → raíz.
# El archivo vive en docs/prompt_gemini.txt junto al resto de la documentación de la tesis.
def _default_prompt_path(module_file: str | Path | None = None) -> Path:
    """
    Resuelve la ruta default al prompt anclada a la RAÍZ del repositorio.

    Recorre los directorios padre del módulo buscando `docs/prompt_gemini.txt`.
    La búsqueda es perezosa (se ejecuta al llamar, no al importar) y defensiva:
    evita el acceso ansioso a `parents[4]`, que en layouts planos —como el de la
    imagen Docker (`/app/app/classifiers/gemini_classifier.py`, solo 4 parents)—
    lanzaba `IndexError` y abortaba `import app.main`.

    Si no encuentra el archivo, devuelve una ruta best-effort inexistente para
    que `_load_prompt` degrade a la copia embebida sin lanzar.

    Args:
        module_file: Ruta del módulo usada como ancla. Por defecto, este módulo.
            Parametrizable para simular layouts alternativos (tests).

    Returns:
        Ruta al archivo de prompt (puede no existir).
    """
    source = Path(module_file) if module_file is not None else Path(__file__)
    resolved = source.resolve()
    for parent in resolved.parents:
        candidate = parent / "docs" / "prompt_gemini.txt"
        if candidate.exists():
            return candidate
    # Best-effort: ruta inexistente anclada al directorio del módulo. `_load_prompt`
    # la captura como FileNotFoundError y degrada a la copia embebida.
    return resolved.parent / "docs" / "prompt_gemini.txt"


def _resolve_prompt_path() -> Path:
    """
    Resuelve la ruta del archivo de prompt de forma determinística.

    Prioridad:
        1. settings.gemini_prompt_path (env var GEMINI_PROMPT_PATH) si está definida —
           necesario en contenedores donde la estructura difiere del repo.
        2. Default anclado a la raíz del repo vía la ubicación de este módulo,
           independiente del directorio de trabajo del proceso.

    Returns:
        Ruta al archivo de prompt (puede no existir; _load_prompt degrada en ese caso).
    """
    settings = get_settings()
    if settings.gemini_prompt_path:
        return Path(settings.gemini_prompt_path)
    return _default_prompt_path()


def _load_prompt() -> str:
    """
    Carga el prompt desde la ruta resuelta por _resolve_prompt_path().

    Si el archivo no existe (por ejemplo, en un entorno de CI donde solo
    está el código), se utiliza una copia embebida que reproduce el contenido
    exacto del archivo original. Esto garantiza que el sistema funcione
    aunque el directorio docs/ no esté presente en todos los entornos.

    Returns:
        Contenido completo del prompt como cadena de texto.
    """
    prompt_path = _resolve_prompt_path()
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        logger.warning("prompt_file_not_found", path=str(prompt_path))
        # Fallback inline: réplica del contenido de docs/prompt_gemini.txt (C-27).
        return (
            "INSTRUCCIÓN DE ROL\n"
            "Eres un agente especializado en clasificación de incidentes técnicos en español rioplatense.\n\n"
            "DEFINICIÓN DE SECTORES\n"
            "El incidente debe clasificarse en UNO de estos cinco sectores:\n\n"
            "1. SEGURIDAD INFORMATICA\n"
            "   Abarca: ciberseguridad, firewall, VPN, malware, phishing, accesos e identidad corporativa\n"
            '   Ejemplo: "Detectamos un ataque de phishing y actividad de malware en la red."\n\n'
            "2. SOPORTE TECNICO HARDWARE\n"
            "   Abarca: equipamiento de usuarios, periféricos, impresoras y fallas físicas\n"
            '   Ejemplo: "Mi impresora no imprime. Sale papel atascado. Código de error 13."\n\n'
            "3. SOPORTE TECNICO SOFTWARE\n"
            "   Abarca: aplicaciones de escritorio, instalación, configuración y asistencia remota\n"
            '   Ejemplo: "No puedo abrir Outlook, la aplicación se traba."\n\n'
            "4. BASES DE DATOS\n"
            "   Abarca: motores de datos, consultas, replicación, backup y recuperación\n"
            '   Ejemplo: "El backup de la base de datos falló durante la replicación."\n\n'
            "5. SISTEMAS\n"
            "   Abarca: infraestructura, redes, servidores y servicios de plataforma\n"
            '   Ejemplo: "Se cayó el servidor de correo. Error SMTP timeout en la red."\n\n'
            "FORMATO DE RESPUESTA\n"
            "Devuelve SIEMPRE un JSON válido con exactamente dos campos:\n"
            '{\n  "categoría": "Seguridad Informatica|Soporte Tecnico Hardware|Soporte Tecnico Software|Bases de Datos|Sistemas",\n  "confianza": 0.0-1.0\n}\n\n'
            "INSTRUCCIÓN DE DECISIÓN\n"
            "Analiza la descripción del incidente y asigna un sector único de las cinco opciones listadas.\n"
            "Si la descripción contiene elementos de múltiples sectores, elige el que sea DOMINANTE.\n\n"
            "CASING\n"
            'El valor del campo "categoría" en tu respuesta JSON debe ser EXACTAMENTE uno de estos cinco strings,\n'
            "respetando el casing (mayúsculas/minúsculas). Los sectores NO llevan tildes:\n"
            '  "Seguridad Informatica"\n'
            '  "Soporte Tecnico Hardware"\n'
            '  "Soporte Tecnico Software"\n'
            '  "Bases de Datos"\n'
            '  "Sistemas"\n'
            'No uses "SISTEMAS", "sistemas" ni variantes con tilde como "Soporte Técnico". Usa exactamente los strings listados.\n\n'
            "VALIDACIÓN\n"
            "- Devuelve SIEMPRE un JSON válido sin texto adicional\n"
            "- No incluyas comentarios, explicaciones ni markdown\n"
            "- Si tu confianza es menor a 0.5, devuelve un valor de confianza bajo pero mantén la categoría"
        )


# Prompt cargado al importar el módulo para evitar I/O en cada clasificación
_PROMPT_TEMPLATE = _load_prompt()


def _validate_gemini_response(raw: str) -> dict:
    """
    Valida la respuesta de Gemini según los criterios del Anexo H §H.3.

    Ejecuta los cuatro controles de validación en orden secuencial:
        1. Parseo JSON: la respuesta debe ser JSON válido (json.loads sin error).
        2. Campo "categoría": debe existir con valor string en el conjunto válido.
        3. Campo "confianza": debe existir con valor numérico en [0.0, 1.0].

    Si cualquier control falla, lanza GeminiResponseInvalidError con un
    mensaje descriptivo del fallo específico. El sistema de logging registra
    el error y el mecanismo de fallback toma el control.

    Args:
        raw: Texto crudo devuelto por la API de Gemini.

    Returns:
        Diccionario validado con las claves "categoría" y "confianza".

    Raises:
        GeminiResponseInvalidError: Si la respuesta no supera cualquier control.
    """
    # Control 1: Validez sintáctica JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GeminiResponseInvalidError(
            f"JSON inválido: {exc}", {"raw_response": raw[:200]}
        ) from exc

    # Control 2a: Presencia del campo "categoría"
    if "categoría" not in data:
        raise GeminiResponseInvalidError(
            "Falta campo 'categoría'", {"raw_response": raw[:200]}
        )

    # Control 2b: Valor de "categoría" dentro del conjunto permitido
    categoria = data["categoría"]
    if not isinstance(categoria, str) or categoria not in _VALID_CATEGORIES:
        raise GeminiResponseInvalidError(
            f"Categoría inválida: {categoria!r}",
            {"raw_response": raw[:200], "categoria": categoria},
        )

    # Control 3a: Presencia del campo "confianza"
    if "confianza" not in data:
        raise GeminiResponseInvalidError(
            "Falta campo 'confianza'", {"raw_response": raw[:200]}
        )

    # Control 3b: Tipo numérico y rango [0.0, 1.0] para "confianza"
    # `bool` es subclase de `int` en Python: se rechaza explícitamente para que
    # `true`/`false` de JSON no pasen como confianza válida (0.0/1.0).
    confianza = data["confianza"]
    if (
        isinstance(confianza, bool)
        or not isinstance(confianza, (int, float))
        or not (0.0 <= float(confianza) <= 1.0)
    ):
        raise GeminiResponseInvalidError(
            f"Confianza inválida: {confianza!r}",
            {"raw_response": raw[:200], "confianza": confianza},
        )

    return {"categoría": categoria, "confianza": float(confianza)}


class GeminiClassifier(BaseClassifier):
    """
    Clasificador semántico basado en Gemini 3.6 Flash.

    Implementa la Etapa 2 del pipeline híbrido. Construye el prompt combinando
    la plantilla fija (docs/prompt_gemini.txt) con la descripción del incidente
    e invoca la API de Gemini con los parámetros exactamente calibrados:
        temperature=0.3, top_p=0.9, max_output_tokens=100, candidate_count=1, timeout=10s.

    Garantías de resiliencia:
        - Respuesta inválida → retorna fallback (confianza=0.0).
        - Timeout           → propaga GeminiTimeoutError al HybridClassifier.
        - API no disponible → propaga GeminiUnavailableError al HybridClassifier.
    """

    def __init__(
        self,
        *,
        client: genai.Client | None = None,
        sleep: Callable[[float], Awaitable[None]] | None = None,
        monotonic: Callable[[], float] | None = None,
        random_fn: Callable[[], float] | None = None,
    ) -> None:
        """
        Inicializa el clasificador configurando el cliente de Gemini con los
        parámetros definidos en Settings (que reproducen docs/parameters_gemini.md).

        Los parametros `sleep`, `monotonic` y `random_fn` son inyectables para que
        el bucle de reintento sea testeable de forma determinista (sin esperas
        reales ni aleatoriedad no reproducible). En produccion se usan los del
        sistema.
        """
        settings = get_settings()
        # Cliente compartido y reutilizado (BE B7); se cierra en el shutdown.
        # Inyectable para tests (cliente genai simulado, sin red ni costo).
        self._client = client if client is not None else get_genai_client()

        # Modelo configurable via settings.gemini_model (default: Gemini 3.6 Flash)
        self._model_name = settings.gemini_model

        # Configuración de generación con parámetros calibrados (Anexo H §H.2).
        # Safety settings parcialmente desactivados para permitir terminología
        # técnica que podría ser bloqueada por los filtros de contenido predeterminados
        # (ej. "se cayó", "atasco", "corte de red"). Ver Anexo H §H.2.
        self._generation_config = genai_types.GenerateContentConfig(
            temperature=settings.gemini_temperature,         # 0.3: reduce variabilidad
            top_p=settings.gemini_top_p,                     # 0.9: nucleus sampling rioplatense
            max_output_tokens=settings.gemini_max_output_tokens,  # 100: suficiente para JSON
            candidate_count=settings.gemini_candidate_count,      # 1: optimiza latencia
            # Modo JSON: la API restringe la salida a JSON puro, sin fences Markdown
            # (```json ... ```) que el validador del Anexo H §H.3 rechaza por diseño.
            response_mime_type="application/json",
            # Schema estructurado: restringe la respuesta a exactamente los 3 strings
            # canónicos con su casing correcto. Evita que Gemini devuelva "SISTEMAS"
            # u otras variantes de mayúsculas que el validador del Anexo H §H.3 rechaza
            # por ser case-sensitive. El enum actúa en el ORIGEN (request), complementando
            # la instrucción del prompt (defensa en profundidad). Ver docs/parameters_gemini.md.
            response_schema=genai_types.Schema(
                type="OBJECT",
                properties={
                    "categoría": genai_types.Schema(
                        type="STRING",
                        enum=list(SECTORES_CANONICOS),
                    ),
                    "confianza": genai_types.Schema(
                        type="NUMBER",
                    ),
                },
                required=["categoría", "confianza"],
            ),
            # Los tokens de razonamiento ("thinking") del modelo cuentan contra
            # max_output_tokens=100, truncando la respuesta visible. Presupuesto
            # 0 desactiva el razonamiento: respuesta directa, completa y de menor latencia.
            thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            safety_settings=[
                genai_types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                genai_types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                genai_types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                genai_types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
            ],
        )

        self._timeout = settings.gemini_timeout_seconds       # configurable (default 30s): límite de latencia
        self._human_review_threshold = settings.human_review_threshold  # 0.70

        # Resiliencia (c-58): reintento acotado con backoff+jitter y presupuesto total.
        self._max_retries = settings.gemini_max_retries
        self._retry_base_delay = settings.gemini_retry_base_delay_seconds
        self._retry_max_delay = settings.gemini_retry_max_delay_seconds
        self._retry_jitter_ratio = settings.gemini_retry_jitter_ratio
        self._total_timeout = settings.gemini_total_timeout_seconds
        self._sleep = sleep or asyncio.sleep
        self._monotonic = monotonic or time.monotonic
        self._random = random_fn or random.random

    def _backoff_delay(self, attempt: int) -> float:
        """
        Espera antes del reintento `attempt+1`: exponencial, topeada y con jitter.

        `min(base * 2**(attempt-1), max_delay)`, multiplicado por un factor de
        jitter en `[1 - jitter_ratio, 1]`. Con `jitter_ratio <= 0` la espera es
        determinista (util para tests).

        Args:
            attempt: numero de intento que acaba de fallar (1-based).

        Returns:
            Segundos de espera antes del proximo intento.
        """
        raw = self._retry_base_delay * (2 ** (attempt - 1))
        capped = min(raw, self._retry_max_delay)
        if self._retry_jitter_ratio <= 0:
            return capped
        return capped * (1.0 - self._retry_jitter_ratio * self._random())


    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Clasifica el incidente invocando la API de Gemini 3.6 Flash.

        Construye el prompt completo concatenando la plantilla con la descripción,
        invoca la API con un reintento ACOTADO ante fallas transitorias, valida la
        respuesta y retorna el resultado estructurado.

        Flujo de manejo de errores:
            1. GeminiResponseInvalidError → retorna fallback silenciosamente (terminal).
            2. Falla transitoria (503/429/5xx/timeout) → reintenta con backoff+jitter
               mientras queden intentos y presupuesto de latencia total.
            3. Agotados los intentos/presupuesto → propaga GeminiTimeoutError (timeout)
               o GeminiUnavailableError (resto), para el fallback del HybridClassifier.
            4. Falla terminal (400/401/403) → un solo intento, propaga
               GeminiUnavailableError sin reintentar.

        Args:
            descripcion: Texto pseudonimizado del incidente.

        Returns:
            ClasificacionResult con la categoría, confianza y etapa="gemini",
            o un resultado de fallback si la clasificación falló.
        """
        # El prompt sigue el formato exacto especificado en docs/prompt_gemini.txt
        prompt = f"{_PROMPT_TEMPLATE}\n\nDESCRIPCIÓN DEL INCIDENTE:\n{descripcion}"
        max_attempts = max(1, self._max_retries + 1)
        started_at = self._monotonic()
        attempt = 0
        last_reason = "unavailable"
        last_error: BaseException | None = None

        while attempt < max_attempts:
            attempt += 1
            raw_response: str | None = None

            try:
                # asyncio.wait_for garantiza el límite de latencia POR INTENTO
                # (asyncio.TimeoutError == TimeoutError en Python ≥3.11).
                response = await asyncio.wait_for(
                    self._client.aio.models.generate_content(
                        model=self._model_name,
                        contents=prompt,
                        config=self._generation_config,
                    ),
                    timeout=self._timeout,
                )
                raw_response = response.text.strip()

                # Validar la respuesta según el protocolo del Anexo H §H.3
                validated = _validate_gemini_response(raw_response)

            except GeminiResponseInvalidError as exc:
                # Respuesta inválida: terminal (no se reintenta); fallback vigente.
                logger.error(
                    "gemini_response_invalid",
                    message=exc.message,
                    details=exc.details,
                )
                return self._fallback(raw_response)

            except TimeoutError as exc:
                # Timeout transitorio: elegible para reintento.
                last_reason = "timeout"
                last_error = exc
                logger.warning(
                    "gemini_timeout", timeout_s=self._timeout, attempt=attempt
                )

            except Exception as exc:
                if not _is_transient_error(exc):
                    # Falla terminal: un solo intento, sin reintento.
                    logger.error(
                        "gemini_retry_terminal",
                        attempt=attempt,
                        error_class=type(exc).__name__,
                    )
                    raise GeminiUnavailableError(
                        "Gemini API no disponible."
                    ) from exc
                last_reason = "transient"
                last_error = exc
                logger.warning(
                    "gemini_transient_error",
                    attempt=attempt,
                    error_class=type(exc).__name__,
                )

            else:
                # Éxito: construir el resultado y salir del bucle.
                confianza = validated["confianza"]
                requiere_revision = confianza < self._human_review_threshold
                logger.info(
                    "gemini_classified",
                    categoria=validated["categoría"],
                    confianza=confianza,
                    requiere_revision_humana=requiere_revision,
                )
                return ClasificacionResult(
                    sector_predicho=validated["categoría"],
                    confianza=confianza,
                    etapa="gemini",
                    requiere_revision_humana=requiere_revision,
                    respuesta_raw=raw_response,  # Guardado para auditoría en clasificacion_log
                )

            # Fallo transitorio: decidir si se agenda otro intento.
            if attempt >= max_attempts:
                break
            delay = self._backoff_delay(attempt)
            remaining = self._total_timeout - (self._monotonic() - started_at)
            if remaining <= 0 or delay >= remaining:
                # Presupuesto de latencia total agotado: cortar sin agotar intentos.
                logger.warning(
                    "gemini_retry_budget_exhausted",
                    attempts=attempt,
                    remaining_seconds=round(max(remaining, 0.0), 4),
                )
                break
            logger.info(
                "gemini_retry_scheduled",
                attempt=attempt,
                next_attempt=attempt + 1,
                delay_seconds=round(delay, 4),
                reason=last_reason,
            )
            await self._sleep(delay)

        logger.warning(
            "gemini_retry_exhausted", attempts=attempt, reason=last_reason
        )
        if last_reason == "timeout":
            raise GeminiTimeoutError(
                f"Gemini no respondió en {self._timeout}s."
            ) from last_error
        raise GeminiUnavailableError("Gemini API no disponible.") from last_error


    @staticmethod
    def _fallback(raw: str | None) -> ClasificacionResult:
        """
        Construye un resultado de fallback seguro ante falla del clasificador.

        Implementa el procedimiento de rechazo del Anexo H §H.3:
            - Confianza = 0.0 (indica fallo explícito).
            - requiere_revision_humana = True (operador debe intervenir).
            - La categoría placeholder "Sistemas" no tiene valor semántico;
              debe ser corregida por el operador durante la revisión.

        Args:
            raw: Respuesta cruda de Gemini (puede ser None si hubo error de red).

        Returns:
            ClasificacionResult de fallback para ser persistido como auditoría.
        """
        return ClasificacionResult(
            sector_predicho="Sistemas",    # Placeholder sin valor semántico real
            confianza=0.0,                 # Indica fallo explícito del clasificador
            etapa="fallback",
            requiere_revision_humana=True, # Revisión humana obligatoria
            respuesta_raw=raw,             # Se conserva para diagnóstico
        )
