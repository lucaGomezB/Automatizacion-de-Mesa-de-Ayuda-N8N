## ADDED Requirements

### Requirement: SGD-017 — Reconciliacion del estado vigente y referencias cruzadas

La documentacion de cumplimiento SHALL reflejar el estado vigente del repositorio y de los changes archivados. `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` MUST incluir un registro de estado vigente que, por cada control reconciliado, indique el estado actual, la evidencia en codigo o documentacion, el residual abierto y el change archivado que lo cerro. El registro MUST marcar como cerrados los controles ya implementados (entre ellos MFA y rotacion de claves de C-63, el retiro de Redis de C-62, la politica, clasificacion, inventario, plan de IR y evaluacion de proveedores de C-61/C-64, el SAST y la auditoria de dependencias de C-64, y la retencion de logs de C-66). El documento MUST NOT declarar ausente un control que ya existe en el repositorio. Los residuales que dependen de la organizacion adoptante (revision independiente 5.35, redundancia 8.14, copia offsite y contratos con proveedores) MUST permanecer explicitamente abiertos.

Las referencias cruzadas de `docs/seguridad/` SHALL resolver a archivos existentes y al estado real de los changes. En particular, el inventario de activos MUST NOT listar Redis como activo activo, MUST marcar Microsoft Outlook como inactivo desde C-55 y MUST referenciar `gestion-secretos-y-rotacion.md` en lugar de un change C-63 inexistente como change unico. El `README.md` de `docs/seguridad/` MUST presentar C-62 a C-67 como archivados (no pendientes), MUST mapear 5.34/8.12 a `adr-001-reversion-minimizacion-directorio.md` y `clasificacion-etiquetado-informacion.md` en lugar de la justificacion superada, y MUST NOT conservar la nota de "pendiente para el orquestador" sobre `CHANGES.md` una vez cumplida. El ROPA MUST indicar que Microsoft Outlook figura como procesador historico inactivo.

#### Scenario: El gap assessment no declara ausente un control implementado

- **WHEN** se lee el registro de estado vigente del gap assessment
- **THEN** MFA, rotacion de claves, retiro de Redis, politica, clasificacion, inventario, plan de IR, evaluacion de proveedores, SAST/auditoria de dependencias y retencion de logs figuran como cerrados con su evidencia y su change archivado

#### Scenario: Los residuales del adoptante permanecen abiertos

- **WHEN** se lee el gap assessment reconciliado
- **THEN** 5.35, 8.14, la copia offsite y los contratos con proveedores siguen declarados como residuales o acciones de la organizacion adoptante

#### Scenario: Las referencias a Redis y a Microsoft son correctas

- **WHEN** se lee `inventario-activos-informacion.md`
- **THEN** Redis no aparece como activo activo y Microsoft Outlook figura como inactivo desde C-55

#### Scenario: El indice refleja los changes archivados

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** C-62 a C-67 figuran como archivados, la justificacion del directorio apunta al ADR y a la clasificacion vigente, y no queda la nota pendiente sobre `CHANGES.md`

### Requirement: SGD-018 — Lint documental de cumplimiento

El proyecto SHALL incluir una prueba automatizada y hermética que valide la integridad de `docs/seguridad/` sin depender de servicios externos ni de red. La prueba MUST verificar que: (a) cada documento listado en el indice existe; (b) cada archivo `.md` de la carpeta de gobernanza esta listado en el indice; (c) cada documento de gobernanza abre con los encabezados requeridos (control mapeado, estado, alcance y encuadre); y (d) ningun documento afirma certificacion o conformidad con ISO, NIST o la Ley 25.326 mediante terminos afirmativos prohibidos. La prueba MUST tolerar las negaciones y encuadres de alineacion ("no constituye certificacion", "alineado con") y MUST fallar ante una afirmacion positiva de certificacion. La prueba SHALL ejecutarse como parte de la suite de backend, de modo que el job de integracion continua existente la ejecute sin modificar el workflow.

#### Scenario: Un documento faltante rompe el lint

- **WHEN** el indice lista un documento que no existe en `docs/seguridad/`
- **THEN** la prueba falla indicando el documento y la referencia faltante

#### Scenario: Un documento no listado rompe el lint

- **WHEN** existe un documento de gobernanza en `docs/seguridad/` que el indice no lista
- **THEN** la prueba falla indicando el documento omitido

#### Scenario: Una afirmacion de certificacion rompe el lint

- **WHEN** un documento afirma que el sistema esta certificado, es compliant o cumple ISO/NIST de forma positiva
- **THEN** la prueba falla indicando el archivo y la frase prohibida

#### Scenario: El encuadre de alineacion no rompe el lint

- **WHEN** un documento declara que esta alineado con los marcos y que no constituye certificacion ni auditoria
- **THEN** la prueba pasa para ese documento

#### Scenario: El lint corre en la suite de backend

- **WHEN** se ejecuta `pytest` en `App/Backend/`
- **THEN** el lint documental se ejecuta y no requiere PostgreSQL, Gemini, N8N ni red

### Requirement: SGD-019 — Manejo de evidencia y cadena de custodia

El plan de respuesta a incidentes de seguridad y la politica de retencion de logs SHALL documentar el manejo de evidencia de un incidente (control ISO/IEC 27002 5.28). La documentacion MUST cubrir la identificacion de la evidencia, su recoleccion y preservacion, la integridad verificable (por ejemplo, hash del artefacto), el registro de custodios y transferencias, y la retencion aplicable segun la clase de registro. MUST aclarar que la cadena de custodia formal y la preservacion forense completa son responsabilidad de la organizacion adoptante cuando el incidente exceda el alcance del repositorio.

#### Scenario: La evidencia tiene identificacion y preservacion

- **WHEN** se lee la seccion de evidencia del plan de respuesta a incidentes
- **THEN** describe que evidencia se recolecta, como se preserva y donde se registra

#### Scenario: La integridad es verificable

- **WHEN** se lee el procedimiento de evidencia
- **THEN** exige un mecanismo de verificacion de integridad (hash o equivalente) y el registro de custodios y transferencias

#### Scenario: La custodia formal queda encuadrada en el adoptante

- **WHEN** se lee el encuadre de la seccion de evidencia
- **THEN** declara que la cadena de custodia formal y la preservacion forense completa competen a la organizacion adoptante

### Requirement: SGD-020 — Inventario de licencias de dependencias

El proyecto SHALL incluir `docs/seguridad/inventario-licencias.md`, alineado con ISO/IEC 27002 5.32 (Propiedad intelectual). El inventario MUST listar las dependencias principales de backend y frontend con su licencia declarada, MUST identificar las licencias que imponen obligaciones de atribucion o copyleft y MUST NOT contener credenciales ni secretos. El documento MUST declarar que es un inventario de referencia y que la verificacion legal definitiva compete a la organizacion adoptante.

#### Scenario: El inventario cubre backend y frontend

- **WHEN** se lee `docs/seguridad/inventario-licencias.md`
- **THEN** lista dependencias principales de backend y frontend con su licencia declarada

#### Scenario: Las obligaciones de licencia quedan identificadas

- **WHEN** se revisan las dependencias con licencias copyleft o de atribucion
- **THEN** el documento identifica la obligacion aplicable

#### Scenario: El inventario se referencia desde el indice

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** `inventario-licencias.md` aparece listado y su referencia resuelve a un archivo existente
