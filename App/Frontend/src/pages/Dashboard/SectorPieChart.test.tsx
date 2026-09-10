/**
 * Tests para el componente SectorPieChart.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SectorPieChart } from './SectorPieChart';

describe('SectorPieChart', () => {
  it('muestra loading spinner cuando isLoading', () => {
    render(<SectorPieChart data={undefined} isLoading={true} />);
    expect(screen.getByText('Cargando distribucion de sectores...')).toBeInTheDocument();
  });

  it('muestra mensaje cuando no hay datos', () => {
    render(<SectorPieChart data={{}} isLoading={false} />);
    expect(screen.getByText('Sin datos de sector')).toBeInTheDocument();
  });

  it('renderiza el grafico con datos de los tres sectores', () => {
    const data = { Sistemas: 50, Operaciones: 30, 'Soporte Técnico': 20 };
    render(<SectorPieChart data={data} isLoading={false} />);

    expect(screen.getByText('Distribucion por Sector')).toBeInTheDocument();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });
});
