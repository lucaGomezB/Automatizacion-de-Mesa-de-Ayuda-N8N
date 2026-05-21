/**
 * Módulo de configuración centralizada del cliente HTTP (Axios).
 *
 * Responsabilidad:
 *   Provee una instancia única de Axios (`apiClient`) preconfigura con la URL base,
 *   cabeceras JSON y un timeout mayor al de Gemini (10 s) para permitir que el backend
 *   maneje su propio timeout antes de que el cliente desista.
 *
 *   También exporta `extractApiErrorMessage`, función utilitaria que normaliza cualquier
 *   tipo de error de Axios a un mensaje legible en español para mostrar al usuario final.
 *
 * Configuración:
 *   La URL base se toma de la variable de entorno `VITE_API_BASE_URL`; si no está
 *   definida, se usa `http://localhost:8000` como valor por defecto para desarrollo local.
 */
import axios, { type AxiosError } from 'axios';

const API_BASE_URL = import.meta.env['VITE_API_BASE_URL'] ?? 'http://localhost:8000';

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
