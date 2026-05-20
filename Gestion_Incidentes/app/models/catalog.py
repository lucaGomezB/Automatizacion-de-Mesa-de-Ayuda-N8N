"""
Modelos ORM para las tablas de catálogo del sistema.

Responsabilidad:
    Define las entidades Sector, Estado y CanalOrigen, que representan
    datos de referencia con valores fijos poblados durante la migración
    inicial (001_seed_catalogs.py). Estas tablas no se modifican en
    tiempo de ejecución y actúan como vocabulario controlado del sistema.

    La restricción UniqueConstraint en el campo 'nombre' de cada tabla
    garantiza la integridad referencial semántica: no puede existir
    duplicación de categorías, estados o canales de ingreso.

Tablas de catálogo definidas en la tesis:
    - sector:       Sistemas | Operaciones | Soporte Técnico
    - estado:       nuevo | en proceso | en espera | resuelto | cerrado
    - canal_origen: correo electrónico | formulario web | llamada telefónica
"""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Sector(Base, TimestampMixin):
    """
    Catálogo de sectores responsables de atender los incidentes.

    Representa los tres sectores funcionales definidos en el modelo
    de clasificación de la tesis. El clasificador híbrido produce
    como resultado el nombre de uno de estos sectores, que luego
    es resuelto a un registro de esta tabla por la capa de servicio.

    Sectores válidos (sembrados en la migración 001):
        - Sistemas: infraestructura, redes, servidores, bases de datos, ciberseguridad.
        - Operaciones: procesos compartidos, gestión de servicios, planificación.
        - Soporte Técnico: equipamiento de usuarios, periféricos, software cliente.
    """

    __tablename__ = "sector"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(500))

    # Restricción de unicidad sobre el nombre para prevenir duplicados semánticos
    __table_args__ = (UniqueConstraint("nombre", name="uq_sector_nombre"),)

    # Relación inversa: todos los incidentes asignados a este sector
    incidentes: Mapped[list["Incidente"]] = relationship(  # type: ignore[name-defined]
        "Incidente", back_populates="sector", lazy="select"
    )
    # Relación inversa: todos los logs donde este sector fue la predicción del clasificador
    clasificaciones: Mapped[list["ClasificacionLog"]] = relationship(  # type: ignore[name-defined]
        "ClasificacionLog", back_populates="sector_predicho", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Sector id={self.id} nombre={self.nombre!r}>"


class Estado(Base, TimestampMixin):
    """
    Catálogo de estados del ciclo de vida de un incidente.

    Los estados modelan el flujo de trabajo de la mesa de ayuda desde
    la recepción del incidente hasta su cierre. El campo es_terminal
    distingue los estados finales (cerrado) de los intermedios, lo que
    permite filtrar incidentes activos en las consultas de la interfaz.

    Estados válidos (sembrados en la migración 001):
        - nuevo:      Incidente recibido, sin asignar.
        - en proceso: Asignado y en atención por el sector responsable.
        - en espera:  Bloqueado esperando respuesta o información del usuario.
        - resuelto:   Solución aplicada, pendiente de confirmación del usuario.
        - cerrado:    Finalizado (estado terminal; es_terminal=True).
    """

    __tablename__ = "estado"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(300))
    # Marca si este estado representa el final del ciclo de vida del ticket
    es_terminal: Mapped[bool] = mapped_column(default=False, nullable=False)

    __table_args__ = (UniqueConstraint("nombre", name="uq_estado_nombre"),)

    # Relación inversa: todos los incidentes en este estado
    incidentes: Mapped[list["Incidente"]] = relationship(  # type: ignore[name-defined]
        "Incidente", back_populates="estado", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Estado id={self.id} nombre={self.nombre!r}>"


class CanalOrigen(Base, TimestampMixin):
    """
    Catálogo de canales de ingreso de incidentes al sistema.

    Registra el medio por el cual el usuario reportó el incidente.
    Esta información es relevante para el análisis estadístico de la
    distribución de incidentes por canal, uno de los indicadores de
    evaluación del sistema propuesto en la tesis.

    Canales válidos (sembrados en la migración 001):
        - correo electrónico: Recibido vía trigger de Microsoft Outlook (N8N).
        - formulario web:     Ingresado directamente por API REST.
        - llamada telefónica: Recibido vía webhook de Twilio (N8N).
    """

    __tablename__ = "canal_origen"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(300))

    __table_args__ = (UniqueConstraint("nombre", name="uq_canal_origen_nombre"),)

    # Relación inversa: todos los incidentes recibidos por este canal
    incidentes: Mapped[list["Incidente"]] = relationship(  # type: ignore[name-defined]
        "Incidente", back_populates="canal_origen", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<CanalOrigen id={self.id} nombre={self.nombre!r}>"
