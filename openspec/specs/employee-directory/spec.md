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

El directorio SHALL almacenar EXACTAMENTE los campos de contacto ya definidos (`id`, `legajo`, `nombre`, `email`, `telefono`, `sector_id`, `rol`, `activo`, `fecha_baja`, `user_id`, `created_at`, `updated_at`) y NINGUN campo de datos personales adicional. El endurecimiento MAY agregar, ademas, columnas DERIVADAS de busqueda no reversibles (`email_bidx`, `telefono_bidx`) construidas como indice ciego; esas columnas NO son datos personales en claro y MUST NOT permitir reconstruir el valor original sin la clave de indice ciego. El `legajo` y el `nombre` MUST estar presentes. El `email` MUST estar presente y SHALL ser unico entre empleados. El `telefono` MAY estar ausente y MAY repetirse. El sistema SHALL validar el formato E.164 del telefono y la forma basica del email al persistir un empleado. El sistema MUST NOT almacenar campos adicionales de datos personales.

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
- **THEN** sus columnas de datos personales son exactamente las de este requisito (incluida `fecha_baja`), mas las columnas derivadas de indice ciego (`email_bidx`, `telefono_bidx`), que no son PII en claro

#### Scenario: Columna derivada no reversible

- **WHEN** se inspecciona el valor de `email_bidx` o `telefono_bidx` de una fila
- **THEN** el valor es un digest determinista que no revela el email ni el telefono sin la clave de indice ciego

### Requirement: DIR-003 — Modelo de roles canonico de tres valores

El sistema SHALL modelar el rol del empleado con un vocabulario minimo de EXACTAMENTE CUATRO valores: `usuario_final`, `mesa_de_ayuda`, `administrador_directorio` y `gestion_incidentes`. El rol `operador` NO SHALL existir. El rol SHALL gobernar la autorizacion sobre el directorio, el alcance de visibilidad de incidentes, las acciones de ciclo de cierre y la elegibilidad como destino de enrutamiento de notificaciones, y MUST NOT alterar el resultado de clasificacion del incidente.

- `usuario_final` es el reportante: alcance PROPIO (solo los incidentes que reporto), NO privilegiado y MUST NOT gestionar el directorio.
- `mesa_de_ayuda` es el rol transversal de mesa de ayuda: alcance GLOBAL (ve todos los incidentes), privilegiado, elegible como destinatario de la notificacion de revision y MUST NOT gestionar el directorio. Absorbe al antiguo `operador`.
- `administrador_directorio` tiene alcance GLOBAL, es privilegiado y MAY gestionar el directorio.
- `gestion_incidentes` es el rol operativo por sector: alcance `SECTOR` (solo los incidentes de su sector no cerrados para su sector), NO privilegiado, MUST NOT gestionar ni leer el directorio, cierra y edita el estado de los incidentes de su sector y es destinatario del aviso post-revision de los sectores del incidente.

El conocimiento de rol SHALL provenir de un unico registro de politica de rol, sin duplicarse entre el enum, el CHECK de la base y los servicios.

#### Scenario: Rol valido aceptado

- **WHEN** se registra un empleado con rol `usuario_final`, `mesa_de_ayuda`, `administrador_directorio` o `gestion_incidentes`
- **THEN** el sistema acepta el rol

#### Scenario: Rol invalido rechazado

- **WHEN** se intenta registrar un empleado con un rol fuera del vocabulario de cuatro valores
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Rol operador ya no existe

- **WHEN** se intenta registrar un empleado con rol `operador`
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Filas legacy con rol operador migradas

- **WHEN** se aplica la migracion sobre datos existentes con filas de rol `operador`
- **THEN** esas filas quedan con rol `mesa_de_ayuda` (backfill ANTES de crearse el CHECK de cuatro valores), de forma append-only

#### Scenario: El downgrade no re-marca filas

- **WHEN** se revierte la migracion que introdujo `gestion_incidentes`
- **THEN** las filas con rol `gestion_incidentes` se reasignan a `usuario_final` ANTES de restaurar el CHECK de tres valores, y las filas `operador` migradas NO se re-marcan

#### Scenario: El rol no afecta la clasificacion

- **WHEN** se clasifica un incidente
- **THEN** el sector y la confianza resultantes son independientes del rol del empleado reportante o vinculado

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores y sector opcional

El directorio SHALL referenciar el sector del empleado mediante una clave foranea nullable al catalogo `sector` existente, cuyo vocabulario canonico es exactamente los cinco strings vigentes. El directorio MUST NOT introducir un vocabulario paralelo de sectores ni reutilizar un conjunto reducido de tres sectores.

