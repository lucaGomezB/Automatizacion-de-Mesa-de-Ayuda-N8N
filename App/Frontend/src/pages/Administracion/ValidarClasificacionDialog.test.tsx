/**
 * FE 3: tras validar una clasificacion debe invalidarse la query del detalle del
 * incidente afectado (no solo la lista), para que el detalle muestre los datos
 * nuevos al reabrirse.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { ValidarClasificacionDialog } from './ValidarClasificacionDialog';
import { createTestQueryClient } from '@/test/utils';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as catalogosService from '@/services/catalogosService';
import { REVISION_PENDIENTE_QUERY_KEY } from '@/hooks/useRevisionPendiente';
import { INCIDENTES_QUERY_KEY } from '@/hooks/useIncidentes';
import type { ClasificacionLogRead } from '@/types/clasificacion';

vi.mock('@/services/clasificacionesService', () => ({
  validarClasificacion: vi.fn(),
}));

vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));

const mockClasificacion: ClasificacionLogRead = {
  id: 5,
  incidente_id: 12,
  confianza: 0.42,
  etapa: 'gemini',
  requiere_revision_humana: true,
  respuesta_raw: null,
  created_at: '2026-06-11T09:00:00Z',
  sector_predicho: { id: 1, nombre: 'Sistemas', descripcion: null },
  sector_validado: null,
};

describe('ValidarClasificacionDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([
      { id: 1, nombre: 'Sistemas' },
      { id: 2, nombre: 'Bases de Datos' },
    ]);
  });

  it('invalida el detalle del incidente tras validar la clasificacion', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue({
      ...mockClasificacion,
      sector_validado: { id: 1, nombre: 'Sistemas', descripcion: null },
    });

    const queryClient = createTestQueryClient();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={queryClient}>
        <ValidarClasificacionDialog open clasificacion={mockClasificacion} onClose={vi.fn()} />
      </QueryClientProvider>
    );

    await user.click(
      screen.getByRole('button', { name: /confirmar predicción|guardar corrección/i })
    );

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['incidente-detalle', 12],
      });
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: ['clasificaciones-historial', 12],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [REVISION_PENDIENTE_QUERY_KEY],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [INCIDENTES_QUERY_KEY],
    });
  });
});
