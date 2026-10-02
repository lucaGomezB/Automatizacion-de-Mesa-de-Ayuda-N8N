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
- [x] 0.5 Registrar OQ2/OQ6 (DELEGADAS): c-68 DEPENDE de `c-69-dedup-correlacion-altas` para dedup web y correlacion exacta de correo (contrato de lectura). NO se edita `CHANGES.md` desde c-68. Verificacion: dependencia documentada en design.md y c-69 ya implementado (`origen_message_id` en `IncidenteRead` + filtro exacto `GET /incidentes/?origen_message_id=`). — gatea la corrida COMPLETA
- [x] 0.6 Registrar el baseline de los tests offline existentes: `cd scripts/corpus_ingest; python -m pytest test_ingest_corpus.py test_pseudonymize_corpus.py -q` = 24 passed, 2 skipped (XLSX omitido por falta de openpyxl; se instalo openpyxl para validar el writer y quedo 0 skipped). `cd evaluation; pytest -q` = 69 passed (usa el fixture `tests/fixtures/corpus_fixture.json`, NO el JSON real; por eso no falla por null). Sin fallos preexistentes. Verificacion: conteos baseline anotados.
- [x] 0.7 Confirmar que NO se modifica ningun archivo de producto bajo `App/**`: `git status` no muestra cambios en `App/**` (solo los dos archivos nuevos del harness). Verificacion: `git status` sin cambios en `App/**`.
- [ ] 0.8 Confirmar el camino de confirmacion separado (D14): la bandeja/carpeta del chequeo NO es la que alimenta el trigger IMAP de ingesta. Verificacion: camino separado documentado y verificado. — BLOCKED: gatea la corrida COMPLETA; requiere configurar la carpeta/buzon de confirmacion real y su IMAP (no hay instancia N8N ni buzon activos). La regla y su verificacion pura (`confirmation_path_is_separate`) quedan implementadas y testeadas.

## 1. Logica pura del harness (TDD)

- [x] 1.1 RED: crear `scripts/corpus_ingest/test_ingest_via_n8n.py` con el test de derivacion de la metrica. Verificacion: fallo por modulo inexistente (RED confirmado).
- [x] 1.2 GREEN: crear `scripts/corpus_ingest/ingest_via_n8n.py` con la funcion pura de derivacion minima (instantes normalizados a UTC). Verificacion: el test de 1.1 pasa.
- [x] 1.3 TRIANGULATE: casos web con espera pequena, correo con espera de poller grande, `latencia_e2e_ms` nulo y `t_e2e_s` no positivo -> anomalo. Verificacion: los cuatro casos en verde.
- [x] 1.4 RED: tests de construccion del payload web (`{descripcion, prioridad, origen_message_id}`) y de la derivacion sin loguear la descripcion. Verificacion: fallo por funcion inexistente.
- [x] 1.5 GREEN: implementar el builder del payload web. Verificacion: el test de 1.4 pasa.
- [x] 1.6 TRIANGULATE: prioridad por defecto, prioridad custom, descripcion con caracteres especiales y ausencia de campos que el backend rechaza. Verificacion: casos en verde.
- [x] 1.7 RED: tests de generacion de `Message-ID` deterministico (`corpus-<ID>@<dominio>`, con `<...>`) y de normalizacion (strip de `<>`). Verificacion: fallo por funcion inexistente.
- [x] 1.8 GREEN: implementar el generador y el normalizador de `Message-ID`. Verificacion: el test de 1.7 pasa.
- [x] 1.9 TRIANGULATE: dominio por env, ids repetidos y header ya sin corchetes. Verificacion: casos en verde.
- [x] 1.10 RED: tests de mapeo de canal tolerante a acentos/alias (JSON y CSV) y de la seleccion (`--only-channel`/`--limit`). Verificacion: fallo por funcion inexistente.
- [x] 1.11 GREEN: implementar el mapeo y la seleccion. Verificacion: el test de 1.10 pasa.
- [x] 1.12 TRIANGULATE: etiquetas desconocidas, vacias y con espacios. Verificacion: casos en verde.
- [x] 1.13 RED: tests puros del chequeo de confirmacion (`t_confirmacion_s`, `confirmacion_recibida`, ausencia no invalida la primaria). Verificacion: fallo por funcion inexistente.
- [x] 1.14 GREEN: implementar la derivacion del chequeo de confirmacion. Verificacion: el test de 1.13 pasa.
- [x] 1.15 REFACTOR: constantes centralizadas (nombres de columnas, prefijo, paths, timeouts) y modulos separados lectura/escritura/transporte. Suite del harness en verde tras cada paso. Verificacion: todos los tests siguen en verde.

## 2. Camino web

