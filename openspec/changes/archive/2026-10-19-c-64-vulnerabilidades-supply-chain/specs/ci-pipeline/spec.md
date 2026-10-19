## ADDED Requirements

### Requirement: Escaneo de seguridad de dependencias y SAST en el pipeline

El workflow de integracion continua SHALL ejecutar un job de escaneo de seguridad, en paralelo a los jobs de pruebas existentes, que corra sobre Python 3.12 y Node 20 y cubra: auditoria de vulnerabilidades conocidas de las dependencias del backend (`pip-audit` sobre `App/Backend/requirements.txt`), analisis estatico de seguridad del codigo del backend (SAST) y auditoria de dependencias del frontend (`npm audit` sobre `App/Frontend/package-lock.json`). El job MUST declarar de forma explicita su politica de bloqueo (que hallazgos hacen fallar la corrida) y MUST poder completarse sin secretos del repositorio. El job MUST NOT modificar el arbol de dependencias instalado por los jobs de pruebas.

La politica de bloqueo SHALL ser conservadora y estar justificada: el SAST MUST bloquear ante hallazgos de severidad alta en el codigo del backend; la auditoria de dependencias del backend MUST bloquear ante vulnerabilidades conocidas con correccion disponible, con una via documentada para exceptuar las que no la tengan; la auditoria de dependencias del frontend MUST operar en modo reporte (no bloqueante) en esta primera iteracion, con su justificacion registrada.

#### Scenario: El job corre los tres escaneos

- **WHEN** se ejecuta el job de escaneo de seguridad
- **THEN** ejecuta la auditoria de dependencias del backend, el analisis estatico de seguridad del backend y la auditoria de dependencias del frontend

#### Scenario: El job declara su politica de bloqueo

- **WHEN** se inspecciona el job de escaneo de seguridad en `.github/workflows/ci.yml`
- **THEN** deja explicito que el SAST bloquea ante severidad alta, que la auditoria del backend bloquea ante vulnerabilidades corregibles y que la auditoria del frontend es no bloqueante en esta iteracion

#### Scenario: El job no requiere secretos

- **WHEN** se ejecuta el job de escaneo de seguridad en un repositorio sin secretos configurados
- **THEN** completa su corrida analizando los archivos de dependencias y el codigo versionados, sin fallar por falta de credenciales

#### Scenario: El job no altera el arbol de dependencias de las pruebas

- **WHEN** el job de escaneo de seguridad instala herramientas o dependencias para escanear
- **THEN** lo hace en su propio entorno y no modifica el conjunto de dependencias instalado por los jobs de pruebas

#### Scenario: El workflow sigue sin referenciar secretos

- **WHEN** se inspecciona `.github/workflows/ci.yml` despues de agregar el job
- **THEN** no aparece ninguna referencia a `secrets.*` ni variables de entorno con credenciales reales
