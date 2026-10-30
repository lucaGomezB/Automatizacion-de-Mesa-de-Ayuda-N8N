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
    3.6 Flash, o el mecanismo de fallback ante falla del clasificador.

    El campo 'sector_id_validado' permanece NULL hasta que un operador humano
    confirma o corrige la categoría predicha, cerrando el ciclo de aprendizaje
    documentado en el Anexo H §H.5.

Relación con el corpus de evaluación:
    Los registros de esta tabla, una vez validados humanamente, conforman
    el corpus de evaluación de 200 casos pseudonimizados utilizado en la
    evaluación experimental de la tesis.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.elements import ColumnElement

from app.models.asociaciones import (
    clasificacion_sector_predicho,
    clasificacion_sector_validado,
)
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
        validado_por_empleado_id, intervencion_inicio_en, validado_en,
        origen_intervencion:    Metadatos de la intervención humana (c-165, migración 024):
                                actor, inicio declarado, instante del servidor y origen
                                (gate | muestreo | rederivacion | completado_manual).
                                Los cuatro son NULL mientras el log no fue intervenido.
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

    # ── Metadatos de la intervención humana (c-165, ASG-005; migración 024) ──────
    #
    # Las cuatro columnas son NULLABLE y sin default: NULL en todas significa que
    # el log nunca fue intervenido. Cada intervención las sobrescribe como unidad
    # junto con sector_id_validado y sectores_validados (gana la última
    # escritura). Estados derivados, sin columna propia (funcion pura en
    # app.services.intervencion_estado; condiciones SQL al final de este modulo):
    #     no_intervenido                    → validado_en IS NULL y sector_id_validado IS NULL
    #     intervenido                       → validado_en IS NOT NULL
    #     intervencion_legada_sin_metadatos → sector_id_validado IS NOT NULL y validado_en IS NULL
    #                                         (validado antes de la 024; sin backfill)

    # Actor de la última intervención. NULL si la cuenta no tiene empleado
    # vinculado o si el empleado fue purgado por retención (DIR-007): SET NULL
    # evita que la purga toque el log. Solo se expone el id (sin PII).
    validado_por_empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "directorio_empleado.id",
            ondelete="SET NULL",
            name="fk_clasificacion_log_validado_por_directorio_empleado",
        ),
        nullable=True,
        index=True,  # ix_clasificacion_log_validado_por_empleado_id
    )

    # Inicio declarado por el cliente al abrir el diálogo de validación. NULL si no
    # se envió y en la rederivación. Depende del reloj del cliente: se guarda en UTC
    # tal cual y el export anula la duración si resulta negativa.
    intervencion_inicio_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Instante en que el SERVIDOR registró la intervención (distinto de created_at).
    validado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Origen de la intervención, derivado SIEMPRE por el backend (gate, muestreo,
    # rederivacion; completado_manual reservado, sin escritor). Sin CHECK: el
    # vocabulario vive en app.constants.ORIGENES_INTERVENCION.
    origen_intervencion: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Sectores adicionales del conjunto predicho (N-a-N): el principal vive en
    # sector_id_predicho; esta coleccion guarda el resto.
    sectores_predichos: Mapped[list[Sector]] = relationship(
        "Sector",
        secondary=clasificacion_sector_predicho,
        lazy="selectin",
    )

    # Sectores adicionales del conjunto validado (N-a-N).
    sectores_validados: Mapped[list[Sector]] = relationship(
        "Sector",
        secondary=clasificacion_sector_validado,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ClasificacionLog id={self.id} incidente_id={self.incidente_id} "
            f"etapa={self.etapa!r} confianza={self.confianza}>"
        )


# ── Condiciones SQL del estado de la intervención (c-165, ASG-005 y ECM-003) ─────
#
# Expresiones puras sobre las columnas del modelo, SIN E/S. Las comparten la métrica
# backend (capa de repositorios) y el export (a través de
# `app.services.intervencion_estado`, que las re-exporta junto con la función pura de
# estado). Viven en el modelo, la capa más baja, para que un repositorio no tenga que
# importar de la capa de servicios (dependencia hacia arriba y riesgo de ciclo).


def condicion_intervenido() -> ColumnElement[bool]:
    """Condición SQL de un log `intervenido` (`validado_en IS NOT NULL`)."""
    return ClasificacionLog.validado_en.is_not(None)


def condicion_legado() -> ColumnElement[bool]:
    """Condición SQL de un log `intervencion_legada_sin_metadatos`.

    Sector validado SIN `validado_en`: fila validada antes de la migración 024.
    """
    return and_(
        ClasificacionLog.validado_en.is_(None),
        ClasificacionLog.sector_id_validado.is_not(None),
    )


def condicion_no_intervenido() -> ColumnElement[bool]:
    """Condición SQL de un log `no_intervenido` (nunca validado por nadie)."""
    return and_(
        ClasificacionLog.validado_en.is_(None),
        ClasificacionLog.sector_id_validado.is_(None),
    )


def condicion_cambio_de_sector() -> ColumnElement[bool]:
    """Condición SQL de `cambio_sector`: validado distinto del predicho (NULL-safe).

    Equivale a `IS DISTINCT FROM`: un predicho NULL (clasificador sin señal) cuenta
    como cambio frente a cualquier sector validado.
    """
    return ClasificacionLog.sector_id_validado.is_distinct_from(
        ClasificacionLog.sector_id_predicho
    )
