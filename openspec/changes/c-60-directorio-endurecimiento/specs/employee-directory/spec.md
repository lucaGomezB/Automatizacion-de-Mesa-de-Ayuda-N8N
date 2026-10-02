## MODIFIED Requirements

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

## ADDED Requirements

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
