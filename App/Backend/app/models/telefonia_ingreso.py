"""
Modelo ORM del ingreso de telefonia asincronico (c-52).

Responsabilidad:
    Persiste un registro por llamada del canal de telefonia, con DOBLE
    REPRESENTACION del transcript:

        transcript_original        — texto crudo con PII, CIFRADO at-rest con
                                     Fernet (`EncryptedText`). Solo para
                                     auditoria / ejercicio de derechos ARCO.
        descripcion_pseudonimizada — texto operativo en claro con etiquetas.
                                     Unica representacion que cruza el borde
                                     hacia n8n.

    Se elige una tabla dedicada (y no reutilizar `incidente`) porque el ingreso
    puede existir SIN incidente (fallo de descarga/STT, denegacion de la guarda,
    reintento pendiente) y porque el transcript crudo no debe vivir en la tabla
    operativa expuesta por la API (design.md D3).

Idempotencia:
    `call_sid` es UNIQUE: un callback repetido de Twilio no puede producir una
    segunda fila. El alta del incidente reutiliza el indice unico de
    `incidente.origen_message_id` con el `CallSid` (design.md D8).

Referencias:
    design.md D3, D8, D11
    specs/telefonia-stt-intake/spec.md
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.incidente import Incidente
from app.utils.encryption import EncryptedText


class TranscripcionEstado(str, PyEnum):
    """
    Estado del procesamiento de transcripcion de un ingreso.

    Hereda de str para almacenar el valor textual y simplificar la lectura.
    El estado explicito garantiza que un fallo (descarga, STT o denegacion de
    la guarda) quede observable y disponible para reintento o revision humana
    (design.md D11).

    Valores:
        pendiente        → ingreso recibido, todavia sin resolver.
        transcrito       → STT completado y descripcion pseudonimizada poblada.
        guarda_denegada  → la guarda de costo nego la reserva del STT.
        error_descarga   → la descarga autenticada de la grabacion fallo.
        error_stt        → el motor de speech-to-text fallo.
    """

    pendiente = "pendiente"
    transcrito = "transcrito"
    guarda_denegada = "guarda_denegada"
    error_descarga = "error_descarga"
    error_stt = "error_stt"


class TelefoniaIngreso(Base, TimestampMixin):
    """Registro de ingreso del canal de telefonia."""

    __tablename__ = "telefonia_ingreso"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Clave de idempotencia del ingreso: el CallSid de Twilio. UNIQUE impide una
    # segunda fila ante un callback repetido (design.md D8).
    call_sid: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    # Identificador de la grabacion de Twilio (`RecordingSid`). Nullable: puede
    # no informarse en algunos callbacks.
    recording_sid: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Numero llamante (`From`) CIFRADO at-rest. Nullable: el callback de estado
    # de grabacion NO provee `From` (design.md Contexto tecnico Twilio).
    caller_cifrado: Mapped[str | None] = mapped_column(EncryptedText, nullable=True)

    # Duracion informada por Twilio (`RecordingDuration`), en segundos. Base de
    # la estimacion de la reserva de `backend_stt` (cap 45 s).
    duracion_segundos: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Transcript crudo CIFRADO at-rest. Solo para auditoria.
    transcript_original: Mapped[str | None] = mapped_column(EncryptedText, nullable=True)

    # Unica representacion que cruza el borde hacia n8n.
    descripcion_pseudonimizada: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Instante de ingreso sellado por el backend al recibir el callback, ANTES
    # de descargar y transcribir (design.md D4).
    ingresado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Instante en que el ingreso quedo persistido.
    persistido_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Estado explicito del procesamiento (design.md D11).
    transcripcion_estado: Mapped[str] = mapped_column(
        String(32),
        default=TranscripcionEstado.pendiente,
        nullable=False,
    )

    # FK nullable al incidente creado a partir del ingreso. SET NULL: borrar el
    # incidente no borra el ingreso (auditoria).
    incidente_id: Mapped[int | None] = mapped_column(
        ForeignKey("incidente.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # eager loading: evita lazy-load en contexto async al serializar/inspeccionar.
    incidente: Mapped[Incidente | None] = relationship(
        Incidente,
        lazy="selectin",
    )

    # Detalle del error cuando la transcripcion no prospera. Nullable.
    error_detalle: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Trazabilidad del motor usado.
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TelefoniaIngreso id={self.id} call_sid={self.call_sid!r} "
            f"estado={self.transcripcion_estado!r}>"
        )


__all__ = ["TelefoniaIngreso", "TranscripcionEstado"]
