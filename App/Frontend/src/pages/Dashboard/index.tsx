/**
 * Pagina del Dashboard de Analitica — ruta "/dashboard".
 *
 * Responsabilidad:
 *   Compone los filtros de fecha/granularidad, los graficos ReCharts
 *   (tendencia, sector, estado) y las tarjetas KPI de resumen.
 *
 * Flujo de datos:
 *   useTendencias → GET /api/v1/estadisticas/tendencias
 *   useResumen    → GET /api/v1/estadisticas/resumen
 */
import { useState, useMemo, useCallback } from 'react';
import { BarChart3, TrendingUp, Users } from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTendencias, useResumen } from '@/hooks/useEstadisticas';
import { extractApiErrorMessage } from '@/services/api';
import { FiltrosDashboard } from './FiltrosDashboard';
import { TendenciaChart } from './TendenciaChart';
import { SectorPieChart } from './SectorPieChart';
import { EstadoBarChart } from './EstadoBarChart';
import type { AgruparPor } from '@/types/estadisticas';

/** Fecha de hoy en formato YYYY-MM-DD */
function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Fecha de hace N dias en formato YYYY-MM-DD */
function daysAgoStr(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

export default function DashboardPage() {
  // ── Estado de filtros ─────────────────────────────────────────────────
  const [desde, setDesde] = useState(() => daysAgoStr(30));
  const [hasta, setHasta] = useState(() => todayStr());
  const [agruparPor, setAgruparPor] = useState<AgruparPor>('dia');

  // ── Consultas de datos ─────────────────────────────────────────────────
  const tendenciasParams = useMemo(
    () => ({ agrupar_por: agruparPor, desde, hasta }),
    [agruparPor, desde, hasta]
  );

  const {
    data: tendencias,
    isLoading: cargandoTendencias,
    isError: errorTendencias,
    error: errorTendenciasObj,
    refetch: refetchTendencias,
  } = useTendencias(tendenciasParams);

  const {
    data: resumen,
    isLoading: cargandoResumen,
  } = useResumen({ desde, hasta });

  // ── Handlers ───────────────────────────────────────────────────────────
  const handleRefetch = useCallback(() => {
    void refetchTendencias();
  }, [refetchTendencias]);

  // ── Renderizado ────────────────────────────────────────────────────────

  return (
    <PageWrapper>
      <div className="space-y-6">
        {/* Encabezado */}
        <div>
          <h1 className="text-2xl font-semibold text-primary">Dashboard de Analitica</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Tendencias, distribucion por sector y estado de los incidentes del sistema.
          </p>
        </div>

        {/* Filtros */}
        <FiltrosDashboard
          desde={desde}
          hasta={hasta}
          agruparPor={agruparPor}
          onDesdeChange={setDesde}
          onHastaChange={setHasta}
          onAgruparPorChange={setAgruparPor}
        />

        {/* Tarjetas KPI */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard
            title="Total Incidentes"
            value={resumen?.total_incidentes}
            loading={cargandoResumen}
            icon={<BarChart3 className="h-5 w-5 text-blue-600" />}
          />
          <KpiCard
            title="Promedio Diario"
            value={resumen?.promedio_diario}
            loading={cargandoResumen}
            icon={<TrendingUp className="h-5 w-5 text-green-600" />}
            decimals={1}
          />
          <KpiCard
            title="Tasa Revision Humana"
            value={
              resumen?.tasa_revision_humana !== undefined
                ? resumen.tasa_revision_humana * 100
                : undefined
            }
            loading={cargandoResumen}
            icon={<Users className="h-5 w-5 text-amber-600" />}
            suffix="%"
            decimals={1}
          />
        </div>

        {/* Grafico de tendencias */}
        <TendenciaChart
          data={tendencias?.series}
          isLoading={cargandoTendencias}
          isError={errorTendencias}
          error={errorTendenciasObj}
          onRefetch={handleRefetch}
        />

        {/* Graficos de distribucion (dos columnas) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SectorPieChart
            data={tendencias?.distribucion_sectores ?? resumen?.distribucion_sectores}
            isLoading={cargandoTendencias && cargandoResumen}
          />
          <EstadoBarChart
            data={tendencias?.distribucion_estados ?? resumen?.distribucion_estados}
            isLoading={cargandoTendencias && cargandoResumen}
          />
        </div>
      </div>
    </PageWrapper>
  );
}

// ── Componente auxiliar: Tarjeta KPI ────────────────────────────────────────

interface KpiCardProps {
  title: string;
  value: number | undefined;
  loading: boolean;
  icon: React.ReactNode;
  decimals?: number;
  suffix?: string;
}

function KpiCard({ title, value, loading, icon, decimals = 0, suffix = '' }: KpiCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-20 bg-muted animate-pulse rounded" />
        ) : (
          <p className="text-2xl font-bold tabular-nums">
            {value !== undefined ? value.toFixed(decimals) : '—'}
            {suffix}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
