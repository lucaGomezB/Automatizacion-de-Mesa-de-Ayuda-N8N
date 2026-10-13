/**
 * Pruebas de la vista "Mis incidentes" (c-81, D5).
 *
 * La vista reutiliza el endpoint EXISTENTE `GET /api/v1/incidentes/` (via el
 * hook `useIncidentes`): el backend ya acota el alcance PROPIO. No introduce
 * superficie de API nueva ni reconstruye datos en el cliente.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import MisIncidentesPage from './index';
import * as incidentesService from '@/services/incidentesService';
import type { IncidenteListItem } from '@/types/incidente';

vi.mock('@/services/incidentesService', () => ({
  listarIncidentes: vi.fn(),
}));

// El Header (via PageWrapper) consume el contexto de auth y el health check.
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    token: 't',
    username: 'u',
    isAuthenticated: true,
    mfaRequired: false,
    rol: 'usuario_final',
    alcance: { modo: 'PROPIO' },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  }),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

const mockSector = { id: 1, nombre: 'Sistemas', descripcion: null };
const mockEstado = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };

function makeItem(id: number): IncidenteListItem {
  return {
    id,
    prioridad: 'media',
    requiere_revision_humana: false,
    created_at: '2026-06-11T10:00:00Z',
    sector: mockSector,
    estado: mockEstado,
  };
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisIncidentesPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('MisIncidentesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('lista exactamente los incidentes devueltos por el backend', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([
      makeItem(11),
      makeItem(22),
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('#00011')).toBeInTheDocument();
    });
    expect(screen.getByText('#00022')).toBeInTheDocument();
    // Reutiliza el endpoint existente, sin parametros de alcance en el cliente.
    expect(incidentesService.listarIncidentes).toHaveBeenCalledWith({});
  });

  it('muestra un estado vacio cuando no hay incidentes propios', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/no tenés incidentes/i)).toBeInTheDocument();
    });
  });

  it('muestra un error normalizado si la consulta falla', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockRejectedValue(
      new Error('boom')
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/error al cargar/i)).toBeInTheDocument();
    });
  });
});
