/**
 * Tipos de identidad y alcance de la sesion (c-81, FR-RBAC-001).
 *
 * Espejo del contrato de `GET /api/v1/auth/me` (IAH-012): el rol del empleado
 * vinculado (o nulo) y el modo de alcance derivado, con EXACTAMENTE los valores
 * PROPIO | GLOBAL | VACIO. NO modela sector ni conceptos del RBAC anterior.
 */

/** Modo de alcance de incidentes derivado del rol. */
export type ModoAlcance = 'PROPIO' | 'GLOBAL' | 'VACIO';

/** Alcance de incidentes de la sesion; solo expone el modo. */
export interface Alcance {
  modo: ModoAlcance;
}

/** Identidad efectiva de la sesion y su alcance derivado. */
export interface IdentidadActual {
  username: string;
  rol: string | null;
  alcance: Alcance;
}

/** Alcance por defecto cuando la identidad no pudo resolverse: VACIO. */
export const ALCANCE_VACIO: Alcance = { modo: 'VACIO' };
