# Runbook de verificación en vivo — Telefonía C-52

Documento operativo para ejecutar la tarea **8.4** del change `c-52-telefonia-transcripcion-async`: una llamada telefónica real de punta a punta que no puede simularse offline. El runbook es una guía humana: se completa a medida que se ejecuta y el resultado se registra en la sección **Resultados**.

- Change: `openspec/changes/c-52-telefonia-transcripcion-async/`
- Gobernanza: CRITICAL (firma Twilio fail-closed, transcript cifrado, frontera de PII)
- Documentos de referencia: `verify-report.md` (Task 8.4, riesgos vivos), `design.md` (D1-D13), `specs/telefonia-stt-intake`, `docs/operational-guide.md` §11.2/§11.6/§11.7, `docs/n8n-workflow-guide.md` (canal telefonía), `docs/medicion-latencia-e2e.md` §5, `n8n/twilio/README.md`.

---

## 1. Objetivo

Verificar con una llamada real que el flujo asincrónico de telefonía del backend (C-52) funciona de punta a punta: Twilio graba, el backend descarga y transcribe con Gemini, pseudonimiza, persiste el ingreso y hace handoff autenticado a n8n, que crea el incidente.

El flujo a verificar es:

```
Llamada entrante
  -> POST /api/v1/cost-guard/twilio/voice          (webhook de voz, firma X-Twilio-Signature)
  -> <Say> + <Record mono, sin transcribe> con recordingStatusCallback y action
  -> POST /api/v1/telefonia/recording-status       (backend sella ingresado_en, idempotencia, reserva backend_stt, descarga, STT, pseudonimiza)
  -> POST /webhook/telefonia-handoff               (handoff, header X-N8N-Secret)
  -> n8n: Guard de costo -> Restaurar item telefonia -> AI Agent -> normalizador
  -> POST /api/v1/incidentes                       (alta con origen_message_id = CallSid)
```

## 2. Criterios de aceptación exactos (tarea 8.4)

La tarea 8.4 se marca como cumplida solo si la llamada de prueba produce TODOS estos resultados:

- [ ] Existe un incidente creado a partir de la llamada, con `descripcion` pseudonimizada **no vacía**.
- [ ] El incidente tiene `origen_message_id` igual al `CallSid` de la llamada.
- [ ] El ingreso persistió con `ingresado_en` (sellado por el backend al recibir el callback) **anterior** al trabajo de STT (es decir, `ingresado_en < persistido_en` en la fila de ingreso).
- [ ] La latencia quedó registrada: `ingresado_en` y `persistido_en` poblados en el ingreso, y `latencia_e2e_ms` disponible/derivable para el incidente.
- [ ] La descripción que cruzó a n8n y al incidente NO contiene PII cruda (no aparece el nombre/teléfono/dirección de correo tal como se enunciaron).

Referencia: `openspec/changes/c-52-telefonia-transcripcion-async/tasks.md` (8.4) y `verify-report.md` (sección "Task 8.4 Status").

## 3. Prerrequisitos

### 3.1 Stack arriba

- [ ] `docker compose up -d` desde la raíz del repo (nombre de proyecto fijo `mesa_local`; no usar `-p`).
- [ ] `docker compose ps` muestra `postgres`, `backend`, `n8n` (y `redis`) saludables.
- [ ] Backend responde: `curl -s http://localhost:8000/health`.
- [ ] n8n UI accesible: `http://localhost:5678`.

### 3.2 Variables de entorno del backend (`App/Backend/.env`)

Confirmar que cada variable tiene el valor real (no placeholder). Nombres EXACTOS:

