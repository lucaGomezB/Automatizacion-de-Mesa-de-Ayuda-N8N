/**
 * Tipos TypeScript y constantes para las entidades de catálogo del sistema.
 *
 * Responsabilidad:
 *   Define las interfaces que espejo los schemas Pydantic de `app/schemas/catalog.py`
 *   y expone constantes derivadas de la migración de seed `001_seed_catalogs.py`.
 *
 *   Los catálogos son inmutables en tiempo de ejecución (no existe endpoint de modificación),
 *   por lo que sus IDs se hardcodean aquí como constantes `as const` en lugar de consultarlos
 *   dinámicamente. Cualquier cambio en la base de datos requiere actualizar este archivo.
 *
 * Valores de catálogo definidos en 001_seed_catalogs.py:
 *   Sectores   : Sistemas (1), Operaciones (2), Soporte Técnico (3)
 *   Estados    : Nuevo (1), En Proceso (2), En Espera (3), Resuelto (4), Cerrado (5)
 *   Canales    : Correo electrónico (1), Formulario web (2), Llamada telefónica (3)
 */

export interface SectorRead {
  id: number;
  /** Uno de: "Sistemas" | "Operaciones" | "Soporte Técnico" */
  nombre: string;
  descripcion: string | null;
}

export interface EstadoRead {
  id: number;
  /** Uno de: "nuevo" | "en proceso" | "en espera" | "resuelto" | "cerrado" */
  nombre: string;
  descripcion: string | null;
  /** True únicamente para el estado "cerrado" (estado terminal del ciclo de vida) */
  es_terminal: boolean;
}

export interface CanalOrigenRead {
  id: number;
  /** Uno de: "correo electrónico" | "formulario web" | "llamada telefónica" */
  nombre: string;
  descripcion: string | null;
}

// IDs de catálogo determinados por la migración 001_seed_catalogs.py.
// Estos valores son estables ya que los catálogos son inmutables en tiempo de ejecución.
export const SECTOR_IDS = {
  SISTEMAS: 1,
  OPERACIONES: 2,
  SOPORTE_TECNICO: 3,
} as const;

export const ESTADO_IDS = {
  NUEVO: 1,
  EN_PROCESO: 2,
  EN_ESPERA: 3,
  RESUELTO: 4,
  CERRADO: 5,
} as const;

export const CANAL_ORIGEN_IDS = {
  CORREO_ELECTRONICO: 1,
  FORMULARIO_WEB: 2,
  LLAMADA_TELEFONICA: 3,
} as const;

// Opciones de sector disponibles para dropdowns de filtro y validación
export const SECTORES_OPCIONES = [
  { id: SECTOR_IDS.SISTEMAS, nombre: 'Sistemas' },
  { id: SECTOR_IDS.OPERACIONES, nombre: 'Operaciones' },
  { id: SECTOR_IDS.SOPORTE_TECNICO, nombre: 'Soporte Técnico' },
] as const;

// Opciones de estado disponibles para dropdowns de filtro
export const ESTADOS_OPCIONES = [
  { id: ESTADO_IDS.NUEVO, nombre: 'Nuevo' },
  { id: ESTADO_IDS.EN_PROCESO, nombre: 'En Proceso' },
  { id: ESTADO_IDS.EN_ESPERA, nombre: 'En Espera' },
  { id: ESTADO_IDS.RESUELTO, nombre: 'Resuelto' },
  { id: ESTADO_IDS.CERRADO, nombre: 'Cerrado' },
] as const;
