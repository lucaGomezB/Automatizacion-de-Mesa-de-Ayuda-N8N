# Delta for sector-assignment

## ADDED Requirements

### Requirement: ASG-012 — Camino unico de clasificacion para los tres canales

El sistema SHALL resolver la clasificacion del incidente por un UNICO camino: la cascada hibrida del backend (determinista primero, etapa semantica solo si la confianza es insuficiente, revision humana como ultimo recurso) sobre la descripcion pseudonimizada. Los canales correo, web y telefonia MUST usar ese mismo camino. La clasificacion final persistida SHALL provenir de la cascada o de un estado de revision humana. El canal de telefonia MUST NOT persistir como sector del incidente una clasificacion precalculada fuera del backend, y el backend MUST NOT usar una clasificacion precalculada de telefonia para omitir la cascada. El contrato multietiqueta persistido (ASG-001) no cambia.

#### Scenario: Telefono usa la misma cascada que correo y web

- **WHEN** un incidente telefonico llega al backend con su descripcion pseudonimizada
- **THEN** el backend lo clasifica con la cascada hibrida, igual que los canales correo y web

#### Scenario: No se persiste una clasificacion precalculada de telefonia

- **WHEN** el emisor telefonico provee una clasificacion precalculada
- **THEN** el sector persistido NO es esa clasificacion precalculada, sino el resultado de la cascada del backend

#### Scenario: El contrato del resultado no cambia

- **WHEN** la cascada del backend clasifica un incidente telefonico
- **THEN** el resultado expone `sector_predicho`, `sectores_adicionales`, `confianza` y `requiere_revision_humana` conforme al contrato vigente
