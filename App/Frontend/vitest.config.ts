/**
 * Configuración de Vitest para el frontend.
 *
 * Espeja el alias "@/" de vite.config.ts y usa happy-dom como entorno DOM.
 * Los archivos de cobertura se enfocan en el código de dominio
 * (components/, hooks/, services/) excluyendo los primitivos de shadcn/ui.
 */
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      include: [
        'src/components/**',
        'src/hooks/**',
        'src/services/**',
      ],
      exclude: [
        'src/components/ui/**',
        'src/components/layout/**',
      ],
      reporter: ['text', 'html'],
    },
  },
});
