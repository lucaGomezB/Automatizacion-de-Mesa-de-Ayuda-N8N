"""
Schemas Pydantic relacionados con el clasificador híbrido.

Responsabilidad:
    Define los contratos de datos utilizados en el pipeline de clasificación
    y en los endpoints de auditoría y revisión humana:

        ClasificacionResult  → DTO interno producido por el HybridClassifier.
                               No se persiste directamente; es mapeado al modelo
                               ORM ClasificacionLog por la capa de servicio.
        ClasificacionLogRead → Representación de un registro de auditoría
                               para los endpoints de revisión.
        ClasificacionValidar → Payload del operador humano al corregir una
                               clasificación incorrecta.

    La distinción entre ClasificacionResult (objeto interno) y ClasificacionLogRead
    (objeto de API) preserva el principio de separación entre la lógica de
    clasificación y la representación HTTP.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constants import SECTORES_CANONICOS
from app.schemas.catalog import SectorRead

# Tipo literal que restringe los valores válidos de la etapa del clasificador.
# "deterministic": el filtro de reglas resolvió con confianza >= 0.90.
# "gemini":        Gemini 2.5 Flash clasificó con confianza en rango válido.
# "fallback":      El sistema no pudo clasificar; intervención humana requerida.
# "precalculada":  La clasificación fue provista por un emisor externo (N8N)
#                  y el backend omitió la clasificación server-side (C-33, D5).
ClasificacionEtapa = Literal["deterministic", "gemini", "fallback", "precalculada"]


class ClasificacionResult(BaseModel):
    """
    Objeto de transferencia de datos (DTO) interno del clasificador híbrido.

    Producido por HybridClassifier.classify() y consumido por la capa de
    servicio para actualizar el incidente y crear el registro de auditoría.
    No debe exponerse directamente en respuestas HTTP; eso es responsabilidad
    de ClasificacionLogRead.

    Contrato multietiqueta (C-27):
        sector_predicho        — sector principal asignado por el clasificador.
        sectores_adicionales   — sectores secundarios predichos (sin incluir el principal).

    Invariantes del sistema:
        - Si etapa == "fallback": confianza == 0.0 y requiere_revision_humana == True.
        - Si confianza < 0.70:    requiere_revision_humana debe ser True.
        - Si confianza >= 0.90 y etapa == "deterministic": Gemini no fue invocado.
    """

    sector_predicho: str                                # Nombre del sector principal predicho
    sectores_adicionales: list[str] = Field(default_factory=list)  # Sectores secundarios predichos
    confianza: float = Field(..., ge=0.0, le=1.0)       # Nivel de certeza normalizado
    etapa: ClasificacionEtapa                           # Componente que produjo el resultado
    requiere_revision_humana: bool                      # Alerta de revisión manual
    respuesta_raw: str | None = None                    # Texto crudo de Gemini (para auditoría)


class ClasificacionLogRead(BaseModel):
    """
    Representación de un registro de auditoría para la API HTTP.

    Expone el historial de clasificaciones de un incidente, incluyendo
    el sector predicho y el sector validado manualmente (si existe).
    Es la forma en que los operadores humanos acceden a los registros
    pendientes de revisión a través de los endpoints correspondientes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    incidente_id: int
    confianza: float
    etapa: str                          # "deterministic" | "gemini" | "fallback"
    requiere_revision_humana: bool
    respuesta_raw: str | None           # None si la etapa fue deterministic
    created_at: datetime
    sector_predicho: SectorRead | None  # Predicción principal del clasificador
    sector_validado: SectorRead | None  # Corrección humana principal; None si aún no fue revisado
    sectores_predichos: list[SectorRead] = Field(default_factory=list)   # Secundarios predichos
    sectores_validados: list[SectorRead] = Field(default_factory=list)   # Secundarios validados


class ClasificacionValidar(BaseModel):
    """
    Payload enviado por el operador humano para validar o corregir una clasificación.

    Acepta el sector principal por nombre canonico (`sector_validado`) o, por
    compatibilidad, por identificador (`sector_id_validado`). `sectores_adicionales`
    permite registrar el conjunto validado completo cuando el incidente es
    multietiqueta.
    """

    sector_id_validado: int | None = None   # FK al sector principal (compatibilidad)
    sector_validado: str | None = None      # Nombre canonico del sector principal
    sectores_adicionales: list[str] = Field(default_factory=list)  # Nombres secundarios validados

    @field_validator("sector_validado")
    @classmethod
    def _validar_nombre_canonico(cls, v: str | None) -> str | None:
        if v is not None and v not in SECTORES_CANONICOS:
            # Mensaje generico SIN el valor sometido: el `loc` del error ya
            # identifica el campo, y un 422 nunca debe reflejar PII (W1/DIR-006).
            raise ValueError(
                "El sector no pertenece al vocabulario canonico."
            )
        return v

    @field_validator("sectores_adicionales")
    @classmethod
    def _validar_adicionales_canonicos(cls, v: list[str]) -> list[str]:
        if any(s not in SECTORES_CANONICOS for s in v):
            # Generico: no se listan los valores ofensores para no reflejar el
            # dato sometido en el cuerpo del 422 (W1/DIR-006).
            raise ValueError(
                "Uno o mas sectores adicionales no pertenecen al vocabulario canonico."
            )
        return v

    @model_validator(mode="after")
    def _requiere_sector_principal(self) -> "ClasificacionValidar":
        if self.sector_id_validado is None and not self.sector_validado:
            raise ValueError(
                "Debe indicar 'sector_validado' (nombre) o 'sector_id_validado' (id)."
            )
        return self
