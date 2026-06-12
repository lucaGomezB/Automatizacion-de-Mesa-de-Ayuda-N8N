/**
 * Archivo de setup global para Vitest.
 *
 * - Registra los matchers de @testing-library/jest-dom (toBeInTheDocument, etc.)
 * - Configura limpieza automática del DOM entre pruebas (afterEach cleanup)
 * - Agrega stubs de APIs del navegador que happy-dom no implementa y que
 *   Radix UI (shadcn Select / Dialog) requiere para no lanzar errores en tests.
 */

/// <reference types="vitest/globals" />
/// <reference types="@testing-library/jest-dom" />

import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Limpia el DOM montado por @testing-library/react tras cada prueba
afterEach(() => {
  cleanup();
});

// ---- Stubs de APIs del navegador requeridas por Radix UI / JSDOM ----

// Radix UI Select llama a hasPointerCapture en los elementos del DOM
if (!Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
}

// Radix UI Select / Dialog llama a scrollIntoView al abrir opciones
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => undefined;
}

// matchMedia no está implementado en happy-dom; varios componentes lo usan
// (p. ej. detectar preferencia de esquema de color).
if (!window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }),
  });
}
