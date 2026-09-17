## ADDED Requirements

### Requirement: Confirmacion obligatoria de la corrida paga

El runner SHALL rechazar por defecto una corrida que invoque un clasificador pago real cuando no exista un cache valido o cuando se bypasee el cache, salvo que el usuario confirme explicitamente la corrida paga mediante el flag `--confirm-paid` o la variable de entorno `EVALUATION_CONFIRM_PAID`. Un cache hit MUST NOT requerir confirmacion, porque no invoca al clasificador. Un clasificador inyectado por parametro (uso en pruebas) MUST NOT requerir confirmacion. El rechazo SHALL ser explicito y accionable, con codigo de salida no-cero, y MUST NOT invocar al clasificador pago.

#### Scenario: Cache hit sin confirmacion

- **WHEN** existe un cache valido y no se aporta confirmacion de corrida paga
- **THEN** el runner carga las predicciones del cache, no invoca al clasificador y no exige confirmacion

#### Scenario: Cache miss sin confirmacion

- **WHEN** no existe un cache valido y no se aporta confirmacion de corrida paga
- **THEN** el runner rechaza la corrida sin invocar al clasificador y termina con codigo de salida no-cero

#### Scenario: Confirmacion por flag

- **WHEN** no existe un cache valido y se invoca el runner con `--confirm-paid`
- **THEN** el runner invoca el clasificador real

#### Scenario: Confirmacion por variable de entorno

- **WHEN** no existe un cache valido y `EVALUATION_CONFIRM_PAID` tiene un valor verdadero
- **THEN** el runner invoca el clasificador real

#### Scenario: Clasificador inyectado en pruebas

- **WHEN** se inyecta un clasificador por parametro y no existe un cache valido
- **THEN** el runner clasifica sin exigir confirmacion de corrida paga

#### Scenario: Bypass de cache no implica confirmacion

- **WHEN** se usa `--force` con un clasificador pago real y sin confirmacion
- **THEN** el runner rechaza la corrida paga; el bypass de cache no sustituye la confirmacion

### Requirement: Estimacion de costo antes de la corrida paga

El runner SHALL imprimir, antes de invocar un clasificador pago real, una estimacion del costo de la corrida derivada de la cantidad de casos del corpus y un costo estimado por llamada, para que el usuario decida con informacion. La estimacion SHALL ser orientativa y SHALL declarar sus supuestos; MUST NOT presentarse como una factura.

#### Scenario: Estimacion impresa antes de clasificar

- **WHEN** una corrida paga procede
- **THEN** antes de invocar al clasificador se imprime la cantidad de casos del corpus y el costo estimado total de la corrida

#### Scenario: Cache hit no reporta costo pago

- **WHEN** existe un cache valido y se usa
- **THEN** el runner no imprime una estimacion de costo pago
