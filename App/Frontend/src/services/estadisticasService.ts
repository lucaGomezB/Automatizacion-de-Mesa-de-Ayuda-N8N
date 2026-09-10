/**
 * Capa de acceso a datos para el recurso Estadisticas.
 *
 * Responsabilidad:
 *   Encapsula las llamadas HTTP al prefijo /api/v1/estadisticas del backend.
 *   Cada funcion retorna los datos tipados extraidos del cuerpo de la respuesta.
 */
import { apiClient } from './api';
import type {
  TendenciasRequest,
  TendenciasResponse,
  ResumenRequest,
  ResumenResponse,
} from '../types/estadisticas';

/** Obtiene serie temporal de incidentes agrupados por dia o mes. */
export async function obtenerTendencias(
  params: TendenciasRequest
): Promise<TendenciasResponse> {
  // Construir params limpios (sin sector_id si es undefined)
  const cleanParams: Record<string, string | number> = {
    agrupar_por: params.agrupar_por,
    desde: params.desde,
    hasta: params.hasta,
  };
  if (params.sector_id !== undefined) {
    cleanParams.sector_id = params.sector_id;
  }

  const { data } = await apiClient.get<TendenciasResponse>(
    '/estadisticas/tendencias',
    { params: cleanParams }
  );
  return data;
}

/** Obtiene KPIs agregados del dashboard para un rango de fechas. */
export async function obtenerResumen(
  params: ResumenRequest = {}
): Promise<ResumenResponse> {
  const { data } = await apiClient.get<ResumenResponse>(
    '/estadisticas/resumen',
    { params }
  );
  return data;
}
