"""
Schemas Pydantic para la entidad Incidente.

Responsabilidad:
    Define los contratos de datos de entrada y salida de la API para la
    gestión de incidentes. Cada schema cumple un rol específico dentro
    del ciclo de vida del recurso:

        IncidenteCreate  → Payload de creación recibido desde N8N o API directa.
        IncidenteUpdate  → Payload de actualización parcial (PATCH semántico).
        IncidenteRead    → Representación completa para detalle de un incidente.
        IncidenteListItem → Proyección ligera para listados paginados.

    La separación entre IncidenteRead e IncidenteListItem responde a un
    principio de eficiencia: los listados no necesitan el texto completo de la
    descripción, lo que reduce el tamaño de las respuestas en consultas masivas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.incidente import PrioridadEnum
from app.schemas.catalog import CanalOrigenRead, EstadoRead, SectorRead


class IncidenteCreate(BaseModel):
    """
    Payload de creación de un incidente.

    Aceptado por el endpoint POST /api/v1/incidentes. Puede provenir de:
        - El webhook de N8N tras recibir un correo electrónico en Outlook.
        - El webhook de N8N tras procesar la transcripción de una llamada en Twilio.
        - Una llamada directa a la API desde un cliente externo.

    Validaciones de negocio:
        - La descripción no puede estar en blanco ni ser solo espacios.
        - La longitud mínima de 10 caracteres evita incidentes vacíos de contenido.
        - La longitud máxima de 5000 caracteres previene abusos de almacenamiento.
    """

    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Texto pseudonimizado del incidente. Mínimo 10 caracteres.",
    )
    prioridad: PrioridadEnum = PrioridadEnum.media  # Prioridad por defecto si no se especifica
    canal_origen_id: int | None = None              # Opcional; NULL si el canal es desconocido

    @field_validator("descripcion")
    @classmethod
    def descripcion_not_blank(cls, v: str) -> str:
        """
        Valida que la descripción no sea únicamente espacios en blanco.

        Complementa la restricción min_length de Pydantic, que no detecta
        cadenas compuestas solo por caracteres de espacio. También aplica
        strip() para normalizar el texto antes de su procesamiento por el
        clasificador.
        """
        if not v.strip():
            raise ValueError("La descripción no puede estar vacía o ser solo espacios.")
        return v.strip()


class IncidenteUpdate(BaseModel):
    """
    Payload de actualización parcial de un incidente.

    Todos los campos son opcionales. El servicio aplica únicamente los
    campos con valor no nulo, implementando el patrón PATCH semántico.

    Casos de uso típicos:
        - Cambio de estado por el operador de mesa de ayuda.
        - Reasignación de sector tras revisión manual.
        - Cambio de prioridad ante escalamiento.
        - Marcado o desmarcado de revisión humana requerida.
    """

    prioridad: PrioridadEnum | None = None
    estado_id: int | None = None
    sector_id: int | None = None
    requiere_revision_humana: bool | None = None


class IncidenteRead(BaseModel):
    """
    Representación completa de un incidente para el endpoint de detalle.

    Incluye los objetos relacionados completos (sector, estado, canal_origen)
    en lugar de solo sus IDs, para que el cliente no necesite realizar
    consultas adicionales para obtener sus nombres.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    descripcion: str                   # Texto completo del incidente
    prioridad: PrioridadEnum
    requiere_revision_humana: bool
    created_at: datetime
    updated_at: datetime
    sector: SectorRead | None          # None mientras la clasificación está pendiente
    estado: EstadoRead
    canal_origen: CanalOrigenRead | None


class IncidenteListItem(BaseModel):
    """
    Proyección ligera de un incidente para endpoints de listado.

    Omite el campo 'descripcion' para reducir el tamaño de las respuestas
    cuando se listan múltiples incidentes. Los consumidores que necesiten
    el texto completo deben usar el endpoint de detalle individual.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    prioridad: PrioridadEnum
    requiere_revision_humana: bool
    created_at: datetime
    sector: SectorRead | None
    estado: EstadoRead
