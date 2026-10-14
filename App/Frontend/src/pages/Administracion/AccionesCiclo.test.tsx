/**
 * Pruebas de las acciones de ciclo en el detalle del incidente (c-86, D11 / FIH-002).
 *
 * La sesion (rol) se mockea; la capa de servicios tambien. Se verifica que:
 *   - `gestion_incidentes` vea "Cerrar para mi sector" y "Actualizar estado",
 *   - `mesa_de_ayuda` vea "Cerrar globalmente"/"Reabrir" y "Actualizar estado",
 *   - un usuario sin permisos no vea ninguna accion,
 *   - un 403 del backend se presente como error sin asumir exito (FIH-004).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AccionesCiclo } from './AccionesCiclo';
import * as incidentesService from '@/services/incidentesService';
import { useAuth } from '@/contexts/AuthContext';
import type { IncidenteRead } from '@/types/incidente';

vi.mock('@/services/incidentesService', () => ({
  cerrarPorSector: vi.fn(),
  cerrarGlobal: vi.fn(),
  rehabilitarIncidente: vi.fn(),
  editarEstadoIncidente: vi.fn(),
}));
vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

function authWithRol(rol: string | null) {
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

const incidenteAbierto: IncidenteRead = {
  id: 12,
  descripcion_pseudonimizada: 'No puedo acceder al sistema.',
  prioridad: 'alta',
  requiere_revision_humana: false,
  created_at: '2026-06-11T09:00:00Z',
  updated_at: '2026-06-11T10:30:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  sectores_adicionales: [],
  estado: { id: 2, nombre: 'en proceso', descripcion: null, es_terminal: false },
  canal_origen: null,
};

const incidenteCerrado: IncidenteRead = {
  ...incidenteAbierto,
  estado: { id: 5, nombre: 'cerrado', descripcion: null, es_terminal: true },
};

function renderAcciones(incidente: IncidenteRead) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <AccionesCiclo incidente={incidente} onMutated={vi.fn()} />
    </QueryClientProvider>
  );
}

describe('AccionesCiclo - permisos por rol', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('gestion_incidentes: cierra su sector y edita estado; no ve cierre global ni reabrir', () => {
    useAuthMock.mockReturnValue(authWithRol('gestion_incidentes'));
    renderAcciones(incidenteAbierto);

    expect(screen.getByRole('button', { name: /cerrar para mi sector/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /actualizar estado/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cerrar globalmente/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /reabrir/i })).not.toBeInTheDocument();
  });

  it('mesa_de_ayuda: cierra globalmente y edita estado; no ve cierre por sector', () => {
    useAuthMock.mockReturnValue(authWithRol('mesa_de_ayuda'));
    renderAcciones(incidenteAbierto);

    expect(screen.getByRole('button', { name: /cerrar globalmente/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /actualizar estado/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cerrar para mi sector/i })).not.toBeInTheDocument();
  });

  it('mesa_de_ayuda sobre un incidente cerrado: solo reabrir', () => {
    useAuthMock.mockReturnValue(authWithRol('mesa_de_ayuda'));
    renderAcciones(incidenteCerrado);

    expect(screen.getByRole('button', { name: /reabrir incidente/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cerrar globalmente/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /actualizar estado/i })).not.toBeInTheDocument();
  });

  it('usuario_final no ve ninguna accion de ciclo', () => {
    useAuthMock.mockReturnValue(authWithRol('usuario_final'));
    const { container } = renderAcciones(incidenteAbierto);

    expect(screen.queryByRole('button', { name: /cerrar/i })).not.toBeInTheDocument();
    expect(container).toBeEmptyDOMElement();
  });

  it('gestion no puede reabrir ni cerrar global aunque el incidente este cerrado', () => {
    useAuthMock.mockReturnValue(authWithRol('gestion_incidentes'));
    const { container } = renderAcciones(incidenteCerrado);

    expect(screen.queryByRole('button', { name: /reabrir/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /cerrar globalmente/i })).not.toBeInTheDocument();
    expect(container).toBeEmptyDOMElement();
  });
});

describe('AccionesCiclo - mutaciones y manejo de errores', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('cerrar por sector invoca el endpoint con el id del incidente', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authWithRol('gestion_incidentes'));
    vi.mocked(incidentesService.cerrarPorSector).mockResolvedValue(incidenteCerrado);
    renderAcciones(incidenteAbierto);

    await user.click(screen.getByRole('button', { name: /cerrar para mi sector/i }));

    await waitFor(() =>
      expect(incidentesService.cerrarPorSector).toHaveBeenCalledWith(12)
    );
  });

  it('un 403 del backend se presenta como error y no como exito', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authWithRol('gestion_incidentes'));
    vi.mocked(incidentesService.cerrarPorSector).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });
    renderAcciones(incidenteAbierto);

    await user.click(screen.getByRole('button', { name: /cerrar para mi sector/i }));

    expect(await screen.findByText(/no tenés permiso/i)).toBeInTheDocument();
  });

  it('un 404 (fuera de alcance) se presenta como error sin exponer el recurso', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authWithRol('gestion_incidentes'));
    vi.mocked(incidentesService.cerrarPorSector).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });
    renderAcciones(incidenteAbierto);

    await user.click(screen.getByRole('button', { name: /cerrar para mi sector/i }));

    expect(await screen.findByText(/no existe/i)).toBeInTheDocument();
  });
});