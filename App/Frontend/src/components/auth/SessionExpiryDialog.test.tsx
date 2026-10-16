/**
 * Pruebas del dialogo de expiracion de sesion (c-91, FSL-002/FSL-004).
 *
 * Verifican que el aviso sea accesible (rol de dialogo + titulo) y que ofrezca
 * explicitamente las dos decisiones: continuar la sesion o cerrarla. La logica
 * de temporizador y cierre vive en AuthContext; aqui solo se prueba la UI.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SessionExpiryDialog } from './SessionExpiryDialog';
import { useAuth, useSessionLifecycle } from '@/contexts/AuthContext';

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  useSessionLifecycle: vi.fn(),
}));

const useAuthMock = vi.mocked(useAuth);
const useSessionLifecycleMock = vi.mocked(useSessionLifecycle);

function setup(options: { visible: boolean; continueSession?: () => Promise<void>; logout?: () => void }) {
  const continueSession = options.continueSession ?? vi.fn().mockResolvedValue(undefined);
  const logout = options.logout ?? vi.fn();
  useAuthMock.mockReturnValue({
    token: 't',
    username: 'u',
    isAuthenticated: true,
    mfaRequired: false,
    rol: null,
    alcance: { modo: 'GLOBAL' },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout,
  });
  useSessionLifecycleMock.mockReturnValue({
    isHydrating: false,
    expirationPromptVisible: options.visible,
    continueSession,
  });
  return { continueSession, logout };
}

describe('SessionExpiryDialog (c-91 FSL-002)', () => {
  beforeEach(() => {
    useAuthMock.mockReset();
    useSessionLifecycleMock.mockReset();
  });

  it('con el aviso visible muestra un dialogo accesible con las dos opciones', () => {
    setup({ visible: true });
    render(<SessionExpiryDialog />);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText(/sesión está por expirar/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continuar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cerrar sesión/i })).toBeInTheDocument();
  });

  it('sin aviso pendiente no renderiza el dialogo', () => {
    setup({ visible: false });
    render(<SessionExpiryDialog />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('"Continuar" extiende la sesion (FSL-004)', async () => {
    const { continueSession } = setup({ visible: true });
    const user = userEvent.setup({ delay: null });
    render(<SessionExpiryDialog />);

    await user.click(screen.getByRole('button', { name: /continuar/i }));
    expect(continueSession).toHaveBeenCalledTimes(1);
  });

  it('"Cerrar sesión" cierra la sesion (FSL-002)', async () => {
    const { logout } = setup({ visible: true });
    const user = userEvent.setup({ delay: null });
    render(<SessionExpiryDialog />);

    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }));
    expect(logout).toHaveBeenCalledTimes(1);
  });
});
