/**
 * Tipos TypeScript para los endpoints de estadisticas y analitica del dashboard.
 *
 * Responsabilidad:
 *   Define las interfaces que espejan los schemas Pydantic de
 *   `app/schemas/estadisticas.py`. Todos los campos en español por convencion
 *   del proyecto (los identifiers de dominio son en español).
 */

export type AgruparPor = 'dia' | 'mes';

/** Query params para GET /api/v1/estadisticas/tendencias */
export interface TendenciasRequest {
  agrupar_por: AgruparPor;
  desde: string;   // ISO 8601 date: YYYY-MM-DD
  hasta: string;   // ISO 8601 date: YYYY-MM-DD
  sector_id?: number;
}

/** Un punto en la serie temporal */
export interface SerieTemporal {
  periodo: string;
  total: number;
  por_sector: Record<string, number>;
}

/** Metadatos del rango en la respuesta de tendencias */
export interface PeriodoInfo {
  desde: string;
  hasta: string;
  agrupar_por: string;
}

/** Respuesta de GET /api/v1/estadisticas/tendencias */
export interface TendenciasResponse {
  periodo: PeriodoInfo;
  total_incidentes: number;
  series: SerieTemporal[];
  distribucion_sectores: Record<string, number>;
  distribucion_estados: Record<string, number>;
}

/** Query params para GET /api/v1/estadisticas/resumen */
export interface ResumenRequest {
  desde?: string;   // ISO 8601 date: YYYY-MM-DD (opcional)
  hasta?: string;   // ISO 8601 date: YYYY-MM-DD (opcional)
}

/** Respuesta de GET /api/v1/estadisticas/resumen */
export interface ResumenResponse {
  total_incidentes: number;
  promedio_diario: number;
  distribucion_sectores: Record<string, number>;
  distribucion_estados: Record<string, number>;
  tasa_revision_humana: number;
}
