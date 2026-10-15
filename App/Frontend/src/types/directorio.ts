/**
 * Tipos del directorio de empleados (c-89, frontend-directorio).
 *
 * Espejo del contrato de la API EXISTENTE `/api/v1/directorio` (c-54/c-60):
 *   - `Empleado`         <- `EmpleadoRead`   (GET/POST/PATCH)
 *   - `EmpleadoCreate`   -> `EmpleadoCreate` (POST)
 *   - `EmpleadoUpdate`   -> `EmpleadoUpdate` (PATCH; edicion parcial)
 *   - `PurgaResultado`   <- `PurgaDirectorioRead` (POST /purga)
 *
 * El catalogo `ROLES_EMPLEADO` es la unica fuente del vocabulario de roles en la
 * UI y refleja la politica de `requires_sector` del backend: solo
 * `gestion_incidentes` exige sector (c-86). El frontend NO revalida el rol: el
 * backend sigue siendo la fuente de verdad.
 */

/** Roles de empleado del directorio; valores EXACTOS del backend. */
export type RolEmpleado =
  | 'usuario_final'
  | 'mesa_de_ayuda'
  | 'administrador_directorio'
  | 'gestion_incidentes';

/** Representacion de un empleado del directorio (campos minimizados). */
export interface Empleado {
  id: number;
  legajo: string;
  nombre: string;
  email: string;
  telefono: string | null;
  sector_id: number | null;
  rol: RolEmpleado;
  activo: boolean;
}

/** Cuerpo de alta de un empleado del directorio. */
export interface EmpleadoCreate {
  legajo: string;
  nombre: string;
  email: string;
  telefono?: string | null;
  sector_id?: number | null;
  rol: RolEmpleado;
}

/** Cuerpo de edicion parcial; solo se aplican los campos enviados. */
export interface EmpleadoUpdate {
  legajo?: string;
  nombre?: string;
  email?: string;
  telefono?: string | null;
  sector_id?: number | null;
  rol?: RolEmpleado;
  activo?: boolean;
}

/** Resultado del disparador manual de purga por retencion (DIR-007). */
export interface PurgaResultado {
  purgados: number;
  ids: number[];
}

/** Opcion del catalogo de roles del formulario del directorio. */
export interface RolEmpleadoOpcion {
  value: RolEmpleado;
  label: string;
  /** true cuando el rol exige un sector asignado (politica `requires_sector`). */
  requiresSector: boolean;
}

/**
 * Catalogo unico de roles del formulario. `gestion_incidentes` exige sector;
 * el resto lo admite como opcional (c-89, D4).
 */
export const ROLES_EMPLEADO: RolEmpleadoOpcion[] = [
  { value: 'usuario_final', label: 'Usuario final', requiresSector: false },
  { value: 'mesa_de_ayuda', label: 'Mesa de ayuda', requiresSector: false },
  {
    value: 'administrador_directorio',
    label: 'Administrador del directorio',
    requiresSector: false,
  },
  {
    value: 'gestion_incidentes',
    label: 'Gestion de incidentes',
    requiresSector: true,
  },
];

/**
 * Indica si un rol exige sector segun el catalogo. Funcion pura de consulta:
 * centraliza la regla para que el formulario no replique el vocabulario.
 */
export function rolRequiereSector(rol: RolEmpleado | null | undefined): boolean {
  if (!rol) return false;
  return ROLES_EMPLEADO.find((r) => r.value === rol)?.requiresSector ?? false;
}
