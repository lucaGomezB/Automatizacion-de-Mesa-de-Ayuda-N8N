/**
 * Badge del sector responsable del incidente con color diferenciado por dominio.
 *
 * Responsabilidad:
 *   Renderiza un `Badge` con la variante de color correspondiente al sector predicho
 *   o validado por el pipeline. Si el sector es `null` o `undefined` (incidente aún
 *   no clasificado), muestra "Pendiente" con variante neutra.
 *
 * Mapeo de colores (derivado de la convención visual del proyecto):
 *   - Sistemas        → azul (info)
 *   - Operaciones     → ámbar (warning)
 *   - Soporte Técnico → verde (success)
 *   - Sin asignar     → gris (muted)
 */
import { Badge } from '@/components/ui/badge';
import type { BadgeProps } from '@/components/ui/badge';

interface SectorBadgeProps {
  nombre: string | null | undefined;
}

function getVariant(nombre: string): BadgeProps['variant'] {
  switch (nombre) {
    case 'Sistemas':        return 'info';
    case 'Operaciones':     return 'warning';
    case 'Soporte Técnico': return 'success';
    default:                return 'muted';
  }
}

export function SectorBadge({ nombre }: SectorBadgeProps) {
  if (!nombre) {
    return <Badge variant="muted">Pendiente</Badge>;
  }
  return <Badge variant={getVariant(nombre)}>{nombre}</Badge>;
}
