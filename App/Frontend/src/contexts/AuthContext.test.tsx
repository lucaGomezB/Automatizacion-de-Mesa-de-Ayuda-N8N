/**
 * Pruebas del AuthContext para el flujo de login con segundo factor (c-63b).
 *
 * Verifican el login de un paso, el reto MFA (mfa_required), la verificacion
 * con codigo valido/invalido y el mapeo del enrollment. La capa de servicios
 * esta mockeada: no hay red.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { ReactNode } from 'react';

vi.mock('@/services/api', () => ({
  apiClient: { post: vi.fn(), get: vi.fn() },
  setAuthToken: vi.fn(),
  clearAuthToken: vi.fn(),
  refreshSession: vi.fn(),
  setSilentRefreshEnabled: vi.fn(),
  onUnauthorized: vi.fn(),
}));

vi.mock('@/services/sessionChannel', () => {
  const handlers = new Set<(event: unknown) => void>();
  return {
    broadcastSessionEvent: vi.fn(),
    subscribeToSessionEvents: vi.fn((handler: (event: unknown) => void) => {
      handlers.add(handler);
      return () => {
        handlers.delete(handler);
      };
    }),
    __handlers: handlers,
  };
});

import { apiClient, refreshSession, setSilentRefreshEnabled } from '@/services/api';
import * as sessionChannel from '@/services/sessionChannel';
import { AuthProvider, useAuth, useSessionLifecycle, SESSION_PROMPT_GRACE_MS } from './AuthContext';

const postMock = apiClient.post as unknown as ReturnType<typeof vi.fn>;
const getMock = apiClient.get as unknown as ReturnType<typeof vi.fn>;
const refreshSessionMock = refreshSession as unknown as ReturnType<typeof vi.fn>;
const setSilentRefreshEnabledMock =
  setSilentRefreshEnabled as unknown as ReturnType<typeof vi.fn>;
const channelMock = sessionChannel as unknown as {
  __handlers: Set<(event: { type: 'logout' } | { type: 'refreshed' }) => void>;
  broadcastSessionEvent: ReturnType<typeof vi.fn>;
};
const broadcastMock = channelMock.broadcastSessionEvent;

/** Dispara un evento entrante desde "otra pestana" a los manejadores suscritos. */
function emitSessionEvent(event: { type: 'logout' } | { type: 'refreshed' }) {
  for (const handler of channelMock.__handlers) handler(event);
}

/** Respuesta por defecto de GET /auth/me para la sesion (identidad sin empleado). */
function identidadVacia() {
  return { data: { username: 'user', rol: null, alcance: { modo: 'VACIO' } } };
}

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

/** Wrapper con ventana de gracia explicita (para probar la configurabilidad). */
function wrapperConGracia(gracePeriodMs: number) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <AuthProvider gracePeriodMs={gracePeriodMs}>{children}</AuthProvider>;
  };
}

/** Hook combinado: identidad + ciclo de vida de sesion. */
function useAuthYLifecycle() {
  return { auth: useAuth(), lifecycle: useSessionLifecycle() };
}

/** Deja correr la microcola (rehidratacion) con timers reales. */
function waitForMicrotasks() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

beforeEach(() => {
  postMock.mockReset();
  postMock.mockResolvedValue({ data: {} });
  getMock.mockReset();
  refreshSessionMock.mockReset();
  refreshSessionMock.mockResolvedValue(null);
  getMock.mockResolvedValue(identidadVacia());
  broadcastMock.mockReset();
  setSilentRefreshEnabledMock.mockReset();
  channelMock.__handlers.clear();
});

