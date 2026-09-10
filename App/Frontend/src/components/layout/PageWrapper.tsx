/**
 * Contenedor de página: incorpora el encabezado global y centra el contenido
 * con un ancho máximo de 7xl (1280 px) para mantener legibilidad en pantallas anchas.
 *
 * Todas las páginas de la aplicación deben envolver su contenido con este componente
 * para garantizar consistencia visual y estructural.
 */
import type { ReactNode } from 'react';
import { Header } from './Header';

interface PageWrapperProps {
  /** Contenido de la página, renderizado debajo del encabezado global. */
  children: ReactNode;
  /** Clase CSS adicional aplicada al contenedor interno (opcional). */
  contentClassName?: string;
}

export function PageWrapper({ children, contentClassName }: PageWrapperProps) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      <main className={`flex-1 max-w-7xl mx-auto w-full px-4 py-8 ${contentClassName ?? ''}`}>
        {children}
      </main>
    </div>
  );
}
