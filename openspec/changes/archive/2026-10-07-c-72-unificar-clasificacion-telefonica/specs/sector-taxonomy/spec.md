# Delta for sector-taxonomy

## ADDED Requirements

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
