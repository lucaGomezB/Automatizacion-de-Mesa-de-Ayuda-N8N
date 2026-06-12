/**
 * Helpers de test reutilizables para el frontend.
 *
 * `renderWithClient`: renderiza un componente envuelto en un QueryClientProvider
 * con un QueryClient nuevo por llamada (retry: false) para aislar el caché
 * de React Query entre pruebas.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, type RenderOptions } from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';

/** Crea un QueryClient aislado con retry desactivado (para que los errores se propaguen inmediatamente). */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface WrapperProps {
  children: ReactNode;
}

/**
 * Renderiza un componente dentro de un QueryClientProvider con cliente aislado.
 * Úsalo para componentes y hooks que dependen de React Query.
 */
export function renderWithClient(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const client = createTestQueryClient();
  const Wrapper = ({ children }: WrapperProps) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return render(ui, { wrapper: Wrapper, ...options });
}
