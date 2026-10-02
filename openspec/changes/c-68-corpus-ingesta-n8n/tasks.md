# Tareas — c-68-corpus-ingesta-n8n

> Strict TDD: cada bloque de logica pura sigue RED -> GREEN -> TRIANGULATE -> REFACTOR.
> Gating REESTRUCTURADO: OQ1/OQ3/OQ4/OQ5 ya estan RESUELTAS y registradas; el harness es
> implementable YA. Solo la dependencia `c-69-dedup-correlacion-altas` (OQ2/OQ6: dedup web +
> correlacion exacta de correo) y el completado MANUAL de los 81 telefono por el autor gatean
> la CORRIDA COMPLETA y la carga total del JSON. El harness produce mediciones web+correo (119)
> y deja telefono explicitamente pendiente.

## 0. Prerequisitos, decisiones y gating

- [x] 0.1 Registrar OQ1 (RESUELTA): canonico D, `tiempo_automatizado_s = t_e2e_s` (poller-inclusivo para correo), `t_espera_s` reportado aparte y `t_pipeline_s` como cota inferior; formulas `t_pipeline_s = latencia_e2e_ms/1000 = persistido_en - ingresado_en`, `t_espera_s = ingresado_en - t_envio`, `t_e2e_s = persistido_en - t_envio`. Verificacion: reflejado en D1.
- [x] 0.2 Registrar OQ3 (RESUELTA): columnas NUEVAS `Tiempo pipeline (s)` y `Tiempo espera (s)` (+ `Latencia e2e (ms)`) en XLSX Y CSV, ademas del sidecar. Verificacion: reflejado en D5.
- [x] 0.3 Registrar OQ4 (RESUELTA): la confirmacion de correo es chequeo end-to-end SECUNDARIO por un camino de recepcion SEPARADO. Verificacion: reflejado en D14.
- [x] 0.4 Registrar OQ5 (RESUELTA): los 81 valores de `llamada telefonica` los mide/carga el autor MANUALMENTE; el harness cubre web+correo (119) y reporta el conteo de nulos pendientes sin sobrescribir con null. Verificacion: reflejado en D5.
- [ ] 0.5 Registrar OQ2/OQ6 (DELEGADAS): c-68 DEPENDE de `c-69-dedup-correlacion-altas` para dedup web y correlacion exacta de correo (contrato de lectura). NO se edita `CHANGES.md` desde c-68. Verificacion: dependencia documentada en design.md. — gatea la corrida COMPLETA
- [ ] 0.6 Registrar el baseline de los tests offline existentes: `cd scripts/corpus_ingest; python -m pytest test_ingest_corpus.py test_pseudonymize_corpus.py -q` y anotar el conteo en verde; si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Anotar tambien `cd evaluation; pytest -q` (se espera fallo por null). Verificacion: conteos baseline anotados.
- [ ] 0.7 Confirmar que NO se modifica ningun archivo de producto bajo `App/**`: el contrato de lectura y el dedup web los toca c-69, NO c-68. Verificacion: `git status` sin cambios en `App/**`.
- [ ] 0.8 Confirmar el camino de confirmacion separado (D14): la bandeja/carpeta del chequeo NO es la que alimenta el trigger IMAP de ingesta. Verificacion: camino separado documentado y verificado. — gatea la corrida COMPLETA

## 1. Logica pura del harness (TDD)

