# identity-access-hardening Specification

## Purpose
Endurece el nucleo de autenticacion del sistema (controles ISO/IEC 27002 8.5 y 5.17): valida la fortaleza de las contrasenas, limita los intentos fallidos y acorta, rota y revoca los tokens JWT, preservando de forma aditiva el contrato de login vigente. Es la Fase A de la capacidad `identity-access-hardening`; MFA y rotacion de claves pertenecen a las fases posteriores (c-63b y c-63c).

## Requirements

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

El sistema SHALL emitir tokens de acceso de vida corta configurable (30 min por defecto) y SHALL ofrecer un token de refresco persistido que rote en cada uso. El token de refresco MUST almacenarse en PostgreSQL unicamente como hash, junto con `user_id`, expiracion, revocacion y el enlace al token rotado (`rotated_from`). Al rotar, el sistema MUST invalidar el token de refresco usado y MUST rechazar la reutilizacion de un token ya rotado. El contrato existente MUST conservarse de forma aditiva: `POST /api/v1/auth/login` MUST seguir devolviendo `access_token` y `token_type`. El token de acceso MUST NOT ser valido una vez transcurrida su expiracion. La rotacion SHALL ser deslizante y gobernada por inactividad (IAH-013): cada rotacion exitosa renueva la ventana de vigencia del refresh, que representa la ventana de inactividad de la sesion.
(Previously: el access token tenia un default de 15 min y la ventana de inactividad no estaba declarada en la spec.)

#### Scenario: El access token dura 30 minutos por defecto

- **WHEN** se emite un access token con la configuracion por defecto
- **THEN** su expiracion es de 30 minutos y la respuesta de login expone `expires_in` igual a `30 * 60`

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

El sistema SHALL permitir revocar tokens de forma explicita: el logout MUST revocar el token de refresco del usuario y MUST limpiar la cookie de refresco (IAH-014), y la revocacion administrativa MUST poder invalidar de forma inmediata todas las sesiones del usuario mediante `token_version`. El cierre automatico de la sesion por falta de respuesta al aviso de expiracion MUST revocar el token de refresco y limpiar la cookie, de modo que la sesion quede efectivamente cerrada. Un token de refresco revocado MUST ser rechazado. La revocacion MUST ser persistente. El sistema MUST declarar que un token de acceso ya emitido conserva validez hasta su TTL (ventana residual) tras una revocacion que no incremente `token_version`. El limite de tasa de nginx sobre `/api/v1/auth/login` SHALL quedar POR ENCIMA del umbral de bloqueo por cuenta, de modo que el bloqueo sea observable antes de que nginx responda 429.
(Previously: el logout no limpiaba cookie alguna porque el refresh viajaba en el cuerpo; el cierre automatico por expiracion no estaba contemplado.)

#### Scenario: Logout revoca el token de refresco

- **WHEN** un usuario autenticado invoca el logout
- **THEN** su token de refresco deja de ser aceptado y no puede refrescar la sesion

#### Scenario: Logout limpia la cookie de refresco

- **WHEN** un usuario autenticado invoca el logout habiendo recibido la cookie de refresco
- **THEN** la respuesta expira la cookie de refresco y una rehidratacion posterior no logra refrescar

#### Scenario: El cierre automatico revoca la sesion

- **WHEN** el frontend cierra la sesion por falta de respuesta al aviso de expiracion
- **THEN** el refresh de la sesion queda revocado y la cookie limpiada, y un nuevo intento de refresco es rechazado

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

### Requirement: IAH-008 — Rotacion del secreto JWT con keyring y ventana de solapamiento

El sistema SHALL soportar la rotacion del secreto de firma JWT sin invalidar de forma inmediata todas las sesiones emitidas. La firma de tokens nuevos MUST usar la clave activa e incluir su `kid` de forma aditiva en el header. Durante una ventana de solapamiento configurable el sistema MUST aceptar tokens firmados con la clave anterior y los tokens legacy sin `kid`; al cerrarse la ventana MUST rechazarlos. La verificacion MUST estar acotada a las claves vigentes del keyring y MUST NOT ser ilimitada. El sistema MUST responder 401 no autenticado ante un token cuya verificacion no corresponda a ninguna clave vigente.

#### Scenario: Token firmado con la clave anterior se acepta durante la ventana

- **WHEN** se presenta un token firmado con la clave anterior dentro de la ventana de solapamiento configurada
- **THEN** el sistema acepta el token y autentica al usuario

#### Scenario: Token con la clave anterior se rechaza tras la ventana

- **WHEN** se presenta un token firmado con la clave anterior una vez cerrada la ventana de solapamiento
- **THEN** el sistema responde 401 no autenticado

