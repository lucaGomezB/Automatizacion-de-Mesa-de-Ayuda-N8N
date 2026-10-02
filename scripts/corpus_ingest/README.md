# corpus_ingest

Harness que carga el corpus de la tesis (`data/Corpus Tesis.xlsx` hoja 1 y su
gemelo `data/Corpus Tesis - Hoja 1.csv`, 200 casos) en el backend FastAPI que
esta corriendo, para que el sistema registre, clasifique y mida cada incidente
SIN realizar llamadas telefonicas (el corpus es texto; no hay audio).

Escribe los resultados de vuelta en AMBOS archivos y deja un sidecar de
trazabilidad. NUNCA imprime ni loguea descripciones.

## Archivos

| Archivo | Rol |
|---------|-----|
| `ingest_corpus.py` | Harness CLI + logica pura (mapeo de canal, payload, escritura XLSX/CSV). |
| `test_ingest_corpus.py` | Tests unitarios offline (sin red, con fixtures temporales). |
| `ingest_via_n8n.py` | Harness de ingesta POR el flujo N8N real (web + correo) con la metrica hibrida D. |
| `test_ingest_via_n8n.py` | Tests offline de la logica pura, los caminos web/correo y los escritores. |
| `pseudonymize_corpus.py` | Genera una copia pseudonimizada del CSV del corpus (Ley 25.326). |
| `test_pseudonymize_corpus.py` | Tests unitarios offline del pseudonimizador de corpus. |
| `requirements.txt` | Dependencias (`requests`, `openpyxl`). |

## Instalacion

```bash
pip install -r scripts/corpus_ingest/requirements.txt
```

`openpyxl` NO viene preinstalado en el host (pandas 3.x si). Sin el, el harness
puede leer el CSV pero no puede tocar el XLSX.

## Credenciales (obligatorias)

El harness lee las credenciales de un operador SOLO desde el entorno. No hay
secretos hardcodeados en el codigo.

```bash
export INGEST_OPERATOR_USERNAME='<usuario del operador>'
export INGEST_OPERATOR_PASSWORD='<password del operador>'
```

> El usuario seed de desarrollo y su password estan documentados en la
> migracion `003_add_users_table.py`; no se repiten literalmente aca (higiene
> de secretos). En un entorno real usar un operador dedicado.

Si alguna variable falta, el harness aborta con un mensaje claro y exit code 2.

## Uso

```bash
# 0) Smoke sin red ni escritura: parsea y reporta conteos por canal.
python scripts/corpus_ingest/ingest_corpus.py --dry-run

# 1) Corrida real contra nginx (certificado autofirmado) con los defaults.
export INGEST_OPERATOR_USERNAME='<usuario del operador>'
export INGEST_OPERATOR_PASSWORD='<password del operador>'
python scripts/corpus_ingest/ingest_corpus.py --base-url https://localhost --insecure

# 2) Smoke acotado: primeros 5 casos de un solo canal.
python scripts/corpus_ingest/ingest_corpus.py --insecure --only-channel Telefono --limit 5
```

### Flags

| Flag | Default | Descripcion |
|------|---------|-------------|
| `--base-url` | `https://localhost` | URL base (nginx). Acepta `http://...`. |
| `--insecure` | off | Acepta el certificado autofirmado (para de desarrollo). |
| `--csv` | `data/Corpus Tesis - Hoja 1.csv` | Ruta del CSV a actualizar. |
| `--xlsx` | `data/Corpus Tesis.xlsx` | Ruta del XLSX a actualizar en el lugar. |
| `--sidecar` | `data/corpus_resultados.json` | JSON de trazabilidad (sin descripciones). |
| `--source` | `csv` | Fuente de lectura: `csv` o `xlsx` (hoja 1). |
| `--only-channel` | — | Filtra por canal (`Correo`, `Formulario Web`, `Telefono`). |
| `--limit` | — | Procesa solo los primeros N casos. |
| `--sleep` | `0.5` | Segundos de espera entre casos (amistad con la latencia). |
| `--timeout` | `30` | Timeout HTTP por request en segundos. |
| `--dry-run` | off | Solo parsea y reporta. Sin red, sin escritura. |

## Flujo por caso

1. `POST /api/v1/auth/login` con `{username, password}` -> Bearer JWT.
2. `POST /api/v1/incidentes/` con:
   - `descripcion` = texto del caso (nunca se loguea),
   - `canal_origen_id` = mapeado (Correo=1, Formulario Web=2, Telefono=3),
   - `origen_evento` = `"creacion_incidente"`,
   - `origen_message_id` = `"corpus-<ID>"` (determinista -> idempotente),
   - `ingresado_en` = instante UTC ISO-8601 con zona explicita.