- [ ] 1.1 RED: crear `scripts/corpus_ingest/test_ingest_via_n8n.py` con el test de derivacion de la metrica: dados `t_envio`, `ingresado_en`, `persistido_en` fijos, exigir `t_pipeline_s = (persistido_en - ingresado_en)`, `t_espera_s = (ingresado_en - t_envio)` y `t_e2e_s = t_espera_s + t_pipeline_s`, y que `tiempo_automatizado_s` sea `t_e2e_s` en web y correo. Verificacion: el test falla por modulo inexistente.
- [ ] 1.2 GREEN: crear `scripts/corpus_ingest/ingest_via_n8n.py` con la funcion pura de derivacion minima (instantes normalizados a UTC). Verificacion: el test de 1.1 pasa.
- [ ] 1.3 TRIANGULATE: agregar casos (a) web con `t_espera_s` pequeno; (b) correo con espera de poller grande; (c) `latencia_e2e_ms` nulo; (d) `t_e2e_s` no positivo -> anomalo. Verificacion: los cuatro casos en verde.
- [ ] 1.4 RED: tests de construccion del payload web (`{descripcion, prioridad?}` sin descripcion en logs) y de `t_envio` en UTC con zona explicita. Verificacion: el test falla por funcion inexistente.
- [ ] 1.5 GREEN: implementar el builder del payload web. Verificacion: el test de 1.4 pasa.
- [ ] 1.6 TRIANGULATE: cubrir prioridad por defecto, descripcion con caracteres especiales y ausencia de campos que el backend rechaza. Verificacion: casos en verde.
- [ ] 1.7 RED: tests de generacion de `Message-ID` deterministico (`corpus-<ID>@<dominio>`, con `<...>` en el header) y de normalizacion (strip de `<>`) para la correlacion exacta. Verificacion: el test falla por funcion inexistente.
- [ ] 1.8 GREEN: implementar el generador y el normalizador de `Message-ID`. Verificacion: el test de 1.7 pasa.
- [ ] 1.9 TRIANGULATE: cubrir dominio por env, ids repetidos y header ya sin corchetes. Verificacion: casos en verde.
- [ ] 1.10 RED: tests de mapeo de canal tolerante a acentos/alias para las etiquetas del JSON (`correo electronico`, `formulario web`, `llamada telefonica`) y del CSV (`Correo`, `Formulario Web`, `Telefono`), y de la seleccion (`--only-channel`/`--limit`) que excluye telefono. Verificacion: el test falla por funcion inexistente.
- [ ] 1.11 GREEN: implementar el mapeo y la seleccion. Verificacion: el test de 1.10 pasa.
- [ ] 1.12 TRIANGULATE: cubrir etiquetas desconocidas, vacias y con espacios. Verificacion: casos en verde.
- [ ] 1.13 RED: tests puros del chequeo de confirmacion: dado un instante de recepcion, derivar `t_confirmacion_s = t_confirmacion - t_envio` y `confirmacion_recibida`; cuando no llega, no invalida la medicion primaria. Verificacion: el test falla por funcion inexistente.
- [ ] 1.14 GREEN: implementar la derivacion del chequeo de confirmacion. Verificacion: el test de 1.13 pasa.
- [ ] 1.15 REFACTOR: extraer constantes (nombres de columnas, prefijo, paths por defecto) y eliminar duplicacion; correr toda la suite del harness tras cada paso. Verificacion: todos los tests siguen en verde.

## 2. Camino web

- [ ] 2.1 RED: test (con transporte HTTP simulado/monkeypatch, sin red) que exija: POST al endpoint del webhook web, lectura del `incidente_id` de la respuesta y `GET /api/v1/incidentes/{id}` para obtener los instantes. Verificacion: el test falla por funcion inexistente.
- [ ] 2.2 GREEN: implementar el camino web con reintentos solo para 5xx/timeouts (reutilizar el patron de `_request_with_retry`), midiendo `t_envio` antes del POST. Verificacion: el test de 2.1 pasa.
- [ ] 2.3 TRIANGULATE: cubrir 4xx (no reintenta), 5xx transitorio (reintenta con backoff), timeout, y respuesta sin `incidente_id`. Verificacion: casos en verde.
- [ ] 2.4 REFACTOR: separar cliente HTTP de la derivacion/registro; verificar que no se loguea la descripcion. Verificacion: tests en verde y salida sin descripcion.

## 3. Camino correo (correlacion exacta + confirmacion)

