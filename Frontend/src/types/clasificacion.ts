/**
 * Tipos TypeScript para la entidad ClasificacionLog y las operaciones de auditoría del pipeline.
 *
 * Responsabilidad:
 *   Define las interfaces que espejo los schemas Pydantic de `app/schemas/clasificacion.py`,
 *   cubriendo el registro de auditoría de cada ejecución del pipeline híbrido de clasificación
 *   y las operaciones de validación humana sobre predicciones de baja confianza.
 *
 *   El flujo de datos es:
 *     1. El backend genera un `ClasificacionLogRead` por cada incidente procesado.
 *     2. Si `confianza < 0.70`, el registro aparece en la cola de revisión humana.
 *     3. El operador envía un `ClasificacionValidar` al endpoint PATCH para corregir o
 *        confirmar el sector predicho; el resultado alimenta el corpus de evaluación.
 */
import type { SectorRead } from './catalog';

/** Componente del pipeline híbrido que produjo la clasificación */
export type ClasificacionEtapa = 'deterministic' | 'gemini' | 'fallback';

// Registro de auditoría devuelto por los endpoints de clasificación
export interface ClasificacionLogRead {
  id: number;
  incidente_id: number;
  /** Nivel de certeza normalizado en [0.0, 1.0] */
  confianza: number;
  /** Etapa del clasificador: "deterministic" (reglas) | "gemini" (LLM) | "fallback" (sin clasificar) */
  etapa: ClasificacionEtapa;
  requiere_revision_humana: boolean;
  /** Respuesta JSON cruda de Gemini; null si la etapa fue deterministic */
  respuesta_raw: string | null;
  created_at: string;
  sector_predicho: SectorRead | null;
  /** Corrección del operador humano; null mientras no haya sido revisado */
  sector_validado: SectorRead | null;
}

// Payload enviado al endpoint PATCH /api/v1/clasificaciones/{id}/validar
export interface ClasificacionValidar {
  sector_id_validado: number;
}

// Parámetros de paginación para la cola de revisión pendiente
export interface RevisionPendienteParams {
  limit?: number;
  offset?: number;
}
