/**
 * Controles de filtro del dashboard: rango de fechas y toggle de granularidad.
 *
 * Responsabilidad:
 *   Provee dos inputs de fecha (desde/hasta) y un toggle dia/mes.
 *   Notifica al componente padre cuando los filtros cambian para que
 *   los hooks de React Query refetchen los datos.
 */
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import type { AgruparPor } from '@/types/estadisticas';

interface FiltrosDashboardProps {
  desde: string;
  hasta: string;
  agruparPor: AgruparPor;
  onDesdeChange: (value: string) => void;
  onHastaChange: (value: string) => void;
  onAgruparPorChange: (value: AgruparPor) => void;
}

export function FiltrosDashboard({
  desde,
  hasta,
  agruparPor,
  onDesdeChange,
  onHastaChange,
  onAgruparPorChange,
}: FiltrosDashboardProps) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      {/* Toggle de granularidad */}
      <div className="flex items-center rounded-md border bg-muted/20 p-0.5">
        <Button
          variant={agruparPor === 'dia' ? 'default' : 'ghost'}
          size="sm"
          className={cn(
            'h-8 px-3 text-xs font-medium',
            agruparPor === 'dia' ? '' : 'text-muted-foreground'
          )}
          onClick={() => onAgruparPorChange('dia')}
        >
          Dia
        </Button>
        <Button
          variant={agruparPor === 'mes' ? 'default' : 'ghost'}
          size="sm"
          className={cn(
            'h-8 px-3 text-xs font-medium',
            agruparPor === 'mes' ? '' : 'text-muted-foreground'
          )}
          onClick={() => onAgruparPorChange('mes')}
        >
          Mes
        </Button>
      </div>

      {/* Inputs de rango de fechas */}
      <div className="flex items-center gap-2">
        <label className="text-xs text-muted-foreground">Desde:</label>
        <Input
          type="date"
          value={desde}
          onChange={(e) => onDesdeChange(e.target.value)}
          className="h-9 w-40 text-xs"
        />
      </div>
      <div className="flex items-center gap-2">
        <label className="text-xs text-muted-foreground">Hasta:</label>
        <Input
          type="date"
          value={hasta}
          onChange={(e) => onHastaChange(e.target.value)}
          className="h-9 w-40 text-xs"
        />
      </div>
    </div>
  );
}
