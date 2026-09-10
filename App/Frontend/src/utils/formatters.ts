/**
 * Funciones de formato para los valores del dominio de mesa de ayuda.
 *
 * Responsabilidad:
 *   Centraliza la lógica de presentación para evitar conversiones dispersas en los componentes.
 *   Cubre: fechas ISO 8601, confianza del clasificador (float → porcentaje),
 *   prioridades, estados del ciclo de vida y etapas del pipeline híbrido.
 *
 *   Se utiliza el locale `es-AR` (español rioplatense) como estándar regional del proyecto,
 *   alineado con la variante del idioma utilizada en el prompt de Gemini 2.5 Flash.
 */

/** Formatea una fecha ISO 8601 al formato "DD/MM/AAAA HH:MM" en español rioplatense. */
export function formatearFecha(isoString: string): string {
  return new Intl.DateTimeFormat('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(isoString));
}

/** Convierte la confianza del clasificador (0.0–1.0) a porcentaje legible: "87%". */
export function formatearConfianza(confianza: number): string {
  return `${Math.round(confianza * 100)}%`;
}

/** Traduce los valores de PrioridadEnum al español capitalizado para presentación. */
export function formatearPrioridad(prioridad: string): string {
  const mapa: Record<string, string> = {
    baja: 'Baja',
    media: 'Media',
    alta: 'Alta',
  };
  return mapa[prioridad] ?? prioridad;
}

/** Traduce los nombres de estado del ciclo de vida a formato de presentación. */
export function formatearEstado(nombre: string): string {
  const mapa: Record<string, string> = {
    nuevo: 'Nuevo',
    'en proceso': 'En Proceso',
    'en espera': 'En Espera',
    resuelto: 'Resuelto',
    cerrado: 'Cerrado',
  };
  return mapa[nombre.toLowerCase()] ?? nombre;
}

/** Traduce el nombre de etapa del clasificador híbrido a español. */
export function formatearEtapa(etapa: string): string {
  const mapa: Record<string, string> = {
    deterministic: 'Determinístico',
    gemini: 'Gemini 2.5 Flash',
    fallback: 'Sin clasificar',
  };
  return mapa[etapa] ?? etapa;
}

/** Trunca una cadena a un máximo de caracteres y agrega "…" si fue recortada. */
export function truncar(texto: string, maxCaracteres = 80): string {
  if (texto.length <= maxCaracteres) return texto;
  return `${texto.slice(0, maxCaracteres)}…`;
}
