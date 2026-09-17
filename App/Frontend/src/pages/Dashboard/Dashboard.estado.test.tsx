/**
 * FE 6: estado de carga compuesto del dashboard.
 *
 * La vista combina dos consultas (tendencias y resumen). Debe considerarse
 * cargando si AL MENOS UNA sigue pendiente, y mostrar error solo cuando TODAS
 * fallaron sin datos utilizables. El error de `resumen` no puede ignorarse.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from './index';
import * as statsService from '@/services/estadisticasService';
import type { TendenciasResponse, ResumenResponse } from '@/types/estadisticas';

vi.mock('@/services/estadisticasService', () => ({
  obtenerTendencias: vi.fn(),
  obtenerResumen: vi.fn(),
}));

// El Header (PageWrapper) consulta la salud; se aísla la red.
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

const mockTendencias: TendenciasResponse = {
  periodo: { desde: '2026-06-01', hasta: '2026-06-07', agrupar_por: 'dia' },
  total_incidentes: 35,
  series: [{ periodo: '2026-06-01', total: 5, por_sector: { Sistemas: 5 } }],
  distribucion_sectores: { Sistemas: 5 },
  distribucion_estados: { nuevo: 5 },
};

const mockResumen: ResumenResponse = {
  total_incidentes: 35,
  promedio_diario: 5,
  distribucion_sectores: { Sistemas: 5 },
  distribucion_estados: { nuevo: 5 },
  tasa_revision_humana: 0.15,
};

function renderDashboard() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('DashboardPage - estado compuesto', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('muestra estado de carga mientras al menos una consulta esta pendiente', () => {
    // Tendencias nunca resuelve, resumen resuelve: la vista sigue cargando.
    vi.mocked(statsService.obtenerTendencias).mockReturnValue(
      new Promise<TendenciasResponse>(() => undefined)
    );
    vi.mocked(statsService.obtenerResumen).mockResolvedValue(mockResumen);

    renderDashboard();

    expect(screen.getByText(/cargando datos del dashboard/i)).toBeInTheDocument();
  });

  it('muestra el error cuando todas las consultas fallan sin datos', async () => {
    vi.mocked(statsService.obtenerTendencias).mockRejectedValue(new Error('fallo tendencias'));
    vi.mocked(statsService.obtenerResumen).mockRejectedValue(new Error('fallo resumen'));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/ocurrió un error inesperado/i)).toBeInTheDocument();
    });
  });

  it('no muestra el error total si una consulta aporta datos', async () => {
    vi.mocked(statsService.obtenerTendencias).mockRejectedValue(new Error('fallo tendencias'));
    vi.mocked(statsService.obtenerResumen).mockResolvedValue(mockResumen);

    renderDashboard();

    // resumen tiene datos: no debe mostrarse el error global
    await waitFor(() => {
      expect(screen.getByText('Total Incidentes')).toBeInTheDocument();
    });
    expect(screen.queryByText(/ocurrió un error inesperado/i)).not.toBeInTheDocument();
  });
});
