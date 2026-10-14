/**
 * Pruebas de la navegacion del Header por alcance (c-81, FR-RBAC-003)
 * y del control de cierre de sesion (c-84, FSU-001).
 *
 * Los enlaces se deciden por `alcance.modo`, NO por pathname:
 *   - "Portal" siempre para autenticados.
 *   - enlace operativo ("Administración") solo en GLOBAL.
 *   - enlace "Mis incidentes" solo en PROPIO.
 *   - en VACIO ninguno de los dos enlaces operativos.
 *
 * El control "Cerrar sesión" (FSU-001) se muestra para TODO autenticado, con
 * independencia del alcance; al accionarlo invoca `logout()` y navega a /login.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { Header } from './Header';
import { useAuth } from '@/contexts/AuthContext';

vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

const useAuthMock = vi.mocked(useAuth);

function authState(modo: 'PROPIO' | 'GLOBAL' | 'VACIO') {
  return {
    token: 't',
    username: 'u',
    isAuthenticated: true,
    mfaRequired: false,
    rol: null,
    alcance: { modo },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  };
}

function renderHeader(modo: 'PROPIO' | 'GLOBAL' | 'VACIO') {
  useAuthMock.mockReturnValue(authState(modo));
  return render(
    <MemoryRouter>
      <Header />
    </MemoryRouter>
  );
}

describe('Header - navegacion por alcance', () => {
  beforeEach(() => {
    useAuthMock.mockReset();
  });

  it('GLOBAL muestra el enlace operativo y no el de Mis incidentes', () => {
    renderHeader('GLOBAL');
    expect(screen.getByRole('link', { name: /administraci/i })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /mis incidentes/i })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: /portal/i })).toBeInTheDocument();
  });

  it('PROPIO muestra Mis incidentes y no el enlace operativo', () => {
    renderHeader('PROPIO');
    expect(screen.getByRole('link', { name: /mis incidentes/i })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /administraci/i })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: /portal/i })).toBeInTheDocument();
  });

  it('VACIO no muestra ningun enlace operativo pero si el portal', () => {
    renderHeader('VACIO');
    expect(screen.queryByRole('link', { name: /administraci/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /mis incidentes/i })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: /portal/i })).toBeInTheDocument();
  });
});

describe('Header - cierre de sesion (FSU-001)', () => {
  beforeEach(() => {
    useAuthMock.mockReset();
  });

  it('renderiza el control Cerrar sesión con alcance PROPIO (no GLOBAL)', () => {
    renderHeader('PROPIO');
    expect(screen.getByRole('button', { name: /cerrar sesión/i })).toBeInTheDocument();
  });

  it.each(['GLOBAL', 'PROPIO'] as const)(
    'muestra el control Cerrar sesión con alcance %s',
    (modo) => {
      renderHeader(modo);
      expect(screen.getByRole('button', { name: /cerrar sesión/i })).toBeInTheDocument();
    }
  );

  it('con alcance PROPIO el control aparece aunque el indicador de salud este ausente', () => {
    renderHeader('PROPIO');
    expect(screen.queryByText(/API operativa/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Verificando API/i)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cerrar sesión/i })).toBeInTheDocument();
  });

  it('accionar el control invoca logout() y navega a /login', async () => {
    const user = userEvent.setup();
    const auth = authState('PROPIO');
    useAuthMock.mockReturnValue(auth);
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<Header />} />
          <Route path="/login" element={<div>Pantalla de login</div>} />
        </Routes>
      </MemoryRouter>
    );

    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }));

    expect(auth.logout).toHaveBeenCalledTimes(1);
    await waitFor(() => {
      expect(screen.getByText('Pantalla de login')).toBeInTheDocument();
    });
  });
});
