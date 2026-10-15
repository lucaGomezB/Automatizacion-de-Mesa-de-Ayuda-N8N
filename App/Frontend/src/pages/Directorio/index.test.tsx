/**
 * Pruebas de la pagina del directorio (c-89, FDIR-002..006).
 *
 * La capa de servicios esta mockeada y la pagina se renderiza con un QueryClient
 * real: se ejercita la integracion pagina -> hook -> servicio.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import DirectorioPage from './index';
import * as directorioService from '@/services/directorioService';
import * as catalogosService from '@/services/catalogosService';
import { createTestQueryClient } from '@/test/utils';
import type { Empleado } from '@/types/directorio';

vi.mock('@/services/directorioService');
vi.mock('@/services/catalogosService', () => ({ listarSectores: vi.fn() }));
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    token: 't',
    username: 'admin',
    isAuthenticated: true,
    mfaRequired: false,
    rol: 'administrador_directorio',
    alcance: { modo: 'GLOBAL' },
    login: vi.fn(),
    verifyMfa: vi.fn(),
    enrollMfa: vi.fn(),
    refreshIdentidad: vi.fn(),
    logout: vi.fn(),
  }),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));

const SECTORES = [{ id: 1, nombre: 'Sistemas' }];

const anaActiva: Empleado = {
  id: 1,
  legajo: '0001',
  nombre: 'Ana Gomez',
  email: 'ana.gomez@example.com',
  telefono: null,
  sector_id: 1,
  rol: 'usuario_final',
  activo: true,
};

const betoInactivo: Empleado = {
  id: 2,
  legajo: '0002',
  nombre: 'Beto Diaz',
  email: 'beto.diaz@example.com',
  telefono: null,
  sector_id: null,
  rol: 'mesa_de_ayuda',
  activo: false,
};

function renderPage() {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DirectorioPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('DirectorioPage - listado (FDIR-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
  });

  it('lista los empleados con legajo, nombre, email, sector, rol y estado', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([
      anaActiva,
      betoInactivo,
    ]);

    renderPage();

    expect(await screen.findByText('0001')).toBeInTheDocument();
    expect(screen.getByText('Ana Gomez')).toBeInTheDocument();
    expect(screen.getByText('ana.gomez@example.com')).toBeInTheDocument();
    expect(screen.getByText('Sistemas')).toBeInTheDocument();
    expect(screen.getByText('Usuario final')).toBeInTheDocument();
    expect(screen.getByText('Activo')).toBeInTheDocument();
    expect(screen.getByText('0002')).toBeInTheDocument();
    expect(screen.getByText('Mesa de ayuda')).toBeInTheDocument();
    expect(screen.getByText('Inactivo')).toBeInTheDocument();
  });

  it('muestra el estado de carga mientras la consulta esta pendiente', () => {
    vi.mocked(directorioService.listarEmpleados).mockReturnValue(new Promise(() => {}));

    renderPage();

    expect(screen.getByText(/cargando empleados/i)).toBeInTheDocument();
    expect(screen.queryByText('Ana Gomez')).not.toBeInTheDocument();
  });

  it('muestra un error con reintento cuando la consulta falla', async () => {
    vi.mocked(directorioService.listarEmpleados).mockRejectedValue(
      new Error('Network Error')
    );

    renderPage();

    expect(await screen.findByText(/error al cargar/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
  });

  it('muestra un estado vacio cuando no hay empleados', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([]);

    renderPage();

    expect(await screen.findByText(/sin empleados/i)).toBeInTheDocument();
  });
});

describe('DirectorioPage - filtro y paginacion (FDIR-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
  });

  it('consulta solo_activos=false por defecto y cambia a true con el filtro', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([anaActiva]);
    const user = userEvent.setup();

    renderPage();

    await screen.findByText('Ana Gomez');
    expect(directorioService.listarEmpleados).toHaveBeenCalledWith({ soloActivos: false });

    await user.click(screen.getByRole('combobox', { name: /filtro de estado/i }));
    await user.click(await screen.findByRole('option', { name: 'Solo activos' }));

    await waitFor(() => {
      expect(directorioService.listarEmpleados).toHaveBeenCalledWith({ soloActivos: true });
    });
  });

  it('pagina el listado en bloques de 20 y permite avanzar de pagina', async () => {
    const muchos: Empleado[] = Array.from({ length: 25 }, (_, i) => ({
      ...anaActiva,
      id: i + 1,
      legajo: String(i + 1).padStart(4, '0'),
      nombre: `Empleado ${i + 1}`,
      email: `empleado${i + 1}@example.com`,
    }));
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue(muchos);
    const user = userEvent.setup();

    renderPage();

    await screen.findByText('Empleado 1');
    expect(screen.queryByText('Empleado 21')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /siguiente/i }));

    expect(await screen.findByText('Empleado 21')).toBeInTheDocument();
    expect(screen.queryByText('Empleado 1')).not.toBeInTheDocument();
  });
});

describe('DirectorioPage - alta y edicion (FDIR-003/004)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([anaActiva]);
  });

  async function abrirAlta(user: ReturnType<typeof userEvent.setup>) {
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /nuevo empleado/i }));
    await user.type(screen.getByLabelText(/legajo/i), '0009');
    await user.type(screen.getByLabelText(/nombre/i), 'Carla Paz');
    await user.type(screen.getByLabelText(/email/i), 'carla.paz@example.com');
  }

  it('crea un empleado via POST /directorio/empleados', async () => {
    vi.mocked(directorioService.crearEmpleado).mockResolvedValue({
      ...anaActiva,
      id: 9,
      legajo: '0009',
      nombre: 'Carla Paz',
    });
    const user = userEvent.setup();

    renderPage();
    await abrirAlta(user);
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));

    await waitFor(() => {
      expect(directorioService.crearEmpleado).toHaveBeenCalledWith({
        legajo: '0009',
        nombre: 'Carla Paz',
        email: 'carla.paz@example.com',
        telefono: null,
        rol: 'usuario_final',
        sector_id: null,
      });
    });
  });

  it('muestra el error del backend sin perder los datos ingresados', async () => {
    vi.mocked(directorioService.crearEmpleado).mockRejectedValue({
      isAxiosError: true,
      response: { status: 422, data: { detail: 'El legajo ya existe.' } },
    });
    const user = userEvent.setup();

    renderPage();
    await abrirAlta(user);
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));

    expect(await screen.findByText(/el legajo ya existe/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/legajo/i)).toHaveValue('0009');
    expect(screen.getByLabelText(/nombre/i)).toHaveValue('Carla Paz');
  });

  it('edita un empleado via PATCH /directorio/empleados/{id}', async () => {
    vi.mocked(directorioService.actualizarEmpleado).mockResolvedValue({
      ...anaActiva,
      nombre: 'Ana Maria',
    });
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /editar ana gomez/i }));

    expect(screen.getByLabelText(/legajo/i)).toHaveValue('0001');
    await user.clear(screen.getByLabelText(/nombre/i));
    await user.type(screen.getByLabelText(/nombre/i), 'Ana Maria');
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }));

    await waitFor(() => {
      expect(directorioService.actualizarEmpleado).toHaveBeenCalledWith(
        1,
        expect.objectContaining({ nombre: 'Ana Maria' })
      );
    });
  });
});

describe('DirectorioPage - activar/desactivar (FDIR-004)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
    vi.mocked(directorioService.actualizarEmpleado).mockResolvedValue(anaActiva);
  });

  it('desactiva un empleado activo enviando activo=false', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([anaActiva]);
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /desactivar ana gomez/i }));

    await waitFor(() => {
      expect(directorioService.actualizarEmpleado).toHaveBeenCalledWith(1, { activo: false });
    });
  });

  it('reactiva un empleado inactivo enviando activo=true', async () => {
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([betoInactivo]);
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Beto Diaz');
    await user.click(screen.getByRole('button', { name: /reactivar beto diaz/i }));

    await waitFor(() => {
      expect(directorioService.actualizarEmpleado).toHaveBeenCalledWith(2, { activo: true });
    });
  });
});

describe('DirectorioPage - borrado ARCO y purga (FDIR-005/006)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(catalogosService.listarSectores).mockResolvedValue(SECTORES);
    vi.mocked(directorioService.listarEmpleados).mockResolvedValue([anaActiva]);
  });

  it('advierte irreversibilidad y NO borra al cancelar la confirmacion ARCO', async () => {
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /borrar ana gomez/i }));

    expect(await screen.findByText(/irreversible/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(directorioService.borrarEmpleadoArco).not.toHaveBeenCalled();
  });

  it('confirma el borrado ARCO y llama al servicio', async () => {
    vi.mocked(directorioService.borrarEmpleadoArco).mockResolvedValue(undefined);
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /borrar ana gomez/i }));
    await screen.findByText(/irreversible/i);
    await user.click(screen.getByRole('button', { name: /confirmar borrado/i }));

    await waitFor(() => {
      expect(directorioService.borrarEmpleadoArco).toHaveBeenCalledWith(1);
    });
  });

  it('exige confirmacion para la purga y muestra el conteo purgado', async () => {
    vi.mocked(directorioService.purgarDirectorio).mockResolvedValue({
      purgados: 3,
      ids: [1, 2, 3],
    });
    const user = userEvent.setup();

    renderPage();
    await screen.findByText('Ana Gomez');
    await user.click(screen.getByRole('button', { name: /purgar directorio/i }));

    const confirmar = await screen.findByRole('button', { name: /confirmar purga/i });
    await user.click(confirmar);

    await waitFor(() => {
      expect(directorioService.purgarDirectorio).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText(/se purgaron 3/i)).toBeInTheDocument();
  });
});
