# Arnés de ejecución en seco (dry-run harness)

Validación local, reproducible y de **costo cero** del tramo compartido de registro
de incidentes (normalización, validación, login dinámico, `POST /api/v1/incidentes/`,
persistencia y clasificación), antes de configurar o consumir cualquier servicio pago.

- Implementación: `scripts/dry_run/`
- Entrypoint: `scripts/dry_run/dry_run.py`
- Alias opcional: `make dry-run`

> Esta guía permite operar el arnés sin leer el código. Los procedimientos de los
> canales correo y teléfono están marcados explícitamente por costo.

---

## 1. Qué verifica

| Grupo | Check | Qué prueba |
|-------|-------|------------|
| Stack | `stack:up` | El stack `mesa_local` se levanta y backend/n8n quedan sanos. |
| Guardarraíl | `guardrail:gemini-key` | La `GEMINI_API_KEY` efectiva es ficticia (no hay llamadas pagas a Gemini). |
| Guardarraíl | `guardrail:cost-guard-budget` | El presupuesto efectivo de la guarda de costo es cero (segunda capa de costo cero). |
| N8N | `n8n:import` | Importa una copia de costo cero del workflow (id estable `P7w2iELDu7O3e8B0`). |
| N8N | `n8n:activate` | El workflow queda activo y el webhook responde. |
| Preflight | `preflight:login` | `POST /api/v1/auth/login` devuelve `access_token`/`token_type`. |
| Preflight | `preflight:create-201` | Un alta válida con `Authorization: Bearer` responde 201. |
| Preflight | `preflight:min-length-422` | Una `descripcion` de menos de 10 caracteres responde 422. |
| Preflight | `preflight:missing-slash-307` | La ruta sin barra final se detecta como 307 (pierde `Authorization` y body). |
| Preflight | `preflight:webhook-reachable` | El webhook de N8N está alcanzable (registra el esquema `http`/`https`). |
| Recorrido | `e2e:webhook-response` | El incidente simulado del formulario web se envía por el webhook. |
| Recorrido | `e2e:persisted` | El incidente queda persistido y se recupera por la API. |
| Recorrido | `e2e:etapa` | La clasificación del incidente es un único registro y su etapa es la determinística. |
| Recorrido | `e2e:canal` | El incidente persistido tiene `canal_origen_id == 2` (formulario web). |
| Recorrido | `e2e:idempotencia` | Reenviar el mismo `origen_message_id` devuelve el mismo incidente y no duplica la fila. |
| Recorrido | `e2e:reintento` | (opt-in `--with-retry-fault`) Recuperación ante indisponibilidad transitoria del backend sin duplicado. |

Un recorrido verde por defecto son **15/15 checks** con exit code `0`; con
`--with-retry-fault` son **16/16**. Los checks del grupo `tls:*` (opt-in
`--with-tls`) se suman a esa base y se describen en el runbook de la referencia.

---

## 2. Prerrequisitos

| Herramienta / recurso | Verificación |
|-----------------------|--------------|
| Docker Engine + Docker Compose v2 | `docker compose version` |
| Python 3.12 (biblioteca estándar) | `python3 --version` |
| Stack `mesa_local` levantado y sano | `docker compose ps` (backend y n8n visibles) |
| Certificados TLS generados | `bash openssl/generate-certs.sh` (una vez) |

El stack se opera con el nombre de proyecto fijo `mesa_local`. No usar `-p` ni
nombres alternativos.

---

## 3. Guardarraíles de costo (obligatorios)

El costo cero se sostiene con **dos capas independientes** sobre el backend del
arnés, más una tercera barrera sobre los canales pagos:

1. **Gemini nunca es real (capa 1).** El arnés levanta el backend con un override
   de Compose (`scripts/dry_run/compose.dry-run.yml`) que inyecta una
   `GEMINI_API_KEY` ficticia. Antes de enviar nada, `guardrail:gemini-key` afirma
   la clave efectiva dentro del contenedor y **aborta** si detecta una clave real.
   El override no modifica `docker-compose.yml` ni `App/Backend/.env`.
2. **Presupuesto nulo (capa 2).** El mismo override fija
   `COST_GUARD_BUDGET_USD=0`. Con presupuesto cero, la guarda de costo (c-45)
   deniega cualquier escalada **antes** de emitir la petición al proveedor: ni
   siquiera se envía una petición de red con la clave falsa. El check
   `guardrail:cost-guard-budget` lee el valor efectivo dentro del contenedor y
   **aborta** si está ausente, no es numérico o es distinto de cero.
3. **Fallback seguro ante escalada.** Si una descripción no alcanza el umbral
   determinístico, la escalada es denegada por la guarda y degrada con
   `confianza=0.0` y revisión humana; no se completa ninguna llamada paga. El
   recorrido lo confirma con `e2e:etapa` (la clasificación del incidente de
   prueba debe ser de la etapa determinística).
