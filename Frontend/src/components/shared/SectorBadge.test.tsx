/**
 * Pruebas de SectorBadge.
 * Verifica que muestra el nombre del sector cuando está presente
 * y "Pendiente" cuando nombre es null o undefined.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SectorBadge } from './SectorBadge';

describe('SectorBadge', () => {
  // ---------- Sectores válidos ----------

  it('muestra "Sistemas" cuando nombre es "Sistemas"', () => {
    render(<SectorBadge nombre="Sistemas" />);
    expect(screen.getByText('Sistemas')).toBeInTheDocument();
  });

  it('muestra "Operaciones" cuando nombre es "Operaciones"', () => {
    render(<SectorBadge nombre="Operaciones" />);
    expect(screen.getByText('Operaciones')).toBeInTheDocument();
  });

  it('muestra "Soporte Técnico" cuando nombre es "Soporte Técnico"', () => {
    render(<SectorBadge nombre="Soporte Técnico" />);
    expect(screen.getByText('Soporte Técnico')).toBeInTheDocument();
  });

  // ---------- Estado pendiente ----------

  it('muestra "Pendiente" cuando nombre es null', () => {
    render(<SectorBadge nombre={null} />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('muestra "Pendiente" cuando nombre es undefined', () => {
    render(<SectorBadge nombre={undefined} />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('NO muestra "Pendiente" cuando nombre es un sector válido', () => {
    render(<SectorBadge nombre="Sistemas" />);
    expect(screen.queryByText('Pendiente')).not.toBeInTheDocument();
  });
});
