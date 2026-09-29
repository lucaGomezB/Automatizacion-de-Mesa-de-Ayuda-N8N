## MODIFIED Requirements

### Requirement: N8N-REFINE-001 — Tope de refinamiento del agente pago

El canal telefonico SHALL limitar a un maximo de 2 el numero de intentos de clasificacion/refinamiento del `AI Agent`. El workflow SHALL contabilizar los intentos y, al agotarse el tope sin una clasificacion valida, SHALL derivar el incidente a un nodo terminal que lo persiste con `requiere_revision_humana=true` y `confianza=0.0`, MUST NOT volver a invocar al agente pago. El refinamiento dentro del tope SHALL conservarse. Ademas, el nodo `AI Agent` SHALL declarar un reintento acotado ante fallas transitorias del modelo de lenguaje (`retryOnFail` verdadero, con `maxTries` y `waitBetweenTries` explicitos y acotados), de modo que una indisponibilidad momentanea del modelo NO aborte la clasificacion telefonica. Los reintentos de transporte y los refinamientos por respuesta invalida son mecanismos distintos: un reintento de transporte MUST NOT consumir un intento de refinamiento, y la cantidad maxima de invocaciones pagas por incidente telefonico queda acotada por el producto entre los intentos de transporte y los intentos de refinamiento, ambos explicitos en el workflow exportado.

#### Scenario: Un fallo dentro del tope reintenta una vez

- **WHEN** la validacion de la respuesta del agente falla en el primer intento y el tope aun no se agoto
- **THEN** el flujo reingresa al `AI Agent` para un unico intento adicional

#### Scenario: Al agotar el tope no se reinvoca al agente pago

- **WHEN** el refinamiento alcanza el tope de 2 intentos sin una clasificacion valida
- **THEN** el flujo NO reingresa al `AI Agent`, persiste el incidente con `requiere_revision_humana=true` y termina

#### Scenario: Clasificacion valida dentro del tope sigue el flujo normal

- **WHEN** el agente produce una clasificacion valida dentro del tope
- **THEN** el flujo continua hacia la normalizacion y el ruteo por umbral como hasta ahora

#### Scenario: El tope es verificable en el workflow exportado

- **WHEN** la suite estructural inspecciona el nodo `AI Agent` y sus conexiones de refinamiento
- **THEN** existe un tope explicito de intentos (por ejemplo `maxIterations` o un contador) y una ruta terminal que no reinvoca al agente

#### Scenario: Una falla transitoria del modelo se reintenta sin consumir refinamiento

- **WHEN** el modelo de lenguaje del agente falla de forma transitoria en el primer intento de transporte
- **THEN** el workflow reintenta la invocacion del agente segun su `maxTries` declarado, y ese reintento de transporte no cuenta como intento de refinamiento por respuesta invalida

#### Scenario: El reintento de transporte esta acotado y es explicito

- **WHEN** la suite estructural inspecciona el nodo `AI Agent`
- **THEN** el nodo declara `retryOnFail` verdadero con `maxTries` y `waitBetweenTries` numericos y acotados, de modo que el peor caso de invocaciones pagas por incidente es finito y verificable

### Requirement: Acoplamiento del AI Agent a su modelo de lenguaje y al payload del trigger

Cada nodo `@n8n/n8n-nodes-langchain.agent` SHALL tener una conexión entrante de tipo `ai_languageModel` desde un nodo de modelo de lenguaje. El nodo de modelo de lenguaje del agente SHALL declarar un modelo EXPLÍCITO (`modelName`) y NO SHALL depender del modelo por defecto del nodo. El `modelName` declarado SHALL ser igual al modelo configurado del backend (`settings.gemini_model`), de modo que la clasificación de n8n y la del backend no diverja por un default implícito. El prompt del agente SHALL interpolar el payload recibido del trigger (por ejemplo `$json` o `$input`), de modo que el contenido de la llamada o del correo sea la entrada efectiva del agente.

#### Scenario: El agente tiene conexión ai_languageModel

- **WHEN** la suite de pruebas inspecciona las conexiones del workflow
- **THEN** cada nodo agente tiene al menos una conexión de tipo `ai_languageModel`
- **AND** el nodo origen de esa conexión es un nodo de modelo de lenguaje

#### Scenario: El prompt interpola el payload del trigger

- **WHEN** la suite de pruebas inspecciona el texto (`text` o `prompt`) del nodo agente
- **THEN** el texto contiene una expresión que referencia el payload de entrada del trigger (`$json` o `$input`)
- **AND** el prompt no es un texto estático sin datos del incidente

#### Scenario: El modelo del agente es explícito y en paridad con el backend

- **WHEN** la suite de pruebas compara el `modelName` del nodo de modelo de lenguaje con el modelo configurado del backend
- **THEN** el nodo declara un `modelName` no vacío y ambos valores coinciden, sin depender del default implícito del nodo
