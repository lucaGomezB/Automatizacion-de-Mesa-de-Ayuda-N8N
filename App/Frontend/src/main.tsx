/**
 * Punto de entrada de la aplicación React.
 *
 * Responsabilidad:
 *   Configura e inicializa los cuatro proveedores globales de la aplicación:
 *   1. `QueryClientProvider` — cliente de React Query con política de reintentos reducidos
 *      para evitar saturar la API ante errores transitorios.
 *   2. `AuthProvider` — estado de autenticación JWT (token en memoria, no en localStorage).
 *   3. `BrowserRouter` — enrutador HTML5 con tres rutas: "/" (portal), "/admin" (panel)
 *      y "/login" (inicio de sesión). Las rutas "/" y "/admin" son protegidas.
 *   4. `ReactQueryDevtools` — panel de depuración de caché, activo solo en desarrollo.
 *
 *   Cualquier ruta no definida redirige a "/" para evitar páginas en blanco.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { onUnauthorized } from './services/api';
import ReportarIncidentePage from './pages/ReportarIncidente';
import AdministracionPage from './pages/Administracion';
import DashboardPage from './pages/Dashboard';
import LoginPage from './pages/LoginPage';
import './index.css';

// Cliente de React Query con reintentos reducidos para evitar saturar la API en errores temporales
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});

// ── ProtectedRoute ────────────────────────────────────────────────────────────

/**
 * Wrapper que redirige a /login si el usuario no está autenticado.
 *
 * También registra el callback onUnauthorized para que el interceptor
 * de Axios pueda redirigir al login cuando el backend responde 401.
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout } = useAuth();

  // Registrar el callback de logout para respuestas 401 del backend.
  // Se usa useEffect en producción; aquí usamos un registro directo
  // que es idempotente (sobrescribe el callback anterior).
  React.useEffect(() => {
    onUnauthorized(() => {
      logout();
    });
  }, [logout]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// ── App ───────────────────────────────────────────────────────────────────────

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ReportarIncidentePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdministracionPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

// ── Mount ─────────────────────────────────────────────────────────────────────

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <App />
      </AuthProvider>
      {/* Devtools disponibles únicamente en entorno de desarrollo */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
);
