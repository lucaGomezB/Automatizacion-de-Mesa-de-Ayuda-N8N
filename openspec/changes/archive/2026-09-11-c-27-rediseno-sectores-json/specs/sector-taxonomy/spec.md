## Purpose

Define el vocabulario canonico de sectores de la mesa de ayuda y su distribucion efectiva en el clasificador deterministico, el prompt/validacion de Gemini y las opciones del frontend.

## ADDED Requirements

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

El clasificador determinista SHALL exponer exactamente los cinco sectores canonicos como vocabulario de salida, derivado de un mapa de keywords redistribuido que cubra los cinco sectores. El clasificador MUST NOT emitir `Operaciones` en ninguna circunstancia y MUST NOT quedar sin terminos para ningun sector canonico.

#### Scenario: Todos los sectores tienen terminos

- **WHEN** se inspecciona el mapa de keywords del clasificador determinista
- **THEN** cada uno de los cinco sectores canonicos tiene al menos un termino asociado

#### Scenario: Termino de hardware clasifica como Soporte Tecnico Hardware

- **WHEN** el clasificador determinista procesa una descripcion con terminos de hardware de equipos
- **THEN** la prediccion pertenece a `Soporte Tecnico Hardware` y no a `Operaciones`

#### Scenario: Ningun termino produce Operaciones

- **WHEN** el clasificador determinista procesa descripciones representativas de todos los sectores
- **THEN** ninguna prediccion resultante es `Operaciones`

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