describe('AuthContext (MFA)', () => {
  beforeEach(() => {
    postMock.mockReset();
    getMock.mockReset();
    getMock.mockResolvedValue(identidadVacia());
  });

  it('login de un paso autentica la sesion', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer', refresh_token: 'r' },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      expect(await result.current.login('user', 'pass')).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.mfaRequired).toBe(false);
  });

  it('respuesta mfa_required activa el reto sin autenticar', async () => {
    postMock.mockResolvedValueOnce({
      data: { mfa_required: true, mfa_ticket: 'ticket-1' },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      expect(await result.current.login('user', 'pass')).toBe(false);
    });

    expect(result.current.mfaRequired).toBe(true);
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('verifyMfa con codigo valido completa el login', async () => {
    postMock.mockResolvedValueOnce({
      data: { mfa_required: true, mfa_ticket: 'ticket-1' },
    });
    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('user', 'pass');
    });

    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer' },
    });

    await act(async () => {
      expect(await result.current.verifyMfa('123456')).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.mfaRequired).toBe(false);
    expect(postMock).toHaveBeenLastCalledWith('/auth/mfa/verify', {
      mfa_ticket: 'ticket-1',
      code: '123456',
    });
  });

  it('verifyMfa con codigo invalido no autentica', async () => {
    postMock.mockResolvedValueOnce({
      data: { mfa_required: true, mfa_ticket: 'ticket-1' },
    });
    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('user', 'pass');
    });

    postMock.mockRejectedValueOnce(new Error('invalid'));

    await act(async () => {
      expect(await result.current.verifyMfa('000000')).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.mfaRequired).toBe(true);
  });

  it('enrollMfa mapea la respuesta a camelCase', async () => {
    postMock.mockResolvedValueOnce({
      data: {
        otpauth_uri: 'otpauth://totp/app?secret=ABC',
        secret: 'ABC',
        recovery_codes: ['AAAAA-11111', 'BBBBB-22222'],
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    let enrollment: Awaited<ReturnType<typeof result.current.enrollMfa>> | undefined;
    await act(async () => {
      enrollment = await result.current.enrollMfa();
    });

    expect(enrollment).toEqual({
      otpauthUri: 'otpauth://totp/app?secret=ABC',
      secret: 'ABC',
      recoveryCodes: ['AAAAA-11111', 'BBBBB-22222'],
    });
  });
});

// ── c-81 FR-RBAC-001: la sesion conoce rol y alcance (GET /auth/me) ────────────

describe('AuthContext (rol y alcance, c-81)', () => {
  beforeEach(() => {
    postMock.mockReset();
    getMock.mockReset();
  });

  it('tras login de un paso expone el rol y el modo de alcance del backend', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer', refresh_token: 'r' },
    });
    getMock.mockResolvedValueOnce({
      data: {
        username: 'user',
        rol: 'usuario_final',
        alcance: { modo: 'PROPIO' },
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      expect(await result.current.login('user', 'pass')).toBe(true);
    });

    expect(getMock).toHaveBeenCalledWith('/auth/me');
    expect(result.current.rol).toBe('usuario_final');
    expect(result.current.alcance.modo).toBe('PROPIO');
  });

  // c-86 FR-RBAC-001: la sesion expone el alcance SECTOR del backend (sin inferirlo).
  it('tras login expone el modo SECTOR y el rol gestion_incidentes del backend', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer', refresh_token: 'r' },
    });
    getMock.mockResolvedValueOnce({
      data: {
        username: 'gestion',
        rol: 'gestion_incidentes',
        alcance: { modo: 'SECTOR' },
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      expect(await result.current.login('gestion', 'pass')).toBe(true);
    });

    expect(result.current.rol).toBe('gestion_incidentes');
    expect(result.current.alcance.modo).toBe('SECTOR');
  });

  it('una cuenta sin empleado vinculado expone alcance VACIO', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer' },
    });
    getMock.mockResolvedValueOnce({
      data: { username: 'user', rol: null, alcance: { modo: 'VACIO' } },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('user', 'pass');
    });

    expect(result.current.rol).toBeNull();
    expect(result.current.alcance.modo).toBe('VACIO');
  });

  it('re-resuelve el alcance sin re-login cuando cambia el modo (triangulacion)', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer' },
    });
    getMock.mockResolvedValueOnce({
      data: { username: 'u', rol: 'mesa_de_ayuda', alcance: { modo: 'GLOBAL' } },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('u', 'pass');
    });
    expect(result.current.alcance.modo).toBe('GLOBAL');

    // El directorio cambia el rol; la identidad se re-resuelve sin re-login.
    getMock.mockResolvedValueOnce({
      data: { username: 'u', rol: 'usuario_final', alcance: { modo: 'PROPIO' } },
    });
    await act(async () => {
      await result.current.refreshIdentidad();
    });

    expect(result.current.rol).toBe('usuario_final');
    expect(result.current.alcance.modo).toBe('PROPIO');
  });

  it('degrada a VACIO si GET /auth/me falla (no habilita superficies)', async () => {
    postMock.mockResolvedValueOnce({
      data: { access_token: 'a', token_type: 'bearer' },
    });
    getMock.mockRejectedValueOnce(new Error('network'));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      expect(await result.current.login('u', 'pass')).toBe(true);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.rol).toBeNull();
    expect(result.current.alcance.modo).toBe('VACIO');
  });
});

