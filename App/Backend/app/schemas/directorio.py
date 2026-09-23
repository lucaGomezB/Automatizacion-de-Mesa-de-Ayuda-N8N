"""
Schemas Pydantic de la API de gestion del directorio (c-54).

Responsabilidad:
    Definir el contrato HTTP de entrada/salida del directorio. La validacion de
    dominio (unicidad, coherencia rol/sector, normalizacion) vive en el servicio;
    estos schemas solo validan tipos y presencia.

Minimizacion (DIR-002/DIR-006):
    `EmpleadoRead` expone SOLO los campos necesarios para la gestion. No expone
    `user_id` ni columnas internas, y NUNCA expone datos mas alla de los campos
    minimizados del directorio.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.models.empleado import RolEmpleado


class EmpleadoCreate(BaseModel):
    """Cuerpo de alta de un empleado del directorio."""

    legajo: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=254)
    telefono: str | None = Field(default=None, max_length=20)
    sector_id: int | None = None
    rol: RolEmpleado = RolEmpleado.usuario_final
    user_id: int | None = None


class EmpleadoUpdate(BaseModel):
    """Cuerpo de edicion parcial (solo se aplican los campos enviados)."""

    legajo: str | None = Field(default=None, min_length=1, max_length=50)
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    telefono: str | None = Field(default=None, max_length=20)
    sector_id: int | None = None
    rol: RolEmpleado | None = None
    activo: bool | None = None
    user_id: int | None = None


class EmpleadoRead(BaseModel):
    """Representacion minimizada de un empleado para la API de gestion."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    legajo: str
    nombre: str
    email: str
    telefono: str | None
    sector_id: int | None
    rol: RolEmpleado
    activo: bool
