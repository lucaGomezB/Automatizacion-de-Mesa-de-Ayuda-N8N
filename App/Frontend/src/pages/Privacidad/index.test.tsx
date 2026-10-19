/**
 * Pruebas de la superficie de privacidad en runtime (c-66, PRIV-001 / PRIV-002).
 *
 * Estrategia:
 *   - El enlace del formulario de reporte y el de la pagina de login se prueban
 *     sobre los componentes reales.
 *   - La accesibilidad publica se prueba renderizando la tabla de rutas real
 *     (`AppRoutes`, exportada por `main.tsx`) dentro de un `MemoryRouter`, con el
 *     contexto de autenticacion SIN sesion: si la superficie quedara detras de
 *     `ProtectedRoute`, el guard redirigiria a `/login` y el contenido no
 *     renderizaria.
 *   - El contexto de auth y el health check estan mockeados: no hay red.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { AppRoutes } from '../../main';
import Privacidad from './index';
import { IncidenteForm } from '../ReportarIncidente/IncidenteForm';
import LoginPage from '../LoginPage';
import * as useReportarIncidenteHook from '@/hooks/useReportarIncidente';
import * as catalogosService from '@/services/catalogosService';
import { createTestQueryClient } from '@/test/utils';

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    token: null,
    username: null,
    isAuthenticated: false,
    mfaRequired: false,
    rol: null,
    alcance: { modo: 'VACIO' },
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

vi.mock('@/hooks/useReportarIncidente');
vi.mock('@/services/catalogosService', () => ({ listarSectores: vi.fn() }));

function makeMockMutation() {
  return {
    mutate: vi.fn(),
    isPending: false,
    error: null,
    data: undefined,
    isSuccess: false,
    isError: false,
    isIdle: true,
    isPaused: false,
    reset: vi.fn(),
    mutateAsync: vi.fn(),
    context: undefined,
    variables: undefined,
    failureCount: 0,
    failureReason: null,
    status: 'idle' as const,
    submittedAt: 0,
  } as unknown as ReturnType<typeof useReportarIncidenteHook.useReportarIncidente>;
}

function renderIncidenteForm() {
  const client = createTestQueryClient();
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <MemoryRouter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
  return render(<IncidenteForm onSuccess={vi.fn()} />, { wrapper: Wrapper });
}

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

function renderRuta(entrada: string) {
  return render(
    <MemoryRouter initialEntries={[entrada]}>
      <AppRoutes />
    </MemoryRouter>,
  );
}

describe('Privacidad (c-66, PRIV-001)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([]);
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation()
    );
  });

  it('el formulario de reporte enlaza la politica de privacidad', async () => {
    const user = userEvent.setup({ delay: null });
    renderIncidenteForm();

    const enlace = await screen.findByRole('link', { name: /pol[ií]tica de privacidad/i });
    expect(enlace).toHaveAttribute('href', '/privacidad');

    // El enlace es visible y operable por teclado (no oculto).
    enlace.focus();
    await user.keyboard('{Enter}');
  });

  it('la pagina de login enlaza la politica de privacidad', () => {
    renderLogin();

    const enlace = screen.getByRole('link', { name: /pol[ií]tica de privacidad/i });
    expect(enlace).toHaveAttribute('href', '/privacidad');
  });

  it('la ruta publica /privacidad se renderiza sin sesion', () => {
    renderRuta('/privacidad');

    expect(
      screen.getByRole('heading', { name: /pol[ií]tica de privacidad/i })
    ).toBeInTheDocument();
    // Si quedara detras de ProtectedRoute, el guard redirigiria a /login.
    expect(screen.queryByLabelText('Usuario')).not.toBeInTheDocument();
  });

  it('la superficie renderiza finalidad, responsable, destinatarios y transferencia', () => {
    render(
      <MemoryRouter>
        <Privacidad />
      </MemoryRouter>,
    );

    expect(screen.getByText(/finalidad del tratamiento/i)).toBeInTheDocument();
    expect(screen.getByText(/responsable del tratamiento/i)).toBeInTheDocument();
    expect(screen.getByText(/destinatarios/i)).toBeInTheDocument();
    expect(screen.getByText(/transferencia internacional/i)).toBeInTheDocument();
    expect(screen.getByText(/Gemini/)).toBeInTheDocument();
    expect(screen.getByText(/Twilio/)).toBeInTheDocument();
  });

  it('declara los plazos correctos de los derechos (acceso 10 dias corridos; resto 5 dias habiles)', () => {
    render(
      <MemoryRouter>
        <Privacidad />
      </MemoryRouter>,
    );

    expect(screen.getByText(/10 d[ií]as corridos/i)).toBeInTheDocument();
    expect(screen.getByText(/5 d[ií]as h[aá]biles/i)).toBeInTheDocument();
    expect(screen.getByText(/acceso/i)).toBeInTheDocument();
    expect(screen.getByText(/rectificaci[oó]n, actualizaci[oó]n y supresi[oó]n/i)).toBeInTheDocument();
  });

  it('no contiene los terminos prohibidos y usa lenguaje de alineacion', () => {
    const { container } = render(
      <MemoryRouter>
        <Privacidad />
      </MemoryRouter>,
    );

    const texto = container.textContent ?? '';
    expect(texto).not.toMatch(/\b(certificado|compliant|cumple)\b/i);
    expect(texto).toMatch(/alineado con/i);
  });

  it('es alcanzable sin autenticarse y sin completar un reporte (no queda detras de ProtectedRoute)', () => {
    renderRuta('/privacidad');

    // La superficie renderiza aun sin sesion y sin pasar por el portal de reporte.
    expect(
      screen.getByRole('heading', { name: /pol[ií]tica de privacidad/i })
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /enviar incidente/i })).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Usuario')).not.toBeInTheDocument();
  });

  it('no recolecta datos personales adicionales (sin campos de entrada)', () => {
    const { container } = render(
      <MemoryRouter>
        <Privacidad />
      </MemoryRouter>,
    );

    expect(container.querySelectorAll('input, textarea, select, form')).toHaveLength(0);
  });
});
