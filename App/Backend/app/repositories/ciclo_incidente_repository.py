"""
Repositorios del ciclo de cierre de incidentes (c-86, D4/D7/D8).

Responsabilidad:
    Encapsula el acceso a datos de las tablas del ciclo de vida:
        - `incidente_cierre_sector`: cierre por sector (idempotente por PK compuesta).
        - `incidente_evento`: auditoria durable del actor y el instante de cada
          operacion de ciclo (cierre, reapertura, cambio de estado).

    La idempotencia del cierre se resuelve por la PK compuesta
    `(incidente_id, sector_id)`: un segundo cierre del mismo sector no inserta fila.
"""

from sqlalchemy import delete, select

from app.models.base import utcnow
from app.models.incidente import IncidenteCierreSector, IncidenteEvento
from app.repositories.base import BaseRepository

__all__ = [
    "IncidenteCierreSectorRepository",
    "IncidenteEventoRepository",
]


class IncidenteCierreSectorRepository(BaseRepository[IncidenteCierreSector]):
    """Acceso a datos de los cierres por sector del incidente."""

    model = IncidenteCierreSector

    async def registrar_cierre(
        self,
        *,
        incidente_id: int,
        sector_id: int,
        actor_empleado_id: int | None,
    ) -> tuple[IncidenteCierreSector, bool]:
        """
        Inserta el cierre del par (incidente, sector) si no existe (idempotente).

        Returns:
            Tupla `(cierre, creado)`. `creado` es False cuando la fila ya existia.
        """
        existente = await self._session.get(
            IncidenteCierreSector, (incidente_id, sector_id)
        )
        if existente is not None:
            return existente, False
        cierre = IncidenteCierreSector(
            incidente_id=incidente_id,
            sector_id=sector_id,
            cerrado_por=actor_empleado_id,
            cerrado_en=utcnow(),
        )
        self._session.add(cierre)
        await self._session.flush()
        return cierre, True

    async def listar_sector_ids(self, incidente_id: int) -> list[int]:
        """Devuelve los `sector_id` con un cierre registrado para el incidente."""
        result = await self._session.execute(
            select(IncidenteCierreSector.sector_id).where(
                IncidenteCierreSector.incidente_id == incidente_id
            )
        )
        return list(result.scalars().all())

    async def eliminar_por_incidente(self, incidente_id: int) -> None:
        """Elimina TODOS los cierres por sector del incidente (reapertura, D5)."""
        await self._session.execute(
            delete(IncidenteCierreSector).where(
                IncidenteCierreSector.incidente_id == incidente_id
            )
        )


class IncidenteEventoRepository(BaseRepository[IncidenteEvento]):
    """Acceso a datos de la auditoria del ciclo de vida del incidente."""

    model = IncidenteEvento

    async def registrar(
        self,
        *,
        incidente_id: int,
        tipo: str,
        actor_empleado_id: int | None = None,
        sector_id: int | None = None,
        estado_anterior: str | None = None,
        estado_nuevo: str | None = None,
    ) -> IncidenteEvento:
        """
        Registra un evento de ciclo de vida SIN PII (identificadores internos).

        Args:
            incidente_id:      incidente afectado.
            tipo:              `cierre_sector`, `cierre_global`, `reapertura` o
                               `cambio_estado`.
            actor_empleado_id: empleado que ejecuta (nullable en operaciones sin actor).
            sector_id:         sector involucrado (nullable).
            estado_anterior:   nombre del estado previo (nullable).
            estado_nuevo:      nombre del estado nuevo (nullable).
        """
        evento = IncidenteEvento(
            incidente_id=incidente_id,
            tipo=tipo,
            actor_empleado_id=actor_empleado_id,
            sector_id=sector_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
        )
        self._session.add(evento)
        await self._session.flush()
        return evento
