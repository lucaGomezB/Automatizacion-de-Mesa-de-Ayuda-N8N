"""
Modelo ORM de la entidad principal del sistema: Incidente.

Responsabilidad:
    Define la tabla 'incidente' con DOBLE REPRESENTACIÓN de la descripción
    (arquitectura C-03, Ley 25.326):

        descripcion_original       — texto crudo con PII, CIFRADO at-rest
                                     mediante EncryptedText (Fernet). Solo para
                                     auditoría / ejercicio de derechos ARCO.
                                     NO se expone en los endpoints de la API.

        descripcion_pseudonimizada — texto operativo en claro con etiquetas
                                     [EMAIL]/[TELEFONO]/[HOST]/[PERSONA].
                                     Única representación que consume el pipeline
                                     de clasificación (Gemini + determinístico)
                                     y que expone la API al frontend.

    La pseudonimización ocurre UNA SOLA VEZ, en IncidenteService.create_and_classify(),
    antes de persistir. N8N ya no garantiza ningún tratamiento previo.

Índices compuestos:
    Se definen dos índices compuestos para optimizar las consultas más frecuentes:
        - (created_at, sector_id): consultas del panel de control por sector y fecha.
        - (estado_id, created_at): filtrado de cola de trabajo por estado activo.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.asociaciones import incidente_sector_adicional
from app.models.base import Base, TimestampMixin, utcnow
from app.models.catalog import CanalOrigen, Estado, Sector
from app.utils.encryption import EncryptedText


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

    # Texto crudo del incidente con PII — CIFRADO at-rest con Fernet (EncryptedText).
    # Solo para auditoría / ejercicio de derechos ARCO (Ley 25.326).
    # No se expone en los endpoints de la API.
    descripcion_original: Mapped[str] = mapped_column(EncryptedText, nullable=False)

    # Texto operativo con etiquetas [EMAIL]/[TELEFONO]/[HOST]/[PERSONA].
    # Única representación que consume el pipeline de clasificación y la API.
    descripcion_pseudonimizada: Mapped[str] = mapped_column(Text, nullable=False)

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

    # Vinculo de REPORTANTE (c-82, VIS-003): FK nullable al directorio de
    # empleados. Es la base del alcance PROPIO del rol `usuario_final` (solo ve
    # los incidentes que reporto). Nullable: un reportante no identificado
    # persiste NULL sin bloquear el alta. ON DELETE SET NULL: borrar un empleado
    # (ARCO) no elimina el incidente. Indexada para el filtrado por reportante.
    # NO altera la clasificacion ni el alcance de los roles GLOBAL.
    reportante_empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directorio_empleado.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Identificador del mensaje de origen (Message-ID de Outlook) usado para la
    # idempotencia de alta (C-33, HIGH-4). Nullable: los emisores que no lo
    # proveen (formulario web, clientes API) crean el incidente normalmente.
    # UNIQUE: un mismo mensaje no puede producir mas de un incidente. El indice
    # unico se llama `ix_incidente_origen_message_id` (migracion 005).
    origen_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    # Marcador de evento declarado por el emisor en el alta (C-33, D6/W2).
    # Nullable: un alta directa puede no declararlo. Sin unicidad ni indice: no
    # se consulta por el, solo registra el origen declarado para auditoria.
    # Valores validos de creacion se validan en el schema (`origen_evento`).
    origen_evento: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Instante de INGRESO al sistema (C-39). Capturado en el borde del trigger de
    # cada canal y enviado por N8N en el payload de alta; se persiste normalizado
    # a UTC. Nullable: los clientes API directos y las filas legacy pueden no
    # proveerlo, y su ausencia no bloquea el alta.
    ingresado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Instante de PERSISTENCIA CONFIRMADA (C-39). Sellado UNA sola vez dentro de
    # la transaccion de alta y clasificacion, inmediatamente antes del commit.
    # Inmutable: sin `onupdate` y fuera del contrato de update, de modo que una
    # revision humana o un PATCH posterior no lo sobrescriben (a diferencia de
    # `updated_at`, que se recalcula en cada UPDATE). La latencia end-to-end se
    # deriva en la capa de lectura como `persistido_en - ingresado_en`.
    persistido_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Marcador de BORRADO LOGICO (c-87, SD-001). NULL = incidente activo; un
    # instante no nulo lo retira de TODAS las superficies de lectura. La fila y
    # sus relaciones NUNCA se eliminan fisicamente por esta via (reversible por
    # diseño). La exclusion se concentra en el repositorio (punto unico, D2).
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Atribucion del actor del borrado logico (c-87, SD-001): FK nullable al
    # directorio de empleados, patron de `reportante_empleado_id`. ON DELETE SET
    # NULL: el borrado ARCO del actor anula la referencia sin eliminar el
    # incidente. Indexada para el filtrado por actor.
    deleted_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directorio_empleado.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Sectores adicionales (N-a-N): el sector principal vive en sector_id; esta
    # coleccion guarda el resto del conjunto multietiqueta del incidente.
    sectores_adicionales: Mapped[list[Sector]] = relationship(
        "Sector",
        secondary=incidente_sector_adicional,
        lazy="selectin",
    )

    # Cierres por sector (c-86, D4). Se cargan eagerly (selectin) para que la
    # decision de visibilidad SECTOR (`sectores_cerrados`) nunca dispare un
    # lazy-load en contexto async. El borrado del incidente cascadea por FK.
    cierres_sector: Mapped[list["IncidenteCierreSector"]] = relationship(
        "IncidenteCierreSector",
        lazy="selectin",
    )

    @property
    def sector_ids(self) -> frozenset[int]:
        """Conjunto de sectores del incidente: principal + adicionales (c-86, D3)."""
        ids = {s.id for s in self.sectores_adicionales}
        if self.sector_id is not None:
            ids.add(self.sector_id)
        return frozenset(ids)

    @property
    def sectores_cerrados(self) -> frozenset[int]:
        """Sectores con un cierre registrado para este incidente (c-86, D4)."""
        return frozenset(c.sector_id for c in self.cierres_sector)

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


class IncidenteCierreSector(Base):
    """
    Cierre de un incidente para UN sector (c-86, D4).

    Modela el cierre por sector que sostiene la vista activa (VIS-007) y el
    historial inmediato por sector (VIS-008). La PK compuesta
    `(incidente_id, sector_id)` da idempotencia natural: un segundo cierre del
    mismo sector no duplica la fila.

    FKs:
        incidente_id: CASCADE (borrar el incidente limpia sus cierres).
        sector_id:    RESTRICT (no se elimina un sector con cierres).
        cerrado_por:  SET NULL (el borrado ARCO del empleado preserva la fila,
                      sin PII: solo se anula el actor).
    """

    __tablename__ = "incidente_cierre_sector"

    incidente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("incidente.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sector_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    )
    cerrado_por: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directorio_empleado.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cerrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<IncidenteCierreSector incidente_id={self.incidente_id} "
            f"sector_id={self.sector_id}>"
        )


class IncidenteEvento(Base):
    """
    Evento de auditoria del ciclo de vida de un incidente (c-86, D8).

    Es el registro durable del actor y el instante de cada operacion de ciclo
    (cierre por sector, cierre global, reapertura y cambio de estado). Como los
    cierres se borran en la reapertura, esta tabla es la unica traza persistente
    del actor (ILC-006). Sin PII: solo identificadores internos.

    Tipos validos: `cierre_sector`, `cierre_global`, `reapertura`, `cambio_estado`.
    """

    __tablename__ = "incidente_evento"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    incidente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("incidente.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directorio_empleado.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sector.id", ondelete="SET NULL"),
        nullable=True,
    )
    estado_anterior: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estado_nuevo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<IncidenteEvento id={self.id} incidente_id={self.incidente_id} "
            f"tipo={self.tipo!r}>"
        )


class IncidenteComentario(Base):
    """
    Comentario APPEND-ONLY sobre un incidente (c-86, D7).

    Conserva por entrada el incidente, el empleado autor (SET NULL si el
    empleado se borra, sin PII), el texto y el instante de creacion. No existe
    endpoint de edicion ni de borrado (ICM-001).
    """

    __tablename__ = "incidente_comentario"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    incidente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("incidente.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    autor_empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("directorio_empleado.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<IncidenteComentario id={self.id} "
            f"incidente_id={self.incidente_id}>"
        )
