"""
Etapa 2 del clasificador híbrido: clasificación semántica con Gemini 2.5 Flash.

Responsabilidad:
    Implementa la segunda etapa del pipeline híbrido. Invoca la API de
    Google Gemini 2.5 Flash con los parámetros exactos documentados en:
        - docs/parameters_gemini.md
        - docs/prompt_gemini.txt
        - Anexo H de la tesis (ANEXO_H_Prompt_Gemini_Especificacion.md)

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
        3. Valor de "categoría" dentro del conjunto {Sistemas, Operaciones, Soporte Técnico}.
        4. Valor de "confianza" numérico en el rango [0.0, 1.0].
"""

import json
from pathlib import Path

import google.generativeai as genai

from app.classifiers.base import BaseClassifier
from app.config.settings import get_settings
from app.core.exceptions import (
    GeminiResponseInvalidError,
    GeminiTimeoutError,
    GeminiUnavailableError,
)
from app.core.logging import get_logger
from app.schemas.clasificacion import ClasificacionResult

logger = get_logger(__name__)

# Conjunto de categorías válidas. Debe coincidir exactamente con los valores
# definidos en el prompt (docs/prompt_gemini.txt), incluyendo tildes y mayúsculas.
_VALID_CATEGORIES = frozenset({"Sistemas", "Operaciones", "Soporte Técnico"})

# Ruta al archivo de prompt documentado en la tesis. Se carga una sola vez
# al importar el módulo y se reutiliza en todas las invocaciones.
_PROMPT_PATH = Path(__file__).parent.parent.parent / "docs" / "prompt_gemini.txt"


