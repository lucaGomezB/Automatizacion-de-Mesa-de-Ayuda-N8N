/**
 * Hooks de React Query para el directorio de empleados (c-89, frontend-directorio).
 *
 * Responsabilidad:
 *   Centraliza la consulta del listado y las mutaciones de gestion (alta, edicion,
 *   activar/desactivar, borrado ARCO y purga) sobre la API EXISTENTE del directorio.
 *   Cada mutacion invalida la clave del listado para reflejar los cambios sin que
 *   la pagina tenga que reconstruir el cache a mano.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarEmpleado,
  borrarEmpleadoArco,
  crearEmpleado,
  listarEmpleados,
  purgarDirectorio,
} from '../services/directorioService';
import type { EmpleadoCreate, EmpleadoUpdate } from '../types/directorio';

/** Clave raiz de React Query para el listado del directorio. */
export const DIRECTORIO_EMPLEADOS_QUERY_KEY = 'directorio-empleados' as const;

/**
 * Obtiene el listado del directorio.
 *
 * @param soloActivos - true consulta `solo_activos=true` (filtro "solo activos").
 * @returns Objeto de React Query con `data: Empleado[]`.
 */
export function useEmpleadosDirectorio(soloActivos: boolean) {
  return useQuery({
    queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY, soloActivos],
    queryFn: () => listarEmpleados({ soloActivos }),
  });
}

/** Alta de un empleado; invalida el listado al exito. */
export function useCrearEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: EmpleadoCreate) => crearEmpleado(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY] });
    },
  });
}

/** Edicion parcial (incluye activar/desactivar); invalida el listado al exito. */
export function useActualizarEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: EmpleadoUpdate }) =>
      actualizarEmpleado(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY] });
    },
  });
}

/** Borrado fisico por ARCO; invalida el listado al exito. */
export function useBorrarEmpleadoArco() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => borrarEmpleadoArco(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY] });
    },
  });
}

/** Purga manual por retencion; invalida el listado al exito. */
export function usePurgarDirectorio() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => purgarDirectorio(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY] });
    },
  });
}
