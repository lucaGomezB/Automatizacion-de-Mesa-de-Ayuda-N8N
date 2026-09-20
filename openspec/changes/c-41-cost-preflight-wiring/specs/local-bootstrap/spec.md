## MODIFIED Requirements

### Requirement: Preflight de entorno con fallo ruidoso

El comando unico de arranque SHALL verificar, antes de tocar Docker, que `App/Backend/.env` existe y que las variables `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `JWT_SECRET_KEY` estan definidas, no vacias y no siguen siendo valores placeholder de la plantilla `App/Backend/.env.example`. Cuando `App/Backend/.env` no existe, o cuando alguna de esas variables esta ausente, vacia o es un placeholder, el comando MUST terminar con exit code distinto de cero sin arrancar el stack, MUST imprimir un mensaje accionable que indique el prerrequisito faltante, y MUST NOT imprimir el valor de ningun secreto. El chequeo de `JWT_SECRET_KEY` MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Archivo .env ausente

- **WHEN** se ejecuta el comando unico y `App/Backend/.env` no existe
- **THEN** el comando termina con exit code distinto de cero, no arranca el stack, e indica que debe copiarse `App/Backend/.env.example` a `App/Backend/.env`

#### Scenario: Variable secreta vacia o placeholder

- **WHEN** `App/Backend/.env` existe pero `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` o `JWT_SECRET_KEY` esta vacia o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica la variable problematica y no arranca el stack

#### Scenario: JWT_SECRET_KEY ausente

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `JWT_SECRET_KEY` no esta definida
- **THEN** el comando termina con exit code distinto de cero, nombra `JWT_SECRET_KEY` como el prerrequisito faltante y no arranca el stack

#### Scenario: JWT_SECRET_KEY con placeholder de la plantilla

- **WHEN** `JWT_SECRET_KEY` conserva el valor placeholder definido en `App/Backend/.env.example`
- **THEN** el comando termina con exit code distinto de cero, identifica `JWT_SECRET_KEY` y no arranca el stack

#### Scenario: Los valores de secretos nunca se muestran

- **WHEN** el preflight detecta cualquier problema con las variables secretas
- **THEN** la salida nombra la variable faltante pero no incluye el valor de la variable ni ningun otro secreto

#### Scenario: Preflight exitoso

- **WHEN** `App/Backend/.env` existe y las variables secretas requeridas, incluida `JWT_SECRET_KEY`, estan definidas y no son placeholders
- **THEN** el comando continua con el arranque del stack
