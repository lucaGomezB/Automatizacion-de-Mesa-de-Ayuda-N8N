/**
 * Panel de Administración — ruta "/admin".
 *
 * Responsabilidad:
 *   Centraliza la gestión operativa del sistema: listado de tickets con filtros,
 *   paginación, y la cola de revisión humana para clasificaciones con confianza < 0.70.
 *
 * Estructura interna:
 *   - TabButton  : botón de pestaña con contador de pendientes.
 *   - Paginacion : control de páginas offset-based para ambas listas.
 *
 * Flujo de datos:
 *   useIncidentes         → GET /api/v1/incidentes (filtros + paginación)
 *   useRevisionPendiente  → GET /api/v1/clasificaciones/revision-pendiente
 *   TicketDetailDialog    → GET /api/v1/incidentes/{id}  (lazy, al abrir el diálogo)
 *   ValidarClasificacionDialog → PATCH /api/v1/clasificaciones/{id}/validar
 */
import type { ReactNode } from 'react';
import { useState, useCallback } from 'react';
import {
  LayoutList,
  ClipboardCheck,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  X,
} from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useIncidentes } from '@/hooks/useIncidentes';
import { useRevisionPendiente } from '@/hooks/useRevisionPendiente';
import { TicketsTable } from './TicketsTable';
import { RevisionHumanaTable } from './RevisionHumanaTable';
import { TicketDetailDialog } from './TicketDetailDialog';
import { ValidarClasificacionDialog } from './ValidarClasificacionDialog';
import { SECTORES_OPCIONES, ESTADOS_OPCIONES } from '@/types/catalog';
import type { IncidenteListParams } from '@/types/incidente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

// ── Tipos internos ───────────────────────────────────────────────────────────

/** Pestañas disponibles en el panel de administración. */
type TabActiva = 'tickets' | 'revision';

// ── Constantes ───────────────────────────────────────────────────────────────

/** Cantidad de registros por página en ambas tablas. */
const PAGE_SIZE = 20;

/**
 * Estado inicial de filtros: todos los campos indefinidos equivale a "sin filtro activo".
 * Se utiliza para resetear la barra de filtros sin perder la estructura del tipo.
 */
const FILTROS_VACIOS: IncidenteListParams = {
  sector_id: undefined,
  estado_id: undefined,
  prioridad: undefined,
  limit: PAGE_SIZE,
  offset: 0,
};

// ── Componente principal ─────────────────────────────────────────────────────

