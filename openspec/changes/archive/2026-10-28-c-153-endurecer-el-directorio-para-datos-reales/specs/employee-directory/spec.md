## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: DIR-005 — Almacenamiento en texto plano (sin cifrado de aplicacion ni indice ciego)

**Reason**: La decision de texto plano se REVIERTE para poder habilitar datos personales reales con PII protegida en reposo. Se adopta cifrado at-rest mas indice ciego determinista, conforme al ADR de reversion.

**Migration**: Sustituida por el requisito `DIR-011 — Cifrado at-rest del contacto con indice ciego determinista`. El modelo, el repositorio y la migracion pasan a cifrado con `EncryptedText` y busqueda por indice ciego; la justificacion por minimizacion previa se conserva marcada como SUPERADA.

### Requirement: DIR-010 — Justificacion documental de la minimizacion del contacto en texto plano

**Reason**: La justificacion por minimizacion del contacto en texto plano queda SUPERADA por la reversion a cifrado; mantenerla como requisito vigente contradiria DIR-011.

**Migration**: Sustituida por el requisito `DIR-016 — ADR de reversion y justificacion documental del cifrado`. El documento de minimizacion previo se conserva como registro historico marcado como SUPERADO.

## ADDED Requirements

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
