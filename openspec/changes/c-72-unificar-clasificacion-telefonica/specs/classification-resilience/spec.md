# Delta for classification-resilience

## MODIFIED Requirements

### Requirement: Resiliencia del canal telefonico ante fallas transitorias del modelo

La resiliencia del canal telefonico SHALL resolverse en la cascada del backend, no en un modelo de lenguaje de n8n. Una falla transitoria del proveedor semantico durante la clasificacion de un incidente telefonico SHALL reintentarse de forma acotada segun los parametros de resiliencia vigentes del backend y, al agotarse, SHALL aplicar el fallback con `requiere_revision_humana=true` y `confianza=0.0`, sin abortar la clasificacion ni propagar la excepcion. El canal telefonico MUST NOT depender de un tope de refinamiento de un agente pago de n8n para su clasificacion. Cualquier invocacion a un modelo dentro de n8n que se conserve para un rol reducido (OQ1) MUST quedar explicitamente acotada y MUST NOT determinar el sector persistido del incidente. Los refinamientos por respuesta invalida y los reintentos de transporte son mecanismos distintos y su producto MUST quedar acotado.

#### Scenario: Una falla transitoria del modelo no aborta la clasificacion telefonica

- **WHEN** el proveedor semantico del backend falla de forma transitoria durante la clasificacion de una llamada
- **THEN** el backend reintenta de forma acotada segun sus parametros vigentes y, si un intento tiene exito, continua la clasificacion normal del incidente

#### Scenario: El tope total de invocaciones pagas queda acotado

- **WHEN** se inspecciona la clasificacion telefonica y cualquier rol reducido de modelo conservado en n8n
- **THEN** la cantidad maxima de invocaciones pagas por incidente queda acotada por valores explicitos y verificables

#### Scenario: Agotado el reintento de transporte se conserva un camino terminal

- **WHEN** todos los intentos de transporte fallan de forma persistente
- **THEN** el flujo conserva un camino terminal que persiste el incidente con `requiere_revision_humana=true` y `confianza=0.0`, sin reejecutar indefinidamente la invocacion paga

## ADDED Requirements

### Requirement: Clasificacion telefonica determinista-primero

El canal telefonico SHALL beneficiarse del mismo pipeline que los canales correo y web: la etapa determinista se ejecuta primero sobre la descripcion pseudonimizada y, si alcanza la confianza calibrada, SHALL cortocircuitar la etapa semantica paga. Si el determinista no alcanza la confianza o senala ausencia de prediccion o ambiguedad, el pipeline SHALL escalar a la etapa semantica conforme al comportamiento vigente. Cuando la cascada escala para un incidente telefonico, la operacion paga SHALL quedar sujeta a la guarda de costo vigente del backend. El comportamiento SHALL ser identico al de correo y web.

#### Scenario: El cortocircuito determinista evita la llamada paga en telefonia

- **WHEN** la etapa determinista alcanza la confianza calibrada sobre la descripcion pseudonimizada de un incidente telefonico
- **THEN** el pipeline omite la etapa semantica paga y persiste el resultado determinista

#### Scenario: La escalacion de telefonia queda sujeta a la guarda

- **WHEN** la etapa determinista no alcanza la confianza para un incidente telefonico y el pipeline escala
- **THEN** la operacion paga se reserva contra la superficie del backend conforme a la guarda vigente

#### Scenario: El pipeline telefonico es el mismo que correo y web

- **WHEN** se comparan los pasos de clasificacion de los tres canales
- **THEN** los tres usan la etapa determinista primero, la etapa semantica como escalamiento y el fallback con revision humana
