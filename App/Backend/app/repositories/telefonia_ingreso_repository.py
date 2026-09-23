"""
Repositorio de acceso a datos del ingreso de telefonia (c-52).

Extiende el CRUD generico de `BaseRepository` con:
    - `get_by_call_sid`: recuperacion por la clave de idempotencia del ingreso,
      con eager loading del incidente vinculado (evita lazy-load en async).
    - `link_incidente`: registra el vinculo con el incidente creado.
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.telefonia_ingreso import TelefoniaIngreso
from app.repositories.base import BaseRepository


class TelefoniaIngresoRepository(BaseRepository[TelefoniaIngreso]):
    """Acceso a datos de los ingresos del canal de telefonia."""

    model = TelefoniaIngreso

    async def get_by_call_sid(self, call_sid: str) -> TelefoniaIngreso | None:
        """
        Recupera el ingreso asociado a un `CallSid`.

        Es la consulta de idempotencia del ingreso: permite cortocircuitar un
        callback repetido de Twilio ANTES de reservar la superficie paga y de
        descargar/transcribir (design.md D8).

        Args:
            call_sid: identificador de la llamada de Twilio.

        Returns:
            El ingreso con su incidente cargado, o None si no existe.
        """
        result = await self._session.execute(
            select(TelefoniaIngreso)
            .where(TelefoniaIngreso.call_sid == call_sid)
            .options(selectinload(TelefoniaIngreso.incidente))
        )
        return result.scalar_one_or_none()

    async def link_incidente(
        self, ingreso: TelefoniaIngreso, incidente_id: int
    ) -> TelefoniaIngreso:
        """
        Registra el vinculo del ingreso con el incidente creado.

        El vínculo se completa cuando el alta se resuelve aguas abajo (n8n
        reutiliza el indice unico de `incidente.origen_message_id` con el
        `CallSid`). Centraliza la escritura para que el servicio no manipule la
        sesion.

        Args:
            ingreso:      instancia ORM del ingreso ya persistida.
            incidente_id: ID del incidente creado a partir del ingreso.

        Returns:
            El ingreso con `incidente_id` actualizado.
        """
        ingreso.incidente_id = incidente_id
        self._session.add(ingreso)
        await self._session.flush()
        await self._session.refresh(ingreso)
        return ingreso


__all__ = ["TelefoniaIngresoRepository"]