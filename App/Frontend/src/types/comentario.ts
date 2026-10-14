/**
 * Tipos de los comentarios append-only de un incidente (c-86, D7).
 *
 * Espejo del schema Pydantic `ComentarioRead`. El backend devuelve `created_at`
 * en UTC; el formato de presentacion `HH:MM:SS DD/MM/AAAA : {texto}` se resuelve
 * en el cliente con la zona `America/Argentina/Buenos_Aires`.
 */

export interface ComentarioRead {
  id: number;
  incidente_id: number;
  /** Empleado autor; `null` si el autor fue borrado (ARCO, SET NULL). */
  autor_empleado_id: number | null;
  texto: string;
  /** Instante de alta en UTC (ISO 8601). */
  created_at: string;
}