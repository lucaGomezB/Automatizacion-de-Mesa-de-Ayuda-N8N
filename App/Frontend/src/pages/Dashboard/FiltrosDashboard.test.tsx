/**
 * Tests de integracion de FiltrosDashboard.
 *
 * Verifica que los filtros Desde/Hasta usen el input enmascarado
 * dd/mm/aaaa y que notifiquen al padre con el ISO correcto.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { FiltrosDashboard } from './FiltrosDashboard';
import type { AgruparPor } from '@/types/estadisticas';

function Harness({
  onDesde,
  onHasta,
}: {
  onDesde: (iso: string) => void;
  onHasta: (iso: string) => void;
}) {
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const [agruparPor, setAgruparPor] = useState<AgruparPor>('dia');
  return (
    <FiltrosDashboard
      desde={desde}
      hasta={hasta}
      agruparPor={agruparPor}
      onDesdeChange={(iso) => {
        onDesde(iso);
        setDesde(iso);
      }}
      onHastaChange={(iso) => {
        onHasta(iso);
        setHasta(iso);
      }}
      onAgruparPorChange={setAgruparPor}
    />
  );
}

const getDateInputs = () => screen.getAllByPlaceholderText('dd/mm/aaaa');

describe('FiltrosDashboard', () => {
  it('renderiza dos inputs de fecha enmascarados', () => {
    render(<Harness onDesde={vi.fn()} onHasta={vi.fn()} />);
    expect(getDateInputs()).toHaveLength(2);
    expect(screen.getByText('Desde:')).toBeInTheDocument();
    expect(screen.getByText('Hasta:')).toBeInTheDocument();
  });

  it('formatea el filtro Desde y notifica al padre con el ISO', async () => {
    const user = userEvent.setup({ delay: null });
    const onDesde = vi.fn();
    render(<Harness onDesde={onDesde} onHasta={vi.fn()} />);

    const [desde] = getDateInputs();
    await user.type(desde, '16092026');

    expect(desde).toHaveValue('16/09/2026');
    expect(onDesde).toHaveBeenCalledWith('2026-09-16');
  });

  it('formatea el filtro Hasta y notifica al padre con el ISO', async () => {
    const user = userEvent.setup({ delay: null });
    const onHasta = vi.fn();
    render(<Harness onDesde={vi.fn()} onHasta={onHasta} />);

    const [, hasta] = getDateInputs();
    await user.type(hasta, '01012025');

    expect(hasta).toHaveValue('01/01/2025');
    expect(onHasta).toHaveBeenCalledWith('2025-01-01');
  });
});
