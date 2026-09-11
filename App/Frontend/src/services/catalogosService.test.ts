/**
 * Pruebas de la capa de servicios para catálogos.
 * apiClient mockeado — sin solicitudes HTTP reales.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import { listarSectores } from './catalogosService';
import type { SectorOpcion } from '../types/catalog';

vi.mock('./api', async (importOriginal) => {
  const original = await importOriginal<typeof import('./api')>();
  return {
    ...original,
    apiClient: {
      get: vi.fn(),
      post: vi.fn(),
      patch: vi.fn(),
    },
  };
});

const mockedApiClient = vi.mocked(apiClient);

const mockSectores: SectorOpcion[] = [
  { id: 1, nombre: 'Seguridad Informatica' },
  { id: 2, nombre: 'Soporte Tecnico Hardware' },
  { id: 3, nombre: 'Soporte Tecnico Software' },
  { id: 4, nombre: 'Bases de Datos' },
  { id: 5, nombre: 'Sistemas' },
];

describe('catalogosService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listarSectores', () => {
    it('hace GET a /catalogos/sectores y devuelve los cinco sectores', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockSectores });

      const result = await listarSectores();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/catalogos/sectores');
      expect(result).toEqual(mockSectores);
      expect(result).toHaveLength(5);
    });

    it('devuelve un arreglo vacío cuando el catálogo no tiene sectores', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

      const result = await listarSectores();

      expect(result).toEqual([]);
    });
  });
});
