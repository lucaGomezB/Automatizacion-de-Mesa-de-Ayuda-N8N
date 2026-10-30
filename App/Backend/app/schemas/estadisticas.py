"""
Schemas Pydantic para los endpoints de estadisticas y analitica del dashboard.

Responsabilidad:
    Define los contratos de datos de entrada (query params) y salida (respuesta)
    para los endpoints GET /api/v1/estadisticas/tendencias y /resumen.

    TendenciasRequest  → Query params: agrupar_por (dia|mes), desde, hasta, sector_id.
    TendenciasResponse → Serie temporal con totales por periodo y distribucion por sector.
    ResumenRequest     → Query params opcionales (desde, hasta).
    ResumenResponse    → KPIs agregados: totales, promedio diario, tasa revision humana y
                         tasa de intervencion registrada por el backend (c-165).
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
        description=(
            "Proporcion de incidentes del rango que, al momento de la consulta, siguen "
            "pendientes de revision humana (flag requiere_revision_humana en True; 0.0 a 1.0). "
            "No cuenta los casos marcados que ya se validaron ni mide intervenciones: para eso "
            "ver tasa_intervencion_backend."
        )
    )
    # c-165 (ECM-003): intervencion humana registrada por el backend sobre la cohorte de
    # logs de clasificacion creados en el rango. Se expone junto a (no en lugar de)
    # tasa_revision_humana.
    tasa_intervencion_backend: float = Field(
        description=(
            "Intervenciones humanas / logs de clasificacion creados en el rango (0.0 a 1.0). "
            "Cuenta un log si tiene validado_en (una confirmacion del sector predicho cuenta; "
            "un caso marcado que nadie valido, no). Excluye del numerador y del denominador "
            "los logs legados (sector validado sin validado_en, previos a la migracion 024), "
            "informados en intervenciones_legadas_excluidas. 0.0 si la cohorte esta vacia."
        )
    )
    intervenciones_por_origen: dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Intervenciones por origen_intervencion (gate, muestreo, rederivacion y "
            "completado_manual, este ultimo reservado y siempre en cero)"
        ),
    )
    intervenciones_por_cambio_sector: dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Intervenciones segun cambiaron o no el sector predicho "
            "(claves 'true' y 'false'; una confirmacion cuenta en 'false')"
        ),
    )
    intervenciones_legadas_excluidas: int = Field(
        description=(
            "Logs de la cohorte validados antes de existir los metadatos de intervencion "
            "(sector validado sin validado_en), excluidos de la tasa"
        )
    )
