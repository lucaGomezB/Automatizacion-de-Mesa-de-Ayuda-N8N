/**
 * Pruebas del hook useReportarIncidente.
 * La capa de servicios está mockeada; se verifica que el hook delega
 * correctamente a crearIncidente y expone el resultado.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useReportarIncidente } from './useReportarIncidente';
import * as incidentesService from '../services/incidentesService';
import { createTestQueryClient } from '../test/utils';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import type { IncidenteCreate, IncidenteRead } from '../types/incidente';

vi.mock('../services/incidentesService');

const mockIncidenteRead: IncidenteRead = {
  id: 7,
  descripcion_pseudonimizada: 'La impresora del piso 3 no funciona desde el lunes',
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T12:00:00Z',
  updated_at: '2026-06-11T12:00:00Z',
  sector: { id: 3, nombre: 'Soporte Técnico', descripcion: null },
  estado: { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false },
  canal_origen: { id: 2, nombre: 'formulario web', descripcion: null },
};

describe('useReportarIncidente', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function makeWrapper() {
    const client = createTestQueryClient();
    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  }

  it('invoca crearIncidente con el payload y expone el IncidenteRead resuelto', async () => {
    vi.mocked(incidentesService.crearIncidente).mockResolvedValueOnce(mockIncidenteRead);

    const { result } = renderHook(() => useReportarIncidente(), {
      wrapper: makeWrapper(),
    });

    const payload: IncidenteCreate = {
      descripcion: 'La impresora del piso 3 no funciona desde el lunes',
      prioridad: 'media',
      canal_origen_id: 2,
    };

    act(() => {
      result.current.mutate(payload);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // React Query v5 pasa un segundo argumento (contexto) a la mutationFn;
    // verificamos solo el primer argumento (el payload del negocio)
    const firstCallArg = vi.mocked(incidentesService.crearIncidente).mock.calls[0][0];
    expect(firstCallArg).toEqual(payload);
    expect(result.current.data).toEqual(mockIncidenteRead);
  });

  it('expone el error cuando crearIncidente rechaza', async () => {
    const networkError = new Error('Network Error');
    vi.mocked(incidentesService.crearIncidente).mockRejectedValueOnce(networkError);

    const { result } = renderHook(() => useReportarIncidente(), {
      wrapper: makeWrapper(),
    });

    act(() => {
      result.current.mutate({ descripcion: 'test' });
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(networkError);
  });
});
