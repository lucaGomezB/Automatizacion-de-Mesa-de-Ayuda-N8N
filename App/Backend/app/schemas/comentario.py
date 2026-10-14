"""
Schemas Pydantic de los comentarios de incidente (c-86, D7).

`ComentarioCreate` es el payload de alta; `ComentarioRead` la representacion de
salida. El backend devuelve `created_at` en UTC; el formato de presentacion
(`HH:MM:SS DD/MM/AAAA : texto`) se resuelve con `app.utils.business_time`.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComentarioCreate(BaseModel):
    """Payload de alta de un comentario (append-only, sin edicion ni borrado)."""

    texto: str = Field(min_length=1, max_length=5000)

    @field_validator("texto")
    @classmethod
    def texto_no_vacio(cls, v: str) -> str:
        """Rechaza un texto vacio o solo espacios."""
        if not v.strip():
            raise ValueError("El comentario no puede estar vacio.")
        return v.strip()


class ComentarioRead(BaseModel):
    """Representacion de salida de un comentario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    incidente_id: int
    autor_empleado_id: int | None = None
    texto: str
    created_at: datetime
