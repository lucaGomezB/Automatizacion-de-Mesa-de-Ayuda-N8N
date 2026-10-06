# employee-directory Specification

## Purpose
Define el directorio interno de empleados de la mesa de ayuda: la entidad de contacto, el modelo de roles, el manejo de datos personales (email y telefono) y las reglas de acceso y ciclo de vida, separado de la autenticacion del sistema.

## Requirements

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

### Requirement: DIR-002 — Campos definitivos y minimizacion del empleado

El directorio SHALL almacenar EXACTAMENTE los siguientes campos y NINGUNO mas: `id` (clave primaria), `legajo` (varchar, obligatorio, unico), `nombre` (varchar, obligatorio), `email` (varchar, obligatorio, unico por empleado e indexado), `telefono` (varchar E.164, opcional, indexado y que MAY repetirse entre empleados), `sector_id` (FK al catalogo `sector`, opcional), `rol`, `activo` (booleano, por defecto verdadero), `fecha_baja` (timestamp nullable con zona; instante de desactivacion y base de la retencion de DIR-007; se limpia al reactivar), `user_id` (FK nullable a `users`), `created_at` y `updated_at`. El `legajo` y el `nombre` MUST estar presentes. El `email` MUST estar presente y MUST ser unico entre empleados. El `telefono` MAY estar ausente y MAY repetirse. El sistema SHALL validar el formato E.164 del telefono y la forma basica del email al persistir un empleado. El sistema MUST NOT almacenar campos adicionales de datos personales.

#### Scenario: Empleado con email y telefono

- **WHEN** se registra un empleado con legajo, nombre, email valido y telefono en formato E.164
- **THEN** el empleado queda persistido y puede resolverse por ambos datos

#### Scenario: Empleado sin telefono

- **WHEN** se registra un empleado con email valido y sin telefono
- **THEN** el empleado se persiste y su resolucion por telefono queda sin resultado

#### Scenario: Email duplicado rechazado

- **WHEN** se intenta registrar un email ya asignado a otro empleado
- **THEN** el sistema rechaza el registro por violar la unicidad del email

#### Scenario: Telefono repetido permitido

- **WHEN** dos empleados comparten el mismo numero de telefono (mesa de area o casilla comun)
- **THEN** ambos registros se persisten, habilitando el tratamiento de ambiguedad de RES-004

#### Scenario: Telefono fuera de E.164

- **WHEN** se registra un telefono que no cumple el formato E.164
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Sin campos adicionales

- **WHEN** se inspecciona el esquema de `directorio_empleado`
- **THEN** sus columnas son exactamente las de este requisito (incluida `fecha_baja`), sin datos personales extra

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

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores y sector por rol

El directorio SHALL referenciar el sector del empleado mediante una clave foranea al catalogo `sector` existente, cuyo vocabulario canonico es exactamente los cinco strings vigentes. El directorio MUST NOT introducir un vocabulario paralelo de sectores ni reutilizar un conjunto reducido de tres sectores. El `sector_id` SHALL ser obligatorio cuando el rol sea `usuario_final` o `operador` (cada usuario pertenece a su sector) y SHALL ser nulo cuando el rol sea `administrador_directorio`.

#### Scenario: Sector tomado del catalogo existente

- **WHEN** se asigna sector a un empleado
- **THEN** el valor referenciado pertenece al catalogo `sector` canonico y no a una lista propia del directorio

#### Scenario: Usuario final y operador requieren sector

- **WHEN** se registra un empleado con rol `usuario_final` o `operador` sin sector
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Administrador sin sector

- **WHEN** se registra un empleado con rol `administrador_directorio` sin sector
- **THEN** el empleado se persiste con `sector` nulo y su visibilidad alcanza a todos los sectores

#### Scenario: Sector inexistente rechazado

- **WHEN** se intenta asignar un sector que no existe en el catalogo canonico
- **THEN** el sistema rechaza la asignacion

### Requirement: DIR-005 — Almacenamiento en texto plano (sin cifrado de aplicacion ni indice ciego)

El sistema SHALL almacenar el email y el telefono del empleado en TEXTO PLANO en columnas `varchar`. El directorio MUST NOT aplicar cifrado de aplicacion (`EncryptedText`) sobre estos campos ni MUST construir un indice ciego (HMAC) para su busqueda, y MUST NOT requerir una clave de cifrado o de indice ciego en la configuracion. Razon: auditabilidad directa y consultas SQL operativas sin custodia de claves; el dato es personal pero no sensible bajo Ley 25.326 art. 2. La proteccion se logra con minimizacion (DIR-002), control de acceso y auditoria (DIR-006), y no-PII en logs (DIR-006). El cifrado Fernet del contenido del incidente NO se modifica.

