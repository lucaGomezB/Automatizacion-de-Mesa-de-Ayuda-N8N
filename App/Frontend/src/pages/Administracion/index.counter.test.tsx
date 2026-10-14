/**
 * FE 4 / FRH-008: el contador de la pestaña "Revisión Humana" debe reflejar el
 * TOTAL REAL de pendientes del alcance (endpoint de conteo), no el tamaño de la
 * página visible de la cola.
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
  contarRevisionPendiente: vi.fn(),
  validarClasificacion: vi.fn(),
}));
vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

// El Header (via PageWrapper) consume el contexto de auth (c-81).
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

describe('AdministracionPage - contador de revision humana', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);
  });

  it('muestra el total del conteo aunque exceda el tamano de pagina', async () => {
    // El conteo devuelve 137 (mucho mayor que PAGE_SIZE); la lista solo trae 20.
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(137);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue(
      Array.from({ length: 20 }, (_, i) => makePendiente(i + 1))
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('137')).toBeInTheDocument();
    });
    // El badge NO se deriva del tamano de la pagina (20).
    expect(screen.queryByText('20')).not.toBeInTheDocument();
  });

  it('oculta el badge cuando el total del conteo es cero', async () => {
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);

    renderPage();

    await waitFor(() => expect(incidentesService.listarIncidentes).toHaveBeenCalled());
    expect(screen.getByText('Revisión Humana')).toBeInTheDocument();
    // Sin pendientes no se muestra ningun badge (ni un "0").
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('muestra el total del alcance propio cuando es menor que una pagina', async () => {
    // Alcance PROPIO: el backend devuelve el total acotado (3), no la cola global.
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(3);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });
});
