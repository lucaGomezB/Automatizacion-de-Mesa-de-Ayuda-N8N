/**
 * Pruebas de la capa de servicios para clasificaciones.
 * apiClient mockeado — sin solicitudes HTTP reales.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import {
  listarRevisionPendiente,
  listarClasificacionesPorIncidente,
  validarClasificacion,
} from './clasificacionesService';
import type { ClasificacionLogRead, ClasificacionValidar } from '../types/clasificacion';
import type { SectorRead } from '../types/catalog';

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

const mockSector: SectorRead = { id: 2, nombre: 'Soporte Tecnico Hardware', descripcion: null };

const mockClasificacion: ClasificacionLogRead = {
  id: 10,
  incidente_id: 42,
  confianza: 0.55,
  etapa: 'gemini',
  requiere_revision_humana: true,
  respuesta_raw: '{"sector_predicho":"Soporte Tecnico Hardware","confianza":0.55}',
  created_at: '2026-06-11T10:00:00Z',
  sector_predicho: mockSector,
  sector_validado: null,
};

// ---- Tests ----

describe('clasificacionesService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---------- listarRevisionPendiente ----------

  describe('listarRevisionPendiente', () => {
    it('hace GET a /clasificaciones/revision-pendiente con los params y devuelve la lista', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockClasificacion] });

      const result = await listarRevisionPendiente({ limit: 20, offset: 0 });

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        '/clasificaciones/revision-pendiente',
        { params: { limit: 20, offset: 0 } }
      );
      expect(result).toEqual([mockClasificacion]);
    });

    it('llama sin params cuando no se pasan argumentos', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

      await listarRevisionPendiente();

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        '/clasificaciones/revision-pendiente',
        { params: {} }
      );
    });
  });

  // ---------- listarClasificacionesPorIncidente ----------

  describe('listarClasificacionesPorIncidente', () => {
    it('hace GET a /clasificaciones/incidente/{id} con el id correcto', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [mockClasificacion] });

      const result = await listarClasificacionesPorIncidente(42);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/clasificaciones/incidente/42');
      expect(result).toEqual([mockClasificacion]);
    });

    it('construye la ruta correctamente para distintos ids', async () => {
      vi.mocked(mockedApiClient.get).mockResolvedValueOnce({ data: [] });

      await listarClasificacionesPorIncidente(99);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/clasificaciones/incidente/99');
    });
  });

  // ---------- validarClasificacion ----------

  describe('validarClasificacion', () => {
    it('hace PATCH a /clasificaciones/{logId}/validar con el payload multi-etiqueta y devuelve el resultado', async () => {
      const validadoSector: SectorRead = { id: 1, nombre: 'Sistemas', descripcion: null };
      const mockValidado: ClasificacionLogRead = {
        ...mockClasificacion,
        sector_validado: validadoSector,
        requiere_revision_humana: false,
      };
      const payload: ClasificacionValidar = {
        sector_validado: 'Sistemas',
        sectores_adicionales: [],
      };
      vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockValidado });

      const result = await validarClasificacion(10, payload);

      expect(mockedApiClient.patch).toHaveBeenCalledWith(
        '/clasificaciones/10/validar',
        payload
      );
      expect(result).toEqual(mockValidado);
    });

    it('reenvia un unico sector adicional por nombre canonico', async () => {
      vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockClasificacion });

      const payload: ClasificacionValidar = {
        sector_validado: 'Sistemas',
        sectores_adicionales: ['Bases de Datos'],
      };
      await validarClasificacion(7, payload);

      expect(mockedApiClient.patch).toHaveBeenCalledWith('/clasificaciones/7/validar', payload);
    });

    it('reenvia varios sectores adicionales por nombre canonico', async () => {
      vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockClasificacion });

      const payload: ClasificacionValidar = {
        sector_validado: 'Soporte Tecnico Software',
        sectores_adicionales: ['Bases de Datos', 'Seguridad Informatica'],
      };
      await validarClasificacion(8, payload);

      expect(mockedApiClient.patch).toHaveBeenCalledWith('/clasificaciones/8/validar', payload);
    });

    it('construye la ruta correctamente para distintos logIds', async () => {
      vi.mocked(mockedApiClient.patch).mockResolvedValueOnce({ data: mockClasificacion });

      await validarClasificacion(99, {
        sector_validado: 'Bases de Datos',
        sectores_adicionales: [],
      });

      expect(mockedApiClient.patch).toHaveBeenCalledWith('/clasificaciones/99/validar', {
        sector_validado: 'Bases de Datos',
        sectores_adicionales: [],
      });
    });
  });
});