4. **Twilio nunca se toca.** El arnés elimina del workflow los nodos con
   credenciales placeholder (incluido `Llamada telefonica`, entrada del canal
   telefónico) y no importa ni invoca el cliente de Twilio en ninguna variante.
   El canal telefónico es solo un procedimiento manual documentado (§7) y queda
   fuera del camino de costo cero.

> No debilitar estos guardarraíles. Si `guardrail:gemini-key` o
> `guardrail:cost-guard-budget` fallan, el arnés no envía incidentes.

---

## 4. Cómo ejecutar

```bash
# Opción recomendada (alias del Makefile)
make dry-run

# Equivalente directo
python3 scripts/dry_run/dry_run.py

# Si el stack ya está arriba y sano (evita recrear contenedores)
python3 scripts/dry_run/dry_run.py --skip-up

# Reutilizar stack e importar solo si hace falta
python3 scripts/dry_run/dry_run.py --skip-up --skip-import
```

Opciones útiles (todas tienen default):

| Opción | Default | Para qué |
|--------|---------|----------|
| `--base-url` | `https://localhost` | URL del borde (nginx) del backend. |
| `--n8n-host` / `--n8n-port` | `localhost` / `5678` | Ubicación de N8N publicada. |
| `--username` / `--password` | `admin` / `admin123` | Operador sembrado (la password nunca se imprime). |
| `--skip-up` | off | Reutiliza el stack en ejecución. |
| `--skip-import` | off | No reimporta/activa el workflow. |
| `--poll-timeout` | `45` | Ventana de sondeo de persistencia (segundos). |
| `--json` | off | Salida estructurada en JSON. |
| `--json-out` | off | Escribe un reporte JSON de evidencia (commit, fecha UTC, versión de N8N y resultado por check) en la ruta indicada. |
| `--with-email` | off | Variante opt-in del canal correo (§6). |
| `--with-retry-fault` | off | Opt-in: desconecta/reconecta el backend para verificar la recuperación ante indisponibilidad transitoria (`e2e:reintento`). Requiere el bloque de reintentos del workflow. |
| `--with-tls` | off | Opt-in: ejecuta el grupo `tls:*` sobre el borde del despliegue de referencia. Ver el runbook de la referencia. |

Credenciales opcionales por variable de entorno: `DRY_RUN_USERNAME`,
`DRY_RUN_PASSWORD`.

### 4.1 Reporte de evidencia (`--json-out`)

Con `--json-out RUTA` el arnés escribe, además del resumen en consola, un
archivo JSON versionable con:

- `commit` (`git rev-parse HEAD`), `timestamp_utc`, `n8n_version` del stack;
- `groups` ejecutados (prefijos de los nombres de check) y `summary`;
- `checks`: nombre, estado, detalle y acción de cada verificación.

El reporte **nunca** contiene la contraseña del operador, el token de acceso,
claves de API ni material criptográfico: los valores sensibles conocidos por el
arnés se sustituyen por `[REDACTED]` y los que coinciden con patrones de
credencial se redactan. Escribir el reporte **fuera** del repositorio (por
ejemplo en un directorio temporal) para no versionar salidas de una corrida
local.

---

## 5. Lectura de resultados y exit codes

```
[PASS] preflight:login - access_token received (token_type=bearer)
[FAIL] e2e:canal - observed canal_origen_id=3, expected 2
         next: the workflow must send canal_origen_id=2 for the web channel
```

| Exit code | Significado |
|-----------|-------------|
| `0` | Todos los checks ejecutados pasaron. |
| `1` | Quiebre de cableado, aborto temprano de preflight, o **cualquier check PENDING/incompleto**. |

Regla firme: una verificación omitida o incompleta **nunca** se reporta como
éxito; el resumen final muestra `RED` y el exit code es distinto de cero.

Cada `FAIL`/`PENDING` incluye una línea `next:` con el componente afectado y el
siguiente paso concreto.

---

## 6. Canal correo (gratuito, opcional)

Recibir correo es gratis: el trigger IMAP `emailReadImap` en N8N hace *polling* al buzón,
por lo que el canal correo **no tiene costo de uso** y queda fuera de los
guardarraíles de servicios pagos. Aun así, es **opcional**: el camino mínimo
obligatorio (recorrido web) se completa sin ninguna credencial de correo.

### 6.1 Procedimiento manual (sin automatizar)

Reproducible sin credenciales reales para el camino mínimo: si no se dispone de
credenciales de correo, ejecutar solo el recorrido web (§4). El procedimiento que
sigue requiere credenciales reales `imap`/`smtp`.

Credenciales requeridas:

- Credenciales `imap` y `smtp` en N8N (casilla Gmail dedicada con 2FA y App
  Password), asociadas al buzón que dispara el workflow y a los envíos `emailSend`.
