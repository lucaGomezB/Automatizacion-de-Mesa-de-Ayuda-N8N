/**
 * Acciones del ciclo de cierre en el detalle del incidente (c-86, D11 / FIH-002).
 *
 * Responsabilidad:
 *   Ofrece al operador las acciones de ciclo que su ROL habilita, derivadas del
 *   alcance y el rol expuestos por el backend:
 *     - `gestion_incidentes`: cerrar su sector y editar el estado no terminal.
 *     - `mesa_de_ayuda`: cerrar globalmente, reabrir y editar el estado.
 *   Un incidente en estado terminal solo admite reapertura (mesa de ayuda).
 *
 *   Es UX, NO el limite de seguridad (FIH-004): ante una respuesta del backend
 *   que deniegue la accion (403/404), se muestra el error sin presentarla como
 *   exitosa ni exponer el recurso.
 */
import { useState } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
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
import { useAuth } from '@/contexts/AuthContext';
import { useCicloIncidente } from '@/hooks/useCicloIncidente';
import { extractApiErrorMessage } from '@/services/api';
import { permisosCiclo, ESTADOS_EDITABLES, type EstadoEditable } from '@/utils/permisosCiclo';
import type { IncidenteRead } from '@/types/incidente';

interface AccionesCicloProps {
  /** Incidente completo (para conocer el estado terminal). */
  incidente: IncidenteRead;
  /** Callback tras una mutacion exitosa (p. ej. refrescar el detalle). */
  onMutated: () => void;
}

export function AccionesCiclo({ incidente, onMutated }: AccionesCicloProps) {
  const { rol } = useAuth();
  const permisos = permisosCiclo(rol);
  const [estadoSeleccionado, setEstadoSeleccionado] = useState<EstadoEditable | null>(null);

  const { cerrarSector, cerrarGlobal, reabrir, editarEstado } = useCicloIncidente(incidente.id);

  const terminal = incidente.estado.es_terminal;
  const mostrarCerrarSector = permisos.cerrarSector && !terminal;
  const mostrarCerrarGlobal = permisos.cerrarGlobal && !terminal;
  const mostrarReabrir = permisos.reabrir && terminal;
  const mostrarEditarEstado = permisos.editarEstado && !terminal;

  // Sin ninguna accion habilitada no se renderiza la seccion (menor ruido visual).
  if (!mostrarCerrarSector && !mostrarCerrarGlobal && !mostrarReabrir && !mostrarEditarEstado) {
    return null;
  }

  const error = cerrarSector.error ?? cerrarGlobal.error ?? reabrir.error ?? editarEstado.error;
  const pendiente =
    cerrarSector.isPending ||
    cerrarGlobal.isPending ||
    reabrir.isPending ||
    editarEstado.isPending;

  return (
    <div className="space-y-4">
      <Separator />
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Acciones de Ciclo
        </p>

        {/* Error de una accion denegada por el backend (403/404): sin exito asumido. */}
        {error != null && (
          <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
            <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span>{extractApiErrorMessage(error)}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {mostrarCerrarSector && (
            <Button
              variant="outline"
              size="sm"
              disabled={pendiente}
              onClick={() => cerrarSector.mutate(undefined, { onSuccess: onMutated })}
            >
              {cerrarSector.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
              Cerrar para mi sector
            </Button>
          )}

          {mostrarCerrarGlobal && (
            <Button
              variant="outline"
              size="sm"
              disabled={pendiente}
              onClick={() => cerrarGlobal.mutate(undefined, { onSuccess: onMutated })}
            >
              {cerrarGlobal.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
              Cerrar globalmente
            </Button>
          )}

          {mostrarReabrir && (
            <Button
              variant="outline"
              size="sm"
              disabled={pendiente}
              onClick={() => reabrir.mutate(undefined, { onSuccess: onMutated })}
            >
              {reabrir.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
              Reabrir incidente
            </Button>
          )}
        </div>

        {mostrarEditarEstado && (
          <div className="flex flex-wrap items-end gap-2">
            <div className="space-y-1">
              <Label htmlFor="estado-editable" className="text-xs text-muted-foreground">
                Estado
              </Label>
              <Select
                value={estadoSeleccionado ?? ''}
                onValueChange={(v) => setEstadoSeleccionado(v as EstadoEditable)}
              >
                <SelectTrigger id="estado-editable" className="h-9 w-44 text-sm">
                  <SelectValue placeholder="Seleccioná un estado" />
                </SelectTrigger>
                <SelectContent>
                  {ESTADOS_EDITABLES.map((estado) => (
                    <SelectItem key={estado.valor} value={estado.valor}>
                      {estado.etiqueta}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              size="sm"
              disabled={pendiente || estadoSeleccionado === null}
              onClick={() =>
                estadoSeleccionado !== null &&
                editarEstado.mutate(estadoSeleccionado, { onSuccess: onMutated })
              }
            >
              {editarEstado.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
              Actualizar estado
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}