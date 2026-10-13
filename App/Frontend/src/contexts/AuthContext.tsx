/**
 * Contexto de autenticacion para el frontend React.
 *
 * Responsabilidad:
 *   Provee el estado de autenticacion global a toda la aplicacion:
 *     - Token JWT almacenado en memoria (no en localStorage por seguridad).
 *     - Funciones login(), verifyMfa(), enrollMfa() y logout().
 *     - Booleano isAuthenticated para control de acceso a rutas.
 *     - mfaRequired: true cuando el backend exige el segundo factor.
 *
 *   Tambien sincroniza el token con el modulo de interceptor de Axios
 *   para que todas las requests incluyan el header Authorization.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { setAuthToken, clearAuthToken, setRefreshToken, clearRefreshToken, getRefreshToken } from '@/services/api';
import { obtenerIdentidad } from '@/services/authService';
import { ALCANCE_VACIO, type Alcance } from '@/types/auth';

// ── Tipos ────────────────────────────────────────────────────────────────────

interface AuthState {
  /** Token JWT actual (null si no autenticado). */
  token: string | null;
  /** Nombre de usuario autenticado (null si no autenticado). */
  username: string | null;
  /** true si hay un usuario autenticado con token valido. */
  isAuthenticated: boolean;
  /** true si el backend respondio que se requiere el segundo factor. */
  mfaRequired: boolean;
  /** Rol del empleado vinculado (null si no hay empleado / no resuelto). */
  rol: string | null;
  /** Alcance de incidentes derivado (PROPIO | GLOBAL | VACIO). */
  alcance: Alcance;
}

/** Respuesta del endpoint de login (aditiva: un paso o reto MFA). */
interface LoginApiResponse {
  access_token?: string | null;
  token_type?: string;
  refresh_token?: string | null;
  expires_in?: number | null;
  mfa_required?: boolean;
  mfa_ticket?: string | null;
}

/** Datos del enrollment de MFA mostrados una sola vez. */
export interface MfaEnrollmentData {
  otpauthUri: string;
  secret: string;
  recoveryCodes: string[];
}

interface AuthContextValue extends AuthState {
  /** Inicia sesion. Retorna true si completo; false si requiere MFA o fallo. */
  login: (username: string, password: string) => Promise<boolean>;
  /** Completa el login con el codigo de segundo factor. */
  verifyMfa: (code: string) => Promise<boolean>;
  /** Inicia el enrollment de MFA para la sesion autenticada. */
  enrollMfa: () => Promise<MfaEnrollmentData>;
  /** Re-resuelve el rol y el alcance desde el backend (sin re-login). */
  refreshIdentidad: () => Promise<void>;
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
    mfaRequired: false,
    rol: null,
    alcance: ALCANCE_VACIO,
  });

  // Ticket y usuario pendientes del segundo factor (no se renderizan).
  const mfaTicketRef = useRef<string | null>(null);
  const mfaUsernameRef = useRef<string | null>(null);

  /**
   * Resuelve la identidad (rol + alcance) desde el backend.
   *
   * Degrada de forma segura: si `/auth/me` falla, devuelve rol nulo y alcance
   * VACIO, de modo que no se habilita ninguna superficie operativa (el backend
   * sigue siendo el limite de seguridad).
   */
  const resolverIdentidad = useCallback(async (): Promise<{
    rol: string | null;
    alcance: Alcance;
  }> => {
    try {
      const identidad = await obtenerIdentidad();
      return { rol: identidad.rol, alcance: identidad.alcance };
    } catch {
      return { rol: null, alcance: ALCANCE_VACIO };
    }
  }, []);

  /** Fija el par de tokens en memoria, resuelve la identidad y autentica. */
  const applyTokenResponse = useCallback(
    async (username: string, data: LoginApiResponse) => {
      const token = data.access_token ?? '';
      setAuthToken(token);
      setRefreshToken(data.refresh_token ?? null);
      mfaTicketRef.current = null;
      mfaUsernameRef.current = null;
      const { rol, alcance } = await resolverIdentidad();
      setState({
        token,
        username,
        isAuthenticated: true,
        mfaRequired: false,
        rol,
        alcance,
      });
    },
    [resolverIdentidad],
  );

  const login = useCallback(
    async (username: string, password: string): Promise<boolean> => {
      try {
        const { apiClient } = await import('@/services/api');
        const response = await apiClient.post<LoginApiResponse>('/auth/login', {
          username,
          password,
        });

        const data = response.data;
        if (data.mfa_required && data.mfa_ticket) {
          // Reto de segundo factor: NO se fija token todavia.
          mfaTicketRef.current = data.mfa_ticket;
          mfaUsernameRef.current = username;
          setState({
            token: null,
            username,
            isAuthenticated: false,
            mfaRequired: true,
            rol: null,
            alcance: ALCANCE_VACIO,
          });
          return false;
        }

        await applyTokenResponse(username, data);
        return true;
      } catch {
        return false;
      }
    },
    [applyTokenResponse],
  );

  const verifyMfa = useCallback(
    async (code: string): Promise<boolean> => {
      const ticket = mfaTicketRef.current;
      const username = mfaUsernameRef.current;
      if (!ticket || !username) {
        return false;
      }
      try {
        const { apiClient } = await import('@/services/api');
        const response = await apiClient.post<LoginApiResponse>(
          '/auth/mfa/verify',
          { mfa_ticket: ticket, code },
        );
        await applyTokenResponse(username, response.data);
        return true;
      } catch {
        return false;
      }
    },
    [applyTokenResponse],
  );

  const enrollMfa = useCallback(async (): Promise<MfaEnrollmentData> => {
    const { apiClient } = await import('@/services/api');
    const response = await apiClient.post<{
      otpauth_uri: string;
      secret: string;
      recovery_codes: string[];
    }>('/auth/mfa/enroll');
    return {
      otpauthUri: response.data.otpauth_uri,
      secret: response.data.secret,  // gitleaks:allow (referencia, no un valor real)
      recoveryCodes: response.data.recovery_codes,
    };
  }, []);

  /**
   * Re-resuelve rol y alcance desde el backend SIN re-login (c-81, FR-RBAC-001).
   *
   * Se usa para reflejar cambios del directorio (rol nuevo, empleado
   * desactivado) en la siguiente resolucion de identidad. Si la sesion no esta
   * autenticada, no hace nada.
   */
  const refreshIdentidad = useCallback(async (): Promise<void> => {
    const { rol, alcance } = await resolverIdentidad();
    setState((prev) =>
      prev.isAuthenticated ? { ...prev, rol, alcance } : prev,
    );
  }, [resolverIdentidad]);

  const logout = useCallback(() => {
    // Logout revocatorio (c-63a): revocar el refresh en el backend antes de
    // limpiar el estado local. Fire-and-forget para no bloquear la UI; el access
    // ya emitido conserva validez hasta su TTL (ventana residual declarada).
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      void import('@/services/api').then(({ apiClient }) =>
        apiClient
          .post('/auth/logout', { refresh_token: refreshToken })
          .catch(() => undefined),
      );
    }
    clearAuthToken();
    clearRefreshToken();
    mfaTicketRef.current = null;
    mfaUsernameRef.current = null;
    setState({
      token: null,
      username: null,
      isAuthenticated: false,
      mfaRequired: false,
      rol: null,
      alcance: ALCANCE_VACIO,
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      verifyMfa,
      enrollMfa,
      refreshIdentidad,
      logout,
    }),
    [state, login, verifyMfa, enrollMfa, refreshIdentidad, logout],
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
