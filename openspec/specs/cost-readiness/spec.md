# cost-readiness Specification

## Purpose
Define como el proyecto demuestra, sin credenciales ni acceso a red, que las guardas de costo de sus artefactos estan efectivamente cableadas antes de habilitar servicios pagos, y como se acota el tiempo de ejecucion del servicio N8N para que ningun trabajo pago quede sin tope.

## Requirements

### Requirement: Preflight de preparacion de costo, sin red ni credenciales

El sistema SHALL proveer un comando de preflight que, leyendo unicamente los artefactos del repositorio, verifique que las guardas de costo estan presentes y reporte una lista de resultados PASS/FAIL por guarda. El comando MUST NOT realizar acceso a red ni requerir Docker, credenciales o servicios externos. El comando SHALL terminar con codigo de salida 0 si y solo si todas las guardas verificadas estan presentes, y con codigo de salida no-cero si falta al menos una.

#### Scenario: Todas las guardas presentes

- **WHEN** se ejecuta el preflight sobre artefactos que contienen todas las guardas verificadas
- **THEN** el preflight reporta PASS para cada guarda y termina con codigo de salida 0

#### Scenario: Una guarda ausente

- **WHEN** se ejecuta el preflight sobre artefactos a los que les falta una guarda
- **THEN** el preflight reporta FAIL nombrando la guarda faltante y termina con codigo de salida no-cero

#### Scenario: Costo cero

- **WHEN** se ejecuta el preflight
- **THEN** el comando no abre conexiones de red ni requiere credenciales o servicios externos

#### Scenario: Reutilizable como test estructural

- **WHEN** una suite de tests importa las funciones puras del preflight
- **THEN** puede verificar guardas presentes y ausentes sin ejecutar el proceso CLI

### Requirement: Guardas del workflow verificadas por el preflight

El preflight SHALL verificar en `n8n/workflow.json`: (a) el nodo `AI Agent` declara un tope de iteraciones en `options.maxIterations`; (b) el trigger de Outlook declara `readStatus=unread` y un lookback de 24 horas sobre `receivedDateTime`; (c) el nodo `Marcar correo como leido` es alcanzable desde las ramas de exito, rechazo y error; (d) el body del nodo `HTTP POST a MTM-SRU` incluye `origen_message_id`, un bloque de clasificacion precalculada con `sector_predicho` y `confianza`, y un marcador explicito de evento; (e) existe un webhook dedicado con ruta `notificacion-clasificacion` que no esta conectado a la creacion de incidentes; (f) ningun nodo pago habilita reintentos.

#### Scenario: Tope del agente pago presente

- **WHEN** el preflight inspecciona el nodo `AI Agent` del workflow
- **THEN** verifica que `options.maxIterations` esta declarado y la guarda pasa

#### Scenario: Lookback del trigger de Outlook presente

- **WHEN** el preflight inspecciona el trigger de Outlook
- **THEN** verifica `readStatus=unread` y una ventana de 24 horas sobre `receivedDateTime`

#### Scenario: Ciclo de vida del correo alcanzable

- **WHEN** el preflight inspecciona el grafo del workflow
- **THEN** verifica que `Marcar correo como leido` es alcanzable desde las ramas de exito, rechazo y error

#### Scenario: Payload de alta enriquecido presente

- **WHEN** el preflight inspecciona el body del nodo `HTTP POST a MTM-SRU`
- **THEN** verifica la presencia de `origen_message_id`, la clasificacion precalculada y el marcador explicito de evento

#### Scenario: Webhook de notificacion dedicado y aislado

- **WHEN** el preflight inspecciona los webhooks del workflow
- **THEN** verifica que existe la ruta `notificacion-clasificacion` y que su subgrafo no alcanza la creacion de incidentes

### Requirement: Definicion de nodo pago para la guarda de reintentos

El preflight SHALL considerar nodos pagos a los que ejecutan inferencia externa metrada: el nodo de agente `@n8n/n8n-nodes-langchain.agent` y los nodos de modelo de lenguaje cuyo tipo comienza con `@n8n/n8n-nodes-langchain.lm`. La guarda de reintentos SHALL fallar si cualquiera de esos nodos declara `retryOnFail` verdadero o un `maxTries` numerico.

#### Scenario: Ningun nodo pago reintenta

- **WHEN** ningun nodo pago declara `retryOnFail` verdadero ni `maxTries`
- **THEN** la guarda de reintentos pasa

#### Scenario: Reintento pago detectado

- **WHEN** un nodo pago declara `retryOnFail` verdadero o un `maxTries` numerico
- **THEN** la guarda de reintentos falla nombrando el nodo infractor

### Requirement: Guardas del compose verificadas por el preflight

El preflight SHALL verificar en `docker-compose.yml`: (a) la imagen del servicio `n8n` esta pineada a una version explicita y no a `latest`; (b) `N8N_WEBHOOK_URL` apunta a la ruta dedicada de notificacion `/webhook/notificacion-clasificacion`; (c) el environment del servicio `n8n` declara `EXECUTIONS_TIMEOUT`.

#### Scenario: Imagen N8N pineada

- **WHEN** el preflight inspecciona la imagen del servicio `n8n`
- **THEN** la guarda pasa si la etiqueta es una version explicita y falla si es `latest` o si falta la etiqueta

