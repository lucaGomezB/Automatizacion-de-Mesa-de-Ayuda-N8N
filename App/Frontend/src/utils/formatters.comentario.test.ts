/**
 * Pruebas del formato de comentarios (c-86, FIH-003 / D7).
 *
 * El formato es `HH:MM:SS DD/MM/AAAA : {texto}` y la marca temporal se resuelve
 * en `America/Argentina/Buenos_Aires` con independencia de la zona del servidor.
 */
import { describe, it, expect } from 'vitest';
import { formatearMarcaTemporal, formatearComentario, SEPARADOR_COMENTARIO } from './formatters';

describe('formatearMarcaTemporal', () => {
  it('convierte un instante UTC a HH:MM:SS DD/MM/AAAA en Buenos Aires', () => {
    // 2026-06-11T09:00:00Z -> 06:00:00 11/06/2026 (UTC-3, sin DST en Argentina).
    expect(formatearMarcaTemporal('2026-06-11T09:00:00Z')).toBe('06:00:00 11/06/2026');
  });

  it('cruza la medianoche local correctamente (UTC del dia siguiente)', () => {
    // 2026-06-12T01:30:00Z -> 22:30:00 11/06/2026 (aun el dia 11 en Buenos Aires).
    expect(formatearMarcaTemporal('2026-06-12T01:30:00Z')).toBe('22:30:00 11/06/2026');
  });
});

describe('formatearComentario', () => {
  it('compone la marca temporal con el texto tras el separador " : "', () => {
    expect(formatearComentario('Reinicio del servicio', '2026-06-11T09:00:00Z')).toBe(
      '06:00:00 11/06/2026 : Reinicio del servicio'
    );
  });

  it('expone el separador canonico entre entradas', () => {
    expect(SEPARADOR_COMENTARIO).toBe('----------');
  });
});