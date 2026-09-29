## MODIFIED Requirements

### Requirement: Costo unitario por superficie paga

El sistema SHALL convertir el gasto de cada superficie paga a la unidad monetaria común mediante un costo unitario configurable por superficie. Cada llamada paga concedida SHALL reservar exactamente el costo unitario de su superficie en la bolsa global. Cuando una superficie paga ejecuta reintentos acotados bajo UNA invocación aceptada, la reserva SHALL dimensionarse al peor caso de intentos de esa invocación (costo unitario multiplicado por el máximo de intentos configurado), evaluada UNA sola vez antes de invocar al proveedor pago; los reintentos MUST NOT disparar reservas adicionales ni re-evaluar la guarda. Los costos unitarios MUST ser configurables sin modificar el código y SHALL quedar documentados como estimaciones, no como contabilidad exacta.

#### Scenario: La reserva usa el costo unitario de la superficie evaluada

- **WHEN** la guarda concede una llamada paga de una superficie
- **THEN** descuenta de la bolsa global el costo unitario configurado para esa superficie

#### Scenario: Superficies distintas usan costos unitarios distintos

- **WHEN** se conceden llamadas pagas de dos superficies con costos unitarios diferentes
- **THEN** cada una descuenta su propio costo unitario de la misma bolsa global

#### Scenario: Una superficie con reintentos reserva el peor caso de intentos

- **WHEN** una superficie paga que ejecuta reintentos acotados es aceptada con un maximo de intentos configurado mayor que uno
- **THEN** la reserva en la bolsa global cubre el costo unitario multiplicado por el maximo de intentos de esa invocacion

#### Scenario: Los reintentos no disparan reservas adicionales

- **WHEN** una invocacion paga aceptada consume uno o mas reintentos por fallas transitorias
- **THEN** la guarda NO se re-evalua ni reserva de nuevo para esa invocacion, y el rate de llamadas pagas cuenta una sola llamada

#### Scenario: Una superficie sin reintentos reserva una unidad

- **WHEN** una superficie paga no ejecuta reintentos (maximo de intentos igual a uno o deshabilitados)
- **THEN** la reserva es exactamente el costo unitario de esa superficie
