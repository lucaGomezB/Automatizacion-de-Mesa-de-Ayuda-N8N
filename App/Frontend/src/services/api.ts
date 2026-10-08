/**
 * Módulo de configuración centralizada del cliente HTTP (Axios).
 *
 * Responsabilidad:
 *   Provee una instancia única de Axios (`apiClient`) preconfigurada con la URL base,
 *   cabeceras JSON y un timeout mayor al de Gemini (10 s) para permitir que el backend
 *   maneje su propio timeout antes de que el cliente desista.
 *
 *   También exporta `extractApiErrorMessage`, función utilitaria que normaliza cualquier
 *   tipo de error de Axios a un mensaje legible en español para mostrar al usuario final.
 *
 *   El interceptor de request inyecta automáticamente el token JWT en el header
 *   Authorization si hay una sesión activa. El interceptor de response captura
 *   errores 401 y dispara el callback de logout.
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
  // El timeout del cliente supera el timeout de Gemini (10 s) para permitir
  // que la API maneje su propio fallback antes de que el cliente desista.
  timeout: 20_000,
});

// ── Tokens en memoria ────────────────────────────────────────────────────────
// c-63a: ademas del access token, se mantiene el refresh token opaco para el
// refresco silencioso (rotativo) ante un 401.

let _authToken: string | null = null;
let _refreshToken: string | null = null;
let _onUnauthorized: (() => void) | null = null;
let _refreshInFlight: Promise<string | null> | null = null;

/** Establece el access token que se inyecta en todas las requests. */
export function setAuthToken(token: string): void {
  _authToken = token;
}

/** Elimina el access token de memoria. */
export function clearAuthToken(): void {
  _authToken = null;
}

/** Establece el refresh token que habilita el refresco silencioso. */
export function setRefreshToken(token: string | null): void {
  _refreshToken = token;
}

/** Devuelve el refresh token actual (o null). */
export function getRefreshToken(): string | null {
  return _refreshToken;
}

/** Elimina el refresh token de memoria. */
export function clearRefreshToken(): void {
  _refreshToken = null;
}

/**
 * Registra un callback que se ejecuta cuando el backend responde 401 y no es
 * posible refrescar la sesion. Usado por AuthContext para redirigir al login.
 */
export function onUnauthorized(callback: () => void): void {
  _onUnauthorized = callback;
}

// ── Refresco silencioso (single-flight) ──────────────────────────────────────

/**
 * Rota el par de tokens usando el refresh token en memoria.
 *
 * Usa una instancia cruda de axios (no `apiClient`) para no reingresar al
 * interceptor de response. Es single-flight: varias respuestas 401 concurrentes
 * comparten una unica rotacion.
 *
 * @returns El nuevo access token, o null si no hay refresh o fallo la rotacion.
 */
async function refreshAccessToken(): Promise<string | null> {
  if (!_refreshToken) return null;
  if (_refreshInFlight) return _refreshInFlight;

  _refreshInFlight = axios
    .post<{ access_token: string; refresh_token?: string }>(
      `${API_BASE_URL}/api/v1/auth/refresh`,
      { refresh_token: _refreshToken },
      { headers: { 'Content-Type': 'application/json', Accept: 'application/json' } },
    )
    .then((response) => {
      _authToken = response.data.access_token;  // gitleaks:allow (variable local, no un valor)
      if (response.data.refresh_token) {
        _refreshToken = response.data.refresh_token;  // gitleaks:allow (variable local, no un valor)
      }
      return _authToken;
    })
    .catch(() => null)
    .finally(() => {
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

// ── Interceptor de response: 401 + refresco silencioso ───────────────────────

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const config = error.config as RetriableRequestConfig | undefined;

      // Intentar refrescar una sola vez por request antes de cerrar sesion.
      if (_refreshToken && config && !config._retry) {
        config._retry = true;
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          config.headers.Authorization = `Bearer ${refreshed}`;
          return apiClient.request(config);
        }
      }

      // Sin refresh posible: limpiar tokens locales y notificar al AuthContext.
      _authToken = null;
      _refreshToken = null;
      if (_onUnauthorized) {
        _onUnauthorized();
      }
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
    if (status === 404) return 'El recurso solicitado no existe.';
    if (status === 422) return 'Los datos enviados no son válidos.';
    if (status === 500) return 'Error interno del servidor. Verificá que la base de datos esté accesible.';
    if (status === 503) return 'El servicio no está disponible temporalmente.';
    if (axiosError.code === 'ECONNABORTED') return 'La solicitud tardó demasiado. Intentá de nuevo.';
    if (!axiosError.response) return 'No se pudo conectar con el servidor. Verificá que la API esté activa.';
  }
  return 'Ocurrió un error inesperado. Intentá de nuevo.';
}
