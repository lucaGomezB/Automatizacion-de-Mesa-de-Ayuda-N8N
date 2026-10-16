/**
 * Pruebas para extractApiErrorMessage de api.ts.
 * Los errores Axios se construyen como objetos con { isAxiosError: true } para
 * que axios.isAxiosError() los reconozca correctamente.
 */
import { describe, it, expect, vi, afterEach } from 'vitest';
import axios, {
  type AxiosAdapter,
  type AxiosError,
  type InternalAxiosRequestConfig,
} from 'axios';
import {
  apiClient,
  clearAuthToken,
  extractApiErrorMessage,
  onUnauthorized,
  refreshSession,
  setAuthToken,
  setSilentRefreshEnabled,
} from './api';

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

describe('api: transporte del refresh por cookie (c-91, IAH-014)', () => {
  const adapterOk: AxiosAdapter = async (config) => ({
    data: {},
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  });

  afterEach(() => {
    vi.restoreAllMocks();
    setSilentRefreshEnabled(true);
    clearAuthToken();
    onUnauthorized(() => undefined);
  });

  it('apiClient envia credenciales para adjuntar la cookie de refresh', () => {
    expect(apiClient.defaults.withCredentials).toBe(true);
  });

  it('refreshSession postea a /auth/refresh con credenciales y SIN cuerpo', async () => {
    const postSpy = vi
      .spyOn(axios, 'post')
      .mockResolvedValue({ data: { access_token: 'nuevo', expires_in: 1800 } } as never);

    const tokens = await refreshSession();

    expect(tokens).toEqual({ accessToken: 'nuevo', expiresIn: 1800 });
    expect(postSpy).toHaveBeenCalledWith(
      expect.stringContaining('/auth/refresh'),
      undefined,
      expect.objectContaining({ withCredentials: true }),
    );
  });

  it('refreshSession comparte una unica rotacion concurrente (single-flight)', async () => {
    let resolvePost: (value: unknown) => void = () => undefined;
    const postSpy = vi.spyOn(axios, 'post').mockReturnValue(
      new Promise((resolve) => {
        resolvePost = resolve;
      }) as never,
    );

    const primero = refreshSession();
    const segundo = refreshSession();
    expect(postSpy).toHaveBeenCalledTimes(1);

    resolvePost({ data: { access_token: 'x', expires_in: 60 } });
    await expect(primero).resolves.toEqual({ accessToken: 'x', expiresIn: 60 });
    await expect(segundo).resolves.toEqual({ accessToken: 'x', expiresIn: 60 });
  });

  it('refreshSession devuelve null cuando el refresco falla (sin cookie o invalida)', async () => {
    vi.spyOn(axios, 'post').mockRejectedValue(new Error('sin cookie'));
    await expect(refreshSession()).resolves.toBeNull();
  });

  it('inyecta el access token en el header Authorization', async () => {
    setAuthToken('access-xyz');

    const response = await apiClient.get('/ping', { adapter: adapterOk });
    expect(response.config.headers.Authorization).toBe('Bearer access-xyz');

    clearAuthToken();
  });

  it('no inyecta Authorization cuando no hay access token', async () => {
    clearAuthToken();

    const response = await apiClient.get('/ping', { adapter: adapterOk });
    expect(response.config.headers.Authorization).toBeUndefined();
  });
});

describe('api: refresco silencioso 401 como respaldo (c-91, FSL-005)', () => {
  interface RetriableConfig extends InternalAxiosRequestConfig {
    _retry?: boolean;
  }

  function make401(config: InternalAxiosRequestConfig): AxiosError {
    return new axios.AxiosError('Unauthorized', 'ERR_BAD_REQUEST', config, undefined, {
      status: 401,
      data: {},
      headers: {},
      config,
      statusText: 'Unauthorized',
    } as never);
  }

  afterEach(() => {
    vi.restoreAllMocks();
    setSilentRefreshEnabled(true);
    clearAuthToken();
    onUnauthorized(() => undefined);
  });

  it('ante un 401 refresca una vez y reintenta la request (fallback)', async () => {
    const adapter: AxiosAdapter = async (config) => {
      if ((config as RetriableConfig)._retry) {
        return { data: { ok: true }, status: 200, statusText: 'OK', headers: {}, config };
      }
      throw make401(config);
    };
    const postSpy = vi
      .spyOn(axios, 'post')
      .mockResolvedValue({ data: { access_token: 'nuevo', expires_in: 1800 } } as never);
    setAuthToken('viejo');

    const response = await apiClient.get('/ping', { adapter });

    expect(response.data).toEqual({ ok: true });
    expect(response.config.headers.Authorization).toBe('Bearer nuevo');
    expect(postSpy).toHaveBeenCalledTimes(1);
  });

  it('NO extiende la sesion sin consentimiento cuando el aviso proactivo esta pendiente', async () => {
    // El aviso proactivo deshabilita el respaldo: la decision es del usuario.
    setSilentRefreshEnabled(false);
    const adapter: AxiosAdapter = async (config) => {
      throw make401(config);
    };
    const postSpy = vi.spyOn(axios, 'post');
    const unauthorized = vi.fn();
    onUnauthorized(unauthorized);
    setAuthToken('viejo');

    await expect(apiClient.get('/ping', { adapter })).rejects.toBeTruthy();

    expect(postSpy).not.toHaveBeenCalled();
    // No se cierra la sesion por detras: el prompt conserva la decision.
    expect(unauthorized).not.toHaveBeenCalled();
  });

  it('cierra la sesion cuando el respaldo esta habilitado pero no puede refrescar', async () => {
    const adapter: AxiosAdapter = async (config) => {
      throw make401(config);
    };
    vi.spyOn(axios, 'post').mockRejectedValue(new Error('refresh invalido'));
    const unauthorized = vi.fn();
    onUnauthorized(unauthorized);
    setAuthToken('viejo');

    await expect(apiClient.get('/ping', { adapter })).rejects.toBeTruthy();

    expect(unauthorized).toHaveBeenCalledTimes(1);
  });
});
