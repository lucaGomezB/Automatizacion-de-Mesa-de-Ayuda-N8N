# identity-access-hardening — Delta Spec

## Purpose

Endurece el nucleo de autenticacion del sistema (controles ISO/IEC 27002 8.5 y 5.17): valida la fortaleza de las contrasenas, limita los intentos fallidos y acorta, rota y revoca los tokens JWT, preservando de forma aditiva el contrato de login vigente. Es la Fase A de la capacidad `identity-access-hardening`; MFA y rotacion de claves pertenecen a las fases posteriores (c-63b y c-63c).

## ADDED Requirements

### Requirement: IAH-001 — Politica de contrasenas

El sistema SHALL validar toda contrasena nueva o cambiada contra una politica configurable de longitud minima (12 por defecto) y MUST rechazar contrasenas comunes, derivables del username y reutilizadas recientemente. La politica MUST NOT exigir composicion artificial obligatoria y MUST aceptar passphrases largas; MUST NOT imponer rotacion forzada. El rechazo MUST producir el sobre de error estandar `{"error": {"code", "message", "details?"}}`. La politica MUST NOT aplicarse retroactivamente a las credenciales sembradas de desarrollo, que quedan grandfathered y son dev-only.

#### Scenario: Contrasena debil rechazada

- **WHEN** se intenta crear o cambiar a una contrasena por debajo de la longitud minima o presente en la lista de claves comunes
- **THEN** el sistema responde con el sobre de error estandar y no persiste el cambio

#### Scenario: Passphrase valida aceptada

- **WHEN** se ingresa una passphrase que cumple la longitud minima y no es comun ni derivable del username
- **THEN** el sistema acepta la contrasena y la almacena hasheada

#### Scenario: Contrasena derivable del username rechazada

- **WHEN** se intenta registrar una contrasena igual, que contiene o es una variacion trivial del username
- **THEN** el sistema rechaza la contrasena con el sobre de error estandar

#### Scenario: Reutilizacion reciente rechazada

- **WHEN** se intenta cambiar a una contrasena usada dentro de la ventana de historial reciente configurada
- **THEN** el sistema rechaza el cambio y no persiste la contrasena

#### Scenario: Credenciales sembradas grandfathered

- **WHEN** una instalacion de desarrollo conserva credenciales sembradas por debajo de la politica (por ejemplo `admin123`)
- **THEN** la politica no las invalida retroactivamente y el login sigue operativo en desarrollo

### Requirement: IAH-002 — Bloqueo por intentos fallidos

El sistema SHALL contar los intentos de login fallidos por cuenta y MUST bloquear temporalmente la cuenta al alcanzar un umbral configurable (5 por defecto), dentro de una ventana configurable y por una duracion configurable (15 min por defecto). El bloqueo MUST ser por cuenta, no por IP. Mientras la cuenta esta bloqueada, el login MUST fallar con un codigo de error distinguible sin revelar si el usuario existe. Un login exitoso MUST resetear el contador. El bloqueo MUST quedar detras de un flag `account_lockout_enabled` apagado por defecto y MUST ser mockeable (reloj/ventana inyectables) sin depender de tiempos reales en la suite.

#### Scenario: Bloqueo al alcanzar el umbral

- **WHEN** se acumulan intentos fallidos consecutivos iguales al umbral configurado
- **THEN** la cuenta queda bloqueada y los intentos subsiguientes fallan con el codigo de bloqueo

#### Scenario: Cuenta bloqueada rechaza credenciales validas

- **WHEN** una cuenta bloqueada presenta credenciales validas antes de que expire el bloqueo
- **THEN** el sistema rechaza el login con el codigo de bloqueo y no emite token

#### Scenario: Login exitoso resetea el contador

- **WHEN** una cuenta con intentos fallidos previos por debajo del umbral inicia sesion correctamente
- **THEN** el contador de intentos fallidos se reinicia

#### Scenario: El bloqueo expira