- [ ] `TWILIO_ACCOUNT_SID` — usuario del HTTP Basic al descargar la grabación (`AccountSid:AuthToken`).
- [ ] `TWILIO_AUTH_TOKEN` — valida `X-Twilio-Signature` (HMAC-SHA1) y completa el Basic auth de descarga. Sin él, los webhooks responden 401 fail-closed.
- [ ] `TWILIO_PHONE_NUMBER` — número virtual comprado (referencia operativa; ver nota en §7).
- [ ] `BACKEND_PUBLIC_BASE_URL` — base pública del backend tal como la ve Twilio; construye `recordingStatusCallback` y `action` del `<Record>`. Debe coincidir con la URL configurada en la consola Twilio (esquema, host y puerto).
- [ ] `N8N_TELEFONIA_WEBHOOK_URL` — URL del webhook de handoff en n8n (p. ej. `http://n8n:5678/webhook/telefonia-handoff` desde el backend en compose).
- [ ] `N8N_WEBHOOK_SECRET` — secreto compartido del handoff, se envía como header `X-N8N-Secret`. Sin él el handoff se OMITE (`HANDOFF_SKIPPED_NO_SECRET`).
- [ ] `GEMINI_API_KEY` — clave de Google AI para el STT.
- [ ] `GEMINI_STT_MODEL` — modelo de transcripción (default `gemini-3.5-transcribe`).
- [ ] `PSEUDONYMIZATION_ENCRYPTION_KEY` — clave Fernet obligatoria; cifra `transcript_original` y `caller_cifrado` at-rest.
- [ ] `DATABASE_URL` — PostgreSQL (en compose apunta a `...@postgres:5432/mesa_de_ayuda`).
- [ ] `COST_GUARD_SHARED_SECRET` — secreto del endpoint de reserva que consume n8n (fuente única en el `.env` de la RAÍZ del repo dentro de compose).
- [ ] `COST_GUARD_UNIT_COST_BACKEND_STT_USD` — costo unitario estimado de la superficie `backend_stt` (default 0.0038).
- [ ] `PSEUDONYMIZATION_INTERNAL_DOMAINS` — dominios internos a enmascarar (opcional).

### 3.3 Consola de Twilio

- [ ] Cuenta Twilio operativa con crédito.
- [ ] Número virtual con capacidad **Voice** comprado.
- [ ] En **Phone Numbers > Manage > Active Numbers**, el número tiene "A call comes in" apuntando a `https://<host-publico>/api/v1/cost-guard/twilio/voice` con **Method: HTTP POST**.
- [ ] NO se usa TwiML Bin ni hosting estático (omitirían la guarda de costo).
- [ ] `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` de la consola coinciden con los del `.env`.

### 3.4 Exposición pública y proxy

- [ ] El backend es alcanzable por HTTPS desde internet. Opción de desarrollo con ngrok:
  - [ ] `ngrok http 443` (túnel hacia Nginx) o el puerto correspondiente al backend.
  - [ ] Copiar la URL pública (p. ej. `https://abc123.ngrok.io`).
  - [ ] Configurarla en la consola Twilio (voice webhook) y en `BACKEND_PUBLIC_BASE_URL`.
- [ ] `FORWARDED_ALLOW_IPS` habilitado en el servicio `backend` del compose para que `request.url` reconstruya el esquema `https` y el host públicos (sin esto, la firma sobre la URL pública no valida y aparecen 401 falsos; ver §7.1).

### 3.5 n8n

- [ ] Workflow importado desde `n8n/workflow.json`.
- [ ] Workflow **activo** (toggle ON en la UI).
- [ ] El nodo `Llamada telefonica` es un webhook `POST` en la ruta `/webhook/telefonia-handoff` con autenticación `headerAuth` (secreto `X-N8N-Secret`).
- [ ] El nodo `Guard de costo` tiene configurado `COST_GUARD_SHARED_SECRET` (`$env.COST_GUARD_SHARED_SECRET`).
- [ ] `BACKEND_URL` del workflow apunta al backend.

### 3.6 Acceso a datos para inspección

- [ ] Acceso a PostgreSQL del stack: host `localhost`, puerto `5433`, base `mesa_de_ayuda`, usuario `mesa` (password según el `.env` raíz).
- [ ] Alternativa: pgAdmin conectado a ese mismo host/puerto/base.
- [ ] Registro de logs del backend accesible: `docker compose logs -f backend` (eventos estructurados `telefonia_*`, `telefonia_handoff_*`, `n8n_*`).

## 4. Procedimiento paso a paso

### 4.1 Antes de llamar

- [ ] Abrir una terminal con `docker compose logs -f backend` para observar los eventos en vivo.
- [ ] (Opcional) Abrir la consola de Twilio en **Monitor > Logs > Calls** para seguir la llamada.
- [ ] Anotar el número Twilio de destino y el número desde el que se llamará.
- [ ] Confirmar los prerequisitos de §3.

### 4.2 Llamada de prueba

- [ ] Marcar el número Twilio desde un teléfono de prueba.
- [ ] Escuchar el `<Say>` de bienvenida ("Bienvenido a la mesa de ayuda...").
- [ ] Hablar un incidente realista en español rioplatense, incluyendo PII natural para ejercitar la pseudonimización. Ejemplo de referencia:
  > "Hola, soy Juan Pérez. No puedo iniciar sesión en el sistema de facturación desde ayer. Me sale un error de credenciales y mi correo es juan.perez@empresa.com."
