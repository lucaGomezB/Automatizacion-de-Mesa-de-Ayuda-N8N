## MODIFIED Requirements

### Requirement: Definicion de nodo pago para la guarda de reintentos

El preflight SHALL considerar nodos pagos a los que ejecutan inferencia externa metrada: el nodo de agente `@n8n/n8n-nodes-langchain.agent` y los nodos de modelo de lenguaje cuyo tipo comienza con `@n8n/n8n-nodes-langchain.lm`. La guarda de reintentos SHALL exigir que el nodo de agente declare un reintento ACOTADO y explicito: `retryOnFail` verdadero acompanado de un `maxTries` numerico dentro de un tope configurado y un `waitBetweenTries` numerico no menor a un minimo configurado. La guarda SHALL fallar si un nodo de modelo de lenguaje declara `retryOnFail` o `maxTries`, o si un nodo pago declara `retryOnFail` verdadero sin las cotas explicitas (`maxTries` y `waitBetweenTries`), de modo que jamas quede un reintento pago ilimitado o implicito.

#### Scenario: Ningun nodo pago reintenta

- **WHEN** ningun nodo pago declara un reintento ilimitado o implicito: el nodo de agente, si reintenta, lo hace con `maxTries` dentro del tope y `waitBetweenTries` no menor al minimo, y ningun nodo de modelo declara reintento
- **THEN** la guarda de reintentos pasa

#### Scenario: Reintento pago detectado

- **WHEN** un nodo pago declara `retryOnFail` verdadero sin `maxTries` o sin `waitBetweenTries`, o un nodo de modelo de lenguaje declara `retryOnFail` verdadero o un `maxTries` numerico
- **THEN** la guarda de reintentos falla nombrando el nodo infractor

#### Scenario: Reintento acotado del agente presente

- **WHEN** el nodo de agente declara `retryOnFail` verdadero con `maxTries` dentro del tope y `waitBetweenTries` no menor al minimo
- **THEN** la guarda de reintentos pasa

#### Scenario: Reintento pago fuera del tope detectado

- **WHEN** el nodo de agente declara un `maxTries` que supera el tope configurado
- **THEN** la guarda de reintentos falla, porque el peor caso de invocaciones pagas debe quedar acotado

## ADDED Requirements

### Requirement: Chequeo estatico de la superficie Gemini del workflow

El preflight SHALL verificar, leyendo unicamente artefactos del repositorio, que la superficie Gemini del workflow esta pineada y es resiliente: el nodo de modelo de lenguaje `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` SHALL declarar un `modelName` explicito no vacio, y el nodo `AI Agent` SHALL declarar un reintento acotado (`retryOnFail` verdadero con `maxTries` y `waitBetweenTries` numericos). El chequeo MUST NOT acceder a la red ni requerir credenciales, y MUST NOT imprimir ni requerir la clave de API. Una sonda viva de disponibilidad queda explicitamente FUERA de este chequeo y del pipeline de CI.

#### Scenario: Superficie Gemini pineada y resiliente

- **WHEN** el nodo de modelo declara un `modelName` explicito y el nodo de agente declara un reintento acotado
- **THEN** el chequeo de superficie Gemini pasa

#### Scenario: Modelo implicito detectado

- **WHEN** el nodo de modelo no declara `modelName` o lo declara vacio
- **THEN** el chequeo falla, porque el modelo no debe depender del default implicito del nodo

#### Scenario: Reintento ausente detectado

- **WHEN** el nodo de agente no declara `retryOnFail` verdadero o le faltan `maxTries`/`waitBetweenTries`
- **THEN** el chequeo falla, porque una falla transitoria del modelo abortaria la clasificacion telefonica

#### Scenario: El chequeo no usa red ni clave

- **WHEN** se ejecuta el chequeo de superficie Gemini en el pipeline de CI
- **THEN** el chequeo corre sin acceso a red y sin la clave de API, y no la imprime
