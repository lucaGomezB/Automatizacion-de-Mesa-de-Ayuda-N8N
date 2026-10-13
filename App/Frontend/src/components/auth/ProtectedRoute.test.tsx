/**
 * Pruebas del guard de rutas por alcance (c-81, FR-RBAC-002).
 *
 * Dos niveles:
 *   1. `resolverRedireccion` — funcion PURA que decide el destino del guard sin
 *      mocks. Es la logica de decision extraida (extract-before-mock).
 *   2. `ProtectedRoute` — comportamiento de redireccion observable por el usuario
 *      (se mockea solo el contexto de autenticacion).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { resolverRedireccion, ProtectedRoute } from './ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

describe('resolverRedireccion (funcion pura)', () => {
  it('anonimo siempre va a /login', () => {
    expect(
      resolverRedireccion({ isAuthenticated: false, modo: 'VACIO' })
    ).toBe('/login');
    expect(
      resolverRedireccion({ isAuthenticated: false, modo: 'GLOBAL', requiere: 'GLOBAL' })
    ).toBe('/login');
  });

  it('GLOBAL accede a la superficie operativa (sin redireccion)', () => {
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'GLOBAL', requiere: 'GLOBAL' })
    ).toBeNull();
  });

  it('PROPIO accede a Mis incidentes (sin redireccion)', () => {
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'PROPIO', requiere: 'PROPIO' })
    ).toBeNull();
  });

  it('PROPIO no accede a la superficie operativa: redirige al portal', () => {
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'PROPIO', requiere: 'GLOBAL' })
    ).toBe('/');
  });

  it('VACIO no accede a ninguna superficie: redirige al portal', () => {
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'VACIO', requiere: 'GLOBAL' })
    ).toBe('/');
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'VACIO', requiere: 'PROPIO' })
    ).toBe('/');
  });

  it('GLOBAL no accede a Mis incidentes (exige PROPIO): redirige al portal', () => {
    expect(
      resolverRedireccion({ isAuthenticated: true, modo: 'GLOBAL', requiere: 'PROPIO' })
    ).toBe('/');
  });
});

function renderGuard(modo: 'PROPIO' | 'GLOBAL' | 'VACIO', autenticado = true) {
  useAuthMock.mockReturnValue({
    token: 't',
    username: 'u',
    isAuthenticated: autenticado,
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
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route
          path="/admin"
          element={
            <ProtectedRoute requiere="GLOBAL">
              <div>SUPERFICIE_OPS</div>
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<div>PORTAL</div>} />
        <Route path="/login" element={<div>LOGIN</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('ProtectedRoute (comportamiento observable)', () => {
  beforeEach(() => {
    useAuthMock.mockReset();
  });

  it('GLOBAL ve la superficie operativa', () => {
    renderGuard('GLOBAL');
    expect(screen.getByText('SUPERFICIE_OPS')).toBeInTheDocument();
  });

  it('PROPIO es redirigido al portal desde la superficie operativa', () => {
    renderGuard('PROPIO');
    expect(screen.queryByText('SUPERFICIE_OPS')).not.toBeInTheDocument();
    expect(screen.getByText('PORTAL')).toBeInTheDocument();
  });

  it('VACIO es redirigido al portal', () => {
    renderGuard('VACIO');
    expect(screen.getByText('PORTAL')).toBeInTheDocument();
  });

  it('anonimo es redirigido a /login', () => {
    renderGuard('VACIO', false);
    expect(screen.getByText('LOGIN')).toBeInTheDocument();
  });
});
