/**
 * Pruebas de la capa de servicios para incidentes.
 * Axis mockeado en el límite de red — sin solicitudes HTTP reales.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import {
  crearIncidente,
  listarIncidentes,
  obtenerIncidente,
  verificarSaludApi,
  listarHistorialCerrados,
  cerrarPorSector,
  cerrarGlobal,
  rehabilitarIncidente,
  editarEstadoIncidente,
  listarComentarios,
  agregarComentario,
} from './incidentesService';
import type { IncidenteCreate, IncidenteRead, IncidenteListItem } from '../types/incidente';
import type { EstadoRead, SectorRead, CanalOrigenRead } from '../types/catalog';

// Mockear el módulo completo de api para controlar apiClient
vi.mock('./api', async (importOriginal) => {
  const original = await importOriginal<typeof import('./api')>();
  return {
    ...original,
    apiClient: {
      post: vi.fn(),
      get: vi.fn(),
      patch: vi.fn(),
    },
  };
});

const mockedApiClient = vi.mocked(apiClient);

// ---- Fixtures ----

const mockSector: SectorRead = { id: 1, nombre: 'Sistemas', descripcion: null };
const mockEstado: EstadoRead = {
  id: 1,
  nombre: 'nuevo',
  descripcion: null,
  es_terminal: false,
};
const mockCanal: CanalOrigenRead = {
  id: 2,
  nombre: 'formulario web',
  descripcion: null,
};

const mockIncidenteRead: IncidenteRead = {
  id: 42,
  descripcion_pseudonimizada: 'El servidor de base de datos no responde desde esta mañana',
  prioridad: 'alta',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  updated_at: '2026-06-11T10:00:00Z',
  sector: mockSector,
  estado: mockEstado,
  canal_origen: mockCanal,
};

const mockListItem: IncidenteListItem = {
  id: 42,
  prioridad: 'alta',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  sector: mockSector,
  estado: mockEstado,
};

// ---- Tests ----

describe('incidentesService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---------- crearIncidente ----------

  describe('crearIncidente', () => {
    it('hace POST a /incidentes con el payload recibido y devuelve el body', async () => {
      const payload: IncidenteCreate = {
        descripcion: 'El servidor no responde desde las 8 am de este lunes',
        prioridad: 'alta',
        canal_origen_id: 2,
      };
      vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: mockIncidenteRead });

      const result = await crearIncidente(payload);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/incidentes/', payload);
      expect(result).toEqual(mockIncidenteRead);
    });

    it('propaga los errores de red tal cual', async () => {
      const networkError = new Error('Network Error');
      vi.mocked(mockedApiClient.post).mockRejectedValueOnce(networkError);

      await expect(crearIncidente({ descripcion: 'test' })).rejects.toThrow('Network Error');
    });
  });

  // ---------- listarIncidentes ----------

  describe('listarIncidentes', () => {
    it('hace GET a /incidentes con los params recibidos y devuelve la lista', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockListItem] });

      const result = await listarIncidentes({ prioridad: 'alta', limit: 10 });

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/', {
        params: { prioridad: 'alta', limit: 10 },
      });
      expect(result).toEqual([mockListItem]);
    });

    it('llama GET /incidentes sin params cuando no se pasan argumentos', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

      await listarIncidentes();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/', { params: {} });
    });
  });

  // ---------- obtenerIncidente ----------

  describe('obtenerIncidente', () => {
    it('hace GET a /incidentes/{id} con el id correcto y devuelve el incidente', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockIncidenteRead });

      const result = await obtenerIncidente(42);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/42');
      expect(result).toEqual(mockIncidenteRead);
    });

    it('construye la ruta con el id como número para distintos valores', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: { ...mockIncidenteRead, id: 99 } });

      await obtenerIncidente(99);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/99');
    });
  });

  // ---------- listarHistorialCerrados (c-86, FIH-001) ----------

  describe('listarHistorialCerrados', () => {
    it('hace GET a /incidentes/historial-cerrados con la paginacion recibida', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockListItem] });

      const result = await listarHistorialCerrados({ limit: 20, offset: 40 });

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/historial-cerrados', {
        params: { limit: 20, offset: 40 },
      });
      expect(result).toEqual([mockListItem]);
    });

    it('usa params vacios cuando no se pasa paginacion', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

      await listarHistorialCerrados();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/historial-cerrados', {
        params: {},
      });
    });
  });

  // ---------- verificarSaludApi ----------

  describe('verificarSaludApi', () => {
    it('hace GET a /health y devuelve el estado de salud', async () => {
      const mockHealth = { status: 'ok', version: '1.0.0' };
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await verificarSaludApi();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockHealth);
    });
  });

  // ---------- ciclo de cierre (c-86) ----------

  describe('ciclo de cierre', () => {
    it('cerrarPorSector hace POST a /incidentes/{id}/cierre-sector', async () => {
      vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: mockIncidenteRead });

      const result = await cerrarPorSector(42);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/incidentes/42/cierre-sector');
      expect(result).toEqual(mockIncidenteRead);
    });

    it('cerrarGlobal hace POST a /incidentes/{id}/cierre-global', async () => {
      vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: mockIncidenteRead });

      await cerrarGlobal(42);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/incidentes/42/cierre-global');
    });

    it('rehabilitarIncidente hace POST a /incidentes/{id}/rehabilitar', async () => {
      vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: mockIncidenteRead });

      await rehabilitarIncidente(42);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/incidentes/42/rehabilitar');
    });

    it('editarEstadoIncidente hace PATCH a /incidentes/{id}/estado con el estado', async () => {
      vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockIncidenteRead });

      await editarEstadoIncidente(42, 'resuelto');

      expect(mockedApiClient.patch).toHaveBeenCalledWith('/incidentes/42/estado', {
        estado: 'resuelto',
      });
    });
  });

  // ---------- comentarios (c-86) ----------

  describe('comentarios', () => {
    it('listarComentarios hace GET a /incidentes/{id}/comentarios', async () => {
      const comentario = {
        id: 1,
        incidente_id: 42,
        autor_empleado_id: 3,
        texto: 'En revision',
        created_at: '2026-06-11T10:00:00Z',
      };
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [comentario] });

      const result = await listarComentarios(42);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/incidentes/42/comentarios');
      expect(result).toEqual([comentario]);
    });

    it('agregarComentario hace POST a /incidentes/{id}/comentarios con el texto', async () => {
      const comentario = {
        id: 2,
        incidente_id: 42,
        autor_empleado_id: 3,
        texto: 'Nuevo',
        created_at: '2026-06-11T11:00:00Z',
      };
      vi.mocked(mockedApiClient.post).mockResolvedValueOnce({ data: comentario });

      const result = await agregarComentario(42, 'Nuevo');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/incidentes/42/comentarios', {
        texto: 'Nuevo',
      });
      expect(result).toEqual(comentario);
    });
  });
});
