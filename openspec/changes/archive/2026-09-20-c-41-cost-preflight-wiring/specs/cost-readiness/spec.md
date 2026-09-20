## ADDED Requirements

### Requirement: Cableado automatico del preflight a los caminos de arranque y CI

El preflight de preparacion de costo SHALL ejecutarse de forma automatica, no solo como comando manual. Los scripts de arranque local `scripts/up.sh` (bash) y `scripts/up.ps1` (PowerShell) SHALL ejecutar el preflight antes de tocar Docker; si el preflight termina con codigo de salida no-cero, el arranque MUST terminar con codigo de salida no-cero, MUST imprimir el resultado del preflight nombrando las guardas en FAIL, y MUST NOT arrancar el stack ni ejecutar efectos previos del arranque (por ejemplo, generacion de certificados). Como unica excepcion a ese bloqueo, el operador MAY omitir el gate estableciendo explicitamente `UP_SKIP_COST_PREFLIGHT=1`; en ese caso el arranque SHALL continuar, pero MUST imprimir una advertencia explicita y audible que nombre la variable y advierta que las guardas de costo no fueron verificadas. El bypass SHALL activarse unicamente cuando la variable tenga el valor `1`, y SHALL aplicarse por igual en `scripts/up.sh` y `scripts/up.ps1`. El preflight MUST ser de solo lectura: su ejecucion y su fallo MUST NOT modificar archivos ni el estado de Docker. El `Makefile` SHALL exponer un objetivo `preflight` que invoque el CLI del preflight. El pipeline de integracion continua SHALL instalar las dependencias del preflight, ejecutar su suite de tests y ejecutar el CLI del preflight; si cualquiera falla, el workflow MUST reportar el job como fallido.

#### Scenario: El preflight falla durante el arranque local

- **WHEN** se ejecuta `scripts/up.sh` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el arranque termina con codigo de salida no-cero, imprime el resultado que nombra la guarda faltante, no arranca el stack y no modifica ningun archivo

#### Scenario: El preflight pasa durante el arranque local

- **WHEN** se ejecuta `scripts/up.sh` y el preflight de costo reporta todas las guardas en PASS
- **THEN** el arranque continua con los pasos siguientes (certificados, stack y verificacion de salud)

#### Scenario: Bypass explicito y audible del gate

- **WHEN** el operador ejecuta el arranque local con `UP_SKIP_COST_PREFLIGHT=1` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el arranque NO es bloqueado por el gate, imprime una advertencia explicita y audible que nombra `UP_SKIP_COST_PREFLIGHT` y advierte que las guardas de costo no fueron verificadas, y continua con los pasos siguientes

#### Scenario: El bypass solo se activa con el valor 1

- **WHEN** el operador ejecuta el arranque local con `UP_SKIP_COST_PREFLIGHT` definida con un valor distinto de `1` y el preflight de costo reporta al menos una guarda en FAIL
- **THEN** el gate NO se omite: el arranque termina con codigo de salida no-cero e imprime el resultado del preflight nombrando la guarda en FAIL

#### Scenario: Objetivo del Makefile para el preflight

- **WHEN** se ejecuta `make preflight` en un sistema con `make` disponible
- **THEN** el objetivo invoca el CLI del preflight y su codigo de salida refleja el resultado (cero si todas las guardas pasan)

#### Scenario: CI ejecuta la suite y el CLI del preflight

- **WHEN** se abre un pull request o se hace push a `main`
- **THEN** el workflow de CI instala las dependencias del preflight, ejecuta la suite de tests del preflight y ejecuta el CLI del preflight, fallando el job si el preflight reporta una guarda en FAIL

#### Scenario: Dependencia del preflight ausente en el arranque

- **WHEN** el preflight no puede evaluarse por falta de su dependencia (por ejemplo PyYAML) al ejecutar `scripts/up.sh`
- **THEN** el arranque termina con codigo de salida no-cero e imprime un mensaje accionable que indica como instalar la dependencia, sin arrancar el stack
