"""
Modelo ORM de la tabla de vida corta `telefonia_pending_call` (c-70, D2).

Responsabilidad:
    Materializar la propagacion del `corpus_case_id` desde el webhook de voz
    pre-llamada de Twilio (`/cost-guard/twilio/voice`) hasta el callback de
    estado de grabacion (`/telefonia/recording-status`) como un store
    keyed-by-CallSid:

        webhook de voz:  upsert(call_sid -> corpus_case_id)
        callback:        get(call_sid) -> corpus_case_id  ->  delete(call_sid)

    La correlacion se persiste al sellar `ingresado_en` en `telefonia_ingreso`;
    esta tabla es EFIMERA. Su ciclo de vida se acota con un TTL (purga de filas
    mas viejas que la ventana de la llamada) ademas del borrado explicito en el
    callback, de modo que nunca se acumulan filas huerfanas.

Decision (OQ1 = Opcion B):
    Se descarta el query param urlencoded en el callback (exigiria que la firma
    Twilio siga validando sobre la URL con query) y NO se agregan dependencias
    nuevas: se reutiliza la infraestructura PostgreSQL ya presente.

Privacidad:
    La tabla NO almacena PII: solo el `CallSid`, el `corpus_case_id` y el
    instante de creacion (UTC).
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utcnow


class TelefoniaPendingCall(Base):
    """Mapeo efimero `call_sid -> corpus_case_id` (tabla de vida corta)."""

    __tablename__ = "telefonia_pending_call"

    # Clave natural del mapeo: el CallSid de Twilio. El upsert es por esta clave.
    call_sid: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Caso del corpus correlacionado con la llamada.
    corpus_case_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Instante de creacion (UTC), base de la purga TTL. Indexado para que la
    # purga por rango sea eficiente.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        # Sin datos sensibles mas alla del CallSid (no-PII en logs).
        return f"<TelefoniaPendingCall call_sid={self.call_sid!r}>"


__all__ = ["TelefoniaPendingCall"]
