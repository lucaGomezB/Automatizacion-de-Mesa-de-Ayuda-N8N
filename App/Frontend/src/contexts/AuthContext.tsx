/**
 * Contexto de autenticacion para el frontend React.
 *
 * Responsabilidad:
 *   Provee el estado de autenticacion global a toda la aplicacion:
 *     - Access token JWT almacenado SOLO en memoria (no en localStorage).
 *     - Funciones login(), verifyMfa(), enrollMfa() y logout().
 *     - Booleano isAuthenticated para control de acceso a rutas.
 *     - mfaRequired: true cuando el backend exige el segundo factor.
 *
 *   Tambien sincroniza el access token con el modulo de interceptor de Axios
 *   para que todas las requests incluyan el header Authorization.
 *
 * Ciclo de vida de la sesion (c-91, FSL-001..005):
 *   - Rehidratacion al arranque por cookie HttpOnly (`isHydrating`).
 *   - Aviso proactivo al expirar el access token, con ventana de gracia para
 *     cerrar la sesion si el usuario no responde.
 *   - Sincronizacion multi-pestana via `BroadcastChannel`.
 *   El refresh NUNCA se guarda en un medio accesible por JavaScript.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import {
  apiClient,
  setAuthToken,
  clearAuthToken,
  refreshSession,
  setSilentRefreshEnabled,
} from '@/services/api';
import {
  broadcastSessionEvent,
  subscribeToSessionEvents,
  type SessionEvent,
} from '@/services/sessionChannel';
import { obtenerIdentidad } from '@/services/authService';
import { ALCANCE_VACIO, type Alcance } from '@/types/auth';

// ── Configuracion del ciclo de vida ──────────────────────────────────────────

/** Ventana de gracia por defecto antes de cerrar la sesion (c-91 OQ-2). */
const DEFAULT_GRACE_SECONDS = 30;

/**
 * Ventana de gracia configurable del aviso de expiracion, en milisegundos.
 * Se toma de `VITE_SESSION_PROMPT_GRACE_SECONDS` (default 30 s) y puede
 * sobreescribirse por prop en `<AuthProvider gracePeriodMs={...}>`.
 */
export const SESSION_PROMPT_GRACE_MS = (() => {
  const raw = Number(import.meta.env['VITE_SESSION_PROMPT_GRACE_SECONDS']);
  const segundos = Number.isFinite(raw) && raw > 0 ? raw : DEFAULT_GRACE_SECONDS;
  return segundos * 1000;
})();

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
  /** Alcance de incidentes derivado (PROPIO | GLOBAL | SECTOR | VACIO). */
  alcance: Alcance;
}

