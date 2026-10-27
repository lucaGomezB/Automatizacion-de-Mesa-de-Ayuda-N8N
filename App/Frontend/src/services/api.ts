/**
 * Módulo de configuración centralizada del cliente HTTP (Axios).
 *
 * Responsabilidad:
 *   Provee una instancia única de Axios (`apiClient`) preconfigurada con la URL base,
 *   cabeceras JSON, `withCredentials` (para adjuntar la cookie de refresh HttpOnly)
 *   y un timeout (65 s) mayor que el peor caso total de una clasificación del backend
 *   (60 s), para permitir que la API resuelva su propio fallback antes de que el
 *   cliente desista.
 *
 *   También exporta `extractApiErrorMessage`, función utilitaria que normaliza cualquier
 *   tipo de error de Axios a un mensaje legible en español para mostrar al usuario final.
 *
 *   El interceptor de request inyecta automáticamente el access token JWT en el header
 *   Authorization si hay una sesión activa. El interceptor de response captura
 *   errores 401 y dispara el refresco silencioso de RESPALDO (c-91, FSL-005).
 *
 * Transporte del refresh (c-91, IAH-014):
 *   El refresh token YA NO vive en memoria ni viaja por el cuerpo: el backend lo
 *   entrega en una cookie `HttpOnly` + `Secure` + `SameSite=Strict`. Este módulo
 *   sólo necesita `withCredentials` para que el navegador adjunte la cookie; nunca
 *   lee ni persiste el refresh en un medio accesible por JavaScript.
 *
 * Configuración:
 *   La URL base se toma de la variable de entorno `VITE_API_BASE_URL` (única fuente
 *   de verdad; en Docker se hornea en tiempo de build como build arg). Si no está
 *   definida, se usa `http://localhost:8000` como fallback único documentado para
 *   desarrollo local. La barra final se recorta y el prefijo `/api/v1` se agrega en
 *   un solo lugar para no duplicar el sufijo.
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = (
  import.meta.env['VITE_API_BASE_URL'] ?? 'http://localhost:8000'
).replace(/\/+$/, '');

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  // El timeout del cliente (65 s) supera el peor caso total de una clasificación
  // del backend (60 s, Settings.gemini_total_timeout_seconds) para permitir que la
  // API maneje su propio fallback antes de que el cliente desista.
  timeout: 65_000,
  // c-91 (IAH-014): las requests deben enviar credenciales para que el navegador
  // adjunte la cookie de refresh HttpOnly (login/rehidratacion/refresh).
  withCredentials: true,
});

// ── Estado en memoria ────────────────────────────────────────────────────────
// El access token vive SOLO en memoria (c-91). El refresh NO se guarda: viaja en
// una cookie HttpOnly que JavaScript no puede leer.

let _authToken: string | null = null;
let _onUnauthorized: (() => void) | null = null;
let _refreshInFlight: Promise<SessionTokens | null> | null = null;
// c-91 (FSL-005): el refresco silencioso ante 401 es RESPALDO. Cuando el aviso
// proactivo de expiracion esta pendiente se deshabilita, para no extender la
// sesion (ni cerrarla) sin el consentimiento del usuario.
let _silentRefreshEnabled = true;

/** Resultado de una rotacion de sesion por cookie. */
export interface SessionTokens {
  /** Nuevo access token de memoria. */
  accessToken: string;
  /** Segundos hasta la expiracion del access token (puede faltar). */
  expiresIn: number | null;
}

/** Establece el access token que se inyecta en todas las requests. */
export function setAuthToken(token: string): void {
  _authToken = token;
}

/** Elimina el access token de memoria. */
export function clearAuthToken(): void {
  _authToken = null;
}

/**
 * Registra un callback que se ejecuta cuando el backend responde 401 y no es
 * posible refrescar la sesion (respaldo agotado). Usado por AuthContext.
 */
export function onUnauthorized(callback: () => void): void {
  _onUnauthorized = callback;
}

/**
 * Habilita o deshabilita el refresco silencioso de respaldo.
 *
 * El aviso proactivo de expiracion (FSL-002) es el mecanismo PRIMARIO; mientras
 * esta visible se deshabilita el respaldo para que un 401 de carrera no extienda
 * la sesion sin consentimiento (FSL-005).
 */
export function setSilentRefreshEnabled(enabled: boolean): void {
  _silentRefreshEnabled = enabled;
}

// ── Rotacion de sesion por cookie (single-flight) ────────────────────────────

