/**
 * Función utilitaria de composición de clases CSS para Tailwind.
 *
 * Responsabilidad:
 *   Combina `clsx` (evaluación condicional de clases) con `tailwind-merge`
 *   (resolución de conflictos entre clases Tailwind) en una sola llamada `cn()`.
 *   Esto permite sobrescribir estilos en props `className` sin que clases duplicadas
 *   o contradictorias generen comportamientos inesperados en producción.
 *
 * Ejemplo: cn('px-2 py-1', condition && 'text-red-500', 'px-4')
 *   → 'py-1 text-red-500 px-4'  (px-2 es eliminado por tailwind-merge al ver px-4)
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combina y deduplica clases Tailwind CSS de forma segura.
 *
 * @param inputs - Lista de clases, objetos condicionales o valores falsy a combinar.
 * @returns Cadena de clases CSS sin conflictos de utilidades Tailwind.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
