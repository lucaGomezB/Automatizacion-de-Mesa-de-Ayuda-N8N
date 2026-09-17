"""
Servicio de estadisticas y analitica para el dashboard.

Responsabilidad:
    Implementa la logica de negocio de las consultas de agregacion para los
    endpoints de estadisticas. El acceso a datos (construccion y ejecucion de
    las queries agregadas) se delega en EstadisticasRepository; este servicio
    estructura las series, calcula periodos y arma los KPIs.

    Las consultas usan los indices compuestos existentes:
        - ix_incidente_created_sector (created_at, sector_id)
        - ix_incidente_estado_created (estado_id, created_at)

Agrupacion temporal portable (BE B1):
    El agrupamiento por periodo lo resuelve el repositorio con una funcion SQL
    por dialecto (`to_char` en PostgreSQL, `strftime` en SQLite). La generacion
    de periodos faltantes con ceros es una funcion pura en este servicio
    (`_fill_missing_periods`), independiente del motor.
"""

from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.estadisticas_repository import EstadisticasRepository
from app.utils.business_time import business_range_to_utc, business_today


class EstadisticasService:
    """
    Servicio de lectura para consultas de agregacion del dashboard.

    Recibe la sesion de base de datos en el constructor y construye el
    repositorio de estadisticas. Todos los metodos son asincronos y retornan
    datos estructurados listos para serializar en las respuestas de la API.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = EstadisticasRepository(session)

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

        Funcion pura: no accede a base de datos ni al dialecto SQL.

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
        desde: date | None, hasta: date | None, now: datetime | None = None
    ) -> tuple[date, date]:
        """
        Resuelve desde/hasta con fallback a ultimos 30 dias.

        El dia de negocio se obtiene con `business_today` (UTC-3), nunca con
        `date.today()`: la fecha local del servidor puede no coincidir con la
        jornada laboral argentina. `now` es la costura de reloj inyectable que
        hace determinista el resultado en los tests.
        """
        if hasta is None:
            hasta = business_today(now)
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
            desde: Fecha de inicio del rango (inclusive, dia de negocio UTC-3).
            hasta: Fecha de fin del rango (inclusive, dia de negocio UTC-3).
            sector_id: ID de sector para filtrar (opcional).

        Returns:
            dict con keys: periodo, total_incidentes, series, distribucion_sectores,
            distribucion_estados.
        """
        # El repositorio compara contra columnas UTC: el rango de dias de
        # negocio se convierte a [desde 00:00 BA, hasta+1 00:00 BA) en UTC.
        desde_utc, hasta_utc_exclusive = business_range_to_utc(desde, hasta)

        rows = await self._repo.contar_por_periodo_y_sector(
            agrupar_por, desde_utc, hasta_utc_exclusive, sector_id
        )

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
        series = self._fill_missing_periods(series_map, desde, hasta, agrupar_por)

        # Distribucion por estado en el rango
        estado_rows = await self._repo.contar_por_estado(
            desde_utc, hasta_utc_exclusive, sector_id
        )
        distribucion_estados = {
            row.estado_nombre: row.total for row in estado_rows
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
        self,
        desde: date | None = None,
        hasta: date | None = None,
        now: datetime | None = None,
    ) -> dict:
        """
        Retorna KPIs agregados para el dashboard.

        Args:
            desde: Fecha de inicio (opcional, default 30 dias atras).
            hasta: Fecha de fin (opcional, default hoy de negocio UTC-3).
            now: Instante de referencia inyectable para resolver el dia de
                negocio por defecto de forma determinista (tests).

        Returns:
            dict con keys: total_incidentes, promedio_diario, distribucion_sectores,
            distribucion_estados, tasa_revision_humana.
        """
        desde, hasta = self._default_date_range(desde, hasta, now)
        # El rango de dias de negocio se traduce a limites UTC semiabiertos:
        # [desde 00:00 BA, (hasta + 1 dia) 00:00 BA), con el superior EXCLUSIVO.
        desde_utc, hasta_utc_exclusive = business_range_to_utc(desde, hasta)

        total_incidentes = await self._repo.contar_total(
            desde_utc, hasta_utc_exclusive
        )

        # Promedio diario
        dias = (hasta - desde).days + 1
        promedio_diario = total_incidentes / max(dias, 1)

        # Distribucion por sector
        sector_rows = await self._repo.contar_por_sector(
            desde_utc, hasta_utc_exclusive
        )
        distribucion_sectores = {
            row.sector_nombre or "Sin asignar": row.total for row in sector_rows
        }

        # Distribucion por estado
        estado_rows = await self._repo.contar_por_estado(
            desde_utc, hasta_utc_exclusive, None
        )
        distribucion_estados = {
            row.estado_nombre: row.total for row in estado_rows
        }

        # Tasa de revision humana
        total_revision = await self._repo.contar_revision_humana(
            desde_utc, hasta_utc_exclusive
        )

        tasa_revision = total_revision / max(total_incidentes, 1)

        return {
            "total_incidentes": total_incidentes,
            "promedio_diario": round(promedio_diario, 2),
            "distribucion_sectores": distribucion_sectores,
            "distribucion_estados": distribucion_estados,
            "tasa_revision_humana": round(tasa_revision, 4),
        }