- [ ] Esperar el tono (beep) e iniciar el mensaje.
- [ ] Presionar `#` al terminar (o dejar pasar hasta 45 s, tope de `maxLength`).
- [ ] Colgar la llamada.
- [ ] Escuchar/verificar que el `<Say>` de cierre ("Gracias. Estamos procesando tu mensaje...") se reproduce tras colgar/terminar la grabación.

### 4.3 Espera de callbacks

- [ ] Esperar el callback de estado de grabación (`POST /api/v1/telefonia/recording-status`); normalmente unos segundos tras finalizar la grabación.
- [ ] Esperar el handoff a n8n (`POST /webhook/telefonia-handoff`) y el alta del incidente.
- [ ] Tiempo total esperado: decenas de segundos (descarga + STT + clasificación). Si supera varios minutos, ver §7.

## 5. Verificación post-llamada

### 5.1 Fila de `telefonia_ingreso`

Conectarse a PostgreSQL y buscar la fila por `call_sid` (o por la más reciente):

```sql
SELECT
    id,
    call_sid,
    recording_sid,
    duracion_segundos,
    transcripcion_estado,
    descripcion_pseudonimizada,
    ingresado_en,
    persistido_en,
    (persistido_en - ingresado_en) AS delta_ingreso_persistencia,
    incidente_id,
    error_detalle,
    provider,
    model,
    created_at,
    updated_at
FROM telefonia_ingreso
ORDER BY created_at DESC
LIMIT 5;
```

Verificaciones:

- [ ] `transcripcion_estado = 'transcrito'`.
- [ ] `descripcion_pseudonimizada` no vacía.
- [ ] `ingresado_en` poblado.
- [ ] `persistido_en` poblado y `persistido_en > ingresado_en` (el sello precede al trabajo de descarga/STT/persistencia).
- [ ] `incidente_id` poblado (vínculo con el incidente creado).
- [ ] `call_sid` coincide con el CallSid de la llamada (visible en logs/Twilio).
- [ ] `error_detalle` es NULL (si no, ver §7).

Comprobar la doble representación y el cifrado del crudo (el crudo NO debe aparecer en claro al leer la columna física):

- [ ] `transcript_original` es ilegible a nivel columna (contenido cifrado Fernet, prefijo `gAAAA`); vía ORM devuelve el texto plano.
- [ ] `caller_cifrado` también está cifrado (o NULL si el callback no informó `From`).
- [ ] `transcript_original`/`caller_cifrado` NO se exponen por ningún endpoint REST.

### 5.2 Incidente creado

```sql
SELECT
    id,
    canal_origen_id,
    descripcion,
    origen_message_id,
    ingresado_en,
    persistido_en,
    created_at
FROM incidente
WHERE origen_message_id = '<CallSid de la llamada>'
ORDER BY created_at DESC
LIMIT 1;
```

Verificaciones:

- [ ] Existe exactamente UNA fila con `origen_message_id = <CallSid>` (índice único).
- [ ] `descripcion` no vacía y coincide con la `descripcion_pseudonimizada` del ingreso.
- [ ] `descripcion` NO contiene PII cruda: buscar explícitamente el nombre, el teléfono y el correo enunciados (p. ej. `juan.perez@empresa.com`, `Juan Pérez`, el número marcado). Deben estar enmascarados (`[EMAIL]`, `[PERSONA]`, `[TELEFONO]` o equivalentes).
- [ ] `canal_origen_id` corresponde al canal `telefonia`.
- [ ] `ingresado_en` del incidente coincide con el `ingresado_en` del ingreso (propagado como passthrough por n8n, sin re-sellar).

### 5.3 Latencia y sellado temporal

- [ ] Confirmar orden: `ingresado_en` (ingreso) < `persistido_en` (ingreso). El sello se toma en `POST /api/v1/telefonia/recording-status`, ANTES de descargar y transcribir.
- [ ] `latencia_e2e_ms` se deriva de `persistido_en - ingresado_en` en la capa de lectura (no es una columna física). Obtenerla vía:
  - [ ] la respuesta de la API del incidente (`GET /api/v1/incidentes/{id}`), o
  - [ ] el cálculo manual: `(persistido_en - ingresado_en)` en milisegundos.
- [ ] Si `latencia_e2e_ms` es negativa, el sistema la marca `latencia_anomala` y la excluye del corpus; registrar el caso en §8.
- [ ] Interpretación del canal (ver `docs/medicion-latencia-e2e.md` §5): la latencia **incluye** descarga + STT + pseudonimización + handoff, pero **NO** la duración de la llamada ni el tiempo previo de generación de la grabación en Twilio.

