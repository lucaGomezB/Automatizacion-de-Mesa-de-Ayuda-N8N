/**
 * Hook de React Query para el historial de incidentes cerrados (c-86, FIH-001).
 *
 * Responsabilidad:
 *   Consume `GET /api/v1/incidentes/historial-cerrados`, que acota el conjunto
 *   por el alcance del usuario en el backend (GLOBAL, SECTOR o PROPIO) y excluye
 *   los incidentes eliminados. El cliente NO amplía ni acota el alcance: solo
 *   presenta lo que el backend devuelve (FIH-004).
 *
 * `enabled` permite mantener la consulta inactiva mientras la pestaña de
 * historial no está seleccionada, evitando llamadas innecesarias.
 */
import { useQuery } from '@tanstack/react-query';
import { listarHistorialCerrados, type HistorialCerradosParams } from '../services/incidentesService';

/** Clave raíz de React Query para el historial de cerrados. */
export const HISTORIAL_CERRADOS_QUERY_KEY = 'historial-cerrados' as const;

/**
 * Obtiene el historial de cerrados visible para el alcance del usuario.
 *
 * @param params - Paginación offset-based (limit/offset).
 * @param enabled - Si es false, la consulta no se dispara (pestaña inactiva).
 * @returns Objeto de React Query con `data: IncidenteListItem[]`.
 */
export function useHistorialCerrados(
  params: HistorialCerradosParams = {},
  enabled = true
) {
  return useQuery({
    queryKey: [HISTORIAL_CERRADOS_QUERY_KEY, params],
    queryFn: () => listarHistorialCerrados(params),
    enabled,
    placeholderData: (previousData) => previousData,
  });
}