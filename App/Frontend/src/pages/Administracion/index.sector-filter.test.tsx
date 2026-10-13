/**
 * Pruebas del filtro de sector como CONVENIENCIA (c-81, FR-RBAC-004).
 *
 * El filtro de sector NO es una frontera de seguridad: la visibilidad la
 * determina exclusivamente el backend. Cambiar o limpiar el filtro NO altera el
 * conjunto de datos autorizado; el cliente nunca acota datos por su cuenta.
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
import type { IncidenteListItem } from '@/types/incidente';

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

const sectorSistemas = { id: 1, nombre: 'Sistemas', descripcion: null };
const sectorBd = { id: 4, nombre: 'Bases de Datos', descripcion: null };
const estadoNuevo = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };

/** Conjunto autorizado por el backend: dos incidentes de sectores distintos. */
const autorizados: IncidenteListItem[] = [
  { id: 1, prioridad: 'media', requiere_revision_humana: false, created_at: '2026-06-11T10:00:00Z', sector: sectorSistemas, estado: estadoNuevo },
  { id: 2, prioridad: 'alta', requiere_revision_humana: false, created_at: '2026-06-11T11:00:00Z', sector: sectorBd, estado: estadoNuevo },
];

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

describe('AdministracionPage - filtro de sector como conveniencia', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([sectorSistemas, sectorBd]);
    // El backend IGNORA el filtro de sector: devuelve siempre el conjunto autorizado.
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue(autorizados);
  });

  it('cambiar el filtro de sector no elimina datos autorizados por el backend', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());
    expect(screen.getByText('#00002')).toBeInTheDocument();

    // Elige el sector "Sistemas" (segundo combobox: Estado, Sector, Prioridad).
    await user.click(screen.getAllByRole('combobox')[1]);
    await user.click(await screen.findByRole('option', { name: 'Sistemas' }));

    // El filtro delega al backend (sector_id=1) y NO acota localmente la lista.
    await waitFor(() => {
      expect(incidentesService.listarIncidentes).toHaveBeenCalledWith(
        expect.objectContaining({ sector_id: 1 })
      );
    });
    expect(screen.getByText('#00001')).toBeInTheDocument();
    expect(screen.getByText('#00002')).toBeInTheDocument();
  });

  it('limpiar el filtro vuelve a consultar sin sector y conserva el conjunto autorizado', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());

    await user.click(screen.getAllByRole('combobox')[1]);
    await user.click(await screen.findByRole('option', { name: 'Bases de Datos' }));
    await waitFor(() =>
      expect(incidentesService.listarIncidentes).toHaveBeenCalledWith(
        expect.objectContaining({ sector_id: 4 })
      )
    );

    await user.click(screen.getByRole('button', { name: /limpiar filtros/i }));

    await waitFor(() => {
      const llamadas = vi.mocked(incidentesService.listarIncidentes).mock.calls;
      const ultima = llamadas[llamadas.length - 1]?.[0];
      if (!ultima) throw new Error('no se registro ninguna llamada a listarIncidentes');
      expect(ultima.sector_id).toBeUndefined();
    });
    expect(screen.getByText('#00001')).toBeInTheDocument();
    expect(screen.getByText('#00002')).toBeInTheDocument();
  });
});

// ── FR-RBAC-005: la UI no reemplaza el enforcement del backend ────────────────

describe('AdministracionPage - denegaciones del backend', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([sectorSistemas]);
  });

  it('ante un 404 la UI no muestra datos y presenta el error', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });

    renderPage();

    await waitFor(() =>
      expect(screen.getByText(/recurso solicitado no existe/i)).toBeInTheDocument()
    );
    // No se concede ningun dato por cuenta del cliente.
    expect(screen.queryByText(/^#\d{5}$/)).not.toBeInTheDocument();
  });

  it('ante un 403 la UI no muestra datos y presenta el error', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });

    renderPage();

    await waitFor(() =>
      expect(screen.getByText(/error al cargar/i)).toBeInTheDocument()
    );
    expect(screen.queryByText(/^#\d{5}$/)).not.toBeInTheDocument();
  });
});
