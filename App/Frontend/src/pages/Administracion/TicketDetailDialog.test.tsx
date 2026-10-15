/**
 * Pruebas de TicketDetailDialog tras la extraccion del detalle compartido (c-83).
 *
 * Verifica FRH-004: el detalle del ticket muestra el MISMO conjunto de campos que
 * la validacion humana (via `DetalleIncidente`) y mantiene el manejo de carga y de
 * error (403/404) sin exponer el recurso.
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
import type { ClasificacionLogRead } from '@/types/clasificacion';

vi.mock('@/services/incidentesService', () => ({
  obtenerIncidente: vi.fn(),
  listarComentarios: vi.fn(),
  agregarComentario: vi.fn(),
  cerrarPorSector: vi.fn(),
  cerrarGlobal: vi.fn(),
  rehabilitarIncidente: vi.fn(),
  editarEstadoIncidente: vi.fn(),
  borrarIncidente: vi.fn(),
}));

vi.mock('@/services/clasificacionesService', () => ({
  listarClasificacionesPorIncidente: vi.fn(),
}));

vi.mock('@/contexts/AuthContext', () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

const mockIncidente: IncidenteRead = {
  id: 12,
  descripcion_pseudonimizada: 'No puedo acceder al sistema [NOMBRE] desde ayer.',
  prioridad: 'alta',
  requiere_revision_humana: true,
  created_at: '2026-06-11T09:00:00Z',
  updated_at: '2026-06-11T10:30:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  sectores_adicionales: [{ id: 2, nombre: 'Bases de Datos', descripcion: null }],
  estado: { id: 2, nombre: 'En Proceso', descripcion: null, es_terminal: false },
  canal_origen: { id: 1, nombre: 'Correo electrónico', descripcion: null },
};

const mockClasificacion: ClasificacionLogRead = {
  id: 5,
  incidente_id: 12,
  confianza: 0.42,
  etapa: 'gemini',
  requiere_revision_humana: true,
  respuesta_raw: '{"sector_predicho":"Soporte Tecnico Hardware"}',
  created_at: '2026-06-11T09:00:00Z',
  sector_predicho: { id: 3, nombre: 'Soporte Tecnico Hardware', descripcion: null },
  sector_validado: null,
  sectores_predichos: [],
  sectores_validados: [],
};

function renderDialog(
  client = createTestQueryClient(),
  onClose = vi.fn()
) {
  render(
    <QueryClientProvider client={client}>
      <TicketDetailDialog open incidenteId={12} onClose={onClose} />
    </QueryClientProvider>
  );
  return { client, onClose };
}

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

describe('TicketDetailDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthMock.mockReturnValue({
      token: 't',
      username: 'u',
      isAuthenticated: true,
      mfaRequired: false,
      rol: 'mesa_de_ayuda',
      alcance: { modo: 'GLOBAL' },
      login: vi.fn(),
      verifyMfa: vi.fn(),
      enrollMfa: vi.fn(),
      refreshIdentidad: vi.fn(),
      logout: vi.fn(),
    });
    vi.mocked(incidentesService.listarComentarios).mockResolvedValue([]);
  });

  it('muestra los campos del detalle compartido (descripcion, metadatos y clasificacion)', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue(mockIncidente);
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([
      mockClasificacion,
    ]);

    renderDialog();

    expect(await screen.findByText(/no puedo acceder al sistema/i)).toBeInTheDocument();
    expect(screen.getByText('En Proceso')).toBeInTheDocument();
    expect(screen.getByText('Bases de Datos')).toBeInTheDocument();
    expect(screen.getByText('Soporte Tecnico Hardware')).toBeInTheDocument();
    expect(screen.getByText('42%')).toBeInTheDocument();
    expect(screen.getByText(/"sector_predicho"/)).toBeInTheDocument();
  });

  it('muestra el estado de carga mientras las consultas estan pendientes', () => {
    vi.mocked(incidentesService.obtenerIncidente).mockReturnValue(new Promise(() => {}));
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockReturnValue(
      new Promise(() => {})
    );

    renderDialog();

    expect(screen.getByText(/cargando información del incidente/i)).toBeInTheDocument();
  });

  it('trata un 404 como error sin exponer datos del recurso y ofrece reintento', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([]);

    renderDialog();

    expect(await screen.findByText(/el recurso solicitado no existe/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    expect(screen.queryByText(/no puedo acceder al sistema/i)).not.toBeInTheDocument();
  });
});

describe('TicketDetailDialog - accion de borrado logico (c-87, FR-RBAC-006)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(incidentesService.listarComentarios).mockResolvedValue([]);
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue(mockIncidente);
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([
      mockClasificacion,
    ]);
  });

  it('el administrador ve la accion de borrado', async () => {
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    renderDialog();

    expect(
      await screen.findByRole('button', { name: /eliminar incidente/i })
    ).toBeInTheDocument();
  });

  it('mesa_de_ayuda no ve la accion de borrado', async () => {
    useAuthMock.mockReturnValue(authConRol('mesa_de_ayuda'));
    renderDialog();

    await screen.findByText(/no puedo acceder al sistema/i);
    expect(
      screen.queryByRole('button', { name: /eliminar incidente/i })
    ).not.toBeInTheDocument();
  });

  it('usuario_final no ve la accion de borrado', async () => {
    useAuthMock.mockReturnValue(authConRol('usuario_final'));
    renderDialog();

    await screen.findByText(/no puedo acceder al sistema/i);
    expect(
      screen.queryByRole('button', { name: /eliminar incidente/i })
    ).not.toBeInTheDocument();
  });

  it('exige confirmacion antes de invocar el backend', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    renderDialog();

    await user.click(await screen.findByRole('button', { name: /eliminar incidente/i }));

    expect(screen.getByRole('button', { name: /confirmar borrado/i })).toBeInTheDocument();
    expect(incidentesService.borrarIncidente).not.toHaveBeenCalled();
  });

  it('cancelar no invoca el backend y el incidente permanece visible', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    renderDialog();

    await user.click(await screen.findByRole('button', { name: /eliminar incidente/i }));
    await user.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(incidentesService.borrarIncidente).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /eliminar incidente/i })).toBeInTheDocument();
  });

  it('confirmar invoca el borrado, invalida listados y cierra el dialogo', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    vi.mocked(incidentesService.borrarIncidente).mockResolvedValue(undefined);
    const { client, onClose } = renderDialog();
    const invalidar = vi.spyOn(client, 'invalidateQueries');

    await user.click(await screen.findByRole('button', { name: /eliminar incidente/i }));
    await user.click(screen.getByRole('button', { name: /confirmar borrado/i }));

    await waitFor(() =>
      expect(incidentesService.borrarIncidente).toHaveBeenCalledWith(12)
    );
    await waitFor(() => expect(invalidar).toHaveBeenCalled());
    await waitFor(() => expect(onClose).toHaveBeenCalled());
  });

  it('un 403 se maneja como acceso denegado sin asumir exito', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    vi.mocked(incidentesService.borrarIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });
    const { onClose } = renderDialog();

    await user.click(await screen.findByRole('button', { name: /eliminar incidente/i }));
    await user.click(screen.getByRole('button', { name: /confirmar borrado/i }));

    expect(await screen.findByText(/no tenés permiso/i)).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });

  it('un 404 se maneja como no encontrado sin asumir exito', async () => {
    const user = userEvent.setup();
    useAuthMock.mockReturnValue(authConRol('administrador_directorio'));
    vi.mocked(incidentesService.borrarIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });
    const { onClose } = renderDialog();

    await user.click(await screen.findByRole('button', { name: /eliminar incidente/i }));
    await user.click(screen.getByRole('button', { name: /confirmar borrado/i }));

    expect(await screen.findByText(/no existe/i)).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });
});
