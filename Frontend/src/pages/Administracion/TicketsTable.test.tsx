/**
 * Pruebas de TicketsTable.
 * Cubre los 4 estados: loading, error, vacío, y con datos.
 * Los callbacks se verifican como vi.fn().
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TicketsTable } from './TicketsTable';
import type { IncidenteListItem } from '@/types/incidente';

const mockSector = { id: 1, nombre: 'Sistemas', descripcion: null };
const mockEstado = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };

function makeItem(id: number, overrides: Partial<IncidenteListItem> = {}): IncidenteListItem {
  return {
    id,
    prioridad: 'media',
    requiere_revision_humana: false,
    created_at: '2026-06-11T10:00:00Z',
    sector: mockSector,
    estado: mockEstado,
    ...overrides,
  };
}

describe('TicketsTable', () => {
  const defaultProps = {
    incidentes: [],
    isLoading: false,
    isError: false,
    error: null,
    onSelectIncidente: vi.fn(),
    onRefetch: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---- Estado de carga ----

  it('muestra el spinner de carga cuando isLoading es true', () => {
    render(
      <TicketsTable {...defaultProps} isLoading={true} incidentes={undefined} />
    );

    // El LoadingSpinner incluye el texto "Cargando tickets…"
    expect(screen.getByText(/cargando tickets/i)).toBeInTheDocument();
  });

  it('NO muestra filas de datos cuando isLoading es true', () => {
    render(
      <TicketsTable
        {...defaultProps}
        isLoading={true}
        incidentes={[makeItem(1)]}
      />
    );

    expect(screen.queryByRole('row')).not.toBeInTheDocument();
  });

  // ---- Estado de error ----

  it('muestra el mensaje de error normalizado cuando isError es true', () => {
    const axiosStyleError = {
      isAxiosError: true,
      response: { status: 503, data: {} },
    };

    render(
      <TicketsTable
        {...defaultProps}
        isError={true}
        error={axiosStyleError}
        incidentes={undefined}
      />
    );

    expect(screen.getByText(/servicio no está disponible/i)).toBeInTheDocument();
  });

  it('invoca onRefetch al hacer clic en Reintentar cuando isError es true', async () => {
    const onRefetch = vi.fn();
    const user = userEvent.setup();

    render(
      <TicketsTable
        {...defaultProps}
        isError={true}
        error={{ isAxiosError: true, response: { status: 500, data: {} } }}
        incidentes={undefined}
        onRefetch={onRefetch}
      />
    );

    await user.click(screen.getByRole('button', { name: /reintentar/i }));
    expect(onRefetch).toHaveBeenCalledOnce();
  });

  // ---- Estado vacío ----

  it('muestra EmptyState cuando incidentes es un array vacío', () => {
    render(<TicketsTable {...defaultProps} incidentes={[]} />);

    expect(screen.getByText(/sin tickets/i)).toBeInTheDocument();
  });

  it('muestra EmptyState cuando incidentes es undefined y sin carga ni error', () => {
    render(<TicketsTable {...defaultProps} incidentes={undefined} />);

    expect(screen.getByText(/sin tickets/i)).toBeInTheDocument();
  });

  // ---- Estado con datos ----

  it('renderiza una fila por incidente cuando hay datos', () => {
    const incidentes = [makeItem(1), makeItem(2), makeItem(3)];
    render(<TicketsTable {...defaultProps} incidentes={incidentes} />);

    // Cada incidente renderiza una fila con su ID formateado
    expect(screen.getByText('#00001')).toBeInTheDocument();
    expect(screen.getByText('#00002')).toBeInTheDocument();
    expect(screen.getByText('#00003')).toBeInTheDocument();
  });

  it('invoca onSelectIncidente con el id correcto al hacer clic en una fila', async () => {
    const onSelectIncidente = vi.fn();
    const user = userEvent.setup();

    const incidentes = [makeItem(7), makeItem(42)];
    render(
      <TicketsTable
        {...defaultProps}
        incidentes={incidentes}
        onSelectIncidente={onSelectIncidente}
      />
    );

    // Clic en la fila del incidente con id=7
    await user.click(screen.getByText('#00007'));
    expect(onSelectIncidente).toHaveBeenCalledWith(7);
  });
});
