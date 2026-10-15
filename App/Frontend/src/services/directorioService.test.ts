/**
 * Pruebas de la capa de servicios del directorio (c-89, FDIR-002..006).
 *
 * Axios mockeado en el limite de red: se verifica que cada funcion arme EXACTAMENTE
 * la ruta `/directorio/...` (el prefijo `/api/v1` lo agrega api.ts) y el parametro
 * `solo_activos` del listado.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import {
  listarEmpleados,
  crearEmpleado,
  actualizarEmpleado,
  borrarEmpleadoArco,
  purgarDirectorio,
} from './directorioService';
import type { Empleado, EmpleadoCreate } from '../types/directorio';

// Mockear el modulo completo de api para controlar apiClient.
vi.mock('./api', async (importOriginal) => {
  const original = await importOriginal<typeof import('./api')>();
  return {
    ...original,
    apiClient: {
      post: vi.fn(),
      get: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    },
  };
});

const mockedApiClient = vi.mocked(apiClient);

const mockEmpleado: Empleado = {
  id: 7,
  legajo: '0007',
  nombre: 'Ana Gomez',
  email: 'ana.gomez@example.com',
  telefono: '+5491122334455',
  sector_id: 1,
  rol: 'usuario_final',
  activo: true,
};

describe('directorioService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('lista empleados con solo_activos en el parametro del endpoint', async () => {
    vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockEmpleado] });

    const resultado = await listarEmpleados({ soloActivos: true });

    expect(mockedApiClient.get).toHaveBeenCalledWith('/directorio/empleados', {
      params: { solo_activos: true },
    });
    expect(resultado).toEqual([mockEmpleado]);
  });

  it('lista todos los empleados cuando soloActivos es false', async () => {
    vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockEmpleado] });

    await listarEmpleados({ soloActivos: false });

    expect(mockedApiClient.get).toHaveBeenCalledWith('/directorio/empleados', {
      params: { solo_activos: false },
    });
  });

  it('crea un empleado via POST /directorio/empleados', async () => {
    vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: mockEmpleado });
    const payload: EmpleadoCreate = {
      legajo: '0007',
      nombre: 'Ana Gomez',
      email: 'ana.gomez@example.com',
      rol: 'usuario_final',
    };

    const resultado = await crearEmpleado(payload);

    expect(mockedApiClient.post).toHaveBeenCalledWith('/directorio/empleados', payload);
    expect(resultado).toEqual(mockEmpleado);
  });

  it('actualiza un empleado via PATCH /directorio/empleados/{id}', async () => {
    vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockEmpleado });

    const resultado = await actualizarEmpleado(7, { activo: false });

    expect(mockedApiClient.patch).toHaveBeenCalledWith('/directorio/empleados/7', {
      activo: false,
    });
    expect(resultado).toEqual(mockEmpleado);
  });

  it('borra por ARCO via DELETE /directorio/empleados/{id}', async () => {
    vi.mocked(mockedApiClient.delete).mockResolvedValueOnce({ data: undefined });

    await borrarEmpleadoArco(7);

    expect(mockedApiClient.delete).toHaveBeenCalledWith('/directorio/empleados/7');
  });

  it('dispara la purga via POST /directorio/purga y devuelve el conteo', async () => {
    vi.mocked(mockedApiClient.post).mockResolvedValueOnce({
      data: { purgados: 3, ids: [1, 2, 3] },
    });

    const resultado = await purgarDirectorio();

    expect(mockedApiClient.post).toHaveBeenCalledWith('/directorio/purga');
    expect(resultado).toEqual({ purgados: 3, ids: [1, 2, 3] });
  });
});
