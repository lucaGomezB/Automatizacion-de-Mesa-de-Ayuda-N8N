/**
 * Tabla principal de tickets del panel de administración.
 *
 * Responsabilidad:
 *   Renderiza la lista paginada de incidentes recibida del hook `useIncidentes`, usando la
 *   proyección ligera `IncidenteListItem` (sin campo `descripcion`) para minimizar el payload.
 *   La descripción completa se carga bajo demanda al abrir `TicketDetailDialog`.
 *
 *   Maneja los tres estados posibles de la consulta:
 *   - Cargando   → `LoadingSpinner`
 *   - Error      → `ErrorAlert` con botón de reintento
 *   - Sin datos  → `EmptyState`
 *   - Con datos  → tabla con filas clicables que disparan `onSelectIncidente`
 *
 * Componente auxiliar `PrioridadBadge`:
 *   Badge local que encapsula la lógica de color por nivel de prioridad para mantener
 *   la tabla limpia y separar presentación de datos.
 */
import { ExternalLink, RefreshCcw } from 'lucide-react';
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

interface TicketsTableProps {
  incidentes: IncidenteListItem[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  onSelectIncidente: (id: number) => void;
  onRefetch: () => void;
}

function PrioridadBadge({ prioridad }: { prioridad: string }) {
  const variant =
    prioridad === 'alta' ? 'destructive' : prioridad === 'media' ? 'warning' : 'muted';
  return <Badge variant={variant}>{formatearPrioridad(prioridad)}</Badge>;
}

export function TicketsTable({
  incidentes,
  isLoading,
  isError,
  error,
  onSelectIncidente,
  onRefetch,
}: TicketsTableProps) {
  if (isLoading) return <LoadingSpinner texto="Cargando tickets…" />;

  if (isError) {
    return (
      <ErrorAlert
        mensaje={extractApiErrorMessage(error)}
        onReintentar={onRefetch}
      />
    );
  }

  if (!incidentes || incidentes.length === 0) {
    return (
      <EmptyState
        titulo="Sin tickets"
        descripcion="No hay incidentes que coincidan con los filtros seleccionados."
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
            <TableHead className="text-center">Rev. Humana</TableHead>
            <TableHead>Fecha de Creación</TableHead>
            <TableHead className="w-16 text-right">
              <Button
                variant="ghost"
                size="icon"
                onClick={onRefetch}
                title="Actualizar lista"
                className="h-7 w-7"
              >
                <RefreshCcw className="h-3.5 w-3.5" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {incidentes.map((incidente) => (
            <TableRow
              key={incidente.id}
              className="cursor-pointer"
              onClick={() => onSelectIncidente(incidente.id)}
            >
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
                <EstadoBadge nombre={incidente.estado.nombre} />
              </TableCell>
              <TableCell className="text-center">
                {incidente.requiere_revision_humana ? (
                  <span className="inline-block h-2.5 w-2.5 rounded-full bg-amber-500" title="Revisión pendiente" />
                ) : (
                  <span className="inline-block h-2.5 w-2.5 rounded-full bg-green-400" title="Clasificado con alta confianza" />
                )}
              </TableCell>
              <TableCell className="text-muted-foreground text-xs tabular-nums">
                {formatearFecha(incidente.created_at)}
              </TableCell>
              <TableCell className="text-right">
                <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