### 5.4 Evidencia en logs

- [ ] `docker compose logs backend` muestra:
  - [ ] ausencia de 401 en `/api/v1/telefonia/recording-status` (si hay 401, ver §7.1),
  - [ ] `telefonia_transcrito` con `call_sid` e `ingreso_id`,
  - [ ] `telefonia_handoff_sent` con `call_sid` (y NO `telefonia_handoff_skipped`/`telefonia_handoff_secret_missing`).
- [ ] En n8n, la ejecución del workflow muestra `Guard de costo` permitido, `AI Agent` con clasificación y el POST a `/api/v1/incidentes` con `201 Created`.

## 6. Registro de eventos y valores esperados

| Punto | Valor/estado esperado | Evento de log / columna |
|-------|-----------------------|-------------------------|
| Callback de grabación | procesado (no 401) | `telefonia_transcrito` |
| Estado del ingreso | `transcrito` | `telefonia_ingreso.transcripcion_estado` |
| Sello de ingreso | anterior a la STT | `ingresado_en < persistido_en` |
| Handoff a n8n | enviado | `telefonia_handoff_sent` |
| Incidente | única fila por CallSid | `incidente.origen_message_id = CallSid` |
| PII | enmascarada | `incidente.descripcion` sin datos crudos |

## 7. Troubleshooting

### 7.1 401 falso por reconstrucción de la URL firmada (proxy)

Síntoma: el callback de Twilio responde 401 aunque la petición provenga de Twilio. Causa: Twilio firma la URL pública configurada en su consola, pero FastAPI reconstruye `request.url` a partir de los headers reenviados; un desajuste (esquema, host, puerto, path o query) invalida la firma.

- [ ] Verificar que `BACKEND_PUBLIC_BASE_URL` y la URL configurada en la consola Twilio sean EXACTAMENTE la misma (esquema `https`, mismo host, mismo path).
- [ ] Verificar que el backend confíe en los headers del proxy: `FORWARDED_ALLOW_IPS` definido en el servicio `backend` del compose (Nginx reenvía `X-Forwarded-Proto` y `Host`).
- [ ] Confirmar que Nginx **sobrescribe** `X-Forwarded-Proto` con `$scheme` (un cliente externo no debe poder falsificar el esquema).
- [ ] Si el backend se expone fuera de este compose, ajustar `FORWARDED_ALLOW_IPS` a la subred del proxy (nunca vacío).
- [ ] Comprobar en logs que la URL reconstruida coincide con la pública (ver `docs/operational-guide.md` §11.6).

### 7.2 Calidad de transcripción `es-419`

Síntoma: transcripción con errores, cortes o términos mal reconocidos.

- [ ] Confirmar `GEMINI_STT_MODEL=gemini-3.5-transcribe` y que el cliente usa `language_codes=["es-419"]` (es-AR NO está soportado).
- [ ] Verificar que el modo es verbatim (sin resumen/alucinación) y `store=False`.
- [ ] Revisar el audio descargado (formato `.wav`/`.mp3`) y la duración informada; grabaciones muy cortas o con ruido degradan el resultado.
- [ ] Comparar `transcript_original` (cifrado, vía ORM) contra `descripcion_pseudonimizada` para separar un problema de STT de uno de pseudonimización.
- [ ] Si la calidad es sistemáticamente baja con voseo/rioplatense, registrarlo como riesgo vivo (no es un fallo del pipeline).

### 7.3 Handoff omitido

Síntoma: no llega nada a n8n; el ingreso queda `transcrito` pero sin incidente.

- [ ] `HANDOFF_SKIPPED_NO_URL`: `N8N_TELEFONIA_WEBHOOK_URL` vacío o incorrecto. Log: `telefonia_handoff_skipped` con `reason=url_not_configured`. Cargar la URL y reiniciar el backend.
- [ ] `HANDOFF_SKIPPED_NO_SECRET`: `N8N_WEBHOOK_SECRET` vacío. Log: `telefonia_handoff_secret_missing` (nivel ERROR). Un handoff sin autenticar NO se envía (no es éxito silencioso). Cargar el secreto y reiniciar.
- [ ] `HANDOFF_FAILED`: la entrega HTTP falló (log `telefonia_handoff_failed` con `error_class`). Verificar que n8n esté arriba, el workflow activo, la ruta `/webhook/telefonia-handoff` y el `headerAuth` coincidente.
- [ ] Recordar: el handoff es fire-and-forget; su resultado NO bloquea la respuesta HTTP del callback ni se persiste como estado. La observabilidad es por logs estructurados. Recuperación: reejecutar el handoff o reintentar el alta (ver §7.5).