3. Se mide el wall-clock del POST->respuesta y se lee `latencia_e2e_ms` del JSON.
4. Se registra `incidente_id`, `numero_incidente`, `sector`, `requiere_revision_humana`,
   wall-clock, `latencia_e2e_ms` y error (si lo hubo).

Reintentos: solo 5xx y timeouts, con backoff exponencial (hasta 3 intentos). Los
4xx no se reintentan. Secuencial, con `--sleep` entre casos (el clasificador
hibrido puede pegarle a Gemini y devolver 503 transitorios).

## Estrategia de escritura (idempotente)

- **XLSX (hoja 1, en el lugar)**: rellena la columna existente
  `TIempo de Registro Automatico (Segundos)` y agrega/actualiza al final la
  columna `Latencia e2e (ms)`. El resto de columnas y filas se preservan.
  Si la columna de latencia ya existe, se reutiliza (no se duplica).
- **CSV (gemelo)**: misma operacion, preservando fila de titulo, encabezado y
  quoting minimo original (`\r\n`, `QUOTE_MINIMAL`).
- **Sidecar** `data/corpus_resultados.json`: lista por caso con `case_id`,
  `incidente_id`, `numero_incidente`, `sector`, `revision`, `wall_s`,
  `latencia_e2e_ms`, `error`. NO contiene descripciones.
- Re-ejecutar es seguro: actualiza las mismas dos columnas, no duplica columnas,
  y del lado servidor el `origen_message_id` determinista devuelve el incidente
  existente sin reclasificar ni volver a llamar a Gemini.

## Caveats de fidelidad

- **No hay STT.** El corpus es texto. Para `Telefono`, el flujo real es
  grabacion -> speech-to-text; aca el texto se ingesta directamente. La latencia
  medida NO incluye transcripcion.
- **El clasificador es el del backend (hibrido: reglas deterministicas +
  Gemini)**, no el AI Agent de n8n que usa el canal telefonico real. Los sectores
  predichos pueden diferir del agente de produccion.
- **"Tiempo automatico" = wall-clock del cliente** midiendo el POST->respuesta.
  `latencia_e2e_ms` es la metrica derivada por el backend
  (`persistido_en - ingresado_en`). Son dos cosas distintas y ambas se guardan.
- En un re-run idempotente, `latencia_e2e_ms` del JSON es la del alta original
  (el incidente ya existente conserva sus instantes); el wall-clock si es el
  actual.

## Privacidad

- Las descripciones son texto interno real. El harness no las imprime, no las
  loguea y no las escribe en el sidecar.
- Ante error solo se reporta un label corto (`http502`, `timeout`, ...), nunca
  el cuerpo de la respuesta.

## Ingesta por el flujo N8N real (`ingest_via_n8n.py`)

`ingest_corpus.py` hace un POST DIRECTO al backend y mide el wall-clock del
POST. No ejercita el flujo real de N8N ni la espera del poller de correo.
`ingest_via_n8n.py` SI: carga el corpus POR el flujo N8N para los canales
**web** y **correo** (119 casos) y deriva la metrica hibrida D por caso.

> **Telefono (81 casos) esta FUERA DE ALCANCE.** El harness lo omite y nunca
> escribe `null` sobre su `tiempo_automatizado_s`; lo reporta como pendiente y
> el autor lo carga MANUALMENTE.

### Metrica hibrida (D1)

Con `t_envio` = reloj UTC del harness (inmediatamente antes del POST al webhook
o del envio SMTP) y los instantes de `IncidenteRead`:

| Componente | Formula | Significado |
|------------|---------|-------------|
| `t_pipeline_s` | `latencia_e2e_ms / 1000` = `persistido_en - ingresado_en` | Pipeline libre del poller |
| `t_espera_s` | `ingresado_en - t_envio` | Correo: entrega SMTP + espera en el buzon; web: red/cola |
| `t_e2e_s` | `persistido_en - t_envio` = `t_espera_s + t_pipeline_s` | Extremo a extremo percibido |

