"""
Repositorio del directorio de empleados (c-54).

Responsabilidad:
    Encapsula el acceso a datos de `directorio_empleado`: busquedas por email y
    telefono (en TEXTO PLANO, igualdad exacta sobre valor normalizado), por
    `user_id` y CRUD de gestion. Las busquedas de contacto devuelven SOLO
    empleados activos (DIR-007); la busqueda por legajo (gestion) tambien ve
    inactivos para permitir la reactivacion.

Decisiones:
    - D6: el telefono es repetible, por lo que la busqueda por telefono devuelve
      una lista; la capa de servicio decide la ambiguedad.
    - Async: se usa `selectinload(Empleado.sector)` para serializar sin
      lazy-load (regla del proyecto).
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.empleado import Empleado
from app.repositories.base import BaseRepository


class EmpleadoRepository(BaseRepository[Empleado]):
    """Repositorio de acceso a datos de la entidad Empleado."""

    model = Empleado

    @staticmethod
    def _con_sector(stmt):
        """Aplica la carga eager del sector a una consulta de Empleado."""
        return stmt.options(selectinload(Empleado.sector))

    async def get_by_legajo(self, legajo: str) -> Empleado | None:
        """Busca por legajo exacto, incluyendo empleados inactivos (gestion)."""
        result = await self._session.execute(
            self._con_sector(select(Empleado).where(Empleado.legajo == legajo))
        )
        return result.scalar_one_or_none()

    async def listar_por_email(self, email: str) -> list[Empleado]:
        """Devuelve los empleados ACTIVOS cuyo email coincide exactamente."""
        result = await self._session.execute(
            self._con_sector(
                select(Empleado).where(
                    Empleado.email == email,
                    Empleado.activo.is_(True),
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> Empleado | None:
        """Busca por email exacto incluyendo inactivos (chequeo de unicidad)."""
        result = await self._session.execute(
            self._con_sector(select(Empleado).where(Empleado.email == email))
        )
        return result.scalar_one_or_none()

    async def listar_por_telefono(self, telefono: str) -> list[Empleado]:
        """Devuelve los empleados ACTIVOS cuyo telefono coincide exactamente."""
        result = await self._session.execute(
            self._con_sector(
                select(Empleado).where(
                    Empleado.telefono == telefono,
                    Empleado.activo.is_(True),
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> Empleado | None:
        """
        Resuelve el empleado ACTIVO vinculado a una cuenta de autenticacion.

        `user_id` NO es UNIQUE en el directorio: si por un error de datos hay
        mas de una fila activa vinculada a la misma cuenta, se devuelve la
        primera por `id` (deterministica) en lugar de lanzar
        `MultipleResultsFound` (N3). La busqueda nunca falla por duplicados.
        """
        result = await self._session.execute(
            self._con_sector(
                select(Empleado)
                .where(
                    Empleado.user_id == user_id,
                    Empleado.activo.is_(True),
                )
                .order_by(Empleado.id)
            )
        )
        return result.scalars().first()

    async def listar_inactivos(self) -> list[Empleado]:
        """
        Devuelve TODOS los empleados inactivos (base de la retencion, DIR-007).

        No pagina: el conjunto de bajas es acotado y la purga debe evaluar el
        universo completo. El filtro de vencimiento (fecha_baja + 1 año) se
        resuelve en el servicio con una funcion pura y deterministica.
        """
        result = await self._session.execute(
            select(Empleado).where(Empleado.activo.is_(False)).order_by(Empleado.id)
        )
        return list(result.scalars().all())

    async def listar(
        self, *, solo_activos: bool = False, limit: int = 100, offset: int = 0
    ) -> list[Empleado]:
        """Lista empleados (por defecto todos, para administracion)."""
        stmt = self._con_sector(select(Empleado))
        if solo_activos:
            stmt = stmt.where(Empleado.activo.is_(True))
        stmt = stmt.order_by(Empleado.id).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
