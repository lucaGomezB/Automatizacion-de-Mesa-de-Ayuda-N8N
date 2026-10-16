/**
 * Dialogo modal de expiracion de sesion (c-91, FSL-002/FSL-004).
 *
 * Responsabilidad:
 *   Presenta un aviso accesible cuando el access token esta por expirar y ofrece
 *   explicitamente continuar la sesion o cerrarla. NO se puede descartar por la
 *   X, el overlay ni Escape: la decision es del usuario (o del cierre automatico
 *   por vencimiento de la ventana de gracia, gestionado en AuthContext).
 *
 *   La logica de temporizador, extension y cierre vive en AuthContext; este
 *   componente solo cablea la UI a `useSessionLifecycle()` y `useAuth()`.
 */
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAuth, useSessionLifecycle } from '@/contexts/AuthContext';

export function SessionExpiryDialog() {
  const { logout } = useAuth();
  const { expirationPromptVisible, continueSession } = useSessionLifecycle();

  return (
    <Dialog open={expirationPromptVisible} onOpenChange={() => undefined}>
      <DialogContent
        hideClose
        onEscapeKeyDown={(event) => event.preventDefault()}
        onInteractOutside={(event) => event.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle>Tu sesión está por expirar</DialogTitle>
          <DialogDescription>
            Por seguridad, la sesión se cerrará automáticamente si no confirmás
            que querés continuar. Elegí continuar para extenderla.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => logout()}>
            Cerrar sesión
          </Button>
          <Button
            type="button"
            onClick={() => {
              void continueSession();
            }}
          >
            Continuar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
