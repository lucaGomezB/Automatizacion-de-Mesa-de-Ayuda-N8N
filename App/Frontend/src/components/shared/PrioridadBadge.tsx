/**
 * Indicador visual compartido de prioridad de un incidente (c-90, FR-RBAC-009).
 *
 * Centraliza el mapeo prioridad -> variante/estilo para que las tres superficies
 * (`TicketsTable`, `MisIncidentes` y `DetalleIncidente`) NO diverjan. `critica`
 * se representa de forma distinguible de `baja`, `media` y `alta` (variante
 * `destructive` con una marca de anillo propia y `data-prioridad`).
 */
import { Badge } from '@/components/ui/badge';
import { formatearPrioridad } from '@/utils/formatters';

type VarianteBadge = 'destructive' | 'warning' | 'muted';

const VARIANTE_POR_PRIORIDAD: Record<string, VarianteBadge> = {
  critica: 'destructive',
  alta: 'destructive',
  media: 'warning',
  baja: 'muted',
};

/** Marca visual exclusiva de `critica` (la distingue de `alta`, tambien destructive). */
const CLASE_CRITICA = 'ring-2 ring-destructive/40 tracking-wide';

export function PrioridadBadge({ prioridad }: { prioridad: string }) {
  const esCritica = prioridad === 'critica';
  return (
    <Badge
      variant={VARIANTE_POR_PRIORIDAD[prioridad] ?? 'muted'}
      className={esCritica ? CLASE_CRITICA : undefined}
      data-prioridad={prioridad}
    >
      {formatearPrioridad(prioridad)}
    </Badge>
  );
}
