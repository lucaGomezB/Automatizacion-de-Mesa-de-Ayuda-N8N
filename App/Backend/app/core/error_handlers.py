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
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AppBaseException,
    CanalOrigenNotFoundError,
    ClassificationError,
    DirectorioValidationError,
    EntityNotFoundError,
    EstadoNotFoundError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    IncidentValidationError,
    IncidenteCerradoError,
    SectorNotFoundError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Mapeo de codigos HTTP estandar a codigos estables del envelope de error.
_HTTP_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


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

    @app.exception_handler(EstadoNotFoundError)
    async def estado_not_found_handler(
        request: Request, exc: EstadoNotFoundError
    ) -> JSONResponse:
        """Convierte EstadoNotFoundError en respuesta 404 con el envelope (ERR-003)."""
        return JSONResponse(
            status_code=404,
            content=_error_body("ESTADO_NOT_FOUND", exc.message, exc.details),
        )

    @app.exception_handler(SectorNotFoundError)
    async def sector_not_found_handler(
        request: Request, exc: SectorNotFoundError
    ) -> JSONResponse:
        """Convierte SectorNotFoundError en respuesta 404 con el envelope (ERR-003)."""
        return JSONResponse(
            status_code=404,
            content=_error_body("SECTOR_NOT_FOUND", exc.message, exc.details),
        )

    @app.exception_handler(CanalOrigenNotFoundError)
    async def canal_origen_not_found_handler(
        request: Request, exc: CanalOrigenNotFoundError
    ) -> JSONResponse:
        """Convierte CanalOrigenNotFoundError en respuesta 404 con el envelope (ERR-003)."""
        return JSONResponse(
            status_code=404,
            content=_error_body("CANAL_ORIGEN_NOT_FOUND", exc.message, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        Normaliza toda HTTPException (401/403/404/...) al envelope de error.

        Preserva los headers originales (por ejemplo `WWW-Authenticate` en 401)
        y evita exponer el campo `detail` en la raiz del cuerpo (ERR-001).
        """
        code = _HTTP_CODE_MAP.get(exc.status_code, "HTTP_ERROR")
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code, detail),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Normaliza los errores de validacion de Pydantic/FastAPI al envelope.

        Devuelve 422 con `error.code`/`error.message` y los errores de detalle
        bajo `error.details`, sin el campo `detail` en la raiz (ERR-001).
        """
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "VALIDATION_ERROR",
                "Request validation failed.",
                {"errors": jsonable_encoder(exc.errors())},
            ),
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

    @app.exception_handler(DirectorioValidationError)
    async def directorio_validation_error_handler(
        request: Request, exc: DirectorioValidationError
    ) -> JSONResponse:
        """Convierte errores de validacion del directorio en respuesta 422."""
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

    @app.exception_handler(IncidenteCerradoError)
    async def incidente_cerrado_handler(
        request: Request, exc: IncidenteCerradoError
    ) -> JSONResponse:
        """Convierte IncidenteCerradoError en respuesta 409 Conflict."""
        return JSONResponse(
            status_code=409,
            content=_error_body("INCIDENTE_CERRADO", exc.message, exc.details),
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

        IMPORTANTE — Por qué el try/except alrededor del logger:
            Si este handler lanzara una excepción (p. ej. fallo en structlog
            antes de que configure_logging() haya corrido, o error en un
            procesador), la excepción escapa de ExceptionMiddleware sin enviar
            ninguna respuesta. CORSMiddleware nunca llama a su `send` wrapper y
            ServerErrorMiddleware responde con un 500 sin el header
            Access-Control-Allow-Origin. El try/except garantiza que este
            handler siempre retorna un JSONResponse, sin importar el estado del
            sistema de logging.
        """
        try:
            logger.exception(
                "unhandled_exception",
                path=str(request.url),
                method=request.method,
                exc_info=exc,
            )
        except Exception:
            # El logging nunca debe impedir que se envíe la respuesta de error.
            pass
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred."),
        )
