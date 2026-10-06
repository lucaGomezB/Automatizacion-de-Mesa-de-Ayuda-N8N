# Delta for telefonia-stt-intake

## ADDED Requirements

### Requirement: Clasificacion telefonica propiedad del backend sobre la descripcion pseudonimizada

El backend SHALL ser el propietario de la clasificacion del incidente telefonico: la SHALL resolver con la cascada hibrida sobre la descripcion pseudonimizada, de modo que el canal no dependa de una clasificacion producida fuera del backend. El handoff del backend hacia n8n MUST NOT transportar una clasificacion precalculada del incidente, y el backend MUST NOT aceptar del canal telefonico una clasificacion precalculada que omita la cascada. La representacion clasificada SHALL ser la pseudonimizada; el transcript crudo MUST NOT transitar n8n ni ser la entrada de la clasificacion.

#### Scenario: La clasificacion telefonica se resuelve en el backend

- **WHEN** un ingreso telefonico pseudonimizado atraviesa el flujo
- **THEN** la clasificacion del incidente se resuelve en la cascada del backend

#### Scenario: El handoff no lleva clasificacion precalculada

- **WHEN** el backend entrega el ingreso a n8n
- **THEN** el payload del handoff no contiene una clasificacion precalculada del incidente

#### Scenario: La clasificacion usa la representacion pseudonimizada

- **WHEN** el backend clasifica un incidente telefonico
- **THEN** la entrada de la cascada es la descripcion pseudonimizada y el transcript crudo no cruza el borde
