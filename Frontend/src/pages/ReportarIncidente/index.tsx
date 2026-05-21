/**
 * Página principal del Portal de Reporte de Incidentes — ruta "/".
 *
 * Responsabilidad:
 *   Gestiona el flujo de dos estados para el usuario final:
 *   1. Estado formulario : presenta `IncidenteForm` para que el usuario complete los datos.
 *   2. Estado confirmación: presenta `SuccessCard` con el número de ticket, sector asignado
 *      por el pipeline de IA y nivel de confianza del clasificador.
 *
 *   La transición entre estados la controla `handleSuccess`, que recibe el `IncidenteRead`
 *   devuelto por el backend y desplaza la página al inicio para mostrar el mensaje de éxito.
 *   `handleNuevoReporte` resetea el estado para comenzar un nuevo reporte.
 */
import { useState } from 'react';
import { ShieldAlert, Info } from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { IncidenteForm } from './IncidenteForm';
import { SuccessCard } from './SuccessCard';
import type { IncidenteRead } from '@/types/incidente';

interface SubmissionResult {
  incidente: IncidenteRead;
  nombreUsuario: string;
}

export default function ReportarIncidentePage() {
  const [resultado, setResultado] = useState<SubmissionResult | null>(null);

  const handleSuccess = (incidente: IncidenteRead, nombreUsuario: string) => {
    setResultado({ incidente, nombreUsuario });
    // Desplazar al inicio de la página para mostrar la confirmación
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNuevoReporte = () => {
    setResultado(null);
  };

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto space-y-6">

        {/* Encabezado de sección */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldAlert className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-semibold text-primary">
              Portal de Reporte de Incidentes
            </h1>
          </div>
          <p className="text-muted-foreground text-sm">
            Completá el formulario para registrar un incidente. El sistema lo clasificará
            automáticamente mediante inteligencia artificial (Gemini 2.5 Flash).
          </p>
        </div>

        {/* Tarjeta de éxito o formulario */}
        {resultado ? (
          <SuccessCard
            incidente={resultado.incidente}
            nombreUsuario={resultado.nombreUsuario}
            onNuevoReporte={handleNuevoReporte}
          />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Nuevo Incidente</CardTitle>
              <CardDescription>
                Todos los campos marcados con <span className="text-destructive">*</span> son
                obligatorios.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <IncidenteForm onSuccess={handleSuccess} />
            </CardContent>
          </Card>
        )}

        {/* Nota informativa sobre el proceso de clasificación */}
        {!resultado && (
          <div className="flex items-start gap-2 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
            <Info className="h-4 w-4 flex-shrink-0 mt-0.5 text-blue-600" />
            <p>
              El incidente será clasificado automáticamente en una de tres categorías:{' '}
              <strong>Sistemas</strong>, <strong>Operaciones</strong> o{' '}
              <strong>Soporte Técnico</strong>. Si la confianza del modelo es baja (&lt; 70%),
              el ticket quedará marcado para revisión humana.
            </p>
          </div>
        )}

        <Separator />
        <p className="text-xs text-muted-foreground text-center">
          Sistema de Automatización de Mesa de Ayuda — UTN · Tesis 2026
        </p>
      </div>
    </PageWrapper>
  );
}
