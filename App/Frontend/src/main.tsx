/**
 * Punto de entrada de la aplicación React.
 *
 * Responsabilidad:
 *   Configura e inicializa los cuatro proveedores globales de la aplicación:
 *   1. `QueryClientProvider` — cliente de React Query con política de reintentos reducidos
 *      para evitar saturar la API ante errores transitorios.
 *   2. `AuthProvider` — estado de autenticación JWT (token en memoria, no en localStorage).
 *   3. `BrowserRouter` — enrutador HTML5 con rutas protegidas por alcance (c-81):
 *      "/" (portal), "/admin" (superficie operativa, exige GLOBAL), "/mis-incidentes"
 *      (exige PROPIO), "/dashboard" y "/login". Las rutas montan `ProtectedRoute`.
 *   4. `ReactQueryDevtools` — panel de depuración de caché, activo solo en desarrollo.
 *
 *   Cualquier ruta no definida redirige a "/" para evitar páginas en blanco.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import ReportarIncidentePage from './pages/ReportarIncidente';
import AdministracionPage from './pages/Administracion';
import DashboardPage from './pages/Dashboard';
import LoginPage from './pages/LoginPage';
import MfaEnrollmentPage from './pages/MfaEnrollmentPage';
import MisIncidentesPage from './pages/MisIncidentes';
import DirectorioPage from './pages/Directorio';
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

// ── App ───────────────────────────────────────────────────────────────────────

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/mfa/enroll"
          element={
            <ProtectedRoute>
              <MfaEnrollmentPage />
            </ProtectedRoute>
          }
        />
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
            <ProtectedRoute requiere={['GLOBAL', 'SECTOR']}>
              <AdministracionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mis-incidentes"
          element={
            <ProtectedRoute requiere="PROPIO">
              <MisIncidentesPage />
            </ProtectedRoute>
          }
        />
        {/* Directorio: guard ADITIVO por ROL (c-89, FR-RBAC-008). El modo GLOBAL
            tambien incluye a mesa_de_ayuda, por eso no basta el alcance. */}
        <Route
          path="/directorio"
          element={
            <ProtectedRoute requiereRol="administrador_directorio">
              <DirectorioPage />
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