`tiempo_automatizado_s = t_e2e_s` para AMBOS canales. En correo INCLUYE la
espera del poller (hasta ~60 s por `everyMinute`); el analisis reporta
`t_espera_s` por separado y `t_pipeline_s` como cota inferior libre de poller,
por canal (ver `docs/medicion-latencia-e2e.md` §5). Un caso es **anomalo** y se
excluye (se reporta, no se recorta a cero) si la latencia es nula/negativa, la
metrica no es positiva o la espera es negativa mas alla del margen de skew.

### Uso

```bash
# 0) Smoke sin red ni escritura: conteos por canal + nulos pendientes.
python3 scripts/corpus_ingest/ingest_via_n8n.py --dry-run

# 1) Corrida real (requiere N8N activo, credenciales y el camino de
#    confirmacion separado; ver runbook abajo).
export INGEST_OPERATOR_USERNAME='<operador con alcance total>'
export INGEST_OPERATOR_PASSWORD='<password>'
python3 scripts/corpus_ingest/ingest_via_n8n.py --insecure

# 2) Smoke acotado por canal.
python3 scripts/corpus_ingest/ingest_via_n8n.py --insecure --only-channel web --limit 2
python3 scripts/corpus_ingest/ingest_via_n8n.py --insecure --only-channel correo --limit 2
```

| Flag | Default | Descripcion |
|------|---------|-------------|
| `--base-url` | `https://localhost` | URL base del backend (nginx). |
| `--webhook-url` | `http://localhost:5678/webhook/incidente-web` | Webhook web de N8N. |
| `--insecure` | off | Acepta certificado autofirmado. |
| `--source` | `json` | Fuente: `json` (evaluacion pseudonimizado), `csv` o `xlsx`. |
| `--json` | `data/corpus_evaluacion_pseudonimizado.json` | JSON de evaluacion a mergear. |
| `--csv` / `--xlsx` | corpus gemelo | Archivos de registro a actualizar. |
| `--sidecar` | `data/corpus_resultados_n8n.json` | Trazabilidad (sin descripciones). |
| `--only-channel` | — | Filtra canal (`correo`, `web`, `telefono`). |
| `--limit` | — | Procesa solo los primeros N. |
| `--sleep` / `--timeout` | `0.5` / `30` | Espera entre casos / timeout HTTP. |
| `--poll-timeout` / `--poll-interval` | `90` / `5` | Sondeo del backend para correlacion de correo. |
| `--confirmation-timeout` / `--confirmation-interval` | `60` / `5` | Chequeo secundario de confirmacion. |
| `--mail-domain` | env `INGEST_CORPUS_MAIL_DOMAIN` (`corpus.local`) | Dominio del `Message-ID`. |
| `--dry-run` | off | Solo parsea y reporta. Sin red, sin escritura. |

### Camino web

`t_envio` -> `POST <webhook-url>` con
`{descripcion, prioridad, origen_message_id: "corpus-<ID>"}` -> la respuesta
trae `incidente_id` -> `GET /api/v1/incidentes/{id}` para leer los instantes. El
`origen_message_id` deterministico lo aporta el llamador (c-69): un re-run
devuelve el incidente existente SIN duplicar (dedup server-side).

### Camino correo

`t_envio` -> envio SMTP al buzon dedicado con `Message-ID:
<corpus-<ID>@<dominio>>` (deterministico) -> el trigger IMAP (`everyMinute`) lo
procesa y el normalizador usa ese `Message-ID` como `origen_message_id` ->
el harness sondea `GET /api/v1/incidentes/?origen_message_id=<clave>` (filtro
exacto de c-69) reclamando solo un incidente con `ingresado_en >= t_envio` ->
`GET /api/v1/incidentes/{id}`. La correlacion exacta es PRIMARIA; la ventana
temporal es solo un fallback documentado.

### Chequeo secundario de confirmacion (D14)

El correo de confirmacion al remitente es una verificacion END-TO-END
**secundaria** (la medicion primaria son los instantes de la API). Se observa
por un camino de recepcion **SEPARADO** (carpeta/buzon dedicado que el trigger
IMAP de ingesta NO lee) para que la confirmacion no se re-ingeste como un
incidente espurio. Si no llega dentro del timeout, el caso queda con
`confirmacion_recibida: false` sin invalidar `t_e2e_s`.

El observer IMAP se construye SOLO si estan definidos el host y el usuario de
confirmacion; si no, `confirmation_observer` queda en `None` (comportamiento no
bloqueante). Antes de cualquier ingesta de correo, si el observer esta activo el
harness ejecuta un **guard de separacion**: compara el camino de confirmacion
con el de ingesta y **ABORTA con exit code != 0** si apuntan al mismo
buzon/carpeta (regla dura: la confirmacion nunca se lee de la bandeja que
alimenta el trigger de ingesta). La lectura es IMAP de solo lectura
(`IMAP4_SSL`, `select(readonly=True)`) y nunca imprime la descripcion ni un
secreto.

