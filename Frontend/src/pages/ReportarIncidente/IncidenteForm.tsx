/**
 * Formulario de reporte de incidente — componente central del portal de usuarios finales.
 *
 * Responsabilidad:
 *   Gestiona la entrada de datos del incidente con validación en el cliente mediante
 *   React Hook Form y delega el envío al hook `useReportarIncidente` (mutación POST).
 *
 * Campos del formulario:
 *   - `nombre_usuario`  : identificación del solicitante (UX); NO se envía a la API.
 *   - `sector_usuario`  : sector de pertenencia (UX); NO se envía a la API.
 *   - `prioridad`       : baja | media | alta; se envía al backend.
 *   - `descripcion`     : texto libre; se envía al backend y al clasificador Gemini.
 *   - `canal_origen_id` : hardcodeado como `FORMULARIO_WEB` (ID=2) en el submit.
 *
 * Validación especial:
 *   La descripción requiere al menos 15 palabras para garantizar que Gemini disponga
 *   de contexto suficiente para una clasificación confiable (umbral UX, no de backend).
 *   Un indicador de progreso visual facilita esta restricción al usuario.
 */
import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Send, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useReportarIncidente } from '@/hooks/useReportarIncidente';
import { validarMinimoPalabras, validarNoVacio, contarPalabras } from '@/utils/validators';
import { extractApiErrorMessage } from '@/services/api';
import type { IncidenteFormData, IncidenteRead } from '@/types/incidente';
import { CANAL_ORIGEN_IDS } from '@/types/catalog';

const MINIMO_PALABRAS = 15;

interface IncidenteFormProps {
  onSuccess: (incidente: IncidenteRead, nombreUsuario: string) => void;
}

export function IncidenteForm({ onSuccess }: IncidenteFormProps) {
  const { mutate, isPending, error, reset: resetMutation } = useReportarIncidente();

  const {
    register,
    handleSubmit,
    control,
    watch,
    reset,
    formState: { errors },
  } = useForm<IncidenteFormData>({
    defaultValues: {
      descripcion: '',
      prioridad: 'media',
      nombre_usuario: '',
      sector_usuario: 'Sistemas',
    },
  });

  const descripcionActual = watch('descripcion');
  const palabrasActuales = contarPalabras(descripcionActual);
  const porcentajeProgreso = Math.min((palabrasActuales / MINIMO_PALABRAS) * 100, 100);
  const cumpleMinimo = palabrasActuales >= MINIMO_PALABRAS;

  // Limpiar el error de mutación si el usuario corrige el formulario
  useEffect(() => {
    if (error) resetMutation();
  }, [descripcionActual]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSubmit = (datos: IncidenteFormData) => {
    mutate(
      {
        descripcion: datos.descripcion.trim(),
        prioridad: datos.prioridad,
        canal_origen_id: CANAL_ORIGEN_IDS.FORMULARIO_WEB,
      },
      {
        onSuccess: (incidente) => {
          reset();
          onSuccess(incidente, datos.nombre_usuario);
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>

      {/* Error de API */}
      {error && (
        <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
          <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span>{extractApiErrorMessage(error)}</span>
        </div>
      )}

      {/* Campo: Nombre del usuario */}
      <div className="space-y-1.5">
        <Label htmlFor="nombre_usuario">
          Nombre completo <span className="text-destructive">*</span>
        </Label>
        <Input
          id="nombre_usuario"
          placeholder="Ej.: María González"
          {...register('nombre_usuario', {
            validate: (v) => validarNoVacio(v, 'El nombre'),
          })}
          className={errors.nombre_usuario ? 'border-destructive' : ''}
        />
        {errors.nombre_usuario && (
          <p className="text-xs text-destructive">{errors.nombre_usuario.message}</p>
        )}
      </div>

      {/* Campo: Sector del usuario (informativo) */}
      <div className="space-y-1.5">
        <Label htmlFor="sector_usuario">
          Sector al que pertenece
          <span className="ml-1.5 text-xs text-muted-foreground font-normal">(informativo)</span>
        </Label>
        <Controller
          name="sector_usuario"
          control={control}
          render={({ field }) => (
            <Select value={field.value} onValueChange={field.onChange}>
              <SelectTrigger id="sector_usuario">
                <SelectValue placeholder="Seleccioná tu sector" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Sistemas">Sistemas</SelectItem>
                <SelectItem value="Operaciones">Operaciones</SelectItem>
                <SelectItem value="Soporte Técnico">Soporte Técnico</SelectItem>
              </SelectContent>
            </Select>
          )}
        />
        <p className="text-xs text-muted-foreground">
          El sector de atención es asignado automáticamente por el clasificador de IA.
        </p>
      </div>

      {/* Campo: Prioridad */}
      <div className="space-y-1.5">
        <Label htmlFor="prioridad">
          Prioridad <span className="text-destructive">*</span>
        </Label>
        <Controller
          name="prioridad"
          control={control}
          render={({ field }) => (
            <Select value={field.value} onValueChange={field.onChange}>
              <SelectTrigger id="prioridad">
                <SelectValue placeholder="Seleccioná la prioridad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="baja">Baja</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="alta">Alta</SelectItem>
              </SelectContent>
            </Select>
          )}
        />
      </div>

      {/* Campo: Canal de origen (solo lectura) */}
      <div className="space-y-1.5">
        <Label>Canal de origen</Label>
        <Input value="Formulario Web" readOnly className="bg-muted cursor-not-allowed text-muted-foreground" />
      </div>

      {/* Campo: Descripción del incidente */}
      <div className="space-y-1.5">
        <Label htmlFor="descripcion">
          Descripción del incidente <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="descripcion"
          rows={6}
          placeholder="Describí el problema con el mayor detalle posible: qué ocurrió, cuándo, en qué equipo o sistema, y qué impacto tiene en tus tareas."
          {...register('descripcion', {
            validate: (v) => validarMinimoPalabras(v, MINIMO_PALABRAS),
          })}
          className={errors.descripcion ? 'border-destructive' : ''}
        />

        {/* Indicador de progreso de palabras */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex-1 bg-slate-200 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${cumpleMinimo ? 'bg-green-500' : 'bg-amber-400'}`}
              style={{ width: `${porcentajeProgreso}%` }}
            />
          </div>
          <span className={`text-xs tabular-nums flex-shrink-0 ${cumpleMinimo ? 'text-green-600' : 'text-muted-foreground'}`}>
            {palabrasActuales} / {MINIMO_PALABRAS} palabras
          </span>
        </div>

        {errors.descripcion && (
          <p className="text-xs text-destructive">{errors.descripcion.message}</p>
        )}
      </div>

      {/* Botón de envío */}
      <Button type="submit" disabled={isPending} className="w-full sm:w-auto" size="lg">
        {isPending ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Clasificando y registrando…
          </>
        ) : (
          <>
            <Send className="h-4 w-4" />
            Enviar incidente
          </>
        )}
      </Button>
    </form>
  );
}
