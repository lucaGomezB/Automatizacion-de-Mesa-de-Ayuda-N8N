/**
 * Tipos TypeScript y constantes para las entidades de catálogo del sistema.
 *
 * Responsabilidad:
 *   Define las interfaces que espejo los schemas Pydantic de `app/schemas/catalog.py`.
 *
 *   Los sectores se obtienen en runtime desde `GET /api/v1/catalogos/sectores`
 *   (ver `services/catalogosService.ts`), por lo que NO se hardcodean identificadores
 *   numéricos de sector: los nombres canónicos son el único identificador estable de
 *   dominio. Los estados y canales, en cambio, son inmutables y sus IDs se declaran
 *   aquí como constantes `as const`.
 *
 * Valores de catálogo definidos en 001_seed_catalogs.py:
 *   Sectores   : obtenidos en runtime desde el endpoint de catálogo
 *   Estados    : Nuevo (1), En Proceso (2), En Espera (3), Resuelto (4), Cerrado (5)
 *   Canales    : Correo electrónico (1), Formulario web (2), Llamada telefónica (3)
 */

export interface SectorRead {
  id: number;
  /**
   * Uno de los cinco nombres canónicos (sin tildes):
   * "Seguridad Informatica" | "Soporte Tecnico Hardware" | "Soporte Tecnico Software"
   * | "Bases de Datos" | "Sistemas".
   */
  nombre: string;
  descripcion: string | null;
}

/**
 * Opción de sector consumida por los controles de la interfaz.
 *
 * Es el contrato mínimo devuelto por `GET /api/v1/catalogos/sectores`: la interfaz
 * solo necesita el `id` (para enviar referencias al backend) y el `nombre` (para
 * mostrar y resolver color/etiqueta).
 */
export type SectorOpcion = Pick<SectorRead, 'id' | 'nombre'>;

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

// Opciones de estado disponibles para dropdowns de filtro
export const ESTADOS_OPCIONES = [
  { id: ESTADO_IDS.NUEVO, nombre: 'Nuevo' },
  { id: ESTADO_IDS.EN_PROCESO, nombre: 'En Proceso' },
  { id: ESTADO_IDS.EN_ESPERA, nombre: 'En Espera' },
  { id: ESTADO_IDS.RESUELTO, nombre: 'Resuelto' },
  { id: ESTADO_IDS.CERRADO, nombre: 'Cerrado' },
] as const;
