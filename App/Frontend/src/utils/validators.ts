/**
 * Funciones de validación para el formulario de reporte de incidentes.
 *
 * Responsabilidad:
 *   Provee validadores compatibles con la API de React Hook Form (retornan `true`
 *   si es válido, o un `string` con el mensaje de error si no lo es).
 *
 *   El requisito mínimo de 15 palabras para la descripción es una convención del portal
 *   de usuario final, no una restricción del backend. Su objetivo es garantizar que
 *   el texto enviado a Gemini 2.5 Flash contenga suficiente contexto para una
 *   clasificación confiable.
 */

/** Valida que la descripción contenga al menos 'minimo' palabras. */
export function validarMinimoPalabras(
  descripcion: string,
  minimo = 15
): true | string {
  const palabras = descripcion.trim().split(/\s+/).filter(Boolean);
  if (palabras.length < minimo) {
    return `La descripción debe tener al menos ${minimo} palabras. Tiene ${palabras.length}.`;
  }
  return true;
}

/** Cuenta las palabras de un texto; se usa para el indicador de progreso en el formulario. */
export function contarPalabras(texto: string): number {
  if (!texto.trim()) return 0;
  return texto.trim().split(/\s+/).filter(Boolean).length;
}

/** Valida que el campo no esté vacío ni sea solo espacios. */
export function validarNoVacio(valor: string, nombreCampo = 'Este campo'): true | string {
  if (!valor.trim()) return `${nombreCampo} es obligatorio.`;
  return true;
}
