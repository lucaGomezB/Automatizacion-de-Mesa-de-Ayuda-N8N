/**
 * Pruebas del canal de sincronizacion multi-pestana (c-91, FSL-005).
 *
 * Verifican que el modulo use el `BroadcastChannel` con el nombre canonico y que
 * retransmita los eventos de sesion a los suscriptores. happy-dom no implementa
 * `BroadcastChannel`, por eso se inyecta un doble controlado y se aisla el
 * registro de modulos con `vi.resetModules()`.
 */
import { describe, it, expect, vi, afterEach } from 'vitest';

interface FakeChannel {
  name: string;
  onmessage: ((ev: MessageEvent) => void) | null;
  posted: unknown[];
  postMessage(message: unknown): void;
  close(): void;
}

function installFakeBroadcastChannel(instances: FakeChannel[]) {
  class FakeBroadcastChannel implements FakeChannel {
    onmessage: ((ev: MessageEvent) => void) | null = null;
    posted: unknown[] = [];
    constructor(public name: string) {
      instances.push(this);
    }
    postMessage(message: unknown): void {
      this.posted.push(message);
    }
    close(): void {
      // no-op en el doble
    }
  }
  (globalThis as unknown as { BroadcastChannel: unknown }).BroadcastChannel =
    FakeBroadcastChannel;
}

afterEach(() => {
  delete (globalThis as unknown as { BroadcastChannel?: unknown }).BroadcastChannel;
  vi.resetModules();
});

describe('sessionChannel (c-91 FSL-005)', () => {
  it('usa el BroadcastChannel "mesa-ayuda-session" y publica los eventos', async () => {
    const instances: FakeChannel[] = [];
    installFakeBroadcastChannel(instances);

    const mod = await import('./sessionChannel');
    mod.broadcastSessionEvent({ type: 'logout' });

    expect(instances).toHaveLength(1);
    expect(instances[0].name).toBe('mesa-ayuda-session');
    expect(instances[0].posted).toEqual([{ type: 'logout' }]);
  });

  it('retransmite los mensajes entrantes a los suscriptores y permite desafiliarse', async () => {
    const instances: FakeChannel[] = [];
    installFakeBroadcastChannel(instances);

    const mod = await import('./sessionChannel');
    const recibidos: unknown[] = [];
    const unsubscribe = mod.subscribeToSessionEvents((event) => recibidos.push(event));

    instances[0].onmessage?.({ data: { type: 'refreshed' } } as MessageEvent);
    expect(recibidos).toEqual([{ type: 'refreshed' }]);

    unsubscribe();
    instances[0].onmessage?.({ data: { type: 'logout' } } as MessageEvent);
    expect(recibidos).toEqual([{ type: 'refreshed' }]);
  });

  it('degrada de forma segura cuando BroadcastChannel no existe', async () => {
    // Sin doble instalado: happy-dom no provee BroadcastChannel.
    const mod = await import('./sessionChannel');
    expect(() => mod.broadcastSessionEvent({ type: 'logout' })).not.toThrow();
    const unsubscribe = mod.subscribeToSessionEvents(() => undefined);
    expect(typeof unsubscribe).toBe('function');
    unsubscribe();
  });
});
