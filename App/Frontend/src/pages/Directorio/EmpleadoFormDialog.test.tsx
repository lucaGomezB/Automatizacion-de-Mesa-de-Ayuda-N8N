/**
 * Pruebas del formulario de empleado del directorio (c-89, FDIR-003).
 *
 * Cubre la validacion de campos obligatorios, el formato del email y la regla de
 * sector condicional: solo `gestion_incidentes` lo exige (D4/D7). El backend sigue
 * siendo la fuente de verdad; esta validacion es de UX.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { EmpleadoFormDialog } from './EmpleadoFormDialog';
import * as catalogosService from '@/services/catalogosService';
import { createTestQueryClient } from '@/test/utils';

vi.mock('@/services/catalogosService', () => ({ listarSectores: vi.fn() }));

const SECTORES = [{ id: 1, nombre: 'Sistemas' }];

function renderForm() {
  const onSubmit = vi.fn();
  const onClose = vi.fn();
  const queryClient = createTestQueryClient();
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <EmpleadoFormDialog
        open
        empleado={null}
        isPending={false}
        error={null}
        onClose={onClose}
        onSubmit={onSubmit}
      />
    </QueryClientProvider>
  );
  return { ...utils, onSubmit, onClose };
}

async function completarBasicos(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText(/legajo/i), '0009');
  await user.type(screen.getByLabelText(/nombre/i), 'Carla Paz');
  await user.type(screen.getByLabelText(/email/i), 'carla.paz@example.com');
}

describe('EmpleadoFormDialog - validacion (FDIR-003)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
  });

  it('bloquea el envio con legajo, nombre y email vacios y muestra los errores', async () => {
    const user = userEvent.setup();
    const { onSubmit } = renderForm();

    await user.click(screen.getByRole('button', { name: /guardar/i }));

    await waitFor(() => {
      expect(screen.getByText(/legajo es obligatorio/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/nombre es obligatorio/i)).toBeInTheDocument();
    expect(screen.getByText(/email es obligatorio/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('bloquea el envio con email de formato invalido', async () => {
    const user = userEvent.setup();
    const { onSubmit } = renderForm();

    await user.type(screen.getByLabelText(/legajo/i), '0009');
    await user.type(screen.getByLabelText(/nombre/i), 'Carla Paz');
    await user.type(screen.getByLabelText(/email/i), 'no-es-un-email');
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    await waitFor(() => {
      expect(screen.getByText(/formato/i)).toBeInTheDocument();
    });
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('gestion_incidentes exige sector y bloquea el envio hasta seleccionarlo', async () => {
    const user = userEvent.setup();
    const { onSubmit } = renderForm();

    await completarBasicos(user);
    await user.click(screen.getByRole('combobox', { name: /^rol/i }));
    await user.click(await screen.findByRole('option', { name: 'Gestion de incidentes' }));
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    await waitFor(() => {
      expect(screen.getByText(/sector es obligatorio/i)).toBeInTheDocument();
    });
    expect(onSubmit).not.toHaveBeenCalled();

    await user.click(screen.getByRole('combobox', { name: /^sector/i }));
    await user.click(await screen.findByRole('option', { name: 'Sistemas' }));
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        legajo: '0009',
        nombre: 'Carla Paz',
        email: 'carla.paz@example.com',
        telefono: null,
        rol: 'gestion_incidentes',
        sector_id: 1,
      });
    });
  });

  it('un rol sin requisito de sector permite enviar sin sector', async () => {
    const user = userEvent.setup();
    const { onSubmit } = renderForm();

    await completarBasicos(user);
    await user.click(screen.getByRole('button', { name: /guardar/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        legajo: '0009',
        nombre: 'Carla Paz',
        email: 'carla.paz@example.com',
        telefono: null,
        rol: 'usuario_final',
        sector_id: null,
      });
    });
  });
});
