/**
 * Pruebas de IncidenteForm.
 *
 * Task 5.1: valida que descripción < 15 palabras → error visible, mutación NO invocada.
 * Task 5.2: valida que envío válido produce payload con canal_origen_id=2
 *            y sin nombre_usuario / sector_usuario.
 *
 * Estrategia Radix UI: los campos prioridad/sector_usuario usan Radix Select,
 * que puede ser frágil en happy-dom. Para el test de payload se usa el valor
 * por defecto (prioridad: 'media') sin interactuar con el Select, conforme
 * al plan de mitigación del design.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { IncidenteForm } from './IncidenteForm';
import * as useReportarIncidenteHook from '@/hooks/useReportarIncidente';
import { createTestQueryClient } from '@/test/utils';
import type { IncidenteCreate, IncidenteRead } from '@/types/incidente';

// Mockear el hook completo para controlar la mutación
vi.mock('@/hooks/useReportarIncidente');

// Mock de IncidenteRead para simular respuesta exitosa
const mockIncidenteRead: IncidenteRead = {
  id: 1,
  descripcion_pseudonimizada: 'test',
  prioridad: 'media',
  requiere_revision_humana: false,
  created_at: '2026-06-11T10:00:00Z',
  updated_at: '2026-06-11T10:00:00Z',
  sector: { id: 1, nombre: 'Sistemas', descripcion: null },
  estado: { id: 1, nombre: 'nuevo', descripcion: null, es_terminal: false },
  canal_origen: { id: 2, nombre: 'formulario web', descripcion: null },
};

function renderForm(onSuccess = vi.fn()) {
  const client = createTestQueryClient();
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return render(<IncidenteForm onSuccess={onSuccess} />, { wrapper: Wrapper });
}

/** Construye un objeto mutate-like que React Query useMutation expone */
function makeMockMutation(overrides: Partial<ReturnType<typeof useReportarIncidenteHook.useReportarIncidente>> = {}) {
  const mutateMock = vi.fn();
  return {
    mutate: mutateMock,
    isPending: false,
    error: null,
    data: undefined,
    isSuccess: false,
    isError: false,
    isIdle: true,
    isPaused: false,
    reset: vi.fn(),
    mutateAsync: vi.fn(),
    context: undefined,
    variables: undefined,
    failureCount: 0,
    failureReason: null,
    status: 'idle' as const,
    submittedAt: 0,
    ...overrides,
  } as unknown as ReturnType<typeof useReportarIncidenteHook.useReportarIncidente>;
}

describe('IncidenteForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---- Task 5.1: Validación de mínimo de palabras ----

  it('muestra error de validación y NO invoca la mutación cuando la descripción tiene menos de 15 palabras', async () => {
    const mutateMock = vi.fn();
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation({ mutate: mutateMock })
    );

    const user = userEvent.setup();
    renderForm();

    // Completar nombre (campo requerido)
    await user.type(screen.getByLabelText(/nombre completo/i), 'María González');

    // Descripción con menos de 15 palabras (aquí son 5)
    await user.type(
      screen.getByLabelText(/descripción del incidente/i),
      'El servidor no funciona hoy.'
    );

    // Enviar el formulario
    await user.click(screen.getByRole('button', { name: /enviar incidente/i }));

    // Esperar que aparezca el mensaje de validación
    await waitFor(() => {
      expect(
        screen.getByText(/al menos 15 palabras/i)
      ).toBeInTheDocument();
    });

    // La mutación NO debe haberse invocado
    expect(mutateMock).not.toHaveBeenCalled();
  });

  it('muestra error de validación cuando el nombre está vacío', async () => {
    const mutateMock = vi.fn();
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation({ mutate: mutateMock })
    );

    const user = userEvent.setup();
    renderForm();

    // No completar nombre, completar descripción válida
    await user.type(
      screen.getByLabelText(/descripción del incidente/i),
      'El servidor de base de datos no responde desde las ocho de la mañana de hoy.'
    );

    await user.click(screen.getByRole('button', { name: /enviar incidente/i }));

    await waitFor(() => {
      expect(screen.getByText(/el nombre es obligatorio/i)).toBeInTheDocument();
    });

    expect(mutateMock).not.toHaveBeenCalled();
  });

  // ---- Task 5.2: Payload del contrato ----

  it('invoca la mutación con canal_origen_id=2 y sin nombre_usuario ni sector_usuario', async () => {
    const mutateMock = vi.fn();
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation({ mutate: mutateMock })
    );

    const user = userEvent.setup();
    renderForm();

    // Completar nombre
    await user.type(screen.getByLabelText(/nombre completo/i), 'Juan Pérez');

    // Descripción con 15+ palabras
    const descripcionValida =
      'El servidor de base de datos no responde desde las ocho de la mañana de este lunes veintidós de junio.';
    await user.type(screen.getByLabelText(/descripción del incidente/i), descripcionValida);

    // Enviar (la prioridad por defecto es 'media', no abrimos el Select de Radix)
    await user.click(screen.getByRole('button', { name: /enviar incidente/i }));

    await waitFor(() => {
      expect(mutateMock).toHaveBeenCalled();
    });

    // Verificar el payload pasado a mutate (primer argumento)
    const payload = mutateMock.mock.calls[0][0] as IncidenteCreate;
    expect(payload.canal_origen_id).toBe(2);
    expect(payload).not.toHaveProperty('nombre_usuario');
    expect(payload).not.toHaveProperty('sector_usuario');
    expect(payload.descripcion).toBeDefined();
  });

  it('el payload incluye la descripción con trim aplicado', async () => {
    const mutateMock = vi.fn();
    vi.mocked(useReportarIncidenteHook.useReportarIncidente).mockReturnValue(
      makeMockMutation({ mutate: mutateMock })
    );

    const user = userEvent.setup();
    renderForm();

    await user.type(screen.getByLabelText(/nombre completo/i), 'Ana García');

    const descripcion =
      '  El servidor de base de datos no responde desde las ocho de la mañana del lunes.  ';
    await user.type(screen.getByLabelText(/descripción del incidente/i), descripcion);
    await user.click(screen.getByRole('button', { name: /enviar incidente/i }));

    await waitFor(() => expect(mutateMock).toHaveBeenCalled());

    const payload = mutateMock.mock.calls[0][0] as IncidenteCreate;
    // La descripción debe ir trimmed
    expect(payload.descripcion).toBe(descripcion.trim());
  });
});
