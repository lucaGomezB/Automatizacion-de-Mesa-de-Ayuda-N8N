/**
 * Pruebas del hook useRevisionPendiente.
 * La capa de servicios está mockeada; se verifica que el hook invoca
 * listarRevisionPendiente y expone la lista de clasificaciones pendientes.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useRevisionPendiente, useRevisionPendienteCount, REVISION_PENDIENTE_QUERY_KEY } from './useRevisionPendiente';
import * as clasificacionesService from '../services/clasificacionesService';
import { createTestQueryClient } from '../test/utils';
import type { ClasificacionLogRead } from '../types/clasificacion';

vi.mock('../services/clasificacionesService');

const mockClasificacion: ClasificacionLogRead = {
  id: 5,
  incidente_id: 12,
  confianza: 0.42,
  etapa: 'gemini',
  requiere_revision_humana: true,
  respuesta_raw: '{"categoría":"Sistemas","confianza":0.42}',
  created_at: '2026-06-11T09:00:00Z',
  sector_predicho: { id: 1, nombre: 'Sistemas', descripcion: null },
  sector_validado: null,
};

describe('useRevisionPendiente', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function makeWrapper() {
    const client = createTestQueryClient();
    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  }

  it('invoca listarRevisionPendiente y expone la lista de clasificaciones pendientes', async () => {
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValueOnce([
      mockClasificacion,
    ]);

    const { result } = renderHook(() => useRevisionPendiente(), {
      wrapper: makeWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalled();
    expect(result.current.data).toEqual([mockClasificacion]);
  });

  it('expone lista vacía cuando no hay clasificaciones pendientes', async () => {
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValueOnce([]);

    const { result } = renderHook(() => useRevisionPendiente(), {
      wrapper: makeWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([]);
  });

  it('pasa los params de paginación al servicio cuando se proporcionan', async () => {
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValueOnce([
      mockClasificacion,
    ]);

    const { result } = renderHook(
      () => useRevisionPendiente({ limit: 5, offset: 10 }),
      { wrapper: makeWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalledWith({
      limit: 5,
      offset: 10,
    });
  });

  it('useRevisionPendienteCount expone el total y usa una queryKey prefijada por REVISION_PENDIENTE_QUERY_KEY', async () => {
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValueOnce(137);
    const client = createTestQueryClient();
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useRevisionPendienteCount(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(clasificacionesService.contarRevisionPendiente).toHaveBeenCalledTimes(1);
    expect(result.current.data).toBe(137);
    // La clave prefijada por REVISION_PENDIENTE_QUERY_KEY permite que la
    // invalidación por prefijo del diálogo de validación alcance el conteo.
    expect(client.getQueryData([REVISION_PENDIENTE_QUERY_KEY, 'count'])).toBe(137);
  });
});
