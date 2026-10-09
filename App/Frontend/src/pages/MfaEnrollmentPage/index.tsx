/**
 * Pagina de enrollment del segundo factor MFA — ruta "/mfa/enroll".
 *
 * Responsabilidad:
 *   Inicia el enrollment TOTP de la sesion autenticada y muestra, UNA sola vez,
 *   el secreto, el URI otpauth y los codigos de recuperacion de un solo uso.
 *   Requiere autenticacion (se monta bajo ProtectedRoute).
 */

import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { useAuth, type MfaEnrollmentData } from '@/contexts/AuthContext';

export default function MfaEnrollmentPage() {
  const { enrollMfa } = useAuth();

  const [data, setData] = useState<MfaEnrollmentData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    enrollMfa()
      .then((enrollment) => {
        if (active) setData(enrollment);
      })
      .catch(() => {
        if (active) {
          setError('No se pudo iniciar el enrollment de MFA. Verifique su sesión.');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [enrollMfa]);

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto mt-16">
        <Card>
          <CardHeader>
            <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <ShieldCheck className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>Configurar segundo factor (MFA)</CardTitle>
            <CardDescription>
              Escanee el código con su aplicación autenticadora o cargue el secreto
              manualmente. Guarde los códigos de recuperación: se muestran una sola vez.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {error && <ErrorAlert titulo="Error de enrollment" mensaje={error} />}
            {loading && <p>Cargando enrollment…</p>}

            {data && (
              <>
                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Secreto TOTP</h3>
                  <code
                    data-testid="mfa-secret"
                    className="block break-all rounded bg-muted p-3 text-sm"
                  >
                    {data.secret}
                  </code>
                </div>

                <div className="space-y-2">
                  <h3 className="text-sm font-medium">URI otpauth</h3>
                  <code className="block break-all rounded bg-muted p-3 text-xs">
                    {data.otpauthUri}
                  </code>
                </div>

                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Códigos de recuperación</h3>
                  <ul
                    data-testid="mfa-recovery-codes"
                    className="grid grid-cols-2 gap-2 rounded bg-muted p-3 text-sm"
                  >
                    {data.recoveryCodes.map((code) => (
                      <li key={code} className="font-mono">
                        {code}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  );
}
