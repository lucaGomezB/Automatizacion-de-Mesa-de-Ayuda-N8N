/**
 * Capa de acceso a datos para el directorio de empleados (c-89, frontend-directorio).
 *
 * Responsabilidad:
 *   Encapsula las llamadas HTTP al prefijo EXISTENTE `/api/v1/directorio` del
 *   backend FastAPI. Cada funcion retorna los datos tipados ya extraidos del
 *   cuerpo de la respuesta y delega el manejo de errores al hook de React Query.
 *
 * Contratos de API (c-54/c-60, sin cambios):
 *   - GET    /directorio/empleados?solo_activos=  -> Empleado[]
 *   - POST   /directorio/empleados                -> Empleado (201)
 *   - PATCH  /directorio/empleados/{id}           -> Empleado
 *   - DELETE /directorio/empleados/{id}           -> 204 sin cuerpo
 *   - POST   /directorio/purga                    -> PurgaResultado
 */
import { apiClient } from './api';
import type {
  Empleado,
  EmpleadoCreate,
  EmpleadoUpdate,
  PurgaResultado,
} from '../types/directorio';

/** Parametros del listado del directorio. */
export interface ListarEmpleadosParams {
  /** true -> solo empleados activos (`solo_activos=true` en el endpoint). */
  soloActivos?: boolean;
}

/** Lista los empleados del directorio, opcionalmente solo los activos. */
export async function listarEmpleados(
  params: ListarEmpleadosParams = {}
): Promise<Empleado[]> {
  const { data } = await apiClient.get<Empleado[]>('/directorio/empleados', {
    params: { solo_activos: params.soloActivos },
  });
  return data;
}

/** Crea un empleado del directorio (alta). */
export async function crearEmpleado(payload: EmpleadoCreate): Promise<Empleado> {
  const { data } = await apiClient.post<Empleado>('/directorio/empleados', payload);
  return data;
}

/** Edita parcialmente un empleado; `activo` alterna su estado. */
export async function actualizarEmpleado(
  id: number,
  payload: EmpleadoUpdate
): Promise<Empleado> {
  const { data } = await apiClient.patch<Empleado>(
    `/directorio/empleados/${id}`,
    payload
  );
  return data;
}

/** Ejecuta el borrado fisico por solicitud ARCO (irreversible). */
export async function borrarEmpleadoArco(id: number): Promise<void> {
  await apiClient.delete(`/directorio/empleados/${id}`);
}

/** Dispara manualmente la purga por retencion y devuelve el conteo purgado. */
export async function purgarDirectorio(): Promise<PurgaResultado> {
  const { data } = await apiClient.post<PurgaResultado>('/directorio/purga');
  return data;
}
