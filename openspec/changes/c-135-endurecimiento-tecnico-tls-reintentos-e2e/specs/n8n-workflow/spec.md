## ADDED Requirements

### Requirement: N8N-RETRY-001 — Reintento acotado e idempotente del tramo de alta hacia el backend

Los dos nodos HTTP del tramo de alta que invocan al backend, `Login operador` (`POST /api/v1/auth/login`) y `HTTP POST a MESA-AYUDAS` (`POST /api/v1/incidentes/`), SHALL declarar un reintento explicito y acotado con los parametros nativos de N8N: `retryOnFail: true`, `maxTries` entre 2 y 3, `waitBetweenTries` entre 1000 y 5000 milisegundos y un tiempo maximo por intento explicito en `parameters.options.timeout`. El presupuesto de peor caso de cada nodo, definido como `maxTries x timeout + (maxTries - 1) x waitBetweenTries`, sumado sobre ambos nodos, MUST ser menor que el `EXECUTIONS_TIMEOUT` del servicio `n8n` en `docker-compose.yml`, de modo que la rama de error siga siendo alcanzable antes de que el tope global cancele la ejecucion. El `timeout` del nodo de alta MUST ser mayor que el presupuesto total de clasificacion del backend (`gemini_total_timeout_seconds`), para que una clasificacion lenta pero valida no dispare un reintento. El nodo de alta MUST conservar `onError: continueErrorOutput` con su salida de error cableada a `Es correo?` y a `Registro de auditoria`, como camino terminal tras agotar los intentos. El cuerpo del alta MUST tomar `origen_message_id` de la salida de `Normalizar entrada del incidente`, de modo que todos los intentos de una misma ejecucion envien la misma clave de idempotencia. La politica MUST implementarse sin agregar nodos: el workflow conserva 32 nodos totales y 29 operativos.

#### Scenario: Ambos nodos declaran el reintento acotado

- **WHEN** la suite estructural inspecciona `Login operador` y `HTTP POST a MESA-AYUDAS` en `n8n/workflow.json`
- **THEN** cada uno declara `retryOnFail: true`, `maxTries` entre 2 y 3, `waitBetweenTries` entre 1000 y 5000 y un `parameters.options.timeout` numerico positivo

#### Scenario: El presupuesto de peor caso cabe en el tope de ejecucion

- **WHEN** la suite calcula `maxTries x timeout + (maxTries - 1) x waitBetweenTries` para ambos nodos y suma los resultados
- **THEN** la suma es menor que `EXECUTIONS_TIMEOUT` del servicio `n8n` leido de `docker-compose.yml`

#### Scenario: El timeout del alta supera el presupuesto de clasificacion del backend

- **WHEN** la suite compara el `timeout` del nodo de alta con `gemini_total_timeout_seconds` de la configuracion del backend
- **THEN** el `timeout` del nodo de alta, expresado en segundos, es estrictamente mayor

#### Scenario: Agotados los intentos se conserva el camino de error

- **WHEN** todos los intentos del nodo de alta fallan
- **THEN** la ejecucion continua por la salida de error del nodo, que alcanza `Es correo?` y `Registro de auditoria`, y la auditoria no registra el resultado como `creado`

#### Scenario: Todos los intentos envian la misma clave de idempotencia

- **WHEN** se inspecciona la expresion de `origen_message_id` en el cuerpo del nodo de alta
- **THEN** referencia la salida de `Normalizar entrada del incidente`, calculada una sola vez por ejecucion, y no un valor generado dentro del propio nodo

#### Scenario: Sin nodos nuevos

- **WHEN** se cuentan los nodos de `n8n/workflow.json` tras aplicar la politica
- **THEN** hay 32 nodos totales, 3 notas adhesivas y 29 nodos operativos

### Requirement: N8N-DOC-007 — La guia del workflow documenta la politica de reintento

`docs/n8n-workflow-guide.md` SHALL documentar la politica de reintento del tramo de alta de forma coherente con `n8n/workflow.json`: los nodos alcanzados, los valores de `maxTries`, `waitBetweenTries` y `timeout`, el presupuesto de peor caso frente a `EXECUTIONS_TIMEOUT`, el comportamiento tras agotar los intentos, la clave de idempotencia que hace seguro el reintento y el efecto de reintentar respuestas 4xx del login sobre el bloqueo por cuenta. La guia MUST NOT describir la espera fija de N8N como retroceso exponencial y SHALL indicar que el workflow debe reimportarse en la instancia operativa para que la politica tenga efecto.

#### Scenario: La guia refleja los valores del JSON

- **WHEN** se comparan los valores de reintento declarados en la guia con los de `n8n/workflow.json`
- **THEN** coinciden para ambos nodos

#### Scenario: La guia no afirma retroceso exponencial en N8N

- **WHEN** se lee la seccion de reintentos de la guia
- **THEN** describe una espera fija entre intentos y no un retroceso exponencial

#### Scenario: La guia advierte la reimportacion

- **WHEN** un operador consulta la guia para actualizar la instancia
- **THEN** encuentra que la politica solo rige despues de reimportar `n8n/workflow.json` y verificar las credenciales del login
