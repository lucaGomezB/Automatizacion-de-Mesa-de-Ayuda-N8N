/**
 * Indicador visual del nivel de confianza del clasificador automático (rango 0.0–1.0).
 *
 * Responsabilidad:
 *   Renderiza una barra de progreso proporcional al valor de confianza, acompañada
 *   de su representación numérica en porcentaje y una etiqueta "Revisar" cuando
 *   el valor cae por debajo del umbral de 0.70 (definido en parameters_gemini.md).
 *
 * Codificación de colores (semáforo):
 *   - Verde  (≥ 0.70) : clasificación aceptada automáticamente.
 *   - Ámbar  (0.50–0.69): confianza baja, requiere revisión humana.
 *   - Rojo   (< 0.50) : confianza muy baja, posiblemente etapa "fallback".
 */
import { cn } from '@/lib/utils';
import { formatearConfianza } from '@/utils/formatters';

interface ConfianzaIndicatorProps {
  confianza: number;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

const UMBRAL_REVISION = 0.70;

export function ConfianzaIndicator({
  confianza,
  showLabel = true,
  size = 'md',
}: ConfianzaIndicatorProps) {
  const porcentaje = Math.round(confianza * 100);
  const requiereRevision = confianza < UMBRAL_REVISION;

  // Color de la barra: verde (≥0.70), ámbar (0.50–0.69), rojo (<0.50)
  const colorBarra = confianza >= UMBRAL_REVISION
    ? 'bg-green-500'
    : confianza >= 0.5
    ? 'bg-amber-500'
    : 'bg-red-500';

  const colorTexto = confianza >= UMBRAL_REVISION
    ? 'text-green-700'
    : confianza >= 0.5
    ? 'text-amber-700'
    : 'text-red-700';

  return (
    <div className={cn('flex items-center gap-2', size === 'sm' ? 'gap-1.5' : 'gap-2')}>
      {/* Barra de progreso proporcional */}
      <div
        className={cn(
          'bg-slate-200 rounded-full overflow-hidden flex-shrink-0',
          size === 'sm' ? 'h-1.5 w-16' : 'h-2 w-20'
        )}
      >
        <div
          className={cn('h-full rounded-full transition-all', colorBarra)}
          style={{ width: `${porcentaje}%` }}
        />
      </div>

      {/* Valor numérico */}
      {showLabel && (
        <span className={cn('font-medium tabular-nums', colorTexto, size === 'sm' ? 'text-xs' : 'text-sm')}>
          {formatearConfianza(confianza)}
        </span>
      )}

      {/* Etiqueta de revisión requerida */}
      {requiereRevision && (
        <span className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
          Revisar
        </span>
      )}
    </div>
  );
}
