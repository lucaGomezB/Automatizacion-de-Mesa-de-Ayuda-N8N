## MODIFIED Requirements

### Requirement: Preflight de entorno con fallo ruidoso

El comando unico de arranque SHALL verificar, antes de tocar Docker, que `App/Backend/.env` existe y que las variables `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` y `COST_GUARD_CALLER_HMAC_KEY` estan definidas, no vacias y no siguen siendo valores placeholder de la plantilla `App/Backend/.env.example`. Cuando `App/Backend/.env` no existe, o cuando alguna de esas variables esta ausente, vacia o es un placeholder, el comando MUST terminar con exit code distinto de cero sin arrancar el stack, MUST imprimir un mensaje accionable que indique el prerrequisito faltante, y MUST NOT imprimir el valor de ningun secreto. El chequeo de las cuatro variables MUST aplicarse tanto en `scripts/up.sh` como en `scripts/up.ps1`, preservando la equivalencia multiplataforma.

#### Scenario: Archivo .env ausente

- **WHEN** se ejecuta el comando unico y `App/Backend/.env` no existe
- **THEN** el comando termina con exit code distinto de cero, no arranca el stack, e indica que debe copiarse `App/Backend/.env.example` a `App/Backend/.env`

#### Scenario: Variable secreta vacia o placeholder

- **WHEN** `App/Backend/.env` existe pero `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` o `COST_GUARD_CALLER_HMAC_KEY` esta vacia o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica la variable problematica y no arranca el stack

#### Scenario: JWT_SECRET_KEY ausente

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `JWT_SECRET_KEY` no esta definida
- **THEN** el comando termina con exit code distinto de cero, nombra `JWT_SECRET_KEY` como el prerrequisito faltante y no arranca el stack

#### Scenario: JWT_SECRET_KEY con placeholder de la plantilla

- **WHEN** `JWT_SECRET_KEY` conserva el valor placeholder definido en `App/Backend/.env.example`
- **THEN** el comando termina con exit code distinto de cero, identifica `JWT_SECRET_KEY` y no arranca el stack

#### Scenario: COST_GUARD_CALLER_HMAC_KEY ausente o con placeholder

- **WHEN** `App/Backend/.env` existe, las demas variables secretas son validas, pero `COST_GUARD_CALLER_HMAC_KEY` no esta definida o conserva el valor placeholder de la plantilla
- **THEN** el comando termina con exit code distinto de cero, identifica `COST_GUARD_CALLER_HMAC_KEY` y no arranca el stack

#### Scenario: Los valores de secretos nunca se muestran

- **WHEN** el preflight detecta cualquier problema con las variables secretas
- **THEN** la salida nombra la variable faltante pero no incluye el valor de la variable ni ningun otro secreto

#### Scenario: Preflight exitoso

- **WHEN** `App/Backend/.env` existe y las cuatro variables secretas requeridas (`GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY` y `COST_GUARD_CALLER_HMAC_KEY`) estan definidas y no son placeholders
- **THEN** el comando continua con el arranque del stack

### Requirement: Recordatorio manual de configuracion de N8N

El comando unico SHALL imprimir, al finalizar con exito, un recordatorio explicito de que el operador debe importar manualmente `n8n/workflow.json` y, en la interfaz de N8N, crear las credenciales IMAP, SMTP, el login del operador y el secreto del webhook de telefonia (ver `docs/n8n-workflow-guide.md`). El recordatorio MUST aclarar que Gemini se configura en el `.env` del backend y no en N8N. El comando MUST NOT intentar importar el workflow de forma automatica.

#### Scenario: Recordatorio presente en la salida exitosa

- **WHEN** el comando termina con exit code cero
- **THEN** la salida incluye el recordatorio de importar `n8n/workflow.json`, de crear las credenciales IMAP, SMTP, el login del operador y el secreto del webhook de telefonia, y aclara que Gemini se configura en el `.env` del backend

#### Scenario: Sin importacion automatica

- **WHEN** el comando arranca el stack
- **THEN** no ejecuta ninguna importacion de `n8n/workflow.json` ni crea workflows en N8N
