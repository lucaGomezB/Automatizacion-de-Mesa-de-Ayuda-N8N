/**
 * Seccion de comentarios del detalle del incidente (c-86, FIH-003 / D7).
 *
 * Responsabilidad:
 *   Lista los comentarios del incidente con el formato `HH:MM:SS DD/MM/AAAA :
 *   {texto}` separados por `----------`, y ofrece agregar uno nuevo a quien
 *   tenga visibilidad del incidente. Es append-only: no hay edicion ni borrado.
 *
 *   Ante una denegacion del backend (403/404 por alcance), se muestra el error y
 *   NO se ofrecen ni se exponen comentarios (FIH-003/FIH-004).
 */
import { useState } from 'react';
import { AlertCircle, Loader2, MessageSquare, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { useComentarios, useAgregarComentario } from '@/hooks/useComentarios';
import { extractApiErrorMessage } from '@/services/api';
import { formatearComentario, SEPARADOR_COMENTARIO } from '@/utils/formatters';

interface ComentariosIncidenteProps {
  /** Id del incidente visible en el detalle. */
  incidenteId: number;
}

export function ComentariosIncidente({ incidenteId }: ComentariosIncidenteProps) {
  const { data: comentarios, isLoading, isError, error } = useComentarios(incidenteId);
  const agregar = useAgregarComentario(incidenteId);
  const [texto, setTexto] = useState('');

  const handleAgregar = () => {
    const limpio = texto.trim();
    if (!limpio) return;
    agregar.mutate(limpio, { onSuccess: () => setTexto('') });
  };

  return (
    <div className="space-y-4">
      <Separator />
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-1.5">
          <MessageSquare className="h-3.5 w-3.5" />
          Comentarios
        </p>

        {/* Lista de comentarios (solo si el incidente esta dentro del alcance) */}
        {isLoading && <LoadingSpinner texto="Cargando comentarios…" />}

        {!isLoading && isError && (
          <ErrorAlert mensaje={extractApiErrorMessage(error)} />
        )}

        {!isLoading && !isError && (
          <>
            {comentarios && comentarios.length > 0 ? (
              <ul className="space-y-2">
                {comentarios.map((comentario, indice) => (
                  <li key={comentario.id}>
                    {indice > 0 && (
                      <p className="text-muted-foreground tracking-widest my-2">
                        {SEPARADOR_COMENTARIO}
                      </p>
                    )}
                    <p className="text-sm leading-relaxed whitespace-pre-wrap bg-muted/40 rounded-md p-3 border tabular-nums">
                      {formatearComentario(comentario.texto, comentario.created_at)}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm italic text-muted-foreground">
                Sin comentarios por el momento.
              </p>
            )}

            {/* Alta de comentario (append-only) */}
            <div className="space-y-2">
              <Label htmlFor="nuevo-comentario" className="text-xs text-muted-foreground">
                Nuevo comentario
              </Label>
              <Textarea
                id="nuevo-comentario"
                value={texto}
                onChange={(e) => setTexto(e.target.value)}
                placeholder="Escribí un comentario…"
                rows={3}
              />
              {agregar.error != null && (
                <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/30 rounded-md text-destructive text-sm">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{extractApiErrorMessage(agregar.error)}</span>
                </div>
              )}
              <Button
                size="sm"
                disabled={agregar.isPending || texto.trim().length === 0}
                onClick={handleAgregar}
              >
                {agregar.isPending ? (
                  <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
                ) : (
                  <Send className="h-3.5 w-3.5 mr-1" />
                )}
                Agregar comentario
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}