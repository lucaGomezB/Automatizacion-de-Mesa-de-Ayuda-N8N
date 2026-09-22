## Context

Ver `proposal.md` — Why. Este change es una desviacion de C-39 y no introduce arquitectura nueva: expone en la proyeccion de listado un contrato temporal que ya existe en el detalle. Estado verificado del codigo:

- `IncidenteRead` (`App/Backend/app/schemas/incidente.py:227-291`) declara `ingresado_en: datetime | None = None`, `persistido_en: datetime | None = None` y las propiedades `@computed_field` `latencia_e2e_ms` y `latencia_anomala`, ambas apoyadas en `_to_utc` (lineas 34-45).
- `IncidenteListItem` (`App/Backend/app/schemas/incidente.py:294-310`) declara solo `id`, `prioridad`, `requiere_revision_humana`, `created_at`, `sector`, `estado`, con `model_config = ConfigDict(from_attributes=True)`.
- `list_filtered` (`App/Backend/app/repositories/incidente_repository.py`) usa `select(Incidente)` (entidad completa) con `selectinload`: los objetos ORM del listado YA cargan `ingresado_en` y `persistido_en`. No hay `defer` ni proyeccion de columnas.
- `App/Backend/app/routes/incidentes.py:137` construye los items con `[IncidenteListItem.model_validate(i) for i in incidentes]`.
- `test_openapi_sync.py` compara `docs/openapi.json` contra `app.openapi()` en memoria; agregar campos al schema rompe el test hasta regenerar el archivo. Comando: `cd App/Backend && python scripts/export_openapi.py`.

## Goals / Non-Goals

**Goals:**

- Exponer `ingresado_en`, `persistido_en`, `latencia_e2e_ms` y `latencia_anomala` en `IncidenteListItem`, con paridad exacta respecto de `IncidenteRead`.
- Unificar la derivacion de la latencia en un unico punto reutilizable, eliminando la duplicacion de la logica entre ambos schemas.
- Mantener el esquema OpenAPI estatico sincronizado con la app.

**Non-Goals:**

- No cambiar la forma de las filas ni la consulta del listado (no se agregan columnas, joins ni `selectinload`).
- No cambiar `IncidenteRead` en su comportamiento observable; la refactorizacion es interna y preserva salida.
- No tocar N8N, migraciones Alembic, servicios, clasificador ni umbral de confianza.
- No actualizar el espejo TypeScript del frontend (`App/Frontend/src/types/incidente.ts`) ni renderizar la latencia en la tabla: el contrato del backend queda disponible y su consumo de UI se difiere a un change de frontend.
- No agregar paginacion, filtros ni indices.

## Decisions

### D1: Extraer la derivacion a funciones puras de modulo y reutilizarla en ambos schemas

Se extraen dos funciones puras a nivel de modulo en `app/schemas/incidente.py`:

- `_derivar_latencia_e2e_ms(ingresado_en, persistido_en) -> int | None`
- `_es_latencia_anomala(ingresado_en, persistido_en) -> bool`

Cada `@computed_field` de `IncidenteRead` e `IncidenteListItem` delega en ellas. La logica de derivacion (normalizar con `_to_utc`, tratar negativos como nulos, marcar anomalia) queda escrita una sola vez.

- Alternativa considerada: copiar las cuatro lineas de la propiedad en `IncidenteListItem`. Se descarta porque crea dos fuentes de verdad que pueden divergir; la spec exige paridad al milisegundo.
- Alternativa considerada: mover campos y computeds a un mixin `BaseModel` compartido. Se descarta porque cambia la MRO de `IncidenteRead` y agrega superficie de riesgo en un schema ya verificado, sin beneficio frente a funciones puras mas declaraciones explicitas.

### D2: `IncidenteListItem` declara los cuatro campos explicitamente, con los mismos defaults nullable

