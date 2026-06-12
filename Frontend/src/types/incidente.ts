/**
 * Tipos TypeScript para la entidad Incidente y sus variantes de API.
 *
 * Responsabilidad:
 *   Define las interfaces que espejo los schemas Pydantic de `app/schemas/incidente.py`
 *   y los tipos auxiliares del formulario de reporte. Se distinguen tres representaciones:
 *
 *   - `IncidenteCreate`   : payload mínimo para el POST (sin IDs ni metadatos).
 *   - `IncidenteRead`     : representación completa con relaciones expandidas (detalle).
 *   - `IncidenteListItem` : proyección ligera para listas paginadas, omite `descripcion`
 *                          para reducir el payload de la respuesta.
 *   - `IncidenteFormData` : datos del formulario de UX; `nombre_usuario` y `sector_usuario`
 *                          no se envían al backend (la clasificación es responsabilidad del IA).
 */
import type { CanalOrigenRead, EstadoRead, SectorRead } from './catalog';

export type PrioridadEnum = 'baja' | 'media' | 'alta';

// Payload enviado al endpoint POST /api/v1/incidentes
export interface IncidenteCreate {
  descripcion: string;
  prioridad?: PrioridadEnum;
  canal_origen_id?: number | null;
}

// Representación completa devuelta por el endpoint de detalle GET /api/v1/incidentes/{id}
export interface IncidenteRead {
  id: number;
  /** El backend expone la descripción ya pseudonimizada (la original viaja cifrada y no sale de la API). */
  descripcion_pseudonimizada: string;
  prioridad: PrioridadEnum;
  requiere_revision_humana: boolean;
  created_at: string;
  updated_at: string;
  sector: SectorRead | null;
  estado: EstadoRead;
  canal_origen: CanalOrigenRead | null;
}

// Proyección ligera para listados paginados GET /api/v1/incidentes (sin campo descripcion)
export interface IncidenteListItem {
  id: number;
  prioridad: PrioridadEnum;
  requiere_revision_humana: boolean;
  created_at: string;
  sector: SectorRead | null;
  estado: EstadoRead;
}

// Parámetros de filtro y paginación para el endpoint de listado
export interface IncidenteListParams {
  sector_id?: number;
  estado_id?: number;
  prioridad?: PrioridadEnum;
  requiere_revision_humana?: boolean;
  desde?: string;
  hasta?: string;
  limit?: number;
  offset?: number;
}

// Datos del formulario de reporte: incluye campos de UX (nombre_usuario, sector_usuario)
// que no se envían a la API pero enriquecen la experiencia del usuario final.
export interface IncidenteFormData {
  descripcion: string;
  prioridad: PrioridadEnum;
  nombre_usuario: string;
  sector_usuario: string;
}
