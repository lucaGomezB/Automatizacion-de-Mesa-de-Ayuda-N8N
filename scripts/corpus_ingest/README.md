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

## Nota de versionado

`.gitignore` (linea `data/Corpus Tesis*`) hoy ignora el corpus. Para publicar el
CSV como se pretende, hay que destrackear esa regla o forzar el add
(`git add -f "data/Corpus Tesis - Hoja 1.csv"`). Este harness NO modifica el
`.gitignore`.
