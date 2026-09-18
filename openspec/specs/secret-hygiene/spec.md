# secret-hygiene Specification

## Purpose
Define como el repositorio publico detecta, tria y remedia la exposicion de secretos de forma repetible y auditable: deteccion local antes del commit, escaneo del lado de GitHub con proteccion de push, resolucion explicita de alertas y un runbook de rotacion de credenciales expuestas.

## Requirements

### Requirement: Deteccion local de secretos antes del commit

El repositorio SHALL proveer un hook pre-commit versionado en `.githooks/pre-commit` que bloquee el commit cuando haya archivos `.env` en el area de staging (salvo plantillas `.env.example`, `.env.sample` o `.env.template`) o lineas agregadas que coincidan con patrones de secretos: claves de Google, claves privadas PEM, y asignaciones genericas de `key`/`secret`/`token`/`password` con valores largos. El hook SHALL aceptar el marcador explicito `gitleaks:allow` en una linea para whitelistear un falso positivo. La activacion del hook SHALL requerir `git config core.hooksPath .githooks` y esa instruccion SHALL estar documentada. El hook MUST NOT exponer el valor de ningun secreto en su salida.

#### Scenario: Archivo .env staged

- **WHEN** se intenta commitear un archivo `.env` no-plantilla
- **THEN** el hook bloquea el commit, termina con codigo de salida no-cero y nombra los archivos bloqueados sin imprimir su contenido

#### Scenario: Plantilla de entorno permitida

- **WHEN** se commitea un archivo `.env.example`, `.env.sample` o `.env.template`
- **THEN** el hook no bloquea el commit por la regla de archivos `.env`

#### Scenario: Secreto en linea agregada

- **WHEN** una linea agregada coincide con un patron de clave de Google, clave privada PEM o asignacion generica de credencial con valor largo
- **THEN** el hook bloquea el commit y nombra el archivo con la linea sospechosa

#### Scenario: Falso positivo con marcador explicito

- **WHEN** una linea agregada incluye el marcador `gitleaks:allow`
- **THEN** el hook no bloquea el commit por esa linea

#### Scenario: Hook no activado

- **WHEN** un clon no ejecuto `git config core.hooksPath .githooks`
- **THEN** el runbook documenta como activarlo y advierte que sin esa configuracion la deteccion local no corre

### Requirement: Escaneo de secretos del lado de GitHub habilitado

El repositorio SHALL mantener habilitados el escaneo de secretos (secret scanning) y la proteccion de push (push protection). El repositorio SHALL proveer `scripts/security/configure_github_secret_scanning.sh`, un script idempotente que habilita mediante `gh api` las protecciones configurables por API e IMPRIME el estado de las dos funciones restantes (patrones no-proveedor y verificaciones de validez), advirtiendo que no estan disponibles en el plan gratuito (requieren GitHub Secret Protection) y que la API REST las ignora en silencio. El script MUST NOT embeber secretos ni reescribir el historial de git. Cuando `gh` no este disponible o no este autenticado con permisos suficientes, el script SHALL fallar ruidosamente con un mensaje accionable y MUST NOT reportar exito.

#### Scenario: Protecciones configurables por API habilitadas

- **WHEN** se ejecuta el script con `gh` autenticado y permisos de administracion del repositorio
- **THEN** el script habilita secret scanning y push protection mediante `gh api` y reporta el estado resultante

#### Scenario: Re-ejecucion idempotente

- **WHEN** el script se ejecuta sobre un repositorio que ya tiene ambas protecciones habilitadas
- **THEN** el script no falla y deja el mismo estado

#### Scenario: Funciones no disponibles reportadas

- **WHEN** se ejecuta el script
- **THEN** reporta los patrones no-proveedor y las verificaciones de validez como no configurables por API y no disponibles en el plan gratuito (requieren GitHub Secret Protection), sin mandar a un toggle inexistente

#### Scenario: Entorno incompleto

- **WHEN** `gh` no esta instalado o no esta autenticado con permisos suficientes
- **THEN** el script termina con codigo de salida no-cero y un mensaje accionable, sin exponer secretos

#### Scenario: Sin reescritura de historial ni secretos embebidos

- **WHEN** se inspecciona o se ejecuta el script
- **THEN** no contiene valores de credenciales y no invoca comandos de reescritura del historial de git

### Requirement: Triaje y resolucion de alertas de secret scanning

El repositorio SHALL triar las alertas de secret scanning y resolverlas con una resolucion explicita y veraz (`revoked`, `false_positive`, `used_in_tests` o `wont_fix`), nunca con un descarte ciego ni dejando `resolution` en nulo cuando corresponde cerrarla. Una alerta cuyo secreto ya fue revocado en el proveedor SHALL resolverse como `revoked`. La alerta historica de la clave Google Gemini (numero `1`, tipo `google_api_key`) SHALL resolverse como `revoked`, dado que la clave ya fue revocada. El script SHALL ofrecer la resolucion de una alerta por numero como operacion opt-in, con confirmacion explicita, y por defecto MUST limitarse a listar y reportar.

#### Scenario: Secreto revocado se resuelve como revoked

- **WHEN** se tria una alerta cuyo secreto ya fue revocado en el proveedor
- **THEN** la alerta se resuelve con `resolution: revoked`

#### Scenario: Alerta historica de Gemini

- **WHEN** se tria la alerta numero `1` de tipo `google_api_key`
- **THEN** se resuelve como `revoked` porque la clave Gemini fue revocada y su remocion del historial es innecesaria

#### Scenario: Resolucion opt-in

- **WHEN** se invoca el script sin la opcion explicita de resolver una alerta
- **THEN** el script lista y reporta las alertas abiertas pero no cambia su estado

#### Scenario: Resolucion con confirmacion

- **WHEN** se invoca el script para resolver una alerta por numero con confirmacion explicita
- **THEN** el script aplica la resolucion indicada y reporta el nuevo estado de la alerta

### Requirement: Runbook de endurecimiento y rotacion de credenciales expuestas

El repositorio SHALL incluir `docs/security-hardening.md`, que documenta: (a) que funciones de escaneo de secretos de GitHub son configurables por API, cuales no, y cuales no estan disponibles en el plan gratuito; (b) como funciona la proteccion de push; (c) como triar y resolver alertas indicando `state` y `resolution`; (d) la instalacion del hook pre-commit; y (e) el procedimiento de rotacion de credenciales expuestas, usando la filtracion de la clave Gemini como caso de estudio. El procedimiento de rotacion SHALL indicar revocar primero la credencial en el proveedor, rotar el valor en el `.env` gitignorado, y que la remocion del historial de git no es necesaria una vez que la credencial fue revocada.

#### Scenario: Cobertura del runbook

- **WHEN** un operador lee `docs/security-hardening.md`
- **THEN** encuentra las secciones de API vs UI, proteccion de push, triaje y resolucion de alertas, instalacion del hook y rotacion de credenciales

#### Scenario: Caso de estudio de la filtracion de Gemini

- **WHEN** se lee el procedimiento de rotacion
- **THEN** referencia la filtracion historica de la clave Gemini y las acciones tomadas (revocacion, rotacion y resolucion de la alerta)

#### Scenario: Rotacion sin reescritura de historial

- **WHEN** se sigue el procedimiento de rotacion para una credencial revocada
- **THEN** el procedimiento no incluye reescribir el historial de git como paso requerido
