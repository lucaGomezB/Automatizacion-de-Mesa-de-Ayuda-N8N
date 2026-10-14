/**
 * Hook de React Query para las mutaciones del ciclo de cierre (c-86, incident-lifecycle).
 *
 * Responsabilidad:
 *   Expone las cuatro mutaciones del ciclo (cerrar por sector, cerrar global,
 *   reabrir, editar estado) y, ante éxito, invalida las cachés que dependen del
 *   incidente: su detalle, el listado activo y el historial de cerrados. La
 *   autorización real la aplica el backend (FIH-004).
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  cerrarPorSector,
  cerrarGlobal as cerrarGlobalApi,
  rehabilitarIncidente,
  editarEstadoIncidente,
} from '../services/incidentesService';
import { INCIDENTES_QUERY_KEY } from './useIncidentes';
import { HISTORIAL_CERRADOS_QUERY_KEY } from './useHistorialCerrados';
import type { EstadoEditable, IncidenteRead } from '../types/incidente';

/**
 * Agrupa las mutaciones de ciclo del incidente indicado.
 *
 * @param incidenteId - Id del incidente sobre el que se opera.
 * @returns Objeto con las mutaciones `cerrarSector`, `cerrarGlobal`, `reabrir`
 *   y `editarEstado` (cada una con su `isPending`/`error`).
 */
export function useCicloIncidente(incidenteId: number) {
  const queryClient = useQueryClient();

  const invalidar = () => {
    void queryClient.invalidateQueries({ queryKey: ['incidente-detalle', incidenteId] });
    void queryClient.invalidateQueries({ queryKey: [INCIDENTES_QUERY_KEY] });
    void queryClient.invalidateQueries({ queryKey: [HISTORIAL_CERRADOS_QUERY_KEY] });
  };

  const cerrarSector = useMutation<IncidenteRead, unknown, void>({
    mutationFn: () => cerrarPorSector(incidenteId),
    onSuccess: invalidar,
  });

  const cerrarGlobal = useMutation<IncidenteRead, unknown, void>({
    mutationFn: () => cerrarGlobalApi(incidenteId),
    onSuccess: invalidar,
  });

  const reabrir = useMutation<IncidenteRead, unknown, void>({
    mutationFn: () => rehabilitarIncidente(incidenteId),
    onSuccess: invalidar,
  });

  const editarEstado = useMutation<IncidenteRead, unknown, EstadoEditable>({
    mutationFn: (estado) => editarEstadoIncidente(incidenteId, estado),
    onSuccess: invalidar,
  });

  return { cerrarSector, cerrarGlobal, reabrir, editarEstado };
}