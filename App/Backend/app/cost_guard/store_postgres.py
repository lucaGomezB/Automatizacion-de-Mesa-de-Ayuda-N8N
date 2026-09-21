"""
Adaptador PostgreSQL de la guarda de costo.

Ejecuta la reserva atomica de contadores en su PROPIA sesion/transaccion, fuera
de la transaccion del incidente, mediante `INSERT ... ON CONFLICT ... DO UPDATE
... RETURNING`. El UPSERT atomico evita la carrera "ambos chequean y ambos
pasan": el incremento y la lectura del valor resultante son una sola operacion.

El motor/sesion se resuelve de forma perezosa (no abre conexion hasta el primer
uso), de modo que construir el adaptador no tiene costo ni requiere PostgreSQL.
"""

from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.cost_guard.protocols import (
    CounterSnapshot,
    Reservation,
)
from app.models.costo_guarda_contador import CostoGuardaContador


class PostgresCounterStore:
    """
    Almacen de contadores en PostgreSQL con reserva atomica.

    Args:
        session_factory: `async_sessionmaker` a usar. Si es None se resuelve
            perezosamente la fabrica global de la aplicacion en el primer uso.
    """

    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession] | None = None
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    def _resolve_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            # Import perezoso: no abre conexion ni importa el engine hasta usar.
            from app.core.database import AsyncSessionFactory

            self._session_factory = AsyncSessionFactory
        return self._session_factory

    async def reserve_many(
        self, reservations: Sequence[Reservation]
    ) -> list[CounterSnapshot]:
        factory = self._resolve_factory()
        self._session = factory()
        snapshots: list[CounterSnapshot] = []
        for reservation in reservations:
            statement = (
                pg_insert(CostoGuardaContador)
                .values(
                    ambito=reservation.key.ambito,
                    clave=reservation.key.clave,
                    ventana_inicio=reservation.key.ventana_inicio,
                    llamadas=reservation.calls_delta,
                    costo_usd=reservation.cost_delta,
                )
                .on_conflict_do_update(
                    index_elements=["ambito", "clave", "ventana_inicio"],
                    set_={
                        "llamadas": CostoGuardaContador.llamadas
                        + reservation.calls_delta,
                        "costo_usd": CostoGuardaContador.costo_usd
                        + reservation.cost_delta,
                    },
                )
                .returning(
                    CostoGuardaContador.llamadas,
                    CostoGuardaContador.costo_usd,
                )
            )
            row = (await self._session.execute(statement)).one()
            snapshots.append(
                CounterSnapshot(
                    llamadas=int(row[0]),
                    costo_usd=Decimal(str(row[1])),
                )
            )
        return snapshots

    async def commit(self) -> None:
        if self._session is None:
            return
        session, self._session = self._session, None
        await session.commit()
        await session.close()

    async def rollback(self) -> None:
        if self._session is None:
            return
        session, self._session = self._session, None
        await session.rollback()
        await session.close()

    async def purge_expired(self, ambito: str, before: datetime) -> int:
        factory = self._resolve_factory()
        async with factory() as session:
            result = await session.execute(
                delete(CostoGuardaContador).where(
                    CostoGuardaContador.ambito == ambito,
                    CostoGuardaContador.ventana_inicio < before,
                )
            )
            await session.commit()
            return int(result.rowcount or 0)


__all__ = ["PostgresCounterStore"]
