# Delta for identity-access-hardening

## MODIFIED Requirements

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

## ADDED Requirements

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
