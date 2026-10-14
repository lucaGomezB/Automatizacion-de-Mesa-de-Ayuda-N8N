/**
 * Pruebas de la seccion de comentarios del detalle (c-86, FIH-003).
 *
 * La capa de servicios esta mockeada. Se verifica el formato de presentacion
 * (`HH:MM:SS DD/MM/AAAA : {texto}`, separador `----------`), el alta de un
 * comentario y el manejo de denegaciones (403/404) sin exponer el recurso.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { ComentariosIncidente } from './ComentariosIncidente';
import { createTestQueryClient } from '@/test/utils';
import * as incidentesService from '@/services/incidentesService';
import type { ComentarioRead } from '@/types/comentario';

vi.mock('@/services/incidentesService', () => ({
  listarComentarios: vi.fn(),
  agregarComentario: vi.fn(),
}));

function comentario(overrides: Partial<ComentarioRead>): ComentarioRead {
  return {
    id: 1,
    incidente_id: 12,
    autor_empleado_id: 3,
    texto: 'Comentario',
    created_at: '2026-06-11T09:00:00Z',
    ...overrides,
  };
}

function renderSeccion() {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <ComentariosIncidente incidenteId={12} />
    </QueryClientProvider>
  );
}

describe('ComentariosIncidente', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('muestra los comentarios con el formato y el separador ----------', async () => {
    vi.mocked(incidentesService.listarComentarios).mockResolvedValue([
      comentario({ id: 1, texto: 'Primero', created_at: '2026-06-11T09:00:00Z' }),
      comentario({ id: 2, texto: 'Segundo', created_at: '2026-06-11T10:00:00Z' }),
    ]);

    renderSeccion();

    expect(await screen.findByText('06:00:00 11/06/2026 : Primero')).toBeInTheDocument();
    expect(screen.getByText('07:00:00 11/06/2026 : Segundo')).toBeInTheDocument();
    expect(screen.getByText('----------')).toBeInTheDocument();
  });

  it('agrega un comentario y refleja la nueva entrada formateada', async () => {
    const user = userEvent.setup();
    vi.mocked(incidentesService.listarComentarios)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        comentario({ id: 9, texto: 'Nuevo', created_at: '2026-06-11T11:00:00Z' }),
      ]);
    vi.mocked(incidentesService.agregarComentario).mockResolvedValue(
      comentario({ id: 9, texto: 'Nuevo', created_at: '2026-06-11T11:00:00Z' })
    );

    renderSeccion();

    await waitFor(() => expect(screen.getByText(/sin comentarios/i)).toBeInTheDocument());

    await user.type(screen.getByLabelText(/nuevo comentario/i), 'Nuevo');
    await user.click(screen.getByRole('button', { name: /agregar comentario/i }));

    await waitFor(() =>
      expect(incidentesService.agregarComentario).toHaveBeenCalledWith(12, 'Nuevo')
    );
    expect(await screen.findByText('08:00:00 11/06/2026 : Nuevo')).toBeInTheDocument();
  });

  it('ante un 403 al agregar muestra el error sin asumir exito', async () => {
    const user = userEvent.setup();
    vi.mocked(incidentesService.listarComentarios).mockResolvedValue([]);
    vi.mocked(incidentesService.agregarComentario).mockRejectedValue({
      isAxiosError: true,
      response: { status: 403, data: {} },
    });

    renderSeccion();

    await waitFor(() => expect(screen.getByText(/sin comentarios/i)).toBeInTheDocument());
    await user.type(screen.getByLabelText(/nuevo comentario/i), 'Intento');
    await user.click(screen.getByRole('button', { name: /agregar comentario/i }));

    expect(await screen.findByText(/no tenés permiso/i)).toBeInTheDocument();
  });

  it('ante un 404 al listar no muestra comentarios ni expone el recurso', async () => {
    vi.mocked(incidentesService.listarComentarios).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404, data: {} },
    });

    renderSeccion();

    expect(await screen.findByText(/no existe/i)).toBeInTheDocument();
    expect(screen.queryByText(/^#\d/)).not.toBeInTheDocument();
  });
});