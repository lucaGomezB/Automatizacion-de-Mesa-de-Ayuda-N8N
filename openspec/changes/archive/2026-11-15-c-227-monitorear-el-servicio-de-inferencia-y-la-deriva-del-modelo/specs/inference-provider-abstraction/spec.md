## Purpose

Define la interfaz del proveedor de inferencia de la que depende la etapa semantica del clasificador hibrido, de modo que el sistema no quede cableado a un unico proveedor ni a una unica version de modelo, y que la seleccion de proveedor y de modelo sea una decision de configuracion. La interfaz preserva el contrato canonico del clasificador (los cinco sectores, el prompt, los parametros y el esquema de resultado) y es neutral por defecto: con la configuracion vigente no altera ningun resultado ni ningun numero canonico.

## ADDED Requirements

### Requirement: Interfaz del proveedor de inferencia

El clasificador hibrido SHALL depender de una interfaz abstracta del proveedor de inferencia en lugar de un SDK o proveedor concreto. La interfaz SHALL exponer una operacion asincrona que, dado un texto de entrada y sus parametros de inferencia, devuelva el texto crudo de la respuesta. La etapa semantica SHALL conservar del lado del clasificador la construccion del prompt, la validacion del contrato de respuesta, el reintento acotado y el fallback, de modo que el contrato de clasificacion no dependa del proveedor. La interfaz MUST NOT exponer tipos ni excepciones del SDK de ningun proveedor.

#### Scenario: El orquestador depende de la interfaz y no del SDK

- **WHEN** se inyecta una implementacion falsa de la interfaz en el clasificador hibrido
- **THEN** el clasificador la usa sin importar el SDK de ningun proveedor

#### Scenario: La interfaz no filtra tipos del proveedor

- **WHEN** se inspecciona la firma de la interfaz
- **THEN** ninguno de sus parametros ni de sus tipos de retorno pertenece al SDK de un proveedor concreto

#### Scenario: El contrato de clasificacion permanece en el clasificador

- **WHEN** un proveedor devuelve una respuesta valida
- **THEN** la validacion del contrato de respuesta y la construccion del resultado las ejecuta la etapa semantica, no el proveedor

### Requirement: Taxonomia de errores del proveedor independiente del proveedor

La interfaz SHALL clasificar las fallas del proveedor como transitorias o terminales, para que el bucle de reintento del clasificador no dependa de los tipos de error de un SDK concreto. SHALL tratar como transitorias, y por lo tanto elegibles para reintento, a la indisponibilidad del proveedor, a los limites de tasa y a los timeouts; SHALL tratar como terminales a los errores de peticion, autenticacion o autorizacion. La implementacion concreta SHALL traducir los errores de su SDK a esa taxonomia canonica.

#### Scenario: Una falla transitoria se expone como transitoria

- **WHEN** el proveedor responde con una condicion de indisponibilidad o de limite de tasa
- **THEN** la interfaz la expone como transitoria y el clasificador agenda un reintento acotado

#### Scenario: Una falla terminal se expone como terminal

- **WHEN** el proveedor responde con un error de peticion, autenticacion o autorizacion
- **THEN** la interfaz la expone como terminal y el clasificador no agenda reintentos

#### Scenario: La traduccion de errores es responsabilidad del proveedor

- **WHEN** un proveedor concreto lanza una excepcion de su SDK
- **THEN** la implementacion la traduce a la taxonomia canonica de la interfaz y el clasificador no conoce el tipo del SDK

### Requirement: Seleccion de proveedor y de modelo por configuracion

El proveedor y la version de modelo SHALL ser seleccionables por configuracion, sin modificar el codigo, mediante un registro que resuelva el nombre del proveedor a su implementacion y un parametro de version de modelo. Los valores por defecto MUST resolver al proveedor y al modelo vigentes, de modo que sin configuracion explicita el comportamiento no cambie. Cambiar la version de modelo MUST NOT exigir editar el clasificador.

#### Scenario: Los defaults resuelven al proveedor y modelo vigentes

- **WHEN** no se configura ningun proveedor ni modelo
- **THEN** el sistema resuelve al proveedor y a la version de modelo vigentes

#### Scenario: El override por entorno cambia el proveedor o el modelo

- **WHEN** se define el proveedor o la version de modelo por variable de entorno
- **THEN** el sistema usa ese valor en lugar del default, sin recompilar

#### Scenario: Un proveedor desconocido falla de forma clara

- **WHEN** se configura un nombre de proveedor que el registro no reconoce
- **THEN** el sistema falla con un error explicito en la inicializacion y no arranca con un proveedor silenciosamente inexistente

### Requirement: Neutralidad por defecto y preservacion del contrato canonico

Con el proveedor y el modelo por defecto, la abstraccion SHALL ser neutral: el clasificador MUST reproducir caso por caso las predicciones del clasificador vigente y MUST NOT alterar ningun numero canonico ni la evidencia congelada. La abstraccion SHALL preservar los cinco sectores canonicos con su casing exacto y sin tildes, el prompt, los parametros de inferencia y el esquema del resultado. El recambio de proveedor o de version de modelo es una decision separada y autorizada, no un efecto de la abstraccion.

#### Scenario: La configuracion por defecto reproduce las predicciones vigentes

- **WHEN** se clasifica el corpus de evaluacion con el proveedor y el modelo por defecto a traves de la interfaz
- **THEN** las predicciones coinciden caso por caso con las del clasificador vigente y ningun numero canonico cambia

#### Scenario: El contrato canonico permanece intacto

- **WHEN** se inspeccionan los sectores validos, el prompt y los parametros de inferencia con la configuracion por defecto
- **THEN** son identicos a los vigentes: mismos cinco strings canonicos, mismo prompt y mismos parametros

#### Scenario: La abstraccion no fuerza el recambio

- **WHEN** no se configura un proveedor distinto ni una version de modelo distinta
- **THEN** la abstraccion no cambia el proveedor efectivo y el comportamiento permanece identico al vigente

### Requirement: Trazabilidad de la version efectiva del proveedor y del modelo

El sistema SHALL registrar, para cada clasificacion, el proveedor y la version de modelo efectivos, de modo que un cambio de modelo sea observable y auditable. La identidad del proveedor y del modelo SHALL distinguir entradas de la cache de predicciones, de forma que las predicciones producidas por un modelo distinto no colisionen con las de otro. La distincion MUST conservar valida la evidencia congelada de la configuracion por defecto, cuyas predicciones no declaran proveedor ni modelo.

#### Scenario: La clasificacion registra proveedor y modelo

- **WHEN** el clasificador produce un resultado
- **THEN** el evento estructurado de la clasificacion identifica el proveedor y la version de modelo efectivos

#### Scenario: La cache distingue versiones de modelo

- **WHEN** la cache de predicciones existe con una version de modelo distinta de la vigente
- **THEN** el runner no la usa como valida e invoca al clasificador conforme al gate vigente

#### Scenario: La evidencia congelada por defecto sigue siendo valida

- **WHEN** la cache de predicciones no declara proveedor ni modelo
- **THEN** se asume el proveedor y el modelo por defecto y la evidencia congelada de la configuracion vigente permanece valida