def _load_prompt() -> str:
    """
    Carga el prompt desde el archivo docs/prompt_gemini.txt.

    Si el archivo no existe (por ejemplo, en un entorno de CI donde solo
    está el código), se utiliza una copia embebida que reproduce el contenido
    exacto del archivo original. Esto garantiza que el sistema funcione
    aunque el directorio docs/ no esté presente en todos los entornos.

    Returns:
        Contenido completo del prompt como cadena de texto.
    """
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        logger.warning("prompt_file_not_found", path=str(_PROMPT_PATH))
        # Fallback inline: réplica exacta del contenido de docs/prompt_gemini.txt
        return (
            "INSTRUCCIÓN DE ROL\n"
            "Eres un agente especializado en clasificación de incidentes técnicos en español rioplatense.\n\n"
            "DEFINICIÓN DE CATEGORÍAS\n"
            "El incidente debe clasificarse en UNA de estas tres categorías:\n\n"
            "1. SISTEMAS\n"
            "   Abarca: infraestructura, redes, servidores, bases de datos, ciberseguridad, autenticación corporativa\n"
            '   Ejemplo: "Se cayó el servidor de correo. No pueden conectarse los clientes de Outlook. Error SMTP timeout."\n\n'
            "2. OPERACIONES\n"
            "   Abarca: procesos compartidos, gestión de servicios, planificación, continuidad operativa, trámites administrativos\n"
            '   Ejemplo: "Necesitamos reservar una sala de 15 personas para reunión el próximo miércoles a las 14 horas."\n\n'
            "3. SOPORTE TÉCNICO\n"
            "   Abarca: equipamiento de usuarios, periféricos, software cliente, asistencia remota, impresoras\n"
            '   Ejemplo: "Mi impresora no imprime. Sale papel atascado. Código de error 13."\n\n'
            "FORMATO DE RESPUESTA\n"
            "Devuelve SIEMPRE un JSON válido con exactamente dos campos:\n"
            '{\n  "categoría": "Sistemas|Operaciones|Soporte Técnico",\n  "confianza": 0.0-1.0\n}\n\n'
            "INSTRUCCIÓN DE DECISIÓN\n"
            "Analiza la descripción del incidente y asigna una categoría única de las tres opciones listadas.\n"
            "Si la descripción contiene elementos de múltiples categorías, elige la que sea DOMINANTE.\n\n"
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
    confianza = data["confianza"]
    if not isinstance(confianza, (int, float)) or not (0.0 <= float(confianza) <= 1.0):
        raise GeminiResponseInvalidError(
            f"Confianza inválida: {confianza!r}",
            {"raw_response": raw[:200], "confianza": confianza},
        )

    return {"categoría": categoria, "confianza": float(confianza)}


class GeminiClassifier(BaseClassifier):
    """
    Clasificador semántico basado en Gemini 2.5 Flash.

    Implementa la Etapa 2 del pipeline híbrido. Construye el prompt combinando
    la plantilla fija (docs/prompt_gemini.txt) con la descripción del incidente
    e invoca la API de Gemini con los parámetros exactamente calibrados:
        temperature=0.3, top_p=0.9, max_output_tokens=100, candidate_count=1, timeout=10s.

    Garantías de resiliencia:
        - Respuesta inválida → retorna fallback (confianza=0.0).
        - Timeout           → propaga GeminiTimeoutError al HybridClassifier.
        - API no disponible → propaga GeminiUnavailableError al HybridClassifier.
    """

    def __init__(self) -> None:
        """
        Inicializa el clasificador configurando el cliente de Gemini con los
        parámetros definidos en Settings (que reproducen docs/parameters_gemini.md).
        """
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)

        # Modelo especificado en la tesis: Gemini 2.5 Flash (marzo 2026)
        self._model = genai.GenerativeModel(settings.gemini_model)

        # Configuración de generación con parámetros calibrados (Anexo H §H.2)
        self._generation_config = genai.types.GenerationConfig(
            temperature=settings.gemini_temperature,         # 0.3: reduce variabilidad
            top_p=settings.gemini_top_p,                     # 0.9: nucleus sampling rioplatense
            max_output_tokens=settings.gemini_max_output_tokens,  # 100: suficiente para JSON
            candidate_count=settings.gemini_candidate_count,      # 1: optimiza latencia
        )

        # Safety settings parcialmente desactivados para permitir terminología
        # técnica que podría ser bloqueada por los filtros de contenido predeterminados
        # (ej. "se cayó", "atasco", "corte de red"). Ver Anexo H §H.2.
        self._safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        self._timeout = settings.gemini_timeout_seconds       # 10s: límite de latencia
        self._human_review_threshold = settings.human_review_threshold  # 0.70

    async def classify(self, descripcion: str) -> ClasificacionResult:
        """
        Clasifica el incidente invocando la API de Gemini 2.5 Flash.

        Construye el prompt completo concatenando la plantilla con la descripción,
        invoca la API, valida la respuesta y retorna el resultado estructurado.

        Flujo de manejo de errores:
            1. GeminiResponseInvalidError → retorna fallback silenciosamente.
            2. TimeoutError              → propaga GeminiTimeoutError.
            3. Cualquier otra excepción  → propaga GeminiUnavailableError.

        Args:
            descripcion: Texto pseudonimizado del incidente.

        Returns:
            ClasificacionResult con la categoría, confianza y etapa="gemini",
            o un resultado de fallback si la clasificación falló.
        """
        # El prompt sigue el formato exacto especificado en docs/prompt_gemini.txt
        prompt = f"{_PROMPT_TEMPLATE}\n\nDESCRIPCIÓN DEL INCIDENTE:\n{descripcion}"
        raw_response: str | None = None

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=self._generation_config,
                safety_settings=self._safety_settings,
                request_options={"timeout": self._timeout},
            )
            raw_response = response.text.strip()

            # Validar la respuesta según el protocolo del Anexo H §H.3
            validated = _validate_gemini_response(raw_response)

        except GeminiResponseInvalidError as exc:
            # Respuesta con formato inválido: activar fallback sin propagar la excepción
            logger.error(
                "gemini_response_invalid",
                message=exc.message,
                details=exc.details,
            )
            return self._fallback(raw_response)

        except TimeoutError as exc:
            # Tiempo de espera agotado: propagar para que el HybridClassifier maneje
            logger.warning("gemini_timeout", timeout_s=self._timeout)
            raise GeminiTimeoutError(
                f"Gemini no respondió en {self._timeout}s."
            ) from exc

        except Exception as exc:
            # API inaccesible u otro error inesperado: propagar como no disponible
            logger.error("gemini_unavailable", exc_info=exc)
            raise GeminiUnavailableError("Gemini API no disponible.") from exc

        confianza = validated["confianza"]

        # Determinar si la confianza supera el umbral para revisión humana
        requiere_revision = confianza < self._human_review_threshold

        logger.info(
            "gemini_classified",
            categoria=validated["categoría"],
            confianza=confianza,
            requiere_revision_humana=requiere_revision,
        )

        return ClasificacionResult(
            categoria=validated["categoría"],
            confianza=confianza,
            etapa="gemini",
            requiere_revision_humana=requiere_revision,
            respuesta_raw=raw_response,  # Guardado para auditoría en clasificacion_log
        )

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
            categoria="Sistemas",          # Placeholder sin valor semántico real
            confianza=0.0,                 # Indica fallo explícito del clasificador
            etapa="fallback",
            requiere_revision_humana=True, # Revisión humana obligatoria
            respuesta_raw=raw,             # Se conserva para diagnóstico
        )
