/**
 * Tests para el componente TendenciaChart.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TendenciaChart } from './TendenciaChart';
import type { SerieTemporal } from '@/types/estadisticas';

const mockData: SerieTemporal[] = [
  { periodo: '2026-06-01', total: 5, por_sector: { Sistemas: 5 } },
  { periodo: '2026-06-02', total: 7, por_sector: { Sistemas: 7 } },
];

describe('TendenciaChart', () => {
  it('muestra loading spinner cuando isLoading', () => {
    render(
      <TendenciaChart
        data={undefined}
        isLoading={true}
        isError={false}
        error={null}
        onRefetch={vi.fn()}
      />
    );
    expect(screen.getByText('Cargando tendencias...')).toBeInTheDocument();
  });

  it('muestra error alert con boton de reintento cuando isError', () => {
    const refetch = vi.fn();
    render(
      <TendenciaChart
        data={undefined}
        isLoading={false}
        isError={true}
        error={new Error('Fallo de red')}
        onRefetch={refetch}
      />
    );
    expect(screen.getByText('Fallo de red')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });

  it('muestra empty state cuando no hay datos', () => {
    render(
      <TendenciaChart
        data={[]}
        isLoading={false}
        isError={false}
        error={null}
        onRefetch={vi.fn()}
      />
    );
    expect(screen.getByText('Sin datos de tendencias')).toBeInTheDocument();
  });

  it('renderiza el grafico con datos y boton exportar', () => {
    render(
      <TendenciaChart
        data={mockData}
        isLoading={false}
        isError={false}
        error={null}
        onRefetch={vi.fn()}
      />
    );
    expect(screen.getByText('Tendencia de Incidentes')).toBeInTheDocument();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });
});
