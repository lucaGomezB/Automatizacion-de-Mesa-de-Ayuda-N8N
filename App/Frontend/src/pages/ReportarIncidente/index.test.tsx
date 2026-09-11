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
import * as catalogosService from '@/services/catalogosService';
import type { SectorOpcion } from '@/types/catalog';

vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
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
});
