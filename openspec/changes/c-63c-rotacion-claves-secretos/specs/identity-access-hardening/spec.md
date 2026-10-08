## Purpose

Endurece el ciclo de vida y la rotacion de claves y secretos del sistema (controles ISO/IEC 27002 8.2 y 8.24): rotacion del secreto de firma JWT con keyring `kid` y ventana de solapamiento, rotacion de la clave Fernet con re-cifrado transaccional sin perdida de datos, inventario de secretos y runbook de rotacion, postura pragmatica de gestion de secretos, y documentacion organizacional del ciclo de vida de identidades y la revision de accesos. Fase C del split de `c-63-identidad-accesos-claves`.

## ADDED Requirements

### Requirement: IAH-008 — Rotacion del secreto JWT con keyring y ventana de solapamiento

El sistema SHALL soportar la rotacion del secreto de firma JWT sin invalidar de forma inmediata todas las sesiones emitidas. La firma de tokens nuevos MUST usar la clave activa e incluir su `kid` de forma aditiva en el header. Durante una ventana de solapamiento configurable el sistema MUST aceptar tokens firmados con la clave anterior y los tokens legacy sin `kid`; al cerrarse la ventana MUST rechazarlos. La verificacion MUST estar acotada a las claves vigentes del keyring y MUST NOT ser ilimitada. El sistema MUST responder 401 no autenticado ante un token cuya verificacion no corresponda a ninguna clave vigente.

#### Scenario: Token firmado con la clave anterior se acepta durante la ventana

- **WHEN** se presenta un token firmado con la clave anterior dentro de la ventana de solapamiento configurada
- **THEN** el sistema acepta el token y autentica al usuario

#### Scenario: Token con la clave anterior se rechaza tras la ventana

- **WHEN** se presenta un token firmado con la clave anterior una vez cerrada la ventana de solapamiento
- **THEN** el sistema responde 401 no autenticado

#### Scenario: Token legacy sin kid se acepta durante la transicion

- **WHEN** se presenta un token sin claim `kid` emitido antes de la rotacion, dentro de la ventana
- **THEN** el sistema lo valida con alguna de las claves vigentes del keyring

#### Scenario: La firma nueva usa la clave activa

- **WHEN** se emite un token de acceso con el keyring configurado
- **THEN** el token queda firmado con la clave activa y lleva su `kid`

#### Scenario: La verificacion esta acotada

- **WHEN** un token no verifica con ninguna de las claves vigentes del keyring
- **THEN** el sistema rechaza el token sin intentar claves fuera del keyring

### Requirement: IAH-009 — Rotacion de la clave Fernet con re-cifrado sin perdida

El sistema SHALL proveer un procedimiento documentado y una herramienta (`scripts/rotate_fernet_key.py`) para rotar la clave Fernet (`pseudonymization_encryption_key`) y re-cifrar los datos at-rest sin perdida de informacion. El procedimiento MUST partir de un inventario exacto de las columnas cifradas con Fernet; la herramienta MUST re-cifrar todas esas columnas dentro de una unica transaccion y MUST exigir un respaldo previo de los datos afectados, abortando si no se aporta. Durante la migracion el sistema MUST poder descifrar datos cifrados con la clave anterior y, al finalizar, los datos MUST quedar legibles con la clave nueva. La clave anterior MUST retirarse del conjunto recien al confirmarse el re-cifrado, de modo que revertir sea reponer la clave previa.

#### Scenario: El inventario de columnas Fernet existe y es exhaustivo

- **WHEN** se prepara la rotacion de la clave Fernet
- **THEN** existe un inventario que enumera todas las columnas cifradas con Fernet y la herramienta usa esa lista de forma explicita

#### Scenario: La rotacion exige respaldo previo

- **WHEN** se invoca la herramienta de rotacion sin respaldo previo declarado
- **THEN** la herramienta aborta con codigo de salida no-cero y no modifica datos