- [x] 2.1 RED: test con transporte HTTP simulado que exige POST al webhook, lectura del `incidente_id` y `GET /api/v1/incidentes/{id}`. Verificacion: fallo por funcion inexistente.
- [x] 2.2 GREEN: implementar el camino web reutilizando `_request_with_retry` (reintentos solo 5xx/timeouts) y midiendo `t_envio` antes del POST. Verificacion: el test de 2.1 pasa.
- [x] 2.3 TRIANGULATE: 4xx (no reintenta), 5xx transitorio (reintenta), timeout y respuesta sin `incidente_id`. Verificacion: casos en verde.
- [x] 2.4 REFACTOR: separar el transporte HTTP de la derivacion/registro; la descripcion no se loguea (solo labels de error). Verificacion: tests en verde y salida sin descripcion.

## 3. Camino correo (correlacion exacta + confirmacion)

- [x] 3.1 RED: test (SMTP simulado + contrato de c-69 mockeado) que exige envio con `Message-ID` deterministico y correlacion EXACTA por `origen_message_id`. Verificacion: fallo por funcion inexistente.
- [x] 3.2 GREEN: implementar el camino correo con correlacion exacta via el filtro de c-69 y backoff acotado (`--poll-timeout`/`--poll-interval`). Verificacion: el test de 3.1 pasa.
- [x] 3.3 TRIANGULATE: (a) sin incidente correlacionado -> timeout ruidoso; (b) `ingresado_en` anterior a `t_envio` -> no reclamado; (c) replay con el mismo `Message-ID` -> id determinista (sin segunda fila/medicion). Verificacion: casos en verde.
- [x] 3.4 TRIANGULATE (fallback documentado): `select_incident_by_window` cubre el buzon limpio con un unico correo nuevo, excluye ids ya reclamados y no confunde un incidente viejo. NO es el mecanismo primario (c-69 da la correlacion exacta). Verificacion: casos en verde.
- [x] 3.5 RED: test de observacion de la confirmacion por camino SEPARADO (observer inyectado). Verificacion: fallo por funcion inexistente.
- [x] 3.6 GREEN: implementar la observacion de confirmacion por el camino separado. Verificacion: el test de 3.5 pasa.
- [x] 3.7 TRIANGULATE: confirmacion ausente -> `confirmacion_recibida: false` sin invalidar la primaria; y `confirmation_path_is_separate` rechaza la misma carpeta del trigger de ingesta. Verificacion: casos en verde.
- [x] 3.8 REFACTOR: parametrizar intervalo/timeout de sondeo, dominio de correo y camino de confirmacion; sin descripcion en logs. Verificacion: tests en verde.
- [x] 3.9 WIRE (D14): conectar el observer de confirmacion al CLI `run()`. Construirlo SOLO si `INGEST_CONFIRMATION_IMAP_HOST` + `INGEST_CONFIRMATION_IMAP_USER` estan definidos (si no, `confirmation_observer=None`, no bloqueante); correr `confirmation_separation_error` antes de la ingesta de correo y ABORTAR con exit != 0 si el camino no es separado; pasar el observer + `--confirmation-timeout`/`--confirmation-interval` a `ingest_email_case`. Matching puro (`select_confirmation_instant`) testeado offline; I/O IMAP (`_fetch_confirmation_messages`) con `# pragma: no cover - I/O` e injectable. Verificacion: 14 tests nuevos en verde y `--dry-run`/`--help` intactos; guard rechaza misma cuenta+carpeta y acepta carpeta/buzon distinto. — el guard queda IMPLEMENTADO y testeado; 0.8 sigue BLOCKED por la configuracion real.

## 4. Write-back y merge del corpus

- [x] 4.1 RED: tests de escritura XLSX Y CSV (`tmp_path`) con `TIempo de Registro Automatico (Segundos)`, `Latencia e2e (ms)`, `Tiempo pipeline (s)` y `Tiempo espera (s)`, preservando filas e idempotentes. Verificacion: fallo por funcion inexistente.
- [x] 4.2 GREEN: implementar los escritores XLSX y CSV reutilizando los helpers de `ingest_corpus.py`. Verificacion: el test de 4.1 pasa.
- [x] 4.3 TRIANGULATE: error deja celdas vacias; un valor previo NUNCA se sobrescribe con vacio; re-ejecucion no duplica columnas. Verificacion: casos en verde.
- [x] 4.4 RED: test del sidecar JSON con campos de trazabilidad (incluidos `confirmacion_recibida`/`t_confirmacion_s`) y AUSENCIA de `descripcion`. Verificacion: fallo por funcion inexistente.
- [x] 4.5 GREEN: implementar el sidecar description-free. Verificacion: el test de 4.4 pasa.
- [x] 4.6 RED: test del merge del JSON: escribe `tiempo_automatizado_s` numerico por `id`, NO sobrescribe un valor no nulo con null, preserva casos sin medicion y reporta el conteo aun nulo. Verificacion: fallo por funcion inexistente.
- [x] 4.7 GREEN: implementar el merge idempotente y el reporte del conteo de nulos. Verificacion: el test de 4.6 pasa.
- [x] 4.8 TRIANGULATE: caso ya cargado, caso sin medicion; `evaluation/corpus.py` NO fue modificado (`git status` sin cambios en `evaluation/`). Verificacion: casos en verde y sin diff en el validador.
- [x] 4.9 REFACTOR: unificar el formato numerico y los nombres de columnas como constantes. Verificacion: suite del harness en verde.

