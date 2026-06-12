/**
 * Pruebas de SuccessCard.
 * Verifica: número de ticket, badge del sector, nota de revisión humana.
 * listarClasificacionesPorIncidente está mockeado para control del query interno.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { SuccessCard } from './SuccessCard';
import * as clasificacionesService from '@/services/clasificacionesService';
import { renderWithClient } from '@/test/utils';
import type { IncidenteRead } from '@/types/incidente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

vi.mock('@/services/clasificacionesService');

const mockSector = { id: 1, nombre: 'Sistemas', descripcion: null };
const mockEstado = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };
const mockCanal = { id: 2, nombre: 'formulario web', descripcion: null };

function makeIncidente(overrides: Partial<IncidenteRead> = {}): IncidenteRead {
  return {
    id: 42,
    descripcion: 'El servidor de base de datos no responde desde esta mañana',
    prioridad: 'alta',
    requiere_revision_humana: false,
    created_at: '2026-06-11T10:00:00Z',
    updated_at: '2026-06-11T10:00:00Z',
    sector: mockSector,
    estado: mockEstado,
    canal_origen: mockCanal,
    ...overrides,
  };
}

const mockClasificacion: ClasificacionLogRead = {
  id: 10,
  incidente_id: 42,
  confianza: 0.88,
  etapa: 'gemini',
  requiere_revision_humana: false,
  respuesta_raw: '{"categoría":"Sistemas","confianza":0.88}',
  created_at: '2026-06-11T10:00:00Z',
  sector_predicho: mockSector,
  sector_validado: null,
};

describe('SuccessCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('muestra el número de ticket del incidente y el badge del sector asignado', async () => {
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValueOnce([
      mockClasificacion,
    ]);

    const incidente = makeIncidente({ id: 42, sector: mockSector });
    renderWithClient(
      <SuccessCard incidente={incidente} nombreUsuario="María" onNuevoReporte={vi.fn()} />
    );

    // El ticket se formatea como #00042
    expect(screen.getByText('#00042')).toBeInTheDocument();

    // El sector asignado (SectorBadge)
    await waitFor(() => {
      expect(screen.getByText('Sistemas')).toBeInTheDocument();
    });
  });

  it('muestra la nota de revisión humana cuando requiere_revision_humana es true', async () => {
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValueOnce([]);

    const incidente = makeIncidente({ id: 7, requiere_revision_humana: true, sector: null });
    renderWithClient(
      <SuccessCard incidente={incidente} nombreUsuario="Carlos" onNuevoReporte={vi.fn()} />
    );

    await waitFor(() => {
      expect(
        screen.getByText(/revisado manualmente/i)
      ).toBeInTheDocument();
    });
  });

  it('NO muestra la nota de revisión cuando requiere_revision_humana es false', async () => {
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValueOnce([
      mockClasificacion,
    ]);

    const incidente = makeIncidente({ id: 3, requiere_revision_humana: false });
    renderWithClient(
      <SuccessCard incidente={incidente} nombreUsuario="Laura" onNuevoReporte={vi.fn()} />
    );

    // No debe aparecer la nota de revisión manual
    await waitFor(() => {
      expect(screen.getByText('#00003')).toBeInTheDocument();
    });

    expect(screen.queryByText(/revisado manualmente/i)).not.toBeInTheDocument();
  });
});
