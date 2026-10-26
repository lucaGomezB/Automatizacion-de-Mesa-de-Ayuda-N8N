## ADDED Requirements

### Requirement: Producto acotado entre reintentos de transporte del alta y reintentos del proveedor

Los reintentos de transporte del orquestador sobre el alta de incidentes y los reintentos del backend hacia el proveedor semantico son mecanismos distintos y su producto SHALL quedar acotado por valores explicitos y verificables: el maximo de invocaciones pagas por incidente MUST ser a lo sumo `maxTries` del nodo de alta de N8N multiplicado por `gemini_max_retries + 1`. Un intento de alta que encuentra el incidente ya confirmado (replay idempotente) MUST NOT invocar al proveedor pago. La guarda de costo en runtime SHALL seguir reservando el peor caso de cada clasificacion y SHALL seguir actuando como tope global, con independencia de los reintentos del orquestador.

#### Scenario: El producto de reintentos queda acotado y verificable

- **WHEN** una prueba de configuracion lee `maxTries` del nodo de alta en `n8n/workflow.json` y `gemini_max_retries` de la configuracion del backend
- **THEN** el producto `maxTries x (gemini_max_retries + 1)` no supera 9 con los valores vigentes

#### Scenario: Un replay no invoca al proveedor

- **WHEN** un reintento del orquestador llega con un `origen_message_id` cuyo incidente ya esta confirmado
- **THEN** el backend devuelve el incidente existente sin invocar al clasificador ni al proveedor pago

#### Scenario: La guarda de costo sigue siendo el tope global

- **WHEN** la guarda de costo deniega una clasificacion durante un reintento del orquestador
- **THEN** se aplica la degradacion configurada sin invocar al proveedor, igual que en un primer intento
