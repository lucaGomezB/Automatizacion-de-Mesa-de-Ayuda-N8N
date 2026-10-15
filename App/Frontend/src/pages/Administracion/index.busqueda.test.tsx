/**
 * Pruebas de la barra de busqueda del Panel de Administracion (c-88, FIS-001/FIS-002).
 *
 * Cubren: disponibilidad del campo, envio del termino como `q` por la cadena
 * `IncidenteListParams -> useIncidentes -> listarIncidentes`, combinacion con los
 * filtros, reinicio de la paginacion al cambiar el termino, estado vacio y
 * limpieza del termino junto con los filtros.
 *
 * Se usan timers reales: el debounce es de 300 ms y `waitFor` espera la emision.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import AdministracionPage from './index';
import * as incidentesService from '@/services/incidentesService';
import * as clasificacionesService from '@/services/clasificacionesService';
import * as catalogosService from '@/services/catalogosService';
import type { IncidenteListItem } from '@/types/incidente';

vi.mock('@/services/incidentesService', () => ({
  listarIncidentes: vi.fn(),
  verificarSaludApi: vi.fn(),
}));
vi.mock('@/services/clasificacionesService', () => ({
  listarRevisionPendiente: vi.fn(),
  contarRevisionPendiente: vi.fn(),
  validarClasificacion: vi.fn(),
}));
vi.mock('@/services/catalogosService', () => ({
  listarSectores: vi.fn(),
}));
vi.mock('@/hooks/useHealthCheck', () => ({
  useHealthCheck: () => ({ data: undefined, isError: false, isPending: true }),
}));
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

const PAGE_SIZE = 20;
const sectorSistemas = { id: 1, nombre: 'Sistemas', descripcion: null };
const estadoNuevo = { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false };

function makeItem(id: number): IncidenteListItem {
  return {
    id,
    prioridad: 'media',
    requiere_revision_humana: false,
    created_at: '2026-06-11T10:00:00Z',
    sector: sectorSistemas,
    estado: estadoNuevo,
  };
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AdministracionPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

/** Espera a que transcurra el debounce de 300 ms, dentro de `act`. */
const esperarDebounce = () =>
  act(() => new Promise((resolve) => setTimeout(resolve, 450)));

/** Ultimo conjunto de parametros con que se invoco listarIncidentes. */
function ultimaLlamada(): Record<string, unknown> {
  const calls = vi.mocked(incidentesService.listarIncidentes).mock.calls;
  const ultima = calls[calls.length - 1]?.[0];
  if (!ultima) throw new Error('no se registro ninguna llamada a listarIncidentes');
  return ultima as Record<string, unknown>;
}

describe('AdministracionPage - barra de busqueda (c-88)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(clasificacionesService.listarRevisionPendiente).mockResolvedValue([]);
    vi.mocked(clasificacionesService.contarRevisionPendiente).mockResolvedValue(0);
    vi.mocked(catalogosService.listarSectores).mockResolvedValue([sectorSistemas]);
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([makeItem(1)]);
  });

  it('muestra el campo de busqueda de texto', async () => {
    renderPage();
    expect(screen.getByLabelText(/buscar incidentes/i)).toBeInTheDocument();
  });

  it('envia el termino como q por la capa de datos existente', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());
    await user.type(screen.getByLabelText(/buscar incidentes/i), 'correo');
    await esperarDebounce();

    await waitFor(() => expect(ultimaLlamada().q).toBe('correo'));
  });

  it('combina el termino con los filtros activos', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());

    // Filtro de prioridad (tercer combobox: Estado, Sector, Prioridad).
    await user.click(screen.getAllByRole('combobox')[2]);
    await user.click(await screen.findByRole('option', { name: 'Alta' }));

    await user.type(screen.getByLabelText(/buscar incidentes/i), 'correo');
    await esperarDebounce();

    await waitFor(() => {
      const llamada = ultimaLlamada();
      expect(llamada.q).toBe('correo');
      expect(llamada.prioridad).toBe('alta');
    });
  });

  it('un termino de 1 caracter no dispara busqueda con q', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());
    await user.type(screen.getByLabelText(/buscar incidentes/i), 'c');
    await esperarDebounce();

    const conQ = vi
      .mocked(incidentesService.listarIncidentes)
      .mock.calls.filter(([p]) => (p as { q?: string }).q !== undefined);
    expect(conQ).toHaveLength(0);
  });

  it('cambiar la busqueda reinicia la paginacion a la primera pagina', async () => {
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue(
      Array.from({ length: PAGE_SIZE }, (_, i) => makeItem(i + 1))
    );
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /siguiente/i }));
    await waitFor(() => expect(ultimaLlamada().offset).toBe(PAGE_SIZE));

    await user.type(screen.getByLabelText(/buscar incidentes/i), 'correo');
    await esperarDebounce();

    await waitFor(() => {
      const llamada = ultimaLlamada();
      expect(llamada.q).toBe('correo');
      expect(llamada.offset).toBe(0);
    });
  });

  it('la busqueda sin resultados muestra un estado vacio neutro', async () => {
    const user = userEvent.setup();
    vi.mocked(incidentesService.listarIncidentes).mockResolvedValue([]);
    renderPage();

    await user.type(screen.getByLabelText(/buscar incidentes/i), 'correo');
    await esperarDebounce();

    await waitFor(() =>
      expect(
        screen.getByText(/no hay incidentes que coincidan con la búsqueda o los filtros/i)
      ).toBeInTheDocument()
    );
  });

  it('limpiar filtros vacia tambien la busqueda y vuelve a la primera pagina', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => expect(screen.getByText('#00001')).toBeInTheDocument());

    const input = screen.getByLabelText(/buscar incidentes/i);
    await user.type(input, 'correo');
    await esperarDebounce();
    await waitFor(() => expect(ultimaLlamada().q).toBe('correo'));

    await user.click(screen.getByRole('button', { name: /limpiar filtros/i }));

    await waitFor(() => {
      expect(ultimaLlamada().q).toBeUndefined();
      expect(ultimaLlamada().offset).toBe(0);
    });
    expect(screen.getByLabelText(/buscar incidentes/i)).toHaveValue('');
  });
});
