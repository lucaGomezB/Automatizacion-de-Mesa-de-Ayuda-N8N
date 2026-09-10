/**
 * Pruebas de los hooks de React Query para estadisticas.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTendencias, useResumen } from './useEstadisticas';
import type { TendenciasResponse, ResumenResponse } from '../types/estadisticas';
import * as service from '../services/estadisticasService';

vi.mock('../services/estadisticasService', () => ({
  obtenerTendencias: vi.fn(),
  obtenerResumen: vi.fn(),
}));

const mockTendencias: TendenciasResponse = {
  periodo: { desde: '2026-01-01', hasta: '2026-06-30', agrupar_por: 'mes' },
  total_incidentes: 100,
  series: [
    { periodo: '2026-01', total: 10, por_sector: { Sistemas: 5 } },
  ],
  distribucion_sectores: { Sistemas: 50, Operaciones: 30, 'Soporte Técnico': 20 },
  distribucion_estados: { nuevo: 10, cerrado: 70 },
};

const mockResumen: ResumenResponse = {
  total_incidentes: 100,
  promedio_diario: 3.33,
  distribucion_sectores: { Sistemas: 50 },
  distribucion_estados: { cerrado: 100 },
  tasa_revision_humana: 0.1,
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('useEstadisticas', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useTendencias', () => {
    it('llama a obtenerTendencias y retorna los datos', async () => {
      vi.mocked(service.obtenerTendencias).mockResolvedValueOnce(mockTendencias);

      const { result } = renderHook(
        () =>
          useTendencias({
            agrupar_por: 'mes',
            desde: '2026-01-01',
            hasta: '2026-06-30',
          }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockTendencias);
      expect(service.obtenerTendencias).toHaveBeenCalledWith({
        agrupar_por: 'mes',
        desde: '2026-01-01',
        hasta: '2026-06-30',
      });
    });
  });

  describe('useResumen', () => {
    it('llama a obtenerResumen y retorna los datos', async () => {
      vi.mocked(service.obtenerResumen).mockResolvedValueOnce(mockResumen);

      const { result } = renderHook(
        () => useResumen({ desde: '2026-01-01', hasta: '2026-06-30' }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResumen);
      expect(service.obtenerResumen).toHaveBeenCalledWith({
        desde: '2026-01-01',
        hasta: '2026-06-30',
      });
    });
  });
});
