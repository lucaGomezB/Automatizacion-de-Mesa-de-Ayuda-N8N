/**
 * Control de asignacion de prioridad en el detalle del incidente (c-90, FR-RBAC-009).
 *
 * Responsabilidad:
 *   Ofrece un boton por prioridad asignable. Solo se renderiza para los roles con
 *   el permiso de asignacion de prioridad critica (`mesa_de_ayuda` y
 *   `administrador_directorio`), conforme a RP-006; para el resto de roles no se
 *   ofrece el control (ni la opcion `critica`).
 *
 *   Es UX, NO el limite de seguridad (FR-RBAC-005): ante una respuesta del backend
 *   que deniegue la accion (403/409), se muestra el error sin presentarla como
 *   exitosa ni exponer el recurso.
 */
import { AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useAuth } from '@/contexts/AuthContext';
import { useAsignarPrioridad } from '@/hooks/useAsignarPrioridad';
import { extractApiErrorMessage } from '@/services/api';
import { formatearPrioridad } from '@/utils/formatters';
import {
  puedeAsignarPrioridadCritica,
  prioridadesAsignables,
} from '@/utils/permisosPrioridad';
import type { IncidenteRead } from '@/types/incidente';

interface AsignarPrioridadProps {
  /** Incidente completo (para conocer la prioridad actual). */
  incidente: IncidenteRead;
  /** Callback tras una mutacion exitosa (p. ej. refrescar el detalle). */
  onMutated: () => void;
}

export function AsignarPrioridad({ incidente, onMutated }: AsignarPrioridadProps) {
  const { rol } = useAuth();
  const { mutate, isPending, error } = useAsignarPrioridad(incidente.id);

  // Sin el permiso no se ofrece el control (oculto); el backend sigue denegando.
  if (!puedeAsignarPrioridadCritica(rol)) {
    return null;
  }

  return (
    <div className="space-y-3">
      <Separator />
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Asignar prioridad
        </p>

        {/* Error de una asignacion denegada por el backend (403/409): sin exito asumido. */}
        {error != null && (
          <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
            <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span>{extractApiErrorMessage(error)}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {prioridadesAsignables(rol).map((prioridad) => {
            const esActual = prioridad === incidente.prioridad;
            return (
              <Button
                key={prioridad}
                variant={esActual ? 'default' : 'outline'}
                size="sm"
                disabled={isPending || esActual}
                onClick={() => mutate(prioridad, { onSuccess: onMutated })}
              >
                {isPending && !esActual && (
                  <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
                )}
                {formatearPrioridad(prioridad)}
              </Button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