#### Scenario: Contacto disponible en claro

- **WHEN** se inspecciona una fila del directorio en la base de datos
- **THEN** el email y el telefono se leen en claro y las consultas SQL operativas funcionan sin descifrado ni clave

#### Scenario: Sin clave ni indice ciego

- **WHEN** se revisa la configuracion del backend y el esquema del directorio
- **THEN** no existe una clave de indice ciego del directorio ni una columna de hash ciega

#### Scenario: El cifrado del incidente no cambia

- **WHEN** se almacena el contenido de un incidente o el llamante de telefonia
- **THEN** estos siguen cifrados con el mecanismo Fernet existente, ajeno al directorio

### Requirement: DIR-006 — Control de acceso, auditoria y no-PII en logs

El directorio contiene datos personales. La gestion (alta, modificacion, activacion/desactivacion, borrado ARCO) SHALL requerir autenticacion y el rol `administrador_directorio`. La consulta SHALL requerir autenticacion y estar restringida a roles autorizados. El sistema SHALL registrar de forma auditables los accesos y cambios del directorio (quien, cuando, operacion y resultado) y SHALL registrar los accesos en el contexto de la resolucion. La resolucion interna de contactos consumida por otros servicios del backend MUST NOT requerir autenticacion HTTP ni exponer datos de contacto fuera del proceso. El sistema MUST NOT registrar email, telefono ni otros datos personales en claro en logs, respuestas de error ni en la auditoria.

#### Scenario: Gestion sin rol suficiente

- **WHEN** un usuario autenticado con rol distinto de `administrador_directorio` intenta modificar el directorio
- **THEN** el sistema responde con un error de autorizacion y no persiste el cambio

#### Scenario: Acceso anonimo rechazado

- **WHEN** una peticion sin token valido intenta consultar o modificar el directorio
- **THEN** el sistema responde con un error de autenticacion

#### Scenario: Resolucion interna sin borde HTTP

- **WHEN** un servicio del backend resuelve un contacto internamente
- **THEN** la resolucion no atraviesa la API publica ni exige token

#### Scenario: Auditoria de accesos

- **WHEN** se produce un alta, modificacion, consulta o borrado del directorio
- **THEN** queda un registro de auditoria con el actor, la operacion y el resultado

#### Scenario: PII fuera de los logs

- **WHEN** se registra una operacion del directorio o de resolucion
- **THEN** el log y el registro de auditoria no contienen el email ni el telefono en claro

### Requirement: DIR-007 — Ciclo de vida: desactivacion, retencion y borrado ARCO

El sistema SHALL desactivar empleados mediante el indicador `activo` en lugar de borrarlos, conservando la trazabilidad. El sistema SHALL registrar el instante de desactivacion en `fecha_baja` (timestamp con zona) y SHALL limpiarlo cuando el empleado se reactive. La resolucion de contactos MUST ignorar empleados inactivos. El sistema SHALL conservar la fila mientras la relacion laboral este activa mas 1 año; vencido ese plazo SHALL ejecutar el borrado fisico, evaluando el vencimiento como `fecha_baja + 1 año`. El borrado por retencion SHALL ser MANUAL y disparado por un operador: MUST NOT existir automatizacion por cron, scheduler o worker en background, y el borrado fisico MUST NOT ser el camino operativo por defecto. El disparador manual SHALL estar disponible para el rol `administrador_directorio` (accion explicita via API y/o script CLI) y SHALL ser IDEMPOTENTE: conservar los empleados activos y las bajas recientes, y no volver a borrar en una segunda ejecucion. El sistema SHALL registrar de forma auditable los **ids** de las filas eliminadas (ademas del conteo) SIN datos personales; los ids son identificadores internos y no PII. El borrado fisico SHALL tambien ejecutarse ante una solicitud de supresion (ARCO) y SHALL ser ejecutado por un `administrador_directorio`.

#### Scenario: Empleado desactivado no resuelve

- **WHEN** un empleado con `activo = false` coincide con un telefono o email buscado
- **THEN** la resolucion no lo devuelve como contacto valido

#### Scenario: Reactivacion

