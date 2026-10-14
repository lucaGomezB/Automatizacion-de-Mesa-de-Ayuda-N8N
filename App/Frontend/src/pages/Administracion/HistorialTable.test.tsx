/**
 * Pruebas de la tabla del historial de incidentes cerrados (c-86, FIH-001 / D10).
 *
 * El estado SIEMPRE se presenta como "Cerrado", incluso si el estado del
 * incidente no es terminal (un cierre por sector aun no global). La tabla es
 * presentacional: el conjunto visible lo determina el backend.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HistorialTable } from './HistorialTable';
import type { IncidenteListItem } from '@/types/incidente';

const itemCerradoGlobal: IncidenteListItem = {
  id: 7,
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  estado: { id: 5, nombre: 'cerrado', descripcion: null, es_terminal: true },
};

function renderTabla(incidentes: IncidenteListItem[] | undefined) {
  return render(
    <HistorialTable
      incidentes={incidentes}
      isLoading={false}
      isError={false}
      error={null}
      onRefetch={vi.fn()}
    />
  );
}

describe('HistorialTable', () => {
  it('muestra el estado como "Cerrado" en una fila globalmente cerrada', () => {
    renderTabla([itemCerradoGlobal]);

    expect(screen.getByText('#00007')).toBeInTheDocument();
    expect(screen.getByText('Cerrado')).toBeInTheDocument();
    expect(screen.getByText('Sistemas')).toBeInTheDocument();
  });

  it('normaliza a "Cerrado" el estado no terminal de un cierre solo por sector', () => {
    renderTabla([
      {
        ...itemCerradoGlobal,
        estado: { id: 2, nombre: 'en proceso', descripcion: null, es_terminal: false },
      },
    ]);

    expect(screen.getByText('Cerrado')).toBeInTheDocument();
    expect(screen.queryByText('En Proceso')).not.toBeInTheDocument();
  });

  it('sin datos muestra el estado vacio del historial', () => {
    renderTabla([]);
    expect(screen.getByText(/no hay incidentes cerrados/i)).toBeInTheDocument();
  });

  it('un error del backend se presenta sin exponer filas', () => {
    render(
      <HistorialTable
        incidentes={undefined}
        isLoading={false}
        isError
        error={{ isAxiosError: true, response: { status: 403, data: {} } }}
        onRefetch={vi.fn()}
      />
    );
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    expect(screen.queryByText(/^#\d{5}$/)).not.toBeInTheDocument();
  });
});