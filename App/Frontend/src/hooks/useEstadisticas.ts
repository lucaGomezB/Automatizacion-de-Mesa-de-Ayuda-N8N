/**
 * Hooks de React Query para los endpoints de estadisticas del dashboard.
 *
 * Responsabilidad:
 *   Centraliza las consultas a GET /api/v1/estadisticas/tendencias y /resumen
 *   con soporte para filtros de fecha y sector. Se utilizan en la pagina
 *   Dashboard para alimentar los componentes de graficos ReCharts.
 */
import { useQuery } from '@tanstack/react-query';
import { obtenerTendencias, obtenerResumen } from '../services/estadisticasService';
import type { TendenciasRequest, ResumenRequest } from '../types/estadisticas';

/** Clave raiz de React Query para consultas de tendencias. */
export const TENDENCIAS_QUERY_KEY = 'estadisticas-tendencias' as const;
/** Clave raiz de React Query para consultas de resumen. */
export const RESUMEN_QUERY_KEY = 'estadisticas-resumen' as const;

/**
 * Obtiene la serie temporal de incidentes agrupados por dia o mes.
 *
 * @param params - Parametros de consulta: agrupar_por, desde, hasta, sector_id.
 * @returns Objeto de React Query con data: TendenciasResponse.
 */
export function useTendencias(params: TendenciasRequest) {
  return useQuery({
    queryKey: [TENDENCIAS_QUERY_KEY, params],
    queryFn: () => obtenerTendencias(params),
    placeholderData: (previousData) => previousData,
    staleTime: 60_000,
  });
}

/**
 * Obtiene los KPIs agregados del dashboard.
 *
 * @param params - Parametros opcionales: desde, hasta (default: ultimos 30 dias).
 * @returns Objeto de React Query con data: ResumenResponse.
 */
export function useResumen(params: ResumenRequest = {}) {
  return useQuery({
    queryKey: [RESUMEN_QUERY_KEY, params],
    queryFn: () => obtenerResumen(params),
    placeholderData: (previousData) => previousData,
    staleTime: 60_000,
  });
}
