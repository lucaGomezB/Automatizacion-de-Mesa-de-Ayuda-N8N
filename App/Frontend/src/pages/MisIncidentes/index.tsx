/**
 * Vista "Mis incidentes" — ruta "/mis-incidentes" (c-81, D5).
 *
 * Responsabilidad:
 *   Presenta al `usuario_final` (alcance PROPIO) la lista de SUS incidentes.
 *   Reutiliza el endpoint EXISTENTE `GET /api/v1/incidentes/`: el backend ya
 *   acota el alcance PROPIO (`reportante_empleado_id`), por lo que NO se
 *   introduce superficie de API nueva NI se reconstruyen datos en el cliente.
 *   Es UX, no seguridad: el backend sigue siendo la fuente de verdad.
 */
import { PageWrapper } from '@/components/layout/PageWrapper';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { EstadoBadge } from '@/components/shared/EstadoBadge';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { useIncidentes } from '@/hooks/useIncidentes';
import { extractApiErrorMessage } from '@/services/api';
import { formatearFecha, formatearPrioridad } from '@/utils/formatters';

/** Badge de prioridad acotado a la vista de incidentes propios. */
function PrioridadBadge({ prioridad }: { prioridad: string }) {
  const variant =
    prioridad === 'alta' ? 'destructive' : prioridad === 'media' ? 'warning' : 'muted';
  return <Badge variant={variant}>{formatearPrioridad(prioridad)}</Badge>;
}

export default function MisIncidentesPage() {
  // Sin parametros: el backend decide que incidentes son visibles (alcance PROPIO).
  const { data, isLoading, isError, error, refetch } = useIncidentes({});

  return (
    <PageWrapper>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-primary">Mis incidentes</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Los incidentes que reportaste. El listado lo determina el sistema según tu alcance.
          </p>
        </div>

        {isLoading ? (
          <LoadingSpinner texto="Cargando tus incidentes…" />
        ) : isError ? (
          <ErrorAlert
            mensaje={extractApiErrorMessage(error)}
            onReintentar={() => void refetch()}
          />
        ) : !data || data.length === 0 ? (
          <EmptyState
            titulo="No tenés incidentes"
            descripcion="Todavía no reportaste ningún incidente. Usá el portal para crear uno."
          />
        ) : (
          <div className="rounded-md border overflow-hidden">
            <Table>
              <TableHeader className="bg-muted/50">
                <TableRow>
                  <TableHead className="w-20">ID</TableHead>
                  <TableHead>Sector</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Fecha de Creación</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((incidente) => (
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
                      <EstadoBadge nombre={incidente.estado.nombre} />
                    </TableCell>
                    <TableCell className="text-muted-foreground text-xs tabular-nums">
                      {formatearFecha(incidente.created_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
