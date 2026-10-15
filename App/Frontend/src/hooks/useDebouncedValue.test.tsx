/**
 * Pruebas del hook useDebouncedValue (c-88, FIS-001).
 *
 * El hook retrasa la propagacion de un valor hasta que dejan de producirse
 * cambios durante el intervalo indicado. Se usan fake timers para controlar el
 * reloj: el valor efectivo solo se actualiza tras 300 ms sin nuevas pulsaciones.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebouncedValue } from './useDebouncedValue';

describe('useDebouncedValue', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('devuelve el valor inicial de inmediato', () => {
    const { result } = renderHook(() => useDebouncedValue('inicial', 300));
    expect(result.current).toBe('inicial');
  });

  it('no actualiza el valor antes de que transcurra el retraso', () => {
    const { result, rerender } = renderHook(
      ({ v }: { v: string }) => useDebouncedValue(v, 300),
      { initialProps: { v: 'a' } }
    );

    rerender({ v: 'ab' });
    act(() => {
      vi.advanceTimersByTime(299);
    });

    expect(result.current).toBe('a');
  });

  it('actualiza el valor tras el retraso', () => {
    const { result, rerender } = renderHook(
      ({ v }: { v: string }) => useDebouncedValue(v, 300),
      { initialProps: { v: 'a' } }
    );

    rerender({ v: 'ab' });
    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current).toBe('ab');
  });

  it('reinicia el temporizador ante cambios rapidos y solo aplica el ultimo', () => {
    const { result, rerender } = renderHook(
      ({ v }: { v: string }) => useDebouncedValue(v, 300),
      { initialProps: { v: 'a' } }
    );

    rerender({ v: 'ab' });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    rerender({ v: 'abc' });
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe('a');

    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current).toBe('abc');
  });
});
