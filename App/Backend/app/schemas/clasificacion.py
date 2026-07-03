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

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import SectorRead

# Tipo literal que restringe los valores válidos de la etapa del clasificador.
# "deterministic": el filtro de reglas resolvió con confianza >= 0.90.
# "gemini":        Gemini 2.5 Flash clasificó con confianza en rango válido.
# "fallback":      El sistema no pudo clasificar; intervención humana requerida.
ClasificacionEtapa = Literal["deterministic", "gemini", "fallback"]


class ClasificacionResult(BaseModel):
    """
    Objeto de transferencia de datos (DTO) interno del clasificador híbrido.

    Producido por HybridClassifier.classify() y consumido por la capa de
    servicio para actualizar el incidente y crear el registro de auditoría.
    No debe exponerse directamente en respuestas HTTP; eso es responsabilidad
    de ClasificacionLogRead.

    Invariantes del sistema:
        - Si etapa == "fallback": confianza == 0.0 y requiere_revision_humana == True.
        - Si confianza < 0.70:    requiere_revision_humana debe ser True.
        - Si confianza >= 0.90 y etapa == "deterministic": Gemini no fue invocado.
    """

    categoria: str                                      # Nombre del sector predicho
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
    sector_predicho: SectorRead | None  # Predicción del clasificador
    sector_validado: SectorRead | None  # Corrección humana; None si aún no fue revisado


class ClasificacionValidar(BaseModel):
    """
    Payload enviado por el operador humano para validar o corregir una clasificación.

    El campo sector_id_validado referencia al sector correcto según el criterio
    del operador. Este dato se almacena en clasificacion_log.sector_id_validado
    y constituye la etiqueta de verdad para las métricas de evaluación del sistema.
    """

    sector_id_validado: int  # FK al sector considerado correcto por el operador
