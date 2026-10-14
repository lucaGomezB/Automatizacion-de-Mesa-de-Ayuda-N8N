/**
 * Hook de React Query para la cola de clasificaciones pendientes de revisión humana.
 *
 * Responsabilidad:
 *   Consulta el endpoint GET /api/v1/clasificaciones/revision-pendiente y mantiene
 *   la lista de clasificaciones con confianza inferior al umbral de revisión humana
 *   del clasificador (0.70) sincronizada con el servidor. Expone además el conteo
 *   total del alcance (GET /clasificaciones/revision-pendiente/count).
 *
 * Política de refresco:
 *   - `staleTime: 15 s` — los datos se consideran frescos durante 15 segundos;
 *     navegaciones rápidas entre pestañas no dispararán una nueva solicitud.
 *   - `refetchInterval: 60 s` — refresco automático en segundo plano cada minuto
 *     para que los operadores vean nuevas llegadas sin recargar la página.
 *   - `placeholderData` — mantiene los datos anteriores visibles mientras se recarga.
 */
import { useQuery } from '@tanstack/react-query';
import {
  listarRevisionPendiente,
  contarRevisionPendiente,
} from '../services/clasificacionesService';
import type { RevisionPendienteParams } from '../types/clasificacion';

/** Clave raíz de React Query para la cola de revisión pendiente de validación humana. */
export const REVISION_PENDIENTE_QUERY_KEY = 'revision-pendiente' as const;

/**
 * Obtiene la cola de clasificaciones pendientes de revisión con refresco periódico.
 *
 * @param params - Parámetros opcionales de paginación (limit/offset).
 * @param enabled - Si es false, la consulta no se dispara (p. ej. fuera del
 *   alcance GLOBAL: la cola de revisión es GLOBAL-only, c-86 FR-RBAC-002).
 * @returns Objeto de React Query con `data: ClasificacionLogRead[]`.
 */
export function useRevisionPendiente(
  params: RevisionPendienteParams = {},
  enabled = true,
) {
  return useQuery({
    queryKey: [REVISION_PENDIENTE_QUERY_KEY, params],
    queryFn: () => listarRevisionPendiente(params),
    enabled,
    staleTime: 15_000,
    refetchInterval: 60_000,
    placeholderData: (previousData) => previousData,
  });
}

/**
 * Obtiene el TOTAL de clasificaciones pendientes de revisión del alcance (FRH-008).
 *
 * La clave está prefijada por `REVISION_PENDIENTE_QUERY_KEY`, de modo que el
 * `invalidateQueries({ queryKey: [REVISION_PENDIENTE_QUERY_KEY] })` ya existente
 * en el diálogo de validación invalida también el conteo, sin tocar el diálogo.
 *
 * @param enabled - Si es false, no se consulta el conteo (alcance no GLOBAL).
 * @returns Objeto de React Query con `data: number` (total de pendientes).
 */
export function useRevisionPendienteCount(enabled = true) {
  return useQuery({
    queryKey: [REVISION_PENDIENTE_QUERY_KEY, 'count'],
    queryFn: contarRevisionPendiente,
    enabled,
    staleTime: 15_000,
    refetchInterval: 60_000,
    placeholderData: (previousData) => previousData,
  });
}
