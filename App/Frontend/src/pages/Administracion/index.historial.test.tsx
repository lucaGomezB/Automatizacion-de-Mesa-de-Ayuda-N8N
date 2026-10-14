/**
 * Pruebas de integracion de la pestana "Historial de Incidentes Cerrados" del
 * panel de administracion (c-86, FIH-001) y del gating de la cola de revision
 * por alcance (FR-RBAC-002).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import AdministracionPage from './index';
import * as incidentesService from '@/services/incidentesService';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as catalogosService from '@/services/catalogosService';
import { useAuth } from '@/contexts/AuthContext';
import type { IncidenteListItem } from '@/types/incidente';

vi.mock('@/services/incidentesService', () => ({
  listarIncidentes: vi.fn(),
  listarHistorialCerrados: vi.fn(),
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
vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

function auth(modo: 'GLOBAL' | 'SECTOR', rol: string) {
  return {
    token: 't',
    username: 'u',
    isAuthenticated: true,
    mfaRequired: false,
    rol,
    alcance: { modo },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  };
}

const itemCerrado: IncidenteListItem = {
  id: 7,
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  estado: { id: 5, nombre: 'cerrado', descripcion: null, es_terminal: true },
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AdministracionPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('AdministracionPage - historial de cerrados (FIH-001)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthMock.mockReturnValue(auth('GLOBAL', 'mesa_de_ayuda'));
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(incidentesService.listarHistorialCerrados).mockResolvedValue([itemCerrado]);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
  });

  it('al abrir la pestana consulta el endpoint de historial y muestra "Cerrado"', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(
      screen.getByRole('button', { name: /historial de incidentes cerrados/i })
    );

    await waitFor(() =>
      expect(incidentesService.listarHistorialCerrados).toHaveBeenCalled()
    );
    expect(await screen.findByText('#00007')).toBeInTheDocument();
    expect(screen.getByText('Cerrado')).toBeInTheDocument();
  });

  it('no consulta el historial mientras la pestana esta inactiva', async () => {
    renderPage();

    // La pestana por defecto es "tickets"; el historial no se dispara.
    await waitFor(() => expect(incidentesService.listarIncidentes).toHaveBeenCalled());
    expect(incidentesService.listarHistorialCerrados).not.toHaveBeenCalled();
  });
});

describe('AdministracionPage - gating de revision por alcance (FR-RBAC-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(incidentesService.listarHistorialCerrados).mockResolvedValue([]);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
  });

  it('un usuario SECTOR no ve la cola de revision pero si el historial', async () => {
    useAuthMock.mockReturnValue(auth('SECTOR', 'gestion_incidentes'));
    renderPage();

    await waitFor(() => expect(incidentesService.listarIncidentes).toHaveBeenCalled());

    expect(screen.queryByRole('button', { name: /revisión humana/i })).not.toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /historial de incidentes cerrados/i })
    ).toBeInTheDocument();
    // No se dispara la consulta de la cola ajena al alcance.
    expect(clasificacionesService.contarRevisionPendiente).not.toHaveBeenCalled();
  });

  it('un usuario GLOBAL ve la cola de revision', async () => {
    useAuthMock.mockReturnValue(auth('GLOBAL', 'mesa_de_ayuda'));
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /revisión humana/i })).toBeInTheDocument()
    );
  });
});