#### Scenario: Token legacy sin kid se acepta durante la transicion

- **WHEN** se presenta un token sin claim `kid` emitido antes de la rotacion, dentro de la ventana
- **THEN** el sistema lo valida con alguna de las claves vigentes del keyring

#### Scenario: La firma nueva usa la clave activa

- **WHEN** se emite un token de acceso con el keyring configurado
- **THEN** el token queda firmado con la clave activa y lleva su `kid`

#### Scenario: La verificacion esta acotada

- **WHEN** un token no verifica con ninguna de las claves vigentes del keyring
- **THEN** el sistema rechaza el token sin intentar claves fuera del keyring

### Requirement: IAH-009 — Rotacion de la clave Fernet con re-cifrado sin perdida

El sistema SHALL proveer un procedimiento documentado y una herramienta (`scripts/rotate_fernet_key.py`) para rotar la clave Fernet (`pseudonymization_encryption_key`) y re-cifrar los datos at-rest sin perdida de informacion. El procedimiento MUST partir de un inventario exacto de las columnas cifradas con Fernet; la herramienta MUST re-cifrar todas esas columnas dentro de una unica transaccion y MUST exigir un respaldo previo de los datos afectados, abortando si no se aporta. Durante la migracion el sistema MUST poder descifrar datos cifrados con la clave anterior y, al finalizar, los datos MUST quedar legibles con la clave nueva. La clave anterior MUST retirarse del conjunto recien al confirmarse el re-cifrado, de modo que revertir sea reponer la clave previa.

#### Scenario: El inventario de columnas Fernet existe y es exhaustivo

- **WHEN** se prepara la rotacion de la clave Fernet
- **THEN** existe un inventario que enumera todas las columnas cifradas con Fernet y la herramienta usa esa lista de forma explicita

#### Scenario: La rotacion exige respaldo previo

- **WHEN** se invoca la herramienta de rotacion sin respaldo previo declarado
- **THEN** la herramienta aborta con codigo de salida no-cero y no modifica datos

#### Scenario: El dato antiguo se descifra durante la rotacion

- **WHEN** la rotacion se ejecuta con la clave anterior presente en el conjunto de claves
- **THEN** los datos cifrados con la clave anterior se descifran correctamente

#### Scenario: El re-cifrado es transaccional

- **WHEN** ocurre un fallo durante el re-cifrado de las filas
- **THEN** la transaccion se revierte y no queda ningun dato re-cifrado de forma parcial

#### Scenario: El dato re-cifrado es legible con la clave nueva

- **WHEN** finaliza la rotacion y la clave anterior se retira del conjunto
- **THEN** los datos re-cifrados se descifran correctamente con la clave nueva

#### Scenario: La rotacion es reversible

- **WHEN** se necesita revertir una rotacion ya ejecutada
- **THEN** reponer la clave anterior como activa permite descifrar los datos respaldados

### Requirement: IAH-010 — Higiene y gestion de secretos (postura pragmatica)

El repositorio MUST NOT contener secretos ni credenciales reales; la verificacion de higiene (`.githooks/pre-commit` y `scripts/security/scan_engram_secrets.py`) MUST seguir pasando. El proyecto MUST documentar un inventario de secretos (al menos los JWT y la clave Fernet) y un runbook de rotacion. El proyecto MUST documentar la postura actual de gestion de secretos basada en `.env`/variables de entorno y MAY documentar SOPS, Docker secrets o Vault como opciones no adoptadas por ahora. La adopcion de un gestor de secretos/KMS, un PAM y una CA real de produccion MUST quedar documentada como prerequisito de despliegue (futuro/organizacional) y MUST NOT presentarse como implementada en este change.

#### Scenario: No hay secretos en el repositorio

- **WHEN** se ejecuta la verificacion de higiene de secretos sobre los archivos versionados
- **THEN** no se reportan hallazgos sin resolver

#### Scenario: Inventario de secretos y runbook de rotacion existen

- **WHEN** se revisa la documentacion de seguridad
- **THEN** existe un inventario de secretos y un runbook de rotacion que referencian el secreto JWT y la clave Fernet

#### Scenario: KMS, PAM y CA real se encuadran como futuros

- **WHEN** se lee la postura de gestion de claves
- **THEN** el gestor de secretos/KMS, el PAM y la CA real aparecen como prerequisito de despliegue, no como control implementado

#### Scenario: La postura de secretos y las opciones no adoptadas se documentan

- **WHEN** se lee la documentacion de gestion de secretos
- **THEN** se declara `.env`/variables como fuente actual y se listan SOPS, Docker secrets y Vault como opciones no adoptadas

### Requirement: IAH-011 — Ciclo de vida de identidades y revision de accesos (organizacional)

