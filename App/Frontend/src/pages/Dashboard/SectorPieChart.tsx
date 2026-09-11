/**
 * Grafico de torta (donut) con la distribucion de incidentes por sector.
 *
 * El color de cada porcion se resuelve por el nombre canonico del sector (nunca por
 * IDs numericos). Un sector desconocido se dibuja con un color por defecto.
 */
import { useRef } from 'react';
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ExportButton } from './ExportButton';

// Colores consistentes para los cinco sectores canonicos.
const SECTOR_COLORS: Record<string, string> = {
  'Seguridad Informatica': '#dc2626',    // rojo
  'Soporte Tecnico Hardware': '#d97706', // ambar
  'Soporte Tecnico Software': '#2563eb', // azul
  'Bases de Datos': '#16a34a',           // verde
  Sistemas: '#7c3aed',                   // violeta
  'Sin asignar': '#9ca3af',              // gris
};

const COLOR_POR_DEFECTO = '#6b7280';

/** Resuelve el color de un sector a partir de su nombre canonico. */
export function getSectorColor(nombre: string): string {
  return SECTOR_COLORS[nombre] ?? COLOR_POR_DEFECTO;
}

interface SectorPieChartProps {
  data: Record<string, number> | undefined;
  isLoading: boolean;
}

export function SectorPieChart({ data, isLoading }: SectorPieChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  if (isLoading) {
    return <LoadingSpinner texto="Cargando distribucion de sectores..." />;
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-card rounded-lg border">
        <p className="text-sm text-muted-foreground">Sin datos de sector</p>
      </div>
    );
  }

  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-foreground">Distribucion por Sector</h3>
        <ExportButton containerRef={chartRef} filename="distribucion-sector" />
      </div>
      <div ref={chartRef} className="bg-card rounded-lg border p-4">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={getSectorColor(entry.name)}
                />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