#### Scenario: Webhook de notificacion dedicado en el compose

- **WHEN** el preflight inspecciona `N8N_WEBHOOK_URL`
- **THEN** la guarda pasa si apunta a `/webhook/notificacion-clasificacion` y falla si apunta a otra ruta

#### Scenario: Tope de ejecucion presente en el compose

- **WHEN** el preflight inspecciona el environment del servicio `n8n`
- **THEN** la guarda pasa si `EXECUTIONS_TIMEOUT` esta declarado y falla si esta ausente

### Requirement: Tope de ejecucion declarado del servicio N8N

El servicio `n8n` de `docker-compose.yml` SHALL declarar `EXECUTIONS_TIMEOUT` como cota por defecto y `EXECUTIONS_TIMEOUT_MAX` como cota maxima, ambas numericas y expresadas en segundos, de modo que una ejecucion colgada no permanezca activa de forma indefinida. `EXECUTIONS_TIMEOUT_MAX` SHALL ser mayor o igual que `EXECUTIONS_TIMEOUT`.

#### Scenario: Ambas cotas declaradas

- **WHEN** se inspecciona el environment del servicio `n8n`
- **THEN** `EXECUTIONS_TIMEOUT` y `EXECUTIONS_TIMEOUT_MAX` estan presentes con valores numericos

#### Scenario: Cotas coherentes

- **WHEN** ambas cotas estan presentes
- **THEN** `EXECUTIONS_TIMEOUT_MAX` es mayor o igual que `EXECUTIONS_TIMEOUT`

### Requirement: Cableado automatico del preflight a los caminos de arranque y CI

El preflight de preparacion de costo SHALL ejecutarse de forma automatica, no solo como comando manual. Los scripts de arranque local `scripts/up.sh` (bash) y `scripts/up.ps1` (PowerShell) SHALL ejecutar el preflight antes de tocar Docker; si el preflight termina con codigo de salida no-cero, el arranque MUST terminar con codigo de salida no-cero, MUST imprimir el resultado del preflight nombrando las guardas en FAIL, y MUST NOT arrancar el stack ni ejecutar efectos previos del arranque (por ejemplo, generacion de certificados). Como unica excepcion a ese bloqueo, el operador MAY omitir el gate estableciendo explicitamente `UP_SKIP_COST_PREFLIGHT=1`; en ese caso el arranque SHALL continuar, pero MUST imprimir una advertencia explicita y audible que nombre la variable y advierta que las guardas de costo no fueron verificadas. El bypass SHALL activarse unicamente cuando la variable tenga el valor `1`, y SHALL aplicarse por igual en `scripts/up.sh` y `scripts/up.ps1`. El preflight MUST ser de solo lectura: su ejecucion y su fallo MUST NOT modificar archivos ni el estado de Docker. El `Makefile` SHALL exponer un objetivo `preflight` que invoque el CLI del preflight. El pipeline de integracion continua SHALL instalar las dependencias del preflight, ejecutar su suite de tests y ejecutar el CLI del preflight; si cualquiera falla, el workflow MUST reportar el job como fallido.

#### Scenario: El preflight falla durante el arranque local

- **WHEN** se ejecuta `scripts/up.sh` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el arranque termina con codigo de salida no-cero, imprime el resultado que nombra la guarda faltante, no arranca el stack y no modifica ningun archivo

#### Scenario: El preflight pasa durante el arranque local

- **WHEN** se ejecuta `scripts/up.sh` y el preflight de costo reporta todas las guardas en PASS
- **THEN** el arranque continua con los pasos siguientes (certificados, stack y verificacion de salud)

#### Scenario: Bypass explicito y audible del gate

- **WHEN** el operador ejecuta el arranque local con `UP_SKIP_COST_PREFLIGHT=1` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el arranque NO es bloqueado por el gate, imprime una advertencia explicita y audible que nombra `UP_SKIP_COST_PREFLIGHT` y advierte que las guardas de costo no fueron verificadas, y continua con los pasos siguientes

#### Scenario: El bypass solo se activa con el valor 1

- **WHEN** el operador ejecuta el arranque local con `UP_SKIP_COST_PREFLIGHT` definida con un valor distinto de `1` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el gate NO se omite: el arranque termina con codigo de salida no-cero e imprime el resultado del preflight nombrando la guarda en FAIL

#### Scenario: Objetivo del Makefile para el preflight

- **WHEN** se ejecuta `make preflight` en un sistema con `make` disponible
- **THEN** el objetivo invoca el CLI del preflight y su codigo de salida refleja el resultado (cero si todas las guardas pasan)

#### Scenario: CI ejecuta la suite y el CLI del preflight

- **WHEN** se abre un pull request o se hace push a `main`
- **THEN** el workflow de CI instala las dependencias del preflight, ejecuta la suite de tests del preflight y ejecuta el CLI del preflight, fallando el job si el preflight reporta una guarda en FAIL

#### Scenario: Dependencia del preflight ausente en el arranque

- **WHEN** el preflight no puede evaluarse por falta de su dependencia (por ejemplo PyYAML) al ejecutar `scripts/up.sh`
- **THEN** el arranque termina con codigo de salida no-cero e imprime un mensaje accionable que indica como instalar la dependencia, sin arrancar el stack