El proyecto SHALL documentar, como responsabilidad de la organizacion adoptante (controles 5.16 y 5.18), el ciclo de vida de las identidades (alta, cambio y baja) y el proceso de aprobacion y revision periodica de derechos de acceso. La documentacion MUST residir en `docs/seguridad/`, MUST estar referenciada desde el indice `docs/seguridad/README.md` y MUST encuadrarse explicitamente como control organizacional (O), no como codigo del repositorio.

#### Scenario: El ciclo de vida de identidades queda documentado

- **WHEN** se revisa la documentacion de seguridad
- **THEN** describe el ciclo de vida de alta, cambio y baja de identidades como responsabilidad de la organizacion adoptante

#### Scenario: La revision de accesos queda documentada

- **WHEN** se revisa la documentacion de seguridad
- **THEN** describe el proceso y la periodicidad de aprobacion/revision de derechos de acceso y lo marca como control organizacional (O)

#### Scenario: La documentacion organizacional esta referenciada desde el indice

- **WHEN** se inspecciona el indice `docs/seguridad/README.md`
- **THEN** referencia los documentos de ciclo de vida de identidades y de revision de accesos, y las referencias cruzadas resuelven a archivos existentes

### Requirement: IAH-012 — Endpoint aditivo de identidad y alcance actual

El sistema SHALL exponer un endpoint autenticado y de SOLO LECTURA que devuelva la identidad efectiva de la sesion y su alcance de incidentes derivado. El endpoint SHALL recomputar el alcance por request a partir del directorio (empleado vinculado a la cuenta), reutilizando la derivacion rol -> alcance existente (VIS-001 y `role-policy`) sin duplicarla. La respuesta SHALL incluir al menos el nombre de usuario, el rol del empleado (o nulo si no hay empleado activo vinculado) y el modo de alcance con EXACTAMENTE los valores `PROPIO`, `GLOBAL` o `VACIO`. El endpoint MUST NOT exponer sector, `ver_todos` ni conceptos del modelo RBAC anterior (los modos SECTOR y REVISION NO existen). El endpoint SHALL ser ADITIVO: no modifica el contrato ni el comportamiento de los endpoints de login, refresh y logout existentes. Una solicitud sin autenticacion SHALL responder HTTP 401 con el envelope de error estandar, sin revelar datos de identidad.

#### Scenario: Usuario autenticado obtiene su identidad y alcance

- **WHEN** un usuario autenticado con empleado activo vinculado consulta el endpoint
- **THEN** el sistema devuelve su rol y el modo de alcance derivado (`PROPIO`, `GLOBAL` o `VACIO`)

#### Scenario: Cuenta sin empleado activo obtiene alcance vacio

- **WHEN** un usuario autenticado sin empleado activo vinculado consulta el endpoint
- **THEN** el sistema devuelve rol nulo y modo de alcance `VACIO`

#### Scenario: El alcance se recomputa desde el directorio

- **WHEN** el rol del empleado vinculado cambia en el directorio
- **THEN** la siguiente consulta del endpoint devuelve el modo de alcance actualizado, sin requerir re-login

#### Scenario: La respuesta no expone el modelo RBAC anterior

- **WHEN** se inspecciona la respuesta del endpoint
- **THEN** el alcance contiene unicamente el modo (`PROPIO`, `GLOBAL` o `VACIO`) y no incluye sector, `ver_todos` ni `revision`

#### Scenario: Acceso anonimo es no autorizado

- **WHEN** una solicitud sin autenticacion llega al endpoint
- **THEN** el sistema responde HTTP 401 con el envelope de error estandar y sin datos de identidad

#### Scenario: El contrato de login permanece aditivo y sin cambios

- **WHEN** un cliente existente consume login, refresh o logout
- **THEN** el contrato y el comportamiento de esos endpoints no cambian respecto de lo previo

### Requirement: IAH-013 — Cierre de sesion por inactividad

El sistema SHALL revocar una sesion tras una semana (10080 min por defecto, expresada en `jwt_refresh_expire_minutes`) sin acceso. La vigencia del refresh SHALL ser deslizante: cada rotacion exitosa emite un nuevo refresh con una ventana renovada, de modo que la sesion permanece viva mientras haya acceso y expira tras siete dias consecutivos sin rotar. Un refresh presentado con su ventana vencida MUST ser rechazado y revocado, y la sesion MUST quedar cerrada, exigiendo un nuevo login. NO se define un tope absoluto de vida de la sesion: la unica regla de cierre temporal es la inactividad de siete dias, por lo que una sesion con actividad continua puede durar indefinidamente. La politica MUST evaluarse por sesion (cadena de rotacion iniciada en el ultimo login), no por cuenta, de modo que la inactividad de una sesion no afecta a otras sesiones del mismo usuario. La evaluacion de la inactividad MUST usar un instante inyectable, sin depender de tiempos reales en la suite.

