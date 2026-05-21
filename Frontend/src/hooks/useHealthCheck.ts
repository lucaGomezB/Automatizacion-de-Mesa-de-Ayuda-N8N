/**
 * Hook de React Query para monitorear el estado de salud del backend en tiempo real.
 *
 * Responsabilidad:
 *   Consulta el endpoint GET /api/v1/health periódicamente y expone el resultado
 *   al componente Header, que lo renderiza como un indicador visual (punto verde/rojo).
 *   Provee retroalimentación inmediata al operador sobre la disponibilidad del servicio.
 *
 * Política de reintentos:
 *   Se limita a un único reintento (`retry: 1`) para que los fallos transitorios
 *   de red no generen esperas prolongadas antes de mostrar el indicador de error.
 */
import { useQuery } from '@tanstack/react-query';
import { verificarSaludApi } from '../services/incidentesService';

/**
 * Verifica la salud de la API con refresco cada 60 segundos.
 *
 * @returns Objeto de React Query con `data: HealthResponse` y estado `isError`/`isPending`.
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: verificarSaludApi,
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  });
}
