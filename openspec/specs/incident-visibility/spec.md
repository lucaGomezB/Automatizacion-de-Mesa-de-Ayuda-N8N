# incident-visibility Specification

## Purpose
Define la visibilidad de incidentes por rol a nivel de API: que porciones del universo de incidentes puede leer/listar cada usuario autenticado segun el rol de su empleado en el directorio. La interfaz de usuario que refleje esta visibilidad queda fuera de este change (diferida).

## Requirements

### Requirement: VIS-001 — Alcance de visibilidad de incidentes y clasificaciones (PROPIO/GLOBAL)

El sistema SHALL restringir la lectura y el listado de incidentes segun el rol del empleado asociado al usuario autenticado, con exactamente dos alcances mas el vacio:

- Un usuario con rol `administrador_directorio` SHALL ver TODOS los incidentes.
- Un usuario con rol `mesa_de_ayuda` SHALL ver TODOS los incidentes (rol transversal que absorbe al antiguo `operador`).
- Un usuario con rol `usuario_final` SHALL ver UNICAMENTE los incidentes cuyo reportante vinculado sea su propio empleado (alcance PROPIO).
- Una cuenta autenticada sin empleado vinculado SHALL tener alcance vacio.

El sector deja de ser frontera de acceso: el sistema MUST NOT acotar la visibilidad por `sector_id` ni por el sector del empleado. La misma regla SHALL aplicarse a los endpoints de clasificaciones atados a un incidente, reutilizando el servicio de visibilidad sin duplicar la logica:
- `GET /api/v1/clasificaciones/incidente/{incidente_id}` SHALL devolver el historial solo si el incidente esta dentro del alcance.
- `PATCH /api/v1/clasificaciones/{log_id}/validar` SHALL validar el alcance ANTES de cualquier mutacion.

Un incidente fuera del alcance SHALL comportarse como NO ENCONTRADO (HTTP 404), sin revelar su existencia ni su contenido, y el `PATCH` NO SHALL mutar nada. El acceso anonimo permanece 401.

#### Scenario: Administrador ve todos los incidentes

- **WHEN** un usuario con rol `administrador_directorio` lista incidentes
- **THEN** el sistema devuelve incidentes de todos los sectores y reportantes

#### Scenario: Mesa de ayuda ve todos los incidentes

- **WHEN** un usuario con rol `mesa_de_ayuda` lista incidentes
- **THEN** el sistema devuelve incidentes de todos los sectores y reportantes

#### Scenario: Usuario final ve solo los incidentes que reporto

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E lista incidentes
- **THEN** el sistema devuelve unicamente los incidentes cuyo reportante vinculado es E

#### Scenario: Usuario final no ve incidentes de otros

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E solicita un incidente cuyo reportante es otro empleado
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Cuenta sin empleado no ve incidentes

- **WHEN** una cuenta autenticada no tiene empleado vinculado
- **THEN** el alcance de incidentes visibles es vacio

#### Scenario: La cuenta admin sembrada ve todos los incidentes

- **WHEN** la cuenta `admin` sembrada por la migracion lista incidentes (esta vinculada a un empleado `administrador_directorio` sintetico)
- **THEN** el sistema los devuelve todos: su alcance efectivo es GLOBAL, no vacio

#### Scenario: El sector no acota la visibilidad

- **WHEN** un usuario con rol `mesa_de_ayuda` o `administrador_directorio` lista incidentes de cualquier sector
- **THEN** el sistema los devuelve; ningun filtro por sector reduce el alcance del rol

#### Scenario: Alcance aplicado en el acceso puntual

- **WHEN** un usuario solicita un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Administrador lee clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` consulta el historial de clasificaciones de un incidente de cualquier sector
- **THEN** el sistema devuelve el historial completo (HTTP 200)

#### Scenario: Mesa de ayuda lee clasificaciones de un incidente en revision

- **WHEN** un usuario con rol `mesa_de_ayuda` consulta el historial de clasificaciones de un incidente
- **THEN** el sistema devuelve el historial (HTTP 200)

#### Scenario: No administrador lee clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` consulta el historial de clasificaciones de un incidente que reporto
- **THEN** el sistema devuelve el historial (HTTP 200)

#### Scenario: Lectura de clasificaciones fuera de alcance es no encontrada

- **WHEN** un usuario consulta el historial de clasificaciones de un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404), sin revelar su existencia ni su historial

#### Scenario: Administrador valida clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` valida una clasificacion de un incidente de cualquier sector
- **THEN** el sistema registra la validacion (HTTP 200)

