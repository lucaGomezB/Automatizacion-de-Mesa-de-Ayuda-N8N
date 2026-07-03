"""
Servicio de estadisticas y analitica para el dashboard.

Responsabilidad:
    Implementa las consultas de agregacion para los endpoints de estadisticas.
    Ejecuta queries SQL con GROUP BY via SQLAlchemy func directamente sobre la
    tabla 'incidente' sin delegar a un repositorio, ya que los resultados de
    agregacion no mapean a una unica entidad ORM (Decision 2 del design.md).

    Las consultas usan los indices compuestos existentes:
        - ix_incidente_created_sector (created_at, sector_id)
        - ix_incidente_estado_created (estado_id, created_at)
"""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Estado, Sector
from app.models.incidente import Incidente


class EstadisticasService:
    """
    Servicio de lectura para consultas de agregacion del dashboard.

    Recibe la sesion de base de datos en el constructor. Todos los metodos
    son asincronos y retornan datos estructurados listos para serializar
    en las respuestas de la API.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Helper: fechas por defecto ──────────────────────────────────────────

    @staticmethod
    def _fill_missing_periods(
        series_map: dict[str, dict],
        desde: date,
        hasta: date,
        agrupar_por: str,
    ) -> list[dict]:
        """
        Genera todos los periodos en el rango [desde, hasta] y completa
        con ceros aquellos periodos sin datos en series_map.

        Args:
            series_map: Mapa periodo → {periodo, total, por_sector} con datos reales.
            desde: Fecha de inicio del rango.
            hasta: Fecha de fin del rango.
            agrupar_por: 'dia' o 'mes'.

        Returns:
            Lista ordenada de periodos, con ceros donde no hubo datos.
        """
        periods: list[str] = []
        current = desde
        while current <= hasta:
            if agrupar_por == "dia":
                periods.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
            else:  # mes
                periods.append(current.strftime("%Y-%m"))
                # Avanzar al primer dia del mes siguiente
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    current = current.replace(month=current.month + 1, day=1)

        result = []
        for p in periods:
            if p in series_map:
                result.append(series_map[p])
            else:
                result.append({"periodo": p, "total": 0, "por_sector": {}})
        return result

    @staticmethod
    def _default_date_range(
        desde: date | None, hasta: date | None
    ) -> tuple[date, date]:
        """Resuelve desde/hasta con fallback a ultimos 30 dias."""
        if hasta is None:
            hasta = date.today()
        if desde is None:
            desde = hasta - timedelta(days=30)
        return desde, hasta

    # ── Tendencias ──────────────────────────────────────────────────────────

    async def get_tendencias(
        self,
        agrupar_por: str,
        desde: date,
        hasta: date,
        sector_id: int | None = None,
    ) -> dict:
        """
        Retorna serie temporal de incidentes agrupados por dia o mes.

        Args:
            agrupar_por: 'dia' o 'mes'.
            desde: Fecha de inicio del rango (inclusive).
            hasta: Fecha de fin del rango (inclusive).
            sector_id: ID de sector para filtrar (opcional).

        Returns:
            dict con keys: periodo, total_incidentes, series, distribucion_sectores,
            distribucion_estados.
        """
        # Formatear periodo segun granularidad
        if agrupar_por == "dia":
            period_label = func.strftime("%Y-%m-%d", Incidente.created_at)
        else:  # mes
            period_label = func.strftime("%Y-%m", Incidente.created_at)

        # Ajustar hasta para incluir el dia completo (hasta + 1 dia, exclusive)
        # porque SQLAlchemy compara DateTime con date como midnight, y los
        # incidentes creados durante el dia quedarian excluidos.
        hasta_inclusive = hasta + timedelta(days=1)

        # Query principal: contar incidentes por periodo y sector
        # Necesitamos el join con sector para obtener el nombre
        base_query = (
            select(
                period_label.label("periodo"),
                Sector.nombre.label("sector_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Sector, Incidente.sector_id == Sector.id, isouter=True)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
        )

        if sector_id is not None:
            base_query = base_query.where(Incidente.sector_id == sector_id)

        grouped_query = (
            base_query.group_by(period_label, Sector.nombre)
            .order_by(period_label)
        )

        result = await self._session.execute(grouped_query)
        rows = result.all()

        # Construir series: cada periodo con su total y por_sector
        series_map: dict[str, dict] = {}
        distribucion_sectores: dict[str, int] = {}
        total_incidentes = 0

        for row in rows:
            periodo = row.periodo
            sector = row.sector_nombre or "Sin asignar"
            count = row.total

            if periodo not in series_map:
                series_map[periodo] = {"periodo": periodo, "total": 0, "por_sector": {}}

            series_map[periodo]["total"] += count
            series_map[periodo]["por_sector"][sector] = count
            distribucion_sectores[sector] = distribucion_sectores.get(sector, 0) + count
            total_incidentes += count

        # Rellenar periodos sin datos con ceros para que la serie sea continua
        series = self._fill_missing_periods(
            series_map, desde, hasta, agrupar_por
        )

        # Distribucion por estado en el rango
        estado_query = (
            select(
                Estado.nombre.label("estado_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Estado, Incidente.estado_id == Estado.id)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
            .group_by(Estado.nombre)
        )
        if sector_id is not None:
            estado_query = estado_query.where(Incidente.sector_id == sector_id)

        estado_result = await self._session.execute(estado_query)
        distribucion_estados = {
            row.estado_nombre: row.total for row in estado_result.all()
        }

        return {
            "periodo": {
                "desde": desde.isoformat(),
                "hasta": hasta.isoformat(),
                "agrupar_por": agrupar_por,
            },
            "total_incidentes": total_incidentes,
            "series": series,
            "distribucion_sectores": distribucion_sectores,
            "distribucion_estados": distribucion_estados,
        }

    # ── Resumen ─────────────────────────────────────────────────────────────

    async def get_resumen(
        self, desde: date | None = None, hasta: date | None = None
    ) -> dict:
        """
        Retorna KPIs agregados para el dashboard.

        Args:
            desde: Fecha de inicio (opcional, default 30 dias atras).
            hasta: Fecha de fin (opcional, default hoy).

        Returns:
            dict con keys: total_incidentes, promedio_diario, distribucion_sectores,
            distribucion_estados, tasa_revision_humana.
        """
        desde, hasta = self._default_date_range(desde, hasta)
        hasta_inclusive = hasta + timedelta(days=1)

        # Total de incidentes en el rango
        total_query = (
            select(func.count(Incidente.id))
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
        )
        total_result = await self._session.execute(total_query)
        total_incidentes = total_result.scalar_one()

        # Promedio diario
        dias = (hasta - desde).days + 1
        promedio_diario = total_incidentes / max(dias, 1)

        # Distribucion por sector
        sector_query = (
            select(
                Sector.nombre.label("sector_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Sector, Incidente.sector_id == Sector.id, isouter=True)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
            .group_by(Sector.nombre)
        )
        sector_result = await self._session.execute(sector_query)
        distribucion_sectores = {
            row.sector_nombre or "Sin asignar": row.total
            for row in sector_result.all()
        }

        # Distribucion por estado
        estado_query = (
            select(
                Estado.nombre.label("estado_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Estado, Incidente.estado_id == Estado.id)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
            .group_by(Estado.nombre)
        )
        estado_result = await self._session.execute(estado_query)
        distribucion_estados = {
            row.estado_nombre: row.total for row in estado_result.all()
        }

        # Tasa de revision humana
        revision_query = (
            select(func.count(Incidente.id))
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_inclusive)
            .where(Incidente.requiere_revision_humana == True)  # noqa: E712
        )
        revision_result = await self._session.execute(revision_query)
        total_revision = revision_result.scalar_one()

        tasa_revision = total_revision / max(total_incidentes, 1)

        return {
            "total_incidentes": total_incidentes,
            "promedio_diario": round(promedio_diario, 2),
            "distribucion_sectores": distribucion_sectores,
            "distribucion_estados": distribucion_estados,
            "tasa_revision_humana": round(tasa_revision, 4),
        }
