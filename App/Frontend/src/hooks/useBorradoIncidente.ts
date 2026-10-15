/**
 * Hook de React Query para el borrado logico de un incidente (c-87, FR-RBAC-006).
 *
 * Responsabilidad:
 *   Expone la mutacion de borrado logico y, ante exito, invalida las caches que
 *   dependen del incidente: el listado activo, el historial de cerrados y su
 *   detalle. La autorizacion real la aplica el backend (403/404): el hook solo
 *   propaga el error para que la UI lo maneje sin exponer el recurso.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { borrarIncidente } from '../services/incidentesService';
import { INCIDENTES_QUERY_KEY } from './useIncidentes';
import { HISTORIAL_CERRADOS_QUERY_KEY } from './useHistorialCerrados';

/**
 * Mutacion de borrado logico del incidente indicado.
 *
 * @param incidenteId - Id del incidente a borrar logicamente.
 * @returns Mutacion de React Query (`mutate`, `isPending`, `error`).
 */
export function useBorradoIncidente(incidenteId: number) {
  const queryClient = useQueryClient();

  return useMutation<void, unknown, void>({
    mutationFn: () => borrarIncidente(incidenteId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [INCIDENTES_QUERY_KEY] });
      void queryClient.invalidateQueries({ queryKey: [HISTORIAL_CERRADOS_QUERY_KEY] });
      void queryClient.invalidateQueries({
        queryKey: ['incidente-detalle', incidenteId],
      });
    },
  });
}
