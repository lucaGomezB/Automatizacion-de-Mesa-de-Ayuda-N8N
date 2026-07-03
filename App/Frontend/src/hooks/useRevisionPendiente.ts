/**
 * Hook de React Query para la cola de clasificaciones pendientes de revisión humana.
 *
 * Responsabilidad:
 *   Consulta el endpoint GET /api/v1/clasificaciones/revision-pendiente y mantiene
 *   la lista de clasificaciones con confianza < 0.70 (umbral definido en
 *   parameters_gemini.md) sincronizada con el servidor.
 *
 * Política de refresco:
 *   - `staleTime: 15 s` — los datos se consideran frescos durante 15 segundos;
 *     navegaciones rápidas entre pestañas no dispararán una nueva solicitud.
 *   - `refetchInterval: 60 s` — refresco automático en segundo plano cada minuto
 *     para que los operadores vean nuevas llegadas sin recargar la página.
 *   - `placeholderData` — mantiene los datos anteriores visibles mientras se recarga.
 */
import { useQuery } from '@tanstack/react-query';
import { listarRevisionPendiente } from '../services/clasificacionesService';
import type { RevisionPendienteParams } from '../types/clasificacion';

/** Clave raíz de React Query para la cola de revisión pendiente de validación humana. */
export const REVISION_PENDIENTE_QUERY_KEY = 'revision-pendiente' as const;

/**
 * Obtiene la cola de clasificaciones pendientes de revisión con refresco periódico.
 *
 * @param params - Parámetros opcionales de paginación (limit/offset).
 * @returns Objeto de React Query con `data: ClasificacionLogRead[]`.
 */
export function useRevisionPendiente(params: RevisionPendienteParams = {}) {
  return useQuery({
    queryKey: [REVISION_PENDIENTE_QUERY_KEY, params],
    queryFn: () => listarRevisionPendiente(params),
    staleTime: 15_000,
    refetchInterval: 60_000,
    placeholderData: (previousData) => previousData,
  });
}
