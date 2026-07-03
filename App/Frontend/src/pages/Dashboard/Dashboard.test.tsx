/**
 * Tests de integracion para la pagina Dashboard.
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

const mockTendencias: TendenciasResponse = {
  periodo: { desde: '2026-06-01', hasta: '2026-06-07', agrupar_por: 'dia' },
  total_incidentes: 35,
  series: [
    { periodo: '2026-06-01', total: 5, por_sector: { Sistemas: 3, Operaciones: 2 } },
    { periodo: '2026-06-02', total: 7, por_sector: { Sistemas: 4, Operaciones: 3 } },
  ],
  distribucion_sectores: { Sistemas: 20, Operaciones: 10, 'Soporte Técnico': 5 },
  distribucion_estados: { nuevo: 5, 'en proceso': 10, cerrado: 20 },
};

const mockResumen: ResumenResponse = {
  total_incidentes: 35,
  promedio_diario: 5.0,
  distribucion_sectores: { Sistemas: 20, Operaciones: 10, 'Soporte Técnico': 5 },
  distribucion_estados: { nuevo: 5, 'en proceso': 10, cerrado: 20 },
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

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('muestra el titulo del dashboard', () => {
    renderDashboard();
    expect(screen.getByText('Dashboard de Analitica')).toBeInTheDocument();
  });

  it('muestra KPI cards cuando los datos se cargan', async () => {
    vi.mocked(statsService.obtenerTendencias).mockResolvedValueOnce(mockTendencias);
    vi.mocked(statsService.obtenerResumen).mockResolvedValueOnce(mockResumen);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('35')).toBeInTheDocument();
    });

    // Verificar KPI cards
    expect(screen.getByText('Total Incidentes')).toBeInTheDocument();
    expect(screen.getByText('Promedio Diario')).toBeInTheDocument();
    expect(screen.getByText('Tasa Revision Humana')).toBeInTheDocument();
  });

  it('muestra controles de filtro', () => {
    renderDashboard();
    expect(screen.getByText('Dia')).toBeInTheDocument();
    expect(screen.getByText('Mes')).toBeInTheDocument();
  });
});
