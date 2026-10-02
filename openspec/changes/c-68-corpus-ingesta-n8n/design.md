## Context

Estado actual y restricciones verificadas que moldean el enfoque (ver `proposal.md` para la motivacion):

- **El corpus JSON no es cargable**: `data/corpus_evaluacion_pseudonimizado.json` tiene 200 casos (ids `R001..R200`) y `tiempo_automatizado_s = null` en 200/200. `evaluation/corpus.py::_a_float` (lineas 138-144) lanza `CorpusError` ante null/bool/no-numerico. Los canales del JSON usan etiquetas acentuadas: `correo electrónico` (66), `formulario web` (53), `llamada telefónica` (81). El gemelo XLSX/CSV usa `Correo`, `Formulario Web`, `Telefono` y ya tiene la columna `TIempo de Registro Automatico (Segundos)`.
- **Harness existente**: `ingest_corpus.py` hace POST DIRECTO a `/api/v1/incidentes/` y mide el wall-clock del POST. No pasa por N8N; para correo no existe sello de poller.
- **Workflow N8N** (`n8n/workflow.json`): `"active": false` y credenciales placeholder (`REPLACE_WITH_IMAP_CREDENTIAL_ID`, `REPLACE_WITH_SMTP_CREDENTIAL_ID`, `REPLACE_WITH_OPERATOR_LOGIN_CREDENTIAL_ID`).
  - **Web**: webhook `incidente-web`; `Marcar canal web` sella `ingresado_en`; `Confirmacion web al usuario` (`respondToWebhook`) devuelve `{incidente_id, numero_incidente, mensaje}`.
  - **Correo**: trigger `emailReadImap` con `pollTimes everyMinute`; sella `ingresado_en` al recoger el mensaje; el normalizador toma `metadata['message-id']` como `origen_message_id` (correo); en exito envia `Correo de confirmacion al usuario` al remitente.
- **Contrato de lectura**: `IncidenteRead` expone `ingresado_en`, `persistido_en` y deriva `latencia_e2e_ms` / `latencia_anomala`. `IncidenteListItem` expone ambos instantes y la latencia, pero NO `origen_message_id`, y el listado no filtra por el. El detalle se lee por `GET /api/v1/incidentes/{id}`. La correlacion exacta de correo y el dedup web NO los resuelve c-68: son propiedad del change hermano `c-69-dedup-correlacion-altas`, del que c-68 pasa a ser DEPENDIENTE (OQ2/OQ6 delegadas).
- **Alcance de lectura por rol** (`incident-visibility`): un operador con rol `usuario_final`/`operador` solo ve su sector; leer todos los casos exige alcance de `administrador_directorio` (o un operador por sector).
- **Relojes**: `t_envio` es del cliente (harness); `ingresado_en`/`persistido_en` son UTC del backend/N8N. La tolerancia de futuro de `ingresado_en` es 30 s (`TIMING_FUTURE_TOLERANCE_SECONDS`).

## Goals / Non-Goals

**Goals:**

- Ingestar el corpus por el flujo N8N real en los canales web y correo.
- Derivar y registrar la metrica hibrida por canal con descomposicion auditable.
- Verificar secundariamente el cierre end-to-end por el correo de confirmacion (D14).
- Dejar `data/corpus_evaluacion_pseudonimizado.json` cargable por `evaluation/corpus.py` sin debilitar el validador (una vez que el autor complete los 81 telefono).
- Mantener la privacidad: ninguna descripcion se loguea, imprime ni persiste en el sidecar.

**Non-Goals:**

- Telefono (lo mide y carga el autor manualmente; fuera de alcance del harness).
- Redefinir `latencia_e2e_ms`/`ingresado_en`/`persistido_en` (propiedad de `e2e-timing-instrumentation`).
- Modificar el contrato de lectura del backend o el dedup web: lo resuelve `c-69-dedup-correlacion-altas` (prerequisito).
- Cambiar el clasificador ni el workflow mas alla de la activacion y las credenciales.

