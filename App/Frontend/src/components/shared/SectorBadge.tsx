/**
 * Badge del sector responsable del incidente con color diferenciado por dominio.
 *
 * Responsabilidad:
 *   Renderiza un `Badge` con la variante de color correspondiente al sector predicho
 *   o validado por el pipeline. Si el sector es `null` o `undefined` (incidente aún
 *   no clasificado), muestra "Pendiente" con variante neutra.
 *
 *   El color se resuelve por el nombre canónico del sector (nunca por IDs numéricos).
 *   Un nombre desconocido se renderiza con la variante neutra `muted`, sin lanzar
 *   excepciones.
 *
 * Mapeo de colores (nombres canónicos sin tildes):
 *   - Seguridad Informatica     → rojo (destructive)
 *   - Soporte Tecnico Hardware  → ámbar (warning)
 *   - Soporte Tecnico Software  → azul (info)
 *   - Bases de Datos            → verde (success)
 *   - Sistemas                  → secundario (secondary)
 *   - Desconocido               → gris (muted)
 */
import { Badge } from '@/components/ui/badge';
import type { BadgeProps } from '@/components/ui/badge';

interface SectorBadgeProps {
  nombre: string | null | undefined;
}

const SECTOR_VARIANTS: Record<string, BadgeProps['variant']> = {
  'Seguridad Informatica': 'destructive',
  'Soporte Tecnico Hardware': 'warning',
  'Soporte Tecnico Software': 'info',
  'Bases de Datos': 'success',
  Sistemas: 'secondary',
};

/** Resuelve la variante de color de un sector a partir de su nombre canónico. */
export function getSectorVariant(nombre: string): BadgeProps['variant'] {
  return SECTOR_VARIANTS[nombre] ?? 'muted';
}

export function SectorBadge({ nombre }: SectorBadgeProps) {
  if (!nombre) {
    return <Badge variant="muted">Pendiente</Badge>;
  }
  return <Badge variant={getSectorVariant(nombre)}>{nombre}</Badge>;
}
