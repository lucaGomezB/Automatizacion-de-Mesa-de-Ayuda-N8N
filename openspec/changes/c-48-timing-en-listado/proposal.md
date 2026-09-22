## Why

C-39 introdujo el contrato temporal end-to-end (`ingresado_en`, `persistido_en`, `latencia_e2e_ms`, `latencia_anomala`) pero lo expuso SOLO en la representacion de detalle (`IncidenteRead`). La proyeccion de listado (`IncidenteListItem`) no incluye ninguno de esos campos, por lo que la tabla del frontend y cualquier consumidor del listado no pueden ver la latencia e2e sin resolver un detalle por cada fila (N+1). Esta es la desviacion #2 de C-39 y bloquea el consumo masivo de la metrica que alimenta `tiempo_automatizado_s`.

## What Changes

- `IncidenteListItem` agrega `ingresado_en` y `persistido_en` (datetimes nullable) y las propiedades derivadas `latencia_e2e_ms` y `latencia_anomala`, espejando `IncidenteRead`.
- La derivacion de la latencia se unifica en funciones puras de modulo reutilizadas por ambos schemas: se elimina la duplicacion de la logica y se garantiza paridad detalle/listado. `IncidenteRead` conserva su comportamiento observable.
- Se regenera `docs/openapi.json` (obligatorio: `test_openapi_sync.py` compara el archivo commiteado contra el esquema en memoria).
- Tests: unitarios de schema para el listado (caso con instantes, caso nulo, caso anomalo, paridad con el detalle) y la verificacion de sincronia OpenAPI.
- Delta spec sobre `e2e-timing-instrumentation`: la latencia y los instantes fuente SHALL exponerse en AMBAS representaciones de lectura, no solo en el detalle.

No hay migracion de base de datos, no se toca N8N, no cambia la logica de negocio ni la politica de clasificacion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `e2e-timing-instrumentation`: el requisito de derivacion de la latencia e2e se amplia para exigir que los dos instantes fuente y la latencia derivada se expongan tambien en la proyeccion de listado (`IncidenteListItem`), con la misma derivacion que el detalle; la politica de latencia negativa se amplia para que la marca de anomalia sea visible en la proyeccion de listado.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/schemas/incidente.py` | Modificado | `IncidenteListItem` gana instantes + propiedades derivadas; se extraen funciones puras compartidas de derivacion |
| `App/Backend/app/repositories/incidente_repository.py` | Sin cambios | `list_filtered` ya selecciona la entidad completa y sus `selectinload`; las columnas temporales ya viajan en el ORM |
| `App/Backend/app/routes/incidentes.py` | Sin cambios | `IncidenteListItem.model_validate(i)` ya construye el item desde el ORM |
| `docs/openapi.json` | Modificado | Regenerado con `python scripts/export_openapi.py`; el schema `IncidenteListItem` incorpora los 4 campos |
| `App/Backend/tests/` | Modificado | Tests de schema del listado (incluye paridad con detalle) y sincronia OpenAPI |
| `App/Backend/alembic/` | Sin cambios | No hay cambio de columnas; `ingresado_en`/`persistido_en` ya existen (migracion 006 de C-39) |
| `n8n/workflow.json` | Sin cambios | El canal no interviene en la serializacion de lectura |
| `App/Frontend/src/types/incidente.ts` | Fuera de alcance | El contrato del backend queda disponible; el espejo TS y el render de la columna se difieren (ver Non-Goals del design) |

**Governance**: MEDIA. Contrato de lectura aditivo, sin migracion, sin n8n y sin logica de servicio. El cambio de mayor riesgo es la extraccion de la derivacion compartida en `IncidenteRead`, que se cubre con red de seguridad sobre los tests existentes de C-39.

**Dependencias**: ninguna. `c-52-telefonia-transcripcion-async` esta activo pero no toca estos archivos.