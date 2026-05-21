/**
 * Punto de entrada de la aplicación React.
 *
 * Responsabilidad:
 *   Configura e inicializa los tres proveedores globales de la aplicación:
 *   1. `QueryClientProvider` — cliente de React Query con política de reintentos reducidos
 *      para evitar saturar la API ante errores transitorios.
 *   2. `BrowserRouter` — enrutador HTML5 con dos rutas: "/" (portal) y "/admin" (panel).
 *   3. `ReactQueryDevtools` — panel de depuración de caché, activo solo en desarrollo.
 *
 *   Cualquier ruta no definida redirige a "/" para evitar páginas en blanco.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import ReportarIncidentePage from './pages/ReportarIncidente';
import AdministracionPage from './pages/Administracion';
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

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ReportarIncidentePage />} />
          <Route path="/admin" element={<AdministracionPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      {/* Devtools disponibles únicamente en entorno de desarrollo */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
