/**
 * Hooks de React Query para los comentarios append-only (c-86, FIH-003 / D7).
 *
 * `useComentarios` lista las entradas y `useAgregarComentario` da de alta una
 * nueva; tras el alta se invalida la lista del incidente para reflejar la
 * entrada sin exponer datos fuera de alcance.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { listarComentarios, agregarComentario } from '../services/incidentesService';
import type { ComentarioRead } from '../types/comentario';

/** Clave raiz de React Query para los comentarios de un incidente. */
export const COMENTARIOS_QUERY_KEY = 'comentarios' as const;

/** Lista los comentarios del incidente (orden cronologico ascendente). */
export function useComentarios(incidenteId: number, enabled = true) {
  return useQuery({
    queryKey: [COMENTARIOS_QUERY_KEY, incidenteId],
    queryFn: () => listarComentarios(incidenteId),
    enabled,
    staleTime: 15_000,
  });
}

/** Agrega un comentario y refresca la lista del incidente. */
export function useAgregarComentario(incidenteId: number) {
  const queryClient = useQueryClient();
  return useMutation<ComentarioRead, unknown, string>({
    mutationFn: (texto: string) => agregarComentario(incidenteId, texto),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [COMENTARIOS_QUERY_KEY, incidenteId] });
    },
  });
}