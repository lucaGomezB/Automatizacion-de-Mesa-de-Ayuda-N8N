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

export type PrioridadEnum = 'baja' | 'media' | 'alta' | 'critica';

/**
 * Estados NO terminales editables por subrecurso (c-86, ILC-005).
 *
 * Espejo del `IncidenteEstadoUpdate` del backend: 'cerrado' se rechaza con 422
 * porque el estado terminal solo se alcanza por el modelo de cierre.
 */
export type EstadoEditable = 'en proceso' | 'en espera' | 'resuelto';

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
  /**
   * Sectores secundarios del incidente (sin incluir el principal) — C-27.
   * La API siempre los devuelve; opcional para no romper mocks previos a c-83.
   */
  sectores_adicionales?: SectorRead[];
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
  /**
   * Búsqueda por texto libre (c-88, IS-001). El backend la trata como
   * coincidencia parcial case-insensitive de la descripción, o como número de
   * incidente cuando el término es numérico. Un término de menos de 2 caracteres
   * se comporta como búsqueda vacía.
   */
  q?: string;
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
