"""
Servicio del store efimero de correlacion de telefonia (c-70, D2).

Responsabilidad:
    Orquestar la propagacion del `corpus_case_id` entre el webhook de voz
    pre-llamada y el callback de estado de grabacion:

        registrar(call_sid, corpus_case_id)  -> upsert del mapeo (si hay param)
        resolver_y_borrar(call_sid)          -> valor + borrado de la fila
        purgar_vencidas()                    -> purga TTL oportunista

    La capa de rutas no toca el repositorio: construye este servicio y delega.
    El reloj es inyectable para testear el TTL sin depender del tiempo real.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.cost_guard.clock import SystemClock
from app.cost_guard.protocols import Clock
from app.models.telefonia_pending_call import TelefoniaPendingCall
from app.repositories.telefonia_pending_call_repository import (
    TelefoniaPendingCallRepository,
)


class TelefoniaPendingCallService:
    """Servicio de correlacion opcional llamada <-> caso del corpus."""

    def __init__(
        self, session: AsyncSession, *, clock: Clock | None = None
    ) -> None:
        self._repo = TelefoniaPendingCallRepository(session)
        self._clock = clock or SystemClock()

    async def registrar(
        self, call_sid: str | None, corpus_case_id: str | None
    ) -> TelefoniaPendingCall | None:
        """
        Persiste el mapeo `call_sid -> corpus_case_id` tras el webhook de voz.

        Es retrocompatible: sin `call_sid` o sin `corpus_case_id` es un no-op
        (una llamada de produccion no escribe nada).
        """
        if not call_sid or not corpus_case_id:
            return None
        return await self._repo.upsert(call_sid, corpus_case_id)

    async def resolver_y_borrar(self, call_sid: str | None) -> str | None:
        """
        Resuelve el `corpus_case_id` de un `call_sid` y BORRA la fila pendiente.

        Returns:
            El `corpus_case_id` correlacionado, o None si no habia mapeo (llamada
            de produccion o callback reintentado tras el borrado).
        """
        if not call_sid:
            return None
        fila = await self._repo.get_by_call_sid(call_sid)
        if fila is None:
            return None
        valor = fila.corpus_case_id
        await self._repo.delete_by_call_sid(call_sid)
        return valor

    async def purgar_vencidas(self) -> int:
        """Purga oportunista de los mapeos vencidos (TTL)."""
        return await self._repo.purge_expired(self._clock.now())


__all__ = ["TelefoniaPendingCallService"]