- **WHEN** transcurre la duracion de bloqueo configurada y la cuenta vuelve a intentar con credenciales validas
- **THEN** el login es exitoso y el estado de bloqueo se limpia

#### Scenario: Flag apagado preserva el flujo de desarrollo

- **WHEN** el flag `account_lockout_enabled` esta apagado
- **THEN** un login fallido no incrementa bloqueo observable y una credencial valida sigue iniciando sesion

### Requirement: IAH-003 — Expiracion y refresco rotativo de tokens

El sistema SHALL emitir tokens de acceso de vida corta configurable (15 min por defecto) y SHALL ofrecer un token de refresco persistido que rote en cada uso. El token de refresco MUST almacenarse en PostgreSQL unicamente como hash, junto con `user_id`, expiracion, revocacion y el enlace al token rotado (`rotated_from`). Al rotar, el sistema MUST invalidar el token de refresco usado y MUST rechazar la reutilizacion de un token ya rotado. El contrato existente MUST conservarse de forma aditiva: `POST /api/v1/auth/login` MUST seguir devolviendo `access_token` y `token_type`. El token de acceso MUST NOT ser valido una vez transcurrida su expiracion.

#### Scenario: El access token expira

- **WHEN** se usa un token de acceso pasado su tiempo de expiracion
- **THEN** el sistema responde 401 no autenticado

#### Scenario: El login conserva los campos existentes

- **WHEN** un cliente inicia sesion con credenciales validas
- **THEN** la respuesta incluye `access_token` y `token_type` con los mismos nombres y semantica que antes del change

#### Scenario: El refresco rota el par de tokens

- **WHEN** se presenta un token de refresco valido en el endpoint de refresco
- **THEN** el sistema emite un nuevo par de tokens e invalida el token de refresco usado

#### Scenario: Token de refresco reutilizado es rechazado

- **WHEN** se presenta un token de refresco ya rotado
- **THEN** el sistema rechaza el refresco con 401 no autenticado

#### Scenario: El refresh se persiste hasheado

- **WHEN** se inspecciona el almacen de refresh tras emitir un token
- **THEN** el valor almacenado es un hash y no el token en claro

### Requirement: IAH-004 — Revocacion de tokens y coherencia del limite de tasa

El sistema SHALL permitir revocar tokens de forma explicita: el logout MUST revocar el token de refresco del usuario, y la revocacion administrativa MUST poder invalidar de forma inmediata todas las sesiones del usuario mediante `token_version`. Un token de refresco revocado MUST ser rechazado. La revocacion MUST ser persistente. El sistema MUST declarar que un token de acceso ya emitido conserva validez hasta su TTL (ventana residual) tras una revocacion que no incremente `token_version`. El limite de tasa de nginx sobre `/api/v1/auth/login` SHALL quedar POR ENCIMA del umbral de bloqueo por cuenta, de modo que el bloqueo sea observable antes de que nginx responda 429.

#### Scenario: Logout revoca el token de refresco

- **WHEN** un usuario autenticado invoca el logout
- **THEN** su token de refresco deja de ser aceptado y no puede refrescar la sesion

#### Scenario: Token de refresco revocado es rechazado

- **WHEN** se presenta un token de refresco revocado en el endpoint de refresco
- **THEN** el sistema responde 401 no autenticado

#### Scenario: Revocacion administrativa masiva

- **WHEN** la revocacion administrativa incrementa `token_version` de un usuario
- **THEN** todos los tokens de acceso emitidos con la version anterior dejan de ser aceptados en la siguiente peticion autenticada

#### Scenario: Ventana residual declarada

- **WHEN** se revoca unicamente el token de refresco del usuario
- **THEN** el sistema documenta y acepta que el access token ya emitido conserva validez hasta su TTL

#### Scenario: El limite de tasa no enmascara el bloqueo

- **WHEN** un cliente acumula intentos fallidos hasta el umbral de bloqueo
- **THEN** el bloqueo por cuenta es observable antes de que nginx devuelva 429 para ese cliente
