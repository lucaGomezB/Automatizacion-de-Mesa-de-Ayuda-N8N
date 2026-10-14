/**
 * Diálogo de detalle completo de un incidente.
 * Realiza dos consultas en paralelo:
 *   1. GET /api/v1/incidentes/{id}           → datos completos incluida la descripción
 *   2. GET /api/v1/clasificaciones/incidente/{id} → historial de clasificación del pipeline
 *
 * La separación en dos queries independientes permite mostrar la información disponible
 * progresivamente, sin bloquear el renderizado por la query más lenta.
 *
 * c-83 (D1/D2): la presentación del detalle se delega al componente compartido
 * `DetalleIncidente` (solo lectura), que también usa la validación humana, para no
 * duplicar la vista rica ni divergir entre ambas superficies (FRH-004).
 */
import { useQuery } from '@tanstack/react-query';
import { Hash } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { DetalleIncidente } from './DetalleIncidente';
import { AccionesCiclo } from './AccionesCiclo';
import { ComentariosIncidente } from './ComentariosIncidente';
import { extractApiErrorMessage } from '@/services/api';
import { obtenerIncidente } from '@/services/incidentesService';
import { listarClasificacionesPorIncidente } from '@/services/clasificacionesService';

interface TicketDetailDialogProps {
  open: boolean;
  incidenteId: number | null;
  onClose: () => void;
}

export function TicketDetailDialog({ open, incidenteId, onClose }: TicketDetailDialogProps) {
  const habilitado = open && incidenteId !== null;

  const {
    data: incidente,
    isLoading: cargandoIncidente,
    isError: errorIncidente,
    error: errorIncidenteObj,
    refetch: refetchIncidente,
  } = useQuery({
    queryKey: ['incidente-detalle', incidenteId],
    queryFn: () => obtenerIncidente(incidenteId!),
    enabled: habilitado,
    staleTime: 30_000,
  });

  const { data: clasificaciones, isLoading: cargandoClasif } = useQuery({
    queryKey: ['clasificaciones-historial', incidenteId],
    queryFn: () => listarClasificacionesPorIncidente(incidenteId!),
    enabled: habilitado,
    staleTime: 30_000,
  });

  const clasificacionPrincipal = clasificaciones?.[0] ?? null;
  const cargando = cargandoIncidente || cargandoClasif;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5 text-primary" />
            {incidente
              ? `Incidente #${incidente.id.toString().padStart(5, '0')}`
              : 'Detalle de Incidente'}
          </DialogTitle>
          <DialogDescription>
            Información completa del ticket y resultado de la clasificación automática.
          </DialogDescription>
        </DialogHeader>

        {/* Estado de carga */}
        {cargando && <LoadingSpinner texto="Cargando información del incidente…" />}

        {/* Error de carga */}
        {errorIncidente && (
          <ErrorAlert
            mensaje={extractApiErrorMessage(errorIncidenteObj)}
            onReintentar={() => void refetchIncidente()}
          />
        )}

        {/* Contenido del incidente (vista compartida de solo lectura) */}
        {incidente && (
          <>
            <DetalleIncidente incidente={incidente} clasificacion={clasificacionPrincipal} />

            {/* Acciones del ciclo de cierre segun el rol (c-86, D11).
                El backend sigue siendo el limite de seguridad (FIH-004). */}
            <AccionesCiclo
              incidente={incidente}
              onMutated={() => void refetchIncidente()}
            />

            {/* Comentarios append-only del incidente (c-86, FIH-003) */}
            <ComentariosIncidente incidenteId={incidente.id} />
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
