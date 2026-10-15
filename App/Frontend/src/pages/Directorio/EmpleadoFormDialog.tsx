/**
 * Dialogo de alta/edicion de un empleado del directorio (c-89, FDIR-003/004).
 *
 * Responsabilidad:
 *   Captura y valida los campos del empleado. Es un componente PRESENTACIONAL:
 *   no conoce la API; delega el envio al padre via `onSubmit` y muestra el error
 *   del backend que el padre le pasa (la validacion de UX no reemplaza al backend).
 *
 * Regla de sector (D4): el selector de sector se muestra siempre, pero solo es
 * OBLIGATORIO cuando el rol seleccionado lo exige (`gestion_incidentes`).
 */
import { useForm, Controller } from 'react-hook-form';
import { Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useSectores } from '@/hooks/useSectores';
import { extractApiErrorMessage } from '@/services/api';
import { ROLES_EMPLEADO, rolRequiereSector } from '@/types/directorio';
import type { Empleado, RolEmpleado } from '@/types/directorio';

/** Valores del formulario de empleado (controlados como texto). */
export interface EmpleadoFormValues {
  legajo: string;
  nombre: string;
  email: string;
  telefono: string;
  rol: RolEmpleado;
  sector_id: number | null;
}

/** Payload normalizado que el formulario entrega al padre (telefono vacio -> null). */
export interface EmpleadoFormPayload {
  legajo: string;
  nombre: string;
  email: string;
  telefono: string | null;
  rol: RolEmpleado;
  sector_id: number | null;
}

interface EmpleadoFormDialogProps {
  open: boolean;
  /** Empleado en edicion; null/undefined = alta. */
  empleado?: Empleado | null;
  isPending: boolean;
  /** Error del backend a mostrar sin perder los datos ingresados. */
  error: unknown;
  onClose: () => void;
  onSubmit: (payload: EmpleadoFormPayload) => void;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function EmpleadoFormDialog({
  open,
  empleado = null,
  isPending,
  error,
  onClose,
  onSubmit,
}: EmpleadoFormDialogProps) {
  const { data: sectores } = useSectores();
  const esEdicion = empleado !== null;

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<EmpleadoFormValues>({
    defaultValues: {
      legajo: empleado?.legajo ?? '',
      nombre: empleado?.nombre ?? '',
      email: empleado?.email ?? '',
      telefono: empleado?.telefono ?? '',
      rol: empleado?.rol ?? 'usuario_final',
      sector_id: empleado?.sector_id ?? null,
    },
  });

  const rolActual = watch('rol');
  const sectorRequerido = rolRequiereSector(rolActual);

  const onSubmitForm = (values: EmpleadoFormValues) => {
    onSubmit({
      legajo: values.legajo.trim(),
      nombre: values.nombre.trim(),
      email: values.email.trim(),
      telefono: values.telefono.trim() || null,
      rol: values.rol,
      sector_id: values.sector_id,
    });
  };

  return (
    <Dialog open={open} onOpenChange={(abierto) => !abierto && onClose()}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>{esEdicion ? 'Editar empleado' : 'Nuevo empleado'}</DialogTitle>
          <DialogDescription>
            {esEdicion
              ? 'Modificá los datos del empleado. El backend valida unicidad y coherencia.'
              : 'Completá los datos del empleado. El backend valida unicidad y coherencia.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-4" noValidate>
          {error !== null && error !== undefined && (
            <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
              {extractApiErrorMessage(error)}
            </div>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="legajo">
              Legajo <span className="text-destructive">*</span>
            </Label>
            <Input
              id="legajo"
              {...register('legajo', {
                validate: (v) => v.trim().length > 0 || 'El legajo es obligatorio.',
              })}
              className={errors.legajo ? 'border-destructive' : ''}
            />
            {errors.legajo && (
              <p className="text-xs text-destructive">{errors.legajo.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="nombre">
              Nombre <span className="text-destructive">*</span>
            </Label>
            <Input
              id="nombre"
              {...register('nombre', {
                validate: (v) => v.trim().length > 0 || 'El nombre es obligatorio.',
              })}
              className={errors.nombre ? 'border-destructive' : ''}
            />
            {errors.nombre && (
              <p className="text-xs text-destructive">{errors.nombre.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="email">
              Email <span className="text-destructive">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              {...register('email', {
                validate: (v) => {
                  if (v.trim().length === 0) return 'El email es obligatorio.';
                  return EMAIL_REGEX.test(v.trim()) || 'El email no tiene un formato válido.';
                },
              })}
              className={errors.email ? 'border-destructive' : ''}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="telefono">Teléfono</Label>
            <Input id="telefono" {...register('telefono')} />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="rol">
              Rol <span className="text-destructive">*</span>
            </Label>
            <Controller
              name="rol"
              control={control}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger id="rol" aria-label="Rol" className="w-full">
                    <SelectValue placeholder="Seleccioná un rol" />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES_EMPLEADO.map((rol) => (
                      <SelectItem key={rol.value} value={rol.value}>
                        {rol.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="sector">
              Sector
              {sectorRequerido && <span className="text-destructive"> *</span>}
            </Label>
            <Controller
              name="sector_id"
              control={control}
              rules={{
                validate: (v) =>
                  !sectorRequerido ||
                  v !== null ||
                  'El sector es obligatorio para este rol.',
              }}
              render={({ field }) => (
                <Select
                  value={field.value === null ? '' : String(field.value)}
                  onValueChange={(v) => field.onChange(v === '' ? null : Number(v))}
                >
                  <SelectTrigger id="sector" aria-label="Sector" className="w-full">
                    <SelectValue placeholder="Seleccioná un sector" />
                  </SelectTrigger>
                  <SelectContent>
                    {sectores?.map((sector) => (
                      <SelectItem key={sector.id} value={String(sector.id)}>
                        {sector.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {errors.sector_id && (
              <p className="text-xs text-destructive">{errors.sector_id.message}</p>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {esEdicion ? 'Guardar cambios' : 'Guardar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
