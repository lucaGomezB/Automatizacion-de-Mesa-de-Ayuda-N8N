# Tasks — c-48-timing-en-listado

Strict TDD. Cada grupo respeta el ciclo: red de seguridad -> RED -> GREEN -> TRIANGULATE -> REFACTOR -> verificacion. Ninguna tarea escribe codigo de produccion antes de su test.

## 1. Red de seguridad (antes de tocar `app/schemas/incidente.py`)

- [x] 1.1 Correr la linea base de los tests que cubren el archivo a modificar: `cd App/Backend; pytest tests/test_timing_contract.py tests/test_api_incidentes.py -m "not integration"` y registrar el conteo ("N passed"). Si algo falla, detenerse y reportarlo como fallo preexistente (no arreglarlo). → 45 passed
- [x] 1.2 Correr la linea base del test de sincronia OpenAPI: `cd App/Backend; pytest tests/test_openapi_sync.py -v` y confirmar que pasa con el `docs/openapi.json` actual. Registrar el conteo. → 5 passed
- [x] 1.3 Verificar versiones pinneadas antes de cualquier regeneracion: `cd App/Backend; pip show fastapi pydantic` contra `requirements.txt` (fastapi==0.115.0, pydantic==2.9.2). Si no coinciden, instalar `requirements.txt` antes de regenerar. → fastapi 0.115.0, pydantic 2.9.2, pydantic-settings 2.5.2 (coinciden)

## 2. RED — tests que describen el contrato del listado

- [x] 2.1 En `App/Backend/tests/test_timing_contract.py`, agregar un helper `_make_list_item(ingresado_en, persistido_en)` que construya un `IncidenteListItem` completo y un grupo de tests "IncidenteListItem: instantes y latencia derivada". Primer test: el item expone `ingresado_en` y `persistido_en` con los valores pasados. Verificar que FALLA (el campo no existe todavia).
- [x] 2.2 Test RED de derivacion: con `ingresado_en=10:00:00Z` y `persistido_en=10:00:12.5Z`, `latencia_e2e_ms == 12500`. Verificar que FALLA por `AttributeError`/campo faltante.
- [x] 2.3 Tests RED de casos borde: `latencia_e2e_ms is None` si falta `ingresado_en`, si falta `persistido_en`, o si ambos son nulos; el item se construye sin error. Verificar que FALLAN.
- [x] 2.4 Test RED de anomalia: con `persistido_en` anterior a `ingresado_en`, `latencia_e2e_ms is None` y `latencia_anomala is True`; con latencia valida, `latencia_anomala is False`; con latencia cero, `latencia_e2e_ms == 0` y no anomalo. Verificar que FALLAN.
- [x] 2.5 GATE RED: `cd App/Backend; pytest tests/test_timing_contract.py -k "ListItem" -v` debe mostrar todos los tests nuevos fallando por la razon esperada (campo ausente), no por errores de sintaxis del test. → 8 failed por AttributeError

## 3. GREEN — implementacion minima

- [x] 3.1 REFACTOR preservador: en `App/Backend/app/schemas/incidente.py`, extraer la derivacion a funciones puras de modulo `_derivar_latencia_e2e_ms(ingresado_en, persistido_en)` y `_es_latencia_anomala(ingresado_en, persistido_en)`, reutilizando `_to_utc`; hacer que las propiedades `@computed_field` de `IncidenteRead` deleguen en ellas. Verificar que `pytest tests/test_timing_contract.py -m "not integration"` sigue verde (comportamiento observable de `IncidenteRead` intacto). → 16 passed (subset IncidenteRead)
- [x] 3.2 GREEN: agregar a `IncidenteListItem` los campos `ingresado_en: datetime | None = None` y `persistido_en: datetime | None = None`, mas las propiedades `@computed_field latencia_e2e_ms` y `latencia_anomala` que delegan en las funciones puras de 3.1. Mantener `model_config = ConfigDict(from_attributes=True)`. Verificar que `pytest tests/test_timing_contract.py -k "ListItem" -v` PASA. → 9 passed
- [x] 3.3 GATE GREEN: correr `cd App/Backend; pytest tests/test_timing_contract.py -m "not integration"` completo y confirmar verde sin regresiones. → 25 passed

## 4. TRIANGULATE — escenarios restantes de la spec

- [x] 4.1 Test de paridad detalle/listado: el mismo par de instantes construido como `IncidenteRead` y como `IncidenteListItem` produce el mismo `latencia_e2e_ms` al milisegundo (cubre el escenario "Paridad de derivacion entre detalle y listado"). Verificar que PASA.
- [x] 4.2 Test de no-regresion de la proyeccion real: via el cliente de test (`make_client`), crear un incidente con `ingresado_en`/`persistido_en` sellados y consultar `GET /api/v1/incidentes`; verificar que el item del listado devuelve `ingresado_en` y `persistido_en` no nulos y `latencia_e2e_ms` no nulo, comprobando que la ruta y el repositorio no necesitan cambios y que una futura proyeccion que omita las columnas rompe el test. Verificar que PASA. → 1 passed
- [x] 4.3 GATE TRIANGULATE: revisar que cada escenario de la delta spec tenga al menos un test: exposicion en listado, instantes ausentes, paridad, anomalia visible en listado. Correr `pytest tests/test_timing_contract.py tests/test_api_incidentes.py -m "not integration"` y confirmar todo verde. → 55 passed

## 5. docs/openapi.json — sincronia estatica

- [x] 5.1 Regenerar el spec: `cd App/Backend; python scripts/export_openapi.py` y verificar con `git diff docs/openapi.json` que el unico cambio sea la incorporacion de `ingresado_en`, `persistido_en`, `latencia_e2e_ms` y `latencia_anomala` en el schema `IncidenteListItem` (sin cambios en otros schemas ni en paths). → diff aditivo puro sobre IncidenteListItem
- [x] 5.2 Verificar la sincronia: `cd App/Backend; pytest tests/test_openapi_sync.py -v` debe pasar (en particular `test_openapi_in_sync_with_app`). → 5 passed

## 6. Verificacion final

- [x] 6.1 Correr la suite offline completa: `cd App/Backend; pytest -m "not integration"` y confirmar verde, con el conteo mayor o igual a la linea base de 1.1 (los tests nuevos suman). → 566 passed, 25 deselected, 1 xfailed, 0 failed
- [x] 6.2 Confirmar que no se modificaron repositorio, ruta, modelos, migraciones, servicios ni `n8n/workflow.json` (`git status --short` solo lista `app/schemas/incidente.py`, `tests/test_timing_contract.py` (y `test_api_incidentes.py` si aplica), `docs/openapi.json` y los artefactos de este change). → solo esos archivos
- [x] 6.3 Confirmar que `App/Frontend/src/types/incidente.ts` NO se modifico (fuera de alcance por design D5). → no aparece en git status
- [x] 6.4 Validar el change: `openspec validate --strict --changes c-48-timing-en-listado` pasa; registrar la salida exacta en el reporte de verificacion. → Totals: 2 passed, 0 failed (exit 0)