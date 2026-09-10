/**
 * Pruebas de la capa de servicios para estadisticas.
 * Axis mockeado — sin solicitudes HTTP reales.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import { obtenerTendencias, obtenerResumen } from './estadisticasService';
import type { TendenciasResponse, ResumenResponse } from '../types/estadisticas';

vi.mock('./api', async (importOriginal) => {
  const original = await importOriginal<typeof import('./api')>();
  return {
    ...original,
    apiClient: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

const mockedApiClient = vi.mocked(apiClient);

const mockTendencias: TendenciasResponse = {
  periodo: { desde: '2026-01-01', hasta: '2026-06-30', agrupar_por: 'mes' },
  total_incidentes: 100,
  series: [
    { periodo: '2026-01', total: 10, por_sector: { Sistemas: 5, Operaciones: 3, 'Soporte Técnico': 2 } },
  ],
  distribucion_sectores: { Sistemas: 50, Operaciones: 30, 'Soporte Técnico': 20 },
  distribucion_estados: { nuevo: 10, 'en proceso': 20, cerrado: 70 },
};

const mockResumen: ResumenResponse = {
  total_incidentes: 100,
  promedio_diario: 3.33,
  distribucion_sectores: { Sistemas: 50, Operaciones: 30, 'Soporte Técnico': 20 },
  distribucion_estados: { nuevo: 10, cerrado: 90 },
  tasa_revision_humana: 0.15,
};

describe('estadisticasService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('obtenerTendencias', () => {
    it('hace GET a /estadisticas/tendencias con los params correctos', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockTendencias });

      const result = await obtenerTendencias({
        agrupar_por: 'mes',
        desde: '2026-01-01',
        hasta: '2026-06-30',
        sector_id: 1,
      });

      expect(mockedApiClient.get).toHaveBeenCalledWith('/estadisticas/tendencias', {
        params: {
          agrupar_por: 'mes',
          desde: '2026-01-01',
          hasta: '2026-06-30',
          sector_id: 1,
        },
      });
      expect(result).toEqual(mockTendencias);
    });

    it('omite sector_id del query cuando es undefined', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockTendencias });

      await obtenerTendencias({
        agrupar_por: 'dia',
        desde: '2026-01-01',
        hasta: '2026-01-31',
      });

      expect(mockedApiClient.get).toHaveBeenCalledWith('/estadisticas/tendencias', {
        params: {
          agrupar_por: 'dia',
          desde: '2026-01-01',
          hasta: '2026-01-31',
        },
      });
    });
  });

  describe('obtenerResumen', () => {
    it('hace GET a /estadisticas/resumen con los params opcionales', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockResumen });

      const result = await obtenerResumen({
        desde: '2026-01-01',
        hasta: '2026-12-31',
      });

      expect(mockedApiClient.get).toHaveBeenCalledWith('/estadisticas/resumen', {
        params: { desde: '2026-01-01', hasta: '2026-12-31' },
      });
      expect(result).toEqual(mockResumen);
    });

    it('hace GET a /estadisticas/resumen sin params cuando se llama vacio', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockResumen });

      await obtenerResumen();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/estadisticas/resumen', {
        params: {},
      });
    });
  });
});
