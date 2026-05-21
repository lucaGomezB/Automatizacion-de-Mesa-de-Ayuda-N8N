/**
 * Hook de mutación de React Query para el envío del formulario de reporte de incidente.
 *
 * Responsabilidad:
 *   Encapsula el ciclo de vida completo de la solicitud POST /api/v1/incidentes:
 *   estado de carga (`isPending`), error de API (`error`) y respuesta del servidor
 *   (`data: IncidenteRead`). El resultado incluye el sector asignado por el pipeline
 *   híbrido (determinístico → Gemini → fallback).
 *
 * Uso:
 *   El componente llamador debe escuchar `onSuccess` para transicionar al estado de
 *   confirmación y `onError` / `error` para mostrar el mensaje de fallo al usuario.
 */
import { useMutation } from '@tanstack/react-query';
import { crearIncidente } from '../services/incidentesService';
import type { IncidenteCreate, IncidenteRead } from '../types/incidente';

/**
 * Expone la mutación de creación de incidente lista para ser disparada por el formulario.
 *
 * @returns Objeto `UseMutationResult<IncidenteRead, Error, IncidenteCreate>` de React Query.
 */
export function useReportarIncidente() {
  return useMutation<IncidenteRead, Error, IncidenteCreate>({
    mutationFn: crearIncidente,
  });
}
