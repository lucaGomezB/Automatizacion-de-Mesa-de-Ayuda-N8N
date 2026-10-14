/**
 * Pruebas de la pagina de login con reto MFA (c-63b, IAH-007).
 *
 * El contexto de autenticacion y el health check estan mockeados: no hay red.
 * Verifican que la respuesta `mfa_required` muestra el paso de verificacion y
 * que un codigo valido completa el login.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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
    rol: null,
    alcance: { modo: 'VACIO' as const },
    login: vi.fn().mockResolvedValue(true),
    verifyMfa: vi.fn().mockResolvedValue(true),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn().mockResolvedValue(undefined),
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

describe('LoginPage (visibilidad de contraseña, FSU-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('la contraseña está oculta por defecto y existe el control de visibilidad', () => {
    useAuthMock.mockReturnValue(baseAuth());
    renderPage();

    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: 'Mostrar contraseña' })).toBeInTheDocument();
  });

  it('al accionar el control la contraseña pasa a texto y el aria-label cambia', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(baseAuth());
    renderPage();

    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }));

    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'text');
    expect(screen.getByRole('button', { name: 'Ocultar contraseña' })).toBeInTheDocument();
  });

  it('al accionar de nuevo la contraseña vuelve a ocultarse', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(baseAuth());
    renderPage();

    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }));
    await user.click(screen.getByRole('button', { name: 'Ocultar contraseña' }));

    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: 'Mostrar contraseña' })).toBeInTheDocument();
  });

  it('el control es operable por teclado', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(baseAuth());
    renderPage();

    screen.getByRole('button', { name: 'Mostrar contraseña' }).focus();
    await user.keyboard('{Enter}');

    expect(screen.getByRole('button', { name: 'Ocultar contraseña' })).toBeInTheDocument();
  });

  it('el valor enviado a login() es la contraseña tipeada, sin transformaciones', async () => {
    const user = userEvent.setup();
    const auth = baseAuth();
    useAuthMock.mockReturnValue(auth);
    renderPage();

    await user.type(screen.getByLabelText('Usuario'), 'operador');
    await user.type(screen.getByLabelText('Contraseña'), 'Secreta123');
    await user.click(screen.getByRole('button', { name: 'Mostrar contraseña' }));
    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    await waitFor(() => {
      expect(auth.login).toHaveBeenCalledWith('operador', 'Secreta123');
    });
  });
});
