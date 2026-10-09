/**
 * Pruebas de la pagina de enrollment MFA (c-63b, IAH-006/007).
 *
 * El contexto de autenticacion esta mockeado: la pagina muestra el secreto, el
 * URI otpauth y los codigos de recuperacion devueltos por el enrollment.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import MfaEnrollmentPage from './index';
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
      <MfaEnrollmentPage />
    </MemoryRouter>,
  );
}

describe('MfaEnrollmentPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('muestra el secreto, el URI y los codigos de recuperacion', async () => {
    useAuthMock.mockReturnValue({
      token: 'a',
      username: 'admin',
      isAuthenticated: true,
      mfaRequired: false,
      login: vi.fn(),
      verifyMfa: vi.fn(),
      enrollMfa: vi.fn().mockResolvedValue({
        otpauthUri: 'otpauth://totp/App?secret=SECRET123',
        secret: 'SECRET123',
        recoveryCodes: ['AAAAA-11111', 'BBBBB-22222'],
      }),
      logout: vi.fn(),
    });

    renderPage();

    const secret = await screen.findByTestId('mfa-secret');
    expect(secret).toHaveTextContent('SECRET123');

    const codes = screen.getByTestId('mfa-recovery-codes');
    await waitFor(() => {
      expect(codes.querySelectorAll('li')).toHaveLength(2);
    });
  });

  it('muestra un error si el enrollment falla', async () => {
    useAuthMock.mockReturnValue({
      token: 'a',
      username: 'admin',
      isAuthenticated: true,
      mfaRequired: false,
      login: vi.fn(),
      verifyMfa: vi.fn(),
      enrollMfa: vi.fn().mockRejectedValue(new Error('fail')),
      logout: vi.fn(),
    });

    renderPage();

    expect(await screen.findByText(/No se pudo iniciar el enrollment/)).toBeInTheDocument();
  });
});
