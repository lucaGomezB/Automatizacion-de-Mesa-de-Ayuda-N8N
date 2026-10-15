/**
 * Hook de debounce de valor (c-88, FIS-001, D3).
 *
 * Devuelve el valor recibido retrasado: mientras el valor de entrada siga
 * cambiando dentro del intervalo, la salida permanece en el ultimo valor que
 * logro estabilizarse. Escribir en la barra de busqueda, por lo tanto, no
 * dispara una consulta por cada pulsacion, sino una sola tras 300 ms sin
 * cambios.
 *
 * Uso:
 *   const debounced = useDebouncedValue(termino, 300);
 *
 * @param value   Valor de entrada a retrasar.
 * @param delayMs Retraso en milisegundos (por defecto 300).
 * @returns El valor de entrada una vez que dejo de cambiar durante `delayMs`.
 */
import { useEffect, useState } from 'react';

export function useDebouncedValue<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