## Decisions

### D1: Metrica hibrida (D) — tres componentes por caso

Se registra `t_envio` con reloj UTC del harness: para web, inmediatamente antes del POST al webhook; para correo, inmediatamente antes del envio SMTP. Con los instantes de `IncidenteRead`:

- `t_pipeline_s = latencia_e2e_ms / 1000` = `persistido_en - ingresado_en` (libre de poller; homogeneo entre canales).
- `t_espera_s = ingresado_en - t_envio` (correo: entrega SMTP + permanencia en el buzon hasta la recogida del poller; web: red/cola cliente -> N8N).
- `t_e2e_s = persistido_en - t_envio = t_espera_s + t_pipeline_s` (extremo a extremo percibido).

Canonico `tiempo_automatizado_s`:
- **web**: `t_e2e_s`.
- **correo**: `t_e2e_s` (INCLUYE la espera del poller). El analisis reporta `t_espera_s` por separado y `t_pipeline_s` como cota inferior libre de poller, por canal, segun `docs/medicion-latencia-e2e.md` §5.

**OQ1 RESUELTA por el autor**: se confirma la forma canonica D (`tiempo_automatizado_s = t_e2e_s`, poller-inclusivo para correo) con `t_espera_s` reportado aparte y `t_pipeline_s` como cota inferior libre de poller. Las formulas `t_pipeline_s = latencia_e2e_ms/1000 = persistido_en - ingresado_en`, `t_espera_s = ingresado_en - t_envio` y `t_e2e_s = persistido_en - t_envio` quedan fijadas.

**Justificacion vs alternativas**:
- **A (wall-clock puro del POST directo)**: valido en web (sincronico), pero inexistente en correo (no hay respuesta sincrona) y no ejercita N8N. Descartado.
- **B (`latencia_e2e_ms` puro)**: homogeneo pero EXCLUYE la espera del buzon, sub-midiendo la latencia percibida de correo; no es comparable caso a caso entre canales. Descartado como headline.
- **D (hibrida)**: deriva `t_e2e_s` de los instantes (web y correo comparables en el mismo origen `t_envio`) y conserva `t_pipeline_s`/`t_espera_s` para reportar la cota inferior y hacer explicita la espera del poller. Elegida.

### D2: Camino web (sincronico)

1. `t_envio = now(UTC)`; `POST <n8n-webhook-url>/incidente-web` con `{descripcion, prioridad?}`.
2. La respuesta `respondToWebhook` trae `incidente_id`; `GET /api/v1/incidentes/{incidente_id}` con token de operador devuelve `IncidenteRead`.
3. Se leen `ingresado_en`, `persistido_en`, `latencia_e2e_ms`, `latencia_anomala`, `sector`, `requiere_revision_humana`.
4. La columna web no envia `origen_message_id` (n8n lo mantiene nulo): el dedup web server-side lo aporta `c-69-dedup-correlacion-altas` (OQ2 delegada); hasta entonces rige la mitigacion de corrida unica. Alternativa considerada: POST directo (harness existente) — descartada por no ejercitar el canal real.

### D3: Camino correo (asincronico) y correlacion exacta (prerequisito c-69)

1. `t_envio = now(UTC)`; envio SMTP al buzon dedicado con cuerpo = descripcion del caso y `Message-ID: <corpus-<ID>@<dominio>>` (D6).
2. El trigger IMAP (`everyMinute`) recoge el mensaje, sella `ingresado_en` y el normalizador usa el `Message-ID` como `origen_message_id`; el backend deduplica por ese id.
3. **Correlacion PRIMARIA exacta via `c-69-dedup-correlacion-altas`** (OQ6 delegada): c-69 expone `origen_message_id` en el contrato de lectura (listado y/o filtro). El harness reclama el incidente cuyo `origen_message_id` normalizado (D6) coincide con el `Message-ID` normalizado del caso. c-68 es DEPENDIENTE de c-69 para este camino; sin c-69 implementado, el harness se prueba con el contrato mockeado.
4. **Fallback documentado, NO primario** (solo si el autor declina el camino de contrato de lectura de c-69): correlacion por ventana temporal — `GET /api/v1/incidentes/?desde=<t_envio - margen>&limit=200` (orden `created_at` desc), reclamando el incidente nuevo con `ingresado_en >= t_envio` y un conjunto de ids ya reclamados, con buzon DEDICADO y limpio, un caso en vuelo por vez y backoff acotado (~60 s de poller + procesamiento). Se conserva unicamente como red de seguridad documentada.
5. No se re-miden replays: el `Message-ID` deterministico devuelve el incidente existente como tal (D6, `docs/medicion-latencia-e2e.md` §6).

