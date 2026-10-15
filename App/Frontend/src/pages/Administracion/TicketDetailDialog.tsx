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
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertCircle, Hash, Loader2, Trash2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { DetalleIncidente } from './DetalleIncidente';
import { AccionesCiclo } from './AccionesCiclo';
import { ComentariosIncidente } from './ComentariosIncidente';
import { useAuth } from '@/contexts/AuthContext';
import { useBorradoIncidente } from '@/hooks/useBorradoIncidente';
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

  // Accion de borrado logico (c-87, FR-RBAC-006): solo visible/ejecutable para
  // el rol administrador del directorio. El backend sigue siendo el limite de
  // seguridad (403/404 se manejan sin asumir exito ni exponer el recurso).
  const { rol } = useAuth();
  const esAdmin = rol === 'administrador_directorio';
  const [confirmandoBorrado, setConfirmandoBorrado] = useState(false);
  const borrado = useBorradoIncidente(incidenteId ?? 0);

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

            {/* Zona de administracion: borrado logico exclusivo del administrador
                del directorio, con confirmacion (c-87, FR-RBAC-006). */}
            {esAdmin && (
              <div className="space-y-3">
                <Separator />
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Zona de administración
                </p>

                {/* Denegacion del backend (403/404): estado de error sin asumir exito. */}
                {borrado.error != null && (
                  <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>{extractApiErrorMessage(borrado.error)}</span>
                  </div>
                )}

                {!confirmandoBorrado ? (
                  <Button
                    variant="destructive"
                    size="sm"
                    disabled={borrado.isPending}
                    onClick={() => setConfirmandoBorrado(true)}
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-1" />
                    Eliminar incidente
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      ¿Confirmás el borrado lógico del incidente? Se retirará de todas las
                      vistas.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={borrado.isPending}
                        onClick={() => setConfirmandoBorrado(false)}
                      >
                        Cancelar
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={borrado.isPending}
                        onClick={() =>
                          borrado.mutate(undefined, { onSuccess: () => onClose() })
                        }
                      >
                        {borrado.isPending && (
                          <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
                        )}
                        Confirmar borrado
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
