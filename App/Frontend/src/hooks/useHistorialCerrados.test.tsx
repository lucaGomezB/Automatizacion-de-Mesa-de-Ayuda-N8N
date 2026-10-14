/**
 * Pruebas del hook useHistorialCerrados (c-86, FIH-001 / D10).
 *
 * La capa de servicios esta mockeada: se verifica que el hook consuma
 * `GET /api/v1/incidentes/historial-cerrados` con la paginacion recibida y que
 * respete `enabled` para no consultar un endpoint fuera de la pestana activa.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useHistorialCerrados } from './useHistorialCerrados';
import * as incidentesService from '../services/incidentesService';
import { createTestQueryClient } from '../test/utils';
import type { IncidenteListItem } from '../types/incidente';

vi.mock('../services/incidentesService');

const mockItem: IncidenteListItem = {
  id: 7,
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  estado: { id: 5, nombre: 'cerrado', descripcion: null, es_terminal: true },
};

describe('useHistorialCerrados', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function makeWrapper() {
    const client = createTestQueryClient();
    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  }

  it('consume el historial con la paginacion recibida y expone la lista', async () => {
    vi.mocked(incidentesService.listarHistorialCerrados).mockResolvedValueOnce([mockItem]);

    const { result } = renderHook(
      () => useHistorialCerrados({ limit: 20, offset: 0 }),
      { wrapper: makeWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(incidentesService.listarHistorialCerrados).toHaveBeenCalledWith({
      limit: 20,
      offset: 0,
    });
    expect(result.current.data).toEqual([mockItem]);
  });

  it('no consulta el endpoint cuando el alcance queda deshabilitado (enabled=false)', async () => {
    const { result } = renderHook(
      () => useHistorialCerrados({ limit: 20, offset: 0 }, false),
      { wrapper: makeWrapper() }
    );

    // La consulta queda en estado idle/pending sin disparar el servicio.
    expect(result.current.fetchStatus).toBe('idle');
    expect(incidentesService.listarHistorialCerrados).not.toHaveBeenCalled();
  });
});