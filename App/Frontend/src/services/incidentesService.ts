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
  EstadoEditable,
  IncidenteCreate,
  IncidenteListItem,
  IncidenteListParams,
  IncidenteRead,
} from '../types/incidente';
import type { ComentarioRead } from '../types/comentario';

/** Respuesta del endpoint GET /api/v1/health para el indicador de estado en el encabezado. */
export interface HealthResponse {
  /** Estado del servicio, típicamente "ok". */
  status: string;
  /** Versión semántica del backend, ej.: "1.0.0". */
  version: string;
}

/** Crea un nuevo incidente y dispara la clasificación automática del pipeline híbrido. */
export async function crearIncidente(payload: IncidenteCreate): Promise<IncidenteRead> {
  const { data } = await apiClient.post<IncidenteRead>('/incidentes/', payload);
  return data;
}

/** Lista incidentes con filtros combinables (AND lógico) y paginación offset-based. */
export async function listarIncidentes(
  params: IncidenteListParams = {}
): Promise<IncidenteListItem[]> {
  const { data } = await apiClient.get<IncidenteListItem[]>('/incidentes/', { params });
  return data;
}

/** Obtiene la representación completa de un incidente, incluida la descripción. */
export async function obtenerIncidente(id: number): Promise<IncidenteRead> {
  const { data } = await apiClient.get<IncidenteRead>(`/incidentes/${id}`);
  return data;
}

/** Parámetros de paginación del historial de cerrados (c-86, FIH-001). */
export interface HistorialCerradosParams {
  limit?: number;
  offset?: number;
}

/**
 * Lista el historial de incidentes cerrados acotado por el alcance del usuario.
 *
 * El backend (GET /api/v1/incidentes/historial-cerrados, D10) decide el conjunto
 * según el alcance derivado (GLOBAL, SECTOR o PROPIO) y excluye los eliminados;
 * el cliente NO acota datos por su cuenta. Se declara antes de `/{id}` en el
 * backend para evitar el conflicto de path.
 */
export async function listarHistorialCerrados(
  params: HistorialCerradosParams = {}
): Promise<IncidenteListItem[]> {
  const { data } = await apiClient.get<IncidenteListItem[]>('/incidentes/historial-cerrados', {
    params,
  });
  return data;
}

/** Verifica el estado de salud de la API; se muestra en el encabezado del panel de administración. */
export async function verificarSaludApi(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health');
  return data;
}

// ── Ciclo de cierre (c-86, incident-lifecycle) ───────────────────────────────

/**
 * Cierra el incidente para el PROPIO sector del actor `gestion_incidentes`
 * (POST /incidentes/{id}/cierre-sector). Idempotente; si todos los sectores
 * cerraron, el backend lo lleva al estado terminal `cerrado`.
 */
export async function cerrarPorSector(id: number): Promise<IncidenteRead> {
  const { data } = await apiClient.post<IncidenteRead>(`/incidentes/${id}/cierre-sector`);
  return data;
}

/**
 * Cierra GLOBALMENTE el incidente (POST /incidentes/{id}/cierre-global):
 * exclusivo de `mesa_de_ayuda`; registra el cierre de todos sus sectores.
 */
export async function cerrarGlobal(id: number): Promise<IncidenteRead> {
  const { data } = await apiClient.post<IncidenteRead>(`/incidentes/${id}/cierre-global`);
  return data;
}

/**
 * Rehabilita (reabre) un incidente cerrado (POST /incidentes/{id}/rehabilitar):
 * exclusivo de `mesa_de_ayuda`; lo devuelve a `en proceso`.
 */
export async function rehabilitarIncidente(id: number): Promise<IncidenteRead> {
  const { data } = await apiClient.post<IncidenteRead>(`/incidentes/${id}/rehabilitar`);
  return data;
}

/**
 * Edita el estado NO terminal del incidente (PATCH /incidentes/{id}/estado).
 * `cerrado` no es admisible: el backend responde 422.
 */
export async function editarEstadoIncidente(
  id: number,
  estado: EstadoEditable
): Promise<IncidenteRead> {
  const { data } = await apiClient.patch<IncidenteRead>(`/incidentes/${id}/estado`, { estado });
  return data;
}

// ── Borrado logico (c-87, incident-soft-delete) ──────────────────────────────

/**
 * Borra LOGICAMENTE un incidente (DELETE /incidentes/{id}).
 *
 * Exclusivo del rol `administrador_directorio` (el backend responde 403 en otro
 * caso). Responde 204 sin cuerpo; el incidente se retira de todas las vistas de
 * lectura. Un 403 o 404 se propaga al llamador para que lo maneje sin exponer el
 * recurso (FR-RBAC-005/FR-RBAC-006).
 */
export async function borrarIncidente(id: number): Promise<void> {
  await apiClient.delete(`/incidentes/${id}`);
}

// ── Comentarios append-only (c-86, incident-comments) ────────────────────────

/** Lista los comentarios del incidente en orden cronológico ascendente. */
export async function listarComentarios(id: number): Promise<ComentarioRead[]> {
  const { data } = await apiClient.get<ComentarioRead[]>(`/incidentes/${id}/comentarios`);
  return data;
}

/** Agrega un comentario append-only al incidente y devuelve la entrada creada. */
export async function agregarComentario(id: number, texto: string): Promise<ComentarioRead> {
  const { data } = await apiClient.post<ComentarioRead>(`/incidentes/${id}/comentarios`, {
    texto,
  });
  return data;
}
