"""
Módulo de configuración del sistema de logging estructurado.

Responsabilidad:
    Inicializa el logging de la aplicación utilizando la librería structlog,
    que emite eventos en formato JSON (producción) o en formato coloreado
    legible por humanos (desarrollo). Los eventos incluyen automáticamente
    metadatos del contexto de la aplicación (nombre, versión, entorno),
    lo que facilita la correlación y el filtrado en herramientas de
    observabilidad como Grafana Loki o ELK Stack.

Diseño:
    - Los procesadores compartidos (shared_processors) se aplican tanto
      a los eventos de structlog como a los de la librería estándar logging,
      unificando el formato de salida de todas las dependencias del sistema.
    - La función get_logger() es el punto de acceso para obtener instancias
      de logger en cualquier módulo de la aplicación.

Uso:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("evento_clasificacion", categoria="Sistemas", confianza=0.95)
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.config.settings import get_settings


def _add_app_context(logger: Any, method: str, event_dict: EventDict) -> EventDict:
    """
    Procesador de structlog que inyecta metadatos de la aplicación en cada evento.

    Agrega los campos 'app', 'version' y 'environment' a todos los mensajes
    de log, permitiendo filtrar eventos por versión desplegada o entorno
    (producción, staging, desarrollo) en sistemas de observabilidad centralizados.
    """
    settings = get_settings()
    event_dict["app"] = settings.app_name
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    return event_dict


def _drop_color_message_key(logger: Any, method: str, event_dict: EventDict) -> EventDict:
    """
    Procesador de structlog que elimina la clave 'color_message' si está presente.

    Esta clave es inyectada por uvicorn en su propio sistema de logging y
    es redundante en el contexto de logging estructurado JSON. Su presencia
    contaminaría la salida con datos innecesarios.
    """
    event_dict.pop("color_message", None)
    return event_dict


def configure_logging() -> None:
    """
    Configura el sistema de logging global de la aplicación.

    Esta función debe invocarse una sola vez, durante el evento de inicio
    (lifespan) de FastAPI, antes de que la aplicación comience a procesar
    solicitudes. Realiza las siguientes acciones:

        1. Define la cadena de procesadores compartidos entre structlog y stdlib.
        2. Selecciona el renderer según el formato configurado en Settings.
        3. Conecta structlog con el sistema de logging estándar de Python
           para que las librerías de terceros (SQLAlchemy, httpx) también
           emitan eventos en el formato unificado.
        4. Reduce la verbosidad de librerías ruidosas (uvicorn, sqlalchemy).
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Procesadores aplicados a todos los eventos antes del renderizado final.
    # El orden importa: cada procesador recibe el dict producido por el anterior.
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,       # Agrega vars de contexto async
        structlog.stdlib.add_log_level,                 # Agrega campo "level"
        structlog.stdlib.add_logger_name,               # Agrega nombre del módulo
        structlog.processors.TimeStamper(fmt="iso"),    # Timestamp ISO 8601 UTC
        _add_app_context,                               # Metadatos de la aplicación
        _drop_color_message_key,                        # Limpieza de keys de uvicorn
        structlog.processors.StackInfoRenderer(),       # Renderiza stack traces si existen
    ]

    # Selección del renderer según el entorno configurado
    if settings.log_format == "json":
        # Formato JSON para producción: parseable por Loki, ELK, CloudWatch, etc.
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        # Formato consola con colores para desarrollo local
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Configuración principal de structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,  # Optimización de rendimiento
    )

    # Formatter que aplica la misma cadena de procesadores a eventos de stdlib
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Handler único a stdout para compatibilidad con contenedores Docker
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Reemplazar cualquier handler preexistente en el logger raíz
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Reducir verbosidad de librerías de terceros para mantener logs limpios
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.db_echo else logging.WARNING
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Retorna una instancia de logger estructurado vinculada al módulo indicado.

    Args:
        name: Nombre del módulo, típicamente se pasa __name__ del módulo llamante.

    Returns:
        Instancia de BoundLogger de structlog lista para emitir eventos.

    Ejemplo de uso:
        logger = get_logger(__name__)
        logger.info("incidente_creado", incidente_id=42, sector="Sistemas")
    """
    return structlog.get_logger(name)
