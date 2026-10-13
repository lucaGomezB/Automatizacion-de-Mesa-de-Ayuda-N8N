/**
 * Pruebas del AuthContext para el flujo de login con segundo factor (c-63b).
 *
 * Verifican el login de un paso, el reto MFA (mfa_required), la verificacion
 * con codigo valido/invalido y el mapeo del enrollment. La capa de servicios
 * esta mockeada: no hay red.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { ReactNode } from 'react';

vi.mock('@/services/api', () => ({
  apiClient: { post: vi.fn(), get: vi.fn() },
  setAuthToken: vi.fn(),
  clearAuthToken: vi.fn(),
  setRefreshToken: vi.fn(),
  clearRefreshToken: vi.fn(),
  getRefreshToken: vi.fn(() => null),
  onUnauthorized: vi.fn(),
}));

import { apiClient } from '@/services/api';
import { AuthProvider, useAuth } from './AuthContext';

const postMock = apiClient.post as unknown as ReturnType<typeof vi.fn>;
const getMock = apiClient.get as unknown as ReturnType<typeof vi.fn>;

/** Respuesta por defecto de GET /auth/me para la sesion (identidad sin empleado). */
function identidadVacia() {
  return { data: { username: 'user', rol: null, alcance: { modo: 'VACIO' } } };
}

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

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