#### Scenario: Una sesion inactiva de siete dias se revoca

- **WHEN** transcurren siete dias sin ninguna rotacion de la cadena de refresh de una sesion
- **THEN** el siguiente intento de refresco es rechazado y la sesion queda cerrada

#### Scenario: La actividad renueva la ventana de inactividad

- **WHEN** una sesion rota su refresh dentro de la ventana de siete dias
- **THEN** la nueva ventana se reinicia y la sesion continua viva

#### Scenario: La inactividad es por sesion y no por cuenta

- **WHEN** un usuario con varias sesiones deja inactiva una de ellas durante siete dias mientras mantiene actividad en otra
- **THEN** solo la sesion inactiva se revoca y las demas continuan operativas

#### Scenario: La ventana de inactividad es configurable

- **WHEN** se configura una ventana de inactividad distinta de 10080 min
- **THEN** la revocacion ocurre exactamente al vencer esa ventana

#### Scenario: No hay tope absoluto de vida de la sesion

- **WHEN** una sesion mantiene actividad (rota su refresh) de forma continua
- **THEN** la sesion continua viva sin un limite absoluto de vida total, y solo se revoca si deja de rotar durante siete dias

### Requirement: IAH-014 — Transporte del refresh en cookie HttpOnly y rehidratacion de sesion

El backend SHALL entregar el token de refresco en una cookie `HttpOnly` + `Secure` + `SameSite` seteada por el servidor, y MUST NOT exponer el refresh token en el cuerpo de la respuesta del flujo de navegador (`login` en un paso y `mfa/verify`). El token de acceso SHALL seguir transportandose en el cuerpo y mantenerse en memoria del frontend (`Authorization: Bearer`). `POST /api/v1/auth/login`, `POST /api/v1/auth/mfa/verify` y `POST /api/v1/auth/refresh` MUST setear (o renovar) la cookie; `POST /api/v1/auth/refresh` MUST leer el refresh desde la cookie; `POST /api/v1/auth/logout` MUST limpiar la cookie. El arranque de la aplicacion SHALL rehidratar la sesion invocando `/refresh` de forma silenciosa; si la cookie no existe o es invalida, el usuario NO SHALL quedar autenticado. Los endpoints que mutan la sesion a partir de la cookie (`/refresh`, `/logout`) MUST mitigar CSRF mediante `SameSite=Strict` en la cookie y la verificacion del header `Origin` contra la lista permitida, y MUST rechazar solicitudes de origen cruzado no confiable. NO SHALL usarse un esquema de doble-submit token. El atributo `Secure` MUST usarse salvo en un modo de desarrollo local explicito sobre HTTP (dev-only). La validacion del access token (`get_current_user`) y la revocacion por `token_version` MUST permanecer sin cambios.

#### Scenario: El login setea la cookie de refresco

- **WHEN** un usuario inicia sesion con credenciales validas
- **THEN** la respuesta setea la cookie de refresco con `HttpOnly`+`Secure`+`SameSite` y el cuerpo incluye `access_token` sin el refresh token

#### Scenario: El refresco lee la cookie y la renueva

- **WHEN** se invoca `/refresh` con la cookie de refresco vigente
- **THEN** el sistema rota el token, setea la cookie actualizada y devuelve un nuevo access token en el cuerpo

#### Scenario: El arranque rehidrata la sesion

- **WHEN** la aplicacion arranca con una cookie de refresco vigente
- **THEN** el frontend obtiene un access token via `/refresh` y queda autenticado sin pedir credenciales

#### Scenario: Sin cookie no hay sesion

- **WHEN** la aplicacion arranca sin cookie de refresco (o con una invalida)
- **THEN** el usuario permanece no autenticado y se le exige el login

#### Scenario: El refresh no es accesible por JavaScript

- **WHEN** el frontend inspecciona `document.cookie` y el almacenamiento del navegador
- **THEN** el refresh token no es legible ni persistido en ningun medio accesible por JS

#### Scenario: Solicitud de origen cruzado es rechazada

- **WHEN** un origen no confiable invoca `/refresh` o `/logout` aprovechando la cookie
- **THEN** el sistema rechaza la solicitud por la proteccion CSRF declarada (`SameSite=Strict` + verificacion de `Origin`)

#### Scenario: La validacion del access token no cambia

- **WHEN** una ruta protegida recibe el access token en `Authorization: Bearer`
- **THEN** `get_current_user` lo valida y aplica la revocacion por `token_version` como antes del change
