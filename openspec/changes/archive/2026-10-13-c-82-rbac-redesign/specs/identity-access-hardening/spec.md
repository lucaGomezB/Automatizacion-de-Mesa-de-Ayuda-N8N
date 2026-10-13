## MODIFIED Requirements

### Requirement: IAH-005 — Rol privilegiado a nivel de identidad

El sistema SHALL exponer a nivel de la identidad (`User`) si una cuenta es privilegiada mediante el campo booleano `is_privileged`, con valor por defecto falso. La cuenta `admin` sembrada por la migracion MUST quedar privilegiada y SHALL quedar vinculada a un `Empleado` con rol `administrador_directorio` (sintetico, sin PII real) para que su alcance sea GLOBAL y no vacio. Las cuentas vinculadas a un `Empleado` cuyo rol sea `mesa_de_ayuda` o `administrador_directorio` MUST quedar privilegiadas; las cuentas de rol `usuario_final` y las cuentas sin vinculo ni seed MUST NOT ser privilegiadas. El rol `operador` NO existe y MUST NOT conferir privilegio. El valor de `is_privileged` MUST ser la fuente de verdad para exigir el segundo factor, y el catalogo de roles privilegiados SHALL derivarse del registro unico de politica de rol.

#### Scenario: El admin sembrado es privilegiado

- **WHEN** se consulta la cuenta `admin` creada por la migracion
- **THEN** `is_privileged` es verdadero

#### Scenario: El admin sembrado tiene empleado administrador_directorio

- **WHEN** se inspecciona la cuenta `admin` sembrada por la migracion
- **THEN** esta vinculada a un `Empleado` `administrador_directorio` sintetico (sin PII real), por lo que su alcance es GLOBAL y no vacio

#### Scenario: Cuenta vinculada a empleado privilegiado es privilegiada

- **WHEN** una cuenta se vincula a un `Empleado` con rol `mesa_de_ayuda` o `administrador_directorio`
- **THEN** la cuenta queda marcada como privilegiada

#### Scenario: Cuenta de usuario final no es privilegiada

- **WHEN** una cuenta se vincula a un `Empleado` con rol `usuario_final`
- **THEN** la cuenta no es privilegiada

#### Scenario: El rol operador ya no existe

- **WHEN** se inspecciona el catalogo de roles privilegiados
- **THEN** no incluye `operador`

#### Scenario: Cuenta nueva sin vinculo tiene el valor por defecto

- **WHEN** se crea una cuenta sin vinculo a un `Empleado` y sin seed de privilegio
- **THEN** `is_privileged` es falso por defecto
