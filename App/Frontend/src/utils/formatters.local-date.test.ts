/**
 * FE 5: el calculo de fechas del dashboard no debe desplazarse por UTC.
 *
 * `toISOString().slice(0, 10)` convierte a UTC y, en zonas negativas (UTC-3),
 * devuelve el dia siguiente despues de las 21:00 locales. `formatearFechaLocal`
 * debe usar los componentes locales de la fecha.
 */
import { describe, it, expect, afterAll } from 'vitest';
import { formatearFechaLocal } from './formatters';

const TZ_ORIGINAL = process.env.TZ;
// Forzar una zona UTC-3 para que el defecto (que solo aparece en zonas negativas)
// sea reproducible con independencia de la zona del runner.
process.env.TZ = 'America/Argentina/Buenos_Aires';

afterAll(() => {
  if (TZ_ORIGINAL === undefined) {
    delete process.env.TZ;
  } else {
    process.env.TZ = TZ_ORIGINAL;
  }
});

describe('formatearFechaLocal', () => {
  it('no corre un dia cuando la hora local supera las 21:00 en UTC-3', () => {
    // 15/01/2026 23:30 local = 16/01/2026 02:30 UTC
    const fecha = new Date(2026, 0, 15, 23, 30);
    expect(fecha.toISOString().slice(0, 10)).toBe('2026-01-16');
    expect(formatearFechaLocal(fecha)).toBe('2026-01-15');
  });

  it('rellena mes y dia con cero a la izquierda', () => {
    expect(formatearFechaLocal(new Date(2026, 0, 5, 10, 0))).toBe('2026-01-05');
  });

  it('respeta el dia local en la primera hora del dia', () => {
    expect(formatearFechaLocal(new Date(2026, 11, 31, 0, 15))).toBe('2026-12-31');
  });
});
