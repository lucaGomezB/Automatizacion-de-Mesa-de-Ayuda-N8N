"""
Modelo ORM de la auditoria durable del directorio (c-153, Tema D, DIR-013).

Responsabilidad:
    Define la tabla `directorio_auditoria`, una traza DURABLE y append-only de
    las operaciones del directorio (gestion y resolucion de contactos), analoga
    a `incidente_evento` (c-86, D8). Complementa —no reemplaza— el evento
    estructurado de structlog.

Privacidad (DIR-013):
    La tabla almacena SOLO identificadores internos, la operacion, el resultado,
    el canal de resolucion (cuando aplica) y el instante. NUNCA almacena email,
    telefono, nombre ni otro dato personal en claro. Los identificadores son
    enteros internos OPACOS, sin clave foranea: una traza de auditoria no debe
    imponer un acoplamiento referencial que pueda hacer fallar la operacion que
    audita (los actores pueden no ser filas del directorio).

Append-only:
    No existe endpoint ni metodo de repositorio de edicion o borrado. El modelo
    NO hereda `TimestampMixin` para no exponer `updated_at`: una fila registrada
    no se modifica. La inmutabilidad es de aplicacion (no hay trigger de base).

Reversibilidad:
    La migracion 023 crea la tabla y su downgrade la elimina por completo.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utcnow


class DirectorioAuditoria(Base):
    """
    Evento durable de auditoria del directorio.

    Campos:
        id:                Clave primaria.
        operacion:         `alta`, `edicion`, `desactivacion`, `reactivacion`,
                           `borrado_arco`, la purga manual de vencidos o
                           `resolucion_contacto`.
        resultado:         Resultado de la operacion (`ok`, `encontrado`,
                           `no_encontrado`, `ambiguo`).
        canal:             Canal de resolucion de contacto (`email`, `telefono`,
                           `usuario`); NULL en operaciones de gestion.
        empleado_id:       Sujeto de la operacion (identificador interno); NULL
                           si no aplica. FK `ON DELETE SET NULL` para que el
                           borrado ARCO no elimine la traza.
        actor_empleado_id: Empleado que ejecuta la operacion (identificador
                           interno); NULL en resoluciones sin actor.
        created_at:        Instante UTC del evento (inmutable).
    """

    __tablename__ = "directorio_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operacion: Mapped[str] = mapped_column(String(40), nullable=False)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    canal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    actor_empleado_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        # Sin datos personales en la representacion (no-PII en logs).
        return (
            f"<DirectorioAuditoria id={self.id} operacion={self.operacion!r} "
            f"resultado={self.resultado!r}>"
        )