Variables de entorno (nombres exactos; tambien en `scripts/corpus_ingest/ingest.env`):

| Variable | Default | Rol |
|----------|---------|-----|
| `INGEST_CONFIRMATION_IMAP_HOST` | — | Host IMAP del camino de confirmacion. Si falta, el observer no se activa. |
| `INGEST_CONFIRMATION_IMAP_PORT` | `993` | Puerto IMAP (SSL). |
| `INGEST_CONFIRMATION_IMAP_USER` | — | Usuario del buzon de confirmacion. Si falta, el observer no se activa. |
| `INGEST_CONFIRMATION_IMAP_PASSWORD` | — | Password/App Password (nunca se imprime). |
| `INGEST_CONFIRMATION_IMAP_FOLDER` | `INBOX` | Carpeta de confirmacion (debe ser distinta de la de ingesta). |
| `INGEST_INGEST_IMAP_HOST` | — | Host de la bandeja que alimenta el trigger de ingesta (guard). |
| `INGEST_INGEST_IMAP_USER` | — | Usuario de esa bandeja (guard). |
| `INGEST_INGEST_IMAP_FOLDER` | `INBOX` | Carpeta de esa bandeja (guard). |

El guard rechaza el mismo host+usuario+carpeta. Distinta carpeta en la misma
cuenta, o distinto host/usuario, se aceptan.


### Escritura (idempotente)

- **XLSX y CSV (ambos)**: `TIempo de Registro Automatico (Segundos)` = `t_e2e_s`
  (3 decimales); `Latencia e2e (ms)` = `latencia_e2e_ms`; columnas nuevas
  `Tiempo pipeline (s)` y `Tiempo espera (s)`. Re-ejecutar no duplica columnas
  ni sobrescribe un valor previo con vacio.
- **JSON de evaluacion**: merge de `tiempo_automatizado_s` numerico por `id`.
  Nunca escribe `null` sobre un valor no nulo; no debilita
  `evaluation/corpus.py::_a_float`. Reporta el conteo de casos aun nulos
  (telefono pendiente).
- **Sidecar** `data/corpus_resultados_n8n.json`: sin descripciones por
  construccion (solo ids, instantes y tiempos).

### Runbook: activar N8N y cablear credenciales

1. **Importar** `n8n/workflow.json` en la instancia N8N.
2. **Reemplazar los placeholders** por IDs de credenciales reales:
   - `REPLACE_WITH_IMAP_CREDENTIAL_ID` (buzon de ingesta, `INBOX`).
   - `REPLACE_WITH_SMTP_CREDENTIAL_ID` (envio de confirmacion).
   - `REPLACE_WITH_OPERATOR_LOGIN_CREDENTIAL_ID` (login del operador que usa
     el workflow para el POST al backend).
   - `REPLACE_WITH_REDIS_CREDENTIAL_ID` y `REPLACE_WITH_GEMINI_CREDENTIAL_ID`
     (telefonia, fuera del alcance del harness pero parte del workflow).
3. **Activar** el workflow (`active: true`).
4. **Operador con alcance total**: el login del harness
   (`INGEST_OPERATOR_USERNAME`/`INGEST_OPERATOR_PASSWORD`) debe corresponder a
   un operador con alcance de lectura sobre todos los sectores
   (`administrador_directorio`), o el sondeo/lectura por `id` no vera los casos.
5. **Camino de confirmacion separado**: definir una carpeta/buzon dedicado
   (p.ej. `Confirmaciones`) NO leido por el trigger de ingesta; el trigger
   apunta a `INBOX`. Variables de IMAP de confirmacion descritas abajo.