### D4: Fuente de casos y mapeo de canal

- Fuente por defecto: el JSON de evaluacion (descripciones PSEUDONIMIZADAS, el artefacto que debe volverse cargable). `--source csv|xlsx` permite el corpus de registro crudo.
- Mapeo de canal tolerante a etiquetas/acentos: `correo electronico`/`Correo` -> `correo`; `formulario web`/`Formulario Web` -> `web`; `llamada telefonica`/`Telefono` -> `telefono`. Normalizacion sin acentos + alias.
- Solo `correo` y `web` se ingestan; `telefono` se OMITE y NO se escribe null sobre su valor (si ya existe, se preserva).

### D5: Write-back y carga del corpus (sin debilitar el validador)

**OQ3 RESUELTA**: la descomposicion se escribe como COLUMNAS NUEVAS en AMBOS formatos, XLSX y CSV gemelo (ademas del sidecar). Nombres exactos: `Tiempo pipeline (s)`, `Tiempo espera (s)`, y se conserva `Latencia e2e (ms)`.

- **XLSX y CSV (ambos, identicos)**: rellenar `TIempo de Registro Automatico (Segundos)` = `t_e2e_s` (3 decimales); `Latencia e2e (ms)` = `latencia_e2e_ms`; agregar/reutilizar `Tiempo pipeline (s)` y `Tiempo espera (s)` (nombres neutrales al canal; la espera del buzon es el caso particular de correo). Escritura idempotente en los dos archivos, preservando filas/columnas.
- **JSON de evaluacion**: merge por `id`. Escribir `tiempo_automatizado_s` solo cuando hay medicion numerica; NUNCA sobrescribir un valor no nulo con null; nunca debilitar `_a_float`.

**OQ5 RESUELTA**: el harness cubre SOLO web+correo (119 casos: 53 `formulario web` + 66 `correo electronico`). Los 81 casos de `llamada telefonica` los mide y carga el autor MANUALMENTE (fuera del harness). El harness DEBE reportar explicitamente el conteo de casos aun nulos (telefono pendiente); el JSON de evaluacion solo carga completo cuando el autor completa esos 81 valores. Actualizar `metadata.descripcion` si corresponde.
- **Verificacion**: `cd evaluation; pytest` carga el corpus y pasa UNA VEZ COMPLETO (tras el completado manual de telefono); antes de eso se espera `CorpusError` por los casos aun nulos y el reporte del conteo pendiente.

### D6: Message-ID deterministico y normalizacion de corchetes

`Message-ID: <corpus-<ID>@<dominio>>`. RFC 5322 exige los `<>`; el workflow toma `metadata['message-id']` tal cual, por lo que el backend puede almacenar `<corpus-R001@...>`. El harness normaliza quitando los `<>` al construir la clave esperada, de modo que la trazabilidad y la idempotencia sean estables ante el formato del header. Dominio configurable por env (`INGEST_CORPUS_MAIL_DOMAIN`, default `corpus.local`).

### D7: Sidecar sin descripciones

`data/corpus_resultados_n8n.json`: por caso `case_id`, `canal`, `incidente_id`, `numero_incidente`, `sector`, `revision`, `t_envio`, `ingresado_en`, `persistido_en`, `latencia_e2e_ms`, `t_pipeline_s`, `t_espera_s`, `t_e2e_s`, `origen_message_id` (correo), `confirmacion_recibida`, `t_confirmacion` (correo, D14), `error`. Sin `descripcion` por construccion.

