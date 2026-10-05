# Delta for n8n-workflow

## ADDED Requirements

### Requirement: N8N-WEB-DEDUP-001 — El normalizador construye `origen_message_id` para el canal web

El nodo "Normalizar entrada del incidente" SHALL construir un `origen_message_id` no nulo para el canal web, en lugar de forzar `null`. La construccion SHALL aplicar esta precedencia:

1. Un identificador explicito provisto por el llamador en el body del webhook (`body.origen_message_id` o un `case_id` del que se derive `corpus-<case_id>`), si viene no vacio.
2. Un identificador generado por el workflow, unico por envio, derivado de la ejecucion (por ejemplo `web-<execution.id>-<timestamp>`), cuando el llamador no provee uno. Este camino cubre al formulario web real, que MUST NOT requerir cambios de cliente. Como la base de generacion es unica por ejecucion, dos envios web legitimos distintos MUST NOT compartir identificador.

N8N es la fuente PRIMARIA del identificador web; un default UUID del backend es opcional y secundario (nunca reemplaza a N8N como fuente primaria). El formulario web real MUST NOT enviar un identificador (OQ-C): es N8N quien lo genera, por lo que NO se requiere cambio alguno en el frontend.

La rama de correo (Message-ID/UID del header) y la rama de telefonia (CallSid del handoff) SHALL permanecer sin cambios. El body del nodo HTTP de persistencia SHALL enviar el `origen_message_id` resultante (no nulo para web), de modo que la restriccion unica del backend deduplique el canal web igual que correo y telefonia.

#### Scenario: El llamador provee un identificador deterministico para web

- **WHEN** el webhook web recibe un body con `origen_message_id = "corpus-R001"`
- **THEN** la estructura normalizada tiene `canal_origen = "web"` y `origen_message_id = "corpus-R001"`, y el POST lo envia al backend

#### Scenario: El formulario real sin id recibe uno generado unico

- **WHEN** el webhook web recibe un envio del formulario real sin `origen_message_id`
- **THEN** la estructura normalizada tiene un `origen_message_id` no nulo generado por el workflow y unico por ejecucion, y dos envios distintos NO comparten el identificador

#### Scenario: La rama de correo no cambia

- **WHEN** una entrada del canal correo atraviesa el nodo de normalizacion
- **THEN** el `origen_message_id` sigue proviniendo del `Message-ID` del header o del UID de fallback, sin cambios respecto del comportamiento previo

#### Scenario: La rama de telefonia no cambia

- **WHEN** una entrada del canal telefonia atraviesa el nodo de normalizacion
- **THEN** el `origen_message_id` sigue proviniendo del `CallSid` del handoff, sin cambios respecto del comportamiento previo

#### Scenario: El POST web envia el identificador

- **WHEN** se inspecciona el body del nodo HTTP de persistencia para una entrada web
- **THEN** la expresion de `origen_message_id` resuelve al identificador construido (no a `null`) y no queda forzada a `null` por el ternario del canal
