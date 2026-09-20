## Why

La tesis necesita medir la latencia END-TO-END por caso (ingreso del mensaje al sistema -> persistencia confirmada en la base) para alimentar `tiempo_automatizado_s` del corpus y el Capitulo 7. Hoy esa medicion es imposible: el backend no persiste ningun instante de ingreso (`IncidenteCreate` no lo acepta y `Incidente` solo tiene `created_at`/`updated_at`), y N8N genera un `timestamp` en el normalizador pero NUNCA lo envia en el POST. El unico rastro temporal es `created_at`, que no cubre la clasificacion (el costo dominante) y que no sobrevive a updates posteriores como fuente de medicion. Sin un contrato explicito y auditable, los tiempos de la tesis no son reproducibles.

## What Changes

- Nuevo contrato temporal por incidente: `ingresado_en` (instante de ingreso al sistema) y `persistido_en` (instante de persistencia confirmada), con `latencia_e2e_ms` derivada.
- Backend: `IncidenteCreate` acepta `ingresado_en` (ISO-8601 con zona); `Incidente` agrega columnas `ingresado_en` y `persistido_en` via migracion Alembic 006 aditiva; `IncidenteRead` expone ambos instantes y la latencia derivada.
- N8N: el workflow captura `ingresado_en` en el BORDE de cada trigger (en telefonia, antes del `AI Agent`) y lo envia en el body del POST a `/api/v1/incidentes/`.
- Contrato de medicion documentado: definicion exacta de "ingreso" y "persistencia confirmada", unidades (ms), caveats por canal (poller de correo, resumen post-llamada de Twilio) y exclusion de replays idempotentes.
- Delta specs: nueva capacidad `e2e-timing-instrumentation` y ampliacion de `n8n-workflow`.
- Tests: unitarios de schema/servicio, de migracion, y estructurales del workflow N8N.

## Capabilities

### New Capabilities

- `e2e-timing-instrumentation`: contrato de medicion de latencia end-to-end por incidente (instante de ingreso, persistencia confirmada, derivacion de la latencia, validacion del payload, exclusion de replays y caveats por canal).

### Modified Capabilities

- `n8n-workflow`: se agrega la captura del instante de ingreso en el borde de cada trigger y el envio de `ingresado_en` en el body del POST de persistencia.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/schemas/incidente.py` | Modificado | `IncidenteCreate.ingresado_en` + validacion; `IncidenteRead` expone instantes y latencia |
| `App/Backend/app/models/incidente.py` | Modificado | Columnas `ingresado_en` y `persistido_en` (inmutables) |
| `App/Backend/app/services/incidente_service.py` | Modificado | Sella `persistido_en` en la transaccion de alta; preserva replays idempotentes |
| `App/Backend/alembic/versions/006_*.py` | Nuevo | Migracion aditiva de dos columnas TIMESTAMPTZ nullable |
| `n8n/workflow.json` | Modificado | Sello de ingreso por trigger y `ingresado_en` en el body del POST |
| `App/Backend/tests/` | Modificado | Tests de schema, servicio, migracion y estructurales N8N |
| `evaluation/corpus.py` | Sin cambios en este change | Consumidor futuro de `latencia_e2e_ms` -> `tiempo_automatizado_s` |

**Dependencia cruzada**: `c-40-n8n-wiring-fixes` depende de este change porque ambos editan `n8n/workflow.json`. c-39 NO duplica los fixes de cableado de c-40.

**Governance**: ALTA (contrato de datos con migracion que afecta resultados de tesis). Requiere revision humana del design antes de implementar.
