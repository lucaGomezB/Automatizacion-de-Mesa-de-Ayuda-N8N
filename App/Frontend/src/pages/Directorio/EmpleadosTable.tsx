/**
 * Tabla del directorio de empleados (c-89, FDIR-002).
 *
 * Responsabilidad:
 *   Presenta el listado recibido por la pagina con los estados de carga, error
 *   (con reintento) y vacio consistentes con el resto de la aplicacion. Cada fila
 *   expone las acciones de gestion: editar, desactivar/reactivar y borrado ARCO.
 *
 * El nombre de sector se resuelve en runtime desde el catalogo (no se asume un
 * identificador numerico estable); el rol se etiqueta desde `ROLES_EMPLEADO`.
 */
import { Pencil, RefreshCcw, Trash2, UserCheck, UserX } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { extractApiErrorMessage } from '@/services/api';
import { ROLES_EMPLEADO } from '@/types/directorio';
import type { Empleado } from '@/types/directorio';
import type { SectorOpcion } from '@/types/catalog';

interface EmpleadosTableProps {
  empleados: Empleado[];
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  sectores: SectorOpcion[] | undefined;
  onRefetch: () => void;
  onEditar: (empleado: Empleado) => void;
  onToggleActivo: (empleado: Empleado) => void;
  onBorrar: (empleado: Empleado) => void;
}

/** Etiqueta legible del rol a partir del catalogo unico. */
function etiquetaRol(rol: Empleado['rol']): string {
  return ROLES_EMPLEADO.find((r) => r.value === rol)?.label ?? rol;
}

/** Resuelve el nombre canonico del sector a partir de su id (catalogo runtime). */
function nombreSector(
  sectorId: number | null,
  sectores: SectorOpcion[] | undefined
): string {
  if (sectorId === null) return 'Sin sector';
  return sectores?.find((s) => s.id === sectorId)?.nombre ?? `Sector ${sectorId}`;
}

export function EmpleadosTable({
  empleados,
  isLoading,
  isError,
  error,
  sectores,
  onRefetch,
  onEditar,
  onToggleActivo,
  onBorrar,
}: EmpleadosTableProps) {
  if (isLoading) return <LoadingSpinner texto="Cargando empleados…" />;

  if (isError) {
    return (
      <ErrorAlert mensaje={extractApiErrorMessage(error)} onReintentar={onRefetch} />
    );
  }

  if (empleados.length === 0) {
    return (
      <EmptyState
        titulo="Sin empleados"
        descripcion="No hay empleados del directorio para el filtro seleccionado."
      />
    );
  }

  return (
    <div className="rounded-md border overflow-hidden">
      <Table>
        <TableHeader className="bg-muted/50">
          <TableRow>
            <TableHead className="w-24">Legajo</TableHead>
            <TableHead>Nombre</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Sector</TableHead>
            <TableHead>Rol</TableHead>
            <TableHead className="w-28">Estado</TableHead>
            <TableHead className="w-40 text-right">
              <Button
                variant="ghost"
                size="icon"
                onClick={onRefetch}
                title="Actualizar lista"
                className="h-7 w-7"
              >
                <RefreshCcw className="h-3.5 w-3.5" />
              </Button>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {empleados.map((empleado) => (
            <TableRow key={empleado.id}>
              <TableCell className="font-mono text-muted-foreground">
                {empleado.legajo}
              </TableCell>
              <TableCell className="font-medium">{empleado.nombre}</TableCell>
              <TableCell className="text-muted-foreground">{empleado.email}</TableCell>
              <TableCell>{nombreSector(empleado.sector_id, sectores)}</TableCell>
              <TableCell>{etiquetaRol(empleado.rol)}</TableCell>
              <TableCell>
                <Badge variant={empleado.activo ? 'success' : 'muted'}>
                  {empleado.activo ? 'Activo' : 'Inactivo'}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    title="Editar"
                    aria-label={`Editar ${empleado.nombre}`}
                    onClick={() => onEditar(empleado)}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    title={empleado.activo ? 'Desactivar' : 'Reactivar'}
                    aria-label={`${
                      empleado.activo ? 'Desactivar' : 'Reactivar'
                    } ${empleado.nombre}`}
                    onClick={() => onToggleActivo(empleado)}
                  >
                    {empleado.activo ? (
                      <UserX className="h-3.5 w-3.5" />
                    ) : (
                      <UserCheck className="h-3.5 w-3.5" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive"
                    title="Borrado ARCO"
                    aria-label={`Borrar ${empleado.nombre}`}
                    onClick={() => onBorrar(empleado)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