/**
 * Rota la sesion usando la cookie de refresh (no hay cuerpo: el refresh es
 * `HttpOnly`). Usa una instancia cruda de axios (no `apiClient`) para no
 * reingresar al interceptor de response. Es single-flight: arranque, "continuar"
 * y el respaldo 401 comparten una unica rotacion.
 *
 * @returns El access token nuevo y su expiracion, o null si no hay cookie
 *   vigente o la rotacion fallo.
 */
async function rotateSession(): Promise<SessionTokens | null> {
  try {
    const response = await axios.post<{
      access_token: string;
      expires_in?: number | null;
    }>(
      `${API_BASE_URL}/api/v1/auth/refresh`,
      undefined,
      {
        withCredentials: true,
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      },
    );
    _authToken = response.data.access_token;  // gitleaks:allow (variable local, no un valor)
    return {
      accessToken: response.data.access_token,  // gitleaks:allow (variable local, no un valor)
      expiresIn: response.data.expires_in ?? null,
    };
  } catch {
    return null;
  }
}

/** Rota la sesion por cookie una sola vez por ventana concurrente. */
export function refreshSession(): Promise<SessionTokens | null> {
  if (_refreshInFlight) return _refreshInFlight;
  _refreshInFlight = rotateSession().finally(() => {
    _refreshInFlight = null;
  });
  return _refreshInFlight;
}

// ── Interceptor de request: inyectar token ────────────────────────────────────

apiClient.interceptors.request.use((config) => {
  if (_authToken) {
    config.headers.Authorization = `Bearer ${_authToken}`;
  }
  return config;
});

// ── Interceptor de response: 401 + refresco silencioso de respaldo ────────────

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const config = error.config as RetriableRequestConfig | undefined;

      // Respaldo: intentar refrescar una sola vez por request (FSL-005).
      if (_silentRefreshEnabled && config && !config._retry) {
        config._retry = true;
        const refreshed = await refreshSession();
        if (refreshed) {
          config.headers.Authorization = `Bearer ${refreshed.accessToken}`;
          return apiClient.request(config);
        }
      }

      if (_silentRefreshEnabled) {
        // Respaldo agotado: limpiar el access de memoria y notificar al AuthContext.
        _authToken = null;
        if (_onUnauthorized) {
          _onUnauthorized();
        }
      }
      // Con el respaldo deshabilitado (aviso proactivo pendiente) NO se cierra la
      // sesion aqui: la decision de continuar o cerrar es del usuario (FSL-004).
    }
    return Promise.reject(error);
  },
);

/** Estructura del cuerpo de error 422 Unprocessable Entity de FastAPI/Pydantic. */
interface FastApiValidationError {
  detail: string | Array<{ msg: string; loc: string[] }>;
  /** Formato de error propio del backend (manejadores personalizados en error_handlers.py). */
  error?: { code: string; message: string };
}

/**
 * Normaliza cualquier tipo de error de Axios a un mensaje legible en español.
 *
 * Orden de evaluación:
 *   1. Si la respuesta incluye un campo `detail` de FastAPI, se usa directamente.
 *   2. Si es un array de errores de validación Pydantic, se concatenan los mensajes.
 *   3. Si el código HTTP es conocido (404, 422, 503), se devuelve un mensaje genérico.
 *   4. Si no hay respuesta (error de red), se indica que el servidor no está disponible.
 *   5. En cualquier otro caso, mensaje de error inesperado.
 *
 * @param error - Error capturado en un bloque catch o en el handler de React Query.
 * @returns Cadena de texto lista para mostrar al usuario final.
 */
export function extractApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<FastApiValidationError>;
    const detail = axiosError.response?.data?.detail;

    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ');
    // Formato de error propio del backend: {"error": {"code": "...", "message": "..."}}
    if (axiosError.response?.data?.error?.message) return axiosError.response.data.error.message;

    const status = axiosError.response?.status;
    if (status === 403) return 'No tenés permiso para realizar esta acción.';
    if (status === 404) return 'El recurso solicitado no existe.';
    if (status === 422) return 'Los datos enviados no son válidos.';
    if (status === 500) return 'Error interno del servidor. Verificá que la base de datos esté accesible.';
    if (status === 503) return 'El servicio no está disponible temporalmente.';
    if (axiosError.code === 'ECONNABORTED') return 'La solicitud tardó demasiado. Intentá de nuevo.';
    if (!axiosError.response) return 'No se pudo conectar con el servidor. Verificá que la API esté activa.';
  }
  return 'Ocurrió un error inesperado. Intentá de nuevo.';
}
