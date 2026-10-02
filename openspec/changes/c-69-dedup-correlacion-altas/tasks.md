# Tareas — c-69-dedup-correlacion-altas

> Strict TDD: cada bloque de codigo sigue RED -> GREEN -> TRIANGULATE -> REFACTOR. Governance MEDIO. Las OQ-A..OQ-D estan RESUELTAS por el autor (ver `design.md` §Resolved Open Questions): el change es apply-ready, sin gating de decisiones. El change es PREREQUISITO de C-68.

## 0. Safety net y arranque

- [ ] 0.1 Safety net: correr los tests existentes que se van a tocar y anotar el baseline en verde: `cd App/Backend; pytest tests/test_schemas_pseudonimizacion.py tests/test_api_incidentes.py tests/test_numero_incidente.py -q`. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificacion: conteo baseline anotado.
- [ ] 0.2 Verificar que se parte de un arbol limpio respecto de `App/**` y `n8n/workflow.json`. Verificacion: `git status` inspeccionado; sin cambios ajenos al change.

## 1. Contrato de lectura: `IncidenteRead` expone `origen_message_id` (TDD)

- [ ] 1.1 RED: agregar en `App/Backend/tests/test_schemas_pseudonimizacion.py` un test que exija que `IncidenteRead` exponga `origen_message_id` y que una instancia con el campo nulo lo serialice sin error. Verificacion: el test falla porque el campo no existe.
- [ ] 1.2 GREEN: agregar `origen_message_id: str | None = None` a `IncidenteRead` en `App/Backend/app/schemas/incidente.py`. Verificacion: el test de 1.1 pasa.
- [ ] 1.3 TRIANGULATE: cubrir (a) valor no nulo expuesto tal cual; (b) `None` serializado como `null`; (c) `model_validate` desde ORM con `from_attributes`. Verificacion: los tres casos en verde.
- [ ] 1.4 REFACTOR: revisar docstring del schema para documentar el campo como identificador de correlacion (sin PII). Verificacion: suite en verde.

## 2. Filtro exacto por `origen_message_id` en el listado (TDD)

- [ ] 2.1 RED: test de repositorio en SQLite que exija que `list_filtered(origen_message_id="X")` devuelva solo el incidente con ese identificador y que el valor inexistente devuelva vacio. Verificacion: el test falla por parametro inexistente.
- [ ] 2.2 GREEN: agregar el parametro `origen_message_id` a `IncidenteRepository.list_filtered` y la condicion exacta cuando no es None. Verificacion: el test de 2.1 pasa.
- [ ] 2.3 TRIANGULATE: cubrir (a) combinacion con otro filtro (AND logico); (b) ausencia del filtro no altera el resultado; (c) coincidencia parcial NO matchea (exacto). Verificacion: casos en verde.
- [ ] 2.4 RED: test de servicio que exija que `IncidenteService.list_incidentes(origen_message_id=...)` propague el filtro y respete el alcance por rol (un no administrador no ve un id fuera de su sector). Verificacion: el test falla por parametro inexistente.
- [ ] 2.5 GREEN: propagar el parametro en `IncidenteService.list_incidentes` y pasarlo al repositorio, sin romper la logica de alcance. Verificacion: el test de 2.4 pasa.
- [ ] 2.6 TRIANGULATE: cubrir alcance total (administrador ve el id de cualquier sector) y alcance vacio (cuenta sin empleado devuelve vacio antes de consultar). Verificacion: casos en verde.
- [ ] 2.7 RED: test de ruta/API que exija `GET /api/v1/incidentes/?origen_message_id=...` devolviendo el incidente correlacionado y la lista vacia para un valor inexistente. Verificacion: el test falla porque el Query param no existe.
- [ ] 2.8 GREEN: agregar el `Query(None, max_length=255)` `origen_message_id` en `list_incidentes` de `App/Backend/app/routes/incidentes.py` y pasarlo al servicio. Verificacion: el test de 2.7 pasa.
- [ ] 2.9 TRIANGULATE: cubrir el filtro junto a `sector_id`/`desde` y un valor con longitud valida. Verificacion: casos en verde.
- [ ] 2.10 REFACTOR: mantener la firma del servicio/repositorio ordenada y documentada; correr la suite tras cada paso. Verificacion: `pytest -m "not integration"` en verde.

## 3. Rama web del workflow N8N (TDD estructural)

- [ ] 3.1 Safety net: correr la suite estructural del workflow existente y anotar el baseline. Verificacion: conteo baseline en verde; `n8n/workflow.json` sin cambios previos.
- [ ] 3.2 RED: agregar un test estructural que inspeccione el `jsCode` del nodo "Normalizar entrada del incidente" y exija que la rama web produzca un `origen_message_id` no nulo cuando (a) el body trae `origen_message_id`/`case_id` y (b) el body no lo trae (generacion unica). Verificacion: el test falla porque el ternario fuerza `null`.
- [ ] 3.3 GREEN: modificar el ternario `origenMessageId` en `n8n/workflow.json`: web toma `webBody.origen_message_id` / `corpus-<case_id>` si viene, y si no un id generado unico por ejecucion. Verificacion: el test de 3.2 pasa.
- [ ] 3.4 TRIANGULATE: ampliar el test para exigir que las ramas correo (`messageIdHeader || uidFallback`) y telefonia (`call_sid`) no cambien, y que el POST envia el valor (no `null`) para web. Verificacion: casos en verde.
- [ ] 3.5 REFACTOR: extraer el prefijo de generacion (`web-`) y documentar la precedencia en el comentario del nodo; re-correr la suite estructural. Verificacion: todos los tests del workflow en verde.
- [ ] 3.6 Verificar que el POST del backend (`HTTP POST a MESA-AYUDAS`) sigue enviando `origen_message_id` por expresion resuelta del normalizador. Verificacion: inspeccion del body y test estructural en verde.

## 4. Documentacion y sincronizacion

- [ ] 4.1 Regenerar `docs/openapi.json` si el contrato cambio y verificar la paridad. Verificacion: `cd App/Backend; pytest tests/test_openapi_sync.py -v` en verde.
- [ ] 4.2 Actualizar `docs/medicion-latencia-e2e.md` §6 para referenciar la correlacion exacta por `origen_message_id` (el replay devuelve la fila existente sin re-medir). Verificacion: referencia cruzada presente y consistente con el spec.
- [ ] 4.3 Verificar que no hay cambio necesario en el frontend (el formulario real no envia id). Verificacion: `git status` sin cambios en `App/Frontend/` y nota en `design.md`.

## 5. Verificacion final

- [ ] 5.1 Suite backend offline: `cd App/Backend; pytest -m "not integration"` en verde con el baseline de 0.5 preservado. Verificacion: sin regresiones.
- [ ] 5.2 Test de integracion del filtro contra PostgreSQL descartable: `cd App/Backend; pytest -m integration -k origen`. Verificacion: el filtro exacto y la unicidad funcionan sobre PostgreSQL.
- [ ] 5.3 Validacion estricta de OpenSpec: `openspec validate --strict --changes c-69-dedup-correlacion-altas`. Verificacion: PASS.
- [ ] 5.4 Checklist de contrato: `IncidenteRead` expone `origen_message_id`; el listado filtra exacto; la rama web no fuerza `null`; correo/telefonia intactos; sin migracion ni backfill. Verificacion: los cinco puntos verificados contra el codigo y el JSON.
- [ ] 5.5 Verificar que `design.md` registra OQ-A..OQ-D como RESUELTAS y que no queda ninguna Open Question bloqueante. Verificacion: seccion "Resolved Open Questions" sin pendientes.
