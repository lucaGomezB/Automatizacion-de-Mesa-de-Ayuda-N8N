/**
 * Guard de rutas por alcance (c-81, FR-RBAC-002; c-86 FR-RBAC-002).
 *
 * Responsabilidad:
 *   Decide si una ruta protegida es accesible segun la autenticacion Y el modo
 *   de alcance (`PROPIO` | `GLOBAL` | `SECTOR` | `VACIO`). La superficie
 *   operativa admite `GLOBAL` y `SECTOR`; "Mis incidentes" exige `PROPIO`; una
 *   cuenta `VACIO` va al portal; un anonimo va a `/login`.
 *
 *   Es UX y least-surprise: NO es el limite de seguridad. El backend sigue
 *   denegando cualquier recurso fuera de alcance (FR-RBAC-005). La cola de
 *   revision NO se gatea aqui: queda GLOBAL-only dentro del panel (FR-RBAC-002).
 *
 *   c-91 FSL-001: mientras la app rehidrata la sesion al arrancar, el guard NO
 *   decide (evita el parpadeo de "no autenticado"): muestra un estado de carga
 *   hasta que la rehidratacion resuelve.
 */
import { useEffect, type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth, useSessionLifecycle } from '@/contexts/AuthContext';
import { onUnauthorized } from '@/services/api';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import type { ModoAlcance } from '@/types/auth';

/**
 * Modo de alcance que una ruta protegida exige. La superficie operativa se
 * expresa como `['GLOBAL', 'SECTOR']`; "Mis incidentes" como `'PROPIO'`.
 */
export type RequiereAlcance = 'GLOBAL' | 'SECTOR' | 'PROPIO';

/** Entrada de la decision del guard. */
export interface DecisionGuard {
  isAuthenticated: boolean;
  modo: ModoAlcance;
  /** Uno o varios modos admitidos (any-of); ausente = solo autenticacion. */
  requiere?: RequiereAlcance | RequiereAlcance[];
  /** Rol del usuario autenticado (para el guard por rol de c-89). */
  rol?: string | null;
  /** Rol exigido por la ruta; ausente = sin requisito de rol (c-89). */
  requiereRol?: string;
}

/**
 * Resuelve el destino de redireccion del guard (o null si se admite).
 *
 * Funcion PURA: misma entrada -> misma salida, sin efectos. Orden de decision:
 *   1. Anonimo -> `/login`.
 *   2. Si la ruta exige un ROL (`requiereRol`), se admite SOLO si coincide; en
 *      caso contrario se redirige al portal. El modo de alcance no basta: el
 *      alcance `GLOBAL` tambien incluye a `mesa_de_ayuda` (c-89, FR-RBAC-008).
 *   3. Si no hay rol exigido, rige la logica por modo (`requiere`), sin cambios.
 */
export function resolverRedireccion({
  isAuthenticated,
  modo,
  requiere,
  rol,
  requiereRol,
}: DecisionGuard): string | null {
  if (!isAuthenticated) return '/login';
  if (requiereRol) return rol === requiereRol ? null : '/';
  if (!requiere) return null;
  const admitidos: ModoAlcance[] = Array.isArray(requiere) ? requiere : [requiere];
  return admitidos.includes(modo) ? null : '/';
}

interface ProtectedRouteProps {
  children: ReactNode;
  /** Modo(s) de alcance exigido(s); ausente = solo exige autenticacion. */
  requiere?: RequiereAlcance | RequiereAlcance[];
  /** Rol exigido por la ruta; ausente = sin requisito de rol (c-89). */
  requiereRol?: string;
}

/**
 * Wrapper de rutas: redirige si el usuario no esta autenticado, si su alcance no
 * habilita la ruta o si su rol no es el exigido. Registra el callback de logout
 * ante respuestas 401. (Logica de decision en `resolverRedireccion`.)
 */
export function ProtectedRoute({ children, requiere, requiereRol }: ProtectedRouteProps) {
  const { isAuthenticated, alcance, rol, logout } = useAuth();
  const { isHydrating } = useSessionLifecycle();

  useEffect(() => {
    onUnauthorized(() => {
      logout();
    });
  }, [logout]);

  // c-91 FSL-001: no resolver el guard hasta que la rehidratacion termine.
  if (isHydrating) {
    return <LoadingSpinner texto="Restaurando sesión…" />;
  }

  const destino = resolverRedireccion({
    isAuthenticated,
    modo: alcance.modo,
    requiere,
    rol,
    requiereRol,
  });

  if (destino) {
    return <Navigate to={destino} replace />;
  }

  return <>{children}</>;
}
