"""
Repositorio de acceso a datos del ingreso de telefonia (c-52).

Extiende el CRUD generico de `BaseRepository` con:
    - `get_by_call_sid`: recuperacion por la clave de idempotencia del ingreso,
      con eager loading del incidente vinculado (evita lazy-load en async).
    - `claim_for_retry`: reclamo atomico de un ingreso en estado terminal de error
      para reprocesarlo (W5).
    - `link_incidente`: registra el vinculo con el incidente creado.
"""

from collections.abc import Collection

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.telefonia_ingreso import TelefoniaIngreso, TranscripcionEstado
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

    async def claim_for_retry(
        self, call_sid: str, estados_error: Collection[TranscripcionEstado | str]
    ) -> bool:
        """
        Reclama atomicamente un ingreso en estado terminal de error para reintento.

        Ejecuta un `UPDATE ... WHERE call_sid = :sid AND transcripcion_estado IN
        (:errores)` que transiciona la fila a `pendiente` y limpia `error_detalle`.
        El UPDATE corre en la MISMA transaccion/sesion que el procesamiento
        posterior, por lo que la fila queda bloqueada (PostgreSQL READ COMMITTED):
        un reintento concurrente bloquea hasta que el primero confirma y luego su
        propio UPDATE reevalua el WHERE y afecta 0 filas.

        Args:
            call_sid:     clave de idempotencia del ingreso.
            estados_error: estados terminales de error elegibles para reintento.

        Returns:
            True si el UPDATE afecto EXACTAMENTE una fila (el reclamo gano);
            False si afecto 0 (otro reintento ya lo tomo, o el estado cambio).
        """
        valores = [getattr(estado, "value", estado) for estado in estados_error]
        statement = (
            update(TelefoniaIngreso)
            .where(
                TelefoniaIngreso.call_sid == call_sid,
                TelefoniaIngreso.transcripcion_estado.in_(valores),
            )
            .values(
                transcripcion_estado=TranscripcionEstado.pendiente,
                error_detalle=None,
            )
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(statement)
        return result.rowcount == 1

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