### D8: Dominios de reloj y exclusion de anomalias

Todos los instantes se normalizan a UTC. Si `latencia_anomala` es `true`, `latencia_e2e_ms` es nulo, o `t_e2e_s <= 0`/`t_espera_s < 0` mas alla de un margen de skew, el caso se marca anomalo y se EXCLUYE del corpus y del analisis (se reporta, no se recorta a cero), en linea con `e2e-timing-instrumentation`.

### D9: Fallos ruidosos y corrida parcial

El harness termina con exit code distinto de cero si algun caso falla o queda anomalo, e imprime un resumen (ok/anomalos/saltados). `--dry-run` no realiza red ni escritura. `--limit`/`--only-channel` acotan el smoke.

### D10: Prerrequisitos de operacion (activar N8N + credenciales + alcance)

- Importar `n8n/workflow.json` en la instancia N8N, reemplazar los placeholders por IDs de credenciales reales (IMAP, SMTP, operador) y ACTIVAR el workflow (`active: true`).
- El login del harness toma `INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD` del entorno (nunca hardcodeado). El operador DEBE tener alcance de lectura sobre todos los sectores (`administrador_directorio`) para que el sondeo y la lectura por `id` funcionen.
- Buzon DEDICADO y limpio para correo. Documentar los placeholders que queden pendientes.

### D11: Privacidad

Nunca se loguea, imprime ni persiste una descripcion; ante error solo un label corto (`http502`, `timeout`, ...). Reutiliza el estilo de `ingest_corpus.py`/`pseudonymize_corpus.py`. Las descripciones del JSON ya estan pseudonimizadas.

### D12: TDD de la logica pura

Tests offline (sin red, `tmp_path`) para: derivacion de la metrica (pipeline/espera/e2e), construccion de payload web, generacion de Message-ID y su normalizacion, mapeo de canal (JSON y CSV), y escritores XLSX/CSV/JSON/sidecar (incluida la idempotencia y la no-sobrescritura con null). Se reutilizan los patrones de `test_ingest_corpus.py`.

### D13: Gobernanza

MEDIO. Las decisiones de metrica (OQ1/OQ3/OQ4) ya estan resueltas y registradas; quedan como prerequisito la dependencia c-69 (correlacion exacta / dedup web) y el completado manual de telefono por el autor. La corrida real (red + escritura) se revisa con el autor antes de ejecutar. No se habilita ni hardcodea ninguna credencial.

### D14: Confirmacion de correo como chequeo secundario (OQ4 RESUELTA)

El correo de confirmacion que el flujo N8N envia al remitente se usa como verificacion END-TO-END secundaria, ADEMAS de la lectura de los instantes de la API (que sigue siendo la medicion primaria y canonica).

- **Camino de recepcion SEPARADO (regla dura)**: el harness MUST NOT observar la confirmacion en la misma bandeja que alimenta el trigger IMAP de ingesta; un correo de confirmacion re-ingestado por el poller crearia un incidente espurio y contaminaria el corpus. Opciones, en orden de preferencia:
  - **A (preferida)**: una carpeta/etiqueta dedicada del buzon dedicado (p.ej. `Confirmaciones`) que el trigger `emailReadImap` de ingesta NO lee (este apunta solo a la bandeja de ingesta).
  - **B**: un segundo buzon dedicado exclusivo para confirmaciones, con el remitente del caso como direccion de retorno.
- **Deteccion**: el harness sondea ese camino separado (IMAP de solo lectura) y empareja la confirmacion con el caso por el `Message-ID`/asunto deterministico. Registra `t_confirmacion = now(UTC)` y `confirmacion_recibida`.
- **Metrica secundaria**: `t_confirmacion_s = t_confirmacion - t_envio` se guarda en el sidecar (D7) como evidencia de cierre percibido; NO reemplaza a `t_e2e_s` (derivada de los instantes de la API).
- **No bloqueante**: si la confirmacion no llega dentro del timeout, el caso se reporta con `confirmacion_recibida: false` sin invalidar la medicion primaria. El harness verifica antes de correr que el camino de confirmacion es distinto del de ingesta.

