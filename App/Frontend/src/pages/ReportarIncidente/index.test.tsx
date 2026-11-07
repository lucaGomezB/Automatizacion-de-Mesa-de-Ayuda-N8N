/**
 * Pruebas de la página del Portal de Reporte de Incidentes.
 * C-27: la nota informativa lista los sectores canónicos obtenidos en runtime
 * desde el catálogo, sin depender de IDs numéricos fijos ni de la taxonomía previa.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import ReportarIncidentePage from './index';
import { SuccessCard } from './SuccessCard';
import * as catalogosService from '@/services/catalogosService';
import type { SectorOpcion } from '@/types/catalog';
import type { IncidenteRead } from '@/types/incidente';

vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));

vi.mock('@/services/clasificacionesService', () => ({
  listarClasificacionesPorIncidente: vi.fn().mockResolvedValue([]),
}));

// El Header (vía PageWrapper) consulta useHealthCheck. Sin este mock, la prueba
// dispararía una solicitud HTTP real a /health (fuga de red, FE 8).
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

// El Header (via PageWrapper) consume el contexto de auth (c-81).
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    token: null,
    username: null,
    isAuthenticated: false,
    mfaRequired: false,
    rol: null,
    alcance: { modo: 'VACIO' },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  }),
}));

const mockSectores: SectorOpcion[] = [
  { id: 1, nombre: 'Seguridad Informatica' },
  { id: 2, nombre: 'Soporte Tecnico Hardware' },
  { id: 3, nombre: 'Soporte Tecnico Software' },
  { id: 4, nombre: 'Bases de Datos' },
  { id: 5, nombre: 'Sistemas' },
];

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ReportarIncidentePage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('ReportarIncidentePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(mockSectores);
  });

  it('lista los cinco sectores canónicos del catálogo en la nota informativa', async () => {
    renderPage();

    const nota = await screen.findByTestId('nota-clasificacion');

    await waitFor(() => {
      expect(within(nota).getByText('Seguridad Informatica')).toBeInTheDocument();
    });
    expect(within(nota).getByText('Soporte Tecnico Hardware')).toBeInTheDocument();
    expect(within(nota).getByText('Soporte Tecnico Software')).toBeInTheDocument();
    expect(within(nota).getByText('Bases de Datos')).toBeInTheDocument();
    expect(within(nota).getByText('Sistemas')).toBeInTheDocument();
    expect(within(nota).queryByText('Operaciones')).not.toBeInTheDocument();
  });

  it('el texto que describe la clasificación automática no nombra un proveedor ni una versión del modelo', async () => {
    renderPage();

    const encabezado = await screen.findByText(/El sistema lo clasificará/i);
    const texto = encabezado.textContent ?? '';

    expect(texto).not.toContain('Gemini');
    expect(texto).not.toContain('2.5 Flash');
    expect(texto).not.toMatch(/\d+\.\d+/);

    // El texto sigue describiendo la clasificación automática sin nombrar al proveedor.
    expect(texto).toMatch(/clasificará automáticamente/i);
    expect(texto).toMatch(/inteligencia artificial/i);

    // La nota informativa conserva el umbral vigente del 70%.
    const nota = await screen.findByTestId('nota-clasificacion');
    expect(within(nota).getByText(/70%/)).toBeInTheDocument();

    // La tarjeta de confirmación conserva la etiqueta "Sector Asignado por IA".
    const incidenteConfirmado: IncidenteRead = {
      id: 1,
      descripcion_pseudonimizada: 'El servidor no responde desde esta mañana',
      prioridad: 'alta',
      requiere_revision_humana: false,
      created_at: '2026-06-11T10:00:00Z',
      updated_at: '2026-06-11T10:00:00Z',
      sector: { id: 5, nombre: 'Sistemas', descripcion: null },
      estado: { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false },
      canal_origen: { id: 2, nombre: 'formulario web', descripcion: null },
    };
    const queryClientTarjeta = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
      <QueryClientProvider client={queryClientTarjeta}>
        <SuccessCard
          incidente={incidenteConfirmado}
          nombreUsuario="María"
          onNuevoReporte={vi.fn()}
        />
      </QueryClientProvider>
    );
    expect(await screen.findByText('Sector Asignado por IA')).toBeInTheDocument();
  });
});
