"""
Modelo ORM de la entidad principal del sistema: Incidente.

Responsabilidad:
    Define la tabla 'incidente', que almacena la descripción pseudonimizada
    del problema reportado, su nivel de prioridad, el sector responsable
    asignado por el clasificador, el estado actual dentro del ciclo de vida
    y el canal por el que fue recibido.

    La descripción almacenada ya tiene los datos de identificación personal
    eliminados o sustituidos por el flujo de N8N antes de llegar a esta API,
    garantizando el cumplimiento de privacidad requerido en la tesis.

Índices compuestos:
    Se definen dos índices compuestos para optimizar las consultas más frecuentes:
        - (created_at, sector_id): consultas del panel de control por sector y fecha.
        - (estado_id, created_at): filtrado de cola de trabajo por estado activo.
"""

from enum import Enum as PyEnum

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.catalog import CanalOrigen, Estado, Sector


class PrioridadEnum(str, PyEnum):
    """
    Enumeración de niveles de prioridad de un incidente.

    Hereda de str para que SQLAlchemy almacene el valor textual en la base
    de datos, lo que mejora la legibilidad de consultas directas y simplifica
    la serialización en las respuestas JSON de la API.

    Niveles (de menor a mayor urgencia):
        baja    → Puede ser atendido en el próximo turno disponible.
        media   → Valor por defecto; afecta a un usuario individual.
        alta    → Afecta a múltiples usuarios o un proceso crítico.
        critica → Detención de operaciones; requiere atención inmediata.
    """
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class Incidente(Base, TimestampMixin):
    """
    Entidad central del sistema de gestión de incidentes.

    Almacena el contexto completo de un ticket de soporte: la descripción
    pseudonimizada del problema, su prioridad, el sector al que fue asignado
    por el clasificador, el estado actual en el flujo de trabajo y el canal
    de ingreso. El campo requiere_revision_humana actúa como señal de alerta
    para el operador cuando el clasificador no pudo determinar la categoría
    con suficiente confianza.

    Relaciones:
        - sector (FK → sector): sector responsable asignado; NULL mientras
          la clasificación está pendiente.
        - estado (FK → estado): estado actual del ticket; obligatorio;
          se inicializa con 'nuevo' al crear el incidente.
        - canal_origen (FK → canal_origen): medio de ingreso; puede ser NULL
          si el incidente se creó directamente por API sin especificar canal.
        - clasificaciones: historial completo de decisiones del clasificador.
    """

    __tablename__ = "incidente"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Texto libre pseudonimizado. El proceso de anonimización ocurre en N8N
    # antes de que el payload llegue a este módulo (ver flujo de trabajo N8N).
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    # Nivel de prioridad; por defecto 'media' si no se especifica en el payload
    prioridad: Mapped[PrioridadEnum] = mapped_column(
        String(20),
        default=PrioridadEnum.media,
        nullable=False,
    )

    # FK → sector: indexada para agilizar consultas de panel por sector responsable
    sector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sector: Mapped[Sector | None] = relationship("Sector", back_populates="incidentes")

    # FK → estado: indexada para filtrar la cola de trabajo por estado activo
    # RESTRICT evita eliminar un estado si hay incidentes en ese estado
    estado_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("estado.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    estado: Mapped[Estado] = relationship("Estado", back_populates="incidentes")

    # FK → canal_origen: NULL si se creó por API sin especificar canal
    canal_origen_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("canal_origen.id", ondelete="SET NULL"),
        nullable=True,
    )
    canal_origen: Mapped[CanalOrigen | None] = relationship(
        "CanalOrigen", back_populates="incidentes"
    )

    # Indicador de alerta: True cuando el clasificador no alcanzó el umbral de
    # confianza de 0.70 o cuando Gemini falló. El operador humano debe revisar
    # y corregir la categoría asignada.
    requiere_revision_humana: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Historial completo de clasificaciones; cascade delete para mantener
    # integridad referencial al eliminar un incidente
    clasificaciones: Mapped[list["ClasificacionLog"]] = relationship(  # type: ignore[name-defined]
        "ClasificacionLog",
        back_populates="incidente",
        lazy="select",
        cascade="all, delete-orphan",
    )

    # Índices compuestos optimizados para los patrones de consulta más frecuentes
    __table_args__ = (
        # Panel de control: incidentes por sector en rango de fechas
        Index("ix_incidente_created_sector", "created_at", "sector_id"),
        # Cola de trabajo: incidentes activos ordenados por antigüedad
        Index("ix_incidente_estado_created", "estado_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Incidente id={self.id} prioridad={self.prioridad} "
            f"estado_id={self.estado_id}>"
        )
