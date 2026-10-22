## ADDED Requirements

### Requirement: Preflight de preparacion de costo antes del arranque

El comando unico de arranque SHALL ejecutar, despues del preflight de entorno y antes de tocar Docker, un preflight estatico de preparacion de costo que verifica las guardas de costo cableadas en `n8n/workflow.json` y `docker-compose.yml`. El preflight SHALL usar unicamente artefactos del repositorio: MUST NOT acceder a red, MUST NOT requerir Docker ni credenciales, y MUST NOT leer ni imprimir la clave `GEMINI_API_KEY` ni ningun otro secreto. La verificacion SHALL implementarse invocando el verificador `scripts/preflight/cost_readiness.py`, cuyo exit code es cero si y solo si todas las guardas estan en PASS. Cuando el verificador termina con exit code distinto de cero, el comando MUST terminar con exit code distinto de cero sin arrancar el stack y MUST imprimir el resumen de guardas, incluidas las que quedaron en FAIL, para diagnostico. `UP_SKIP_COST_PREFLIGHT=1` SHALL ser el unico bypass y MUST ser ruidoso: al definir esa variable el comando omite el gate unicamente si imprime una advertencia explicita; nunca omite el gate en silencio. El gate MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Guardas de costo en PASS

- **WHEN** el verificador de costo termina con exit code cero porque todas las guardas estan en PASS
- **THEN** el comando imprime el resumen del preflight y continua con el siguiente paso del arranque

#### Scenario: Guarda de costo en FAIL bloquea el arranque

- **WHEN** el verificador de costo termina con exit code distinto de cero porque al menos una guarda esta en FAIL
- **THEN** el comando termina con exit code distinto de cero, imprime el resumen de guardas con las fallidas e informa que el stack NO se arranco

#### Scenario: Preflight de costo estatico sin red ni credenciales

- **WHEN** el comando ejecuta el preflight de costo
- **THEN** el preflight verifica unicamente `n8n/workflow.json` y `docker-compose.yml` sin acceder a red, sin requerir Docker ni credenciales y sin leer ni imprimir ningun secreto

#### Scenario: Falla cerrada ante verificador o interprete ausente

- **WHEN** el script `scripts/preflight/cost_readiness.py` no existe o no hay interprete de Python disponible
- **THEN** el comando termina con exit code distinto de cero, informa la dependencia faltante y no arranca el stack

#### Scenario: Bypass explicito y ruidoso del gate de costo

- **WHEN** se define `UP_SKIP_COST_PREFLIGHT=1`
- **THEN** el comando omite el gate de costo e imprime una advertencia explicita de que el stack puede arrancar con guardas de costo rotas

### Requirement: Preflight de preparacion de Gemini antes del arranque

El comando unico de arranque SHALL ejecutar, en el mismo punto del arranque que el preflight de costo (despues del preflight de entorno y antes de tocar Docker), un preflight estatico de la superficie Gemini del workflow que verifica que el nodo de modelo Gemini declara un `modelName` explicito no vacio y que el nodo agente declara un reintento acotado y explicito. Como la rama de IA de N8N fue retirada, estas guardas SHALL conservarse como verificacion de regresion: SHALL pasar cuando el nodo esta ausente y SHALL fallar solo si el nodo reaparece mal configurado. El preflight SHALL usar unicamente artefactos del repositorio: MUST NOT acceder a red, MUST NOT requerir Docker ni credenciales, y MUST NOT leer ni imprimir `GEMINI_API_KEY` ni ningun otro secreto. La verificacion SHALL implementarse invocando el verificador `scripts/preflight/gemini_readiness.py`, cuyo exit code es cero si y solo si todas las guardas estan en PASS. Cuando el verificador termina con exit code distinto de cero, el comando MUST terminar con exit code distinto de cero sin arrancar el stack y MUST imprimir el resumen de guardas para diagnostico. `UP_SKIP_GEMINI_PREFLIGHT=1` SHALL ser el unico bypass y MUST ser ruidoso: al definir esa variable el comando omite el gate unicamente si imprime una advertencia explicita; nunca omite el gate en silencio. El gate MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Superficie Gemini en PASS

- **WHEN** el verificador de Gemini termina con exit code cero porque el modelo esta pineado o ausente y el reintento del agente esta acotado o el nodo esta ausente
- **THEN** el comando imprime el resumen del preflight y continua con el siguiente paso del arranque

#### Scenario: Guarda de Gemini en FAIL bloquea el arranque

- **WHEN** el verificador de Gemini termina con exit code distinto de cero porque el nodo de modelo reaparece sin `modelName` explicito o el nodo agente reaparece con un reintento no acotado
- **THEN** el comando termina con exit code distinto de cero, imprime el resumen de guardas e informa que el stack NO se arranco

#### Scenario: Preflight de Gemini estatico sin red ni clave

- **WHEN** el comando ejecuta el preflight de Gemini
- **THEN** el preflight verifica unicamente `n8n/workflow.json` sin acceder a red, sin requerir Docker ni credenciales y sin leer ni imprimir `GEMINI_API_KEY` ni ningun otro secreto

#### Scenario: Falla cerrada ante verificador o interprete ausente

- **WHEN** el script `scripts/preflight/gemini_readiness.py` no existe o no hay interprete de Python disponible
- **THEN** el comando termina con exit code distinto de cero, informa la dependencia faltante y no arranca el stack

#### Scenario: Bypass explicito y ruidoso del gate de Gemini

- **WHEN** se define `UP_SKIP_GEMINI_PREFLIGHT=1`
- **THEN** el comando omite el gate de Gemini e imprime una advertencia explicita de que el stack puede arrancar con un modelo Gemini implicito o sin reintentos acotados
