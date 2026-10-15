/**
 * Confirmacion de la purga manual por retencion (c-89, FDIR-006).
 *
 * La purga elimina fisicamente los empleados vencidos y no se puede deshacer:
 * este dialogo exige confirmacion explicita. Componente presentacional: la pagina
 * ejecuta la mutacion y muestra el conteo resultante.
 */
import { Loader2, TriangleAlert } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { extractApiErrorMessage } from '@/services/api';

interface ConfirmarPurgaDialogProps {
  open: boolean;
  isPending: boolean;
  error: unknown;
  onClose: () => void;
  onConfirm: () => void;
}

export function ConfirmarPurgaDialog({
  open,
  isPending,
  error,
  onClose,
  onConfirm,
}: ConfirmarPurgaDialogProps) {
  return (
    <Dialog open={open} onOpenChange={(abierto) => !abierto && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TriangleAlert className="h-5 w-5 text-destructive" />
            Purga por retencion
          </DialogTitle>
          <DialogDescription>
            Se eliminaran de forma fisica los empleados que superaron su periodo de
            retencion. Esta accion no se puede deshacer.
          </DialogDescription>
        </DialogHeader>

        {error !== null && error !== undefined && (
          <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
            {extractApiErrorMessage(error)}
          </div>
        )}

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
            Cancelar
          </Button>
          <Button type="button" onClick={onConfirm} disabled={isPending}>
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Confirmar purga
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