- **WHEN** un empleado desactivado se reactiva
- **THEN** vuelve a ser elegible para la resolucion sin volver a cargar sus datos y su `fecha_baja` queda limpia

#### Scenario: Borrado por retencion

- **WHEN** una fila de directorio desactivada supera `fecha_baja + 1 año`
- **THEN** el sistema ejecuta su borrado fisico, conserva los activos y las bajas recientes, y registra el conteo sin datos personales

#### Scenario: Purga manual disparada por un operador

- **WHEN** un `administrador_directorio` dispara manualmente la purga (API o script CLI)
- **THEN** el sistema borra fisicamente las filas desactivadas que superan `fecha_baja + 1 año`, sin intervencion automatica ni programada

#### Scenario: Sin automatizacion de la purga

- **WHEN** se inspecciona el sistema en busca de cron, scheduler o worker de purga
- **THEN** no existe ningun mecanismo que dispare el borrado por retencion sin una invocacion humana explicita

#### Scenario: Registro auditable con ids

- **WHEN** el sistema ejecuta una purga que elimina filas
- **THEN** el registro de auditoria incluye la lista de **ids** de las filas eliminadas y el conteo, sin email ni telefono en claro

#### Scenario: Borrado por retencion idempotente

- **WHEN** una fila de directorio desactivada supera `fecha_baja + 1 año` y se ejecuta la purga
- **THEN** el sistema ejecuta su borrado fisico, conserva los activos y las bajas recientes, y una segunda ejecucion no vuelve a borrar nada (ids vacios)

#### Scenario: Borrado por ARCO

- **WHEN** un `administrador_directorio` ejecuta una solicitud ARCO de supresion
- **THEN** la fila correspondiente se elimina fisicamente de la base

### Requirement: DIR-008 — Guardia de entorno acotada al seed

El seed dev-only del directorio SHALL verificar el entorno de ejecucion y MUST rechazar la ejecucion, sin abrir transaccion ni tocar la base, cuando `settings.environment` no pertenezca al conjunto de entornos de desarrollo o prueba (por ejemplo `development`, `local`, `test`). La guardia MUST aplicarse UNICAMENTE al camino de seed: ninguna ruta, servicio, dependencia ni operacion de runtime normal SHALL consultar el entorno para autorizar, denegar o alterar su comportamiento. El seed MUST NOT sembrar datos en un entorno que no sea de desarrollo o prueba.

#### Scenario: Seed rechazado fuera de desarrollo

- **WHEN** se ejecuta el seed con `environment` igual a `production`
- **THEN** el sistema aborta la ejecucion con error, no escribe filas y no modifica la base

#### Scenario: Seed permitido en desarrollo

- **WHEN** se ejecuta el seed con `environment` en el conjunto de desarrollo o prueba
- **THEN** el seed procede de forma idempotente segun DIR-009 de c-54

#### Scenario: El runtime normal no se gatea

- **WHEN** se opera la API del directorio, la resolucion o la visibilidad con `environment` igual a `production`
- **THEN** el comportamiento es normal: la guardia de entorno no interviene en el runtime

### Requirement: DIR-009 — Evidencia de cumplimiento y confirmaciones de revision humana

El sistema SHALL mantener evidencia verificable de las confirmaciones de la revision humana de alto riesgo del directorio: (a) la politica de retencion y ARCO (relacion activa + 1 año; borrado fisico por vencimiento manual o por ARCO, ejecutado por `administrador_directorio`); (b) que el repositorio y la base NO contienen datos personales reales (los datos existentes son sinteticos o estructurales); y (c) que NO existe una clave de indice ciego del directorio ni una columna de hash ciega, conforme a DIR-005. Activar datos personales reales SHALL quedar bloqueado hasta que la revision humana HIGH registre su aprobacion; la implementacion con datos sinteticos NO habilita ese uso.

#### Scenario: Sin PII real en repositorio y base

- **WHEN** se inspeccionan el repositorio y la base de datos del directorio
- **THEN** no hay datos personales reales; los contactos presentes son sinteticos o estructurados para pruebas

#### Scenario: Sin clave de indice ciego

- **WHEN** se revisa la configuracion y el esquema del directorio
- **THEN** no existe clave de indice ciego ni columna de hash ciega del directorio

#### Scenario: Datos reales bloqueados hasta la aprobacion

- **WHEN** se intenta activar datos personales reales en el directorio
- **THEN** el uso queda bloqueado hasta que la revision humana HIGH confirme la politica de retencion/ARCO y la regla de visibilidad
