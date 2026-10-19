## MODIFIED Requirements

### Requirement: Escaneo de seguridad de dependencias y SAST en el pipeline

El workflow de integracion continua SHALL ejecutar un job de escaneo de seguridad, en paralelo a los jobs de pruebas existentes, que corra sobre Python 3.12 y Node 20 y cubra: auditoria de vulnerabilidades conocidas de las dependencias del backend (`pip-audit` sobre `App/Backend/requirements.txt`), analisis estatico de seguridad del codigo del backend (SAST) y auditoria de dependencias del frontend (`npm audit` sobre `App/Frontend/package-lock.json`). El job MUST declarar de forma explicita su politica de bloqueo (que hallazgos hacen fallar la corrida) y MUST poder completarse sin secretos del repositorio. El job MUST NOT modificar el arbol de dependencias instalado por los jobs de pruebas.

La politica de bloqueo SHALL ser conservadora y estar justificada: el SAST MUST bloquear ante hallazgos de severidad alta en el codigo del backend; la auditoria de dependencias del backend MUST bloquear ante vulnerabilidades conocidas con una correccion NO rompiente disponible, y MUST ofrecer una via documentada para exceptuar de forma explicita y por ID los hallazgos SIN correccion publicada. Los hallazgos corregibles solo mediante una actualizacion mayor rompiente NO MUST exceptuarse mientras la actualizacion sea viable: MUST resolverse subiendo la dependencia. Si la actualizacion resulta NO viable sin rotura desproporcionada, la excepcion MAY mantenerse con el seguimiento revisado registrado, y el bloqueo MUST seguir siendo explicito y auditable. La auditoria de dependencias del frontend MUST operar en modo reporte (no bloqueante) en esta primera iteracion, con su justificacion registrada. Las excepciones MUST ser explicitas y auditables por ID; NO MUST existir un mecanismo global de omision (por ejemplo `continue-on-error`) que suprima el bloqueo de forma silenciosa.

#### Scenario: El job corre los tres escaneos

- **WHEN** se ejecuta el job de escaneo de seguridad
- **THEN** ejecuta la auditoria de dependencias del backend, el analisis estatico de seguridad del backend y la auditoria de dependencias del frontend

#### Scenario: El job declara su politica de bloqueo

- **WHEN** se inspecciona el job de escaneo de seguridad en `.github/workflows/ci.yml`
- **THEN** deja explicito que el SAST bloquea ante severidad alta, que la auditoria del backend bloquea ante vulnerabilidades con correccion NO rompiente (exceptuando de forma explicita y por ID solo los hallazgos sin correccion publicada) y que la auditoria del frontend es no bloqueante en esta iteracion

#### Scenario: Las excepciones de la auditoria del backend son explicitas y auditables

- **WHEN** se inspecciona la politica de bloqueo de la auditoria de dependencias del backend en `.github/workflows/ci.yml` junto con la lista de excepciones versionada en `scripts/security/pip_audit_exceptions.txt`
- **THEN** cada hallazgo exceptuado figura de forma explicita por ID con su motivo, y no existe ningun `continue-on-error` global que suprima de forma silenciosa el bloqueo

#### Scenario: La lista de excepciones solo contiene hallazgos sin correccion publicada

- **WHEN** se revisa `scripts/security/pip_audit_exceptions.txt` despues del cambio
- **THEN** sus entradas corresponden unicamente a hallazgos sin correccion publicada (`python-jose`, `ecdsa`) y las advisories corregibles solo con una actualizacion mayor rompiente ya no figuran porque la dependencia se subio

#### Scenario: El job no requiere secretos

- **WHEN** se ejecuta el job de escaneo de seguridad en un repositorio sin secretos configurados
- **THEN** completa su corrida analizando los archivos de dependencias y el codigo versionados, sin fallar por falta de credenciales

#### Scenario: El job no altera el arbol de dependencias de las pruebas

- **WHEN** el job de escaneo de seguridad instala herramientas o dependencias para escanear
- **THEN** lo hace en su propio entorno y no modifica el conjunto de dependencias instalado por los jobs de pruebas

#### Scenario: El workflow sigue sin referenciar secretos

- **WHEN** se inspecciona `.github/workflows/ci.yml` despues de agregar el job
- **THEN** no aparece ninguna referencia a `secrets.*` ni variables de entorno con credenciales reales
