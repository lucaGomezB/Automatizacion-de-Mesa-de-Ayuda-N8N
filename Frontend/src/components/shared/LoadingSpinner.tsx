/**
 * Indicador de carga genérico para estados de espera de respuestas de la API.
 *
 * Responsabilidad:
 *   Reemplaza el contenido de una sección mientras se resuelve una promesa asíncrona,
 *   evitando que el operador perciba una pantalla en blanco o un parpadeo brusco.
 *   Acepta un texto descriptivo opcional para contextualizar qué se está cargando.
 */
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  texto?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingSpinner({ texto, size = 'md', className }: LoadingSpinnerProps) {
  const iconSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-8 w-8' : 'h-6 w-6';

  return (
    <div className={cn('flex items-center justify-center gap-3 text-muted-foreground py-10', className)}>
      <Loader2 className={cn('animate-spin flex-shrink-0', iconSize)} />
      {texto && <span className="text-sm">{texto}</span>}
    </div>
  );
}