6. **Variables de entorno** (nunca hardcodeadas):
   - `INGEST_OPERATOR_USERNAME`, `INGEST_OPERATOR_PASSWORD` (login backend).
   - `INGEST_SMTP_HOST`, `INGEST_SMTP_PORT` (default `465`), `INGEST_SMTP_USER`,
     `INGEST_SMTP_PASSWORD`, `INGEST_SMTP_FROM`.
   - `INGEST_MAILBOX_ADDRESS` (destinatario de ingesta y remitente de retorno).
   - `INGEST_CORPUS_MAIL_DOMAIN` (dominio del `Message-ID`; default
     `corpus.local`).
   - **IMAP de confirmacion** (solo lectura, camino separado; ver la tabla de la
     seccion D14): `INGEST_CONFIRMATION_IMAP_HOST`, `INGEST_CONFIRMATION_IMAP_PORT`
     (default `993`), `INGEST_CONFIRMATION_IMAP_USER`,
     `INGEST_CONFIRMATION_IMAP_PASSWORD`, `INGEST_CONFIRMATION_IMAP_FOLDER`
     (default `INBOX`). Para el guard de separacion, exportar ademas
     `INGEST_INGEST_IMAP_HOST`, `INGEST_INGEST_IMAP_USER` y
     `INGEST_INGEST_IMAP_FOLDER` (default `INBOX`). Estas dos ultimas describen
     la bandeja de ingesta del trigger; sus valores NO deben coincidir con los de
     confirmacion. No se hardcodea ninguna credencial y no hay flags de CLI para
     secretos de IMAP (solo se leen del entorno).
7. **Placeholders pendientes** si aun no se cablearon: IDs de credenciales de
   IMAP/SMTP/operador y la carpeta de confirmaciones. Documentarlos antes de la
   corrida real.

### Gates de la corrida COMPLETA

- **`c-69-dedup-correlacion-altas` (implementado)**: dedup web y correlacion
  exacta de correo. Sin el, solo aplica el fallback documentado o se pospone.
- **Completado manual de los 81 telefono por el autor**: gatea la carga
  COMPLETA del JSON de evaluacion. Hasta entonces el harness reporta el conteo
  de nulos pendientes.

## Pseudonimizacion del corpus (`pseudonymize_corpus.py`)

Genera una copia PSEUDONIMIZADA del CSV del corpus para poder publicarlo
(Ley 25.326 de Proteccion de Datos Personales). El unico campo de texto libre es
`Descripcion`; ahi pueden venir nombres de personas, emails, telefonos y
hostnames. La publicacion (destrackear `data/Corpus Tesis*` en `.gitignore` y
commitear) es un paso MANUAL y separado que este script NO ejecuta.

Reutiliza el pseudonimizador de PRODUCCION
(`App/Backend/app/utils/pseudonymizer.py`) como unica fuente de verdad de los
patrones; no reimplementa regexes. Solo necesita CSV + stdlib: `openpyxl` NO es
requerido y el XLSX no se toca.

```bash
# 0) Smoke sin escritura: reporta conteos de reemplazo y PII residual.
python3 scripts/corpus_ingest/pseudonymize_corpus.py --dry-run

# 1) Corrida real: escribe data/Corpus Tesis - Hoja 1 (pseudonimizado).csv
python3 scripts/corpus_ingest/pseudonymize_corpus.py
```

### Flags

| Flag | Default | Descripcion |
|------|---------|-------------|
| `--csv` | `data/Corpus Tesis - Hoja 1.csv` | CSV de entrada (crudo). Nunca se sobrescribe. |
| `--out` | `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` | CSV de salida. No puede ser igual a `--csv`. |
| `--internal-domains` | env `PSEUDONYMIZATION_INTERNAL_DOMAINS` | Dominios corporativos a enmascarar como `[HOST]` (coma o lista JSON). |
| `--dry-run` | off | Calcula y reporta, sin escribir archivos. |

### Garantias

- Enmascara SOLO la columna `Descripcion`; fila de titulo, encabezado y el resto
  de las columnas se preservan. Row count y estilo (`\r\n`, quoting minimal)
  intactos.
- Reporta conteos AGREGADOS por categoria (email/telefono/host/persona). Nunca
  imprime ni loguea texto de caso.
- Escaneo residual post-enmascarado (email/telefono): si queda PII visible,
  el proceso termina con exit code distinto de cero.
- No sobrescribe el archivo de entrada (si `--out == --csv`, aborta con exit 2).

Los dominios internos se derivan igual que produccion: de
`PSEUDONYMIZATION_INTERNAL_DOMAINS` (JSON), con `--internal-domains` como
override explicito. Hoy el default del proyecto es `[]`.

## Nota de versionado

`.gitignore` (linea `data/Corpus Tesis*`) hoy ignora el corpus. Para publicar el
CSV como se pretende, hay que destrackear esa regla o forzar el add
(`git add -f "data/Corpus Tesis - Hoja 1.csv"`). Este harness NO modifica el
`.gitignore`.
