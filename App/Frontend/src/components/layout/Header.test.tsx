/**
 * Pruebas de la navegacion del Header por alcance (c-81, FR-RBAC-003).
 *
 * Los enlaces se deciden por `alcance.modo`, NO por pathname:
 *   - "Portal" siempre para autenticados.
 *   - enlace operativo ("Administración") solo en GLOBAL.
 *   - enlace "Mis incidentes" solo en PROPIO.
 *   - en VACIO ninguno de los dos enlaces operativos.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from './Header';
import { useAuth } from '@/contexts/AuthContext';

vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

const useAuthMock = vi.mocked(useAuth);

function renderHeader(modo: 'PROPIO' | 'GLOBAL' | 'VACIO') {
  useAuthMock.mockReturnValue({
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
  });
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
