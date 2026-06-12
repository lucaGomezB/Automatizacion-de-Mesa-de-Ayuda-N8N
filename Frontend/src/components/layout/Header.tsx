/**
 * Encabezado global de la aplicación (componente sticky en la parte superior de todas las páginas).
 *
 * Responsabilidad:
 *   Presenta tres columnas en un grid de 3 columnas:
 *   1. Identidad institucional: logotipo y nombre del sistema.
 *   2. Navegación principal: enlaces a Portal ("/") y Administración ("/admin").
 *   3. Indicador de salud de la API: solo visible en la ruta /admin; usa `useHealthCheck`
 *      para mostrar un punto color verde/amarillo/rojo según el estado del backend.
 *
 *   El estilo active de los NavLinks se aplica dinámicamente para reflejar la ruta actual.
 */
import { NavLink, useLocation } from 'react-router-dom';
import { TicketCheck } from 'lucide-react';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { cn } from '@/lib/utils';

export function Header() {
  const location = useLocation();
  const isAdmin = location.pathname.startsWith('/admin');
  const { data: health, isError: healthError, isPending: healthPending } = useHealthCheck();

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      'px-2.5 py-2 sm:px-4 rounded-md text-xs sm:text-sm font-medium transition-colors whitespace-nowrap',
      isActive
        ? 'bg-white/20 text-white'
        : 'text-white/75 hover:bg-white/10 hover:text-white'
    );

  return (
    <header className="bg-primary text-primary-foreground shadow-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 grid grid-cols-[auto_1fr_auto] sm:grid-cols-3 items-center gap-2">

        {/* Columna izquierda: identidad institucional */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="hidden sm:block bg-white/10 p-1.5 rounded-md">
            <TicketCheck className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <p className="font-semibold text-base leading-none whitespace-nowrap">Mesa de Ayuda</p>
            {/* El subtítulo no entra en viewports angostos sin pisar la navegación */}
            <p className="hidden sm:block text-[11px] text-white/60 mt-0.5">
              UTN · Automatización IA — 2026
            </p>
          </div>
        </div>

        {/* Columna central: navegación principal */}
        <nav className="flex items-center justify-center gap-1">
          <NavLink to="/" end className={navLinkClass}>
            Portal
          </NavLink>
          <NavLink to="/admin" className={navLinkClass}>
            Administración
          </NavLink>
        </nav>

        {/* Columna derecha: indicador de salud de la API (solo en /admin) */}
        <div className="flex justify-end">
          {isAdmin && (
            <div className="flex items-center gap-2 text-sm">
              <span
                className={cn(
                  'h-2.5 w-2.5 rounded-full flex-shrink-0',
                  healthPending && 'bg-yellow-400 animate-pulse',
                  health && !healthError && 'bg-green-400',
                  healthError && 'bg-red-400'
                )}
              />
              {/* En móvil queda solo el punto de color; el texto necesita ancho de tablet+ */}
              <span className="hidden md:inline text-white/75 text-xs whitespace-nowrap">
                {healthPending && 'Verificando API…'}
                {health && !healthError && `API operativa · v${health.version}`}
                {healthError && 'API sin conexión'}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
