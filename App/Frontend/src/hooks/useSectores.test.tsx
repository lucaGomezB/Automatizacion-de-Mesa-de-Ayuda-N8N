/**
 * Pruebas del hook useSectores.
 * El catálogo se obtiene en runtime desde el endpoint; la capa de servicios está mockeada.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useSectores } from './useSectores';
import * as catalogosService from '../services/catalogosService';
import type { SectorOpcion } from '../types/catalog';

vi.mock('../services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));

const mockSectores: SectorOpcion[] = [
  { id: 1, nombre: 'Seguridad Informatica' },
  { id: 2, nombre: 'Soporte Tecnico Hardware' },
  { id: 3, nombre: 'Soporte Tecnico Software' },
  { id: 4, nombre: 'Bases de Datos' },
  { id: 5, nombre: 'Sistemas' },
];

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('useSectores', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('invoca listarSectores y expone los sectores canónicos', async () => {
    vi.mocked(catalogosService.listarSectores).mockResolvedValueOnce(mockSectores);

    const { result } = renderHook(() => useSectores(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(catalogosService.listarSectores).toHaveBeenCalled();
    expect(result.current.data).toEqual(mockSectores);
  });

  it('expone un arreglo vacío cuando el catálogo no tiene sectores', async () => {
    vi.mocked(catalogosService.listarSectores).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useSectores(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([]);
  });
});
