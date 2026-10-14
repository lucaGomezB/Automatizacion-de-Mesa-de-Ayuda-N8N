/**
 * FRH-010: el aviso de criterio de la pestaña "Revisión Humana" debe describir el
 * umbral de revisión humana (70%) sin referenciar un modelo de lenguaje concreto.
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

const TEXTO_ESPERADO =
  'Estos incidentes fueron clasificados con una confianza inferior al 70%, ' +
  'umbral de revisión humana del clasificador. Revisá y confirmá el sector ' +
  'correcto para cada uno.';

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
}

describe('AdministracionPage - aviso de criterio (FRH-010)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);
  });

  it('no menciona ningun modelo de lenguaje y comunica el umbral vigente del 70%', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole('button', { name: /revisión humana/i }));

    const aviso = await screen.findByText(/umbral de revisión humana del clasificador/i);
    expect(aviso.textContent).toBe(TEXTO_ESPERADO);
    expect(aviso.textContent).not.toMatch(/gemini/i);
    expect(aviso.textContent).not.toMatch(/flash/i);
    expect(aviso.textContent).toMatch(/70%/);
  });
});
