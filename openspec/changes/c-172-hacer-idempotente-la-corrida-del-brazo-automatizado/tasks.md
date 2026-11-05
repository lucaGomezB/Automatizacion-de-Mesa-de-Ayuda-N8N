# Tasks: Corrida idempotente y reanudable del brazo automatizado

Convencion TDD estricta: cada tarea RED escribe el test y lo ejecuta fallando por la razon esperada; cada GREEN escribe el minimo y lo ejecuta en verde; cada TRIANGULATE agrega un caso con otra entrada; cada REFACTOR re-ejecuta la suite. Alcance acotado: SOLO `scripts/corpus_ingest/ingest_via_n8n.py` y `scripts/corpus_ingest/test_ingest_via_n8n.py`. NO se tocan backend, DB, N8N, `evaluation/`, `write_sidecar_json` (su semantica de merge) ni el guard `min_ingresado_en`.

## 0. Safety net

- [x] 0.1 Ejecutar `python -m pytest scripts/corpus_ingest/test_ingest_via_n8n.py -q` desde la raiz y registrar el baseline ("N passed"). Verificacion: todo en verde; si algo falla, frenar y reportarlo como falla preexistente sin arreglarlo.
- [x] 0.2 Registrar en el lado del test los helpers existentes (`_ingesta_falsa`, `_argv_campana`, `_escribir_plan`, `_leer_sidecar`) que los tests nuevos reutilizan. Verificacion: los tests nuevos usan esos helpers sin duplicar infraestructura.

## 1. RED — Tests que describen el nuevo contrato (fallan primero)

- [x] 1.1 RED (sonda + B1): test de que, con `--resume`, un caso cuyo sondeo de pre-envio encuentra un incidente PREEXISTENTE (`ingresado_en` ANTERIOR al envio, sesion HTTP falsa que lista ese incidente viejo) NO se reenvia (cero POST al webhook / cero `send_func`) y NO termina en `timeout_correlacion`; su entrada del sidecar lleva `error="incidente_preexistente_sin_t_envio"` y `t_e2e_s`/`t_espera_s` nulas. Verificacion: falla por `--resume` inexistente / comportamiento actual (reenvio).
- [x] 1.2 RED (ledger incremental): test de que una corrida interrumpida tras N casos validos deja N entradas validas en el sidecar. Simular la interrupcion haciendo que el caso N+1 levante una excepcion o cortando la iteracion tras el N-esimo envio; el sidecar debe contener las primeras N entradas ANTES de que la corrida termine. Verificacion: falla (hoy el sidecar se escribe solo al final).
- [x] 1.3 RED (skip por sidecar): test de que una re-corrida con `--resume` sobre el mismo `--id-corrida` y el mismo `--sidecar` NO reenvia los `case_id` que ya tienen entrada VALIDA (la sesion/send falsos registran cero envios para ellos y se reutiliza la medicion almacenada) y SI procesa los casos que aun no tienen entrada. Verificacion: falla (hoy reenvia todos).

## 2. GREEN — Implementar el minimo para pasar 1.1-1.3

- [x] 2.1 GREEN (escritura incremental, A): llamar a `write_sidecar_json(args.sidecar, [result])` dentro del loop de `run` tras producir cada `result`. Verificacion: 1.2 en verde.
- [x] 2.2 GREEN (anotacion por caso): en modo campana, anotar cada `result` con `modo_campana.anotar_resultados(..., args.id_corrida)` ANTES de la escritura incremental, de modo que cada entrada lleve `id_corrida/posicion/mitad/brazo_primero/orden`. Verificacion: 1.2 y la suite de campana existente en verde.
- [x] 2.3 GREEN (`--resume` + skip): agregar `--resume` (`store_true`) a `parse_args`; al iniciar, si `--resume`, cargar las entradas del sidecar (`_load_sidecar_entries`) y saltar los `case_id` con entrada valida de la MISMA corrida (en modo no-campana, corrida `None`). Verificacion: 1.3 en verde.
- [x] 2.4 GREEN (sonda single-shot): helper `probe_existing_incident(...)` que consulta UNA vez por clave el filtro exacto `origen_message_id` SIN el guard `min_ingresado_en` y devuelve el primer incidente o `None`; usarlo en el loop con claves `correlation_keys(case_id, domain)` (correo) y `[corpus-<ID>]` (web). Verificacion: 1.1 en verde.

## 3. TRIANGULATE — Casos adicionales por escenario

- [x] 3.1 TRIANGULATE (residuo vs. medido): un caso con incidente preexistente Y entrada valida en el sidecar se SALTA sin sonda ni residuo; un caso con incidente preexistente y SIN entrada valida se registra como residuo. Verificacion: en verde.
- [x] 3.2 TRIANGULATE (sin residuo): con `--resume`, un caso SIN incidente preexistente se envia normalmente y se mide como hoy (la sonda no altera el camino feliz). Verificacion: en verde.
- [x] 3.3 TRIANGULATE (conducta por defecto intacta): sin `--resume`, un reenvio con el mismo `id_corrida` sigue reenviando TODOS los casos; el test existente `test_un_sidecar_existente_con_el_mismo_id_corrida_se_reanuda` permanece en verde. Verificacion: en verde.
- [x] 3.4 TRIANGULATE (ledger no mezcla corridas): el skip por `--resume` solo considera entradas del `id_corrida` actual; un sidecar de otra corrida se sigue rechazando en preflight como hoy. Verificacion: en verde.

## 4. REFACTOR

- [x] 4.1 REFACTOR: extraer la logica del skip/sonda en funciones puras o helpers con docstring; actualizar el docstring del modulo y el `--help` de `--resume` para declarar que las corridas de campana lo usan y que el ledger es por `id_corrida`. Verificacion: `python -m pytest scripts/corpus_ingest/test_ingest_via_n8n.py -q` en verde y baseline de 0.1 sin regresiones.
- [x] 4.2 REFACTOR: confirmar por lectura que `write_sidecar_json` (`:738-775`) y `select_correlated_incident`/`min_ingresado_en` (`:253-267`, `:1060`) NO cambiaron. Verificacion: `git diff` no muestra cambios en esas funciones.

## 5. Validacion y cierre

- [x] 5.1 Ejecutar `openspec validate c-172-hacer-idempotente-la-corrida-del-brazo-automatizado --strict --no-interactive`. Verificacion: en verde.
- [x] 5.2 Re-ejecutar la suite de 0.1 y confirmar el baseline sin regresiones. Verificacion: en verde.
- [x] 5.3 Confirmar con `git diff --stat` que SOLO se tocaron `scripts/corpus_ingest/ingest_via_n8n.py` y `scripts/corpus_ingest/test_ingest_via_n8n.py` (mas los artefactos OPSX del change). Verificacion: sin backend, DB, N8N ni `evaluation/` en el diff.
