"""
Modelo ORM de los contadores de la guarda de costo en runtime (c-45).

Responsabilidad:
    Persiste los contadores de la guarda en la tabla `costo_guarda_contador`.
    Cada fila representa el estado de un contador dentro de una ventana
    (bucket tumbling), identificado por la terna (ambito, clave, ventana_inicio):

        ambito        → `global` (bolsa/rate global) | `surface` | `caller`
        clave         → `budget`, `rate`, nombre de superficie, o numero E.164 CRUDO
        ventana_inicio→ inicio de la ventana

    `llamadas` cuenta las llamadas pagas reservadas y `costo_usd` el gasto
    acumulado de la ventana. La restriccion unica de la terna habilita el
    UPSERT atomico de la reserva (evita la carrera chequear-y-actualizar).

Privacidad:
    La clave `caller` almacena el numero de origen CRUDO, acotado a la ventana
    del rate por origen (se purga al vencer). NO se incorpora a las tablas de
    negocio del incidente ni al corpus de evaluacion de la tesis.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

#: Nombre de la restriccion unica que habilita el UPSERT atomico.
UNIQUE_COST_GUARD_COUNTER = "uq_costo_guarda_contador_ambito_clave_ventana"


class CostoGuardaContador(Base, TimestampMixin):
    """Contador de la guarda de costo por (ambito, clave, ventana)."""

    __tablename__ = "costo_guarda_contador"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Ambito del contador: global | surface | caller.
    ambito: Mapped[str] = mapped_column(String(16), nullable=False)

    # Clave logica dentro del ambito: `budget`, `rate`, nombre de superficie o
    # numero E.164 CRUDO para el ambito `caller`.
    clave: Mapped[str] = mapped_column(String(64), nullable=False)

    # Inicio de la ventana (bucket tumbling); indexado para la purga de ventanas.
    ventana_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Cantidad de llamadas pagas reservadas en la ventana.
    llamadas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Gasto acumulado de la ventana en USD (estimado por costo unitario).
    costo_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 6), nullable=False, default=0, server_default="0"
    )

    __table_args__ = (
        UniqueConstraint(
            "ambito",
            "clave",
            "ventana_inicio",
            name=UNIQUE_COST_GUARD_COUNTER,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<CostoGuardaContador ambito={self.ambito!r} clave={self.clave!r} "
            f"ventana_inicio={self.ventana_inicio!r} llamadas={self.llamadas}>"
        )


__all__ = ["CostoGuardaContador", "UNIQUE_COST_GUARD_COUNTER"]