`ingresado_en: datetime | None = None`, `persistido_en: datetime | None = None`, mas `@computed_field latencia_e2e_ms` y `@computed_field latencia_anomala`. Los defaults preservan compatibilidad con consumidores y filas legacy sin instantes. `model_config = ConfigDict(from_attributes=True)` se mantiene: la lectura desde ORM no cambia.

- Alternativa considerada: exponer solo `latencia_e2e_ms` y omitir `latencia_anomala`. Se descarta: sin la marca, el listado no puede distinguir "sin datos" de "dato anomalo"; la spec de politica negativa exige que la marca sea observable donde se expone la latencia.

### D3: Sin cambios en repositorio ni en la ruta

El repositorio ya selecciona la entidad completa y la ruta ya valida desde atributos. El cambio es puramente de schema. Se agrega un test de no-regresion que verifique que el listado real (seam en memoria) devuelve los campos temporales no nulos para un incidente con instantes, de modo que una futura proyeccion de columnas que omita los instantes rompa el test.

- Alternativa considerada: cambiar `list_filtered` a una proyeccion de columnas mas liviana. Se descarta: contradice el objetivo de eficiencia solo marginalmente y obliga a reescribir el mapeo; fuera de alcance.

### D4: Regenerar `docs/openapi.json` como parte del cambio

`test_openapi_sync.py::test_openapi_in_sync_with_app` compara el archivo commiteado con el esquema en memoria. El cambio no esta completo sin regenerar. Se usa el script versionado `App/Backend/scripts/export_openapi.py`, que inyecta env dummies y escribe con `indent=2, sort_keys=True`.

- Alternativa considerada: editar el JSON a mano. Se descarta: el orden de claves y la serializacion deben coincidir bit a bit con la salida del script.

### D5: Frontera con el frontend

El cambio entrega el contrato backend del listado. El espejo `IncidenteListItem` de TypeScript y el render de la latencia en `TicketsTable` quedan fuera. Razones: (1) el scope pedido es backend + openapi; (2) el render de la columna implica decisiones de UX (formato de duracion, tooltip de anomalia) que merecen su propio change; (3) `npm run build` esta desaconsejado como paso de verificacion en este flujo. Se registra como consumidor futuro.

## Risks / Trade-offs

- [La extraccion de la derivacion cambia `IncidenteRead`] -> La refactorizacion es preservadora de comportamiento y la red de seguridad son los tests existentes de C-39 sobre `IncidenteRead`; se corren antes de tocar el archivo.
- [El listado crece en payload] -> Cuatro campos escalares por item; despreciable frente al texto de descripcion que el listado ya omite. Sin cambios de performance.
- [Deriva entre la logica del detalle y la del listado] -> Funciones puras compartidas (D1) + escenario de paridad detalle/listado en la spec + test unitario de paridad.
- [`docs/openapi.json` desincronizado] -> Regeneracion con el script versionado y verificacion con el test de sincronia en la suite.
- [Consumidores del JSON estricto que no esperaban campos extra] -> Adicion pura de campos en una respuesta de lectura; no hay `additionalProperties: false` en la respuesta de listado.

## Migration Plan

1. Implementar por TDD el cambio de schema y la extraccion de la derivacion.
2. Regenerar `docs/openapi.json` con `python scripts/export_openapi.py`.
3. Verificar `pytest tests/test_openapi_sync.py` y la suite offline (`pytest -m "not integration"`).
4. Deploy: cambio aditivo y retrocompatible; no requiere migracion ni orden de despliegue especial.
5. Rollback: revertir el commit elimina los campos y restaura `docs/openapi.json`; no hay datos ni estado persistido afectados.

## Open Questions

- Ninguna que cambie las specs, el enfoque o el desglose de tareas.
- Diferible: el consumo en el frontend (espejo TS + formato de la columna de latencia y de la marca de anomalia) se aborda en un change de UI posterior.
- Diferible: si el corpus o el analisis de la tesis necesita la latencia por canal desde el listado, evaluar si el listado debe exponer tambien el canal de origen; hoy no es un requisito.