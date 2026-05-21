/**
 * Estado vacío genérico para tablas y listas sin resultados.
 * Se utiliza como reemplazo visual cuando una consulta no retorna datos,
 * evitando que el operador vea una tabla en blanco sin contexto.
 */
import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  /** Título principal del estado vacío. */
  titulo?: string;
  /** Descripción explicativa del motivo por el cual no hay datos. */
  descripcion?: string;
  /** Ícono personalizado; por defecto se usa el ícono de bandeja de entrada. */
  icon?: ReactNode;
}

export function EmptyState({
  titulo = 'Sin resultados',
  descripcion = 'No se encontraron registros para los filtros seleccionados.',
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center text-muted-foreground">
      <div className="mb-4 p-4 rounded-full bg-muted">
        {icon ?? <Inbox className="h-8 w-8 text-muted-foreground/60" />}
      </div>
      <p className="font-medium text-foreground">{titulo}</p>
      <p className="text-sm mt-1 max-w-xs">{descripcion}</p>
    </div>
  );
}