- El workflow con la rama de correo activa (nodo `Llega un email a Mesa de Ayuda`).

Pasos:

1. **Inducir el mensaje.** Enviar un correo al buzón monitoreado con un asunto
   cualquiera y un **cuerpo de al menos 10 caracteres** (el cuerpo se usa como
   `descripcion`). Por ejemplo: `La impresora del sector no enciende`.
2. **Esperar el polling.** El trigger IMAP `emailReadImap` consulta el buzón
   periódicamente; dar unos minutos.
3. **Verificar la persistencia** con `canal_origen_id == 1`:

   ```bash
   TOKEN=$(curl -k -s -X POST https://localhost/api/v1/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"admin","password":"admin123"}' \
     | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

   # IDs recientes (el listado no trae canal_origen; usarlo solo para ubicar el id)
   curl -k -s -H "Authorization: Bearer $TOKEN" \
     "https://localhost/api/v1/incidentes/?limit=5"

   # Detalle del incidente: canal_origen.id debe ser 1
   curl -k -s -H "Authorization: Bearer $TOKEN" \
     "https://localhost/api/v1/incidentes/<ID>"
   ```

   Alternativa directa por base de datos:

   ```bash
   docker compose exec postgres psql -U mesa mesa_de_ayuda \
     -c "SELECT id, canal_origen_id, created_at FROM incidente ORDER BY id DESC LIMIT 5;"
   ```

### 6.2 Variante automatizada (opt-in, ausente del camino mínimo)

El arnés puede inducir el correo y verificar la persistencia por sí mismo, pero
**solo si se habilita explícitamente**. Por defecto **no se ejecuta** y no agrega
ningún check.

```bash
make dry-run-email
# o
python3 scripts/dry_run/dry_run.py --skip-up --with-email
```

Variables de entorno para la variante:

| Variable | Obligatoria | Default | Descripción |
|----------|-------------|---------|-------------|
| `DRY_RUN_EMAIL_SMTP_HOST` | sí | — | Servidor SMTP que entrega al buzón monitoreado. |
| `DRY_RUN_EMAIL_FROM` | sí | — | Remitente del correo de prueba. |
| `DRY_RUN_EMAIL_TO` | sí | — | Buzón monitoreado por el trigger IMAP. |
| `DRY_RUN_EMAIL_SMTP_PORT` | no | `587` | Puerto SMTP. |
| `DRY_RUN_EMAIL_SMTP_USER` | no | vacío | Usuario SMTP (si requiere autenticación). |
| `DRY_RUN_EMAIL_SMTP_PASSWORD` | no | vacío | Password SMTP (nunca se imprime). |
| `DRY_RUN_EMAIL_USE_TLS` | no | `true` | `starttls` antes de enviar. |

Comportamiento:

- Con `--with-email` y configuración completa: agrega `email:induced` y
  `email:persisted` (verifica `canal_origen_id == 1`).
- Con `--with-email` y configuración incompleta: agrega `email:config` como
  **PENDING** y el exit code es distinto de cero. Es un fallo deliberado: el
  operador pidió la variante y no la configuró.
- Sin `--with-email`: cero checks de correo. El arnés completa sin credenciales.

Prerrequisito para que la variante tenga éxito: la rama de correo IMAP del workflow
en N8N debe estar activa y con credenciales reales (§6.1).

---

## 7. Canal teléfono (manual, PAGO, fuera del camino de costo cero)

> **ADVERTENCIA DE COSTO.** El canal telefónico usa Twilio, que **cobra llamadas
> y transcripciones**. Este procedimiento está **fuera del camino de costo cero**
> y **no lo ejecuta el arnés**. Limitarse a **1 o 2 llamadas**.

El arnés elimina la rama de Twilio del workflow que importa, por lo que este canal
se valida directamente sobre el workflow completo cargado en N8N (con credenciales
reales), nunca a través del arnés.

Credenciales requeridas:

- Twilio **Account SID** y **Auth Token**.
- Número de Twilio habilitado para voz (número entrante).
- La credencial Header Auth `X-N8N-Secret` asignada al webhook `Llamada
  telefonica` (`POST /webhook/telefonia-handoff`) y el workflow completo activo.
  El handoff lo origina el backend; N8N no tiene ningún nodo de Twilio.

Pasos:

1. Cargar/activar el workflow completo (`n8n/workflow.json`) en N8N con la
   credencial de Twilio ya configurada.
2. Realizar **una o dos llamadas** al número de Twilio. Hablar una descripción
   válida (al menos 10 caracteres), por ejemplo: `La impresora del sector no
   enciende`.
3. Esperar a que Twilio genere la grabación; el backend la descarga, transcribe,
   pseudonimiza y dispara el handoff `POST /webhook/telefonia-handoff`.
