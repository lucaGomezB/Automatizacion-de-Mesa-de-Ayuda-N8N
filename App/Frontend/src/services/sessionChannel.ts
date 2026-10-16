/**
 * Canal de sincronizacion de sesion entre pestanas (c-91, FSL-005).
 *
 * Responsabilidad:
 *   Propaga eventos de sesion (`logout`, `refreshed`) entre las pestanas de la
 *   misma aplicacion usando un `BroadcastChannel` con nombre canonico. Un cierre
 *   de sesion en una pestana cierra las demas; una extension exitosa mantiene a
 *   las demas autenticadas (rehidratan con la cookie compartida).
 *
 *   Es infraestructura sin estado de dominio: no conoce tokens ni la API. Si el
 *   entorno no provee `BroadcastChannel` (p. ej. tests, navegadores antiguos),
 *   degrada de forma segura a no-op para no romper la app.
 */

/** Nombre canonico del canal de sesion compartido por todas las pestanas. */
export const SESSION_CHANNEL_NAME = 'mesa-ayuda-session';

/** Eventos de sesion difundidos entre pestanas. */
export type SessionEvent = { type: 'logout' } | { type: 'refreshed' };

type SessionEventHandler = (event: SessionEvent) => void;

let channel: BroadcastChannel | null = null;
const handlers = new Set<SessionEventHandler>();

/**
 * Crea (o reutiliza) el canal. Devuelve null si `BroadcastChannel` no existe en
 * el entorno, de modo que la app sigue funcionando sin sincronizacion.
 */
function ensureChannel(): BroadcastChannel | null {
  if (channel) return channel;
  if (typeof BroadcastChannel === 'undefined') return null;
  channel = new BroadcastChannel(SESSION_CHANNEL_NAME);
  channel.onmessage = (event: MessageEvent<SessionEvent>) => {
    for (const handler of handlers) {
      handler(event.data);
    }
  };
  return channel;
}

/** Difunde un evento de sesion a las demas pestanas (no-op si no hay canal). */
export function broadcastSessionEvent(event: SessionEvent): void {
  ensureChannel()?.postMessage(event);
}

/**
 * Suscribe un manejador a los eventos entrantes de otras pestanas.
 *
 * @returns Funcion para desafiliarse (limpieza en el unmount del consumidor).
 */
export function subscribeToSessionEvents(handler: SessionEventHandler): () => void {
  handlers.add(handler);
  ensureChannel();
  return () => {
    handlers.delete(handler);
  };
}
