"""
Modelo ORM para el registro de auditoría de clasificaciones.

Responsabilidad:
    Define la tabla 'clasificacion_log', que almacena cada decisión emitida
    por el clasificador híbrido para un incidente dado. Este registro de
    auditoría es un componente clave de la tesis: permite comparar las
    predicciones automáticas contra las validaciones humanas, calcular
    métricas de exactitud (accuracy, F1 por categoría) y analizar la
    distribución de confianza del sistema.

    El campo 'etapa' identifica qué componente del pipeline híbrido produjo
    la clasificación: el filtro determinístico de reglas, el modelo Gemini
    2.5 Flash, o el mecanismo de fallback ante falla del clasificador.

    El campo 'sector_id_validado' permanece NULL hasta que un operador humano
    confirma o corrige la categoría predicha, cerrando el ciclo de aprendizaje
    documentado en el Anexo H §H.5.

Relación con el corpus de evaluación:
    Los registros de esta tabla, una vez validados humanamente, conforman
    el corpus de evaluación de 200 casos pseudonimizados utilizado en la
    evaluación experimental de la tesis.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.catalog import Sector


class ClasificacionLog(Base, TimestampMixin):
    """
    Registro de auditoría de una decisión del clasificador híbrido.

    Cada vez que el sistema clasifica un incidente, se crea un registro en
    esta tabla independientemente del resultado. Esto garantiza trazabilidad
    completa, incluyendo los casos de fallo (confianza=0.0) que requieren
    intervención humana.

    Campos clave:
        confianza:              Valor en [0.0, 1.0]. Si es 0.0, indica fallo del
                                clasificador; el incidente queda en revisión humana.
        etapa:                  "deterministic" | "gemini" | "fallback"
        requiere_revision_humana: True cuando confianza < 0.70 o ante fallo de Gemini.
        respuesta_raw:          Texto crudo devuelto por Gemini (None en etapa deterministic).
        sector_id_validado:     FK llenada a posteriori por el operador humano;
                                NULL mientras el registro aguarda revisión.
    """

    __tablename__ = "clasificacion_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # FK al incidente clasificado; CASCADE garantiza eliminación de logs huérfanos
    incidente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("incidente.id", ondelete="CASCADE"),
        nullable=False,
        index=True,   # Índice para recuperar el historial de un incidente específico
    )
    incidente: Mapped["Incidente"] = relationship(  # type: ignore[name-defined]
        "Incidente", back_populates="clasificaciones"
    )

    # Sector predicho por el clasificador; puede ser NULL si el clasificador
    # falló completamente (etapa="fallback" con confianza=0.0)
    sector_id_predicho: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="SET NULL"),
        nullable=True,
    )
    # foreign_keys es obligatorio: ClasificacionLog tiene DOS FK apuntando a sector.id
    # (sector_id_predicho y sector_id_validado). Sin este argumento, SQLAlchemy
    # no puede determinar el join y lanza AmbiguousForeignKeysError en la primera
    # query que involucre ClasificacionLog, causando HTTP 500 en todos los endpoints
    # de clasificaciones.
    sector_predicho: Mapped[Sector | None] = relationship(
        "Sector",
        foreign_keys=[sector_id_predicho],
        back_populates="clasificaciones",
    )

    # Valor de confianza normalizado en [0.0, 1.0].
    # Numeric(5,4) permite representar valores como 0.9500 con 4 decimales de precisión.
    confianza: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)

    # Etapa del pipeline que produjo este resultado:
    #   "deterministic" → el filtro de reglas alcanzó confianza >= 0.90
    #   "gemini"        → Gemini clasificó con confianza >= 0.70
    #   "fallback"      → Gemini falló o devolvió respuesta inválida
    etapa: Mapped[str] = mapped_column(String(30), nullable=False)

    # Indicador de alerta para el operador humano
    requiere_revision_humana: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Respuesta textual cruda devuelta por Gemini; útil para auditoría y diagnóstico.
    # Es None cuando la clasificación fue resuelta en la etapa determinística.
    respuesta_raw: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Categoría validada manualmente por el operador humano.
    # Su presencia indica que el ciclo de revisión fue completado para este registro.
    sector_id_validado: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="SET NULL"),
        nullable=True,
    )
    sector_validado: Mapped[Sector | None] = relationship(
        "Sector",
        foreign_keys=[sector_id_validado],  # Distinción explícita de la FK ante múltiples relaciones a Sector
    )

    def __repr__(self) -> str:
        return (
            f"<ClasificacionLog id={self.id} incidente_id={self.incidente_id} "
            f"etapa={self.etapa!r} confianza={self.confianza}>"
        )