El `sector_id` SHALL ser OPCIONAL para `usuario_final`, `mesa_de_ayuda` y `administrador_directorio`. El rol `gestion_incidentes` SHALL requerir un sector: un empleado `gestion_incidentes` sin sector NO SHALL ver ningun incidente (alcance VACIO) y el sistema SHALL exigir el sector al operar la autorizacion por sector de ese rol. Para el resto de los roles el sector MUST NOT condicionar la autorizacion, la visibilidad ni la elegibilidad como destinatario de la notificacion de revision. El sistema MUST NOT aplicar una regla de coherencia entre rol y sector para roles distintos de `gestion_incidentes`.

#### Scenario: Sector tomado del catalogo existente

- **WHEN** se asigna sector a un empleado
- **THEN** el valor referenciado pertenece al catalogo `sector` canonico y no a una lista propia del directorio

#### Scenario: Sector opcional para cualquier rol

- **WHEN** se registra un empleado `usuario_final`, `mesa_de_ayuda` o `administrador_directorio`, con o sin sector
- **THEN** el sistema lo persiste; ninguno de esos roles exige un sector

#### Scenario: Gestion sin sector no ve incidentes

- **WHEN** un empleado `gestion_incidentes` no tiene sector asignado
- **THEN** su alcance de incidentes es VACIO y no ve ningun incidente

#### Scenario: El sector no cambia la autorizacion

- **WHEN** dos empleados con el mismo rol distinto de `gestion_incidentes` y distinto sector (o sin sector) operan el sistema
- **THEN** su alcance de incidentes y su autorizacion sobre el directorio son identicos

#### Scenario: Sector inexistente rechazado

- **WHEN** se intenta asignar un sector que no existe en el catalogo canonico
- **THEN** el sistema rechaza la asignacion

### Requirement: DIR-006 — Control de acceso, auditoria y no-PII en logs

El directorio contiene datos personales. La gestion (alta, modificacion, activacion/desactivacion, borrado ARCO) SHALL requerir autenticacion y el rol `administrador_directorio`. La consulta SHALL requerir autenticacion y SHALL regirse por una politica de acceso por sujeto registrada de forma unica: `administrador_directorio` y `mesa_de_ayuda` MAY leer el directorio; `usuario_final` MAY leer UNICAMENTE su propia fila; `gestion_incidentes` MUST NOT leer el directorio. Los endpoints de lectura del directorio SHALL aplicar limitacion de tasa y anti-enumeracion. El sistema SHALL registrar de forma auditable los accesos y cambios del directorio (quien, cuando, operacion y resultado), en la traza durable de DIR-013 ademas del registro estructurado, y SHALL registrar los accesos en el contexto de la resolucion. La resolucion interna de contactos consumida por otros servicios del backend MUST NOT requerir autenticacion HTTP ni exponer datos de contacto fuera del proceso. El sistema MUST NOT registrar email, telefono ni otros datos personales en claro en logs, respuestas de error ni en la auditoria.

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
- **THEN** queda un registro de auditoria con el actor, la operacion y el resultado, persistido en la traza durable de DIR-013 ademas del registro estructurado

#### Scenario: PII fuera de los logs

- **WHEN** se registra una operacion del directorio o de resolucion
- **THEN** el log y el registro de auditoria no contienen el email ni el telefono en claro

#### Scenario: Lectura por sujeto de usuario_final

- **WHEN** un `usuario_final` autenticado intenta leer el directorio
- **THEN** solo puede leer su propia fila y ninguna otra; el intento de leer otra fila se trata como no autorizado o no encontrado sin revelar la fila

#### Scenario: gestion_incidentes no lee el directorio

- **WHEN** un `gestion_incidentes` intenta leer el directorio
- **THEN** el sistema deniega el acceso

#### Scenario: Anti-enumeracion en la lectura

- **WHEN** se realizan peticiones repetidas o masivas de lectura del directorio
- **THEN** la limitacion de tasa acota la frecuencia y las respuestas no revelan la existencia de filas fuera de alcance

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

