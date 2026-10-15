/**
 * Confirmacion del borrado fisico por solicitud ARCO (c-89, FDIR-005).
 *
 * El borrado ARCO es IRREVERSIBLE: este dialogo advierte explicitamente antes de
 * enviar la solicitud. Componente presentacional: solo notifica `onConfirm` /
 * `onClose`; la pagina ejecuta la mutacion.
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
import type { Empleado } from '@/types/directorio';

interface ConfirmarBorradoDialogProps {
  open: boolean;
  empleado: Empleado | null;
  isPending: boolean;
  error: unknown;
  onClose: () => void;
  onConfirm: () => void;
}

export function ConfirmarBorradoDialog({
  open,
  empleado,
  isPending,
  error,
  onClose,
  onConfirm,
}: ConfirmarBorradoDialogProps) {
  return (
    <Dialog open={open} onOpenChange={(abierto) => !abierto && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TriangleAlert className="h-5 w-5 text-destructive" />
            Confirmar borrado ARCO
          </DialogTitle>
          <DialogDescription>
            Se eliminara de forma fisica el empleado{' '}
            <span className="font-medium text-foreground">{empleado?.nombre}</span> (legajo{' '}
            {empleado?.legajo}). Esta accion es <span className="font-medium">irreversible</span> y
            no puede deshacerse.
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
          <Button
            type="button"
            variant="destructive"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Confirmar borrado
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
