/**
 * Derivacion de permisos de ciclo de vida en el cliente (c-86, D11).
 *
 * Los permisos se derivan del ROL devuelto por el backend, espejo del registro
 * canonico de politica de rol (`ROLE_POLICY` en el backend):
 *   - `gestion_incidentes`: cierra SU sector y edita el estado no terminal.
 *   - `mesa_de_ayuda`: cierra globalmente, reabre y edita el estado.
 *   - resto de roles: sin permisos de ciclo.
 *
 * Es una conveniencia de UX para decidir que acciones mostrar; el backend sigue
 * siendo el limite de seguridad (FIH-004): un rol no autorizado recibe 403.
 */
import type { EstadoEditable } from '@/types/incidente';

export interface PermisosCiclo {
  /** Cerrar el incidente para el sector propio del actor. */
  cerrarSector: boolean;
  /** Cerrar el incidente globalmente (todos los sectores). */
  cerrarGlobal: boolean;
  /** Rehabilitar (reabrir) un incidente cerrado. */
  reabrir: boolean;
  /** Editar el estado no terminal del incidente. */
  editarEstado: boolean;
}

export type { EstadoEditable };

/** Opciones de estado editable para el control de la UI. */
export const ESTADOS_EDITABLES: ReadonlyArray<{ valor: EstadoEditable; etiqueta: string }> = [
  { valor: 'en proceso', etiqueta: 'En Proceso' },
  { valor: 'en espera', etiqueta: 'En Espera' },
  { valor: 'resuelto', etiqueta: 'Resuelto' },
];

export function permisosCiclo(rol: string | null): PermisosCiclo {
  const esGestion = rol === 'gestion_incidentes';
  const esMesa = rol === 'mesa_de_ayuda';
  return {
    cerrarSector: esGestion,
    cerrarGlobal: esMesa,
    reabrir: esMesa,
    editarEstado: esGestion || esMesa,
  };
}