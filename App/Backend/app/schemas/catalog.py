"""
Schemas Pydantic de solo lectura para las entidades de catálogo.

Responsabilidad:
    Define las representaciones serializables de Sector, Estado y CanalOrigen
    destinadas exclusivamente a la lectura y serialización en respuestas HTTP.
    Ninguno de estos schemas acepta escritura directa; los catálogos son datos
    de referencia inmutables en tiempo de ejecución.

    El atributo from_attributes=True habilita la construcción de estas instancias
    a partir de objetos ORM de SQLAlchemy sin necesidad de conversión manual,
    preservando la separación entre la capa de persistencia y la API.
"""

from pydantic import BaseModel, ConfigDict


class SectorRead(BaseModel):
    """
    Proyección de solo lectura de un sector responsable.

    Utilizada en las respuestas de endpoints de incidentes y clasificaciones
    para presentar el sector asignado sin exponer detalles internos del ORM.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str           # Uno de: "Sistemas", "Operaciones", "Soporte Técnico"
    descripcion: str | None


class EstadoRead(BaseModel):
    """
    Proyección de solo lectura de un estado del ciclo de vida del incidente.

    El campo es_terminal permite a los clientes de la API identificar si el
    incidente llegó a un estado final sin necesidad de lógica adicional.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str           # Uno de: "nuevo", "en proceso", "en espera", "resuelto", "cerrado"
    descripcion: str | None
    es_terminal: bool     # True únicamente para el estado "cerrado"


class CanalOrigenRead(BaseModel):
    """
    Proyección de solo lectura del canal de ingreso del incidente.

    Informa al consumidor de la API a través de qué medio fue recibido
    el reporte: correo electrónico, formulario web o llamada telefónica.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str           # Uno de: "correo electrónico", "formulario web", "llamada telefónica"
    descripcion: str | None
