/**
 * Capa de acceso a datos para los catálogos de referencia del sistema.
 *
 * Responsabilidad:
 *   Encapsula las llamadas HTTP al prefijo /api/v1/catalogos del backend FastAPI.
 *   Los catálogos son datos de referencia de solo lectura; sus identificadores
 *   numéricos NO se asumen estables en el frontend, por lo que las opciones de
 *   la interfaz se construyen en runtime a partir de la respuesta del endpoint.
 *
 * Contratos de API relevantes:
 *   - GET /catalogos/sectores → devuelve `SectorOpcion[]` con id y nombre.
 */
import { apiClient } from './api';
import type { SectorOpcion } from '../types/catalog';

/** Obtiene el catálogo de sectores canónicos (id y nombre) desde el backend. */
export async function listarSectores(): Promise<SectorOpcion[]> {
  const { data } = await apiClient.get<SectorOpcion[]>('/catalogos/sectores');
  return data;
}
