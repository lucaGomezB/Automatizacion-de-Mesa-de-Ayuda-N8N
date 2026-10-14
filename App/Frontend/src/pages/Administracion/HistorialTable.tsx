/**
 * Tabla del historial de incidentes cerrados (c-86, FIH-001 / D10).
 *
 * Responsabilidad:
 *   Presenta la lista de incidentes cerrados que el backend devuelve para el
 *   alcance del usuario (GLOBAL, SECTOR o PROPIO). El conjunto visible lo
 *   determina EXCLUSIVAMENTE el backend; la tabla no acota ni amplía datos por
 *   su cuenta (FIH-004).
 *
 *   El estado se presenta SIEMPRE como "Cerrado": un `gestion_incidentes` ve
 *   incidentes cerrados solo para su sector aunque no estén globalmente cerrados
 *   (D10), por lo que se normaliza la etiqueta mostrada.
 */
import { RefreshCcw } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { EstadoBadge } from '@/components/shared/EstadoBadge';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { formatearFecha, formatearPrioridad } from '@/utils/formatters';
import { extractApiErrorMessage } from '@/services/api';
import type { IncidenteListItem } from '@/types/incidente';

interface HistorialTableProps {
  incidentes: IncidenteListItem[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  onRefetch: () => void;
}

function PrioridadBadge({ prioridad }: { prioridad: string }) {
  const variant =
    prioridad === 'alta' ? 'destructive' : prioridad === 'media' ? 'warning' : 'muted';
  return <Badge variant={variant}>{formatearPrioridad(prioridad)}</Badge>;
}

/** Etiqueta canonica del estado en el historial (D10). */
export const ESTADO_HISTORIAL = 'Cerrado';

export function HistorialTable({
  incidentes,
  isLoading,
  isError,
  error,
  onRefetch,
}: HistorialTableProps) {
  if (isLoading) return <LoadingSpinner texto="Cargando historial de cerrados…" />;

  if (isError) {
    return <ErrorAlert mensaje={extractApiErrorMessage(error)} onReintentar={onRefetch} />;
  }

  if (!incidentes || incidentes.length === 0) {
    return (
      <EmptyState
        titulo="Sin incidentes cerrados"
        descripcion="No hay incidentes cerrados en tu alcance por el momento."
      />
    );
  }

  return (
    <div className="rounded-md border overflow-hidden">
      <Table>
        <TableHeader className="bg-muted/50">
          <TableRow>
            <TableHead className="w-20">ID</TableHead>
            <TableHead>Sector Asignado</TableHead>
            <TableHead>Prioridad</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Fecha de Creación</TableHead>
            <TableHead className="w-16 text-right">
              <Button
                variant="ghost"
                size="icon"
                onClick={onRefetch}
                title="Actualizar historial"
                className="h-7 w-7"
              >
                <RefreshCcw className="h-3.5 w-3.5" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {incidentes.map((incidente) => (
            <TableRow key={incidente.id}>
              <TableCell className="font-mono font-medium text-primary">
                #{incidente.id.toString().padStart(5, '0')}
              </TableCell>
              <TableCell>
                <SectorBadge nombre={incidente.sector?.nombre} />
              </TableCell>
              <TableCell>
                <PrioridadBadge prioridad={incidente.prioridad} />
              </TableCell>
              <TableCell>
                {/* El historial normaliza el estado mostrado a "Cerrado" (D10). */}
                <EstadoBadge nombre={ESTADO_HISTORIAL} />
              </TableCell>
              <TableCell className="text-muted-foreground text-xs tabular-nums">
                {formatearFecha(incidente.created_at)}
              </TableCell>
              <TableCell />
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}