El sistema SHALL mantener evidencia verificable de las confirmaciones de la revision humana de alto riesgo del directorio: (a) la politica de retencion y ARCO (relacion activa + 1 año; borrado fisico por vencimiento manual o por ARCO, ejecutado por `administrador_directorio`); (b) que el repositorio y la base NO contienen datos personales reales (los datos existentes son sinteticos o estructurales); y (c) que el mecanismo de activacion de datos reales es deliberado y auditado (DIR-014). Activar datos personales reales SHALL quedar bloqueado hasta que la revision humana HIGH registre su aprobacion de forma verificable en `docs/directorio-evidencia-cumplimiento.md` seccion 4 y en `CHANGES.md`; la implementacion con datos sinteticos NO habilita ese uso. La evidencia SHALL declarar el estado real de la aprobacion (PENDIENTE o CONCEDIDA) y MUST NOT registrar como concedida una aprobacion que no exista de forma verificable.

#### Scenario: Sin PII real en repositorio y base

- **WHEN** se inspeccionan el repositorio y la base de datos del directorio
- **THEN** no hay datos personales reales; los contactos presentes son sinteticos o estructurados para pruebas

#### Scenario: Sin clave de indice ciego

- **WHEN** se revisa la configuracion y el esquema del directorio
- **THEN** la garantia original de ausencia de clave de indice ciego queda SUPERADA: el directorio usa una clave de indice ciego dedicada y columnas de indice ciego (DIR-011); el escenario se conserva como ancla historica de la decision revertida

#### Scenario: Datos reales bloqueados hasta la aprobacion

- **WHEN** se intenta activar datos personales reales en el directorio sin la aprobacion humana HIGH registrada
- **THEN** la activacion queda bloqueada y el sistema permanece operando con datos sinteticos

#### Scenario: Activacion deliberada y auditada

- **WHEN** se inspecciona el mecanismo que habilita el uso de datos reales
- **THEN** existe un procedimiento explicito y auditable (migracion gobernada por entorno mas artefacto de aprobacion) y no un interruptor de runtime oculto

#### Scenario: La aprobacion concedida se registra de forma verificable

- **WHEN** la revision humana HIGH concede la aprobacion
- **THEN** queda registrada de forma verificable en el aviso de cumplimiento (seccion 4) y en `CHANGES.md`, con la fecha

### Requirement: Fidelidad del estado en los registros de gobernanza

Un registro de gobernanza del proyecto (al menos `docs/directorio-evidencia-cumplimiento.md` y las secciones de estado de los changes archivados) SHALL declarar el estado real de cada control y su conteo de tareas de forma verificable. Una aprobacion humana PENDIENTE del autor MUST quedar registrada como PENDIENTE y MUST NOT registrarse como concedida hasta que exista de forma verificable. Cuando el contenido de una tarea cerrada sea precisamente registrar que otra aprobacion queda pendiente, la tarea MAY figurar completada y la aprobacion pendiente SHALL permanecer visible como tal, sin que el cierre de la tarea se confunda con la aprobacion concedida.

#### Scenario: La aprobacion pendiente no se confunde con la tarea cerrada

- **WHEN** se revisa el registro de un control cuya aprobacion humana esta pendiente
- **THEN** el estado declara la aprobacion como PENDIENTE, esperando al autor
- **AND** no se presenta como concedida

#### Scenario: El conteo de tareas refleja el contenido de las tareas

- **WHEN** se revisa el registro de un change cuyo conteo se declara cerrado
- **THEN** una tarea marcada completada cuyo contenido era registrar una aprobacion pendiente no se lee como aprobacion otorgada
- **AND** el estado real de la aprobacion se declara a continuacion

#### Scenario: Dato de estado stale corregido sin reescribir la historia

- **WHEN** una afirmacion de estado actual quedo obsoleta por un cierre posterior
- **THEN** se corrige al estado real
- **AND** las entradas fechadas que documentan el hecho previo se conservan

### Requirement: DIR-011 — Cifrado at-rest del contacto con indice ciego determinista

El sistema SHALL almacenar el email y el telefono del empleado CIFRADOS at-rest mediante el TypeDecorator `EncryptedText` (Fernet) y SHALL construir un indice ciego determinista (`email_bidx`, `telefono_bidx`) derivado con HMAC-SHA-256 y una clave dedicada de indice ciego, para permitir la busqueda por igualdad sobre columnas cifradas. El directorio SHALL requerir una clave de cifrado dedicada y una clave de indice ciego en la configuracion. La unicidad del email SHALL preservarse sobre el indice determinista. El cifrado Fernet del contenido del incidente NO se modifica.

#### Scenario: Contacto cifrado en reposo

- **WHEN** se inspecciona una fila del directorio directamente en la base de datos
- **THEN** el email y el telefono se leen como ciphertext Fernet, no en claro

