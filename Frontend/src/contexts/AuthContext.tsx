/**
 * Contexto de autenticacion para el frontend React.
 *
 * Responsabilidad:
 *   Provee el estado de autenticacion global a toda la aplicacion:
 *     - Token JWT almacenado en memoria (no en localStorage por seguridad).
 *     - Funciones login() y logout() para gestionar la sesion.
 *     - Booleano isAuthenticated para control de acceso a rutas.
 *
 *   Tambien sincroniza el token con el modulo de interceptor de Axios
 *   para que todas las requests incluyan el header Authorization.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { setAuthToken, clearAuthToken } from '@/services/api';

// ── Tipos ────────────────────────────────────────────────────────────────────

interface AuthState {
  /** Token JWT actual (null si no autenticado). */
  token: string | null;
  /** Nombre de usuario autenticado (null si no autenticado). */
  username: string | null;
  /** true si hay un usuario autenticado con token valido. */
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  /** Inicia sesion con username y password. Retorna true si fue exitoso. */
  login: (username: string, password: string) => Promise<boolean>;
  /** Cierra la sesion, eliminando el token de memoria. */
  logout: () => void;
}

// ── Contexto ─────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

/** Nombre para mostrar en errores si se usa fuera del provider. */
const DISPLAY_NAME = 'AuthContext';

// ── Provider ─────────────────────────────────────────────────────────────────

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    token: null,
    username: null,
    isAuthenticated: false,
  });

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    try {
      const { apiClient } = await import('@/services/api');
      const response = await apiClient.post<{
        access_token: string;
        token_type: string;
      }>('/auth/login', {
        username,
        password,
      });

      const token = response.data.access_token;
      setAuthToken(token);
      setState({
        token,
        username,
        isAuthenticated: true,
      });
      return true;
    } catch {
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    clearAuthToken();
    setState({
      token: null,
      username: null,
      isAuthenticated: false,
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      logout,
    }),
    [state, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Hook ─────────────────────────────────────────────────────────────────────

/**
 * Hook para acceder al contexto de autenticacion.
 *
 * Lanza un error si se usa fuera de <AuthProvider>.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error(
      `${DISPLAY_NAME}: useAuth debe usarse dentro de <AuthProvider>`,
    );
  }
  return context;
}

AuthContext.displayName = DISPLAY_NAME;
