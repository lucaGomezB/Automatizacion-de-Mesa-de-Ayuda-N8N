/**
 * Diálogo de validación humana para clasificaciones de baja confianza.
 *
 * Responsabilidad:
 *   Permite al operador revisar TODA la información disponible del incidente y su
 *   clasificación antes de decidir el sector correcto. Consulta el detalle del
 *   incidente y su historial de clasificaciones (mismas query keys que
 *   `TicketDetailDialog`) y los presenta con el componente compartido
 *   `DetalleIncidente` (solo lectura). Invoca PATCH /api/v1/clasificaciones/{id}/validar
 *   y, ante éxito, invalida las cachés de `revision-pendiente` e `incidentes` para que
 *   ambas listas reflejen el cambio sin necesidad de recargar la página.
 *
 * Flujo de estado interno:
 *   - Al abrirse (`open=true`), pre-selecciona el sector predicho como valor por defecto
 *     para que la confirmación sin corrección sea el camino de menor fricción.
 *   - Muestra un mensaje contextual diferenciando "confirmación" de "corrección",
 *     ya que las correcciones alimentan el corpus de evaluación del modelo.
 *   - `resetMutation()` al abrir asegura que errores de intentos previos no persistan.
 *   - c-165 (ASG-005): al abrirse toma el instante de INICIO de la intervencion y lo envia
 *     al confirmar como `intervencion_inicio_en`. El dialogo NUNCA envia
 *     `origen_intervencion`: el backend lo deriva (gate o muestreo segun el log).
 */
import { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCheck, Loader2, AlertCircle, User } from 'lucide-react';
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
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { DetalleIncidente } from './DetalleIncidente';
import { validarClasificacion, listarClasificacionesPorIncidente } from '@/services/clasificacionesService';
import { obtenerIncidente } from '@/services/incidentesService';
import { extractApiErrorMessage } from '@/services/api';
import { useSectores } from '@/hooks/useSectores';
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
  // c-83 (D5): el conjunto multi-etiqueta se edita por NOMBRES CANONICOS, un unico
  // esquema de identificador para principal y adicionales.
  const [sectorPrincipalNombre, setSectorPrincipalNombre] = useState<string>('');
  const [sectoresAdicionales, setSectoresAdicionales] = useState<string[]>([]);
  // c-165 (ASG-005): instante (ISO-8601 UTC) en que el operador abrio el dialogo para este
  // log. Es un dato de auditoria que no se renderiza: va en una ref, no en estado.
  const inicioIntervencionRef = useRef<string | null>(null);
  // Opciones de sector obtenidas en runtime desde el catálogo (sin IDs numéricos fijos)
  const { data: sectores } = useSectores();

  const incidenteId = clasificacion?.incidente_id ?? null;
  const habilitado = open && incidenteId !== null;
  const clasificacionId = clasificacion?.id ?? null;

  // El inicio se fija cuando el dialogo SE ABRE (o pasa a mostrar otro log), no al
  // confirmar ni cuando la lista refresca el mismo log con otra identidad de objeto.
  useEffect(() => {
    inicioIntervencionRef.current =
      open && clasificacionId !== null ? new Date().toISOString() : null;
  }, [open, clasificacionId]);

  // Detalle del incidente — misma query key que TicketDetailDialog (cache compartida)
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

  // Historial de clasificaciones del incidente — misma query key que TicketDetailDialog
  const { data: clasificaciones, isLoading: cargandoClasif } = useQuery({
    queryKey: ['clasificaciones-historial', incidenteId],
    queryFn: () => listarClasificacionesPorIncidente(incidenteId!),
    enabled: habilitado,
    staleTime: 30_000,
  });

  const clasificacionMostrada = clasificaciones?.[0] ?? clasificacion;
  // Estado de carga compuesto (FRH-005): la vista espera a que AMBAS consultas resuelvan
  // para no mostrar datos parciales.
  const cargando = cargandoIncidente || cargandoClasif;

  const { mutate, isPending, error, reset: resetMutation } = useMutation({
    mutationFn: ({
      logId,
      sectorValidado,
      sectoresAdicionales: adicionales,
      intervencionInicioEn,
    }: {
      logId: number;
      sectorValidado: string;
      sectoresAdicionales: string[];
      intervencionInicioEn: string | null;
    }) =>
      validarClasificacion(logId, {
        sector_validado: sectorValidado,
        sectores_adicionales: adicionales,
        // c-165: unico dato de la intervencion que declara el cliente. NO se envia
        // `origen_intervencion` (lo deriva el backend y un payload que lo traiga da 422).
        ...(intervencionInicioEn ? { intervencion_inicio_en: intervencionInicioEn } : {}),
      }),
    onSuccess: (clasificacionActualizada) => {
      // Invalida la cola de revisión y la lista de incidentes para reflejar el cambio
      void queryClient.invalidateQueries({ queryKey: [REVISION_PENDIENTE_QUERY_KEY] });
      void queryClient.invalidateQueries({ queryKey: [INCIDENTES_QUERY_KEY] });
      // Invalida el detalle del incidente afectado para que muestre la validación
      // recién guardada al reabrir el diálogo (FE 3)
      void queryClient.invalidateQueries({
        queryKey: ['incidente-detalle', clasificacionActualizada.incidente_id],
      });
      // Invalida el historial de clasificaciones del incidente (incluye el sector validado)
      void queryClient.invalidateQueries({
        queryKey: ['clasificaciones-historial', clasificacionActualizada.incidente_id],
      });
      onClose();
    },
  });

  // Reiniciar estado interno cada vez que el diálogo se abre o cambia la clasificación
  useEffect(() => {
    if (open && clasificacion) {
      // Pre-seleccionar el sector predicho como valor por defecto
      const principal = clasificacion.sector_predicho?.nombre ?? '';
      setSectorPrincipalNombre(principal);
      // Pre-seleccionar los adicionales predichos, sin repetir el principal (FRH-006)
      setSectoresAdicionales(
        (clasificacion.sectores_predichos ?? [])
          .map((sector) => sector.nombre)
          .filter((nombre) => nombre !== principal)
      );
      resetMutation();
    }
  }, [open, clasificacion, resetMutation]);

  /** Cambia el sector principal y elimina cualquier duplicado del conjunto adicional (FRH-006). */
  const handlePrincipalChange = (nombre: string) => {
    setSectorPrincipalNombre(nombre);
    setSectoresAdicionales((prev) => prev.filter((n) => n !== nombre));
  };

  /** Agrega o quita un sector adicional del conjunto editable (FRH-006). */
  const toggleAdicional = (nombre: string) => {
    setSectoresAdicionales((prev) =>
      prev.includes(nombre) ? prev.filter((n) => n !== nombre) : [...prev, nombre]
    );
  };

  const handleValidar = () => {
    if (!clasificacion || !sectorPrincipalNombre) return;
    mutate({
      logId: clasificacion.id,
      sectorValidado: sectorPrincipalNombre,
      sectoresAdicionales,
      intervencionInicioEn: inicioIntervencionRef.current,
    });
  };

  const sectorPredicho = clasificacion?.sector_predicho;
  const esConfirmacion = sectorPrincipalNombre === sectorPredicho?.nombre;
  // Las opciones adicionales EXCLUYEN el principal elegido (FRH-006).
  const opcionesAdicionales = (sectores ?? []).filter(
    (sector) => sector.nombre !== sectorPrincipalNombre
  );

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
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
          {/* Estado de carga compuesto: no se muestran datos parciales (FRH-005) */}
          {cargando && <LoadingSpinner texto="Cargando información del incidente…" />}

          {/* Error de carga del recurso (403/404): no se renderiza el recurso (FRH-005) */}
          {!cargando && errorIncidente && (
            <ErrorAlert
              mensaje={extractApiErrorMessage(errorIncidenteObj)}
              onReintentar={() => void refetchIncidente()}
            />
          )}

          {/* Información completa del incidente y su clasificación (solo lectura) */}
          {!cargando && !errorIncidente && incidente && (
            <DetalleIncidente incidente={incidente} clasificacion={clasificacionMostrada} />
          )}

          {/* Controles de validación — solo cuando el detalle está disponible */}
          {!cargando && !errorIncidente && (
            <>
              <Separator />

              {/* Selector de sector correcto */}
              <div className="space-y-2">
                <Label htmlFor="sector-validado">
                  Sector correcto según tu criterio{' '}
                  <span className="text-destructive">*</span>
                </Label>
                <Select value={sectorPrincipalNombre} onValueChange={handlePrincipalChange}>
                  <SelectTrigger id="sector-validado">
                    <SelectValue placeholder="Seleccioná el sector correcto" />
                  </SelectTrigger>
                  <SelectContent>
                    {sectores?.map((sector) => (
                      <SelectItem key={sector.id} value={sector.nombre}>
                        {sector.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {sectorPrincipalNombre && (
                  <p
                    className={`text-xs ${esConfirmacion ? 'text-green-600' : 'text-amber-600'}`}
                  >
                    {esConfirmacion
                      ? '✓ Confirmás la predicción del clasificador.'
                      : `✎ Estás corrigiendo: "${sectorPredicho?.nombre ?? 'Sin clasificar'}" → "${sectorPrincipalNombre}". Este dato alimentará el corpus de evaluación.`}
                  </p>
                )}
              </div>

              {/* Multi-select de sectores adicionales (FRH-006): el conjunto completo es editable */}
              <div className="space-y-2" role="group" aria-label="Sectores adicionales">
                <span className="text-sm font-medium leading-none">
                  Sectores adicionales (opcional)
                </span>
                <div className="flex flex-wrap gap-2">
                  {opcionesAdicionales.map((sector) => {
                    const seleccionado = sectoresAdicionales.includes(sector.nombre);
                    return (
                      <Button
                        key={sector.id}
                        type="button"
                        variant={seleccionado ? 'default' : 'outline'}
                        size="sm"
                        aria-pressed={seleccionado}
                        onClick={() => toggleAdicional(sector.nombre)}
                      >
                        {sector.nombre}
                      </Button>
                    );
                  })}
                </div>
              </div>

              {/* Error de API */}
              {error && (
                <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{extractApiErrorMessage(error)}</span>
                </div>
              )}
            </>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose} disabled={isPending}>
            Cancelar
          </Button>
          {!errorIncidente && (
            <Button onClick={handleValidar} disabled={isPending || !sectorPrincipalNombre}>
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
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
