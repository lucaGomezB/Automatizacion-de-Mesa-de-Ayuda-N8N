/**
 * Tests para el componente EstadoBarChart.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EstadoBarChart } from './EstadoBarChart';

describe('EstadoBarChart', () => {
  it('muestra loading spinner cuando isLoading', () => {
    render(<EstadoBarChart data={undefined} isLoading={true} />);
    expect(screen.getByText('Cargando distribucion de estados...')).toBeInTheDocument();
  });

  it('muestra mensaje cuando no hay datos', () => {
    render(<EstadoBarChart data={{}} isLoading={false} />);
    expect(screen.getByText('Sin datos de estado')).toBeInTheDocument();
  });

  it('renderiza el grafico con los cinco estados', () => {
    const data = {
      nuevo: 5,
      'en proceso': 10,
      'en espera': 3,
      resuelto: 15,
      cerrado: 20,
    };
    render(<EstadoBarChart data={data} isLoading={false} />);

    expect(screen.getByText('Distribucion por Estado')).toBeInTheDocument();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });
});
