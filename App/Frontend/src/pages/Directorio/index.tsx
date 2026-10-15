/**
 * Pagina del directorio de empleados — ruta "/directorio" (c-89, FDIR-001..006).
 *
 * Responsabilidad:
 *   Ofrece al `administrador_directorio` la superficie de gestion del directorio
 *   sobre la API EXISTENTE: alta, listado con filtro, edicion, activar/desactivar,
 *   borrado ARCO y purga por retencion. La lista se pagina del lado del cliente
 *   (el endpoint devuelve un arreglo sin paginar; D5) reutilizando `Paginacion`.
 *
 * Acceso: el guard de ruta por rol (`requiereRol="administrador_directorio"`) y el
 * backend (`require_directorio_admin`) son la frontera de seguridad; la UI es UX.
 */
import { useState } from 'react';
import { Plus, Trash2, Users } from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Paginacion } from '@/pages/Administracion';
import {
  useActualizarEmpleado,
  useBorrarEmpleadoArco,
  useCrearEmpleado,
  useEmpleadosDirectorio,
  usePurgarDirectorio,
} from '@/hooks/useDirectorio';
import { useSectores } from '@/hooks/useSectores';
import { EmpleadosTable } from './EmpleadosTable';
import { EmpleadoFormDialog, type EmpleadoFormPayload } from './EmpleadoFormDialog';
import { ConfirmarBorradoDialog } from './ConfirmarBorradoDialog';
import { ConfirmarPurgaDialog } from './ConfirmarPurgaDialog';
import type { Empleado } from '@/types/directorio';

/** Tamano de pagina de la lista del directorio (D5). */
const PAGE_SIZE = 20;

/** Opciones del filtro de estado del directorio. */
type FiltroEstado = 'todos' | 'activos';

export default function DirectorioPage() {
  const [filtro, setFiltro] = useState<FiltroEstado>('todos');
  const [pagina, setPagina] = useState(0);

  // Estado de dialogos.
  const [formAbierto, setFormAbierto] = useState(false);
  const [empleadoEditando, setEmpleadoEditando] = useState<Empleado | null>(null);
  const [empleadoABorrar, setEmpleadoABorrar] = useState<Empleado | null>(null);
  const [purgaAbierta, setPurgaAbierta] = useState(false);

  const soloActivos = filtro === 'activos';

  const { data: empleados, isLoading, isError, error, refetch } =
    useEmpleadosDirectorio(soloActivos);
  const { data: sectores } = useSectores();

  const crear = useCrearEmpleado();
  const actualizar = useActualizarEmpleado();
  const borrar = useBorrarEmpleadoArco();
  const purgar = usePurgarDirectorio();

  const total = empleados?.length ?? 0;
  const visibles = (empleados ?? []).slice(pagina * PAGE_SIZE, (pagina + 1) * PAGE_SIZE);

  const handleFiltroChange = (valor: string) => {
    setFiltro(valor as FiltroEstado);
    setPagina(0);
  };

  const abrirAlta = () => {
    crear.reset();
    actualizar.reset();
    setEmpleadoEditando(null);
    setFormAbierto(true);
  };

  const abrirEdicion = (empleado: Empleado) => {
    crear.reset();
    actualizar.reset();
    setEmpleadoEditando(empleado);
    setFormAbierto(true);
  };

  const cerrarForm = () => {
    setFormAbierto(false);
    setEmpleadoEditando(null);
    crear.reset();
    actualizar.reset();
  };

  const handleSubmitForm = (values: EmpleadoFormPayload) => {
    if (empleadoEditando) {
      actualizar.mutate(
        { id: empleadoEditando.id, payload: values },
        { onSuccess: cerrarForm }
      );
    } else {
      crear.mutate(values, { onSuccess: cerrarForm });
    }
  };

  const handleToggleActivo = (empleado: Empleado) => {
    actualizar.mutate({ id: empleado.id, payload: { activo: !empleado.activo } });
  };

  const abrirBorrado = (empleado: Empleado) => {
    borrar.reset();
    setEmpleadoABorrar(empleado);
  };

  const cerrarBorrado = () => {
    setEmpleadoABorrar(null);
    borrar.reset();
  };

  const handleConfirmarBorrado = () => {
    if (!empleadoABorrar) return;
    borrar.mutate(empleadoABorrar.id, { onSuccess: cerrarBorrado });
  };

  const abrirPurga = () => {
    purgar.reset();
    setPurgaAbierta(true);
  };

  const handleConfirmarPurga = () => {
    purgar.mutate(undefined, { onSuccess: () => setPurgaAbierta(false) });
  };

  return (
    <PageWrapper>
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-primary flex items-center gap-2">
              <Users className="h-6 w-6" />
              Directorio de Empleados
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Alta, edicion, activacion y borrado del directorio de empleados.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={abrirPurga}>
              <Trash2 className="h-4 w-4 mr-1" />
              Purgar directorio
            </Button>
            <Button onClick={abrirAlta}>
              <Plus className="h-4 w-4 mr-1" />
              Nuevo empleado
            </Button>
          </div>
        </div>

        {/* Resultado de la purga (FDIR-006): conteo devuelto por el backend */}
        {purgar.isSuccess && purgar.data && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md text-green-800 text-sm">
            Se purgaron {purgar.data.purgados} registros por retencion.
          </div>
        )}

        {/* Barra de filtros */}
        <div className="flex flex-wrap items-center gap-3">
          <Select value={filtro} onValueChange={handleFiltroChange}>
            <SelectTrigger aria-label="Filtro de estado" className="h-9 w-44 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos</SelectItem>
              <SelectItem value="activos">Solo activos</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <EmpleadosTable
          empleados={visibles}
          isLoading={isLoading}
          isError={isError}
          error={error}
          sectores={sectores}
          onRefetch={() => void refetch()}
          onEditar={abrirEdicion}
          onToggleActivo={handleToggleActivo}
          onBorrar={abrirBorrado}
        />

        <Paginacion
          pagina={pagina}
          totalEnPagina={visibles.length}
          pageSize={PAGE_SIZE}
          total={total}
          onChange={setPagina}
        />
      </div>

      {formAbierto && (
        <EmpleadoFormDialog
          key={empleadoEditando?.id ?? 'nuevo'}
          open
          empleado={empleadoEditando}
          isPending={empleadoEditando ? actualizar.isPending : crear.isPending}
          error={empleadoEditando ? actualizar.error : crear.error}
          onClose={cerrarForm}
          onSubmit={handleSubmitForm}
        />
      )}

      {empleadoABorrar && (
        <ConfirmarBorradoDialog
          open
          empleado={empleadoABorrar}
          isPending={borrar.isPending}
          error={borrar.error}
          onClose={cerrarBorrado}
          onConfirm={handleConfirmarBorrado}
        />
      )}

      {purgaAbierta && (
        <ConfirmarPurgaDialog
          open
          isPending={purgar.isPending}
          error={purgar.error}
          onClose={() => setPurgaAbierta(false)}
          onConfirm={handleConfirmarPurga}
        />
      )}
    </PageWrapper>
  );
}
