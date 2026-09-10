"""
Schemas Pydantic para los endpoints de estadisticas y analitica del dashboard.

Responsabilidad:
    Define los contratos de datos de entrada (query params) y salida (respuesta)
    para los endpoints GET /api/v1/estadisticas/tendencias y /resumen.

    TendenciasRequest  → Query params: agrupar_por (dia|mes), desde, hasta, sector_id.
    TendenciasResponse → Serie temporal con totales por periodo y distribucion por sector.
    ResumenRequest     → Query params opcionales (desde, hasta).
    ResumenResponse    → KPIs agregados: totales, promedio diario, tasa revision humana.
"""

from datetime import date, timedelta
from enum import Enum

from pydantic import BaseModel, Field


class AgruparPorEnum(str, Enum):
    """Granularidad de agrupacion temporal para la serie de tendencias."""
    dia = "dia"
    mes = "mes"


class TendenciasRequest(BaseModel):
    """Query params para el endpoint GET /api/v1/estadisticas/tendencias."""
    agrupar_por: AgruparPorEnum = Field(description="Granularidad: 'dia' o 'mes'")
    desde: date = Field(description="Fecha de inicio del rango (ISO 8601, YYYY-MM-DD)")
    hasta: date = Field(description="Fecha de fin del rango (ISO 8601, YYYY-MM-DD)")
    sector_id: int | None = Field(None, description="Filtrar por sector responsable (opcional)")


class SerieTemporal(BaseModel):
    """Un punto en la serie temporal de tendencias (un periodo)."""
    periodo: str = Field(description="Etiqueta del periodo: YYYY-MM-DD (dia) o YYYY-MM (mes)")
    total: int = Field(description="Cantidad de incidentes en este periodo")
    por_sector: dict[str, int] = Field(
        default_factory=dict,
        description="Desglose de incidentes por nombre de sector (ej. {'Sistemas': 10, ...})"
    )


class PeriodoInfo(BaseModel):
    """Metadatos del rango consultado en la respuesta de tendencias."""
    desde: str = Field(description="Fecha de inicio del rango consultado")
    hasta: str = Field(description="Fecha de fin del rango consultado")
    agrupar_por: str = Field(description="Granularidad usada: 'dia' o 'mes'")


class TendenciasResponse(BaseModel):
    """Respuesta del endpoint GET /api/v1/estadisticas/tendencias."""
    periodo: PeriodoInfo
    total_incidentes: int = Field(description="Total de incidentes en el rango completo")
    series: list[SerieTemporal] = Field(default_factory=list)
    distribucion_sectores: dict[str, int] = Field(
        default_factory=dict,
        description="Distribucion agregada de incidentes por sector en el rango"
    )
    distribucion_estados: dict[str, int] = Field(
        default_factory=dict,
        description="Distribucion agregada de incidentes por estado en el rango"
    )


class ResumenRequest(BaseModel):
    """Query params opcionales para el endpoint GET /api/v1/estadisticas/resumen."""
    desde: date | None = Field(
        None,
        description="Fecha de inicio del rango. Por defecto: 30 dias atras."
    )
    hasta: date | None = Field(
        None,
        description="Fecha de fin del rango. Por defecto: hoy."
    )


class ResumenResponse(BaseModel):
    """Respuesta del endpoint GET /api/v1/estadisticas/resumen."""
    total_incidentes: int = Field(description="Total de incidentes en el rango")
    promedio_diario: float = Field(description="Promedio de incidentes por dia en el rango")
    distribucion_sectores: dict[str, int] = Field(
        default_factory=dict,
        description="Distribucion de incidentes por sector"
    )
    distribucion_estados: dict[str, int] = Field(
        default_factory=dict,
        description="Distribucion de incidentes por estado"
    )
    tasa_revision_humana: float = Field(
        description="Proporcion de incidentes que requirieron revision humana (0.0 a 1.0)"
    )
