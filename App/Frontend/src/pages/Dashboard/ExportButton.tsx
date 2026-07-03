/**
 * Boton de exportacion de grafico a PNG via html2canvas.
 */
import { useCallback } from 'react';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ExportButtonProps {
  /** Ref al contenedor DOM del grafico a exportar. */
  containerRef: React.RefObject<HTMLDivElement | null>;
  /** Nombre del archivo descargado (sin extension). */
  filename: string;
}

export function ExportButton({ containerRef, filename }: ExportButtonProps) {
  const handleExport = useCallback(async () => {
    if (!containerRef.current) return;

    try {
      // Dynamic import para tree-shaking: html2canvas solo se carga al exportar
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(containerRef.current, {
        backgroundColor: '#ffffff',
        scale: 2, // Alta resolucion
      });
      const link = document.createElement('a');
      link.download = `${filename}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch {
      alert('No se pudo exportar el grafico. Intente de nuevo.');
    }
  }, [containerRef, filename]);

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleExport}
      className="h-7 text-xs"
    >
      <Download className="h-3 w-3 mr-1" />
      Exportar
    </Button>
  );
}
