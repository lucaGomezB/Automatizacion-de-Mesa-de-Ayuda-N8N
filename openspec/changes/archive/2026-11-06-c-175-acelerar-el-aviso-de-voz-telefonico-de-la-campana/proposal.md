# Proposal: Acelerar el aviso de voz telefónico de la campaña

## Why

Durante la campaña de telefonía de c-169 el operador escucha el aviso de
privacidad completo en cada una de las 81 llamadas (`render_twiml_allowed`, voz
`Polly.Mia-Neural`). El aviso es exigible por PRIV-003 / Ley 25.326 art. 6: no
puede acortarse ni quitarse, pero su tasa de locución sí puede aumentarse.
Entregar el mismo texto a ~125% reduce el tiempo por llamada sin comprometer la
inteligibilidad.

## What Changes

- `render_twiml_allowed` gana un parámetro opcional `rate`; con valor envuelve el
  contenido del `<Say>` en `<prosody rate="...">`. Sin valor, el TwiML es idéntico
  al actual (tasa normal). El TEXTO no cambia.
- El webhook de voz `POST /api/v1/cost-guard/twilio/voice` lee el parámetro custom
  `tts_rate` y lo pasa a `render_twiml_allowed`, que lo valida/acota a 20–200%.
- El softphone de desarrollo envía `tts_rate="125%"` en las llamadas con caso
  seleccionado (alcance DEV-ONLY): la campaña acelera el aviso sin alterar el aviso
  que reciben los titulares reales en producción.
- **BREAKING**: ninguno.

## Capabilities

### New Capabilities
- `telephony-notice-cadence`: control acotado y seguro de la tasa de locución del
  aviso telefónico (validación/clamp y envoltura `<prosody>`), con tasa normal por
  defecto y texto intacto.

### Modified Capabilities
- `telephony-test-softphone`: el softphone SHALL enviar la tasa de aviso como
  parámetro custom de la llamada cuando haya un caso del corpus seleccionado.

## Impact

- `App/Backend/app/cost_guard/twiml.py` (`render_twiml_allowed`).
- `App/Backend/app/routes/cost_guard.py` (webhook de voz).
- `scripts/voip_softphone/softphone.html` y sus tests.
- `docs/openapi.json` (nuevo campo de formulario del webhook).
- Tests: `test_twiml_record.py`, `test_runtime_cost_guard.py`,
  `scripts/voip_softphone/test_softphone_html.py`.
- Sin cambios en PRIV-003, en el texto del aviso, ni en los atributos/callbacks del
  `<Record>`.

## Scope Decision

Alcance recomendado: **DEV-ONLY (B1, parámetro custom + validación)**. El motor del
change es la campaña; NO se altera el aviso legal que reciben los titulares reales.
Alternativa documentada en `design.md` (D1): alcance PRODUCCIÓN (A), que acelera el
aviso para todos y es más simple, pero cambia la entrega del aviso legal (juicio de
cumplimiento). El autor puede redirigir el alcance; ver D1.

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| El rate inyecta XML | Baja | Validación estricta `^\d{1,3}%$` + clamp 20–200% |
| Se debilita PRIV-003 | Baja | Texto intacto; alcance B no toca producción |
| Deriva de OpenAPI | Media | Regenerar `docs/openapi.json` con el generador canónico |

## Rollback Plan

Revertir el commit del apply restaura el TwiML de producción (tasa normal) y el
softphone sin `tts_rate`. El cambio es aditivo y retrocompatible: sin el parámetro el
comportamiento es el actual.

## Success Criteria

- [ ] `render_twiml_allowed()` sin `rate` produce TwiML idéntico al actual.
- [ ] Con `rate="125%"` el `<Say>` se envuelve en `<prosody rate="125%">` y el texto no cambia.
- [ ] Un `tts_rate` inválido o fuera de rango se ignora o se acota sin romper el XML.
- [ ] El softphone envía `tts_rate` solo con caso seleccionado.
- [ ] `openspec validate --strict` PASS; suites backend y softphone en verde.
