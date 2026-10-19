/**
 * Pagina de inicio de sesion — ruta "/login".
 *
 * Responsabilidad:
 *   Presenta un formulario de username + password. Al enviar, invoca
 *   useAuth().login(). Si el backend exige el segundo factor (MFA), muestra el
 *   paso de verificacion y completa el login con verifyMfa(). Si las
 *   credenciales son validas, redirige a "/" (portal de reporte).
 *
 *   Esta pagina es publica: no requiere autenticacion previa. Ofrece ademas un
 *   enlace al enrollment de MFA para las sesiones autenticadas.
 */

import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, LogIn, ShieldCheck } from 'lucide-react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { ErrorAlert } from '@/components/shared/ErrorAlert';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, mfaRequired, verifyMfa } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [mfaCode, setMfaCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!username.trim() || !password.trim()) {
      setError('Debe completar usuario y contraseña.');
      return;
    }

    setLoading(true);
    try {
      const success = await login(username.trim(), password);
      if (success) {
        navigate('/', { replace: true });
      } else if (!mfaRequired) {
        // Si el contexto no marco el reto MFA, las credenciales fueron invalidas.
        setError('Usuario o contraseña incorrectos.');
      }
    } catch {
      setError('Error de conexión con el servidor. Verifique que la API esté activa.');
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!mfaCode.trim()) {
      setError('Ingrese el código de su aplicación autenticadora.');
      return;
    }

    setLoading(true);
    try {
      const success = await verifyMfa(mfaCode.trim());
      if (success) {
        navigate('/', { replace: true });
      } else {
        setError('Código de verificación inválido. Intente nuevamente.');
      }
    } catch {
      setError('Error de conexión con el servidor. Verifique que la API esté activa.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <div className="max-w-md mx-auto mt-16">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              {mfaRequired ? (
                <ShieldCheck className="h-6 w-6 text-primary" />
              ) : (
                <LogIn className="h-6 w-6 text-primary" />
              )}
            </div>
            <CardTitle>{mfaRequired ? 'Verificación en dos pasos' : 'Iniciar Sesión'}</CardTitle>
            <CardDescription>
              {mfaRequired
                ? 'Ingrese el código de su aplicación autenticadora para completar el acceso.'
                : 'Ingrese sus credenciales de operador para acceder al sistema.'}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {mfaRequired ? (
              <form onSubmit={handleMfaSubmit} className="space-y-4" noValidate>
                {error && (
                  <ErrorAlert titulo="Error de verificación" mensaje={error} />
                )}

                <div className="space-y-2">
                  <Label htmlFor="mfa-code">Código MFA</Label>
                  <Input
                    id="mfa-code"
                    type="text"
                    inputMode="numeric"
                    placeholder="123456"
                    value={mfaCode}
                    onChange={(e) => setMfaCode(e.target.value)}
                    autoComplete="one-time-code"
                    autoFocus
                    disabled={loading}
                  />
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Verificando...' : 'Verificar'}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                {error && (
                  <ErrorAlert titulo="Error de inicio de sesión" mensaje={error} />
                )}

                <div className="space-y-2">
                  <Label htmlFor="username">Usuario</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="admin"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username"
                    autoFocus
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Contraseña</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="current-password"
                      disabled={loading}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((v) => !v)}
                      aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                      className="absolute inset-y-0 right-0 flex items-center px-3 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" aria-hidden="true" />
                      ) : (
                        <Eye className="h-4 w-4" aria-hidden="true" />
                      )}
                    </button>
                  </div>
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Ingresando...' : 'Ingresar'}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  <Link to="/mfa/enroll" className="underline underline-offset-4">
                    Configurar segundo factor (MFA)
                  </Link>
                </p>
              </form>
            )}

            {/* Aviso en el punto de recolección (c-66, PRIV-001): enlace visible a la política */}
            <p className="text-center text-sm text-muted-foreground mt-4">
              <Link to="/privacidad" className="underline underline-offset-4">
                Política de Privacidad
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  );
}