#### Scenario: El dato antiguo se descifra durante la rotacion

- **WHEN** la rotacion se ejecuta con la clave anterior presente en el conjunto de claves
- **THEN** los datos cifrados con la clave anterior se descifran correctamente

#### Scenario: El re-cifrado es transaccional

- **WHEN** ocurre un fallo durante el re-cifrado de las filas
- **THEN** la transaccion se revierte y no queda ningun dato re-cifrado de forma parcial

#### Scenario: El dato re-cifrado es legible con la clave nueva

- **WHEN** finaliza la rotacion y la clave anterior se retira del conjunto
- **THEN** los datos re-cifrados se descifran correctamente con la clave nueva

#### Scenario: La rotacion es reversible

- **WHEN** se necesita revertir una rotacion ya ejecutada
- **THEN** reponer la clave anterior como activa permite descifrar los datos respaldados

### Requirement: IAH-010 — Higiene y gestion de secretos (postura pragmatica)

El repositorio MUST NOT contener secretos ni credenciales reales; la verificacion de higiene (`.githooks/pre-commit` y `scripts/security/scan_engram_secrets.py`) MUST seguir pasando. El proyecto MUST documentar un inventario de secretos (al menos los JWT y la clave Fernet) y un runbook de rotacion. El proyecto MUST documentar la postura actual de gestion de secretos basada en `.env`/variables de entorno y MAY documentar SOPS, Docker secrets o Vault como opciones no adoptadas por ahora. La adopcion de un gestor de secretos/KMS, un PAM y una CA real de produccion MUST quedar documentada como prerequisito de despliegue (futuro/organizacional) y MUST NOT presentarse como implementada en este change.

#### Scenario: No hay secretos en el repositorio

- **WHEN** se ejecuta la verificacion de higiene de secretos sobre los archivos versionados
- **THEN** no se reportan hallazgos sin resolver

#### Scenario: Inventario de secretos y runbook de rotacion existen

- **WHEN** se revisa la documentacion de seguridad
- **THEN** existe un inventario de secretos y un runbook de rotacion que referencian el secreto JWT y la clave Fernet

#### Scenario: KMS, PAM y CA real se encuadran como futuros

- **WHEN** se lee la postura de gestion de claves
- **THEN** el gestor de secretos/KMS, el PAM y la CA real aparecen como prerequisito de despliegue, no como control implementado

#### Scenario: La postura de secretos y las opciones no adoptadas se documentan

- **WHEN** se lee la documentacion de gestion de secretos
- **THEN** se declara `.env`/variables como fuente actual y se listan SOPS, Docker secrets y Vault como opciones no adoptadas

### Requirement: IAH-011 — Ciclo de vida de identidades y revision de accesos (organizacional)

El proyecto SHALL documentar, como responsabilidad de la organizacion adoptante (controles 5.16 y 5.18), el ciclo de vida de las identidades (alta, cambio y baja) y el proceso de aprobacion y revision periodica de derechos de acceso. La documentacion MUST residir en `docs/seguridad/`, MUST estar referenciada desde el indice `docs/seguridad/README.md` y MUST encuadrarse explicitamente como control organizacional (O), no como codigo del repositorio.

#### Scenario: El ciclo de vida de identidades queda documentado

- **WHEN** se revisa la documentacion de seguridad
- **THEN** describe el ciclo de vida de alta, cambio y baja de identidades como responsabilidad de la organizacion adoptante

#### Scenario: La revision de accesos queda documentada

- **WHEN** se revisa la documentacion de seguridad
- **THEN** describe el proceso y la periodicidad de aprobacion/revision de derechos de acceso y lo marca como control organizacional (O)

#### Scenario: La documentacion organizacional esta referenciada desde el indice

- **WHEN** se inspecciona el indice `docs/seguridad/README.md`
- **THEN** referencia los documentos de ciclo de vida de identidades y de revision de accesos, y las referencias cruzadas resuelven a archivos existentes
