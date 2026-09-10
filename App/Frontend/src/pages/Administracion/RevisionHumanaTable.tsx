/**
 * Tabla de la cola de revisión humana del panel de administración.
 *
 * Responsabilidad:
 *   Presenta las clasificaciones cuya confianza fue inferior al umbral de 0.70 definido
 *   en `parameters_gemini.md`. El operador puede verificar la predicción de Gemini y,
 *   mediante el botón "Validar", abrir `ValidarClasificacionDialog` para confirmar o
 *   corregir el sector asignado.
 *
 *   Una vez validado un registro (`sector_validado !== null`), el botón se reemplaza por
 *   el texto "✓ Validado" para evitar doble validación sobre la misma clasificación.
 *
 *   El estado vacío con ícono verde comunica al operador que la cola está despejada,
 *   diferenciándolo del estado de error para que no se confunda con un fallo de carga.
 */
import { ClipboardCheck, RefreshCcw } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { ConfianzaIndicator } from '@/components/shared/ConfianzaIndicator';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { formatearFecha, formatearEtapa } from '@/utils/formatters';
import { extractApiErrorMessage } from '@/services/api';
import type { ClasificacionLogRead } from '@/types/clasificacion';

interface RevisionHumanaTableProps {
  clasificaciones: ClasificacionLogRead[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  onValidar: (clasificacion: ClasificacionLogRead) => void;
  onRefetch: () => void;
}

export function RevisionHumanaTable({
  clasificaciones,
  isLoading,
  isError,
  error,
  onValidar,
  onRefetch,
}: RevisionHumanaTableProps) {
  if (isLoading) return <LoadingSpinner texto="Cargando cola de revisión…" />;

  if (isError) {
    return (
      <ErrorAlert
        mensaje={extractApiErrorMessage(error)}
        onReintentar={onRefetch}
      />
    );
  }

  if (!clasificaciones || clasificaciones.length === 0) {
    return (
      <EmptyState
        titulo="Cola vacía"
        descripcion="No hay clasificaciones pendientes de revisión humana. Todos los incidentes fueron clasificados con confianza suficiente."
        icon={<ClipboardCheck className="h-8 w-8 text-green-500/60" />}
      />
    );
  }

  return (
    <div className="rounded-md border overflow-hidden">
      <Table>
        <TableHeader className="bg-muted/50">
          <TableRow>
            <TableHead className="w-28">ID Incidente</TableHead>
            <TableHead>Sector Predicho</TableHead>
            <TableHead>Sector Validado</TableHead>
            <TableHead>Confianza</TableHead>
            <TableHead>Etapa del Pipeline</TableHead>
            <TableHead>Fecha de Clasificación</TableHead>
            <TableHead className="text-right">
              <Button
                variant="ghost"
                size="icon"
                onClick={onRefetch}
                title="Actualizar cola"
                className="h-7 w-7"
              >
                <RefreshCcw className="h-3.5 w-3.5" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {clasificaciones.map((clf) => (
            <TableRow key={clf.id}>
              <TableCell className="font-mono font-medium text-primary">
                #{clf.incidente_id.toString().padStart(5, '0')}
              </TableCell>
              <TableCell>
                <SectorBadge nombre={clf.sector_predicho?.nombre} />
              </TableCell>
              <TableCell>
                {clf.sector_validado ? (
                  <SectorBadge nombre={clf.sector_validado.nombre} />
                ) : (
                  <span className="text-xs text-muted-foreground italic">Sin validar</span>
                )}
              </TableCell>
              <TableCell>
                <ConfianzaIndicator confianza={clf.confianza} size="sm" showLabel />
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatearEtapa(clf.etapa)}
              </TableCell>
              <TableCell className="text-xs text-muted-foreground tabular-nums">
                {formatearFecha(clf.created_at)}
              </TableCell>
              <TableCell className="text-right">
                {/* Solo mostrar botón si aún no fue validado */}
                {!clf.sector_validado ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onValidar(clf)}
                    className="text-xs h-8"
                  >
                    <ClipboardCheck className="h-3.5 w-3.5 mr-1" />
                    Validar
                  </Button>
                ) : (
                  <span className="text-xs text-green-600 font-medium">✓ Validado</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
