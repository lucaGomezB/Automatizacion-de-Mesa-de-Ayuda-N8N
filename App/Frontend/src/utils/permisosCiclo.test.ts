/**
 * Pruebas de la derivacion de permisos de ciclo en el cliente (c-86, D11).
 *
 * Los permisos se derivan del ROL devuelto por el backend (nunca de la ruta ni
 * de `is_privileged`) y reflejan el registro canonico de politica de rol:
 *   - `gestion_incidentes`: cierra su sector y edita el estado (no global/reabrir).
 *   - `mesa_de_ayuda`: cierra globalmente, reabre y edita el estado.
 * La UI es UX, no el limite de seguridad: el backend sigue denegando (FIH-004).
 */
import { describe, it, expect } from 'vitest';
import { permisosCiclo } from './permisosCiclo';

describe('permisosCiclo', () => {
  it('gestion_incidentes cierra su sector y edita estado; no cierra global ni reabre', () => {
    expect(permisosCiclo('gestion_incidentes')).toEqual({
      cerrarSector: true,
      cerrarGlobal: false,
      reabrir: false,
      editarEstado: true,
    });
  });

  it('mesa_de_ayuda cierra globalmente, reabre y edita; no cierra por sector', () => {
    expect(permisosCiclo('mesa_de_ayuda')).toEqual({
      cerrarSector: false,
      cerrarGlobal: true,
      reabrir: true,
      editarEstado: true,
    });
  });

  it('administrador_directorio sin permisos de ciclo', () => {
    expect(permisosCiclo('administrador_directorio')).toEqual({
      cerrarSector: false,
      cerrarGlobal: false,
      reabrir: false,
      editarEstado: false,
    });
  });

  it('usuario_final y rol nulo/desconocido sin permisos de ciclo', () => {
    for (const rol of ['usuario_final', null, 'rol_inexistente'] as const) {
      expect(permisosCiclo(rol)).toEqual({
        cerrarSector: false,
        cerrarGlobal: false,
        reabrir: false,
        editarEstado: false,
      });
    }
  });
});