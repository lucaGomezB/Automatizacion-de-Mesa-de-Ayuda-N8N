# Design: Acelerar el aviso de voz telefónico de la campaña

## Context

Ver `proposal.md` para la motivación. Estado actual relevante:

- `App/Backend/app/cost_guard/twiml.py::render_twiml_allowed` emite texto TwiML
  estático (sin interpolación) con un `<Say voice="Polly.Mia-Neural"
  language="es-US">` que precede al `<Record>` (PRIV-003).
- `App/Backend/app/routes/cost_guard.py::twilio_voice_webhook` recibe el webhook de
  voz de Twilio y ya lee un parámetro custom `corpus_case_id` (c-70/D2), patrón que
  reutilizamos para `tts_rate`.
- `scripts/voip_softphone/softphone.html` coloca la llamada con
  `device.connect({ params: { corpus_case_id: selected } })` cuando hay caso, y con
  `device.connect()` cuando no lo hay.
- Hechos verificados (Twilio/Amazon Polly, no re-verificados aquí): la voz
  `Polly.Mia-Neural` es NEURAL y soporta el atributo `rate` (no `pitch`); `<Say>`
  procesa SSML para voces no Basic; `rate` acepta un porcentaje 20–200% (100% =
  normal). `125%` = 25% más rápido, cambio leve compatible con el deber de
  información "expresa y clara" (Ley 25.326 art. 6). El texto del aviso es corto y
  muy por debajo del tope de 3.000 caracteres de `<Say>`, de modo que no hay riesgo
  de truncamiento.
- Los escenarios de PRIV-003 verifican el TEXTO del `<Say>`; la envoltura
  `<prosody>` no lo altera (`root.find("Say")` e `itertext()` siguen funcionando).

## Goals / Non-Goals

**Goals:**
- Entregar el aviso a ~125% sin tocar el texto, para reducir el tiempo por llamada.
- Mantener el aviso de PRODUCCIÓN intacto (sin acelerar a titulares reales).
- Validación/acotamiento del rate como frontera de seguridad del XML.

**Non-Goals:**
- Cambiar el texto del aviso o PRIV-003.
- Tocar los atributos/callbacks del `<Record>` o el flujo de la guarda de costo.
- Acelerar el `<Say>` de cierre (`render_twiml_record_complete`) ni el denegado.

## Decisions

### D1 — Alcance: DEV-ONLY (B1) frente a PRODUCCIÓN (A) [DECISIÓN REDIRIGIBLE]

Elegimos **DEV-ONLY (B1)**: el rate llega como parámetro custom `tts_rate` desde el
softphone y solo las llamadas de la campaña se aceleran. Producción (llamadas PSTN
reales) no envía el parámetro y recibe el aviso a tasa normal, byte-idéntico al
vigente.

Racional: el motor del change es la campaña de c-169; acelerar el aviso legal para
TODOS los titulares sería una decisión de cumplimiento que no hace falta tomar para
el objetivo. B1 es además verificable in-code y no depende de configuración externa
de Twilio.

Alternativas consideradas:
- **(A) PRODUCCIÓN**: envolver siempre el aviso en `<prosody rate="125%">` para
  todos. Ventaja: un solo cambio en `render_twiml_allowed`, el softphone queda
  idéntico a producción. Desventaja: altera la entrega del aviso legal a sujetos
  reales (juicio de cumplimiento). Es el fallback si el autor quiere acelerar a
  todos: se elimina la tarea del softphone y el delta de `telephony-test-softphone`,
  y el default de `render_twiml_allowed` pasa a 125%; el resto del diseño se mantiene.
- **(B2) Endpoint/Voice URL de desarrollo separado**: descartado, agrega una segunda
  URL y configuración de Twilio, mayor superficie y mantenimiento que un parámetro.
- **(B3) Query param en la Voice URL del TwiML App**: descartado, no distingue por
  origen/llamada y también afectaría llamadas reales si se reutiliza la app.

El autor puede redirigir el alcance cambiando D1; las tareas y deltas de este change
están escritos para B1.

### D2 — Validación y acotamiento centralizados en el módulo TwiML

`render_twiml_allowed(rate=None)` normaliza el valor con un helper privado:

- `rate` ausente o `None` → sin `<prosody>` (tasa normal; salida byte-idéntica).
- Formato válido solo si matchea `^\d{1,3}%$` (se admite `%` y dígitos, con trim).
- Fuera de 20–200 → clamp al límite más cercano.
- Formato inválido → se ignora (tasa normal).

Racional: la frontera de seguridad es el documento XML; centralizar ahí la
validación garantiza un único punto de escape y evita re-validaciones divergentes.
El webhook pasa el valor crudo sin interpolar (el valor nunca se concatena al texto
del aviso, solo al atributo `rate` ya saneado).

Solo se acepta la forma porcentual (no valores nombrados `slow`/`fast`): da control
explícito y un rango numérico acotable trivialmente. El canal `rate` numérico cubre
el objetivo (125%).

### D3 — Default byte-idéntico para no romper producción ni los tests

Sin `rate`, `render_twiml_allowed()` NO emite `<prosody>`: la salida es exactamente la
actual. Esto preserva PRIV-003, el comportamiento de producción y los tests
existentes (que comparan texto vía `itertext()` y atributos del `<Record>`).

### D4 — El softphone envía `tts_rate` solo con caso seleccionado

Se extiende la rama con caso a
`device.connect({ params: { corpus_case_id: selected, tts_rate: TTS_RATE } })`
(`TTS_RATE = "125%"`), y la rama sin caso se mantiene como `device.connect()`.
Racional: la campaña siempre opera con un caso; el modo de desarrollo sin caso queda
intacto y retrocompatible, y la constante vive en un único lugar de la página.

### D5 — Sincronización de OpenAPI

El nuevo campo de formulario `tts_rate` cambia el OpenAPI del webhook. Hay que
regenerar `docs/openapi.json` con el generador canónico
(`cd App/Backend; python scripts/export_openapi.py`) y confirmar
`tests/test_openapi_sync.py`.

## Risks / Trade-offs

- [El rate inyecta XML] → D2: validación estricta por regex + clamp; el valor nunca
  se interpola en el texto.
- [Se debilita PRIV-003 por acelerar el aviso] → D1: alcance B no toca producción;
  D3: default sin prosody; el texto es idéntico.
- [Deriva de `docs/openapi.json`] → D5: regenerar con el generador canónico y correr
  el test de sincronización.
- [El softphone pasa de `device.connect()` a parámetros] → D4 mantiene `device.connect()`
  en la rama sin caso y se actualiza la aserción literal del caso (comportamiento
  preservado para `corpus_case_id`).

## Migration Plan

Cambio aditivo; no requiere migración de datos ni de esquema. Despliegue normal del
backend. Rollback: revertir el commit revierte TwiML y softphone al estado previo
(sin parámetro, tasa normal).

## Open Questions

- Ninguna que condicione specs, alcance o tareas. La única decisión redirigible es D1
  (A vs B); su alternativa está documentada y su resolución no cambia el mecanismo de
  validación (D2) ni la envoltura `<prosody>`.