## 5. Runbook y prerrequisitos de operacion

- [x] 5.1 Documentar en `scripts/corpus_ingest/README.md` el harness, sus flags, las formulas de la metrica D, la privacidad y los caveats por canal. Verificacion: seccion nueva presente y consistente con `docs/medicion-latencia-e2e.md` §5.
- [x] 5.2 Documentar el runbook de N8N: importar `n8n/workflow.json`, reemplazar los placeholders (`REPLACE_WITH_IMAP_CREDENTIAL_ID`, `REPLACE_WITH_SMTP_CREDENTIAL_ID`, `REPLACE_WITH_OPERATOR_LOGIN_CREDENTIAL_ID`, Redis/Gemini), activar el workflow y usar un operador con alcance total. Verificacion: pasos concretos y placeholders pendientes listados.
- [x] 5.3 Documentar que el login se lee de `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD` y que no hay secretos en el codigo. Verificacion: variables referenciadas y ninguna credencial hardcodeada (solo nombres de variables de entorno).
- [x] 5.4 Documentar el camino de confirmacion separado (D14): carpeta/buzon dedicado NO leido por el trigger de ingesta, variables de IMAP de confirmacion y regla de no contaminacion. Verificacion: seccion presente y `confirmation_path_is_separate` testeado.
- [x] 5.5 Documentar la dependencia `c-69` (dedup web + correlacion exacta) y el completado manual de los 81 telefono por el autor como gates de la corrida completa. Verificacion: dependencias y gates explicitos.
- [x] 5.6 Actualizar `docs/como_cargar_datos_corpus.md` para referenciar el camino N8N y la metrica D como productores de `tiempo_automatizado_s`. Verificacion: referencia cruzada presente.

## 6. Verificacion final

- [x] 6.1 Smoke sin red ni escritura: `python3 scripts/corpus_ingest/ingest_via_n8n.py --dry-run` reporta `200 casos | correo=66 web=53 telefono=81 | ingesta=119 telefono_omitido=81 pendientes_nulos=200`, exit 0 y `git status` sin cambios en `data/`. Verificacion: exit 0 y `data/` intacto.
- [ ] 6.2 Corrida acotada web: `--only-channel web --limit 2` con el workflow activo y credenciales de entorno. — BLOCKED by 0.8: requiere N8N activo con credenciales reales y el camino de confirmacion separado; no se corrio la ingesta real.
- [ ] 6.3 Corrida acotada correo: `--only-channel correo --limit 2`. — BLOCKED by 0.5, 0.8: requiere N8N activo + IMAP/SMTP reales; la correlacion exacta y la observacion de confirmacion quedan implementadas y testeadas con transporte simulado.
- [ ] 6.4 Corrida completa de web y correo (119 casos). — BLOCKED by 0.5, 0.8: requiere la corrida real (N8N activo + credenciales + camino separado) que este entorno no tiene. El harness queda listo para ejecutarla.
- [x] 6.5 Reportar el conteo de casos aun nulos (81 telefono pendientes) en el resumen del harness. Verificacion: `--dry-run` reporta `pendientes_nulos=200` y el `run` real imprime `telefono_pendiente`; ningun valor no nulo se sobrescribe con null (testeado).
- [ ] 6.6 Verificar la carga COMPLETA del corpus: `cd evaluation; pytest -q` sin `CorpusError` UNA VEZ que el autor complete los 81 telefono. — BLOCKED by 6.4 + completado manual de telefono: con 200/200 nulos el JSON real no es cargable aun; el validador `_a_float` permanece intacto.
- [x] 6.7 Correr la suite offline: harness `48 passed`; `cd App/Backend; pytest -m "not integration"` = `878 passed, 37 deselected, 1 xfailed`. Sin fallos nuevos respecto del baseline (no hubo cambios en `App/**`). Verificacion: conteos en verde.
- [x] 6.8 `openspec validate --strict --changes c-68-corpus-ingesta-n8n` pasa. Verificacion: validacion estricta sin errores.

## Notas de desviacion

- **D2 (design) vs c-69 implementado**: D2 decia que el canal web no envia `origen_message_id` y que el dedup lo aportaba c-69. c-69 ya implementado admite un id deterministico provisto por el llamador (`webBody.origen_message_id`, precedencia D1 de c-69). El harness envia `origen_message_id = corpus-<ID>` para hacer el re-run idempotente, alineado con el prompt de la tarea y con c-69. Se documenta aqui.
- **Fallback temporal (3.4)**: se implementa como funcion pura documentada (`select_incident_by_window`) y testeada, pero NO es el mecanismo primario; la correlacion exacta via filtro `origen_message_id` de c-69 es la primaria.
- **openpyxl**: no venia instalado en el host; se instalo (`pip install --user --break-system-packages openpyxl`, 3.1.5) para poder validar el writer XLSX en lugar de omitir su test.
