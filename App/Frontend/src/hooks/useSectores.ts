/**
 * Hook de React Query para el catálogo de sectores.
 *
 * Responsabilidad:
 *   Obtiene en runtime las opciones de sector desde GET /api/v1/catalogos/sectores.
 *   Es la única fuente de verdad de las opciones del formulario, del diálogo de
 *   validación humana y del filtro del panel de administración: el frontend NO
 *   depende de identificadores numéricos fijos.
 *
 * Política de caché:
 *   Los catálogos son inmutables en tiempo de ejecución; `staleTime` alto evita
 *   refetches innecesarios durante la sesión.
 */
import { useQuery } from '@tanstack/react-query';
import { listarSectores } from '../services/catalogosService';

/** Clave raíz de React Query para el catálogo de sectores. */
export const SECTORES_QUERY_KEY = 'catalogos-sectores' as const;

/**
 * Obtiene el catálogo de sectores canónicos desde la API.
 *
 * @returns Objeto de React Query con `data: SectorOpcion[]`.
 */
export function useSectores() {
  return useQuery({
    queryKey: [SECTORES_QUERY_KEY],
    queryFn: listarSectores,
    staleTime: 5 * 60_000,
  });
}