4. **Verificar la persistencia** con `canal_origen_id == 3`:

   ```bash
   docker compose exec postgres psql -U mesa mesa_de_ayuda \
     -c "SELECT id, canal_origen_id, created_at FROM incidente ORDER BY id DESC LIMIT 5;"
   ```

   El incidente más reciente del canal telefónico debe tener
   `canal_origen_id = 3`. También puede confirmarse por API:

   ```bash
   curl -k -s -H "Authorization: Bearer $TOKEN" \
     "https://localhost/api/v1/incidentes/<ID>"
   ```

5. Detener la rama o desactivar la credencial al terminar para evitar llamadas
   accidentales facturadas.

---

## 8. Garantía sobre Twilio

El arnés **no marca, crea ni dispara** recursos ni llamadas de Twilio en ninguna
variante:

- La transformación de costo cero elimina del workflow los nodos con credenciales
  placeholder, incluido el nodo `Llamada telefonica` (entrada del canal telefónico).
- El código del arnés no importa ni invoca el cliente de Twilio.
- La variante de correo usa SMTP estándar y no toca Twilio.

Esto se cubre con pruebas en `scripts/dry_run/test_workflow_transform.py`
(no sobreviven nodos de tipo Twilio; la fuente no invoca la API de Twilio).

---

## 9. Solución de problemas

| Síntoma | Causa probable | Acción |
|---------|----------------|--------|
| `guardrail:gemini-key` FAIL | El backend no se levantó con el override de dry-run. | Volver a levantar con `-f scripts/dry_run/compose.dry-run.yml` (sin `--skip-up`). |
| `guardrail:cost-guard-budget` FAIL | El backend no tiene `COST_GUARD_BUDGET_USD=0` (falta el override o el valor no es cero). | Verificar `scripts/dry_run/compose.dry-run.yml` y volver a levantar con el override. |
| `preflight:login` FAIL | Operador no sembrado o backend no healthy. | Verificar `admin`/`admin123` y `docker compose logs backend`. |
| `preflight:missing-slash-307` FAIL | Cambió el contrato de rutas. | Revisar el enrutado del backend; los llamadores deben conservar la barra final. |
| `e2e:persisted` FAIL | El webhook no completó el registro en la ventana de sondeo. | Revisar `docker compose logs n8n` y el nodo HTTP POST del workflow. |
| `e2e:etapa` FAIL | La clasificación no es única o no es determinística. | Revisar la descripción de prueba y la guarda de costo; ver `docker compose logs backend`. |
| `e2e:canal` FAIL | El workflow envía un `canal_origen_id` distinto de 2. | Revisar el nodo `Marcar canal web`. |
| `e2e:idempotencia` FAIL | El reenvío duplicó el incidente o devolvió otro id. | Revisar el índice único de `origen_message_id` y el cortocircuito de idempotencia. |
| `e2e:reintento` FAIL | El backend no se recuperó dentro de la ventana o duplicó la fila. | Revisar la política de reintento del workflow y que el backend vuelva a la red `mesa_local_automation` con el alias `backend`. |
| `email:config` PENDING | Se usó `--with-email` sin configurar SMTP. | Definir `DRY_RUN_EMAIL_*` o quitar `--with-email`. |

---

## 10. Archivos relevantes

- `scripts/dry_run/dry_run.py` — entrypoint y orquestación (I/O).
- `scripts/dry_run/e2e_checks.py` — evaluadores puros de los checks E2E (sin red, sin Docker).
- `scripts/dry_run/checks.py` — modelo de checks, contrato de exit code y formato.
- `scripts/dry_run/compose.dry-run.yml` — override de costo cero (clave Gemini ficticia y presupuesto cero).
- `scripts/dry_run/test_checks.py`, `test_exit_contract.py`,
  `test_workflow_transform.py`, `test_email_variant.py`, `test_checks_c135.py` — pruebas del arnés.
- `docs/runbook-smoke-stack-referencia.md` — [runbook del despliegue de referencia](runbook-smoke-stack-referencia.md) (recorrido E2E y grupo TLS).
- `docs/operational-guide.md` — guía operativa general.

## 11. Ejecución en CI

Las pruebas **offline** del arnés (`python -m pytest scripts/dry_run -q`, desde
la raíz del repositorio) no requieren Docker, red ni secretos: cubren el modelo
de checks, el contrato de exit code, la transformación de costo cero y los
evaluadores puros, y son las que se suman al job `backend-tests` para que el
arnés no se degrade entre releases.

La corrida **completa** del arnés (con Docker) es local en esta release (decisión
OQ2 del change c-140): el resumen JSON de la corrida se conserva como evidencia.
El workflow de CI que levanta el stack y corre el arnés queda diferido; ver el
runbook del despliegue de referencia para los comandos de la corrida local.