## Risks / Trade-offs

- **[Re-run web duplica (sin dedup)]** -> resuelto por el prerequisito `c-69` (dedup web, OQ2 delegada); hasta que c-69 exista, corrida unica documentada y el harness no reescribe el corpus si detecta duplicados inesperados.
- **[Correlacion de correo]** trafico ajeno al buzon o carrera -> correlacion exacta via contrato de lectura de c-69 (primaria); el fallback por ventana temporal queda documentado y mitigado (buzon dedicado, un caso en vuelo, ids reclamados).
- **[Confirmacion re-ingestada por el poller]** contamina el corpus -> camino de recepcion separado obligatorio (D14), verificado antes de la corrida.
- **[Corrida parcial / telefono nulo]** el JSON no carga hasta que el autor complete los 81 telefono -> merge idempotente + reporte del conteo de nulos; no escribir null; no debilitar `_a_float`.
- **[Skew de relojes]** `t_espera_s` negativo -> exclusion como anomalia, no clamp.
- **[PII]** -> default sobre JSON pseudonimizado; sidecar y logs sin descripcion (D7/D11).
- **[Alcance de lectura por rol]** el sondeo/listado puede no ver todos los casos -> exigir operador con alcance total (D10).

## Migration Plan

1. Sin migracion de esquema ni cambios en `App/**`.
2. Implementar por dependencia: logica pura (metrica/payload/Message-ID/mapeo/escritores) -> camino web -> camino correo -> write-back/merge -> runbook. El harness es implementable YA con el contrato de c-69 mockeado en tests.
3. Prerrequisito de corrida real: `c-69-dedup-correlacion-altas` implementado (dedup web + correlacion exacta de correo). Sin c-69, solo se corre con el fallback documentado o se pospone la corrida completa.
4. Prerrequisitos: activar N8N y cablear credenciales; exportar las credenciales de login desde el entorno; habilitar el camino de confirmacion separado (D14).
5. Smoke `--dry-run` y corrida acotada (`--limit`, `--only-channel`); luego corrida de web+correo (119). El completado manual de telefono (81) por el autor es lo que habilita la carga COMPLETA del JSON.
6. Rollback: revertir el commit; restaurar el respaldo de `data/` (no trackeado) y desactivar el workflow/credenciales.

## Open Questions

- **OQ1 (RESUELTA)** — Canonico de correo: confirmado D, `tiempo_automatizado_s = t_e2e_s` (poller-inclusivo) con `t_espera_s` aparte y `t_pipeline_s` como cota inferior (D1).
- **OQ2 (DELEGADA a c-69)** — Dedup web: lo resuelve `c-69-dedup-correlacion-altas`, prerequisito de c-68. No se edita `CHANGES.md` desde c-68.
- **OQ3 (RESUELTA)** — Descomposicion: columnas nuevas en XLSX Y CSV (`Tiempo pipeline (s)`, `Tiempo espera (s)`, `Latencia e2e (ms)`), ademas del sidecar (D5).
- **OQ4 (RESUELTA)** — Confirmacion de correo: chequeo end-to-end SECUNDARIO por camino de recepcion separado, sin romper la medicion primaria (D14).
- **OQ5 (RESUELTA)** — Fuente de telefono: los 81 valores de `llamada telefónica` los mide/carga el autor manualmente; el harness cubre web+correo (119) y reporta el conteo de nulos pendientes sin sobrescribir con null (D5).
- **OQ6 (DELEGADA a c-69)** — Correlacion de correo: exacta via el contrato de lectura de `c-69` (primaria); la ventana temporal queda solo como fallback documentado si el autor declina ese camino (D3).
