/**
 * Pruebas para extractApiErrorMessage de api.ts.
 * Los errores Axios se construyen como objetos con { isAxiosError: true } para
 * que axios.isAxiosError() los reconozca correctamente.
 */
import { describe, it, expect } from 'vitest';
import axios from 'axios';
import { extractApiErrorMessage } from './api';

/** Construye un AxiosError sintético que pasa axios.isAxiosError() */
function makeAxiosError(overrides: {
  response?: {
    status?: number;
    data?: Record<string, unknown>;
  };
  code?: string;
  message?: string;
}): unknown {
  const err = new axios.AxiosError(
    overrides.message ?? 'Request failed',
    overrides.code,
    undefined,
    undefined,
    overrides.response
      ? ({
          status: overrides.response.status ?? 500,
          data: overrides.response.data ?? {},
          headers: {},
          config: {} as never,
          statusText: '',
        } as never)
      : undefined
  );
  return err;
}

describe('extractApiErrorMessage', () => {
  // ---------- detail como string (FastAPI) ----------

  it('devuelve el detail de FastAPI cuando es una cadena de texto', () => {
    const err = makeAxiosError({
      response: { status: 400, data: { detail: 'El incidente no existe.' } },
    });
    expect(extractApiErrorMessage(err)).toBe('El incidente no existe.');
  });

  // ---------- detail como array Pydantic ----------

  it('concatena los mensajes de validación de Pydantic cuando detail es un array', () => {
    const err = makeAxiosError({
      response: {
        status: 422,
        data: {
          detail: [
            { msg: 'field required', loc: ['body', 'descripcion'] },
            { msg: 'value is not a valid integer', loc: ['body', 'canal_origen_id'] },
          ],
        },
      },
    });
    expect(extractApiErrorMessage(err)).toBe(
      'field required; value is not a valid integer'
    );
  });

  // ---------- error.message del backend ----------

  it('devuelve el mensaje del error propio del backend cuando existe', () => {
    const err = makeAxiosError({
      response: {
        status: 409,
        data: {
          error: { code: 'DUPLICATE_ENTRY', message: 'Ya existe un incidente con esa descripción.' },
        },
      },
    });
    expect(extractApiErrorMessage(err)).toBe('Ya existe un incidente con esa descripción.');
  });

  // ---------- códigos HTTP conocidos ----------

  it('devuelve el mensaje de recurso no encontrado para 404', () => {
    const err = makeAxiosError({ response: { status: 404, data: {} } });
    expect(extractApiErrorMessage(err)).toBe('El recurso solicitado no existe.');
  });

  it('devuelve el mensaje de datos no válidos para 422 (sin detail)', () => {
    const err = makeAxiosError({ response: { status: 422, data: {} } });
    expect(extractApiErrorMessage(err)).toBe('Los datos enviados no son válidos.');
  });

  it('devuelve el mensaje de error interno para 500', () => {
    const err = makeAxiosError({ response: { status: 500, data: {} } });
    expect(extractApiErrorMessage(err)).toBe(
      'Error interno del servidor. Verificá que la base de datos esté accesible.'
    );
  });

  it('devuelve el mensaje de servicio no disponible para 503', () => {
    const err = makeAxiosError({ response: { status: 503, data: {} } });
    expect(extractApiErrorMessage(err)).toBe('El servicio no está disponible temporalmente.');
  });

  // ---------- timeout (ECONNABORTED) ----------

  it('devuelve el mensaje de timeout cuando el código es ECONNABORTED', () => {
    const err = makeAxiosError({ code: 'ECONNABORTED' });
    expect(extractApiErrorMessage(err)).toBe('La solicitud tardó demasiado. Intentá de nuevo.');
  });

  // ---------- error de red (sin response) ----------

  it('devuelve el mensaje de servidor no disponible cuando no hay response', () => {
    const err = makeAxiosError({ message: 'Network Error' });
    // Sin response ni code especial → mensaje de red
    expect(extractApiErrorMessage(err)).toBe(
      'No se pudo conectar con el servidor. Verificá que la API esté activa.'
    );
  });

  // ---------- error no-Axios ----------

  it('devuelve el mensaje genérico para errores que no son de Axios', () => {
    expect(extractApiErrorMessage(new Error('TypeError qualquiera'))).toBe(
      'Ocurrió un error inesperado. Intentá de nuevo.'
    );
    expect(extractApiErrorMessage('string error')).toBe(
      'Ocurrió un error inesperado. Intentá de nuevo.'
    );
    expect(extractApiErrorMessage(null)).toBe(
      'Ocurrió un error inesperado. Intentá de nuevo.'
    );
  });
});
