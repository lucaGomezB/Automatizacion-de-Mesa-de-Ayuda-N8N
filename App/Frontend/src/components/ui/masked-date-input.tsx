/**
 * MaskedDateInput — input de fecha con mascara dd/mm/aaaa.
 *
 * Responsabilidad:
 *   Mostrar y aceptar fechas siempre en formato dd/mm/aaaa, independiente
 *   del locale del navegador (a diferencia de `<input type="date">`).
 *   Emite ISO (YYYY-MM-DD) solo cuando la fecha es completa y valida;
 *   ante entrada incompleta o invalida no notifica al padre.
 *
 * Sin dependencias externas ni libreria de fechas: la mascara y la
 * validacion se resuelven con helpers puros y `Date` nativo.
 */
import * as React from 'react';
import { cn } from '@/lib/utils';

const NON_DIGIT = /\D/g;
const MASKED_RE = /^(\d{2})\/(\d{2})\/(\d{4})$/;
const ISO_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

/**
 * Aplica la mascara dd/mm/aaaa a una cadena, ignorando todo lo que no sea
 * digito y limitando a 8 digitos (dd mm aaaa).
 */
export function maskDigits(raw: string): string {
  const digits = raw.replace(NON_DIGIT, '').slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

/** Convierte un ISO "YYYY-MM-DD" al texto mostrado "dd/mm/aaaa" (o ""). */
export function isoToMasked(iso: string): string {
  const match = ISO_RE.exec(iso);
  if (!match) return '';
  return `${match[3]}/${match[2]}/${match[1]}`;
}

/**
 * Devuelve el ISO "YYYY-MM-DD" si el texto es una fecha completa y real
 * (rechaza 31/02, 31/04, 00/00/0000; acepta 29/02/2024). Devuelve null
 * cuando esta incompleta o es invalida.
 */
export function parseMasked(masked: string): string | null {
  const match = MASKED_RE.exec(masked);
  if (!match) return null;

  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  if (month < 1 || month > 12 || day < 1) return null;

  const date = new Date(year, month - 1, day);
  const isReal =
    date.getFullYear() === year &&
    date.getMonth() === month - 1 &&
    date.getDate() === day;
  if (!isReal) return null;

  return `${match[3]}-${match[2]}-${match[1]}`;
}

export interface MaskedDateInputProps {
  value: string;
  onChange: (iso: string) => void;
  id?: string;
  'aria-label'?: string;
  className?: string;
  disabled?: boolean;
}

export function MaskedDateInput({
  value,
  onChange,
  id,
  'aria-label': ariaLabel,
  className,
  disabled,
}: MaskedDateInputProps) {
  const [text, setText] = React.useState(() => isoToMasked(value));
  const errorId = React.useId();

  // Sincroniza el texto mostrado cuando el ISO del padre cambia desde afuera,
  // sin pisar lo que el usuario esta tipeando si el ISO no cambio.
  React.useEffect(() => {
    setText((prev) => {
      const prevIso = parseMasked(prev) ?? '';
      if (prevIso === value) return prev;
      return isoToMasked(value);
    });
  }, [value]);

  const isComplete = text.replace(NON_DIGIT, '').length === 8;
  const isValid = parseMasked(text) !== null;
  const isInvalid = isComplete && !isValid;

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const next = maskDigits(event.target.value);
    setText(next);
    const iso = parseMasked(next);
    if (iso !== null) onChange(iso);
  };

  return (
    <div className="relative">
      <input
        id={id}
        type="text"
        value={text}
        onChange={handleChange}
        placeholder="dd/mm/aaaa"
        inputMode="numeric"
        maxLength={10}
        autoComplete="off"
        disabled={disabled}
        aria-label={ariaLabel}
        aria-invalid={isInvalid || undefined}
        aria-describedby={isInvalid ? errorId : undefined}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
          'ring-offset-background placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          isInvalid && 'border-destructive focus-visible:ring-destructive',
          className
        )}
      />
      {isInvalid && (
        <p id={errorId} role="alert" className="mt-1 text-xs text-destructive">
          Fecha inválida
        </p>
      )}
    </div>
  );
}
