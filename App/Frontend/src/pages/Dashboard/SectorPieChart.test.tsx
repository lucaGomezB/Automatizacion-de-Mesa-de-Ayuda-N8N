/**
 * Tests para el componente SectorPieChart.
 * Verifica los estados de carga/vacío y que el color de cada sector se resuelve
 * por el nombre canónico (tolerando nombres desconocidos con color por defecto).
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SectorPieChart, getSectorColor } from './SectorPieChart';

const SECTORES_CANONICOS: Array<[string, string]> = [
  ['Seguridad Informatica', '#dc2626'],
  ['Soporte Tecnico Hardware', '#d97706'],
  ['Soporte Tecnico Software', '#2563eb'],
  ['Bases de Datos', '#16a34a'],
  ['Sistemas', '#7c3aed'],
];

describe('SectorPieChart', () => {
  it('muestra loading spinner cuando isLoading', () => {
    render(<SectorPieChart data={undefined} isLoading={true} />);
    expect(screen.getByText('Cargando distribucion de sectores...')).toBeInTheDocument();
  });

  it('muestra mensaje cuando no hay datos', () => {
    render(<SectorPieChart data={{}} isLoading={false} />);
    expect(screen.getByText('Sin datos de sector')).toBeInTheDocument();
  });

  it('renderiza el grafico con datos de los cinco sectores', () => {
    const data = {
      'Seguridad Informatica': 10,
      'Soporte Tecnico Hardware': 20,
      'Soporte Tecnico Software': 30,
      'Bases de Datos': 25,
      Sistemas: 15,
    };
    render(<SectorPieChart data={data} isLoading={false} />);

    expect(screen.getByText('Distribucion por Sector')).toBeInTheDocument();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });

  it.each(SECTORES_CANONICOS)('resuelve el color del sector "%s"', (nombre, color) => {
    expect(getSectorColor(nombre)).toBe(color);
  });

  it('usa un color por defecto para un sector desconocido', () => {
    expect(getSectorColor('Sector Inexistente')).toBe('#6b7280');
  });

  it('renderiza un sector desconocido sin lanzar excepciones', () => {
    render(<SectorPieChart data={{ 'Sector Inexistente': 3 }} isLoading={false} />);
    expect(screen.getByText('Distribucion por Sector')).toBeInTheDocument();
  });
});
