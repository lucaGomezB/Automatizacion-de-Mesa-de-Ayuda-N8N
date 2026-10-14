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
 */
import { useEffect, type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { onUnauthorized } from '@/services/api';
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
}

/**
 * Resuelve el destino de redireccion del guard (o null si se admite).
 *
 * Funcion PURA: misma entrada -> misma salida, sin efectos. El portal ("/") es
 * el destino canonico cuando el alcance no habilita la ruta solicitada. Un
 * `requiere` multiple admite cualquiera de los modos listados.
 */
export function resolverRedireccion({
  isAuthenticated,
  modo,
  requiere,
}: DecisionGuard): string | null {
  if (!isAuthenticated) return '/login';
  if (!requiere) return null;
  const admitidos: ModoAlcance[] = Array.isArray(requiere) ? requiere : [requiere];
  return admitidos.includes(modo) ? null : '/';
}

interface ProtectedRouteProps {
  children: ReactNode;
  /** Modo(s) de alcance exigido(s); ausente = solo exige autenticacion. */
  requiere?: RequiereAlcance | RequiereAlcance[];
}

/**
 * Wrapper de rutas: redirige si el usuario no esta autenticado o su alcance no
 * habilita la ruta. Registra el callback de logout ante respuestas 401.
 * (Logica de decision en `resolverRedireccion`.)
 */
export function ProtectedRoute({ children, requiere }: ProtectedRouteProps) {
  const { isAuthenticated, alcance, logout } = useAuth();

  useEffect(() => {
    onUnauthorized(() => {
      logout();
    });
  }, [logout]);

  const destino = resolverRedireccion({
    isAuthenticated,
    modo: alcance.modo,
    requiere,
  });

  if (destino) {
    return <Navigate to={destino} replace />;
  }

  return <>{children}</>;
}