#### Scenario: No administrador valida clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` valida una clasificacion de un incidente que reporto
- **THEN** el sistema registra la validacion y propaga el veredicto al incidente (HTTP 200)

#### Scenario: Validacion fuera de alcance es no encontrada y no muta

- **WHEN** un usuario valida una clasificacion cuyo incidente esta fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404) y NO modifica el registro de clasificacion ni el incidente

#### Scenario: Acceso anonimo a clasificaciones es no autorizado

- **WHEN** una solicitud sin autenticacion llega a los endpoints de clasificaciones por incidente o de validacion
- **THEN** el sistema responde HTTP 401

### Requirement: VIS-002 — Cola de revision pendiente acotada por alcance

El sistema SHALL acotar la cola `GET /api/v1/clasificaciones/revision-pendiente` segun el alcance del usuario, reutilizando el mismo servicio de visibilidad sin duplicar la derivacion rol -> alcance. `administrador_directorio` y `mesa_de_ayuda` SHALL ver la cola completa; un usuario con rol `usuario_final` SHALL ver unicamente los pendientes cuyo incidente reporto; una cuenta con alcance vacio SHALL ver una lista vacia. El orden FIFO y la definicion de "pendiente" (`requiere_revision_humana` verdadero y sin validacion) SHALL preservarse. El sector MUST NOT acotar la cola.

#### Scenario: Administrador ve la cola completa

- **WHEN** un usuario con rol `administrador_directorio` consulta `revision-pendiente`
- **THEN** el sistema devuelve los pendientes de todos los sectores

#### Scenario: Mesa de ayuda ve la cola completa

- **WHEN** un usuario con rol `mesa_de_ayuda` consulta `revision-pendiente`
- **THEN** el sistema devuelve los pendientes de todos los sectores, ordenados FIFO

#### Scenario: Usuario final ve solo sus pendientes

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E consulta `revision-pendiente`
- **THEN** el sistema devuelve unicamente los pendientes cuyo incidente reporto E

#### Scenario: Sin empleado no ve pendientes

- **WHEN** una cuenta autenticada sin empleado vinculado consulta `revision-pendiente`
- **THEN** el sistema devuelve una lista vacia

#### Scenario: Acceso anonimo rechazado

- **WHEN** una solicitud sin autenticacion consulta `revision-pendiente`
- **THEN** el sistema responde HTTP 401

### Requirement: VIS-003 — Vinculo de reportante del incidente

El sistema SHALL registrar en cada incidente un unico reportante opcional mediante una clave foranea nullable a `directorio_empleado`. El vinculo SHALL ser la base del alcance PROPIO del rol `usuario_final`: un incidente sin reportante vinculado NO SHALL ser visible para ningun `usuario_final`. El vinculo MUST NOT alterar la clasificacion, el sector ni el alcance de los roles GLOBAL (`mesa_de_ayuda`, `administrador_directorio`), que ven todos los incidentes con o sin reportante. Las filas legacy sin reportante SHALL seguir siendo legibles por los roles GLOBAL.

#### Scenario: Incidente con reportante

- **WHEN** un incidente se crea con un reportante resuelto
- **THEN** el incidente persiste la referencia al empleado reportante, nullable y sin alterar la clasificacion

#### Scenario: Incidente sin reportante

- **WHEN** un incidente se crea sin poder resolver un reportante
- **THEN** el incidente se persiste con el vinculo nulo y el alta no se bloquea

#### Scenario: El reportante no altera la clasificacion

- **WHEN** se clasifica un incidente
- **THEN** el sector y la confianza resultantes son independientes del vinculo de reportante

#### Scenario: Filas legacy sin reportante

- **WHEN** un incidente previo al cambio no tiene reportante vinculado
- **THEN** los roles GLOBAL lo siguen viendo y ningun `usuario_final` lo ve por esta via

### Requirement: VIS-004 — Resolucion del reportante segun el canal de ingreso

El sistema SHALL resolver el reportante del incidente segun el canal de ingreso, orquestado por la capa de servicio sin logica de negocio en la ruta:
- Para el formulario web SHALL resolverlo desde la cuenta autenticada, siguiendo el vinculo `directorio_empleado.user_id`.
- Para correo y telefonia, donde la cuenta autenticada es el operador de N8N y NO el reportante, SHALL resolverlo desde el contacto del remitente (email) o del llamante (telefono) provisto en el alta, reutilizando el servicio de resolucion de contactos existente (sin una resolucion paralela).

