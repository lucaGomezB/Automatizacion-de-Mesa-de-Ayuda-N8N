/**
 * Grafico de tendencias: linea con incidentes por periodo (dia o mes).
 *
 * Muestra la serie temporal de incidentes con tooltips interactivos
 * y soporte de exportacion a PNG via html2canvas.
 */
import { useRef } from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ExportButton } from './ExportButton';
import type { SerieTemporal } from '@/types/estadisticas';

interface TendenciaChartProps {
  data: SerieTemporal[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  onRefetch: () => void;
}

export function TendenciaChart({
  data,
  isLoading,
  isError,
  error,
  onRefetch,
}: TendenciaChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  if (isLoading) {
    return <LoadingSpinner texto="Cargando tendencias..." />;
  }

  if (isError) {
    return (
      <ErrorAlert
        mensaje={typeof error === 'object' && error !== null && 'message' in error
          ? String((error as { message: unknown }).message)
          : 'Error al cargar tendencias'}
        onReintentar={onRefetch}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        titulo="Sin datos de tendencias"
        descripcion="No hay incidentes en el rango seleccionado."
      />
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-foreground">Tendencia de Incidentes</h3>
        <ExportButton containerRef={chartRef} filename="tendencia-incidentes" />
      </div>
      <div ref={chartRef} className="bg-card rounded-lg border p-4">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="periodo" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ r: 3 }}
              name="Incidentes"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
