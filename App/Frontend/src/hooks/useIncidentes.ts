/**
 * Hook de React Query para obtener la lista paginada de incidentes con filtros combinables.
 *
 * Responsabilidad:
 *   Centraliza la consulta al endpoint GET /api/v1/incidentes con soporte para filtros
 *   opcionales (sector, estado, prioridad) y paginación offset-based. Se utiliza
 *   exclusivamente en el panel de administración (TicketsTable).
 *
 * Comportamiento de caché:
 *   La clave de consulta incluye los parámetros completos para que cada combinación
 *   de filtros tenga su propia entrada en caché. `placeholderData` mantiene los datos
 *   anteriores visibles mientras se carga la nueva página, evitando parpadeos de UI.
 */
import { useQuery } from '@tanstack/react-query';
import { listarIncidentes } from '../services/incidentesService';
import type { IncidenteListParams } from '../types/incidente';

/** Clave raíz de React Query para todas las consultas de la lista de incidentes. */
export const INCIDENTES_QUERY_KEY = 'incidentes' as const;

/**
 * Obtiene la lista de incidentes filtrada y paginada desde la API.
 *
 * @param params - Filtros opcionales y parámetros de paginación (limit/offset).
 * @returns Objeto de React Query con `data: IncidenteListItem[]`, estados de carga y error.
 */
export function useIncidentes(params: IncidenteListParams = {}) {
  return useQuery({
    queryKey: [INCIDENTES_QUERY_KEY, params],
    queryFn: () => listarIncidentes(params),
    placeholderData: (previousData) => previousData,
  });
}
