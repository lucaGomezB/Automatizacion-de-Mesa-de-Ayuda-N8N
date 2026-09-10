/**
 * Capa de acceso a datos para el recurso Incidente.
 *
 * Responsabilidad:
 *   Encapsula todas las llamadas HTTP al prefijo /api/v1/incidentes del backend FastAPI.
 *   Cada función retorna los datos tipados ya extraídos del cuerpo de la respuesta,
 *   delegando el manejo de errores al llamador (hook de React Query o componente).
 *
 * Contratos de API relevantes:
 *   - POST /incidentes   → recibe `IncidenteCreate`, devuelve `IncidenteRead` completo
 *   - GET  /incidentes   → devuelve `IncidenteListItem[]` (sin campo `descripcion`)
 *   - GET  /incidentes/{id} → devuelve `IncidenteRead` con `descripcion` completa
 *   - GET  /health       → devuelve `HealthResponse { status, version }`
 */
import { apiClient } from './api';
import type {
  IncidenteCreate,
  IncidenteListItem,
  IncidenteListParams,
  IncidenteRead,
} from '../types/incidente';

/** Respuesta del endpoint GET /api/v1/health para el indicador de estado en el encabezado. */
export interface HealthResponse {
  /** Estado del servicio, típicamente "ok". */
  status: string;
  /** Versión semántica del backend, ej.: "1.0.0". */
  version: string;
}

/** Crea un nuevo incidente y dispara la clasificación automática del pipeline híbrido. */
export async function crearIncidente(payload: IncidenteCreate): Promise<IncidenteRead> {
  const { data } = await apiClient.post<IncidenteRead>('/incidentes', payload);
  return data;
}

/** Lista incidentes con filtros combinables (AND lógico) y paginación offset-based. */
export async function listarIncidentes(
  params: IncidenteListParams = {}
): Promise<IncidenteListItem[]> {
  const { data } = await apiClient.get<IncidenteListItem[]>('/incidentes', { params });
  return data;
}

/** Obtiene la representación completa de un incidente, incluida la descripción. */
export async function obtenerIncidente(id: number): Promise<IncidenteRead> {
  const { data } = await apiClient.get<IncidenteRead>(`/incidentes/${id}`);
  return data;
}

/** Verifica el estado de salud de la API; se muestra en el encabezado del panel de administración. */
export async function verificarSaludApi(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health');
  return data;
}
