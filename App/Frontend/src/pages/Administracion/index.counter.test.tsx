/**
 * FE 4: el contador de revision humana debe reflejar el total de pendientes del
 * backend, no el tamano de la pagina visible. La cola se consulta sin paginar.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import AdministracionPage from './index';
import * as incidentesService from '@/services/incidentesService';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as catalogosService from '@/services/catalogosService';
import type { ClasificacionLogRead } from '@/types/clasificacion';

vi.mock('@/services/incidentesService', () => ({
  listarIncidentes: vi.fn(),
  verificarSaludApi: vi.fn(),
}));
vi.mock('@/services/clasificacionesService', () => ({
  listarRevisionPendiente: vi.fn(),
  validarClasificacion: vi.fn(),
}));
vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

function makePendiente(id: number): ClasificacionLogRead {
  return {
    id,
    incidente_id: id,
    confianza: 0.4,
    etapa: 'gemini',
    requiere_revision_humana: true,
    respuesta_raw: null,
    created_at: '2026-06-11T09:00:00Z',
    sector_predicho: { id: 1, nombre: 'Sistemas', descripcion: null },
    sector_validado: null,
  };
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AdministracionPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('AdministracionPage - contador de revision humana', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
  });

  it('muestra el total de pendientes aunque exceda el tamano de pagina', async () => {
    // 25 pendientes > PAGE_SIZE (20): el contador debe mostrar 25.
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue(
      Array.from({ length: 25 }, (_, i) => makePendiente(i + 1))
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('25')).toBeInTheDocument();
    });

    // La consulta no debe paginar: sin limit/offset que recorten el total.
    expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalled();
    const args = vi.mocked(clasificacionesService.listarRevisionPendiente).mock.calls[0][0];
    expect(args).toEqual({});
  });
});
