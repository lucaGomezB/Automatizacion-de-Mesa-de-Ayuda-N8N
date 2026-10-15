/**
 * Pruebas del indicador de prioridad compartido (c-90, FR-RBAC-009).
 *
 * `critica` debe representarse de forma distinguible de `baja|media|alta`, y
 * `formatearPrioridad` debe cubrirla (hoy cae al fallback sin formato).
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PrioridadBadge } from './PrioridadBadge';
import { formatearPrioridad } from '@/utils/formatters';

describe('PrioridadBadge', () => {
  it('formatearPrioridad cubre critica', () => {
    expect(formatearPrioridad('critica')).toBe('Crítica');
  });

  it('mapea las prioridades base a su etiqueta', () => {
    const { rerender } = render(<PrioridadBadge prioridad="baja" />);
    expect(screen.getByText('Baja')).toBeInTheDocument();
    rerender(<PrioridadBadge prioridad="media" />);
    expect(screen.getByText('Media')).toBeInTheDocument();
    rerender(<PrioridadBadge prioridad="alta" />);
    expect(screen.getByText('Alta')).toBeInTheDocument();
  });

  it('renderiza critica de forma distinguible de alta', () => {
    const { rerender } = render(<PrioridadBadge prioridad="alta" />);
    const alta = screen.getByText('Alta');
    expect(alta).not.toHaveAttribute('data-prioridad', 'critica');
    expect(alta.className).not.toMatch(/ring-2/);

    rerender(<PrioridadBadge prioridad="critica" />);
    const critica = screen.getByText('Crítica');
    expect(critica).toHaveAttribute('data-prioridad', 'critica');
    // Marca visual propia de critica (ausente en alta): la distingue.
    expect(critica.className).toMatch(/ring-2/);
  });
});
