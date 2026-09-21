## Why

Una auditoría de solo lectura confirmó que NO existe ningún tope de gasto, rate ni quota en runtime. El único control es el preflight ESTÁTICO (`scripts/preflight/cost_readiness.py`), que verifica cableado pero NO limita el gasto ni corre por petición. Activado el workflow con credenciales reales, las llamadas pagas se disparan solas: Gemini en el backend (`HybridClassifier`), el `AI Agent` de n8n y la transcripción de Twilio por llamada. Nada las intercepta. Es el riesgo real de pérdida de dinero.

## What Changes

- Guarda de costo en RUNTIME con una bolsa GLOBAL compartida de USD 10/semana entre las TRES superficies pagas (Gemini backend, Gemini n8n, transcripción Twilio), convertida a un costo unitario USD por superficie.
- Rate limit por número de origen (llamadas por teléfono del llamador) además del presupuesto global.
- Enforcement REAL de Twilio mediante un webhook de voz PRE-llamada (TwiML) que permite `<Record transcribe="true">` o rechaza con `<Say>` + `<Hangup>`.
- Enforcement del `AI Agent` de n8n con un nodo de guarda antes de invocarlo (cambio en `workflow.json`).
- Almacén de contadores en PostgreSQL (tabla nueva + migración Alembic `007`); fail-closed con notificación estructurada ante almacén no disponible.
- Degradación segura resuelta: determinístico + revisión humana, sin invocar al proveedor pago.
- Registro del número de origen CRUDO para atribución anti-abuso, acotado a la guarda y explícitamente fuera del corpus de evaluación.
- Defaults seguros y explícitos: guarda HABILITADA conservadora con override por `.env`.
- Guarda unit-testeable offline con fakes; CI/dev offline y sin costo.

## Capabilities

### New Capabilities

- `runtime-cost-guard`: enforcement en runtime del gasto pago de las tres superficies (presupuesto global compartido, costo unitario por superficie, rate global y por origen, webhook pre-llamada de Twilio, guarda de n8n, fail-closed con notificación, degradación segura, observabilidad, defaults seguros), testeable offline.

### Modified Capabilities

None. `cost-readiness` permanece acotada al preflight estático y al tope de ejecución N8N; no se modifica ningún requisito existente ni se duplica esa guarda.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `App/Backend/app/cost_guard/` (nueva guarda) | New | Decisión pura, protocolos, fake y adaptador PostgreSQL |
| `App/Backend/app/models/` + `alembic/versions/007_cost_guard_counters.py` | New | Tabla `costo_guarda_contador`; migración 007 (down_revision 006) |
| `App/Backend/app/services/incidente_service.py` | Modified | Enforcement antes de invocar Gemini |
| `App/Backend/app/classifiers/hybrid.py` | Modified | Manejo de `CostGuardTrippedError` y degradación |
| `App/Backend/app/config/settings.py` + `.env.example` | Modified | Presupuesto, ventana, costos unitarios, tasas y políticas |
| `App/Backend/app/routes/` (endpoints de guarda) | New | Webhook pre-llamada de Twilio y endpoint de reserva para n8n |
| `n8n/workflow.json` | Modified | Nodo de guarda + IF antes del `AI Agent` |
| `n8n/twilio/twiml.xml` | Modified | Grabación servida por el webhook pre-llamada |
| `App/Backend/tests/` | New | Tests offline de la guarda + subconjunto integration PostgreSQL |
| `README.md`, `docs/operational-guide.md` | Modified | Variables, postura, degradación, fail-closed y webhook |
| Preflight estático, `evaluation/` | Out of scope | Sin cambios; el corpus NO incorpora el caller crudo |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Monto/ventana mal elegidos bloquean operación legítima | Med | Configurable; default conservador USD 10/semana; override por `.env` |
| Store PostgreSQL caído descontrola el gasto | Low | Fail-closed con notificación; degrada a determinístico + revisión humana |
| Costo unitario estimado no refleja el precio real | Med | Es un tope, no contabilidad exacta; configurable y documentado como estimación |
| Endpoint de Twilio público abusado | Med | Validación de firma/secreto; rate por origen; fail-closed |
| El evento call-summary no trae caller o transcripción | Med | Caller opcional (la bolsa global aplica igual); campo de transcripción marcado NO verificado |
| Registrar el caller crudo roza la privacidad | Low | Aceptado explícitamente; acotado a la guarda; fuera del corpus; retención por ventana |
| Tests acoplados a PostgreSQL/Gemini reales | Low | Fakes inyectables; subconjunto integration con base descartable; CI/dev offline |

## Rollback Plan

`alembic downgrade 006` dropea la tabla de contadores (efímera; sin datos de negocio que restaurar). Revertir el commit de la guarda, la configuración, los endpoints, `workflow.json` y `twiml.xml`. Deshabilitar la guarda por configuración (`cost_guard_enabled=False`) es el rollback operativo inmediato.

## Success Criteria

- [ ] La guarda limita el gasto pago con una bolsa global USD/semana compartida por las tres superficies, con costo unitario por superficie.
- [ ] La guarda aplica un rate limit global y uno por número de origen.
- [ ] El webhook pre-llamada de Twilio permite o rechaza la grabación con transcripción según la guarda.
- [ ] El `AI Agent` de n8n no se invoca cuando la guarda deniega.
- [ ] Ante almacén no disponible, la guarda aplica fail-closed, degrada sin invocar al proveedor pago y emite la notificación estructurada.
- [ ] El número de origen crudo se registra en la guarda y NO entra al corpus de evaluación.
- [ ] Al excederse, la guarda degrada sin invocar el proveedor pago y emite log estructurado.
- [ ] Tests offline con fakes cubren ventana, costos unitarios, tasas, fail-closed, degradación y bypass.
- [ ] `openspec validate --strict --changes c-45-runtime-cost-guard` pasa.
