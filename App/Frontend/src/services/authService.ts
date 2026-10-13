/**
 * Servicio de identidad de la sesion (c-81, FR-RBAC-001 / IAH-012).
 *
 * Responsabilidad:
 *   Encapsula la consulta al endpoint ADITIVO de solo lectura
 *   `GET /api/v1/auth/me`, que devuelve la identidad efectiva y su alcance
 *   derivado (PROPIO | GLOBAL | VACIO). No introduce logica de autorizacion en
 *   el cliente: el backend sigue siendo la fuente de verdad.
 */
import { apiClient } from './api';
import type { IdentidadActual } from '@/types/auth';

/** Obtiene la identidad y el alcance de la sesion autenticada. */
export async function obtenerIdentidad(): Promise<IdentidadActual> {
  const { data } = await apiClient.get<IdentidadActual>('/auth/me');
  return data;
}
