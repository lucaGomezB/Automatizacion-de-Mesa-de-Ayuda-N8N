## 1. Contrato de migracion (governance ALTA)

- [x] 1.1 Obtener aprobacion humana explicita del design y del plan de migracion antes de escribir codigo; registrar la aprobacion en la cabecera de la migracion. Verificacion: aprobacion registrada en el archivo de migracion.
- [x] 1.2 Escribir el test de migracion que verifique `revision="006"`, `down_revision="005"`, columnas `ingresado_en` y `persistido_en` nullable, y `downgrade` que dropea ambas; confirmar RED (falla por ausencia de la revision).
- [x] 1.3 Crear `App/Backend/alembic/versions/006_add_timing_instrumentation.py` aditiva (sin backfill, sin indices) y verificar GREEN del test de migracion.
- [x] 1.4 Agregar `ingresado_en` y `persistido_en` (`DateTime(timezone=True)`, nullable, sin `onupdate`) al modelo `Incidente`; verificar que el mapper expone ambas columnas.

## 2. Schema y validacion

- [x] 2.1 Escribir tests de `IncidenteCreate.ingresado_en` (acepta con `Z`/offset y normaliza a UTC; rechaza naive; rechaza futuro fuera de tolerancia; acepta futuro dentro de tolerancia; acepta nulo); confirmar RED.
- [x] 2.2 Implementar el campo `ingresado_en` con sus validadores y el setting de tolerancia de futuro; verificar GREEN.
- [x] 2.3 Escribir tests de `IncidenteRead` (expone `ingresado_en`, `persistido_en` y `latencia_e2e_ms`; latencia nula si falta un instante; 12.5 s deriva 12500 ms); confirmar RED.
- [x] 2.4 Implementar la exposicion de los instantes y la derivacion de `latencia_e2e_ms`; verificar GREEN.

## 3. Servicio

- [x] 3.1 Escribir el test que verifique que `create_and_classify` sella `persistido_en` no nulo; confirmar RED.
- [x] 3.2 Implementar el sello de `persistido_en` dentro de la transaccion de alta y clasificacion; verificar GREEN.
- [x] 3.3 Escribir el test que verifique que un PATCH (`update_incidente`) modifica `updated_at` pero NO `persistido_en`; confirmar GREEN (inmutabilidad).
- [x] 3.4 Escribir el test de replay idempotente: un segundo alta con el mismo `origen_message_id` devuelve la fila existente con sus instantes originales y no aumenta el conteo de filas; confirmar GREEN.

## 4. Workflow N8N

- [x] 4.1 Escribir los tests estructurales: el body del POST incluye `ingresado_en` por expresion; el sello de telefonia esta aguas arriba del `AI Agent`; el correo sella al inicio del trigger de Outlook (recogida del poller), no con `receivedDateTime`; el web sella en `Marcar canal web`; el normalizador propaga `ingresado_en`; confirmar RED.
- [x] 4.2 Implementar la captura de ingreso por canal (nodo de sello inmediatamente posterior a `Llamada telefonica` y anterior al `AI Agent`; sellado en correo y web) y la propagacion en el normalizador; verificar GREEN.
- [x] 4.3 Agregar `ingresado_en` al body del nodo `HTTP POST a MTM-SRU` resolviendo al valor capturado; verificar GREEN del test estructural de body.
- [x] 4.4 Verificar que no se introdujeron fixes de cableado de c-40 ni host/credenciales hardcodeadas, y que las suites estructurales previas del workflow siguen en verde.

## 5. Documentacion y verificacion de integracion

- [x] 5.1 Documentar el contrato de medicion (definiciones de ingreso y persistencia confirmada, unidades, caveats por canal y exclusion de replays) en `docs/medicion-latencia-e2e.md` y referenciarlo desde la guia operativa; verificar contenido.
- [x] 5.2 Regenerar `docs/openapi.json` y verificar `pytest tests/test_openapi_sync.py` en verde.
- [x] 5.3 Correr `pytest -m "not integration"` en `App/Backend` y verificar que no hay regresiones.
- [x] 5.4 Correr `pytest -m integration` con PostgreSQL disposable y verificar el ciclo `upgrade`/`downgrade` de la migracion 006.
- [x] 5.5 Verificacion final: `openspec validate --strict --change c-39-e2e-timing-instrumentation` en verde y evidencia TDD (RED/GREEN) registrada por tarea.
