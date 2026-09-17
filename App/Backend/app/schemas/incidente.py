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

from app.constants import es_sector_canonico
from app.models.incidente import PrioridadEnum
from app.schemas.catalog import CanalOrigenRead, EstadoRead, SectorRead

# Marcadores de `origen_evento` que representan la CREACION de un incidente.
# Cualquier otro valor (por ejemplo "notificacion") es un evento que no debe
# crear incidentes y el contrato lo rechaza (C-33, D6).
_ORIGEN_EVENTO_CREACION = frozenset({"creacion", "creacion_incidente"})


class ClasificacionPrecalculada(BaseModel):
    """
    Clasificación ya producida por un emisor externo (N8N) — C-33, D5.

    Todos los campos son opcionales: el bloque hace explícita la intención de
    "clasificación provista" y permite el caso de refinamiento agotado, donde no
    hay sector válido pero sí la marca de revisión humana. Cuando el bloque está
    presente y es válido, el servicio lo persiste y omite la clasificación
    server-side (sin llamada paga).

    Validaciones de borde (D6):
        - `sector_predicho` presente debe pertenecer al vocabulario canónico.
        - `sectores_adicionales` presentes deben ser canónicos.
        - `confianza` presente debe estar en [0.0, 1.0].
    """

    sector_predicho: str | None = None
    sectores_adicionales: list[str] = Field(default_factory=list)
    confianza: float | None = Field(None, ge=0.0, le=1.0)
    requiere_revision_humana: bool | None = None
    origen: str | None = None

    @field_validator("sector_predicho")
    @classmethod
    def _sector_canonico(cls, v: str | None) -> str | None:
        if v is not None and not es_sector_canonico(v):
            raise ValueError(
                f"Sector precalculado '{v}' no pertenece al vocabulario canonico."
            )
        return v

    @field_validator("sectores_adicionales")
    @classmethod
    def _adicionales_canonicos(cls, v: list[str]) -> list[str]:
        invalidos = [s for s in v if not es_sector_canonico(s)]
        if invalidos:
            raise ValueError(
                f"Sectores adicionales fuera del vocabulario canonico: {invalidos}"
            )
        return v


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

    Guardas de costo (C-33):
        - `origen_message_id`: idempotencia del alta por Message-ID de Outlook.
        - `clasificacion`: clasificación precalculada que omite la llamada paga.
        - `origen_evento`: marcador de evento; un evento de notificación se
          rechaza con error de validación para no crear incidentes.
    """

    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Texto pseudonimizado del incidente. Mínimo 10 caracteres.",
    )
    prioridad: PrioridadEnum = PrioridadEnum.media  # Prioridad por defecto si no se especifica
    canal_origen_id: int | None = None              # Opcional; NULL si el canal es desconocido

    # Identificador del mensaje de origen (Message-ID de Outlook). Opcional.
    origen_message_id: str | None = Field(None, max_length=255)

    # Clasificación precalculada provista por el emisor. Opcional: su ausencia
    # conserva la clasificación server-side.
    clasificacion: ClasificacionPrecalculada | None = None

    # Marcador explícito de origen/evento. Sin marcador el payload es un alta
    # directa; un marcador que no sea de creación (p. ej. "notificacion") se
    # rechaza con error de validación.
    origen_evento: str | None = None

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

    @field_validator("origen_evento")
    @classmethod
    def origen_evento_de_creacion(cls, v: str | None) -> str | None:
        """
        Rechaza marcadores de evento que no correspondan a la creación de un
        incidente (por ejemplo, una notificación de clasificación) — C-33, D6.
        """
        if v is not None and v not in _ORIGEN_EVENTO_CREACION:
            raise ValueError(
                f"El evento '{v}' no crea incidentes; "
                f"se esperaba uno de {sorted(_ORIGEN_EVENTO_CREACION)}."
            )
        return v

    @field_validator("origen_message_id")
    @classmethod
    def origen_message_id_normalizado(cls, v: str | None) -> str | None:
        """
        Normaliza el identificador vacío a None para que la idempotencia solo
        aplique a identificadores reales (varios NULL conviven bajo el UNIQUE).
        """
        if v is None:
            return None
        v = v.strip()
        return v or None


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

    Política de privacidad (C-03, Ley 25.326):
        Solo se expone 'descripcion_pseudonimizada' (texto con etiquetas PII).
        'descripcion_original' (cifrada, con PII) NO forma parte de esta respuesta.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    descripcion_pseudonimizada: str    # Texto pseudonimizado del incidente (única repr. operativa)
    prioridad: PrioridadEnum
    requiere_revision_humana: bool
    created_at: datetime
    updated_at: datetime
    sector: SectorRead | None          # Sector principal; None mientras la clasificación está pendiente
    sectores_adicionales: list[SectorRead] = Field(default_factory=list)  # Sectores secundarios (C-27)
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
