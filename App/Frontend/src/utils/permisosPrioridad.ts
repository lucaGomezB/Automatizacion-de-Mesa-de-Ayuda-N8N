/**
 * Derivacion de permisos de asignacion de prioridad en el cliente (c-90, FR-RBAC-009).
 *
 * El permiso se deriva del ROL devuelto por el backend (espejo del registro
 * canonico de politica de rol, RP-006):
 *   - `mesa_de_ayuda` y `administrador_directorio`: pueden asignar `critica`.
 *   - `usuario_final`, `gestion_incidentes` y cualquier otro: no pueden.
 *
 * Es una conveniencia de UX para decidir que control mostrar; el backend sigue
 * siendo el limite de seguridad (FR-RBAC-005): un rol no autorizado recibe 403.
 */
import type { PrioridadEnum } from '@/types/incidente';

/** Prioridades siempre asignables, con o sin el permiso de critica. */
export const PRIORIDADES_BASE: ReadonlyArray<PrioridadEnum> = ['baja', 'media', 'alta'];

/** Prioridad restringida al permiso de asignacion critica (RP-006). */
export const PRIORIDAD_CRITICA: PrioridadEnum = 'critica';

/**
 * Indica si el rol puede asignar la prioridad `critica` (espejo de
 * `puede_asignar_prioridad_critica` del backend). Deniega por defecto.
 */
export function puedeAsignarPrioridadCritica(rol: string | null): boolean {
  return rol === 'mesa_de_ayuda' || rol === 'administrador_directorio';
}

/**
 * Prioridades ofrecidas en el control segun el rol: las base mas `critica`
 * unicamente cuando el rol declara el permiso.
 */
export function prioridadesAsignables(rol: string | null): PrioridadEnum[] {
  return puedeAsignarPrioridadCritica(rol)
    ? [...PRIORIDADES_BASE, PRIORIDAD_CRITICA]
    : [...PRIORIDADES_BASE];
}
