/**
 * Pruebas de ConfianzaIndicator.
 * Verifica el umbral estricto UMBRAL_REVISION = 0.70:
 *   - confianza < 0.70  → muestra "Revisar" y el porcentaje
 *   - confianza == 0.70 → NO muestra "Revisar"
 *   - confianza > 0.70  → NO muestra "Revisar"
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConfianzaIndicator } from './ConfianzaIndicator';

describe('ConfianzaIndicator', () => {
  // ---------- Por debajo del umbral ----------

  it('muestra la etiqueta "Revisar" y el porcentaje cuando confianza < 0.70', () => {
    render(<ConfianzaIndicator confianza={0.55} />);

    expect(screen.getByText('Revisar')).toBeInTheDocument();
    expect(screen.getByText('55%')).toBeInTheDocument();
  });

  it('muestra la etiqueta "Revisar" y el porcentaje correctamente para confianza muy baja (0.30)', () => {
    render(<ConfianzaIndicator confianza={0.30} />);

    expect(screen.getByText('Revisar')).toBeInTheDocument();
    expect(screen.getByText('30%')).toBeInTheDocument();
  });

  // ---------- En el umbral exacto (0.70 NO pide revisión) ----------

  it('NO muestra "Revisar" cuando confianza == 0.70 (límite exacto)', () => {
    render(<ConfianzaIndicator confianza={0.70} />);

    expect(screen.queryByText('Revisar')).not.toBeInTheDocument();
    expect(screen.getByText('70%')).toBeInTheDocument();
  });

  // ---------- Por encima del umbral ----------

  it('NO muestra "Revisar" cuando confianza > 0.70', () => {
    render(<ConfianzaIndicator confianza={0.92} />);

    expect(screen.queryByText('Revisar')).not.toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
  });

  // ---------- Porcentajes formateados (triangulación) ----------

  it('formatea el porcentaje correctamente para 0.0', () => {
    render(<ConfianzaIndicator confianza={0.0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('Revisar')).toBeInTheDocument();
  });

  it('formatea el porcentaje correctamente para 1.0 (100%)', () => {
    render(<ConfianzaIndicator confianza={1.0} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.queryByText('Revisar')).not.toBeInTheDocument();
  });
});
