/**
 * Regresion (c-90, FR-RBAC-009): el formulario de reporte del usuario final NO
 * debe ofrecer la opcion `critica` entre las prioridades seleccionables.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import type { ReactNode } from 'react';
import { IncidenteForm } from './IncidenteForm';
import * as useReportarIncidenteHook from '@/hooks/useReportarIncidente';
import * as catalogosService from '@/services/catalogosService';
import { createTestQueryClient } from '@/test/utils';

vi.mock('@/hooks/useReportarIncidente');
vi.mock('@/services/catalogosService', () => ({ listarSectores: vi.fn() }));

function makeMockMutation() {
  return {
    mutate: vi.fn(),
    isPending: false,
    error: null,
    data: undefined,
    isSuccess: false,
    isError: false,
    isIdle: true,
    isPaused: false,
    reset: vi.fn(),
    mutateAsync: vi.fn(),
    context: undefined,
    variables: undefined,
    failureCount: 0,
    failureReason: null,
    status: 'idle' as const,
    submittedAt: 0,
  } as unknown as ReturnType<typeof useReportarIncidenteHook.useReportarIncidente>;
}

function renderForm() {
  const client = createTestQueryClient();
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <MemoryRouter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
  return render(<IncidenteForm onSuccess={vi.fn()} />, { wrapper: Wrapper });
}

describe('IncidenteForm - prioridad (c-90)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation()
    );
  });

  it('no ofrece la opcion critica entre las prioridades seleccionables', async () => {
    const user = userEvent.setup({ delay: null });
    renderForm();

    const trigger = document.getElementById('prioridad');
    if (!trigger) throw new Error('No se encontro el trigger de prioridad');
    await user.click(trigger);

    expect(await screen.findByRole('option', { name: 'Baja' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Media' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Alta' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: /crítica/i })).not.toBeInTheDocument();
  });
});
