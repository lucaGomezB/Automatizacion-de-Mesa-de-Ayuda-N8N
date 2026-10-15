/**
 * Hook de React Query para asignar la prioridad de un incidente (c-90, FR-RBAC-009).
 *
 * Responsabilidad:
 *   Expone la mutacion de asignacion de prioridad y, ante exito, invalida las
 *   caches que dependen del incidente: su detalle, el listado activo y el
 *   historial de cerrados. La autorizacion real la aplica el backend (403): el
 *   hook solo propaga el error para que la UI lo maneje sin exponer el recurso.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { actualizarPrioridadIncidente } from '../services/incidentesService';
import { INCIDENTES_QUERY_KEY } from './useIncidentes';
import { HISTORIAL_CERRADOS_QUERY_KEY } from './useHistorialCerrados';
import type { IncidenteRead, PrioridadEnum } from '../types/incidente';

/**
 * Mutacion de asignacion de prioridad del incidente indicado.
 *
 * @param incidenteId - Id del incidente a modificar.
 * @returns Mutacion de React Query (`mutate`, `isPending`, `error`).
 */
export function useAsignarPrioridad(incidenteId: number) {
  const queryClient = useQueryClient();

  return useMutation<IncidenteRead, unknown, PrioridadEnum>({
    mutationFn: (prioridad) => actualizarPrioridadIncidente(incidenteId, prioridad),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['incidente-detalle', incidenteId] });
      void queryClient.invalidateQueries({ queryKey: [INCIDENTES_QUERY_KEY] });
      void queryClient.invalidateQueries({ queryKey: [HISTORIAL_CERRADOS_QUERY_KEY] });
    },
  });
}
