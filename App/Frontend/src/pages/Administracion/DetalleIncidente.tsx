/**
 * Vista de detalle de incidente de SOLO LECTURA y presentacional (c-83, D2).
 *
 * Responsabilidad:
 *   Renderiza toda la informacion disponible de un incidente y su clasificacion
 *   principal para que el operador decida sin salir de la superficie que la invoca.
 *   NO consulta ni muta datos: recibe el `IncidenteRead` y la clasificacion (o
 *   `null`) y compone la vista. El fetch, el estado de carga/error y los controles
 *   editables viven en cada dialogo contenedor.
 *
 * Reutilizacion (FRH-004):
 *   La usan tanto `TicketDetailDialog` (detalle del ticket) como
 *   `ValidarClasificacionDialog` (revision humana), de modo que un cambio en los
 *   campos mostrados se refleja en ambas superficies sin divergencia.
 *
 * Privacidad (FRH-001):
 *   Solo se muestra `descripcion_pseudonimizada`; la descripcion original cifrada
 *   con PII nunca se expone. No se muestran `reportante_empleado_id`,
 *   `ingresado_en` ni `persistido_en` (OQ3).
 */
import type { ReactNode } from 'react';
import {
  Calendar,
  Lock,
  Mail,
  FileText,
  Brain,
  AlertTriangle,
  Tag,
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import { SectorBadge } from '@/components/shared/SectorBadge';
import { EstadoBadge } from '@/components/shared/EstadoBadge';
import { PrioridadBadge } from '@/components/shared/PrioridadBadge';
import { ConfianzaIndicator } from '@/components/shared/ConfianzaIndicator';
import { formatearFecha, formatearEtapa } from '@/utils/formatters';
import type { IncidenteRead } from '@/types/incidente';
import type { ClasificacionLogRead } from '@/types/clasificacion';

interface DetalleIncidenteProps {
  /** Incidente completo obtenido de GET /api/v1/incidentes/{id}. */
  incidente: IncidenteRead;
  /** Clasificacion principal del incidente; `null` si aun no hay registro. */
  clasificacion: ClasificacionLogRead | null;
}

/**
 * Componente interno de presentacion clave-valor de campos de detalle.
 * Cada instancia muestra un icono, una etiqueta descriptiva y el valor.
 */
function CampoDetalle({
  icono,
  etiqueta,
  children,
}: {
  icono: ReactNode;
  etiqueta: string;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {icono}
        {etiqueta}
      </div>
      <div className="text-sm">{children}</div>
    </div>
  );
}

export function DetalleIncidente({ incidente, clasificacion }: DetalleIncidenteProps) {
  const descripcion = incidente.descripcion_pseudonimizada?.trim();
  const sectoresAdicionalesIncidente = incidente.sectores_adicionales ?? [];
  const sectoresPredichos = clasificacion?.sectores_predichos ?? [];
  const sectoresValidados = clasificacion?.sectores_validados ?? [];

  return (
    <div className="space-y-5">
      {/* Indicador de revision pendiente (FRH-002) */}
      {incidente.requiere_revision_humana && (
        <div className="flex items-center gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded-md text-amber-800 text-sm">
          <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-600" />
          Este incidente requiere revision humana (confianza insuficiente).
        </div>
      )}

      {/* Indicador de solo lectura para incidentes en estado terminal */}
      {incidente.estado.es_terminal && (
        <div className="flex items-center gap-2 p-2.5 bg-slate-100 border border-slate-200 rounded-md text-slate-600 text-sm">
          <Lock className="h-4 w-4 flex-shrink-0 text-slate-500" />
          Solo lectura — Cerrado. Este incidente esta en estado terminal y no puede ser
          modificado.
        </div>
      )}

      {/* Grilla de metadatos principales (FRH-002) */}
      <div className="grid grid-cols-2 gap-4">
        <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Estado">
          <EstadoBadge nombre={incidente.estado.nombre} />
        </CampoDetalle>

        <CampoDetalle icono={<Brain className="h-3.5 w-3.5" />} etiqueta="Sector Asignado">
          <SectorBadge nombre={incidente.sector?.nombre} />
        </CampoDetalle>

        <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Prioridad">
          <PrioridadBadge prioridad={incidente.prioridad} />
        </CampoDetalle>

        <CampoDetalle icono={<Mail className="h-3.5 w-3.5" />} etiqueta="Canal de Origen">
          <span className="capitalize">{incidente.canal_origen?.nombre ?? 'Desconocido'}</span>
        </CampoDetalle>

        <CampoDetalle icono={<Calendar className="h-3.5 w-3.5" />} etiqueta="Creado">
          {formatearFecha(incidente.created_at)}
        </CampoDetalle>

        <CampoDetalle
          icono={<Calendar className="h-3.5 w-3.5" />}
          etiqueta="Última actualización"
        >
          {formatearFecha(incidente.updated_at)}
        </CampoDetalle>

        {sectoresAdicionalesIncidente.length > 0 && (
          <CampoDetalle
            icono={<Tag className="h-3.5 w-3.5" />}
            etiqueta="Sectores Adicionales"
          >
            <div className="flex flex-wrap gap-1.5">
              {sectoresAdicionalesIncidente.map((sector) => (
                <SectorBadge key={sector.id} nombre={sector.nombre} />
              ))}
            </div>
          </CampoDetalle>
        )}
      </div>

      <Separator />

      {/* Descripcion pseudonimizada del incidente (FRH-001) */}
      <CampoDetalle icono={<FileText className="h-3.5 w-3.5" />} etiqueta="Descripción">
        {descripcion ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap bg-muted/40 rounded-md p-3 border">
            {descripcion}
          </p>
        ) : (
          <p className="text-sm italic text-muted-foreground">
            Sin descripción disponible.
          </p>
        )}
      </CampoDetalle>

      {/* Resultado de clasificacion (FRH-003) */}
      {clasificacion && (
        <>
          <Separator />
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-1.5">
              <Brain className="h-3.5 w-3.5" />
              Clasificación Automática
            </p>
            <div className="grid grid-cols-2 gap-4">
              <CampoDetalle icono={null} etiqueta="Sector Predicho">
                <SectorBadge nombre={clasificacion.sector_predicho?.nombre} />
              </CampoDetalle>
              <CampoDetalle icono={null} etiqueta="Confianza">
                <ConfianzaIndicator confianza={clasificacion.confianza} />
              </CampoDetalle>
              <CampoDetalle icono={null} etiqueta="Etapa del Pipeline">
                <span className="text-sm">{formatearEtapa(clasificacion.etapa)}</span>
              </CampoDetalle>
              {clasificacion.sector_validado && (
                <CampoDetalle icono={null} etiqueta="Sector Validado por Operador">
                  <SectorBadge nombre={clasificacion.sector_validado.nombre} />
                </CampoDetalle>
              )}
            </div>

            {/* Sectores adicionales predichos/validados (FRH-003) */}
            {sectoresPredichos.length > 0 && (
              <CampoDetalle icono={null} etiqueta="Sectores Adicionales Predichos">
                <div className="flex flex-wrap gap-1.5">
                  {sectoresPredichos.map((sector) => (
                    <SectorBadge key={sector.id} nombre={sector.nombre} />
                  ))}
                </div>
              </CampoDetalle>
            )}
            {sectoresValidados.length > 0 && (
              <CampoDetalle icono={null} etiqueta="Sectores Adicionales Validados">
                <div className="flex flex-wrap gap-1.5">
                  {sectoresValidados.map((sector) => (
                    <SectorBadge key={sector.id} nombre={sector.nombre} />
                  ))}
                </div>
              </CampoDetalle>
            )}

            {/* Respuesta raw de Gemini (auditoria, FRH-003) */}
            {clasificacion.respuesta_raw && (
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  Respuesta raw de Gemini
                </p>
                <pre className="text-xs bg-slate-900 text-green-400 rounded-md p-3 overflow-x-auto">
                  {clasificacion.respuesta_raw}
                </pre>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
