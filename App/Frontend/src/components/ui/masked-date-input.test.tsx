/**
 * Tests del componente MaskedDateInput.
 *
 * Contrato: input de texto controlado que muestra y acepta fechas en
 * formato dd/mm/aaaa, sin depender del locale del navegador, y emite
 * ISO (YYYY-MM-DD) solo cuando la fecha es completa y valida.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import {
  MaskedDateInput,
  maskDigits,
  isoToMasked,
  parseMasked,
} from './masked-date-input';

/** Envoltorio controlado que refleja el patron de uso real del dashboard. */
function Controlled({
  initial = '',
  onChange,
}: {
  initial?: string;
  onChange?: (iso: string) => void;
}) {
  const [value, setValue] = useState(initial);
  return (
    <MaskedDateInput
      aria-label="fecha"
      value={value}
      onChange={(iso) => {
        onChange?.(iso);
        setValue(iso);
      }}
    />
  );
}

const getInput = () => screen.getByLabelText('fecha');

describe('MaskedDateInput', () => {
  it('renderiza un input de texto con los atributos del formato dd/mm/aaaa', () => {
    render(<Controlled />);
    const input = getInput();
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('placeholder', 'dd/mm/aaaa');
    expect(input).toHaveAttribute('inputmode', 'numeric');
    expect(input).toHaveAttribute('maxlength', '10');
    expect(input).toHaveAttribute('autocomplete', 'off');
  });

  it('formatea los digitos tipeados como dd/mm/aaaa insertando las barras', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Controlled />);
    await user.type(getInput(), '16092026');
    expect(getInput()).toHaveValue('16/09/2026');
  });

  it('emite el ISO solo cuando la fecha esta completa y es valida', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.type(getInput(), '16092026');
    expect(onChange).toHaveBeenCalledWith('2026-09-16');
  });

  it('no emite mientras la fecha esta incompleta', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.type(getInput(), '1609');
    expect(getInput()).toHaveValue('16/09');
    expect(onChange).not.toHaveBeenCalled();
  });

  it('marca 31/02 como invalida, muestra el error y no emite', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.type(getInput(), '31022026');
    expect(getInput()).toHaveValue('31/02/2026');
    expect(onChange).not.toHaveBeenCalled();
    expect(getInput()).toHaveAttribute('aria-invalid', 'true');
    expect(getInput()).toHaveClass('border-destructive');
    expect(screen.getByRole('alert')).toHaveTextContent('Fecha inválida');
  });

  it('marca 00/00/0000 como invalida', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.type(getInput(), '00000000');
    expect(onChange).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Fecha inválida');
  });

  it('acepta 29/02/2024 como fecha bisiesta valida', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.type(getInput(), '29022024');
    expect(onChange).toHaveBeenCalledWith('2024-02-29');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('sincroniza el texto cuando el prop value cambia externamente', () => {
    const { rerender } = render(
      <MaskedDateInput aria-label="fecha" value="" onChange={() => {}} />
    );
    expect(getInput()).toHaveValue('');

    rerender(
      <MaskedDateInput aria-label="fecha" value="2024-02-29" onChange={() => {}} />
    );
    expect(getInput()).toHaveValue('29/02/2024');

    rerender(<MaskedDateInput aria-label="fecha" value="" onChange={() => {}} />);
    expect(getInput()).toHaveValue('');
  });

  it('soporta pegar digitos sin separadores', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.click(getInput());
    await user.paste('16092026');
    expect(getInput()).toHaveValue('16/09/2026');
    expect(onChange).toHaveBeenCalledWith('2026-09-16');
  });

  it('soporta pegar una fecha ya formateada con barras', async () => {
    const user = userEvent.setup({ delay: null });
    const onChange = vi.fn();
    render(<Controlled onChange={onChange} />);
    await user.click(getInput());
    await user.paste('16/09/2026');
    expect(getInput()).toHaveValue('16/09/2026');
    expect(onChange).toHaveBeenCalledWith('2026-09-16');
  });

  it('ignora los caracteres que no son digitos', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Controlled />);
    await user.type(getInput(), 'ab16cd09ef2026');
    expect(getInput()).toHaveValue('16/09/2026');
  });

  it('borra naturalmente: al eliminar un digito antes de la barra tambien quita la barra', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Controlled />);
    await user.type(getInput(), '160');
    expect(getInput()).toHaveValue('16/0');
    await user.type(getInput(), '{Backspace}');
    expect(getInput()).toHaveValue('16');
  });

  it('no se traba al borrar desde una fecha completa', async () => {
    const user = userEvent.setup({ delay: null });
    render(<Controlled />);
    await user.type(getInput(), '16092026');
    expect(getInput()).toHaveValue('16/09/2026');
    await user.type(getInput(), '{Backspace}');
    expect(getInput()).toHaveValue('16/09/202');
    await user.type(getInput(), '{Backspace}');
    expect(getInput()).toHaveValue('16/09/20');
  });
});

describe('helpers puros de mascara y validacion', () => {
  it('maskDigits aplica la mascara e ignora no-digitos', () => {
    expect(maskDigits('16092026')).toBe('16/09/2026');
    expect(maskDigits('16/09/2026')).toBe('16/09/2026');
    expect(maskDigits('16')).toBe('16');
    expect(maskDigits('160')).toBe('16/0');
    expect(maskDigits('abc')).toBe('');
  });

  it('parseMasked devuelve ISO solo para fechas reales completas', () => {
    expect(parseMasked('29/02/2024')).toBe('2024-02-29');
    expect(parseMasked('31/02/2026')).toBeNull();
    expect(parseMasked('31/04/2026')).toBeNull();
    expect(parseMasked('00/00/0000')).toBeNull();
    expect(parseMasked('16/09')).toBeNull();
  });

  it('isoToMasked convierte ISO a dd/mm/aaaa y vacio ante entradas invalidas', () => {
    expect(isoToMasked('2026-09-16')).toBe('16/09/2026');
    expect(isoToMasked('')).toBe('');
    expect(isoToMasked('no-es-iso')).toBe('');
  });
});
