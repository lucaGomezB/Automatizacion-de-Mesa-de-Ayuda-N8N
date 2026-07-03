"""
Jerarquía de excepciones de dominio del sistema.

Responsabilidad:
    Define una taxonomía de excepciones estructuradas que representan
    condiciones de error propias del dominio de negocio. Cada excepción
    lleva información contextual (mensaje + detalles) que permite al
    manejador de errores HTTP construir respuestas informativas sin
    acceder a trazas de pila internas.

Diseño:
    La jerarquía está organizada en tres grupos funcionales:
        - Clasificador: errores originados en las etapas del pipeline híbrido.
        - Persistencia: errores propios de la capa de repositorios.
        - Aplicación: errores de validación y consistencia de dominio.

    Todas las excepciones heredan de AppBaseException, lo que permite
    capturarlas en bloque en el manejador de errores global cuando sea necesario.
"""

from typing import Any


class AppBaseException(Exception):
    """
    Excepción base para todos los errores de dominio del sistema.

    Extiende Exception con un campo 'details' estructurado que permite
    transportar información adicional (por ejemplo, el identificador de la
    entidad no encontrada, la respuesta malformada de Gemini, etc.) desde
    el punto de falla hasta el manejador HTTP sin acoplar ambas capas.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ── Grupo: Clasificador ───────────────────────────────────────────────────────

class ClassificationError(AppBaseException):
    """
    Error genérico del pipeline de clasificación.

    Se utiliza como base para las excepciones específicas de Gemini
    y como captura de último recurso dentro del HybridClassifier.
    """


class GeminiTimeoutError(ClassificationError):
    """
    Gemini no respondió dentro del límite de tiempo configurado (10 segundos).

    Según la especificación del Anexo H, este caso debe activar el mecanismo
    de fallback: asignar confianza 0.0 y marcar el incidente para revisión humana.
    """


class GeminiResponseInvalidError(ClassificationError):
    """
    La respuesta de Gemini no superó la validación de formato establecida en el Anexo H §H.3.

    Puede ocurrir cuando el modelo devuelve JSON malformado, una categoría no
    reconocida, un valor de confianza fuera del rango [0.0, 1.0], o markdown
    envolviendo el JSON esperado.
    """


class GeminiUnavailableError(ClassificationError):
    """
    La API de Gemini es inalcanzable o devolvió un error no recuperable.

    Este estado activa el mismo mecanismo de fallback que GeminiTimeoutError,
    garantizando que el sistema no se bloquee ante indisponibilidad del servicio externo.
    """


# ── Grupo: Persistencia ───────────────────────────────────────────────────────

class RepositoryError(AppBaseException):
    """
    Error genérico de la capa de persistencia.

    Actúa como clase base para excepciones más específicas relacionadas
    con operaciones de lectura o escritura en la base de datos.
    """


class EntityNotFoundError(RepositoryError):
    """
    La entidad solicitada no existe en la base de datos.

    Incluye el nombre del modelo y el identificador buscado en el campo
    'details', lo que permite que el manejador HTTP construya un mensaje
    404 preciso sin acceso directo a la capa de persistencia.
    """

    def __init__(self, entity: str, identifier: Any) -> None:
        super().__init__(
            f"{entity} with identifier '{identifier}' not found.",
            {"entity": entity, "identifier": str(identifier)},
        )
        self.entity = entity
        self.identifier = identifier


class DuplicateEntityError(RepositoryError):
    """
    Intento de inserción que viola una restricción de unicidad en la base de datos.

    Se lanza cuando se intenta crear un registro con un valor que ya existe
    en una columna con restricción UNIQUE (por ejemplo, nombre de sector).
    """


# ── Grupo: Aplicación ─────────────────────────────────────────────────────────

class IncidentValidationError(AppBaseException):
    """
    El payload del incidente no pasó la validación de reglas de negocio.

    Distinto de los errores de validación de Pydantic (422 automático),
    este error representa violaciones de reglas de dominio que no pueden
    expresarse únicamente con restricciones de tipo.
    """


class SectorNotFoundError(AppBaseException):
    """El sector referenciado no existe en el catálogo de sectores."""


class EstadoNotFoundError(AppBaseException):
    """
    El estado referenciado no existe en el catálogo de estados del ciclo de vida.

    Crítico para la creación de incidentes: si el estado 'nuevo' no está
    presente en la base de datos, la operación debe fallar con este error.
    """


class CanalOrigenNotFoundError(AppBaseException):
    """El canal de origen referenciado no existe en el catálogo correspondiente."""