### 7.4 Denegación de la guarda de costo

Síntoma A (antes de grabar): el `<Say>` indica servicio no disponible y cuelga. La admisión de voz fue denegada; NO se grabó. Revisar `cost_guard_tripped` / `cost_guard_store_unavailable` y el presupuesto (`COST_GUARD_BUDGET_USD`) o los límites de tasa.

Síntoma B (al transcribir): el ingreso queda con `transcripcion_estado = 'guarda_denegada'` y `error_detalle` poblado; no se descarga ni transcribe. Log `telefonia_fallo`. Causas: bolsa global agotada, rate global (`COST_GUARD_RATE_LIMIT_CALLS`) o por origen (`COST_GUARD_CALLER_RATE_LIMIT_CALLS`) excedidos.

- [ ] Verificar presupuesto y ventana (`COST_GUARD_BUDGET_WINDOW_SECONDS`).
- [ ] Recordar que `backend_stt` y la admisión de voz Twilio comparten la MISMA bolsa global.
- [ ] Para una prueba controlada, ajustar temporalmente el presupuesto (y revertirlo al terminar).
- [ ] Si el almacén de contadores cayó, la política default es `fail_closed`.

### 7.5 Idempotencia ante callbacks repetidos

- [ ] Un callback repetido con el MISMO `CallSid` sobre un ingreso ya `transcrito` o `pendiente` es un no-op: no re-descarga, no re-reserva, no re-transcribe. Log: `telefonia_idempotente`.
- [ ] A nivel incidente, `origen_message_id` es único: un replay devuelve el incidente existente sin crear una segunda fila ni una segunda latencia (`docs/medicion-latencia-e2e.md` §6).
- [ ] Reintento automatico (W5): si el ingreso quedo en un estado terminal de error (`error_descarga`, `error_stt` o `guarda_denegada`), un callback repetido del mismo `CallSid` REPROCESA la MISMA fila tras un reclamo atomico. Logs: `telefonia_reintento` (reclamo ganado) o `telefonia_reintento_no_reclamado` (otro reintento ya lo tomo).
- [ ] Codigos de respuesta del callback: `error_descarga`/`error_stt` -> 503 (Twilio reintenta de forma nativa); `transcrito`/`pendiente`/`guarda_denegada` -> 200. El estado de error se confirma antes del 503 para que el reintento encuentre la fila.
- [ ] `guarda_denegada` NO dispara reintento automatico (la causa es una decision de negocio); una vez liberado el presupuesto, se recupera con un callback posterior del mismo `CallSid`.
- [ ] En un reintento se preserva `ingresado_en` (sello de auditoria) y se reserva costo por intento.
- [ ] No modificar manualmente `call_sid` para forzar reintentos en la base operativa.

## 8. Resultados (completar al ejecutar)

### 8.1 Datos de la ejecución

- Fecha/hora de la llamada:
- Operador:
- Número Twilio (destino):
- Número desde el que se llamó:
- `CallSid`:
- `RecordingSid`:
- URL pública usada (`BACKEND_PUBLIC_BASE_URL`):
- Modelo STT y código de idioma:

### 8.2 Transcripción y pseudonimización

- Texto enunciado (referencia, con PII de prueba):
- `transcript_original` (si se inspeccionó vía ORM; marcar si no se accedió):
- `descripcion_pseudonimizada` (pegar resultado real):
- PII detectada en claro en el incidente: SI / NO (si SI, detallar):

### 8.3 Verificación de aceptación (tarea 8.4)

| Criterio | Resultado (SI/NO) | Evidencia |
|----------|-------------------|-----------|
| Incidente creado | | `incidente.id =` |
| `descripcion` pseudonimizada no vacía | | texto de §8.2 |
| `origen_message_id = CallSid` | | |
| `ingresado_en < persistido_en` | | timestamps |
| Latencia registrada/derivable | | `latencia_e2e_ms =` |
| Sin PII cruda en el incidente | | |
| `telefonia_ingreso.transcripcion_estado = 'transcrito'` | | |
| `incidente_id` vinculado en el ingreso | | |

### 8.4 Logs y observaciones

- Eventos relevantes del backend:
- Estado del workflow en n8n:
- Incidencias encontradas (con causa raíz si se identificó):
- Desviaciones respecto de este runbook:

### 8.5 Conclusión

- Resultado global: APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO
- ¿Se puede marcar la tarea 8.4 como cumplida con esta evidencia? SI / NO
- Notas para el orquestador / próximos pasos:
