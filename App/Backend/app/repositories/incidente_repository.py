"""
Repositorio para la entidad Incidente.

Responsabilidad:
    Implementa las consultas específicas de dominio para la gestión de incidentes.
    Extiende el CRUD genérico de BaseRepository con:
        - Carga de relaciones (eager loading) para evitar N+1 queries.
        - Filtrado combinado por múltiples criterios opcionales.
        - Actualización parcial de campos mediante setattr dinámico.

Decisión de eager loading:
    Se utiliza selectinload() (en lugar de joinedload) para las relaciones
    uno-a-muchos, ya que evita la duplicación de filas en el resultado
    SQL que produce un JOIN con colecciones. Para la relación uno-a-uno
    (sector, estado, canal_origen), ambas estrategias son equivalentes.
"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from app.models.incidente import Incidente, PrioridadEnum
from app.repositories.base import BaseRepository


class IncidenteRepository(BaseRepository[Incidente]):
    """
    Repositorio de acceso a datos para la entidad Incidente.

    Provee operaciones de consulta complejas que la capa de servicio
    necesita para implementar las vistas de la mesa de ayuda:
    detalle completo, listado con filtros y actualización parcial.
    """

    model = Incidente

    async def get_with_relations(self, incidente_id: int) -> Incidente | None:
        """
        Recupera un incidente con todas sus relaciones cargadas en una sola consulta.

        Usa selectinload para cargar eagerly sector, estado, canal_origen y
        clasificaciones. Esto evita el problema N+1 que ocurriría si SQLAlchemy
        lazily cargara cada relación al acceder a ella dentro del contexto de sesión.

        Args:
            incidente_id: ID del incidente a recuperar.

        Returns:
            Instancia de Incidente con relaciones cargadas, o None si no existe.
        """
        result = await self._session.execute(
            select(Incidente)
            .where(Incidente.id == incidente_id)
            .options(
                selectinload(Incidente.sector),
                selectinload(Incidente.estado),
                selectinload(Incidente.canal_origen),
                selectinload(Incidente.clasificaciones),
            )
        )
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        sector_id: int | None = None,
        estado_id: int | None = None,
        prioridad: PrioridadEnum | None = None,
        requiere_revision_humana: bool | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Incidente]:
        """
        Lista incidentes aplicando filtros opcionales combinados con AND lógico.

        Solo se incluyen en la cláusula WHERE los filtros cuyo valor es distinto
        de None. Esto implementa el patrón de búsqueda flexible donde el cliente
        puede especificar cualquier combinación de criterios.

        El resultado se ordena por created_at descendente (más reciente primero),
        que es el orden natural para una cola de trabajo de mesa de ayuda.

        Args:
            sector_id:               Filtra por sector responsable asignado.
            estado_id:               Filtra por estado actual del ciclo de vida.
            prioridad:               Filtra por nivel de prioridad.
            requiere_revision_humana: Filtra por indicador de revisión pendiente.
            desde:                   Filtra incidentes creados desde esta fecha.
            hasta:                   Filtra incidentes creados hasta esta fecha.
            limit:                   Cantidad máxima de resultados (paginación).
            offset:                  Desplazamiento para paginación.

        Returns:
            Lista de incidentes que cumplen todos los filtros especificados.
        """
        # Construcción dinámica de condiciones: solo se agregan filtros con valor
        conditions = []
        if sector_id is not None:
            conditions.append(Incidente.sector_id == sector_id)
        if estado_id is not None:
            conditions.append(Incidente.estado_id == estado_id)
        if prioridad is not None:
            conditions.append(Incidente.prioridad == prioridad)
        if requiere_revision_humana is not None:
            conditions.append(
                Incidente.requiere_revision_humana == requiere_revision_humana
            )
        if desde is not None:
            conditions.append(Incidente.created_at >= desde)
        if hasta is not None:
            conditions.append(Incidente.created_at <= hasta)

        # Consulta base con carga eager de relaciones para el listado
        stmt = (
            select(Incidente)
            .options(
                selectinload(Incidente.sector),
                selectinload(Incidente.estado),
                selectinload(Incidente.canal_origen),
            )
            .order_by(Incidente.created_at.desc())  # Más reciente primero
            .limit(limit)
            .offset(offset)
        )

        # Aplicar condiciones combinadas con AND solo si hay al menos una
        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_fields(self, incidente_id: int, **kwargs) -> Incidente:
        """
        Actualiza dinámicamente los campos especificados de un incidente.

        Implementa el patrón de actualización parcial (PATCH): solo modifica
        los atributos que se pasan como kwargs. Los valores None no se aplican,
        lo cual es coherente con el schema IncidenteUpdate que excluye None.

        Args:
            incidente_id: ID del incidente a actualizar.
            **kwargs:     Pares campo=valor a asignar.

        Returns:
            Instancia actualizada del incidente.

        Raises:
            EntityNotFoundError: Si no existe el incidente con ese ID.
        """
        instance = await self.get_by_id(incidente_id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance
