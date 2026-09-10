/**
 * Capa de acceso a datos para el recurso ClasificacionLog.
 *
 * Responsabilidad:
 *   Encapsula las llamadas HTTP al prefijo /api/v1/clasificaciones del backend FastAPI,
 *   exponiendo las operaciones necesarias para la auditoría del pipeline de IA y el
 *   flujo de revisión humana cuando la confianza de Gemini es insuficiente (< 0.70).
 *
 * Contratos de API relevantes:
 *   - GET   /clasificaciones/revision-pendiente       → cola FIFO de baja confianza
 *   - GET   /clasificaciones/incidente/{id}           → historial de un incidente
 *   - PATCH /clasificaciones/{id}/validar             → decisión del operador humano
 */
import { apiClient } from './api';
import type {
  ClasificacionLogRead,
  ClasificacionValidar,
  RevisionPendienteParams,
} from '../types/clasificacion';

/** Retorna la cola de clasificaciones pendientes de revisión humana (confianza < 0.70), orden FIFO. */
export async function listarRevisionPendiente(
  params: RevisionPendienteParams = {}
): Promise<ClasificacionLogRead[]> {
  const { data } = await apiClient.get<ClasificacionLogRead[]>(
    '/clasificaciones/revision-pendiente',
    { params }
  );
  return data;
}

/** Obtiene el historial completo de clasificaciones de un incidente específico. */
export async function listarClasificacionesPorIncidente(
  incidenteId: number
): Promise<ClasificacionLogRead[]> {
  const { data } = await apiClient.get<ClasificacionLogRead[]>(
    `/clasificaciones/incidente/${incidenteId}`
  );
  return data;
}

/** Registra la decisión del operador humano: sector correcto para un incidente con baja confianza. */
export async function validarClasificacion(
  logId: number,
  payload: ClasificacionValidar
): Promise<ClasificacionLogRead> {
  const { data } = await apiClient.patch<ClasificacionLogRead>(
    `/clasificaciones/${logId}/validar`,
    payload
  );
  return data;
}