- [ ] 3.1 RED: test (SMTP simulado + API con contrato de c-69 mockeado) que exija: envio con `Message-ID` deterministico, correlacion EXACTA por `origen_message_id` normalizado expuesto por el contrato de lectura, y derivacion de la metrica. Verificacion: el test falla por funcion inexistente.
- [ ] 3.2 GREEN: implementar el camino correo con correlacion exacta via el contrato de c-69 (SMTP configurable por env, backoff acotado que cubra hasta ~60 s de poller). Verificacion: el test de 3.1 pasa.
- [ ] 3.3 TRIANGULATE: cubrir (a) sin incidente correlacionado -> timeout ruidoso; (b) incidente con `ingresado_en` anterior a `t_envio` -> no reclamado; (c) replay con el mismo `Message-ID` -> no produce segunda fila ni segunda medicion. Verificacion: casos en verde.
- [ ] 3.4 TRIANGULATE (fallback documentado): sin el contrato de c-69 y con la correlacion por ventana temporal, cubrir buzon limpio con un unico correo nuevo y no confundir un incidente de otro canal. Verificacion: casos en verde.
- [ ] 3.5 RED: test de observacion de la confirmacion por camino SEPARADO (IMAP de confirmacion simulado): lee la confirmacion, empareja por `Message-ID`/asunto y registra `t_confirmacion`/`confirmacion_recibida` sin tocar el camino de ingesta. Verificacion: el test falla por funcion inexistente.
- [ ] 3.6 GREEN: implementar la observacion de confirmacion en el camino separado. Verificacion: el test de 3.5 pasa.
- [ ] 3.7 TRIANGULATE: cubrir confirmacion ausente dentro del timeout -> `confirmacion_recibida: false` sin invalidar la medicion primaria; y verificacion de que el camino separado no alimenta el trigger de ingesta. Verificacion: casos en verde.
- [ ] 3.8 REFACTOR: parametrizar intervalo/timeout de sondeo, dominio de correo y camino de confirmacion; sin descripcion en logs. Verificacion: tests en verde.

## 4. Write-back y merge del corpus

- [ ] 4.1 RED: tests de escritura XLSX Y CSV (con `tmp_path`): rellenar `TIempo de Registro Automatico (Segundos)` con `t_e2e_s`, escribir `Latencia e2e (ms)`, `Tiempo pipeline (s)` y `Tiempo espera (s)` como columnas nuevas en AMBOS formatos, preservando filas y con idempotencia (sin columnas duplicadas). Verificacion: el test falla por funcion inexistente.
- [ ] 4.2 GREEN: implementar los escritores XLSX y CSV reutilizando los helpers de `ingest_corpus.py`. Verificacion: el test de 4.1 pasa.
- [ ] 4.3 TRIANGULATE: cubrir caso con error (deja celdas vacias), caso anomalo (no escribe valor), y re-ejecucion. Verificacion: casos en verde.
- [ ] 4.4 RED: test del sidecar JSON: campos de trazabilidad (incluidos `confirmacion_recibida` y `t_confirmacion` para correo) y AUSENCIA de la clave `descripcion`. Verificacion: el test falla por funcion inexistente.
- [ ] 4.5 GREEN: implementar el sidecar. Verificacion: el test de 4.4 pasa.
- [ ] 4.6 RED: test del merge del JSON de evaluacion: escribir `tiempo_automatizado_s` numerico por `id`, NO sobrescribir un valor no nulo con null, preservar los casos sin medicion y REPORTAR el conteo de casos aun nulos (telefono pendiente). Verificacion: el test falla por funcion inexistente.
- [ ] 4.7 GREEN: implementar el merge idempotente del JSON y el reporte del conteo de nulos. Verificacion: el test de 4.6 pasa.
- [ ] 4.8 TRIANGULATE: cubrir caso ya cargado, caso sin medicion, y verificacion de que `_a_float` no fue modificado (`git diff` sobre `evaluation/corpus.py` vacio). Verificacion: casos en verde y sin diff en el validador.
- [ ] 4.9 REFACTOR: unificar el formato numerico y los nombres de columnas como constantes. Verificacion: suite del harness en verde.

