/**
 * Pruebas del hook useIncidentes.
 * La capa de servicios está mockeada; se verifica que el hook pasa los params
 * correctos y expone la lista devuelta por listarIncidentes.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useIncidentes } from './useIncidentes';
import * as incidentesService from '../services/incidentesService';
import { createTestQueryClient } from '../test/utils';
import type { IncidenteListItem } from '../types/incidente';

vi.mock('../services/incidentesService');

const mockSector = { id: 1, nombre: 'Sistemas', descripcion: null };
const mockEstado = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };

const mockItem: IncidenteListItem = {
  id: 1,
  prioridad: 'alta',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  sector: mockSector,
  estado: mockEstado,
};

describe('useIncidentes', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function makeWrapper() {
    const client = createTestQueryClient();
    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  }

  it('invoca listarIncidentes con los params de filtro y expone la lista', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValueOnce([mockItem]);

    const { result } = renderHook(
      () => useIncidentes({ prioridad: 'alta', limit: 10 }),
      { wrapper: makeWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(incidentesService.listarIncidentes).toHaveBeenCalledWith({ prioridad: 'alta', limit: 10 });
    expect(result.current.data).toEqual([mockItem]);
  });

  it('invoca listarIncidentes con params diferentes para una segunda llamada distinta', async () => {
    const mockItem2: IncidenteListItem = { ...mockItem, id: 2, prioridad: 'baja' };
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValueOnce([mockItem2]);

    const { result } = renderHook(
      () => useIncidentes({ prioridad: 'baja', sector_id: 2 }),
      { wrapper: makeWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(incidentesService.listarIncidentes).toHaveBeenCalledWith({ prioridad: 'baja', sector_id: 2 });
    expect(result.current.data).toEqual([mockItem2]);
  });

  it('expone la lista vacía cuando el servicio devuelve un array vacío', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useIncidentes(), { wrapper: makeWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([]);
  });
});
