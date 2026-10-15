/**
 * Pruebas de la derivacion de permisos de asignacion de prioridad en el cliente
 * (c-90, FR-RBAC-009).
 *
 * El permiso se deriva del ROL devuelto por el backend (espejo del registro
 * canonico de politica de rol, RP-006): `mesa_de_ayuda` y
 * `administrador_directorio` pueden asignar `critica`; el resto no. La UI es UX,
 * no el limite de seguridad: el backend sigue denegando con 403.
 */
import { describe, it, expect } from 'vitest';
import { puedeAsignarPrioridadCritica, prioridadesAsignables } from './permisosPrioridad';

describe('permisosPrioridad', () => {
  it('mesa_de_ayuda y administrador_directorio pueden asignar critica', () => {
    expect(puedeAsignarPrioridadCritica('mesa_de_ayuda')).toBe(true);
    expect(puedeAsignarPrioridadCritica('administrador_directorio')).toBe(true);
  });

  it('usuario_final, gestion_incidentes y rol nulo/desconocido no pueden', () => {
    for (const rol of ['usuario_final', 'gestion_incidentes', null, 'rol_inexistente'] as const) {
      expect(puedeAsignarPrioridadCritica(rol)).toBe(false);
    }
  });

  it('las prioridades asignables incluyen critica solo con el permiso', () => {
    expect(prioridadesAsignables('mesa_de_ayuda')).toEqual(['baja', 'media', 'alta', 'critica']);
    expect(prioridadesAsignables('administrador_directorio')).toEqual([
      'baja',
      'media',
      'alta',
      'critica',
    ]);
    expect(prioridadesAsignables('usuario_final')).toEqual(['baja', 'media', 'alta']);
    expect(prioridadesAsignables(null)).toEqual(['baja', 'media', 'alta']);
  });
});