/** Respuesta del endpoint de login (aditiva: un paso o reto MFA). */
interface LoginApiResponse {
  access_token?: string | null;
  token_type?: string;
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

/** Ciclo de vida de la sesion expuesto a la UI (c-91, FSL-001..005). */
export interface SessionLifecycleValue {
  /** true mientras la app rehidrata la sesion al arrancar (FSL-001). */
  isHydrating: boolean;
  /** true cuando el aviso proactivo de expiracion esta visible (FSL-002). */
  expirationPromptVisible: boolean;
  /** Extiende la sesion por consentimiento del usuario (FSL-004). */
  continueSession: () => Promise<void>;
}

// ── Contextos ────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);
const SessionLifecycleContext = createContext<SessionLifecycleValue | null>(null);

/** Nombre para mostrar en errores si se usa fuera del provider. */
const DISPLAY_NAME = 'AuthContext';

// ── Provider ─────────────────────────────────────────────────────────────────

interface AuthProviderProps {
  children: ReactNode;
  /** Sobreescribe la ventana de gracia del aviso (default 30 s). */
  gracePeriodMs?: number;
}

export function AuthProvider({ children, gracePeriodMs = SESSION_PROMPT_GRACE_MS }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    token: null,
    username: null,
    isAuthenticated: false,
    mfaRequired: false,
    rol: null,
    alcance: ALCANCE_VACIO,
  });
  const [isHydrating, setIsHydrating] = useState(true);
  const [expirationPromptVisible, setExpirationPromptVisible] = useState(false);

  // Ticket y usuario pendientes del segundo factor (no se renderizan).
  const mfaTicketRef = useRef<string | null>(null);
  const mfaUsernameRef = useRef<string | null>(null);
  // Temporizador proactivo hacia la expiracion del access token.
  const expiryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearExpiryTimer = useCallback(() => {
    if (expiryTimerRef.current !== null) {
      clearTimeout(expiryTimerRef.current);
      expiryTimerRef.current = null;
    }
  }, []);

  /** Programa el aviso proactivo `expiresIn` segundos en el futuro. */
  const scheduleExpiry = useCallback(
    (expiresIn: number | null) => {
      clearExpiryTimer();
      if (expiresIn == null || expiresIn <= 0) return;
      expiryTimerRef.current = setTimeout(() => {
        setExpirationPromptVisible(true);
      }, expiresIn * 1000);
    },
    [clearExpiryTimer],
  );

  useEffect(() => {
    return () => clearExpiryTimer();
  }, [clearExpiryTimer]);

  /**
   * Resuelve la identidad (username + rol + alcance) desde el backend.
   *
   * Degrada de forma segura: si `/auth/me` falla, devuelve identidad nula y
   * alcance VACIO, de modo que no se habilita ninguna superficie operativa (el
   * backend sigue siendo el limite de seguridad).
   */
  const resolverIdentidad = useCallback(async (): Promise<{
    username: string | null;
    rol: string | null;
    alcance: Alcance;
  }> => {
    try {
      const identidad = await obtenerIdentidad();
      return {
        username: identidad.username,
        rol: identidad.rol,
        alcance: identidad.alcance,
      };
    } catch {
      return { username: null, rol: null, alcance: ALCANCE_VACIO };
    }
  }, []);

  /**
   * Rehidrata la sesion con la cookie de refresh (arranque y multi-pestana).
   *
   * @returns true si se obtuvo un access nuevo y la sesion quedo autenticada.
   */
  const rehydrate = useCallback(async (): Promise<boolean> => {
    const tokens = await refreshSession();
    if (!tokens) return false;
    setAuthToken(tokens.accessToken);
    const { username, rol, alcance } = await resolverIdentidad();
    setExpirationPromptVisible(false);
    setState({
      token: tokens.accessToken,
      username,
      isAuthenticated: true,
      mfaRequired: false,
      rol,
      alcance,
    });
    scheduleExpiry(tokens.expiresIn);
    return true;
  }, [resolverIdentidad, scheduleExpiry]);

  /**
   * Aplica el cierre de sesion local (revoca el refresh y limpia el estado).
   *
   * @param broadcast difunde el logout a las demas pestanas (false si el cierre
   *   proviene de otra pestana, para no re-difundir en bucle).
   * @param revoke invoca el logout del backend (revoca la cookie).
   */
  const applyLogout = useCallback(
    (options?: { broadcast?: boolean; revoke?: boolean }) => {
      const { broadcast = true, revoke = true } = options ?? {};
      if (revoke) {
        void apiClient.post('/auth/logout').catch(() => undefined);
      }
      clearAuthToken();
      clearExpiryTimer();
      setExpirationPromptVisible(false);
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
      if (broadcast) {
        broadcastSessionEvent({ type: 'logout' });
      }
    },
    [clearExpiryTimer],
  );

  /** Cierra la sesion (manual) y propaga el evento a las demas pestanas. */
  const logout = useCallback(() => {
    applyLogout();
  }, [applyLogout]);

  /** Extiende la sesion por consentimiento del usuario (FSL-004). */
  const continueSession = useCallback(async (): Promise<void> => {
    const tokens = await refreshSession();
    if (!tokens) {
      // El refresco fallo (cookie invalida): la sesion se trata como cerrada.
      applyLogout();
      return;
    }
    setAuthToken(tokens.accessToken);
    setExpirationPromptVisible(false);
    setState((prev) =>
      prev.isAuthenticated ? { ...prev, token: tokens.accessToken } : prev,
    );
    scheduleExpiry(tokens.expiresIn);
    broadcastSessionEvent({ type: 'refreshed' });
  }, [applyLogout, scheduleExpiry]);

  /** Fija el access token en memoria, resuelve la identidad y autentica. */
  const applyTokenResponse = useCallback(
    async (username: string, data: LoginApiResponse) => {
      const token = data.access_token ?? '';
      setAuthToken(token);
      setExpirationPromptVisible(false);
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
      scheduleExpiry(data.expires_in ?? null);
    },
    [resolverIdentidad, scheduleExpiry],
  );

  // Rehidratacion al arranque: si hay cookie vigente, restaura la sesion.
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      await rehydrate();
      if (!cancelled) setIsHydrating(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [rehydrate]);

  // Coherencia multi-pestana (FSL-005).
  useEffect(() => {
    const unsubscribe = subscribeToSessionEvents((event: SessionEvent) => {
      if (event.type === 'logout') {
        // Cierre remoto: limpiar local sin re-difundir ni re-revocar.
        applyLogout({ broadcast: false, revoke: false });
      } else if (event.type === 'refreshed') {
        // Otra pestana extendio la sesion: rehidratar para seguir autenticada.
        void rehydrate();
      }
    });
    return unsubscribe;
  }, [applyLogout, rehydrate]);

  // Ventana de gracia: sin respuesta, la sesion se cierra sola (FSL-003).
  useEffect(() => {
    if (!expirationPromptVisible) return;
    const id = setTimeout(() => {
      applyLogout();
    }, gracePeriodMs);
    return () => clearTimeout(id);
  }, [expirationPromptVisible, gracePeriodMs, applyLogout]);

  // Precedencia: mientras el aviso esta visible, el respaldo 401 no extiende
  // ni cierra la sesion sin consentimiento (FSL-005).
  useEffect(() => {
    setSilentRefreshEnabled(!expirationPromptVisible);
    return () => setSilentRefreshEnabled(true);
  }, [expirationPromptVisible]);

  const login = useCallback(
    async (username: string, password: string): Promise<boolean> => {
      try {
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
        const response = await apiClient.post<LoginApiResponse>('/auth/mfa/verify', {
          mfa_ticket: ticket,
          code,
        });
        await applyTokenResponse(username, response.data);
        return true;
      } catch {
        return false;
      }
    },
    [applyTokenResponse],
  );

  const enrollMfa = useCallback(async (): Promise<MfaEnrollmentData> => {
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
    setState((prev) => (prev.isAuthenticated ? { ...prev, rol, alcance } : prev));
  }, [resolverIdentidad]);

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

  const lifecycleValue = useMemo<SessionLifecycleValue>(
    () => ({
      isHydrating,
      expirationPromptVisible,
      continueSession,
    }),
    [isHydrating, expirationPromptVisible, continueSession],
  );

  return (
    <AuthContext.Provider value={value}>
      <SessionLifecycleContext.Provider value={lifecycleValue}>
        {children}
      </SessionLifecycleContext.Provider>
    </AuthContext.Provider>
  );
}

// ── Hooks ────────────────────────────────────────────────────────────────────

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

/**
 * Hook para acceder al ciclo de vida de la sesion (rehidratacion y expiracion).
 *
 * Lanza un error si se usa fuera de <AuthProvider>.
 */
export function useSessionLifecycle(): SessionLifecycleValue {
  const context = useContext(SessionLifecycleContext);
  if (!context) {
    throw new Error(
      `${DISPLAY_NAME}: useSessionLifecycle debe usarse dentro de <AuthProvider>`,
    );
  }
  return context;
}

AuthContext.displayName = DISPLAY_NAME;
