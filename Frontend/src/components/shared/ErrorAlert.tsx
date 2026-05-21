/**
 * Alerta de error reutilizable para presentar fallos de la API al operador.
 *
 * Responsabilidad:
 *   Muestra un mensaje de error contextualizado con título editable y, opcionalmente,
 *   un botón de reintento que delega la acción al componente padre mediante `onReintentar`.
 *   Se utiliza como reemplazo de tabla/lista cuando una consulta de React Query falla.
 */
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface ErrorAlertProps {
  titulo?: string;
  mensaje: string;
  onReintentar?: () => void;
}

export function ErrorAlert({
  titulo = 'Error al cargar los datos',
  mensaje,
  onReintentar,
}: ErrorAlertProps) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{titulo}</AlertTitle>
      <AlertDescription className="mt-1 flex flex-col gap-3">
        <span>{mensaje}</span>
        {onReintentar && (
          <Button variant="outline" size="sm" onClick={onReintentar} className="w-fit">
            Reintentar
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}
