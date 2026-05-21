/**
 * Diálogo de detalle completo de un incidente.
 * Realiza dos consultas en paralelo:
 *   1. GET /api/v1/incidentes/{id}           → datos completos incluida la descripción
 *   2. GET /api/v1/clasificaciones/incidente/{id} → historial de clasificación del pipeline
 *
 * La separación en dos queries independientes permite mostrar la información disponible
 * progresivamente, sin bloquear el renderizado por la query más lenta.
 */
import type { ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Hash,
  Calendar,
  Mail,
  FileText,
  Brain,
  AlertTriangle,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { EstadoBadge } from '@/components/shared/EstadoBadge';
import { ConfianzaIndicator } from '@/components/shared/ConfianzaIndicator';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { formatearFecha, formatearPrioridad, formatearEtapa } from '@/utils/formatters';
import { extractApiErrorMessage } from '@/services/api';
import { obtenerIncidente } from '@/services/incidentesService';
import { listarClasificacionesPorIncidente } from '@/services/clasificacionesService';

interface TicketDetailDialogProps {
  open: boolean;
  incidenteId: number | null;
  onClose: () => void;
}

/**
 * Componente interno reutilizable para presentación clave-valor de campos de detalle.
 * Cada instancia muestra un ícono, una etiqueta descriptiva y el valor correspondiente.
 */
function CampoDetalle({
  icono,
  etiqueta,
  children,
}: {
  icono: ReactNode;
  etiqueta: string;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {icono}
        {etiqueta}
      </div>
      <div className="text-sm">{children}</div>
    </div>
  );
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

  const clasificacionPrincipal = clasificaciones?.[0];
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

        {/* Contenido del incidente */}
        {incidente && (
          <div className="space-y-5">
            {/* Indicador de revisión pendiente */}
            {incidente.requiere_revision_humana && (
              <div className="flex items-center gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded-md text-amber-800 text-sm">
                <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-600" />
                Este incidente requiere revisión humana (confianza insuficiente).
              </div>
            )}

            {/* Grilla de metadatos principales */}
            <div className="grid grid-cols-2 gap-4">
              <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Estado">
                <EstadoBadge nombre={incidente.estado.nombre} />
              </CampoDetalle>

              <CampoDetalle icono={<Brain className="h-3.5 w-3.5" />} etiqueta="Sector Asignado">
                <SectorBadge nombre={incidente.sector?.nombre} />
              </CampoDetalle>

              <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Prioridad">
                <Badge
                  variant={
                    incidente.prioridad === 'alta'
                      ? 'destructive'
                      : incidente.prioridad === 'media'
                      ? 'warning'
                      : 'muted'
                  }
                >
                  {formatearPrioridad(incidente.prioridad)}
                </Badge>
              </CampoDetalle>

              <CampoDetalle icono={<Mail className="h-3.5 w-3.5" />} etiqueta="Canal de Origen">
                <span className="capitalize">
                  {incidente.canal_origen?.nombre ?? 'Desconocido'}
                </span>
              </CampoDetalle>

              <CampoDetalle icono={<Calendar className="h-3.5 w-3.5" />} etiqueta="Creado">
                {formatearFecha(incidente.created_at)}
              </CampoDetalle>

              <CampoDetalle icono={<Calendar className="h-3.5 w-3.5" />} etiqueta="Última actualización">
                {formatearFecha(incidente.updated_at)}
              </CampoDetalle>
            </div>

            <Separator />

            {/* Descripción completa del incidente */}
            <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Descripción">
              <p className="text-sm leading-relaxed whitespace-pre-wrap bg-muted/40 rounded-md p-3 border">
                {incidente.descripcion}
              </p>
            </CampoDetalle>

            {/* Resultado de clasificación */}
            {clasificacionPrincipal && (
              <>
                <Separator />
                <div className="space-y-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-1.5">
                    <Brain className="h-3.5 w-3.5" />
                    Clasificación Automática
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <CampoDetalle icono={null} etiqueta="Confianza">
                      <ConfianzaIndicator confianza={clasificacionPrincipal.confianza} />
                    </CampoDetalle>
                    <CampoDetalle icono={null} etiqueta="Etapa del Pipeline">
                      <span className="text-sm">{formatearEtapa(clasificacionPrincipal.etapa)}</span>
                    </CampoDetalle>
                    {clasificacionPrincipal.sector_validado && (
                      <CampoDetalle icono={null} etiqueta="Sector Validado por Operador">
                        <SectorBadge nombre={clasificacionPrincipal.sector_validado.nombre} />
                      </CampoDetalle>
                    )}
                  </div>

                  {/* Respuesta raw de Gemini (solo si la etapa fue gemini) */}
                  {clasificacionPrincipal.respuesta_raw && (
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Respuesta raw de Gemini
                      </p>
                      <pre className="text-xs bg-slate-900 text-green-400 rounded-md p-3 overflow-x-auto">
                        {clasificacionPrincipal.respuesta_raw}
                      </pre>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
