"""
Clases base compartidas por todos los modelos ORM del sistema.

Responsabilidad:
    Provee la clase base declarativa de SQLAlchemy (Base) y el mixin
    TimestampMixin, que agrega columnas de auditoría de fecha y hora a
    cualquier entidad que lo incluya en su herencia.

    El uso de timezone=True en las columnas DateTime garantiza que todos
    los timestamps se almacenen en UTC en PostgreSQL (tipo TIMESTAMPTZ),
    evitando ambigüedades al operar en entornos con múltiples zonas horarias.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow() -> datetime:
    """
    Retorna el instante actual en UTC con información de zona horaria.

    Se utiliza como valor por defecto de las columnas created_at y updated_at.
    Al ser una función (no un valor fijo), SQLAlchemy la evalúa en el momento
    de cada inserción o actualización, garantizando timestamps precisos.
    """
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Mixin que agrega columnas de auditoría temporal a los modelos ORM.

    Cualquier clase que herede de este mixin obtendrá automáticamente:
        - created_at: fecha y hora de creación del registro (inmutable tras inserción).
        - updated_at: fecha y hora de la última modificación del registro.

    Ambas columnas están indexadas en created_at para optimizar las consultas
    de listado ordenadas por fecha, que son el patrón de acceso más frecuente
    en la interfaz de gestión de incidentes.

    El atributo onupdate en updated_at garantiza que SQLAlchemy actualice
    automáticamente este valor cada vez que se ejecuta un UPDATE sobre el registro.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
        index=True,   # Índice para consultas ordenadas por fecha de creación
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,  # Se recalcula automáticamente en cada UPDATE
        nullable=False,
    )


__all__ = ["Base", "TimestampMixin"]
