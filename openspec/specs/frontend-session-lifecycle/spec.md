# frontend-session-lifecycle Specification

## Purpose

Define el ciclo de vida completo de la sesion en el frontend: la rehidratacion de la sesion al arrancar la aplicacion, el aviso proactivo cuando el access token esta por expirar, la extension de la sesion por consentimiento del usuario, el cierre automatico cuando el usuario no responde, y la coherencia del estado de sesion entre multiples pestanas. El refresh token nunca se almacena en ningun medio accesible por JavaScript.

## Requirements

### Requirement: FSL-001 — Rehidratacion de la sesion al arranque

Al arrancar la aplicacion, si existe una cookie de refresco vigente, el frontend SHALL rehidratar la sesion invocando el endpoint de refresco de forma silenciosa, obtener un access token nuevo y quedar autenticado sin volver a pedir credenciales. Si no hay cookie o el refresco falla, el usuario MUST permanecer no autenticado y MUST ser conducido al login. El access token SHALL mantenerse unicamente en memoria; el refresh token MUST NOT guardarse en `localStorage`, `sessionStorage`, cookies accesibles por JS ni ningun otro medio legible por JavaScript. El estado de rehidratacion SHALL exponerse de forma que la interfaz no muestre pantallas protegidas antes de completarse.

#### Scenario: La sesion sobrevive un reload de pagina

- **WHEN** un usuario autenticado recarga la aplicacion y la cookie de refresco sigue vigente
- **THEN** la aplicacion rehidrata la sesion silenciosamente, obtiene un access token nuevo y continua autenticada

#### Scenario: Sin cookie se exige login

- **WHEN** la aplicacion arranca sin una cookie de refresco vigente
- **THEN** el usuario queda no autenticado y es conducido al login

#### Scenario: El refresh no persiste en almacenamiento accesible por JS

- **WHEN** se inspecciona `localStorage`, `sessionStorage` y `document.cookie` tras un login exitoso
- **THEN** ninguno contiene el refresh token

#### Scenario: La interfaz espera a la rehidratacion

- **WHEN** la aplicacion esta rehidratando la sesion al arrancar
- **THEN** no se renderiza una pantalla protegida como si no hubiera sesion hasta resolver el resultado de la rehidratacion

### Requirement: FSL-002 — Aviso proactivo de expiracion del access token

El frontend SHALL derivar el instante de expiracion del access token a partir de la respuesta del backend (`expires_in`) o del claim `exp` del JWT, y SHALL programar un temporizador proactivo que se dispare al o antes de la expiracion. Al dispararse, la interfaz MUST presentar un dialogo que ofrezca explicitamente al usuario continuar la sesion o cerrarla. El dialogo MUST ser accesible (rol de dialogo, foco gestionado, operable por teclado) y MUST NOT cerrar la sesion por si solo mientras el usuario responde.

#### Scenario: El aviso aparece al expirar el access token

- **WHEN** transcurre el tiempo hasta la expiracion del access token
- **THEN** la interfaz muestra un dialogo que ofrece continuar la sesion o cerrarla

#### Scenario: El aviso se programa desde la respuesta del backend

- **WHEN** se emite un access token con `expires_in` (o un JWT con `exp`)
- **THEN** el temporizador se programa usando ese valor sin recargar la pagina

#### Scenario: El dialogo es accesible

- **WHEN** el dialogo de expiracion aparece
- **THEN** es operable por teclado, anuncia su proposito y recibe el foco

### Requirement: FSL-003 — Cierre automatico ante falta de respuesta

Si el usuario no responde al aviso de expiracion dentro de una ventana de gracia configurable (constante del frontend con un valor por defecto de 30 segundos), el frontend SHALL cerrar la sesion de forma automatica: MUST revocar el refresh en el backend, limpiar el estado local y el access token en memoria, y redirigir a `/login`. Tras el cierre automatico, ninguna pantalla protegida SHALL permanecer accesible. La ventana de gracia SHALL ser configurable y no bloquear la interfaz mientras el usuario aun puede responder.

#### Scenario: Sin respuesta la sesion se cierra

- **WHEN** el aviso de expiracion se muestra y el usuario no responde dentro de la ventana de gracia (30 segundos por defecto)
- **THEN** el sistema revoca la sesion, limpia el estado local y redirige a `/login`

#### Scenario: El cierre automatico ocurre a los 30 segundos por defecto

- **WHEN** el aviso de expiracion se muestra con la configuracion por defecto y el usuario no responde
- **THEN** el cierre automatico ocurre 30 segundos despues de mostrarse el aviso

#### Scenario: La sesion cerrada no conserva acceso

- **WHEN** ocurre el cierre automatico
- **THEN** el access token se elimina de memoria y las rutas protegidas dejan de ser accesibles

#### Scenario: La ventana de gracia es configurable

- **WHEN** se configura una ventana de gracia distinta
- **THEN** el cierre automatico ocurre exactamente al vencer esa ventana, siempre que el usuario no haya respondido

### Requirement: FSL-004 — Extension de la sesion por consentimiento

Al elegir continuar en el aviso de expiracion, el frontend SHALL invocar el refresco de la sesion, y ante exito MUST descartar el aviso, fijar el nuevo access token en memoria y reiniciar el temporizador de expiracion. Si el refresco falla (por ejemplo, la cookie ya no es valida), el frontend MUST tratar la sesion como cerrada y redirigir a `/login`. Elegir continuar MUST NOT requerir recargar la pagina ni reingresar credenciales.

#### Scenario: Continuar extiende la sesion

- **WHEN** el usuario elige continuar en el aviso de expiracion y el refresco tiene exito
- **THEN** el aviso se descarta, el access token se renueva y el temporizador se reinicia

#### Scenario: Si el refresco falla la sesion se cierra

- **WHEN** el usuario elige continuar pero el refresco falla
- **THEN** el frontend cierra la sesion y redirige a `/login`

#### Scenario: Continuar no exige re-login

- **WHEN** el usuario elige continuar con una cookie vigente
- **THEN** la sesion se extiende sin pedir credenciales ni recargar la pagina

### Requirement: FSL-005 — Coherencia multi-pestana y precedencia del aviso

El estado de sesion SHALL ser coherente entre las pestanas de la misma aplicacion, utilizando un `BroadcastChannel` para propagar los eventos de sesion: un cierre de sesion (manual o automatico) en una pestana MUST reflejarse en las demas, y una extension de sesion exitosa SHALL mantenerlas autenticadas. El aviso proactivo de expiracion (FSL-002) SHALL ser el mecanismo primario de continuidad de la sesion; el refresco silencioso ante 401 SHALL quedar como respaldo para condiciones de carrera (deriva del temporizador, pestanas en segundo plano) y MUST NOT extender la sesion de forma indefinida sin el consentimiento descrito en FSL-004.

#### Scenario: El cierre de sesion se propaga entre pestanas

- **WHEN** una pestana cierra la sesion (manual o automaticamente)
- **THEN** las demas pestanas dejan de considerarse autenticadas y son conducidas al login

#### Scenario: La extension mantiene autenticadas a las pestanas

- **WHEN** una pestana extiende la sesion exitosamente
- **THEN** las demas pestanas continuan autenticadas

#### Scenario: El aviso es primario y el 401 es respaldo

- **WHEN** el access token expira y el backend responde 401 antes de que el temporizador proactivo actue
- **THEN** el refresco silencioso cubre la condicion de carrera y el aviso proactivo sigue siendo el mecanismo primario de continuidad
