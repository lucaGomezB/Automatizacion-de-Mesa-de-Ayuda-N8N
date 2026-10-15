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
 *   useIncidentes             → GET /api/v1/incidentes (filtros + paginación)
 *   useRevisionPendiente      → GET /api/v1/clasificaciones/revision-pendiente (paginado)
 *   useRevisionPendienteCount → GET /api/v1/clasificaciones/revision-pendiente/count (badge)
 *   TicketDetailDialog    → GET /api/v1/incidentes/{id}  (lazy, al abrir el diálogo)
 *   ValidarClasificacionDialog → PATCH /api/v1/clasificaciones/{id}/validar
 *
 * El badge de la pestaña usa el TOTAL del recurso de conteo (FRH-008), de modo
 * que no quede acotado al tamaño de una página. La cola se pagina con
 * limit/offset y el total del conteo determina si hay página siguiente (FRH-009).
 *
 * Frontera de seguridad (c-81, FR-RBAC-004/005):
 *   El filtro de sector de esta pantalla es una CONVENIENCIA de la interfaz, NO
 *   un control de acceso. El sector dejo de ser limite de alcance en el modelo
 *   c-82. La visibilidad de los incidentes la determina EXCLUSIVAMENTE el
 *   backend; el cliente nunca acota datos por su cuenta. Ante una denegacion del
 *   backend (403/404), la UI muestra un estado de error sin exponer el recurso.
 */
import type { ReactNode } from 'react';
import { useState, useCallback, useEffect } from 'react';
import {
  LayoutList,
  ClipboardCheck,
  History,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  Search,
  X,
} from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { useIncidentes } from '@/hooks/useIncidentes';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import {
  useRevisionPendiente,
  useRevisionPendienteCount,
} from '@/hooks/useRevisionPendiente';
import { useHistorialCerrados } from '@/hooks/useHistorialCerrados';
import { useSectores } from '@/hooks/useSectores';
import { TicketsTable } from './TicketsTable';
import { RevisionHumanaTable } from './RevisionHumanaTable';
import { HistorialTable } from './HistorialTable';
import { TicketDetailDialog } from './TicketDetailDialog';
import { ValidarClasificacionDialog } from './ValidarClasificacionDialog';
import { ESTADOS_OPCIONES } from '@/types/catalog';
import type { IncidenteListParams } from '@/types/incidente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

// ── Tipos internos ───────────────────────────────────────────────────────────

/**
 * Pestañas disponibles en el panel de administración (c-86, D11).
 * "Revisión Humana" queda GLOBAL-only; "Historial de Incidentes Cerrados" está
 * disponible para GLOBAL y SECTOR.
 */
type TabActiva = 'tickets' | 'revision' | 'historial';

// ── Constantes ───────────────────────────────────────────────────────────────

/** Cantidad de registros por página en ambas tablas. */
const PAGE_SIZE = 20;

/** Retraso del debounce de la barra de búsqueda (c-88, D3). */
const BUSQUEDA_DEBOUNCE_MS = 300;

