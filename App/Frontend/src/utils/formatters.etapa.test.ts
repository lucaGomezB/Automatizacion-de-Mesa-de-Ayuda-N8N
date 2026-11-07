/**
 * Pruebas de `formatearEtapa` (c-176, frontend-model-mentions).
 *
 * El contrato exige que la etiqueta de la etapa `gemini` sea agnóstica a la
 * versión del modelo: "Gemini", sin número de versión ni el literal "2.5 Flash".
 * Las etapas `deterministic` y `fallback` conservan su etiqueta.
 */
import { describe, it, expect } from 'vitest';
import { formatearEtapa } from './formatters';

describe('formatearEtapa', () => {
  it('etiqueta la etapa gemini sin versión del modelo', () => {
    const etiqueta = formatearEtapa('gemini');

    expect(etiqueta).toBe('Gemini');
    expect(etiqueta).not.toContain('2.5 Flash');
  });

  it('conserva las etiquetas de las etapas deterministic y fallback', () => {
    expect(formatearEtapa('deterministic')).toBe('Determinístico');
    expect(formatearEtapa('fallback')).toBe('Sin clasificar');
  });

  it('devuelve la etapa desconocida tal cual', () => {
    expect(formatearEtapa('etapa-inexistente')).toBe('etapa-inexistente');
  });
});
