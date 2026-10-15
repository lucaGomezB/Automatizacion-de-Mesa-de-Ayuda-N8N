/**
 * Pruebas del control de asignacion de prioridad en el panel de administracion
 * (c-90, FR-RBAC-009).
 *
 * Verifica que el control (y la opcion `critica`) se ofrece UNICAMENTE a los
 * roles con permiso (`mesa_de_ayuda`, `administrador_directorio`), que un rol
 * sin permiso no la ofrece, que la asignacion invoca el backend y que un 403 se
 * maneja sin asumir exito (FR-RBAC-005).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { TicketDetailDialog } from './TicketDetailDialog';
import { createTestQueryClient } from '@/test/utils';
import * as incidentesService from '@/services/incidentesService';
import * as clasificacionesService from '@/services/clasificacionesService';
import { useAuth } from '@/contexts/AuthContext';
import type { IncidenteRead } from '@/types/incidente';

vi.mock('@/services/incidentesService', () => ({
  obtenerIncidente: vi.fn(),
  listarComentarios: vi.fn(),
  agregarComentario: vi.fn(),
  cerrarPorSector: vi.fn(),
  cerrarGlobal: vi.fn(),
  rehabilitarIncidente: vi.fn(),
  editarEstadoIncidente: vi.fn(),
  borrarIncidente: vi.fn(),
  actualizarPrioridadIncidente: vi.fn(),
}));

vi.mock('@/services/clasificacionesService', () => ({
  listarClasificacionesPorIncidente: vi.fn(),
}));

vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

const mockIncidente: IncidenteRead = {
  id: 12,
  descripcion_pseudonimizada: 'No puedo acceder al sistema [NOMBRE] desde ayer.',
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T09:00:00Z',
  updated_at: '2026-06-11T10:30:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  sectores_adicionales: [],
  estado: { id: 2, nombre: 'En Proceso', descripcion: null, es_terminal: false },
  canal_origen: { id: 1, nombre: 'Correo electrónico', descripcion: null },
};

function authConRol(rol: string) {
  return {
    token: 't',
    username: 'u',
    isAuthenticated: true,
    mfaRequired: false,
    rol,
    alcance: { modo: 'GLOBAL' as const },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  };
}

function renderDialog() {
  render(
    <QueryClientProvider client={createTestQueryClient()}>
      <TicketDetailDialog open incidenteId={12} onClose={vi.fn()} />
    </QueryClientProvider>
  );
}

describe('TicketDetailDialog - asignacion de prioridad (c-90)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarComentarios).mockResolvedValue([]);
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue(mockIncidente);
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([]);
  });

  it('mesa_de_ayuda ve el control y la opcion critica', async () => {
    useAuthMock.mockReturnValue(authConRol('mesa_de_ayuda'));
    renderDialog();

    expect(
      await screen.findByRole('button', { name: /crítica/i })
    ).toBeInTheDocument();
  });

  it('administrador_directorio ve el control y la opcion critica', async () => {
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    renderDialog();

    expect(
      await screen.findByRole('button', { name: /crítica/i })
    ).toBeInTheDocument();
  });

  it('usuario_final no ve la opcion critica', async () => {
    useAuthMock.mockReturnValue(authConRol('usuario_final'));
    renderDialog();

    await screen.findByText(/no puedo acceder al sistema/i);
    expect(screen.queryByRole('button', { name: /crítica/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/asignar prioridad/i)).not.toBeInTheDocument();
  });

  it('asignar critica invoca el backend con el id y la prioridad', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('mesa_de_ayuda'));
    vi.mocked(incidentesService.actualizarPrioridadIncidente).mockResolvedValue({
      ...mockIncidente,
      prioridad: 'critica',
    });
    renderDialog();

    await user.click(await screen.findByRole('button', { name: /crítica/i }));

    await waitFor(() =>
      expect(incidentesService.actualizarPrioridadIncidente).toHaveBeenCalledWith(12, 'critica')
    );
  });

  it('un 403 del backend se maneja como acceso denegado sin asumir exito', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('mesa_de_ayuda'));
    vi.mocked(incidentesService.actualizarPrioridadIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });
    renderDialog();

    await user.click(await screen.findByRole('button', { name: /crítica/i }));

    expect(await screen.findByText(/no tenés permiso/i)).toBeInTheDocument();
  });
});
