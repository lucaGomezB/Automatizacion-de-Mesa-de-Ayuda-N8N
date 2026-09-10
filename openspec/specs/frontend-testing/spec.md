## ADDED Requirements

### Requirement: Infraestructura de pruebas del frontend

El proyecto SHALL proveer una infraestructura de pruebas automatizadas para el frontend React ejecutable por comando. La configuración SHALL usar Vitest como runner, un entorno DOM (`happy-dom`) que permita renderizar componentes React, el alias `@/` resuelto al directorio `src/` (espejando `vite.config.ts`), y un archivo de setup que registre los matchers de `@testing-library/jest-dom` para todas las pruebas. El proyecto MUST exponer un script `test` en `App/Frontend/package.json` que ejecute la suite, y un medio para generar el reporte de cobertura. Las dependencias de prueba MUST agregarse solo como `devDependencies`, sin alterar las dependencias de runtime.

#### Scenario: La suite se ejecuta por comando

- **WHEN** se ejecuta el script `test` definido en `App/Frontend/package.json`
- **THEN** Vitest descubre y ejecuta los archivos de prueba del frontend en el entorno DOM configurado, sin requerir un servidor backend en ejecución

#### Scenario: El alias de importación resuelve como en producción

- **WHEN** una prueba importa un módulo del frontend mediante el prefijo `@/` (por ejemplo `@/services/api`)
- **THEN** la importación resuelve al archivo correspondiente bajo `src/`, igual que en la build de Vite

#### Scenario: Los matchers de jest-dom están disponibles

- **WHEN** una prueba de componente usa un matcher de DOM (por ejemplo `toBeInTheDocument` o `toBeDisabled`)
- **THEN** el matcher está registrado y disponible sin importarlo en cada archivo de prueba

### Requirement: Cobertura mínima de la capa cliente

La suite del frontend SHALL alcanzar una cobertura de líneas superior al 70% en los directorios `src/components/`, `src/hooks/` y `src/services/`, medida con el reporte de cobertura de Vitest (proveedor `v8`). El reporte de cobertura MUST poder generarse por comando.

#### Scenario: La cobertura supera el umbral en las tres capas

- **WHEN** se ejecuta la suite con el reporte de cobertura habilitado
- **THEN** la cobertura de líneas reportada para `src/components/`, `src/hooks/` y `src/services/` es superior al 70% en cada uno

### Requirement: Pruebas de la capa de servicios con Axios mockeado

La suite SHALL verificar la capa de servicios (`api.ts`, `incidentesService.ts`, `clasificacionesService.ts`) mockeando Axios en el límite de red, sin realizar solicitudes HTTP reales. Las pruebas MUST verificar que cada función de servicio invoca el método y la ruta correctos del cliente, que `crearIncidente` envía el payload recibido sin alterarlo, y que `extractApiErrorMessage` normaliza cada forma de error a un mensaje en español.

#### Scenario: Las funciones de servicio invocan la ruta y el método correctos

- **WHEN** se invoca una función de servicio (por ejemplo `listarIncidentes`, `obtenerIncidente`, `validarClasificacion`) con el cliente Axios mockeado
- **THEN** la prueba verifica que se llamó al método HTTP correcto sobre la ruta esperada del prefijo `/api/v1` y que la función devuelve el cuerpo de datos de la respuesta

#### Scenario: extractApiErrorMessage normaliza un detail de FastAPI

- **WHEN** el error de Axios trae `response.data.detail` como cadena de texto
- **THEN** `extractApiErrorMessage` devuelve esa cadena tal cual

#### Scenario: extractApiErrorMessage concatena errores de validación de Pydantic

- **WHEN** el error de Axios trae `response.data.detail` como arreglo de objetos `{ msg, loc }`
- **THEN** `extractApiErrorMessage` devuelve los mensajes `msg` unidos en una sola cadena

#### Scenario: extractApiErrorMessage cubre los códigos HTTP conocidos y el error de red

- **WHEN** el error tiene un código de estado conocido (404, 422, 500, 503), o el código `ECONNABORTED`, o no tiene `response` (error de red)
- **THEN** `extractApiErrorMessage` devuelve el mensaje en español correspondiente a ese caso, y para cualquier otro caso devuelve el mensaje genérico de error inesperado

### Requirement: Pruebas de los hooks de React Query

La suite SHALL verificar los hooks `useReportarIncidente`, `useIncidentes` y `useRevisionPendiente` renderizándolos con un `QueryClient` nuevo por prueba y con la capa de servicios mockeada. Las pruebas MUST verificar que cada hook delega en la función de servicio correcta pasando los parámetros recibidos, y que expone el resultado (`data`) o el error de forma observable.

#### Scenario: useReportarIncidente dispara la creación y expone el resultado

- **WHEN** se monta `useReportarIncidente` con `crearIncidente` mockeado y se ejecuta la mutación con un payload
- **THEN** el hook invoca `crearIncidente` con ese payload y, al resolver, expone el `IncidenteRead` devuelto

#### Scenario: useIncidentes reenvía los parámetros de filtro al servicio

- **WHEN** se monta `useIncidentes` con un objeto de parámetros de filtro y `listarIncidentes` mockeado
- **THEN** el hook invoca `listarIncidentes` con esos mismos parámetros y expone la lista devuelta

#### Scenario: useRevisionPendiente consulta la cola de revisión

