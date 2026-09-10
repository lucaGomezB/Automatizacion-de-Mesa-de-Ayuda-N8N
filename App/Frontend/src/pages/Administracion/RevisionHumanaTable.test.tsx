/**
 * Pruebas de RevisionHumanaTable.
 * Cubre los 4 estados: loading, error, vacío, y con datos.
 * Verifica distinción entre clasificaciones validadas y sin validar.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RevisionHumanaTable } from './RevisionHumanaTable';
import type { ClasificacionLogRead } from '@/types/clasificacion';

const mockSectorPredicho = { id: 2, nombre: 'Operaciones', descripcion: null };
const mockSectorValidado = { id: 1, nombre: 'Sistemas', descripcion: null };

function makeClasificacion(
  id: number,
  overrides: Partial<ClasificacionLogRead> = {}
): ClasificacionLogRead {
  return {
    id,
    incidente_id: id * 10,
    confianza: 0.45,
    etapa: 'gemini',
    requiere_revision_humana: true,
    respuesta_raw: null,
    created_at: '2026-06-11T10:00:00Z',
    sector_predicho: mockSectorPredicho,
    sector_validado: null,
    ...overrides,
  };
}

describe('RevisionHumanaTable', () => {
  const defaultProps = {
    clasificaciones: [],
    isLoading: false,
    isError: false,
    error: null,
    onValidar: vi.fn(),
    onRefetch: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---- Estado de carga ----

  it('muestra el spinner de carga cuando isLoading es true', () => {
    render(
      <RevisionHumanaTable {...defaultProps} isLoading={true} clasificaciones={undefined} />
    );

    expect(screen.getByText(/cargando cola de revisión/i)).toBeInTheDocument();
  });

  it('NO muestra botones de validación cuando isLoading es true', () => {
    render(
      <RevisionHumanaTable
        {...defaultProps}
        isLoading={true}
        clasificaciones={[makeClasificacion(1)]}
      />
    );

    expect(screen.queryByRole('button', { name: /validar/i })).not.toBeInTheDocument();
  });

  // ---- Estado de error ----

  it('muestra el mensaje de error cuando isError es true', () => {
    render(
      <RevisionHumanaTable
        {...defaultProps}
        isError={true}
        error={{ isAxiosError: true, response: { status: 500, data: {} } }}
        clasificaciones={undefined}
      />
    );

    expect(screen.getByText(/error interno del servidor/i)).toBeInTheDocument();
  });

  it('invoca onRefetch al hacer clic en Reintentar', async () => {
    const onRefetch = vi.fn();
    const user = userEvent.setup();

    render(
      <RevisionHumanaTable
        {...defaultProps}
        isError={true}
        error={{ isAxiosError: true, response: { status: 404, data: {} } }}
        clasificaciones={undefined}
        onRefetch={onRefetch}
      />
    );

    await user.click(screen.getByRole('button', { name: /reintentar/i }));
    expect(onRefetch).toHaveBeenCalledOnce();
  });

  // ---- Estado vacío ----

  it('muestra EmptyState con mensaje de cola vacía cuando clasificaciones es vacío', () => {
    render(<RevisionHumanaTable {...defaultProps} clasificaciones={[]} />);

    expect(screen.getByText(/cola vacía/i)).toBeInTheDocument();
  });

  it('muestra EmptyState cuando clasificaciones es undefined', () => {
    render(<RevisionHumanaTable {...defaultProps} clasificaciones={undefined} />);

    expect(screen.getByText(/cola vacía/i)).toBeInTheDocument();
  });

  // ---- Estado con datos ----

  it('muestra el botón "Validar" para una clasificación sin validar', () => {
    const clasificacion = makeClasificacion(5, { sector_validado: null });
    render(
      <RevisionHumanaTable {...defaultProps} clasificaciones={[clasificacion]} />
    );

    expect(screen.getByRole('button', { name: /validar/i })).toBeInTheDocument();
  });

  it('invoca onValidar con la clasificación correcta al pulsar el botón Validar', async () => {
    const onValidar = vi.fn();
    const user = userEvent.setup();

    const clasificacion = makeClasificacion(5);
    render(
      <RevisionHumanaTable
        {...defaultProps}
        clasificaciones={[clasificacion]}
        onValidar={onValidar}
      />
    );

    await user.click(screen.getByRole('button', { name: /validar/i }));
    expect(onValidar).toHaveBeenCalledWith(clasificacion);
  });

  it('muestra "✓ Validado" en lugar del botón para una clasificación ya validada', () => {
    const clasificacion = makeClasificacion(8, { sector_validado: mockSectorValidado });
    render(
      <RevisionHumanaTable {...defaultProps} clasificaciones={[clasificacion]} />
    );

    // El indicador de validación usa "✓ Validado" en texto exacto
    expect(screen.getByText('✓ Validado')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /validar/i })).not.toBeInTheDocument();
  });

  it('distingue correctamente validadas y no validadas en la misma lista', async () => {
    const noValidada = makeClasificacion(1, { sector_validado: null });
    const validada = makeClasificacion(2, { sector_validado: mockSectorValidado });

    render(
      <RevisionHumanaTable
        {...defaultProps}
        clasificaciones={[noValidada, validada]}
      />
    );

    // El botón Validar existe (para la no validada)
    expect(screen.getByRole('button', { name: /validar/i })).toBeInTheDocument();
    // El indicador validado existe (para la ya validada)
    expect(screen.getByText('✓ Validado')).toBeInTheDocument();
  });
});