La resolucion SHALL distinguir ENCONTRADO / NO ENCONTRADO / AMBIGUO. Un resultado NO ENCONTRADO o AMBIGUO SHALL persistir el vinculo nulo SIN elegir un contacto arbitrario y SIN bloquear ni demorar la respuesta de alta. La trazabilidad SHALL registrar el canal y el resultado sin email ni telefono en claro.

#### Scenario: Reportante web desde la sesion

- **WHEN** el formulario web crea un incidente con una cuenta cuyo empleado esta vinculado
- **THEN** el reportante persistido es el empleado de la cuenta autenticada

#### Scenario: Reportante de correo resuelto por remitente

- **WHEN** el canal de correo crea un incidente y el email del remitente corresponde a un empleado activo
- **THEN** el reportante persistido es ese empleado, no el operador de N8N

#### Scenario: Reportante de telefonia resuelto por llamante

- **WHEN** el canal de telefonia crea un incidente y el telefono del llamante corresponde a un empleado activo
- **THEN** el reportante persistido es ese empleado, no el operador de N8N

#### Scenario: Reportante no encontrado

- **WHEN** el contacto del remitente o llamante no corresponde a ningun empleado activo
- **THEN** el incidente se persiste con reportante nulo y el alta concluye con normalidad

#### Scenario: Reportante ambiguo no se elige arbitrariamente

- **WHEN** el contacto del remitente o llamante corresponde a mas de un empleado activo
- **THEN** el incidente se persiste con reportante nulo, sin elegir un contacto arbitrario

#### Scenario: La resolucion no bloquea el alta

- **WHEN** la resolucion del reportante falla o no encuentra contacto
- **THEN** la respuesta de creacion del incidente se completa con independencia del resultado

#### Scenario: Trazabilidad sin PII

- **WHEN** se resuelve el reportante, con o sin coincidencia
- **THEN** el log registra el canal y el resultado, sin email ni telefono en claro

### Requirement: VIS-005 — Derivacion a revision humana ante reportante no identificado

El sistema SHALL derivar el incidente a revision humana (`requiere_revision_humana = true`) cuando NO pueda identificar al reportante, es decir, cuando no haya contacto de canal (ni email de remitente ni telefono de llamante, segun el canal), cuando el contacto no resuelva a un empleado ACTIVO del directorio (NO ENCONTRADO o AMBIGUO), o cuando la cuenta web autenticada no tenga empleado vinculado. La derivacion SHALL persistir `reportante_empleado_id = NULL` y MUST NOT bloquear ni demorar el alta.

El sistema SHALL combinar esta derivacion por OR con la condicion de revision del clasificador: `requiere_revision_humana = (confianza < 0.70) OR (reportante no identificado)`, de modo que un incidente ya marcado por el clasificador NUNCA deje de requerir revision. La identificacion exitosa del reportante MUST NOT forzar revision humana por si misma. La trazabilidad SHALL registrar el canal y el resultado sin email ni telefono en claro.

#### Scenario: Sin contacto de canal deriva a revision

- **WHEN** el alta de correo o telefonia no transporta contacto del remitente o llamante
- **THEN** el incidente se persiste con `reportante_empleado_id` nulo y `requiere_revision_humana = true`, sin bloquear el alta

#### Scenario: Contacto no resoluble deriva a revision

- **WHEN** el contacto del remitente o llamante no corresponde a ningun empleado activo
- **THEN** el incidente se persiste con reportante nulo y `requiere_revision_humana = true`

#### Scenario: Cuenta web sin empleado deriva a revision

- **WHEN** la cuenta web autenticada que crea el incidente no tiene empleado vinculado
- **THEN** el incidente se persiste con reportante nulo y `requiere_revision_humana = true`

#### Scenario: La derivacion no quita una revision ya marcada

- **WHEN** el clasificador ya marco el incidente para revision (`confianza < 0.70`) aunque el reportante se identifique
- **THEN** el incidente conserva `requiere_revision_humana = true`

#### Scenario: Reportante identificado no fuerza revision

- **WHEN** el reportante se identifica y el clasificador no exige revision
- **THEN** el incidente queda con `requiere_revision_humana = false` y el reportante persistido

#### Scenario: La derivacion no bloquea el alta

- **WHEN** el reportante no se identifica y el incidente se deriva a revision humana
- **THEN** la respuesta de creacion del incidente se completa con normalidad (HTTP 201)
