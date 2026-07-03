/**
 * Badge del estado del ciclo de vida del incidente con color semántico.
 *
 * Responsabilidad:
 *   Renderiza un `Badge` con la variante de color que refleja la etapa del ciclo de vida
 *   del incidente, permitiendo una lectura visual rápida en tablas y diálogos.
 *
 * Mapeo de colores (convención del proyecto):
 *   - Nuevo      → azul (info)      — ingresado, sin atender aún.
 *   - En Proceso → ámbar (warning)  — asignado a un técnico.
 *   - En Espera  → gris (muted)     — bloqueado por un agente externo.
 *   - Resuelto   → verde (success)  — solución aplicada, pendiente de cierre formal.
 *   - Cerrado    → gris oscuro (secondary) — estado terminal del ciclo.
 */
import { Badge } from '@/components/ui/badge';
import { formatearEstado } from '@/utils/formatters';
import type { BadgeProps } from '@/components/ui/badge';

interface EstadoBadgeProps {
  nombre: string;
  esTerminal?: boolean;
}

function getVariant(nombre: string): BadgeProps['variant'] {
  switch (nombre.toLowerCase()) {
    case 'nuevo':        return 'info';
    case 'en proceso':   return 'warning';
    case 'en espera':    return 'muted';
    case 'resuelto':     return 'success';
    case 'cerrado':      return 'secondary';
    default:             return 'outline';
  }
}

export function EstadoBadge({ nombre }: EstadoBadgeProps) {
  return (
    <Badge variant={getVariant(nombre)}>
      {formatearEstado(nombre)}
    </Badge>
  );
}
