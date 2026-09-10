/**
 * Tarjeta de confirmación que se muestra tras el envío exitoso de un incidente.
 *
 * Responsabilidad:
 *   Presenta al usuario el resultado completo de la clasificación automática:
 *   número de ticket, sector asignado, confianza del modelo y etapa del pipeline.
 *
 *   Dado que `IncidenteRead` (respuesta del POST) no incluye el campo `confianza`
 *   (que reside en `ClasificacionLogRead`), este componente realiza una segunda consulta
 *   asíncrona a `listarClasificacionesPorIncidente` con `staleTime: Infinity` —
 *   los datos son estáticos una vez creado el incidente, por lo que no necesitan
 *   revalidarse durante la sesión.
 */
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, Hash, Brain, RefreshCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { ConfianzaIndicator } from '@/components/shared/ConfianzaIndicator';
import { formatearEtapa } from '@/utils/formatters';
import { listarClasificacionesPorIncidente } from '@/services/clasificacionesService';
import type { IncidenteRead } from '@/types/incidente';

interface SuccessCardProps {
  incidente: IncidenteRead;
  nombreUsuario: string;
  onNuevoReporte: () => void;
}

export function SuccessCard({ incidente, nombreUsuario, onNuevoReporte }: SuccessCardProps) {
  // Obtiene el registro de clasificación para mostrar la confianza del modelo
  const { data: clasificaciones } = useQuery({
    queryKey: ['clasificaciones', incidente.id],
    queryFn: () => listarClasificacionesPorIncidente(incidente.id),
    staleTime: Infinity,
  });

  const clasificacion = clasificaciones?.[0];

  return (
    <Card className="border-green-200 bg-green-50/40 animate-fade-in">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-100 rounded-full">
            <CheckCircle2 className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <CardTitle className="text-green-800 text-lg">
              Incidente registrado correctamente
            </CardTitle>
            {nombreUsuario && (
              <p className="text-sm text-green-700 mt-0.5">
                Gracias, <strong>{nombreUsuario}</strong>. Recibirás seguimiento a la brevedad.
              </p>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <Separator className="bg-green-200" />

        {/* Datos del ticket creado */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

          {/* Número de ticket */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground uppercase tracking-wide">
              <Hash className="h-3.5 w-3.5" />
              Número de Ticket
            </div>
            <p className="text-2xl font-bold text-primary tabular-nums">
              #{incidente.id.toString().padStart(5, '0')}
            </p>
          </div>

          {/* Sector asignado por el clasificador */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground uppercase tracking-wide">
              <Brain className="h-3.5 w-3.5" />
              Sector Asignado por IA
            </div>
            <div className="flex items-center gap-2">
              <SectorBadge nombre={incidente.sector?.nombre} />
              {incidente.requiere_revision_humana && (
                <span className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                  Revisión pendiente
                </span>
              )}
            </div>
          </div>

          {/* Nivel de confianza del clasificador (disponible tras la consulta async) */}
          {clasificacion && (
            <div className="flex flex-col gap-1">
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                Confianza del Clasificador
              </p>
              <ConfianzaIndicator confianza={clasificacion.confianza} size="md" />
              <p className="text-xs text-muted-foreground">
                Etapa: {formatearEtapa(clasificacion.etapa)}
              </p>
            </div>
          )}

          {/* Prioridad asignada */}
          <div className="flex flex-col gap-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Prioridad</p>
            <p className="text-sm font-medium capitalize">{incidente.prioridad}</p>
          </div>
        </div>

        {incidente.requiere_revision_humana && (
          <div className="bg-amber-50 border border-amber-200 rounded-md p-3 text-sm text-amber-800">
            <strong>Nota:</strong> La confianza del clasificador fue insuficiente. El ticket será
            revisado manualmente por el equipo de mesa de ayuda antes de su asignación definitiva.
          </div>
        )}

        <Separator className="bg-green-200" />

        <Button onClick={onNuevoReporte} variant="outline" className="w-full sm:w-auto">
          <RefreshCcw className="h-4 w-4 mr-2" />
          Reportar otro incidente
        </Button>
      </CardContent>
    </Card>
  );
}
