"""
Repositorio de consultas de agregacion para el dashboard.

Responsabilidad:
    Concentra el acceso a datos de las estadisticas del dashboard. Las
    consultas de agregacion no mapean a una unica entidad ORM, por lo que
    este repositorio expone metodos especificos que devuelven filas crudas
    listas para que el servicio las estructure.

Agrupacion temporal portable por dialecto (BE B1):
    El agrupamiento por periodo se expresa con una funcion SQL que depende
    del motor: `to_char` en PostgreSQL (produccion) y `strftime` en SQLite
    (costura de tests). Ambas devuelven el mismo formato textual
    (`YYYY-MM-DD` para dia, `YYYY-MM` para mes), de modo que la forma de la
    serie es identica en ambos motores. Nunca se usa una funcion exclusiva
    de SQLite sobre PostgreSQL.

    La seleccion del formato es una funcion pura (`period_format`) testeable
    sin base de datos; la expresion SQL se construye a partir de ella.

Limites temporales:
    Todos los metodos reciben limites de tiempo como datetimes con zona horaria
    UTC, ya convertidos desde el dia de negocio por el servicio
    (`app.utils.business_time.business_range_to_utc`). El limite `desde` es
    inclusivo y `hasta_exclusive` es EXCLUSIVO, de modo que el rango es
    semiabierto [desde, hasta_exclusive) y cubre el dia de negocio completo.
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Estado, Sector
from app.models.incidente import Incidente

# Dialectos soportados para la agrupacion temporal.
_POSTGRESQL = "postgresql"
_SQLITE = "sqlite"

# Zona horaria de negocio. Debe coincidir con
# `app.utils.business_time.BUSINESS_TZ` (America/Argentina/Buenos_Aires).
# Argentina no observa DST, por lo que UTC-3 es constante.
_BUSINESS_TZ_NAME = "America/Argentina/Buenos_Aires"


class EstadisticasRepository:
    """
    Repositorio de lectura con las consultas agregadas del dashboard.

    Recibe la sesion de base de datos por inyeccion. No expone operaciones de
    escritura: las estadisticas son de solo lectura.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Helper: seleccion portable de la funcion de periodo ────────────────

    @staticmethod
    def period_format(agrupar_por: str, dialect: str) -> str:
        """
        Devuelve el patron de formato de periodo segun granularidad y dialecto.

        Funcion PURA (sin base de datos) que permite cubrir la equivalencia
        entre motores en un test unitario.

        Args:
            agrupar_por: 'dia' o 'mes'.
            dialect:     Nombre del dialecto SQLAlchemy (ej. 'postgresql', 'sqlite').

        Returns:
            Patron de formato compatible con la funcion del dialecto.
        """
        if dialect == _POSTGRESQL:
            return "YYYY-MM-DD" if agrupar_por == "dia" else "YYYY-MM"
        return "%Y-%m-%d" if agrupar_por == "dia" else "%Y-%m"

    def _period_expression(self, agrupar_por: str, tz_offset_hours: int = -3):
        """
        Construye la expresion SQL de agrupacion temporal para el dialecto activo.

        La etiqueta de periodo refleja el DIA DE NEGOCIO argentino (UTC-3), no la
        fecha UTC: un incidente creado entre las 21:00 y las 24:00 BA pertenece al
        dia de negocio en curso aunque su timestamp UTC ya caiga en el dia
        calendario siguiente.

        Por dialecto:
            - PostgreSQL: `created_at` se convierte a
              `America/Argentina/Buenos_Aires` con `func.timezone(...)` antes de
              `to_char`.
            - SQLite: no soporta zonas horarias; se aplica un desplazamiento fijo
              de `tz_offset_hours` horas con `func.datetime(...)` antes de
              `strftime`. El default -3 es equivalente a `BUSINESS_TZ` (Argentina
              no observa DST). Es una aproximacion valida SOLO para tests: SQLite
              nunca corre en produccion.

        Args:
            agrupar_por: 'dia' o 'mes'.
            tz_offset_hours: Desplazamiento horario de la costura SQLite
                (default -3, equivalente a America/Argentina/Buenos_Aires).
                Inyectable para verificar limites de forma determinista.

        Raises:
            ValueError: Si el dialecto no esta soportado.
        """
        dialect = self._session.get_bind().dialect.name
        fmt = self.period_format(agrupar_por, dialect)
        if dialect == _POSTGRESQL:
            localized = func.timezone(_BUSINESS_TZ_NAME, Incidente.created_at)
            return func.to_char(localized, fmt)
        if dialect == _SQLITE:
            offset = f"{tz_offset_hours:+d} hours"
            localized = func.datetime(Incidente.created_at, offset)
            return func.strftime(fmt, localized)
        raise ValueError(
            f"Dialecto no soportado para agrupacion temporal: {dialect!r}"
        )

    # ── Tendencias ──────────────────────────────────────────────────────────

    async def contar_por_periodo_y_sector(
        self,
        agrupar_por: str,
        desde: datetime,
        hasta_exclusive: datetime,
        sector_id: int | None,
    ):
        """
        Cuenta incidentes agrupados por periodo y sector.

        Args:
            agrupar_por: 'dia' o 'mes'.
            desde: Limite inferior UTC inclusivo.
            hasta_exclusive: Limite superior UTC EXCLUSIVO.
            sector_id: Sector a filtrar (opcional).

        Returns:
            Lista de filas con atributos `periodo`, `sector_nombre` y `total`.
        """
        period_label = self._period_expression(agrupar_por)
        query = (
            select(
                period_label.label("periodo"),
                Sector.nombre.label("sector_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Sector, Incidente.sector_id == Sector.id, isouter=True)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_exclusive)
        )
        if sector_id is not None:
            query = query.where(Incidente.sector_id == sector_id)
        query = query.group_by(period_label, Sector.nombre).order_by(period_label)
        result = await self._session.execute(query)
        return result.all()

    async def contar_por_estado(
        self,
        desde: datetime,
        hasta_exclusive: datetime,
        sector_id: int | None,
    ):
        """
        Cuenta incidentes agrupados por estado dentro del rango.

        Args:
            desde: Limite inferior UTC inclusivo.
            hasta_exclusive: Limite superior UTC EXCLUSIVO.
            sector_id: Sector a filtrar (opcional).

        Returns:
            Lista de filas con atributos `estado_nombre` y `total`.
        """
        query = (
            select(
                Estado.nombre.label("estado_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Estado, Incidente.estado_id == Estado.id)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_exclusive)
            .group_by(Estado.nombre)
        )
        if sector_id is not None:
            query = query.where(Incidente.sector_id == sector_id)
        result = await self._session.execute(query)
        return result.all()

    # ── Resumen ─────────────────────────────────────────────────────────────

    async def contar_total(self, desde: datetime, hasta_exclusive: datetime) -> int:
        """
        Cuenta el total de incidentes creados en el rango UTC semiabierto.

        Args:
            desde: Limite inferior UTC inclusivo.
            hasta_exclusive: Limite superior UTC EXCLUSIVO.
        """
        query = (
            select(func.count(Incidente.id))
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_exclusive)
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    async def contar_por_sector(self, desde: datetime, hasta_exclusive: datetime):
        """
        Cuenta incidentes agrupados por sector dentro del rango.

        Args:
            desde: Limite inferior UTC inclusivo.
            hasta_exclusive: Limite superior UTC EXCLUSIVO.

        Returns:
            Lista de filas con atributos `sector_nombre` y `total`.
        """
        query = (
            select(
                Sector.nombre.label("sector_nombre"),
                func.count(Incidente.id).label("total"),
            )
            .select_from(Incidente)
            .join(Sector, Incidente.sector_id == Sector.id, isouter=True)
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_exclusive)
            .group_by(Sector.nombre)
        )
        result = await self._session.execute(query)
        return result.all()

    async def contar_revision_humana(
        self, desde: datetime, hasta_exclusive: datetime
    ) -> int:
        """
        Cuenta los incidentes marcados como pendientes de revision humana.

        Args:
            desde: Limite inferior UTC inclusivo.
            hasta_exclusive: Limite superior UTC EXCLUSIVO.
        """
        query = (
            select(func.count(Incidente.id))
            .where(Incidente.created_at >= desde)
            .where(Incidente.created_at < hasta_exclusive)
            .where(Incidente.requiere_revision_humana == True)  # noqa: E712
        )
        result = await self._session.execute(query)
        return result.scalar_one()
