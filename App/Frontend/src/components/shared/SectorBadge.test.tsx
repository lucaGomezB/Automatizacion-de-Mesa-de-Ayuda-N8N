/**
 * Pruebas de SectorBadge.
 * Verifica que la insignia resuelve color/etiqueta por el nombre canónico del sector
 * (no por IDs numéricos), que cubre los cinco sectores y que tolera un nombre
 * desconocido sin romper el renderizado.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SectorBadge, getSectorVariant } from './SectorBadge';

const SECTORES_CANONICOS: Array<[string, string]> = [
  ['Seguridad Informatica', 'destructive'],
  ['Soporte Tecnico Hardware', 'warning'],
  ['Soporte Tecnico Software', 'info'],
  ['Bases de Datos', 'success'],
  ['Sistemas', 'secondary'],
];

describe('SectorBadge', () => {
  // ---------- Sectores canónicos ----------

  it.each(SECTORES_CANONICOS)('muestra el nombre canónico "%s"', (nombre) => {
    render(<SectorBadge nombre={nombre} />);
    expect(screen.getByText(nombre)).toBeInTheDocument();
    expect(screen.queryByText('Pendiente')).not.toBeInTheDocument();
  });

  it.each(SECTORES_CANONICOS)(
    'asigna la variante de color esperada a "%s"',
    (nombre, variante) => {
      expect(getSectorVariant(nombre)).toBe(variante);
    }
  );

  // ---------- Sector desconocido ----------

  it('usa la variante muted para un nombre de sector desconocido', () => {
    expect(getSectorVariant('Sector Inexistente')).toBe('muted');
  });

  it('renderiza un nombre desconocido sin romper y sin marcarlo como Pendiente', () => {
    render(<SectorBadge nombre="Sector Inexistente" />);
    expect(screen.getByText('Sector Inexistente')).toBeInTheDocument();
    expect(screen.queryByText('Pendiente')).not.toBeInTheDocument();
  });

  it('NO reconoce el sector eliminado "Operaciones" como canónico', () => {
    expect(getSectorVariant('Operaciones')).toBe('muted');
  });

  // ---------- Estado pendiente ----------

  it('muestra "Pendiente" cuando nombre es null', () => {
    render(<SectorBadge nombre={null} />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('muestra "Pendiente" cuando nombre es undefined', () => {
    render(<SectorBadge nombre={undefined} />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });
});