#### Scenario: Busqueda determinista sobre el indice ciego

- **WHEN** se resuelve un contacto por email o telefono
- **THEN** la busqueda usa el indice ciego determinista y devuelve el mismo empleado para el mismo valor de entrada y la misma clave de indice ciego

#### Scenario: Unicidad del email preservada sobre el indice determinista

- **WHEN** se intenta registrar dos empleados con el mismo email
- **THEN** el sistema rechaza el segundo registro por violar la unicidad sobre el indice determinista

#### Scenario: Indice ciego dependiente de la clave

- **WHEN** se deriva `email_bidx` con dos claves de indice ciego distintas
- **THEN** los digests resultantes para el mismo email son distintos

#### Scenario: El cifrado del incidente no cambia

- **WHEN** se almacena el contenido de un incidente o el llamante de telefonia
- **THEN** estos siguen cifrados con el mecanismo Fernet existente, ajeno al directorio

### Requirement: DIR-012 — Gestion y rotacion de las claves dedicadas del directorio

El directorio SHALL usar claves DEDICADAS de un solo proposito: una clave de cifrado del directorio y una clave de indice ciego (`directory_blind_index_key`), independientes de la clave de pseudonimizacion. El sistema SHALL permitir rotar la clave de cifrado del directorio re-cifrando sus columnas en una transaccion, con respaldo previo obligatorio, mediante la herramienta `App/Backend/scripts/rotate_fernet_key.py` extendida al inventario del directorio. La gestion y rotacion de ambas claves SHALL documentarse en `docs/seguridad/gestion-secretos-y-rotacion.md`.

#### Scenario: Clave dedicada independiente de la de pseudonimizacion

- **WHEN** se inspecciona la configuracion del backend
- **THEN** el directorio usa una clave de cifrado dedicada y una clave de indice ciego dedicadas, distintas de la clave de pseudonimizacion

#### Scenario: Inventario de rotacion cubre el directorio

- **WHEN** se revisa el inventario de columnas cifradas de `rotate_fernet_key.py`
- **THEN** incluye las columnas cifradas del directorio y un test verifica que el inventario coincide con las columnas `EncryptedText` del modelo

#### Scenario: Rotacion con respaldo previo

- **WHEN** se ejecuta la rotacion de la clave del directorio sin un respaldo previo usable
- **THEN** el procedimiento aborta sin re-cifrar datos

#### Scenario: Rotacion documentada

- **WHEN** se lee `docs/seguridad/gestion-secretos-y-rotacion.md`
- **THEN** documenta la generacion, custodia y rotacion de las claves dedicadas del directorio

### Requirement: DIR-013 — Auditoria durable del directorio sin PII

El sistema SHALL mantener una traza DURABLE y append-only de las operaciones del directorio (alta, edicion, activacion/desactivacion, consulta de gestion, resolucion de contacto y borrado), analoga a `incidente_evento`, ademas del registro estructurado. La tabla de auditoria del directorio SHALL almacenar solo identificadores internos, la operacion, el resultado, el instante y el actor; MUST NOT almacenar email, telefono, nombre ni otro dato personal en claro. La auditoria SHALL cubrir los canales de resolucion de contacto. La traza durable SHALL conservarse segun la ventana de retencion de logs alineada con el ciclo de vida del directorio.

#### Scenario: Traza durable de las operaciones

- **WHEN** se produce un alta, edicion, consulta o borrado del directorio
- **THEN** queda una fila en el almacen de auditoria durable con actor, operacion, resultado e instante

#### Scenario: Auditoria durable de la resolucion de contacto

- **WHEN** un servicio resuelve un contacto por email o telefono
- **THEN** queda una traza durable del evento de resolucion, sin el valor de contacto en claro

#### Scenario: La tabla de auditoria no contiene PII

- **WHEN** se inspecciona el contenido de la tabla de auditoria durable
- **THEN** no contiene email, telefono ni nombre en claro; solo identificadores internos y metadatos

#### Scenario: Append-only

- **WHEN** se revisa la tabla de auditoria durable
- **THEN** no existe camino que edite o elimine sus filas

### Requirement: DIR-014 — Activacion deliberada y auditada de datos reales

El sistema SHALL exponer un mecanismo de activacion deliberado y auditable que habilite el uso de datos personales reales en el directorio, gobernado por (a) una migracion/env gateado por el entorno y (b) un artefacto de aprobacion humana HIGH registrado de forma verificable. NO SHALL existir un interruptor de runtime oculto que active datos reales sin aprobacion. Mientras la aprobacion no exista, la activacion SHALL quedar bloqueada y el directorio SHALL operar solo con datos sinteticos. El cambio de estado SHALL quedar auditado.

