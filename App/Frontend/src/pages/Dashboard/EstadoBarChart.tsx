/**
 * Grafico de barras con la distribucion de incidentes por estado.
 */
import { useRef } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ExportButton } from './ExportButton';

// Colores para los cinco estados del ciclo de vida
const ESTADO_COLORS: Record<string, string> = {
  nuevo: '#3b82f6',       // azul
  'en proceso': '#f59e0b', // ambar
  'en espera': '#8b5cf6',  // violeta
  resuelto: '#10b981',     // esmeralda
  cerrado: '#6b7280',      // gris
};

interface EstadoBarChartProps {
  data: Record<string, number> | undefined;
  isLoading: boolean;
}

export function EstadoBarChart({ data, isLoading }: EstadoBarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  if (isLoading) {
    return <LoadingSpinner texto="Cargando distribucion de estados..." />;
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-card rounded-lg border">
        <p className="text-sm text-muted-foreground">Sin datos de estado</p>
      </div>
    );
  }

  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    total: value,
    fill: ESTADO_COLORS[name] ?? '#6b7280',
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-foreground">Distribucion por Estado</h3>
        <ExportButton containerRef={chartRef} filename="distribucion-estado" />
      </div>
      <div ref={chartRef} className="bg-card rounded-lg border p-4">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="total" radius={[4, 4, 0, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
