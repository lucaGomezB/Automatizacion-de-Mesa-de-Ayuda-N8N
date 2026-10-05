"""
Repositorio de la tabla de vida corta `telefonia_pending_call` (c-70, D2).

Responsabilidad:
    Encapsular el mapeo efimero `call_sid -> corpus_case_id` tras una interfaz
    mockeable (`upsert`/`get_by_call_sid`/`delete_by_call_sid`/`purge_expired`),
    de modo que el backend pueda propagar el `corpus_case_id` del webhook de voz
    al callback de grabacion SIN depender de cambios de firma de Twilio ni de un
    query param en la URL del callback.

TTL:
    Ademas del borrado explicito en el callback, `purge_expired` elimina las
    filas mas viejas que la ventana de la llamada para que nunca se acumulen
    filas huerfanas.
"""

from datetime import datetime, timedelta

from sqlalchemy import delete, select

from app.models.telefonia_pending_call import TelefoniaPendingCall
from app.repositories.base import BaseRepository

# Ventana de vida del mapeo efimero (30 minutos). Cubre con holgura el tiempo
# entre el webhook de voz y el callback de estado de grabacion de una llamada.
PENDING_CALL_TTL_SECONDS = 1800


class TelefoniaPendingCallRepository(BaseRepository[TelefoniaPendingCall]):
    """Acceso a datos del mapeo efimero `call_sid -> corpus_case_id`."""

    model = TelefoniaPendingCall

    async def upsert(
        self, call_sid: str, corpus_case_id: str
    ) -> TelefoniaPendingCall:
        """
        Inserta o actualiza el mapeo por `call_sid` (clave del upsert).

        El `created_at` original se preserva ante una actualizacion: el TTL mide
        la antiguedad desde el primer registro de la llamada, no desde el ultimo
        update.

        Args:
            call_sid:        clave natural del mapeo (CallSid de Twilio).
            corpus_case_id:  caso del corpus correlacionado.

        Returns:
            La fila persistida.
        """
        existente = await self._session.get(TelefoniaPendingCall, call_sid)
        if existente is None:
            fila = TelefoniaPendingCall(
                call_sid=call_sid, corpus_case_id=corpus_case_id
            )
            self._session.add(fila)
        else:
            existente.corpus_case_id = corpus_case_id
            fila = existente
        await self._session.flush()
        await self._session.refresh(fila)
        return fila

    async def get_by_call_sid(self, call_sid: str) -> TelefoniaPendingCall | None:
        """Devuelve el mapeo del `call_sid` o None si no existe."""
        return await self._session.get(TelefoniaPendingCall, call_sid)

    async def delete_by_call_sid(self, call_sid: str) -> bool:
        """
        Borra el mapeo del `call_sid`.

        Returns:
            True si habia fila y se borro; False si no existia (no-op).
        """
        fila = await self._session.get(TelefoniaPendingCall, call_sid)
        if fila is None:
            return False
        await self._session.delete(fila)
        await self._session.flush()
        return True

    async def purge_expired(
        self, now: datetime, ttl_seconds: int = PENDING_CALL_TTL_SECONDS
    ) -> int:
        """
        Purga las filas mas viejas que la ventana de la llamada.

        Args:
            now:         instante actual (reloj inyectable en tests).
            ttl_seconds: ventana de vida del mapeo.

        Returns:
            Cantidad de filas purgadas.
        """
        cutoff = now - timedelta(seconds=ttl_seconds)
        result = await self._session.execute(
            delete(TelefoniaPendingCall).where(
                TelefoniaPendingCall.created_at < cutoff
            )
        )
        return result.rowcount or 0


__all__ = ["TelefoniaPendingCallRepository", "PENDING_CALL_TTL_SECONDS"]