// ── c-91 FSL-001: rehidratacion de la sesion al arranque por cookie ───────────

describe('AuthContext (rehidratacion, c-91 FSL-001)', () => {
  it('rehidrata la sesion al arrancar con cookie vigente', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'rehidratado', expiresIn: 1800 });
    getMock.mockResolvedValueOnce({
      data: { username: 'cookie-user', rol: 'usuario_final', alcance: { modo: 'PROPIO' } },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });
    await act(async () => {
      await waitForMicrotasks();
    });

    expect(refreshSessionMock).toHaveBeenCalledTimes(1);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.username).toBe('cookie-user');
    expect(result.current.rol).toBe('usuario_final');
    expect(result.current.alcance.modo).toBe('PROPIO');
  });

  it('expone isHydrating=true hasta resolver la rehidratacion', async () => {
    let resolver: (value: unknown) => void = () => undefined;
    refreshSessionMock.mockReturnValueOnce(
      new Promise((resolve) => {
        resolver = resolve;
      }),
    );

    const { result } = renderHook(() => useSessionLifecycle(), { wrapper });
    expect(result.current.isHydrating).toBe(true);

    await act(async () => {
      resolver(null);
      await waitForMicrotasks();
    });
    expect(result.current.isHydrating).toBe(false);
  });

  it('sin cookie deja no autenticado y no consulta /auth/me', async () => {
    refreshSessionMock.mockResolvedValueOnce(null);

    const { result } = renderHook(() => useAuth(), { wrapper });
    await act(async () => {
      await waitForMicrotasks();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(getMock).not.toHaveBeenCalled();
  });

  it('no persiste el refresh en almacenamiento accesible por JS', async () => {
    window.localStorage.clear();
    window.sessionStorage.clear();
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'tok', expiresIn: 100 });
    getMock.mockResolvedValueOnce(identidadVacia());

    const { result } = renderHook(() => useAuth(), { wrapper });
    await act(async () => {
      await waitForMicrotasks();
    });
    expect(result.current.isAuthenticated).toBe(true);

    const rastro = [
      ...Object.keys(window.localStorage),
      ...Object.keys(window.sessionStorage),
      document.cookie,
    ]
      .join('|')
      .toLowerCase();
    expect(rastro).not.toContain('refresh');
    expect(document.cookie).toBe('');
  });
});

// ── c-91 FSL-002..005: expiracion, cierre, multi-pestana y precedencia ───────

