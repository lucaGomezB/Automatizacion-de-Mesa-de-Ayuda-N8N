/**
 * Pruebas del componente presentacional compartido `DetalleIncidente` (c-83).
 *
 * Cubre los escenarios FRH-001 a FRH-004 desde la vista de solo lectura:
 *   - descripcion pseudonimizada (nunca la original),
 *   - metadatos del incidente (estado, sector, adicionales, prioridad, canal, fechas),
 *   - resultado completo de la clasificacion (predicho, confianza, etapa, validado,
 *     adicionales predichos/validados y respuesta_raw),
 *   - estados borde: sin clasificacion, sin respuesta_raw, sin adicionales,
 *     revision humana requerida y estado terminal.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DetalleIncidente } from './DetalleIncidente';
import { formatearFecha } from '@/utils/formatters';
import type { IncidenteRead } from '@/types/incidente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

const mockIncidente: IncidenteRead = {
  id: 12,
  descripcion_pseudonimizada: 'No puedo acceder al sistema [NOMBRE] desde ayer por la manana.',
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
  respuesta_raw: '{"sector_predicho":"Soporte Tecnico Hardware","confianza":0.42}',
  created_at: '2026-06-11T09:00:00Z',
  sector_predicho: { id: 3, nombre: 'Soporte Tecnico Hardware', descripcion: null },
  sector_validado: { id: 4, nombre: 'Soporte Tecnico Software', descripcion: null },
  sectores_predichos: [{ id: 5, nombre: 'Seguridad Informatica', descripcion: null }],
  sectores_validados: [],
};

describe('DetalleIncidente', () => {
  it('muestra la descripcion pseudonimizada, los metadatos del incidente y la clasificacion completa', () => {
    render(<DetalleIncidente incidente={mockIncidente} clasificacion={mockClasificacion} />);

    // FRH-001 — descripcion pseudonimizada
    expect(
      screen.getByText(/no puedo acceder al sistema \[NOMBRE\]/i)
    ).toBeInTheDocument();

    // FRH-002 — metadatos del incidente
    expect(screen.getByText('En Proceso')).toBeInTheDocument();
    expect(screen.getByText('Sistemas')).toBeInTheDocument();
    expect(screen.getByText('Bases de Datos')).toBeInTheDocument();
    expect(screen.getByText('Alta')).toBeInTheDocument();
    expect(screen.getByText(/correo electrónico/i)).toBeInTheDocument();
    expect(screen.getByText(formatearFecha(mockIncidente.created_at))).toBeInTheDocument();
    expect(screen.getByText(formatearFecha(mockIncidente.updated_at))).toBeInTheDocument();

    // FRH-002 — senal de revision humana requerida
    expect(screen.getByText(/requiere revision humana/i)).toBeInTheDocument();

    // FRH-003 — clasificacion completa
    expect(screen.getByText('Soporte Tecnico Hardware')).toBeInTheDocument();
    expect(screen.getByText('42%')).toBeInTheDocument();
    expect(screen.getByText('Gemini 2.5 Flash')).toBeInTheDocument();
    expect(screen.getByText('Soporte Tecnico Software')).toBeInTheDocument();
    expect(screen.getByText('Seguridad Informatica')).toBeInTheDocument();
    expect(screen.getByText(/"sector_predicho"/)).toBeInTheDocument();
  });

  // ---- TRIANGULACION ----

  it('sin clasificacion muestra los metadatos del incidente y omite la seccion de clasificacion', () => {
    render(<DetalleIncidente incidente={mockIncidente} clasificacion={null} />);

    expect(screen.getByText(/no puedo acceder al sistema/i)).toBeInTheDocument();
    expect(screen.getByText('En Proceso')).toBeInTheDocument();
    expect(screen.queryByText(/clasificación automática/i)).not.toBeInTheDocument();
    expect(screen.queryByText('Confianza')).not.toBeInTheDocument();
  });

  it('omite la respuesta raw cuando la clasificacion no la aporta', () => {
    render(
      <DetalleIncidente
        incidente={mockIncidente}
        clasificacion={{ ...mockClasificacion, respuesta_raw: null }}
      />
    );

    expect(screen.queryByText(/respuesta raw de gemini/i)).not.toBeInTheDocument();
  });

  it('omite los bloques de sectores adicionales cuando no hay ninguno', () => {
    render(
      <DetalleIncidente
        incidente={{ ...mockIncidente, sectores_adicionales: [] }}
        clasificacion={{
          ...mockClasificacion,
          sectores_predichos: [],
          sectores_validados: [],
        }}
      />
    );

    expect(screen.queryByText('Sectores Adicionales')).not.toBeInTheDocument();
    expect(screen.queryByText('Sectores Adicionales Predichos')).not.toBeInTheDocument();
    expect(screen.queryByText('Sectores Adicionales Validados')).not.toBeInTheDocument();
  });

  it('lista los sectores adicionales validados cuando existen', () => {
    render(
      <DetalleIncidente
        incidente={{ ...mockIncidente, sectores_adicionales: [] }}
        clasificacion={{
          ...mockClasificacion,
          sectores_predichos: [],
          sectores_validados: [{ id: 9, nombre: 'Bases de Datos', descripcion: null }],
        }}
      />
    );

    expect(screen.getByText('Sectores Adicionales Validados')).toBeInTheDocument();
    expect(screen.getByText('Bases de Datos')).toBeInTheDocument();
  });

  it('no muestra la senal de revision humana cuando no es requerida', () => {
    render(
      <DetalleIncidente
        incidente={{ ...mockIncidente, requiere_revision_humana: false }}
        clasificacion={mockClasificacion}
      />
    );

    expect(screen.queryByText(/requiere revision humana/i)).not.toBeInTheDocument();
  });

  it('indica solo lectura cuando el incidente esta en un estado terminal', () => {
    render(
      <DetalleIncidente
        incidente={{
          ...mockIncidente,
          estado: { id: 5, nombre: 'Cerrado', descripcion: null, es_terminal: true },
        }}
        clasificacion={mockClasificacion}
      />
    );

    expect(screen.getByText(/solo lectura/i)).toBeInTheDocument();
    expect(screen.getByText('Cerrado')).toBeInTheDocument();
  });

  it('indica la ausencia de descripcion sin romper el flujo', () => {
    render(
      <DetalleIncidente
        incidente={{ ...mockIncidente, descripcion_pseudonimizada: '   ' }}
        clasificacion={null}
      />
    );

    expect(screen.getByText(/sin descripción disponible/i)).toBeInTheDocument();
  });
});
