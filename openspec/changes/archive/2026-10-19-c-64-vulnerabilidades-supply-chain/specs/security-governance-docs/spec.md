## MODIFIED Requirements

### Requirement: SGD-001 — Ubicacion, indice y trazabilidad de la documentacion

El proyecto SHALL mantener la documentacion de gobernanza de seguridad en `docs/seguridad/`, con un indice `docs/seguridad/README.md`. El indice MUST listar cada documento con su proposito y MUST incluir un mapa de trazabilidad que asocie cada control objetivo (ISO/IEC 27002 5.1, 5.2, 5.9, 5.12, 5.13, 5.19, 5.20, 5.21, 5.22, 5.23, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26 y NIST CSF Govern/Identify) con el documento que lo cubre. El indice MUST declarar que los documentos son **alineados con** los marcos citados y MUST NOT presentarlos como prueba de certificacion. Cada documento de la carpeta MUST ser referenciable desde el indice y las referencias cruzadas entre documentos MUST resolverse a archivos existentes.

#### Scenario: La carpeta y el indice existen

- **WHEN** se inspecciona `docs/seguridad/`
- **THEN** existe `README.md` y los documentos de gobernanza listados por el indice

#### Scenario: El mapa de trazabilidad cubre los controles objetivo

- **WHEN** se lee el mapa de trazabilidad de `docs/seguridad/README.md`
- **THEN** cada control objetivo (5.1, 5.2, 5.9, 5.12, 5.13, 5.19, 5.20, 5.21, 5.22, 5.23, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26) apunta a un documento existente que lo cubre

#### Scenario: Los controles de proveedores quedan mapeados

- **WHEN** se lee el mapa de trazabilidad de `docs/seguridad/README.md`
- **THEN** los controles 5.19 a 5.23 apuntan a `docs/seguridad/evaluacion-seguridad-proveedores.md`

#### Scenario: Las referencias cruzadas resuelven

- **WHEN** un documento de `docs/seguridad/` referencia a otro
- **THEN** el archivo referenciado existe en la carpeta

## ADDED Requirements

### Requirement: SGD-016 — Evaluacion de seguridad de proveedores

El proyecto SHALL incluir `docs/seguridad/evaluacion-seguridad-proveedores.md`, alineado con ISO/IEC 27002 5.19, 5.20, 5.21, 5.22 y 5.23. El documento MUST cubrir los proveedores de servicios del sistema (Twilio, Gemini/Google, Microsoft y N8N), y por cada uno MUST describir la postura de seguridad observable publicamente (por ejemplo: cifrado en transito, gestion de identidades, certificaciones declaradas por el proveedor, canales de reporte de vulnerabilidades) y las clausulas o garantias contractuales a evaluar por la organizacion adoptante. El documento MUST distinguir lo evaluable publicamente de lo que requiere una accion contractual de la organizacion adoptante y MUST registrar como pendientes las garantias que no esten suscritas. El documento MUST usar el lenguaje de alineacion ("alineado con" / "controles mapeados a") y MUST NOT afirmar que el sistema, el repositorio o los proveedores estan "certificados" o son "compliant" con ISO, NIST o la Ley 25.326. El documento MUST ser referenciable desde `docs/seguridad/README.md`.

#### Scenario: El documento cubre los cuatro proveedores

- **WHEN** se lee `docs/seguridad/evaluacion-seguridad-proveedores.md`
- **THEN** contiene una seccion por cada proveedor del sistema (Twilio, Gemini/Google, Microsoft y N8N)

#### Scenario: Cada proveedor declara postura y clausulas

- **WHEN** se lee la seccion de un proveedor
- **THEN** describe su postura de seguridad observable y las clausulas o garantias contractuales a evaluar, distinguiendo lo evaluable publicamente de lo que requiere accion contractual

#### Scenario: Se registran las garantias no suscritas

- **WHEN** se lee el encuadre del documento
- **THEN** declara que las garantias y clausulas no suscritas quedan como accion pendiente de la organizacion adoptante

#### Scenario: El lenguaje de alineacion se respeta

- **WHEN** se revisa `docs/seguridad/evaluacion-seguridad-proveedores.md`
- **THEN** usa "alineado con" o "controles mapeados a" y no afirma que el sistema o los proveedores esten certificados ni sean "compliant"

#### Scenario: El documento se referencia desde el indice

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** el documento de evaluacion de proveedores aparece listado y su referencia resuelve a un archivo existente
