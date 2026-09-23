## Purpose

Define el directorio interno de empleados de la mesa de ayuda: la entidad de contacto, el modelo de roles, el manejo de datos personales (email y telefono) y las reglas de acceso y ciclo de vida, separado de la autenticacion del sistema.

## ADDED Requirements

### Requirement: DIR-001 — Entidad de directorio separada de la autenticacion

El sistema SHALL mantener los datos de contacto de empleados en una entidad propia (`directorio_empleado`), separada de la tabla de autenticacion `users`. El directorio MUST NOT reutilizar ni extender `users` para almacenar email, telefono, sector o rol. El sistema MAY vincular una fila del directorio con una cuenta de `users` mediante una referencia nullable (`user_id`), de modo que una cuenta pueda existir sin empleado asociado y viceversa.

#### Scenario: Fila de directorio independiente de la cuenta de acceso

- **WHEN** se registra un empleado en el directorio sin cuenta de acceso asociada
- **THEN** el empleado queda persistido con sus datos de contacto y sin `user_id`, sin crear ni modificar una fila en `users`

#### Scenario: Cuenta de autenticacion sin empleado

- **WHEN** existe una cuenta en `users` sin fila de directorio vinculada
- **THEN** la autenticacion sigue funcionando y el directorio no exige un empleado para esa cuenta

#### Scenario: Vinculo opcional entre cuenta y empleado

- **WHEN** un empleado se asocia a una cuenta de acceso existente
- **THEN** la fila del directorio referencia `users.id` de forma nullable, sin fusionar el dominio de autenticacion con el de contacto

### Requirement: DIR-002 — Campos del empleado

El directorio SHALL almacenar, como minimo: nombre completo, email, telefono en formato E.164, sector, rol y un indicador `activo`. El email MUST NOT ser obligatorio si el empleado solo se resuelve por telefono, y el telefono MUST NOT ser obligatorio si el empleado solo se resuelve por email. Al menos uno de email o telefono MUST estar presente. El sistema SHALL validar el formato E.164 del telefono y la forma basica del email al persistir un empleado.

#### Scenario: Empleado con email y telefono

- **WHEN** se registra un empleado con email valido y telefono en formato E.164
- **THEN** el empleado queda persistido y puede resolverse por ambos datos

#### Scenario: Empleado solo con email

- **WHEN** se registra un empleado sin telefono pero con email valido
- **THEN** el empleado se persiste y su resolucion por telefono queda sin resultado

#### Scenario: Registro sin ningun dato de contacto

- **WHEN** se intenta registrar un empleado sin email y sin telefono
- **THEN** el sistema rechaza el registro con un error de validacion accionable

#### Scenario: Telefono fuera de E.164

- **WHEN** se registra un telefono que no cumple el formato E.164
- **THEN** el sistema rechaza el registro con un error de validacion

### Requirement: DIR-003 — Modelo de roles minimo

El sistema SHALL modelar el rol del empleado con un vocabulario minimo de exactamente tres valores: `usuario_final`, `operador` y `administrador_directorio`. El rol SHALL gobernar la autorizacion sobre el directorio y la elegibilidad como destino de enrutamiento, y MUST NOT alterar el resultado de clasificacion del incidente. Un `usuario_final` MUST NOT poder administrar el directorio; un `operador` MAY ser destino de enrutamiento de su sector; un `administrador_directorio` MAY gestionar el directorio.

#### Scenario: Rol valido aceptado

- **WHEN** se registra un empleado con rol `usuario_final`, `operador` o `administrador_directorio`
- **THEN** el sistema acepta el rol

#### Scenario: Rol invalido rechazado

- **WHEN** se intenta registrar un empleado con un rol fuera del vocabulario de tres valores
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: El rol no afecta la clasificacion

- **WHEN** se clasifica un incidente
- **THEN** el sector y la confianza resultantes son independientes del rol del empleado reportante o asignado

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores

El directorio SHALL referenciar el sector del empleado mediante una clave foranea al catalogo `sector` existente, cuyo vocabulario canonico es exactamente los cinco strings vigentes. El directorio MUST NOT introducir un vocabulario paralelo de sectores ni reutilizar un conjunto reducido de tres sectores. Un empleado MAY tener sector nulo cuando su funcion no pertenece a un sector especifico.

