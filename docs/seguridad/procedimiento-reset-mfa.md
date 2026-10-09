# Procedimiento: reset administrativo de MFA y re-enrollment forzado

Alcance: cuentas privilegiadas del sistema de Mesa de Ayuda (roles `operador`,
`administrador_directorio`, `mesa_de_ayuda` y el seed `admin`). Aplica al segundo
factor TOTP introducido por `c-63b-mfa-y-rol-privilegiado` (controles ISO/IEC
27002 5.15 y 8.5).

Decision de diseno: el reset administrativo NO se implementa como endpoint en
`c-63b` (OQ-B2 = documentar). La via de recuperacion por codigos de un solo uso
cubre al usuario final; este procedimiento cubre los casos en que el usuario
perdio el dispositivo Y los codigos de recuperacion.

## 1. Requisito de despliegue: MFA en produccion

- `MFA_REQUIRED_FOR_PRIVILEGED` es `false` por defecto (dev/test/CI). Con la
  bandera apagada el login de las cuentas privilegiadas es de un solo paso,
  preservando el flujo de desarrollo (`admin`/`admin123`, `directorio.admin`).
- **En produccion real la bandera MUST habilitarse** (`MFA_REQUIRED_FOR_PRIVILEGED=true`).
  Si permanece apagada, ninguna cuenta privilegiada recibe el reto de segundo
  factor.
- El secreto TOTP se almacena cifrado at-rest con Fernet
  (`PSEUDONYMIZATION_ENCRYPTION_KEY`, la misma clave que usa el cifrado de PII).
  Perder esa clave hace ilegible el secreto y obliga al reset por base de datos
  (seccion 3).

## 2. Reset del segundo factor con acceso administrativo

1. Identificar la cuenta afectada (`users.username`) y verificar la identidad del
   solicitante por un canal fuera de banda.
2. Registrar el pedido en el registro de eventos de seguridad (actor, cuenta,
   motivo, fecha).
3. Ejecutar el reset sobre la base de datos (no existe endpoint en esta fase):

   ```sql
   UPDATE users
      SET totp_secret = NULL,
          totp_enabled = false,
          mfa_recovery_codes = NULL
    WHERE username = '<cuenta>';
   ```

4. Notificar al usuario. En su proximo inicio de sesion, si la bandera esta
   encendida y la cuenta ya no tiene MFA activo, el login es de un solo paso: el
   usuario debe completar el enrollment (`POST /api/v1/auth/mfa/enroll` desde la
   pantalla de configuracion de MFA) antes de que el reto vuelva a exigirse.
5. Revocar las sesiones vigentes de la cuenta (revocacion administrativa por
   `token_version`) para que un token previo no sobreviva al reset.

## 3. Perdida de la clave Fernet

Si se pierde `PSEUDONYMIZATION_ENCRYPTION_KEY`, los secretos TOTP no pueden
descifrarse. El procedimiento es el mismo reset de la seccion 2 (pone el secreto
en `NULL`), tras restaurar una clave valida en el entorno.

## 4. Prevencion

- En el enrollment, el usuario MUST guardar los codigos de recuperacion fuera del
  dispositivo autenticador. Son de un solo uso y estan hasheados con bcrypt.
- El reset administrativo NUNCA devuelve un secreto previo: siempre fuerza un
  nuevo enrollment.

## 5. Referencias

- `openspec/changes/c-63b-mfa-y-rol-privilegiado/design.md` (OQ-B2).
- `App/Backend/app/services/mfa_service.py`.
- `docs/seguridad/plan-respuesta-incidentes-seguridad.md`.
