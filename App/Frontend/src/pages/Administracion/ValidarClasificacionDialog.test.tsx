/**
 * Pruebas de ValidarClasificacionDialog (c-83).
 *
 * Cubre:
 *   - FE 3: tras validar debe invalidarse la query del detalle del incidente afectado.
 *   - FRH-001/002/003: el dialogo enriquece la validacion con la descripcion
 *     pseudonimizada, los metadatos del incidente y la clasificacion completa.
 *   - FRH-005: carga compuesta y error 403/404 con reintento sin exponer el recurso.
 *   - FRH-006/007: validacion multi-etiqueta editable por nombres canonicos.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { ValidarClasificacionDialog } from './ValidarClasificacionDialog';
import { createTestQueryClient } from '@/test/utils';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as incidentesService from '@/services/incidentesService';
import * as catalogosService from '@/services/catalogosService';
import { REVISION_PENDIENTE_QUERY_KEY } from '@/hooks/useRevisionPendiente';
import { INCIDENTES_QUERY_KEY } from '@/hooks/useIncidentes';
import type { ClasificacionLogRead } from '@/types/clasificacion';
import type { IncidenteRead } from '@/types/incidente';

vi.mock('@/services/clasificacionesService', () => ({
  validarClasificacion: vi.fn(),
  listarClasificacionesPorIncidente: vi.fn(),
}));

vi.mock('@/services/incidentesService', () => ({
  obtenerIncidente: vi.fn(),
}));

vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));

const mockClasificacion: ClasificacionLogRead = {
  id: 5,
  incidente_id: 12,
  confianza: 0.42,
  etapa: 'gemini',
  requiere_revision_humana: true,
  respuesta_raw: '{"sector_predicho":"Sistemas","confianza":0.42}',
  created_at: '2026-06-11T09:00:00Z',
  sector_predicho: { id: 1, nombre: 'Sistemas', descripcion: null },
  sector_validado: null,
  sectores_predichos: [],
  sectores_validados: [],
};

const mockIncidente: IncidenteRead = {
  id: 12,
  descripcion_pseudonimizada: 'La impresora del sector no responde desde ayer.',
  prioridad: 'media',
  requiere_revision_humana: true,
  created_at: '2026-06-11T09:00:00Z',
  updated_at: '2026-06-11T10:00:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  sectores_adicionales: [{ id: 2, nombre: 'Bases de Datos', descripcion: null }],
  estado: { id: 2, nombre: 'En Proceso', descripcion: null, es_terminal: false },
  canal_origen: { id: 1, nombre: 'Correo electrónico', descripcion: null },
};

const SECTORES = [
  { id: 1, nombre: 'Sistemas' },
  { id: 2, nombre: 'Bases de Datos' },
  { id: 3, nombre: 'Soporte Tecnico Software' },
];

function renderDialog(onClose = vi.fn()) {
  const queryClient = createTestQueryClient();
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <ValidarClasificacionDialog open clasificacion={mockClasificacion} onClose={onClose} />
    </QueryClientProvider>
  );
  return { ...utils, queryClient, onClose };
}

describe('ValidarClasificacionDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue(mockIncidente);
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([
      mockClasificacion,
    ]);
  });

  it('invalida el detalle del incidente tras validar la clasificacion', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue({
      ...mockClasificacion,
      sector_validado: { id: 1, nombre: 'Sistemas', descripcion: null },
    });

    const { queryClient } = renderDialog();
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const user = userEvent.setup();

    await user.click(
      screen.getByRole('button', { name: /confirmar predicción|guardar corrección/i })
    );

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['incidente-detalle', 12],
      });
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: ['clasificaciones-historial', 12],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [REVISION_PENDIENTE_QUERY_KEY],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: [INCIDENTES_QUERY_KEY],
    });
  });

  // ---- FRH-001/002/003: enriquecimiento ----

  it('muestra la descripcion pseudonimizada y los metadatos del incidente', async () => {
    renderDialog();

    expect(
      await screen.findByText(/la impresora del sector no responde/i)
    ).toBeInTheDocument();
    expect(screen.getByText('En Proceso')).toBeInTheDocument();
    expect(screen.getByText('Sectores Adicionales')).toBeInTheDocument();
  });

  it('muestra la clasificacion completa incluida la respuesta raw', async () => {
    renderDialog();

    expect(await screen.findByText(/clasificación automática/i)).toBeInTheDocument();
    expect(screen.getByText('42%')).toBeInTheDocument();
    expect(screen.getByText('Gemini 2.5 Flash')).toBeInTheDocument();
    expect(screen.getByText(/"sector_predicho"/)).toBeInTheDocument();
  });

  it('consulta el detalle del incidente y el historial con las query keys compartidas', async () => {
    renderDialog();

    await waitFor(() => {
      expect(incidentesService.obtenerIncidente).toHaveBeenCalledWith(12);
      expect(clasificacionesService.listarClasificacionesPorIncidente).toHaveBeenCalledWith(12);
    });
  });

  // ---- FRH-005: carga compuesta y manejo de 403/404 ----

  it('muestra la carga compuesta mientras el detalle o el historial estan pendientes', () => {
    vi.mocked(incidentesService.obtenerIncidente).mockReturnValue(new Promise(() => {}));
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockReturnValue(
      new Promise(() => {})
    );

    renderDialog();

    expect(screen.getByText(/cargando información del incidente/i)).toBeInTheDocument();
    expect(screen.queryByText(/la impresora del sector/i)).not.toBeInTheDocument();
  });

  it('trata un 404 como error con reintento sin exponer el recurso', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });

    renderDialog();

    expect(await screen.findByText(/el recurso solicitado no existe/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    expect(screen.queryByText(/la impresora del sector/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /confirmar predicción|guardar corrección/i })
    ).not.toBeInTheDocument();
  });

  it('trata un 403 como error con reintento sin exponer el recurso', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });

    renderDialog();

    expect(await screen.findByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    expect(screen.queryByText(/la impresora del sector/i)).not.toBeInTheDocument();
  });

  // ---- TRIANGULACION ----

  it('omite la respuesta raw cuando la clasificacion no la aporta', async () => {
    vi.mocked(clasificacionesService.listarClasificacionesPorIncidente).mockResolvedValue([
      { ...mockClasificacion, respuesta_raw: null },
    ]);

    renderDialog();

    expect(await screen.findByText(/clasificación automática/i)).toBeInTheDocument();
    expect(screen.queryByText(/respuesta raw de gemini/i)).not.toBeInTheDocument();
  });

  it('muestra la senal de revision humana cuando el incidente la requiere', async () => {
    renderDialog();

    expect(await screen.findByText(/requiere revision humana/i)).toBeInTheDocument();
  });

  it('no muestra la senal de revision humana cuando el incidente no la requiere', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue({
      ...mockIncidente,
      requiere_revision_humana: false,
    });

    renderDialog();

    expect(await screen.findByText(/la impresora del sector/i)).toBeInTheDocument();
    expect(screen.queryByText(/requiere revision humana/i)).not.toBeInTheDocument();
  });

  it('omite los sectores adicionales del incidente cuando no hay ninguno', async () => {
    vi.mocked(incidentesService.obtenerIncidente).mockResolvedValue({
      ...mockIncidente,
      sectores_adicionales: [],
    });

    renderDialog();

    expect(await screen.findByText(/la impresora del sector/i)).toBeInTheDocument();
    expect(screen.queryByText('Sectores Adicionales')).not.toBeInTheDocument();
  });

  // ---- FRH-006/007: validacion multi-etiqueta editable ----

  it('ofrece el multi-select de adicionales desde el catalogo excluyendo el principal', async () => {
    renderDialog();

    const grupo = await screen.findByRole('group', { name: /sectores adicionales/i });
    expect(within(grupo).getByRole('button', { name: 'Bases de Datos' })).toBeInTheDocument();
    expect(
      within(grupo).getByRole('button', { name: 'Soporte Tecnico Software' })
    ).toBeInTheDocument();
    // El principal preseleccionado ('Sistemas') no es una opcion adicional.
    expect(within(grupo).queryByRole('button', { name: 'Sistemas' })).not.toBeInTheDocument();
  });

  it('al confirmar envia sector_validado y sectores_adicionales por nombres canonicos', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue({
      ...mockClasificacion,
      sector_validado: { id: 1, nombre: 'Sistemas', descripcion: null },
    });
    const user = userEvent.setup();

    renderDialog();

    const grupo = await screen.findByRole('group', { name: /sectores adicionales/i });
    await user.click(within(grupo).getByRole('button', { name: 'Bases de Datos' }));
    await user.click(
      screen.getByRole('button', { name: /confirmar predicción|guardar corrección/i })
    );

    await waitFor(() => {
      expect(clasificacionesService.validarClasificacion).toHaveBeenCalledWith(5, {
        sector_validado: 'Sistemas',
        sectores_adicionales: ['Bases de Datos'],
      });
    });
  });

  it('permite deseleccionar un adicional y no lo envia en el payload', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue(mockClasificacion);
    const user = userEvent.setup();

    renderDialog();

    const grupo = await screen.findByRole('group', { name: /sectores adicionales/i });
    const botonBd = within(grupo).getByRole('button', { name: 'Bases de Datos' });

    await user.click(botonBd);
    expect(botonBd).toHaveAttribute('aria-pressed', 'true');
    await user.click(botonBd);
    expect(botonBd).toHaveAttribute('aria-pressed', 'false');

    await user.click(
      screen.getByRole('button', { name: /confirmar predicción|guardar corrección/i })
    );

    await waitFor(() => {
      expect(clasificacionesService.validarClasificacion).toHaveBeenCalledWith(5, {
        sector_validado: 'Sistemas',
        sectores_adicionales: [],
      });
    });
  });

  it('confirmar sin adicionales envia sectores_adicionales como lista vacia', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue(mockClasificacion);
    const user = userEvent.setup();

    renderDialog();

    await screen.findByRole('group', { name: /sectores adicionales/i });
    await user.click(
      screen.getByRole('button', { name: /confirmar predicción|guardar corrección/i })
    );

    await waitFor(() => {
      expect(clasificacionesService.validarClasificacion).toHaveBeenCalledWith(5, {
        sector_validado: 'Sistemas',
        sectores_adicionales: [],
      });
    });
  });

  it('cambiar el principal actualiza las opciones y elimina el duplicado del conjunto adicional', async () => {
    vi.mocked(clasificacionesService.validarClasificacion).mockResolvedValue(mockClasificacion);
    const user = userEvent.setup();

    renderDialog();

    const grupo = await screen.findByRole('group', { name: /sectores adicionales/i });
    // Marca 'Bases de Datos' como adicional...
    await user.click(within(grupo).getByRole('button', { name: 'Bases de Datos' }));

    // ...y luego lo elige como principal: debe desaparecer de las opciones adicionales.
    await user.click(screen.getByRole('combobox'));
    await user.click(await screen.findByRole('option', { name: 'Bases de Datos' }));

    const grupoActualizado = screen.getByRole('group', { name: /sectores adicionales/i });
    expect(
      within(grupoActualizado).queryByRole('button', { name: 'Bases de Datos' })
    ).not.toBeInTheDocument();
    expect(within(grupoActualizado).getByRole('button', { name: 'Sistemas' })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /guardar corrección/i }));

    await waitFor(() => {
      expect(clasificacionesService.validarClasificacion).toHaveBeenCalledWith(5, {
        sector_validado: 'Bases de Datos',
        sectores_adicionales: [],
      });
    });
  });
});
