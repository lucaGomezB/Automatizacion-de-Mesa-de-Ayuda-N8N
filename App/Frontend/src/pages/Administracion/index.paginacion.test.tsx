/**
 * FRH-009: la cola de revisión debe ser paginable (limit/offset) y el control
 * `Paginacion` debe usar el total exacto del conteo para decidir si hay página
 * siguiente, conservando la heurística previa cuando no se provee `total`
 * (pestaña de tickets).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import AdministracionPage, { Paginacion } from './index';
import * as incidentesService from '@/services/incidentesService';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as catalogosService from '@/services/catalogosService';
import { REVISION_PENDIENTE_QUERY_KEY } from '@/hooks/useRevisionPendiente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

vi.mock('@/services/incidentesService', () => ({
  listarIncidentes: vi.fn(),
  verificarSaludApi: vi.fn(),
}));
vi.mock('@/services/clasificacionesService', () => ({
  listarRevisionPendiente: vi.fn(),
  contarRevisionPendiente: vi.fn(),
  validarClasificacion: vi.fn(),
}));
vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    token: 't',
    username: 'admin',
    isAuthenticated: true,
    mfaRequired: false,
    rol: 'administrador_directorio',
    alcance: { modo: 'GLOBAL' },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  }),
}));

const PAGE_SIZE = 20;

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
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AdministracionPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
  return { queryClient };
}

describe('Paginacion (componente)', () => {
  it('con total provisto: no ofrece siguiente si (pagina+1)*pageSize >= total', () => {
    render(
      <Paginacion
        pagina={0}
        totalEnPagina={PAGE_SIZE}
        pageSize={PAGE_SIZE}
        total={PAGE_SIZE}
        onChange={vi.fn()}
      />
    );
    // Sin pagina anterior ni siguiente, el control no se renderiza.
    expect(screen.queryByRole('button', { name: /siguiente/i })).not.toBeInTheDocument();
  });

  it('con total provisto: deshabilita siguiente cuando hay anterior pero no siguiente', () => {
    render(
      <Paginacion
        pagina={1}
        totalEnPagina={0}
        pageSize={PAGE_SIZE}
        total={PAGE_SIZE}
        onChange={vi.fn()}
      />
    );
    expect(screen.getByRole('button', { name: /anterior/i })).toBeEnabled();
    expect(screen.getByRole('button', { name: /siguiente/i })).toBeDisabled();
  });

  it('con total provisto: ofrece siguiente si (pagina+1)*pageSize < total', () => {
    render(
      <Paginacion
        pagina={0}
        totalEnPagina={PAGE_SIZE}
        pageSize={PAGE_SIZE}
        total={PAGE_SIZE + 1}
        onChange={vi.fn()}
      />
    );
    expect(screen.getByRole('button', { name: /siguiente/i })).toBeEnabled();
  });

  it('sin total: conserva la heuristica totalEnPagina === pageSize (pestana de tickets)', () => {
    render(
      <Paginacion pagina={0} totalEnPagina={5} pageSize={PAGE_SIZE} onChange={vi.fn()} />
    );
    // Sin anterior ni siguiente, el control no se renderiza.
    expect(screen.queryByRole('button', { name: /siguiente/i })).not.toBeInTheDocument();
  });

  it('sin total: habilita siguiente cuando la pagina esta llena (heuristica previa)', () => {
    render(
      <Paginacion
        pagina={0}
        totalEnPagina={PAGE_SIZE}
        pageSize={PAGE_SIZE}
        onChange={vi.fn()}
      />
    );
    expect(screen.getByRole('button', { name: /siguiente/i })).toBeEnabled();
  });
});

describe('AdministracionPage - paginacion de la cola de revision', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
  });

  it('consulta la cola con limit=PAGE_SIZE y offset=pagina*PAGE_SIZE; Siguiente avanza el offset', async () => {
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(25);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue(
      Array.from({ length: PAGE_SIZE }, (_, i) => makePendiente(i + 1))
    );

    renderPage();

    await waitFor(() =>
      expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalledWith({
        limit: PAGE_SIZE,
        offset: 0,
      })
    );

    // La paginacion de la cola vive en la pestana "Revision Humana".
    await user.click(screen.getByRole('button', { name: /revisión humana/i }));
    await user.click(await screen.findByRole('button', { name: /siguiente/i }));

    await waitFor(() =>
      expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalledWith({
        limit: PAGE_SIZE,
        offset: PAGE_SIZE,
      })
    );
  });

  it('si la pagina queda fuera de rango tras el refetch, retrocede a la ultima pagina con resultados', async () => {
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(25);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockImplementation(
      async (params) => {
        const offset = params?.offset ?? 0;
        const size = offset === 0 ? PAGE_SIZE : 5;
        return Array.from({ length: size }, (_, i) => makePendiente(offset + i + 1));
      }
    );

    const { queryClient } = renderPage();

    await waitFor(() =>
      expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalledWith({
        limit: PAGE_SIZE,
        offset: 0,
      })
    );

    await user.click(screen.getByRole('button', { name: /revisión humana/i }));
    await user.click(await screen.findByRole('button', { name: /siguiente/i }));
    await waitFor(() =>
      expect(clasificacionesService.listarRevisionPendiente).toHaveBeenCalledWith({
        limit: PAGE_SIZE,
        offset: PAGE_SIZE,
      })
    );

    // Se valida la ultima fila de la ultima pagina: el total baja a 20 y la
    // pagina 1 (offset 20) queda fuera de rango.
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(20);
    await queryClient.invalidateQueries({ queryKey: [REVISION_PENDIENTE_QUERY_KEY] });

    await waitFor(() => {
      const calls = vi.mocked(clasificacionesService.listarRevisionPendiente).mock.calls;
      const last = calls[calls.length - 1]?.[0];
      expect(last).toEqual({ limit: PAGE_SIZE, offset: 0 });
    });
  });
});