## 5. Runbook y prerrequisitos de operacion

- [ ] 5.1 Documentar en `scripts/corpus_ingest/README.md` el harness, sus flags, las formulas de la metrica D, la privacidad y los caveats por canal. Verificacion: seccion nueva presente y consistente con `docs/medicion-latencia-e2e.md` §5.
- [ ] 5.2 Documentar el runbook de N8N: importar `n8n/workflow.json`, reemplazar los placeholders (`REPLACE_WITH_IMAP_CREDENTIAL_ID`, `REPLACE_WITH_SMTP_CREDENTIAL_ID`, `REPLACE_WITH_OPERATOR_LOGIN_CREDENTIAL_ID`), activar el workflow y usar un operador con alcance de lectura total. Verificacion: pasos concretos y placeholders pendientes listados.
- [ ] 5.3 Documentar que el login se lee de `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD` y que no hay secretos en el codigo. Verificacion: variables referenciadas y ninguna credencial hardcodeada (`git grep` sin valores).
- [ ] 5.4 Documentar el camino de confirmacion separado (D14): bandeja/carpeta dedicada NO leida por el trigger de ingesta, variables de entorno de IMAP de confirmacion y regla de no contaminacion. Verificacion: seccion presente y camino verificado.
- [ ] 5.5 Documentar la dependencia `c-69` (dedup web + correlacion exacta) y el completado manual de los 81 telefono por el autor como gates de la corrida completa. Verificacion: dependencias y gates explicitos.
- [ ] 5.6 Actualizar `docs/como_cargar_datos_corpus.md` para referenciar el camino N8N y la metrica D como productores de `tiempo_automatizado_s`. Verificacion: referencia cruzada presente.

## 6. Verificacion final

- [ ] 6.1 Smoke sin red ni escritura: `cd scripts/corpus_ingest; python ingest_via_n8n.py --dry-run` reporta conteos por canal y no toca archivos. Verificacion: exit 0 y `git status` sin cambios en `data/`.
- [ ] 6.2 Corrida acotada web: `python ingest_via_n8n.py --only-channel web --limit 2` con el workflow activo y credenciales de entorno; verificar sidecar y celdas actualizadas. Verificacion: 2 casos con metrica y sin descripcion en la salida. — blocked by 0.6, 0.7
- [ ] 6.3 Corrida acotada correo con correlacion exacta: `python ingest_via_n8n.py --only-channel correo --limit 2`; verificar que `t_espera_s` refleja la espera del poller, que la correlacion por `origen_message_id` es exacta y que la confirmacion se observa por el camino separado. Verificacion: 2 casos con metrica y sin duplicados. — blocked by 0.5, 0.8
- [ ] 6.4 Corrida completa de web y correo (119 casos); verificar el resumen (ok/anomalos/saltados) y que los casos de telefono se preservan sin null. Verificacion: sidecar y corpus consistentes; casos anomalos listados. — blocked by 0.5, 0.8
- [ ] 6.5 Reportar el conteo de casos aun nulos (81 telefono pendientes) en el resumen del harness. Verificacion: conteo explicito y ningun `tiempo_automatizado_s` no nulo sobrescrito con null.
- [ ] 6.6 Verificar la carga COMPLETA del corpus: `cd evaluation; pytest -q` carga `data/corpus_evaluacion_pseudonimizado.json` sin `CorpusError` UNA VEZ que el autor complete los 81 telefono. Antes, se espera `CorpusError` por los casos aun nulos y el reporte de 6.5. Verificacion: la suite de `evaluation/` pasa. — blocked by 6.4 + completado manual de telefono
- [ ] 6.7 Correr la suite offline del harness y (si hubo cambios compartidos) `cd App/Backend; pytest -m "not integration"`, confirmando cero fallos nuevos respecto del baseline de 0.6. Verificacion: conteos en verde.
- [ ] 6.8 `openspec validate --strict --changes c-68-corpus-ingesta-n8n` pasa. Verificacion: validacion estricta sin errores.
