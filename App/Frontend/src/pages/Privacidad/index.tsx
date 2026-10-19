/**
 * Superficie de politica de privacidad — ruta publica "/privacidad" (c-66, PRIV-001 / PRIV-002).
 *
 * Responsabilidad:
 *   Presenta al titular la informacion de tratamiento (finalidad, responsable,
 *   destinatarios, bases de licitud y transferencia internacional), los derechos
 *   con sus plazos y el canal para ejercerlos. El texto editorial vive en
 *   `privacidadContent.ts` (testeable de forma aislada).
 *
 *   Es una pagina estatica y autocontenida: NO monta el encabezado de la
 *   aplicacion (que depende de la sesion) y NO recolecta datos personales. Se
 *   declara FUERA de `ProtectedRoute` en `main.tsx` para que sea alcanzable sin
 *   sesion, en el punto de recoleccion del canal web.
 *
 *   Encuadre: el texto usa lenguaje de alineacion ("alineado con") y NO afirma
 *   certificacion ni conformidad.
 */
import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import {
  ADVERTENCIA_RESPUESTAS_AUTOMATICAS,
  INTRO_PRIVACIDAD,
  SECCIONES_PRIVACIDAD,
  TITULO_PRIVACIDAD,
} from './privacidadContent';

export default function Privacidad() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-8">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <h1 className="text-2xl font-semibold text-primary">{TITULO_PRIVACIDAD}</h1>
        </div>
        <p className="text-muted-foreground text-sm mb-6">{INTRO_PRIVACIDAD}</p>

        <Card>
          <CardHeader>
            <CardTitle>Informacion al titular</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-sm text-foreground">
            {SECCIONES_PRIVACIDAD.map((seccion, i) => (
              <Fragment key={seccion.titulo}>
                {i > 0 && <Separator />}
                <section>
                  <h2 className="font-semibold mb-1">{seccion.titulo}</h2>
                  {seccion.parrafos.map((parrafo) => (
                    <p key={parrafo} className="text-muted-foreground">
                      {parrafo}
                    </p>
                  ))}
                </section>
              </Fragment>
            ))}

            <Separator />

            <p className="text-xs text-muted-foreground">
              {ADVERTENCIA_RESPUESTAS_AUTOMATICAS}
            </p>
          </CardContent>
        </Card>

        <p className="text-center text-sm mt-6">
          <Link to="/" className="underline underline-offset-4">
            Volver al portal
          </Link>
        </p>
      </main>
    </div>
  );
}