/** Longitud mínima del término de búsqueda tras recortar (c-88, D2). */
const BUSQUEDA_MIN_CARACTERES = 2;

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
  // ── Alcance (c-86, FR-RBAC-002): la cola de revisión es GLOBAL-only ─────────
  const { alcance } = useAuth();
  const esGlobal = alcance.modo === 'GLOBAL';

  // ── Estado de navegación ────────────────────────────────────────────────────
  const [tabActiva, setTabActiva] = useState<TabActiva>('tickets');

  // ── Estado de filtros y paginación ─────────────────────────────────────────
  const [filtros, setFiltros] = useState<IncidenteListParams>(FILTROS_VACIOS);
  const [paginaTickets, setPaginaTickets] = useState(0);
  const [paginaRevision, setPaginaRevision] = useState(0);
  const [paginaHistorial, setPaginaHistorial] = useState(0);

  // ── Estado de búsqueda por texto libre (c-88, FIS-001) ─────────────────────
  // El texto crudo del input se debounce 300 ms; el valor efectivo se refleja en
  // `filtros.q` (mínimo 2 caracteres tras recortar) y viaja por la cadena
  // IncidenteListParams -> useIncidentes -> listarIncidentes.
  const [terminoBusqueda, setTerminoBusqueda] = useState('');
  const terminoDebounced = useDebouncedValue(terminoBusqueda, BUSQUEDA_DEBOUNCE_MS);

  // ── Estado de diálogos ──────────────────────────────────────────────────────
  const [incidenteIdSeleccionado, setIncidenteIdSeleccionado] = useState<number | null>(null);
  const [clasificacionSeleccionada, setClasificacionSeleccionada] =
    useState<ClasificacionLogRead | null>(null);

  // ── Catálogo de sectores (opciones en runtime, sin IDs numéricos fijos) ─────
  const { data: sectores } = useSectores();

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
   * Cola de clasificaciones pendientes de revisión humana, PAGINADA (FRH-009).
   * El badge de la pestaña NO se deriva de esta página: usa el total del recurso
   * de conteo (ver `useRevisionPendienteCount`). Se refresca cada 60 s (hook).
   */
  const {
    data: clasificacionesPendientes,
    isLoading: cargandoRevision,
    isError: errorRevision,
    error: errorRevisionObj,
    refetch: refetchRevision,
  } = useRevisionPendiente(
    {
      limit: PAGE_SIZE,
      offset: paginaRevision * PAGE_SIZE,
    },
    // La cola de revisión es GLOBAL-only (c-86, FR-RBAC-002): no se consulta
    // fuera de ese alcance. Para GLOBAL conserva el comportamiento previo
    // (consulta al montar; el badge usa el conteo aunque no esté la pestaña activa).
    esGlobal
  );

  /**
   * Total real de pendientes del alcance (FRH-008). Alimenta el badge de la
   * pestaña y la detección de páginas adicionales de la tabla de revisión.
   */
  const { data: totalRevision = 0 } = useRevisionPendienteCount(esGlobal);

  /**
   * Historial de incidentes cerrados (c-86, FIH-001). El backend acota el
   * conjunto por alcance (GLOBAL, SECTOR o PROPIO) y excluye los eliminados; la
   * UI solo presenta lo devuelto. Se consulta únicamente con la pestaña activa.
   */
  const {
    data: historialCerrados,
    isLoading: cargandoHistorial,
    isError: errorHistorial,
    error: errorHistorialObj,
    refetch: refetchHistorial,
  } = useHistorialCerrados(
    {
      limit: PAGE_SIZE,
      offset: paginaHistorial * PAGE_SIZE,
    },
    tabActiva === 'historial'
  );

  /**
   * Mantiene coherente la paginación tras un refetch (FRH-009, D7): si la página
   * actual queda fuera de rango (p. ej. al validar la última fila), retrocede a la
   * última página con resultados; si la cola quedó vacía, vuelve a la primera.
   */
  useEffect(() => {
    if (totalRevision <= 0) {
      if (paginaRevision !== 0) setPaginaRevision(0);
      return;
    }
    const ultimaPagina = Math.ceil(totalRevision / PAGE_SIZE) - 1;
    if (paginaRevision > ultimaPagina) setPaginaRevision(ultimaPagina);
  }, [totalRevision, paginaRevision]);

  // ── Handlers ────────────────────────────────────────────────────────────────

  /**
   * Refleja el término de búsqueda (ya debounced) en `filtros.q` y reinicia la
   * paginación a la primera página (FIS-001). Un término de menos de 2
   * caracteres tras recortar se trata como búsqueda vacía (sin `q`). Si el valor
   * efectivo no cambia, el updater devuelve el mismo objeto para evitar un
   * refetch espurio.
   */
  useEffect(() => {
    const normalizado = terminoDebounced.trim();
    const q =
      normalizado.length >= BUSQUEDA_MIN_CARACTERES ? normalizado : undefined;
    setFiltros((prev) => (prev.q === q ? prev : { ...prev, q }));
    setPaginaTickets(0);
  }, [terminoDebounced]);

  /**
   * Actualiza un campo de filtro y reinicia la paginación a la primera página.
   * La aserción `as IncidenteListParams` es necesaria porque TypeScript no puede
   * verificar estáticamente que el valor dinámico `[campo]` sea compatible con
   * el tipo exacto del campo correspondiente en la interfaz.
   *
   * NOTA (FR-RBAC-004): el filtro de sector es solo conveniencia de UX. Se
   * delega al backend (params de la consulta); el cliente NO acota el conjunto
   * autorizado por su cuenta.
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

  /** Resetea todos los filtros y el término de búsqueda, y vuelve a la primera página. */
  const handleLimpiarFiltros = useCallback(() => {
    setPaginaTickets(0);
    setFiltros(FILTROS_VACIOS);
    setTerminoBusqueda('');
  }, []);

  /** Indica si hay al menos un filtro o término de búsqueda activo (para el botón "Limpiar"). */
  const hayFiltrosActivos =
    filtros.sector_id !== undefined ||
    filtros.estado_id !== undefined ||
    filtros.prioridad !== undefined ||
    filtros.q !== undefined;

  /** Abre el diálogo de detalle para el incidente seleccionado. */
  const handleSelectIncidente = useCallback((id: number) => {
    setIncidenteIdSeleccionado(id);
  }, []);

  /** Abre el diálogo de validación para la clasificación pendiente seleccionada. */
  const handleValidar = useCallback((clasificacion: ClasificacionLogRead) => {
    setClasificacionSeleccionada(clasificacion);
  }, []);

  /**
   * Total de clasificaciones pendientes del alcance (FRH-008): se muestra como
   * badge en la pestaña "Revisión Humana". Proviene del recurso de conteo, por
   * lo que NO queda acotado al tamaño de una página de la cola.
   */
  const totalPendientes = totalRevision;

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
          {/* La cola de revisión queda fuera del alcance SECTOR (FR-RBAC-002). */}
          {esGlobal && (
            <TabButton
              activa={tabActiva === 'revision'}
              icono={<ClipboardCheck className="h-4 w-4" />}
              etiqueta="Revisión Humana"
              badge={totalPendientes > 0 ? totalPendientes : undefined}
              onClick={() => setTabActiva('revision')}
            />
          )}
          <TabButton
            activa={tabActiva === 'historial'}
            icono={<History className="h-4 w-4" />}
            etiqueta="Historial de Incidentes Cerrados"
            onClick={() => setTabActiva('historial')}
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

              {/* Barra de búsqueda por texto libre (c-88, FIS-001) */}
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  aria-label="Buscar incidentes"
                  placeholder="Buscar por descripción o número…"
                  value={terminoBusqueda}
                  onChange={(e) => setTerminoBusqueda(e.target.value)}
                  className="h-9 w-64 pl-8 text-sm"
                />
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
                  {sectores?.map((s) => (
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

            {/* Aviso explicativo del criterio de revisión (agnóstico al modelo, FRH-010) */}
            <div className="flex items-start gap-2 p-4 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
              <ClipboardCheck className="h-4 w-4 flex-shrink-0 mt-0.5 text-amber-600" />
              <p>
                Estos incidentes fueron clasificados con una confianza inferior al 70%, umbral de
                revisión humana del clasificador. Revisá y confirmá el sector correcto para cada uno.
              </p>
            </div>

            {/* Cola de revisión humana (paginada) */}
            <RevisionHumanaTable
              clasificaciones={clasificacionesPendientes}
              isLoading={cargandoRevision}
              isError={errorRevision}
              error={errorRevisionObj}
              onValidar={handleValidar}
              onRefetch={() => void refetchRevision()}
            />

            {/* Control de paginación de la cola, con el total exacto del conteo */}
            <Paginacion
              pagina={paginaRevision}
              totalEnPagina={clasificacionesPendientes?.length ?? 0}
              pageSize={PAGE_SIZE}
              total={totalRevision}
              onChange={setPaginaRevision}
            />
          </section>
        )}

        {/* ── Pestaña: Historial de Incidentes Cerrados (c-86, FIH-001) ──── */}
        {tabActiva === 'historial' && (
          <section className="space-y-4 animate-fade-in">
            {/* Tabla del historial; el alcance y la exclusión de eliminados los
                determina el backend (la UI no acota ni amplía el conjunto). */}
            <HistorialTable
              incidentes={historialCerrados}
              isLoading={cargandoHistorial}
              isError={errorHistorial}
              error={errorHistorialObj}
              onRefetch={() => void refetchHistorial()}
            />

            {/* Control de paginación del historial */}
            <Paginacion
              pagina={paginaHistorial}
              totalEnPagina={historialCerrados?.length ?? 0}
              pageSize={PAGE_SIZE}
              onChange={setPaginaHistorial}
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
  /**
   * Total exacto del conjunto (opcional). Cuando se provee, la existencia de una
   * página siguiente se deriva de `(pagina + 1) * pageSize < total` (exacto, FRH-009).
   * Sin él se conserva la heurística `totalEnPagina === pageSize` (pestaña de tickets).
   */
  total?: number;
  /** Callback que recibe el nuevo índice de página al navegar. */
  onChange: (pagina: number) => void;
}

/**
 * Control de paginación offset-based.
 *
 * Con `total` provisto (cola de revisión), la página siguiente existe si y solo si
 * `(pagina + 1) * pageSize < total`: es la detección exacta que habilita el total
 * del recurso de conteo. Sin `total` (pestaña de tickets), se conserva la
 * heurística previa: si la página actual tiene exactamente `pageSize` elementos,
 * probablemente haya más.
 */
export function Paginacion({
  pagina,
  totalEnPagina,
  pageSize,
  total,
  onChange,
}: PaginacionProps) {
  const hayAnterior = pagina > 0;
  const haySiguiente =
    total !== undefined ? (pagina + 1) * pageSize < total : totalEnPagina === pageSize;

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
