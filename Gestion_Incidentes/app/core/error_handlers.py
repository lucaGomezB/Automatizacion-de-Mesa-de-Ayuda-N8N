"""
Manejadores de errores HTTP de la aplicación.

Responsabilidad:
    Registra en la instancia de FastAPI los manejadores de excepción que
    transforman las excepciones de dominio (definidas en core/exceptions.py)
    en respuestas HTTP con código de estado y cuerpo JSON estandarizados.

    El cuerpo de error sigue siempre la estructura:
        {"error": {"code": "CODIGO_ERROR", "message": "...", "details": {...}}}

    Esto facilita que los consumidores de la API (N8N, interfaces web, clientes
    de prueba) procesen los errores de forma uniforme sin necesidad de parsear
    mensajes de texto libre.

Decisión de diseño:
    Los manejadores están ordenados de más específico a más genérico. FastAPI
    evalúa los handlers en el orden en que fueron registrados, por lo que las
    subclases deben registrarse antes que sus superclases para ser alcanzadas.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppBaseException,
    ClassificationError,
    EntityNotFoundError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    IncidentValidationError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_body(code: str, message: str, details: dict | None = None) -> dict:
    """
    Construye el cuerpo JSON estándar de respuesta de error.

    Args:
        code: Identificador corto de la condición de error (ej. "NOT_FOUND").
        message: Descripción legible del error.
        details: Información estructurada adicional (opcional).

    Returns:
        Diccionario listo para ser serializado como JSON en la respuesta HTTP.
    """
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_error_handlers(app: FastAPI) -> None:
    """
    Registra todos los manejadores de excepción en la instancia de FastAPI.

    Debe llamarse una sola vez durante la inicialización de la aplicación,
    antes de que esta comience a recibir solicitudes. Se invoca desde
    la función de fábrica create_app() en main.py.

    Args:
        app: La instancia de FastAPI sobre la que se registran los handlers.
    """

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        """Convierte EntityNotFoundError en respuesta 404 con detalles de la entidad."""
        return JSONResponse(
            status_code=404,
            content=_error_body("NOT_FOUND", exc.message, exc.details),
        )

    @app.exception_handler(IncidentValidationError)
    async def validation_error_handler(
        request: Request, exc: IncidentValidationError
    ) -> JSONResponse:
        """Convierte errores de validación de dominio en respuesta 422."""
        return JSONResponse(
            status_code=422,
            content=_error_body("VALIDATION_ERROR", exc.message, exc.details),
        )

    @app.exception_handler(GeminiTimeoutError)
    async def gemini_timeout_handler(
        request: Request, exc: GeminiTimeoutError
    ) -> JSONResponse:
        """
        Informa al cliente que el clasificador no respondió en tiempo.

        Se devuelve 503 (Service Unavailable) para que los sistemas
        intermedios (como N8N) puedan aplicar reintentos con backoff.
        """
        logger.warning("gemini_timeout", path=str(request.url))
        return JSONResponse(
            status_code=503,
            content=_error_body("CLASSIFIER_TIMEOUT", exc.message),
        )

    @app.exception_handler(GeminiUnavailableError)
    async def gemini_unavailable_handler(
        request: Request, exc: GeminiUnavailableError
    ) -> JSONResponse:
        """Informa al cliente que la API de Gemini no está disponible."""
        logger.error("gemini_unavailable", path=str(request.url))
        return JSONResponse(
            status_code=503,
            content=_error_body("CLASSIFIER_UNAVAILABLE", exc.message),
        )

    @app.exception_handler(ClassificationError)
    async def classification_error_handler(
        request: Request, exc: ClassificationError
    ) -> JSONResponse:
        """
        Captura cualquier error de clasificación no manejado por los handlers
        más específicos de Gemini, como errores internos del clasificador determinístico.
        """
        logger.error("classification_error", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=500,
            content=_error_body("CLASSIFICATION_ERROR", exc.message),
        )

    @app.exception_handler(AppBaseException)
    async def app_base_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        """
        Captura cualquier excepción de dominio no cubierta por los handlers anteriores.
        Actúa como red de seguridad para errores de aplicación no anticipados.
        """
        logger.error("app_error", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", exc.message),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Última línea de defensa: captura cualquier excepción no tipificada.

        Registra la traza completa en el sistema de logging para diagnóstico
        posterior, pero devuelve al cliente un mensaje genérico para evitar
        filtración de detalles internos del sistema.
        """
        logger.exception("unhandled_exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred."),
        )