#### Scenario: Sin aprobacion no hay activacion

- **WHEN** se intenta habilitar datos reales sin el artefacto de aprobacion humana HIGH
- **THEN** la activacion se rechaza y el sistema permanece en modo sintetico

#### Scenario: Activacion con aprobacion auditada

- **WHEN** existe la aprobacion humana HIGH registrada y se ejecuta el mecanismo de activacion
- **THEN** el sistema habilita el uso de datos reales en el entorno gobernado y deja constancia auditable del cambio de estado

#### Scenario: Sin interruptor oculto

- **WHEN** se inspecciona el runtime del directorio en busca de un flag que active datos reales sin aprobacion
- **THEN** no existe ningun interruptor oculto; la unica via es el mecanismo deliberado y auditado

### Requirement: DIR-015 — Retencion operativa, alerta de acumulacion y ARCO de acceso y rectificacion

El sistema SHALL proveer un runbook operativo y una alerta para las filas desactivadas que superan `fecha_baja + 1 año` y que aun no fueron purgadas, SIN introducir cron, scheduler ni worker en el codigo: la purga sigue siendo MANUAL, disparada por un `administrador_directorio`. La alerta SHALL informar la acumulacion de filas vencidas sin exponer datos personales. El sistema SHALL cubrir, ademas del borrado ARCO de supresion, el ACCESO y la RECTIFICACION de los datos del titular, con procedimiento documentado y constancia auditable. La ventana de retencion de los registros de auditoria del directorio SHALL alinearse con el ciclo de vida del directorio y documentarse.

#### Scenario: Alerta de acumulacion de vencidos

- **WHEN** existen filas desactivadas que superan `fecha_baja + 1 año` y no fueron purgadas
- **THEN** el sistema emite una alerta operativa con el conteo, sin datos personales, para que un `administrador_directorio` dispare la purga manual

#### Scenario: Sin automatizacion de la purga

- **WHEN** se inspecciona el sistema en busca de cron, scheduler o worker de purga
- **THEN** no existe ningun mecanismo que dispare el borrado por retencion sin una invocacion humana explicita

#### Scenario: ARCO de acceso

- **WHEN** un titular ejerce el derecho de acceso sobre datos del directorio
- **THEN** el procedimiento documentado permite poner a disposicion sus datos y deja constancia auditable del tramite y su plazo

#### Scenario: ARCO de rectificacion

- **WHEN** un titular ejerce el derecho de rectificacion sobre datos del directorio
- **THEN** el procedimiento documentado permite corregir los datos y deja constancia auditable, sin limitar el flujo ARCO a la supresion

#### Scenario: Retencion de auditoria alineada

- **WHEN** se revisa la politica de retencion de los registros de auditoria del directorio
- **THEN** la ventana esta alineada con el ciclo de vida del directorio y queda documentada

### Requirement: DIR-016 — ADR de reversion y justificacion documental del cifrado

El directorio SHALL mantener el email y el telefono CIFRADOS at-rest conforme a DIR-011 y SHALL documentar, bajo `docs/seguridad/`, un ADR nuevo que registre la reversion de la decision de texto plano, su motivacion (habilitar datos reales con PII protegida en reposo) y las alternativas evaluadas. La justificacion previa por minimizacion SHALL conservarse como registro historico y SHALL quedar marcada como SUPERADA por el ADR de reversion, sin reescribir la historia. La documentacion MUST vincular la decision con el hallazgo del gap assessment (ISO/IEC 27002 5.34 y 8.12; `models/empleado.py:16-18`) y con el esquema de custodia y rotacion de la clave dedicada.

#### Scenario: El ADR de reversion queda documentado

- **WHEN** se inspecciona `docs/seguridad/` en busca de la decision de cifrado del contacto
- **THEN** existe un ADR que registra la reversion de la decision de texto plano y su motivacion

#### Scenario: La justificacion previa se conserva como superada

- **WHEN** se lee la justificacion por minimizacion previa
- **THEN** queda marcada como SUPERADA por el ADR de reversion, conservando su contenido historico sin reescribirlo

#### Scenario: La decision de cifrado esta vigente en el esquema

- **WHEN** se revisa el esquema de `directorio_empleado` y la configuracion del backend
- **THEN** el email y el telefono se almacenan con `EncryptedText` y existe un indice ciego, coherente con DIR-011