describe('AuthContext (expiracion y cierre, c-91 FSL-002..005)', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  /** Deja correr la microcola con timers falsos. */
  async function flush() {
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    });
  }

  it('al vencer expires_in abre el aviso proactivo (FSL-002)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 10 });
    getMock.mockResolvedValueOnce(identidadVacia());

    const { result } = renderHook(() => useSessionLifecycle(), { wrapper });
    await flush();
    expect(result.current.expirationPromptVisible).toBe(false);

    await act(async () => {
      vi.advanceTimersByTime(10_000);
    });
    expect(result.current.expirationPromptVisible).toBe(true);
  });

  it('continuar refresca, cierra el aviso y reinicia el temporizador (FSL-004)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 10 });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();
    await act(async () => {
      vi.advanceTimersByTime(10_000);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);

    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'nuevo', expiresIn: 20 });
    await act(async () => {
      await result.current.lifecycle.continueSession();
    });

    expect(result.current.lifecycle.expirationPromptVisible).toBe(false);
    expect(refreshSessionMock).toHaveBeenCalledTimes(2);
    expect(broadcastMock).toHaveBeenCalledWith({ type: 'refreshed' });

    await act(async () => {
      vi.advanceTimersByTime(20_000);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);
  });

  it('sin respuesta dentro de la ventana de gracia de 30 s cierra la sesion (FSL-003)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 5 });
    getMock.mockResolvedValue(identidadVacia());
    postMock.mockResolvedValue({ data: {} });

    const { result } = renderHook(() => useAuthYLifecycle(), {
      wrapper: wrapperConGracia(30_000),
    });
    await flush();
    await act(async () => {
      vi.advanceTimersByTime(5_000);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);

    await act(async () => {
      vi.advanceTimersByTime(30_000);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(result.current.lifecycle.expirationPromptVisible).toBe(false);
    expect(result.current.auth.isAuthenticated).toBe(false);
    expect(broadcastMock).toHaveBeenCalledWith({ type: 'logout' });
    expect(postMock).toHaveBeenCalledWith('/auth/logout');
  });

  it('la ventana de gracia es configurable (cierre exacto al vencer)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 5 });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), {
      wrapper: wrapperConGracia(1_000),
    });
    await flush();
    await act(async () => {
      vi.advanceTimersByTime(5_000);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);

    await act(async () => {
      vi.advanceTimersByTime(999);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);

    await act(async () => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(false);
    expect(result.current.auth.isAuthenticated).toBe(false);
  });

  it('si continuar falla (cookie invalida) cierra la sesion (FSL-004)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 5 });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();
    await act(async () => {
      vi.advanceTimersByTime(5_000);
    });
    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);

    refreshSessionMock.mockResolvedValueOnce(null);
    await act(async () => {
      await result.current.lifecycle.continueSession();
    });

    expect(result.current.auth.isAuthenticated).toBe(false);
    expect(result.current.lifecycle.expirationPromptVisible).toBe(false);
  });

  it('propaga el logout a las demas pestanas via BroadcastChannel (FSL-005)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'a', expiresIn: null });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();
    expect(result.current.auth.isAuthenticated).toBe(true);

    await act(async () => {
      emitSessionEvent({ type: 'logout' });
    });
    expect(result.current.auth.isAuthenticated).toBe(false);
  });

  it('una extension mantiene autenticadas a las demas pestanas (FSL-005)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'a', expiresIn: null });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();

    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'b', expiresIn: 60 });
    getMock.mockResolvedValueOnce(identidadVacia());
    await act(async () => {
      emitSessionEvent({ type: 'refreshed' });
    });
    await flush();

    expect(result.current.auth.isAuthenticated).toBe(true);
    expect(refreshSessionMock).toHaveBeenCalledTimes(2);
  });

  it('el logout manual difunde el evento a las demas pestanas (FSL-005)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'a', expiresIn: null });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();

    await act(async () => {
      result.current.auth.logout();
    });
    expect(broadcastMock).toHaveBeenCalledWith({ type: 'logout' });
  });

  it('deshabilita el respaldo 401 mientras el aviso esta visible (FSL-005)', async () => {
    refreshSessionMock.mockResolvedValueOnce({ accessToken: 'boot', expiresIn: 5 });
    getMock.mockResolvedValue(identidadVacia());

    const { result } = renderHook(() => useAuthYLifecycle(), { wrapper });
    await flush();
    await act(async () => {
      vi.advanceTimersByTime(5_000);
    });

    expect(result.current.lifecycle.expirationPromptVisible).toBe(true);
    expect(setSilentRefreshEnabledMock).toHaveBeenLastCalledWith(false);
  });

  it('la ventana de gracia por defecto es de 30 segundos (FSL-003)', () => {
    expect(SESSION_PROMPT_GRACE_MS).toBe(30_000);
  });
});
