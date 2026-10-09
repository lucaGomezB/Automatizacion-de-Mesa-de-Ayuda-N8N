/**
 * Pruebas de la pagina de login con reto MFA (c-63b, IAH-007).
 *
 * El contexto de autenticacion y el health check estan mockeados: no hay red.
 * Verifican que la respuesta `mfa_required` muestra el paso de verificacion y
 * que un codigo valido completa el login.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './index';
import { useAuth } from '@/contexts/AuthContext';

vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

const useAuthMock = vi.mocked(useAuth);

function renderPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

function baseAuth() {
  return {
    token: null,
    username: null,
    isAuthenticated: false,
    mfaRequired: false,
    login: vi.fn().mockResolvedValue(true),
    verifyMfa: vi.fn().mockResolvedValue(true),
    enrollMfa: vi.fn(),
    logout: vi.fn(),
  };
}

describe('LoginPage (MFA)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('sin reto MFA muestra el formulario de credenciales', () => {
    useAuthMock.mockReturnValue(baseAuth());
    renderPage();

    expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument();
    expect(screen.getByLabelText('Usuario')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
    expect(screen.queryByLabelText('Código MFA')).not.toBeInTheDocument();
  });

  it('con mfaRequired muestra el paso de verificacion y completa el login', async () => {
    const auth = baseAuth();
    auth.mfaRequired = true;
    useAuthMock.mockReturnValue(auth);
    renderPage();

    expect(screen.getByText('Verificación en dos pasos')).toBeInTheDocument();
    const input = screen.getByLabelText('Código MFA');

    fireEvent.change(input, { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /verificar/i }));

    await waitFor(() => {
      expect(auth.verifyMfa).toHaveBeenCalledWith('123456');
    });
  });
});