export default function AdministracionPage() {
  // ── Estado de navegación ────────────────────────────────────────────────────
  const [tabActiva, setTabActiva] = useState<TabActiva>('tickets');

  // ── Estado de filtros y paginación ─────────────────────────────────────────
  const [filtros, setFiltros] = useState<IncidenteListParams>(FILTROS_VACIOS);
  const [paginaTickets, setPaginaTickets] = useState(0);
  const [paginaRevision, setPaginaRevision] = useState(0);

  // ── Estado de diálogos ──────────────────────────────────────────────────────
  const [incidenteIdSeleccionado, setIncidenteIdSeleccionado] = useState<number | null>(null);
  const [clasificacionSeleccionada, setClasificacionSeleccionada] =
    useState<ClasificacionLogRead | null>(null);

  // ── Consultas de datos ──────────────────────────────────────────────────────

  /**
   * Lista de incidentes con filtros combinables.
   * El offset se calcula en función de la página actual y el tamaño de página.
   */
  const {
    data: incidentes,
    isLoading: cargandoTickets,
    isError: errorTickets,
    error: errorTicketsObj,
    refetch: refetchTickets,
  } = useIncidentes({
    ...filtros,
    limit: PAGE_SIZE,
    offset: paginaTickets * PAGE_SIZE,
  });

  /**
   * Cola de clasificaciones pendientes de revisión humana.
   * Se refresca automáticamente cada 60 s (configurado en el hook).
   */
  const {
    data: clasificacionesPendientes,
    isLoading: cargandoRevision,
    isError: errorRevision,
    error: errorRevisionObj,
    refetch: refetchRevision,
  } = useRevisionPendiente({
    limit: PAGE_SIZE,
    offset: paginaRevision * PAGE_SIZE,
  });

  // ── Handlers ────────────────────────────────────────────────────────────────

  /**
   * Actualiza un campo de filtro y reinicia la paginación a la primera página.
   * La aserción `as IncidenteListParams` es necesaria porque TypeScript no puede
   * verificar estáticamente que el valor dinámico `[campo]` sea compatible con
   * el tipo exacto del campo correspondiente en la interfaz.
   */
  const handleFiltroChange = useCallback(
    (campo: keyof IncidenteListParams, valor: string | undefined) => {
      setPaginaTickets(0);
      setFiltros(
        (prev) =>
          ({
            ...prev,
            [campo]:
              valor
                ? campo === 'sector_id' || campo === 'estado_id'
                  ? Number(valor)
                  : valor
                : undefined,
          }) as IncidenteListParams
      );
    },
    []
  );

  /** Resetea todos los filtros y vuelve a la primera página. */
  const handleLimpiarFiltros = useCallback(() => {
    setPaginaTickets(0);
    setFiltros(FILTROS_VACIOS);
  }, []);

  /** Indica si hay al menos un filtro activo (para mostrar el botón "Limpiar"). */
  const hayFiltrosActivos =
    filtros.sector_id !== undefined ||
    filtros.estado_id !== undefined ||
    filtros.prioridad !== undefined;

  /** Abre el diálogo de detalle para el incidente seleccionado. */
  const handleSelectIncidente = useCallback((id: number) => {
    setIncidenteIdSeleccionado(id);
  }, []);

  /** Abre el diálogo de validación para la clasificación pendiente seleccionada. */
  const handleValidar = useCallback((clasificacion: ClasificacionLogRead) => {
    setClasificacionSeleccionada(clasificacion);
  }, []);

  /**
   * Total de clasificaciones pendientes: se muestra como badge en la pestaña
   * "Revisión Humana" para alertar al operador sin que necesite cambiar de pestaña.
   */
  const totalPendientes = clasificacionesPendientes?.length ?? 0;

  // ── Renderizado ─────────────────────────────────────────────────────────────

  return (
    <PageWrapper>
      <div className="space-y-6">

        {/* Encabezado de sección */}
        <div>
          <h1 className="text-2xl font-semibold text-primary">Panel de Administración</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Gestión de tickets, revisión de clasificaciones y auditoría del pipeline de IA.
          </p>
        </div>

        {/* Barra de pestañas */}
        <div className="flex items-center gap-1 border-b pb-0">
          <TabButton
            activa={tabActiva === 'tickets'}
            icono={<LayoutList className="h-4 w-4" />}
            etiqueta="Lista de Tickets"
            onClick={() => setTabActiva('tickets')}
          />
          <TabButton
            activa={tabActiva === 'revision'}
            icono={<ClipboardCheck className="h-4 w-4" />}
            etiqueta="Revisión Humana"
            badge={totalPendientes > 0 ? totalPendientes : undefined}
            onClick={() => setTabActiva('revision')}
          />
        </div>

        {/* ── Pestaña: Lista de Tickets ──────────────────────────────────── */}
        {tabActiva === 'tickets' && (
          <section className="space-y-4 animate-fade-in">

            {/* Barra de filtros combinables */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <SlidersHorizontal className="h-4 w-4" />
                Filtros:
              </div>

              {/* Filtro por Estado del ciclo de vida */}
              <Select
                value={filtros.estado_id?.toString() ?? ''}
                onValueChange={(v) => handleFiltroChange('estado_id', v || undefined)}
              >
                <SelectTrigger className="h-9 w-44 text-sm">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  {ESTADOS_OPCIONES.map((e) => (
                    <SelectItem key={e.id} value={e.id.toString()}>
                      {e.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Filtro por Sector responsable */}
              <Select
                value={filtros.sector_id?.toString() ?? ''}
                onValueChange={(v) => handleFiltroChange('sector_id', v || undefined)}
              >
                <SelectTrigger className="h-9 w-48 text-sm">
                  <SelectValue placeholder="Sector" />
                </SelectTrigger>
                <SelectContent>
                  {SECTORES_OPCIONES.map((s) => (
                    <SelectItem key={s.id} value={s.id.toString()}>
                      {s.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Filtro por Prioridad */}
              <Select
                value={filtros.prioridad ?? ''}
                onValueChange={(v) => handleFiltroChange('prioridad', v || undefined)}
              >
                <SelectTrigger className="h-9 w-40 text-sm">
                  <SelectValue placeholder="Prioridad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="baja">Baja</SelectItem>
                  <SelectItem value="media">Media</SelectItem>
                  <SelectItem value="alta">Alta</SelectItem>
                </SelectContent>
              </Select>

              {/* Botón de limpieza de filtros (visible solo si hay filtros activos) */}
              {hayFiltrosActivos && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLimpiarFiltros}
                  className="h-9 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3.5 w-3.5 mr-1" />
                  Limpiar filtros
                </Button>
              )}
            </div>

            {/* Tabla principal de tickets */}
            <TicketsTable
              incidentes={incidentes}
              isLoading={cargandoTickets}
              isError={errorTickets}
              error={errorTicketsObj}
              onSelectIncidente={handleSelectIncidente}
              onRefetch={() => void refetchTickets()}
            />

            {/* Control de paginación */}
            <Paginacion
              pagina={paginaTickets}
              totalEnPagina={incidentes?.length ?? 0}
              pageSize={PAGE_SIZE}
              onChange={setPaginaTickets}
            />
          </section>
        )}

        {/* ── Pestaña: Revisión Humana ───────────────────────────────────── */}
        {tabActiva === 'revision' && (
          <section className="space-y-4 animate-fade-in">

            {/* Aviso explicativo del criterio de revisión */}
            <div className="flex items-start gap-2 p-4 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
              <ClipboardCheck className="h-4 w-4 flex-shrink-0 mt-0.5 text-amber-600" />
              <p>
                Estos incidentes fueron clasificados con una confianza inferior al{' '}
                <strong>70%</strong> (umbral definido en la especificación Gemini 2.5 Flash).
                Revisá y confirmá el sector correcto para cada uno.
              </p>
            </div>

            {/* Cola de revisión humana */}
            <RevisionHumanaTable
              clasificaciones={clasificacionesPendientes}
              isLoading={cargandoRevision}
              isError={errorRevision}
              error={errorRevisionObj}
              onValidar={handleValidar}
              onRefetch={() => void refetchRevision()}
            />

            {/* Control de paginación */}
            <Paginacion
              pagina={paginaRevision}
              totalEnPagina={clasificacionesPendientes?.length ?? 0}
              pageSize={PAGE_SIZE}
              onChange={setPaginaRevision}
            />
          </section>
        )}
      </div>

      {/* Diálogo de detalle — se monta siempre pero permanece cerrado hasta que se selecciona un ID */}
      <TicketDetailDialog
        open={incidenteIdSeleccionado !== null}
        incidenteId={incidenteIdSeleccionado}
        onClose={() => setIncidenteIdSeleccionado(null)}
      />

      {/* Diálogo de validación humana — idem, controlado por clasificacionSeleccionada */}
      <ValidarClasificacionDialog
        open={clasificacionSeleccionada !== null}
        clasificacion={clasificacionSeleccionada}
        onClose={() => setClasificacionSeleccionada(null)}
      />
    </PageWrapper>
  );
}

// ── Componentes auxiliares internos ─────────────────────────────────────────

interface TabButtonProps {
  /** Indica si esta pestaña es la activa actualmente. */
  activa: boolean;
  /** Ícono descriptivo de la pestaña. */
  icono: ReactNode;
  /** Texto de la etiqueta de la pestaña. */
  etiqueta: string;
  /** Contador opcional mostrado como badge (ej.: pendientes de revisión). */
  badge?: number;
  /** Callback invocado al hacer clic sobre la pestaña. */
  onClick: () => void;
}

/**
 * Botón de pestaña estilizado con indicador de estado activo y contador opcional.
 * El contador se usa para alertar al operador sobre la cantidad de revisiones pendientes.
 */
function TabButton({ activa, icono, etiqueta, badge, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={[
        'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors',
        activa
          ? 'border-primary text-primary'
          : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border',
      ].join(' ')}
    >
      {icono}
      {etiqueta}
      {badge !== undefined && (
        <Badge variant="destructive" className="h-5 min-w-5 px-1.5 text-[11px]">
          {badge}
        </Badge>
      )}
    </button>
  );
}

interface PaginacionProps {
  /** Índice de la página actual (base 0). */
  pagina: number;
  /** Cantidad de elementos en la página actual. */
  totalEnPagina: number;
  /** Tamaño configurado de página (para detectar si puede haber una página siguiente). */
  pageSize: number;
  /** Callback que recibe el nuevo índice de página al navegar. */
  onChange: (pagina: number) => void;
}

/**
 * Control de paginación offset-based.
 * La existencia de una página siguiente se infiere por comparación:
 * si la página actual tiene exactamente `pageSize` elementos, probablemente haya más.
 * Este enfoque evita una consulta extra de conteo al backend.
 */
function Paginacion({ pagina, totalEnPagina, pageSize, onChange }: PaginacionProps) {
  const hayAnterior = pagina > 0;
  const haySiguiente = totalEnPagina === pageSize;

  if (!hayAnterior && !haySiguiente) return null;

  return (
    <div className="flex items-center justify-between text-sm text-muted-foreground pt-2">
      <span>
        Página {pagina + 1} · {totalEnPagina} resultado{totalEnPagina !== 1 ? 's' : ''}
      </span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!hayAnterior}
          onClick={() => onChange(pagina - 1)}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!haySiguiente}
          onClick={() => onChange(pagina + 1)}
        >
          Siguiente
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}
