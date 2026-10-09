## Purpose

Segundo factor de la capability `identity-access-hardening` (Fase B de `c-63`): agrega un rol privilegiado a nivel de identidad, el segundo factor TOTP para las cuentas privilegiadas (enrollment, verificacion, codigos de recuperacion y secreto cifrado at-rest) y el login en dos pasos aditivo con reto MFA en el frontend, cerrando los controles ISO/IEC 27002 5.15 y 8.5.

## ADDED Requirements

### Requirement: IAH-005 — Rol privilegiado a nivel de identidad

El sistema SHALL exponer a nivel de la identidad (`User`) si una cuenta es privilegiada mediante el campo booleano `is_privileged`, con valor por defecto falso. La cuenta `admin` sembrada por la migracion MUST quedar privilegiada. Las cuentas vinculadas a un `Empleado` cuyo rol sea `operador`, `administrador_directorio` o `mesa_de_ayuda` MUST quedar privilegiadas; las cuentas de rol `usuario_final` y las cuentas sin vinculo ni seed MUST NOT ser privilegiadas. El valor de `is_privileged` MUST ser la fuente de verdad para exigir el segundo factor.

#### Scenario: El admin sembrado es privilegiado

- **WHEN** se consulta la cuenta `admin` creada por la migracion
- **THEN** `is_privileged` es verdadero

#### Scenario: Cuenta vinculada a empleado privilegiado es privilegiada

- **WHEN** una cuenta se vincula a un `Empleado` con rol `operador`, `administrador_directorio` o `mesa_de_ayuda`
- **THEN** la cuenta queda marcada como privilegiada

#### Scenario: Cuenta de usuario final no es privilegiada

- **WHEN** una cuenta se vincula a un `Empleado` con rol `usuario_final`
- **THEN** la cuenta no es privilegiada

#### Scenario: Cuenta nueva sin vinculo tiene el valor por defecto

- **WHEN** se crea una cuenta sin vinculo a un `Empleado` y sin seed de privilegio
- **THEN** `is_privileged` es falso por defecto

### Requirement: IAH-006 — MFA TOTP para cuentas privilegiadas

El sistema SHALL ofrecer enrollment y verificacion de un segundo factor basado en TOTP (RFC 6238) para las cuentas privilegiadas. El enrollment MUST entregar el URI `otpauth://` (con el secreto asociado) para configurar una aplicacion autenticadora. La verificacion de un codigo TOTP valido MUST tener exito; un codigo invalido o expirado MUST ser rechazado. El sistema MUST entregar codigos de recuperacion de un solo uso, almacenados hasheados, y MUST almacenar el secreto TOTP cifrado at-rest (nunca en texto plano). Todo el requisito MUST quedar detras de la bandera `mfa_required_for_privileged`, apagada por defecto en desarrollo y pruebas.

#### Scenario: Enrollment entrega el URI otpauth y el secreto

- **WHEN** una cuenta privilegiada inicia el enrollment de MFA
- **THEN** el sistema devuelve un URI `otpauth://` y el secreto para configurar la aplicacion autenticadora

#### Scenario: Codigo TOTP valido verifica

- **WHEN** se presenta un codigo TOTP valido para la cuenta en la ventana de tiempo vigente
- **THEN** la verificacion tiene exito

#### Scenario: Codigo TOTP invalido o expirado es rechazado

- **WHEN** se presenta un codigo TOTP incorrecto o fuera de la ventana de tiempo
- **THEN** la verificacion es rechazada sin conceder el segundo factor

#### Scenario: Codigo de recuperacion de un solo uso

- **WHEN** se usa un codigo de recuperacion valido y no consumido
- **THEN** el segundo factor se concede y ese codigo queda consumido e inutilizable en adelante

#### Scenario: El secreto TOTP no se almacena en claro

- **WHEN** se persiste el secreto TOTP
- **THEN** el valor almacenado esta cifrado at-rest y no coincide con el secreto en texto plano

#### Scenario: Bandera apagada no exige MFA

- **WHEN** `mfa_required_for_privileged` esta apagada y una cuenta privilegiada inicia el login
- **THEN** el sistema no exige segundo factor

### Requirement: IAH-007 — Login en dos pasos aditivo para cuentas privilegiadas

El sistema SHALL requerir el segundo factor antes de emitir el token cuando una cuenta privilegiada con MFA activo inicie sesion con `mfa_required_for_privileged` encendida. Tras validar la contrasena, `POST /api/v1/auth/login` MUST devolver una respuesta intermedia distinguible que indica "segundo factor requerido" junto con un ticket corto, y MUST NOT emitir el token de acceso. `POST /api/v1/auth/mfa/verify` con el ticket y un segundo factor valido MUST completar el login devolviendo `access_token` y `token_type` (preservando los campos actuales del contrato). Un ticket invalido o expirado MUST ser rechazado. Las cuentas no privilegiadas, o con la bandera apagada, MUST completar el login en un solo paso. El frontend MUST presentar el reto de segundo factor cuando la respuesta lo indique.

#### Scenario: Cuenta privilegiada recibe el reto sin token

- **WHEN** una cuenta privilegiada con MFA activo valida su contrasena con la bandera encendida
- **THEN** el sistema responde indicando que el segundo factor es requerido, entrega un ticket y no emite token de acceso

#### Scenario: Verificacion correcta emite el token con los campos actuales

- **WHEN** se presenta el ticket vigente con un segundo factor valido en `POST /api/v1/auth/mfa/verify`
- **THEN** el sistema devuelve `access_token` y `token_type` junto con los campos adicionales definidos

#### Scenario: Ticket invalido o expirado es rechazado

- **WHEN** se presenta un ticket invalido o fuera de su vigencia
- **THEN** el sistema rechaza la verificacion sin emitir token

#### Scenario: Cuenta no privilegiada usa el flujo de un paso

- **WHEN** una cuenta no privilegiada inicia sesion con credenciales validas
- **THEN** el sistema emite el token directamente sin requerir segundo factor

#### Scenario: Flag apagado mantiene el flujo dev de un paso

- **WHEN** `mfa_required_for_privileged` esta apagada y `admin`/`admin123` inicia sesion
- **THEN** el login es exitoso en un solo paso sin reto MFA

#### Scenario: El frontend presenta el reto MFA

- **WHEN** el backend responde que el segundo factor es requerido
- **THEN** el frontend muestra el paso de verificacion de MFA y completa el login al validar el codigo