#### Scenario: Sector tomado del catalogo existente

- **WHEN** se asigna sector a un empleado
- **THEN** el valor referenciado pertenece al catalogo `sector` canonico y no a una lista propia del directorio

#### Scenario: Sector nulo permitido

- **WHEN** se registra un empleado sin sector asociado
- **THEN** el empleado se persiste con `sector` nulo y sigue siendo resoluble por sus datos de contacto

#### Scenario: Sector inexistente rechazado

- **WHEN** se intenta asignar un sector que no existe en el catalogo canonico
- **THEN** el sistema rechaza la asignacion

### Requirement: DIR-005 — PII cifrada at-rest e indice ciego para busqueda

El sistema SHALL almacenar el email y el telefono del empleado cifrados at-rest, y SHALL permitir su busqueda por igualdad sin descifrado masivo mediante un indice ciego: un valor HMAC-SHA256 calculado sobre la forma normalizada del dato (email en minusculas; telefono E.164) con una clave dedicada. El indice ciego MUST ser determinista para permitir la comparacion por igualdad y MUST NOT almacenar el dato en claro. La clave del indice ciego MUST ser distinta de la clave de cifrado y MUST provenir de la configuracion del backend.

#### Scenario: Busqueda por igualdad sobre dato cifrado

- **WHEN** se busca un empleado por un email o telefono conocido
- **THEN** la busqueda se resuelve comparando el indice ciego del valor normalizado, sin descifrar todas las filas

#### Scenario: El dato en claro no se persiste

- **WHEN** se inspecciona una fila del directorio en la base de datos
- **THEN** el email y el telefono no aparecen en claro; solo el valor cifrado y su indice ciego

#### Scenario: Normalizacion consistente

- **WHEN** dos registros del mismo email difieren solo en mayusculas o espacios
- **THEN** producen el mismo indice ciego y la unicidad del dato se puede hacer cumplir

### Requirement: DIR-006 — Control de acceso al directorio

El directorio es PII. La gestion (alta, modificacion, activacion/desactivacion) SHALL requerir autenticacion y el rol `administrador_directorio`. La consulta SHALL requerir autenticacion y estar restringida a roles autorizados. La resolucion interna de contactos consumida por otros servicios del backend MUST NOT requerir autenticacion HTTP ni exponer datos de contacto fuera del proceso. El sistema MUST NOT registrar email ni telefono en claro en logs, respuestas de error ni auditoria.

#### Scenario: Gestion sin rol suficiente

- **WHEN** un usuario autenticado con rol distinto de `administrador_directorio` intenta modificar el directorio
- **THEN** el sistema responde con un error de autorizacion y no persiste el cambio

#### Scenario: Acceso anonimo rechazado

- **WHEN** una peticion sin token valido intenta consultar o modificar el directorio
- **THEN** el sistema responde con un error de autenticacion

#### Scenario: Resolucion interna sin borde HTTP

- **WHEN** un servicio del backend resuelve un contacto internamente
- **THEN** la resolucion no atraviesa la API publica ni exige token

#### Scenario: PII fuera de los logs

- **WHEN** se registra una operacion del directorio o de resolucion
- **THEN** el log no contiene el email ni el telefono en claro

### Requirement: DIR-007 — Ciclo de vida: desactivacion en lugar de borrado

El sistema SHALL desactivar empleados mediante el indicador `activo` en lugar de borrarlos, conservando la trazabilidad. La resolucion de contactos MUST ignorar empleados inactivos. El borrado fisico SHALL reservarse para el ejercicio de derechos de supresion (ARCO) y MUST NOT ser el camino operativo por defecto.

#### Scenario: Empleado desactivado no resuelve

- **WHEN** un empleado con `activo = false` coincide con un telefono o email buscado
- **THEN** la resolucion no lo devuelve como contacto valido

#### Scenario: Reactivacion

- **WHEN** un empleado desactivado se reactiva
- **THEN** vuelve a ser elegible para la resolucion sin volver a cargar sus datos
