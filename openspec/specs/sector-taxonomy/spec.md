# sector-taxonomy Specification

## Purpose
Define el vocabulario canonico de sectores de la mesa de ayuda y su distribucion efectiva en el clasificador deterministico, el prompt/validacion de Gemini y las opciones del frontend.

## Requirements

### Requirement: TAX-001 — Conjunto canonico de cinco sectores

El sistema SHALL reconocer exactamente los siguientes cinco sectores canonicos, como cadenas exactas, sensibles a mayusculas y SIN tildes: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`. `Operaciones` MUST quedar eliminado por completo del vocabulario y `Sistemas` MUST mantenerse como una categoria propia, sin repartirse entre las demas.

#### Scenario: Conjunto valido aceptado

- **WHEN** un componente del dominio recibe un sector igual a uno de los cinco strings canonicos
- **THEN** lo acepta como valido

#### Scenario: Sector eliminado rechazado

- **WHEN** un componente del dominio recibe el sector `Operaciones`
- **THEN** lo rechaza por no pertenecer al conjunto canonico

#### Scenario: Variante con tilde o casing incorrecto rechazada

- **WHEN** un componente recibe `Soporte Técnico Hardware`, `soporte tecnico hardware` o cualquier variante con tilde o mayusculas distintas
- **THEN** la rechaza por no coincidir exactamente con el string canonico

#### Scenario: Sistemas es una categoria independiente

- **WHEN** un caso corresponde a un servidor en produccion o a un sistema corporativo sin encuadre especifico de seguridad, hardware, software o datos
- **THEN** el sector asignado puede ser `Sistemas`, que permanece como categoria propia

### Requirement: TAX-002 — Redistribucion de keywords del clasificador determinista

El clasificador determinista SHALL exponer exactamente los cinco sectores canonicos como vocabulario de salida, derivado de un mapa de keywords redistribuido que cubra los cinco sectores. El mapa SHALL incluir sinonimos, variantes morfologicas y frases representativas por sector, de modo que Hardware y Software (los sectores con mayor soporte real del corpus) tengan cobertura suficiente y NO queden sub-representados. El clasificador MUST NOT emitir `Operaciones` en ninguna circunstancia y MUST NOT quedar sin terminos para ningun sector canonico. Las claves del mapa MUST ser exactamente los cinco strings canonicos, verificable por una invariante estructural (`set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)`), y MUST NOT alterar los cinco strings canonicos ni sus acentos.

#### Scenario: Todos los sectores tienen terminos

- **WHEN** se inspecciona el mapa de keywords del clasificador determinista
- **THEN** cada uno de los cinco sectores canonicos tiene al menos un termino asociado

#### Scenario: Termino de hardware clasifica como Soporte Tecnico Hardware

- **WHEN** el clasificador determinista procesa una descripcion con terminos de hardware de equipos
- **THEN** la prediccion pertenece a `Soporte Tecnico Hardware` y no a `Operaciones`

#### Scenario: Ningun termino produce Operaciones

- **WHEN** el clasificador determinista procesa descripciones representativas de todos los sectores
- **THEN** ninguna prediccion resultante es `Operaciones`

#### Scenario: La invariante de claves se preserva tras ampliar el vocabulario

- **WHEN** se amplia el vocabulario con nuevos sinonimos o frases
- **THEN** las claves del mapa siguen siendo exactamente los cinco sectores canonicos y el assert estructural no se rompe

#### Scenario: Hardware y Software tienen cobertura ampliada

- **WHEN** se inspecciona el vocabulario de `Soporte Tecnico Hardware` y `Soporte Tecnico Software`
- **THEN** cada uno expone un conjunto de terminos mayor o igual al que tenia antes del endurecimiento, guiado por las misclasificaciones del corpus

### Requirement: TAX-003 — Prompt, enum y validacion de Gemini alineados al vocabulario

El prompt de Gemini, el `response_schema` con su enum de categorias y la validacion de la respuesta SHALL enumerar exactamente los cinco sectores canonicos. La respuesta de Gemini MUST ser rechazada cuando devuelve un valor fuera del conjunto canonico, y el sistema SHALL degradar a la etapa de fallback sin propagar categorias invalidas.

#### Scenario: El prompt enumera los cinco sectores

- **WHEN** se inspecciona el prompt cargado por el clasificador de Gemini
- **THEN** contiene los cinco strings canonicos exactos y no menciona `Operaciones`

#### Scenario: El response_schema restringe a los cinco sectores

- **WHEN** se inspecciona el `response_schema` del clasificador de Gemini
- **THEN** el enum de la propiedad de sector contiene exactamente los cinco strings canonicos

#### Scenario: Respuesta invalida degrada a fallback

- **WHEN** Gemini devuelve un sector fuera del conjunto canonico, por ejemplo `Operaciones`
- **THEN** el clasificador rechaza la respuesta y activa la etapa de fallback

### Requirement: Dependencia de los nombres canonicos en el frontend

El frontend SHALL consumir los nombres canonicos de sector como fuente de verdad y MUST NOT depender de identificadores numericos de sector fijos para construir las opciones del formulario ni para resolver etiquetas. La interfaz SHALL mostrar correctamente los cinco sectores y manejar de forma segura un nombre de sector desconocido sin romper el renderizado.

#### Scenario: Opciones del formulario derivadas de los nombres

- **WHEN** se cargan las opciones de sector del formulario de reporte
- **THEN** las opciones corresponden a los cinco nombres canonicos y no a IDs numericos fijos

#### Scenario: Sector desconocido no rompe la interfaz

- **WHEN** un incidente trae un nombre de sector que no coincide con las opciones conocidas
- **THEN** el componente de insignia y el de distribucion lo renderizan con un estilo por defecto sin lanzar excepciones

### Requirement: Cobertura medida del vocabulario determinista

El sistema SHALL medir la cobertura del vocabulario determinista sobre el corpus de evaluacion, definida como la fraccion de casos en que al menos un termino del mapa hace match. El endurecimiento SHALL reducir la tasa de casos sin match respecto de la linea base y la sobre-prediccion del sector por defecto (linea base: 126 predicciones de `Seguridad Informatica` vs 31 reales en 200 casos) y SHALL reportar la cobertura por sector, de modo que la ampliacion del vocabulario sea verificable con datos y no por inspeccion subjetiva. La medicion MUST ser offline (sin invocar a Gemini) y MUST NOT modificar `evaluation/corpus.py::_a_float`.

#### Scenario: Cobertura reportada por sector

- **WHEN** se corre la medicion offline del vocabulario sobre el corpus
- **THEN** el reporte expone la cobertura global y por sector, y la cantidad de casos sin match

#### Scenario: La cobertura sube respecto de la linea base

- **WHEN** se compara la cobertura tras ampliar el vocabulario contra la linea base medida
- **THEN** la cantidad de casos sin senal es estrictamente menor y ningun sector pierde terminos

#### Scenario: La medicion no invoca al proveedor pago

- **WHEN** se ejecuta la medicion de cobertura
- **THEN** no se realiza ninguna llamada a Gemini y el resultado depende solo del corpus y del mapa de keywords

### Requirement: TAX-004 — Reglas de desambiguacion de frontera en el prompt compartido

El prompt compartido de clasificacion (`docs/prompt_gemini.txt`) SHALL incluir reglas de desambiguacion de frontera entre sectores adyacentes, de modo que los casos de borde se resuelvan de forma consistente en los tres canales. Las reglas SHALL cubrir, al menos: las acciones sobre aplicaciones o sistemas operativos (acceder, iniciar sesion, abrir una aplicacion) se asignan a `Soporte Tecnico Software`; los dispositivos fisicos y su digitalizacion (escaner, impresora, periferico, error de digitalizacion) se asignan a `Soporte Tecnico Hardware`; la infraestructura y los servicios de plataforma (servidor, red, SMTP, VM) se asignan a `Sistemas`. Las reglas MUST usar exactamente los cinco strings canonicos sin tildes y MUST NOT introducir sectores fuera del conjunto canonico. El prompt compartido SHALL ser el unico prompt de clasificacion del sistema: el canal telefonico MUST NOT mantener un prompt divergente.

#### Scenario: Regla de frontera Software para accesos a aplicaciones

- **WHEN** la descripcion indica que el usuario no puede acceder o iniciar sesion en una aplicacion o sistema operativo
- **THEN** la regla del prompt lo orienta a `Soporte Tecnico Software`

#### Scenario: Regla de frontera Hardware para digitalizacion

- **WHEN** la descripcion menciona un error de digitalizacion, escaner o impresora
- **THEN** la regla del prompt lo orienta a `Soporte Tecnico Hardware`

#### Scenario: Regla de frontera Sistemas para infraestructura

- **WHEN** la descripcion menciona un servidor, una red, SMTP o una VM
- **THEN** la regla del prompt lo orienta a `Sistemas`

#### Scenario: El prompt es unico y no introduce sectores nuevos

- **WHEN** se inspecciona el prompt compartido
- **THEN** contiene las reglas de frontera y usa exclusivamente los cinco strings canonicos, sin tildes

#### Scenario: No hay prompt divergente en telefonia

- **WHEN** se inspecciona el flujo telefonico
- **THEN** no mantiene un prompt de clasificacion propio distinto del prompt compartido
