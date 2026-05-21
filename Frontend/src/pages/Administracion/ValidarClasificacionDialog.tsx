/**
 * Diálogo de validación humana para clasificaciones de baja confianza.
 *
 * Responsabilidad:
 *   Permite al operador revisar la predicción del pipeline (sector y confianza) y
 *   seleccionar el sector correcto antes de confirmar. Invoca PATCH /api/v1/clasificaciones/{id}/validar
 *   y, ante éxito, invalida las cachés de `revision-pendiente` e `incidentes` para que
 *   ambas listas reflejen el cambio sin necesidad de recargar la página.
 *
 * Flujo de estado interno:
 *   - Al abrirse (`open=true`), pre-selecciona el sector predicho como valor por defecto
 *     para que la confirmación sin corrección sea el camino de menor fricción.
 *   - Muestra un mensaje contextual diferenciando "confirmación" de "corrección",
 *     ya que las correcciones alimentan el corpus de evaluación del modelo.
 *   - `resetMutation()` al abrir asegura que errores de intentos previos no persistan.
 */
import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCheck, Loader2, AlertCircle, Brain, User } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { ConfianzaIndicator } from '@/components/shared/ConfianzaIndicator';
import { validarClasificacion } from '@/services/clasificacionesService';
import { extractApiErrorMessage } from '@/services/api';
import { SECTORES_OPCIONES } from '@/types/catalog';
import { REVISION_PENDIENTE_QUERY_KEY } from '@/hooks/useRevisionPendiente';
import { INCIDENTES_QUERY_KEY } from '@/hooks/useIncidentes';
import type { ClasificacionLogRead } from '@/types/clasificacion';

interface ValidarClasificacionDialogProps {
  open: boolean;
  clasificacion: ClasificacionLogRead | null;
  onClose: () => void;
}

export function ValidarClasificacionDialog({
  open,
  clasificacion,
  onClose,
}: ValidarClasificacionDialogProps) {
  const queryClient = useQueryClient();
  const [sectorIdSeleccionado, setSectorIdSeleccionado] = useState<string>('');

  const { mutate, isPending, error, reset: resetMutation } = useMutation({
    mutationFn: ({ logId, sectorId }: { logId: number; sectorId: number }) =>
      validarClasificacion(logId, { sector_id_validado: sectorId }),
    onSuccess: () => {
      // Invalida la cola de revisión y la lista de incidentes para reflejar el cambio
      void queryClient.invalidateQueries({ queryKey: [REVISION_PENDIENTE_QUERY_KEY] });
      void queryClient.invalidateQueries({ queryKey: [INCIDENTES_QUERY_KEY] });
      onClose();
    },
  });

  // Reiniciar estado interno cada vez que el diálogo se abre o cambia la clasificación
  useEffect(() => {
    if (open && clasificacion) {
      // Pre-seleccionar el sector predicho como valor por defecto
      setSectorIdSeleccionado(
        clasificacion.sector_predicho?.id.toString() ?? ''
      );
      resetMutation();
    }
  }, [open, clasificacion, resetMutation]);

  const handleValidar = () => {
    if (!clasificacion || !sectorIdSeleccionado) return;
    mutate({ logId: clasificacion.id, sectorId: Number(sectorIdSeleccionado) });
  };

  const sectorPredicho = clasificacion?.sector_predicho;
  const sectorSeleccionadoNombre = SECTORES_OPCIONES.find(
    (s) => s.id.toString() === sectorIdSeleccionado
  )?.nombre;

  const esConfirmacion = sectorSeleccionadoNombre === sectorPredicho?.nombre;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            Validación Humana
          </DialogTitle>
          <DialogDescription>
            Incidente #{clasificacion?.incidente_id} · Confirmá o corregí el sector asignado por
            el clasificador automático.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-1">
          {/* Predicción del modelo */}
          <div className="bg-muted/50 rounded-md p-3 space-y-2.5">
            <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wide">
              <Brain className="h-3.5 w-3.5" />
              Predicción del clasificador
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <SectorBadge nombre={sectorPredicho?.nombre} />
              {clasificacion && (
                <ConfianzaIndicator confianza={clasificacion.confianza} size="sm" />
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Etapa:{' '}
              {clasificacion?.etapa === 'deterministic'
                ? 'Determinístico'
                : clasificacion?.etapa === 'gemini'
                ? 'Gemini 2.5 Flash'
                : 'Sin clasificar'}
            </p>
          </div>

          <Separator />

          {/* Selector de sector correcto */}
          <div className="space-y-2">
            <Label htmlFor="sector-validado">
              Sector correcto según tu criterio{' '}
              <span className="text-destructive">*</span>
            </Label>
            <Select value={sectorIdSeleccionado} onValueChange={setSectorIdSeleccionado}>
              <SelectTrigger id="sector-validado">
                <SelectValue placeholder="Seleccioná el sector correcto" />
              </SelectTrigger>
              <SelectContent>
                {SECTORES_OPCIONES.map((sector) => (
                  <SelectItem key={sector.id} value={sector.id.toString()}>
                    {sector.nombre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {sectorIdSeleccionado && (
              <p className={`text-xs ${esConfirmacion ? 'text-green-600' : 'text-amber-600'}`}>
                {esConfirmacion
                  ? '✓ Confirmás la predicción del clasificador.'
                  : `✎ Estás corrigiendo: "${sectorPredicho?.nombre ?? 'Sin clasificar'}" → "${sectorSeleccionadoNombre}". Este dato alimentará el corpus de evaluación.`}
              </p>
            )}
          </div>

          {/* Error de API */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{extractApiErrorMessage(error)}</span>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose} disabled={isPending}>
            Cancelar
          </Button>
          <Button
            onClick={handleValidar}
            disabled={isPending || !sectorIdSeleccionado}
          >
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Guardando…
              </>
            ) : (
              <>
                <CheckCheck className="h-4 w-4" />
                {esConfirmacion ? 'Confirmar predicción' : 'Guardar corrección'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
