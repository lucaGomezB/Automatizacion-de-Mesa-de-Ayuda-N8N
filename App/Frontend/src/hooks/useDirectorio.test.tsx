/**
 * Pruebas del hook useDirectorio (c-89, FDIR-002..006).
 *
 * La capa de servicios esta mockeada. Se verifica:
 *   - `useEmpleadosDirectorio` consume el listado con el flag `soloActivos`.
 *   - Cada mutacion invalida la clave del directorio tras el exito, de modo que
 *     el listado se refresca (FDIR-004/005/006).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import {
  useEmpleadosDirectorio,
  useCrearEmpleado,
  useActualizarEmpleado,
  useBorrarEmpleadoArco,
  usePurgarDirectorio,
  DIRECTORIO_EMPLEADOS_QUERY_KEY,
} from './useDirectorio';
import * as directorioService from '../services/directorioService';
import { createTestQueryClient } from '../test/utils';
import type { Empleado } from '../types/directorio';

vi.mock('../services/directorioService');

const mockEmpleado: Empleado = {
  id: 7,
  legajo: '0007',
  nombre: 'Ana Gomez',
  email: 'ana.gomez@example.com',
  telefono: null,
  sector_id: 1,
  rol: 'usuario_final',
  activo: true,
};

describe('useDirectorio', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function wrapperWith(client = createTestQueryClient()) {
    const Wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    return { client, Wrapper };
  }

  it('useEmpleadosDirectorio consume el listado con soloActivos y expone la lista', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValueOnce([mockEmpleado]);
    const { Wrapper } = wrapperWith();

    const { result } = renderHook(() => useEmpleadosDirectorio(true), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(directorioService.listarEmpleados).toHaveBeenCalledWith({ soloActivos: true });
    expect(result.current.data).toEqual([mockEmpleado]);
  });

  it('useCrearEmpleado invalida la clave del directorio tras el alta', async () => {
    vi.mocked(directorioService.crearEmpleado).mockResolvedValueOnce(mockEmpleado);
    const { client, Wrapper } = wrapperWith();
    const invalidateSpy = vi.spyOn(client, 'invalidateQueries');

    const { result } = renderHook(() => useCrearEmpleado(), { wrapper: Wrapper });

    act(() => {
      result.current.mutate({
        legajo: '0007',
        nombre: 'Ana Gomez',
        email: 'ana.gomez@example.com',
        rol: 'usuario_final',
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY],
    });
  });

  it('useActualizarEmpleado envia id y payload e invalida la clave', async () => {
    vi.mocked(directorioService.actualizarEmpleado).mockResolvedValueOnce({
      ...mockEmpleado,
      activo: false,
    });
    const { client, Wrapper } = wrapperWith();
    const invalidateSpy = vi.spyOn(client, 'invalidateQueries');

    const { result } = renderHook(() => useActualizarEmpleado(), { wrapper: Wrapper });

    act(() => {
      result.current.mutate({ id: 7, payload: { activo: false } });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(directorioService.actualizarEmpleado).toHaveBeenCalledWith(7, { activo: false });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY],
    });
  });

  it('useBorrarEmpleadoArco borra por id e invalida la clave', async () => {
    vi.mocked(directorioService.borrarEmpleadoArco).mockResolvedValueOnce(undefined);
    const { client, Wrapper } = wrapperWith();
    const invalidateSpy = vi.spyOn(client, 'invalidateQueries');

    const { result } = renderHook(() => useBorrarEmpleadoArco(), { wrapper: Wrapper });

    act(() => {
      result.current.mutate(7);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(directorioService.borrarEmpleadoArco).toHaveBeenCalledWith(7);
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY],
    });
  });

  // -- TRIANGULACION (c-89, 2.3): caminos de error --

  it('useEmpleadosDirectorio expone isError cuando el listado falla', async () => {
    const networkError = new Error('Network Error');
    vi.mocked(directorioService.listarEmpleados).mockRejectedValueOnce(networkError);
    const { Wrapper } = wrapperWith();

    const { result } = renderHook(() => useEmpleadosDirectorio(false), {
      wrapper: Wrapper,
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(networkError);
  });

  it('una mutacion rechazada expone el error sin lanzar y no invalida el listado', async () => {
    const serverError = new Error('Legajo duplicado');
    vi.mocked(directorioService.crearEmpleado).mockRejectedValueOnce(serverError);
    const { client, Wrapper } = wrapperWith();
    const invalidateSpy = vi.spyOn(client, 'invalidateQueries');

    const { result } = renderHook(() => useCrearEmpleado(), { wrapper: Wrapper });

    act(() => {
      result.current.mutate({
        legajo: '0007',
        nombre: 'Ana Gomez',
        email: 'ana.gomez@example.com',
        rol: 'usuario_final',
      });
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(serverError);
    expect(invalidateSpy).not.toHaveBeenCalledWith({
      queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY],
    });
  });

  it('usePurgarDirectorio dispara la purga y expone el conteo', async () => {
    vi.mocked(directorioService.purgarDirectorio).mockResolvedValueOnce({
      purgados: 2,
      ids: [1, 2],
    });
    const { client, Wrapper } = wrapperWith();
    const invalidateSpy = vi.spyOn(client, 'invalidateQueries');

    const { result } = renderHook(() => usePurgarDirectorio(), { wrapper: Wrapper });

    act(() => {
      result.current.mutate();
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual({ purgados: 2, ids: [1, 2] });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [DIRECTORIO_EMPLEADOS_QUERY_KEY],
    });
  });
});