- **WHEN** se monta `useRevisionPendiente` con `listarRevisionPendiente` mockeado
- **THEN** el hook invoca el servicio y expone la lista de clasificaciones pendientes devuelta

#### Scenario: Cada prueba de hook usa un QueryClient aislado

- **WHEN** se ejecutan varias pruebas de hooks en la misma corrida
- **THEN** cada una usa un `QueryClient` propio recién creado, de modo que la caché de una prueba no afecta a otra

### Requirement: Pruebas de los indicadores compartidos

La suite SHALL verificar los componentes compartidos `ConfianzaIndicator` y `SectorBadge` consultando su salida accesible. `ConfianzaIndicator` MUST mostrar el porcentaje de confianza y la etiqueta de revisión "Revisar" exactamente cuando la confianza es inferior al umbral 0.70; en el límite 0.70 NO debe pedir revisión. `SectorBadge` MUST mostrar el nombre del sector cuando está presente y el texto "Pendiente" cuando el nombre es nulo o indefinido.

#### Scenario: ConfianzaIndicator pide revisión por debajo del umbral

- **WHEN** se renderiza `ConfianzaIndicator` con una confianza inferior a 0.70
- **THEN** muestra el porcentaje correspondiente y la etiqueta "Revisar"

#### Scenario: ConfianzaIndicator no pide revisión en el umbral o por encima

- **WHEN** se renderiza `ConfianzaIndicator` con una confianza igual o superior a 0.70
- **THEN** muestra el porcentaje correspondiente y NO muestra la etiqueta "Revisar"

#### Scenario: SectorBadge muestra el sector o el estado pendiente

- **WHEN** se renderiza `SectorBadge` con un nombre de sector válido, y luego con `null` o `undefined`
- **THEN** en el primer caso muestra el nombre del sector y en el segundo muestra el texto "Pendiente"

### Requirement: Pruebas del formulario de reporte y la tarjeta de éxito

La suite SHALL verificar el comportamiento observable de `IncidenteForm` y `SuccessCard`. Para `IncidenteForm`, las pruebas MUST verificar que el envío con una descripción de menos de 15 palabras es rechazado por la validación del cliente sin disparar la mutación, y que un envío válido produce un payload que contiene `canal_origen_id = 2` y NO contiene `nombre_usuario` ni `sector_usuario`. Para `SuccessCard`, las pruebas MUST verificar que se muestra el número de ticket y el sector asignado, y que la nota de revisión humana aparece cuando el incidente requiere revisión.

#### Scenario: El formulario rechaza una descripción demasiado corta

- **WHEN** se completa `IncidenteForm` con una descripción de menos de 15 palabras y se envía
- **THEN** se muestra el mensaje de validación de mínimo de palabras y NO se invoca la mutación de creación

#### Scenario: El envío válido arma el payload del contrato de la API

- **WHEN** se completa `IncidenteForm` con datos válidos (descripción de 15 o más palabras) y se envía
- **THEN** la mutación se invoca con un payload que incluye `canal_origen_id` igual a 2 y que NO incluye los campos `nombre_usuario` ni `sector_usuario`

#### Scenario: SuccessCard presenta el ticket creado

- **WHEN** se renderiza `SuccessCard` con un `IncidenteRead` cuyo sector está asignado
- **THEN** muestra el número de ticket del incidente y el badge del sector asignado

#### Scenario: SuccessCard advierte cuando se requiere revisión humana

- **WHEN** se renderiza `SuccessCard` con un incidente cuyo `requiere_revision_humana` es verdadero
- **THEN** muestra la nota de que el ticket será revisado manualmente

### Requirement: Pruebas de las tablas de administración

La suite SHALL verificar `TicketsTable` y `RevisionHumanaTable` en sus distintos estados de consulta. Las pruebas MUST cubrir, para cada tabla: el estado de carga, el estado de error (con el mensaje normalizado y la opción de reintento), el estado vacío, y el estado con datos. Para el estado con datos, las pruebas MUST verificar que se renderiza una fila por elemento y que las interacciones del operador disparan los callbacks correctos (`onSelectIncidente` al hacer clic en una fila de `TicketsTable`; `onValidar` al pulsar "Validar" en `RevisionHumanaTable`, que además oculta el botón cuando la clasificación ya fue validada).

#### Scenario: La tabla muestra el estado de carga

- **WHEN** se renderiza la tabla con `isLoading` verdadero
- **THEN** muestra el indicador de carga y no renderiza filas de datos

#### Scenario: La tabla muestra el estado de error con reintento

- **WHEN** se renderiza la tabla con `isError` verdadero y un error
- **THEN** muestra el mensaje de error normalizado y, al accionar el reintento, invoca `onRefetch`

#### Scenario: La tabla muestra el estado vacío

- **WHEN** se renderiza la tabla con una lista vacía o indefinida y sin carga ni error
- **THEN** muestra el mensaje de estado vacío correspondiente

#### Scenario: TicketsTable renderiza filas y notifica la selección

- **WHEN** se renderiza `TicketsTable` con una lista de incidentes y se hace clic en una fila
- **THEN** se renderiza una fila por incidente y el clic invoca `onSelectIncidente` con el id de ese incidente

#### Scenario: RevisionHumanaTable distingue clasificaciones validadas

- **WHEN** se renderiza `RevisionHumanaTable` con una clasificación sin validar y otra ya validada
- **THEN** la primera muestra el botón "Validar" que al pulsarse invoca `onValidar` con esa clasificación, y la segunda muestra el indicador de validada en lugar del botón
