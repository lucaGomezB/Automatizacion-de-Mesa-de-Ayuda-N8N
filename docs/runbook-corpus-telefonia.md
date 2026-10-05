# Runbook — Perfil Compose `corpus` (medición de telefonía, c-70)

Este runbook documenta cómo correr la medición del corpus por el canal de
telefonía REAL contra un stack AISLADO, sin contaminar la base operativa, y cómo
conmutar y restaurar la Voice URL del TwiML App durante la corrida. Corresponde
a la sección 6 del change `c-70-softphone-corpus-telefonia` (decisión D8, OQ2 =
stack aislado completo).

Fuente de requisitos:
`openspec/changes/c-70-softphone-corpus-telefonia/specs/telefonia-corpus-medicion/spec.md`
(requirement "Corrida de telefonía sobre una base descartable").

## 1. Objetivo y alcance

- Correr el flujo telefónico real (`softphone -> TwiML App -> backend -> STT ->
  pseudonimización -> handoff N8N -> alta`) contra una base DESCARTABLE
  (`mesa_de_ayuda_corpus`) con volúmenes propios.
- Garantizar que una corrida de medición NO escribe en la base operativa
  (`mesa_de_ayuda`) ni toca sus volúmenes.
- Conmutar MANUALMENTE la Voice URL del TwiML App al backend del corpus y
  restaurarla al terminar.

Fuera de alcance de este runbook: el write-back al corpus y el `--replace`
(secciones 5 y 7 del change), y la métrica canónica de telefonía
(`docs/medicion-latencia-e2e.md` §5).

## 2. Servicios del perfil

Los tres servicios viven en `docker-compose.yml` bajo `profiles: ["corpus"]` y
NO arrancan con un `docker compose up` normal. El stack base queda intacto.

| Servicio | Base / destino | Puerto host | Volumen propio |
|----------|----------------|-------------|----------------|
| `postgres-corpus` | PostgreSQL 15.5, DB `mesa_de_ayuda_corpus` | `5434` (base operativa: `5433`) | `mesa_local_postgres_corpus_data` |
| `backend-corpus` | `DATABASE_URL` -> `postgres-corpus`; corre `alembic upgrade head` | `8001` (entrada del túnel propio) | — (solo bind del prompt) |
| `n8n-corpus` | `BACKEND_URL` -> `backend-corpus` | `5679` (N8N operativo: `5678`) | `mesa_local_n8n_corpus_data` |

Notas:

- `n8n-corpus` reutiliza el `redis` del stack base (sin estado y sin volumen):
  lo usa solo como memoria del agente. Por eso, al arrancar el perfil, Compose
  puede levantar también el contenedor `redis` del stack base si no estaba
  corriendo. No comparte datos de negocio.
- Los puertos del corpus están desplazados (`5434`, `8001`, `5679`) para poder
  coexistir con el stack base sin colisión.

## 3. Prerrequisitos

- Docker Compose v2 disponible (`docker compose version`).
- `.env` de la raíz con `POSTGRES_USER` / `POSTGRES_PASSWORD` /
  `COST_GUARD_SHARED_SECRET` (el compose los interpola).
- `App/Backend/.env` con `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`,
  `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` y `JWT_SECRET_KEY`.
- Un túnel público propio para el backend del corpus (por ejemplo `ngrok http
  8001`) apuntando al puerto host `8001`. El stack base usa `ngrok` sobre
  `nginx:443`; el corpus NO reutiliza ese túnel.
- Las credenciales y el workflow de N8N aislado siguen los mismos caveats que
  `docs/runbook-verificacion-telefonia-c52.md` §3.5 (credencial Header Auth del
  handoff, workflow activo, `BACKEND_URL`).

## 4. Arranque aislado

ADVERTENCIA: `docker compose --profile corpus up` a secas también levanta los
servicios SIN perfil del stack base (`postgres`, `backend`, `nginx`, `frontend`),
porque los servicios sin `profiles` quedan siempre activos en Compose. Para
arrancar SOLO el stack aislado, nombrar los servicios:

```bash
docker compose --profile corpus up -d postgres-corpus backend-corpus n8n-corpus
```

Verificar:

```bash
docker compose --profile corpus ps
```

Esperado: `postgres-corpus` y `backend-corpus` en `healthy`, `n8n-corpus` arriba,
y ningún contenedor base (`postgres`, `backend`, `n8n`, `nginx`, `frontend`).

El `command` de `backend-corpus` ejecuta `alembic upgrade head` antes de uvicorn,
de modo que la base descartable queda migrada al head vigente (hoy `010`) al
arrancar. Confirmar en logs:

```bash
docker logs mesa_local-backend-corpus-1 2>&1 | grep -E 'Running upgrade|Application startup complete'
```

## 5. Verificación de aislamiento (tarea 6.2)

1. La base del corpus existe, tiene las tablas migradas y acepta escrituras:

   ```bash
   docker exec mesa_local-postgres-corpus-1 psql -U mesa -d mesa_de_ayuda_corpus \
     -c "SELECT current_database();" \
     -c "SELECT version_num FROM alembic_version;"
   ```

   Esperado: `mesa_de_ayuda_corpus` y el head de Alembic (hoy `010`).

2. Los contenedores del corpus montan SOLO volúmenes del corpus (nunca
   `mesa_local_postgres_data` ni `mesa_local_n8n_data`):

   ```bash
   for c in mesa_local-postgres-corpus-1 mesa_local-backend-corpus-1 mesa_local-n8n-corpus-1; do
     echo "-- $c"; docker inspect -f '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{"\n"}}{{end}}' "$c"
   done
   ```

   Esperado: `mesa_local_postgres_corpus_data` y `mesa_local_n8n_corpus_data`.

3. Ningún contenedor del stack base está corriendo durante la corrida:

   ```bash
   docker ps --filter "name=mesa_local" --format '{{.Names}}'
   ```

   Esperado: solo los del corpus (y, si aplica, `mesa_local-redis-1`).

Como el `DATABASE_URL` de `backend-corpus` apunta exclusivamente a
`postgres-corpus` y ningún contenedor del corpus referencia los volúmenes de la
aplicación, una corrida no puede escribir en la base operativa.

## 6. Wipe seguro (tarea 6.3)

LIMITACIÓN CONFIRMADA DE COMPOSE v2: `docker compose --profile corpus down -v` a
secas borra TODOS los volúmenes de nivel superior del proyecto, incluidos
`mesa_local_postgres_data` y `mesa_local_n8n_data` del stack base. El motivo es
que los servicios sin `profiles` siguen activos y `down --volumes` elimina los
volúmenes declarados en el archivo, no solo los del perfil habilitado. Esto se
verificó empíricamente con un proyecto de prueba: el comando a secas eliminó
tanto el volumen del servicio con perfil como el del servicio sin perfil.

Para limpiar SOLO lo descartable, acotar los servicios a remover:

```bash
docker compose --profile corpus down -v postgres-corpus backend-corpus n8n-corpus
```

Verificar que los volúmenes de la aplicación sobreviven y que los del corpus se
eliminan:

```bash
docker volume ls --filter name=mesa_local --format '{{.Name}}'
```

Esperado tras el wipe: `mesa_local_postgres_data` y `mesa_local_n8n_data`
presentes; `mesa_local_postgres_corpus_data` y `mesa_local_n8n_corpus_data`
ausentes.

Si además se quiere detener el `redis` que el perfil pudo haber levantado como
dependencia (no tiene volumen ni datos de negocio):

```bash
docker compose down redis
```

## 7. Conmutación y restauración de la Voice URL del TwiML App (tarea 6.4)

El softphone inicia la llamada hacia un TwiML App cuya Voice URL apunta al
endpoint de voz (`POST /api/v1/cost-guard/twilio/voice`). Durante la corrida esa
URL debe apuntar al backend del CORPUS; al terminar, debe restaurarse. El SID del
TwiML App está en `TWILIO_TWIML_APP_SID` (formato `AP...`).

### 7.1 Antes de la corrida (conmutar al corpus)

1. Levantar el stack aislado (§4) y el túnel público hacia el backend del corpus:

   ```bash
   # En otra terminal, túnel propio sobre el puerto host 8001 del backend-corpus
   ngrok http 8001
   ```

2. Copiar la URL pública del túnel (por ejemplo `https://<subdominio>.ngrok-free.dev`).

3. Apuntar la Voice URL del TwiML App a esa URL + el path del endpoint de voz.

   Con Twilio CLI:

   ```bash
   twilio api:core:applications:update \
     --sid "$TWILIO_TWIML_APP_SID" \
     --voice-url "https://<subdominio>.ngrok-free.dev/api/v1/cost-guard/twilio/voice" \
     --voice-method POST
   ```

   O en la Consola: Voice > TwiML > TwiML Apps > (el App del softphone) >
   Voice URL = `https://<subdominio>.ngrok-free.dev/api/v1/cost-guard/twilio/voice`,
   Voice Method = `POST`.

4. Registrar la URL ANTERIOR (la de producción) antes de cambiarla, para poder
   restaurarla. Queda también en `BACKEND_PUBLIC_BASE_URL` de `App/Backend/.env`.

5. `backend-corpus` ya define `FORWARDED_ALLOW_IPS=*`, de modo que `request.url`
   reconstruye el esquema y el host públicos del túnel y la firma
   `X-Twilio-Signature` valida sobre la URL pública. Si aparece un `401` falso,
   revisar §7.1 del runbook C-52.

### 7.2 Después de la corrida (restaurar)

1. Apuntar la Voice URL del TwiML App de vuelta a la URL de producción:

   ```bash
   twilio api:core:applications:update \
     --sid "$TWILIO_TWIML_APP_SID" \
     --voice-url "https://tameness-trilogy-unrefined.ngrok-free.dev/api/v1/cost-guard/twilio/voice" \
     --voice-method POST
   ```

   O en la Consola: restaurar la Voice URL previa registrada en §7.1 paso 4.

2. Confirmar que el stack base (producción) sigue apuntando a su propio backend
   (su túnel sobre `nginx:443` no se tocó).

3. Ejecutar el wipe seguro (§6) y detener el túnel del corpus.

> Nota: la conmutación es MANUAL y deliberada. El stack aislado NO reutiliza el
> `nginx`/`ngrok`/`n8n` del stack base para no contaminar la operativa (D8).

## 8. Tradeoffs

- Más servicios que mantener y un N8N adicional; a cambio, aislamiento total y
  wipe limpio de los datos descartables.
- El wipe debe acotarse por servicio (§6): el comando a secas de Compose v2
  eliminaría también los volúmenes de la aplicación.
- `n8n-corpus` comparte el `redis` base (sin estado): no hay datos de negocio en
  juego, pero el perfil depende de que ese servicio esté disponible.

## 9. Evidencia de verificación (2026-10-05)

- `docker compose config -q` OK; servicios por defecto sin cambios (6) y con
  `--profile corpus` se agregan los 3 del corpus.
- `docker compose --profile corpus up -d postgres-corpus backend-corpus
  n8n-corpus`: `postgres-corpus` y `backend-corpus` `healthy`, `n8n-corpus`
  arriba; ningún contenedor base arrancado (salvo `redis` como dependencia).
- `backend-corpus` migró la base descartable hasta el head vigente (en la
  verificación inicial de la infra, `010`; el change c-70 agrega después la
  migración `011_telefonia_corpus_case_id`, por lo que el head actual es `011`);
  la DB `mesa_de_ayuda_corpus` respondió con las tablas del esquema y aceptó
  escrituras.
- `docker compose --profile corpus down -v postgres-corpus backend-corpus
  n8n-corpus`: eliminó solo `mesa_local_postgres_corpus_data` y
  `mesa_local_n8n_corpus_data`; `mesa_local_postgres_data` y
  `mesa_local_n8n_data` sobrevivieron.
- El comando a secas `docker compose --profile corpus down -v` se probó en un
  proyecto de prueba aislado y eliminó también el volumen del servicio sin
  perfil: por eso NO se usa sobre este repositorio.

## 10. Operador administrador del corpus (para el write-back)

El endpoint de lectura `GET /api/v1/telefonia/ingresos` y el de borrado
(`DELETE ...&dry_run=`) exigen un operador con rol `administrador_directorio`
(el rol se resuelve desde `directorio_empleado`, no desde `users`). La base
descartable del corpus arranca **sin** empleados, así que un `admin` recién
sembrado por la migración no tiene el rol y los endpoints responden 403.

Provisionar el directorio en la base descartable (seed dev-only, datos
sintéticos, dominio `.test`):

```bash
docker exec mesa_local-backend-corpus-1 python -m scripts.seed_directorio
```

Crea, entre otros, el operador `directorio.admin` (rol
`administrador_directorio`) con la clave `cambiar-esta-clave-admin`.

El script de write-back `scripts/corpus_ingest/ingest_telefonia_corpus.py` usa
`INGEST_OPERATOR_USERNAME` / `INGEST_OPERATOR_PASSWORD`; para la corrida del
corpus deben apuntar a ese operador admin (no a `admin`):

```bash
export INGEST_OPERATOR_USERNAME=directorio.admin
export INGEST_OPERATOR_PASSWORD=cambiar-esta-clave-admin  # gitleaks:allow (password de desarrollo, usuario sintetico)
python3 scripts/corpus_ingest/ingest_telefonia_corpus.py --base-url http://localhost:8001
```

Nota: en un entorno con `ENVIRONMENT=production` el seed queda como paso manual
del runbook; el endurecimiento del seed (guardia de entorno) se planifica en
`c-60-directorio-endurecimiento`.

## 11. Rate de la guarda de costo para la corrida

Los defaults de produccion de la guarda de costo (`c-45`) son **30 llamadas/hora
globales** y **3/hora por llamante**. Con esos valores, una corrida de 81 casos
desde el mismo softphone se bloquea a las 3 llamadas: la guarda deniega la
pre-llamada y Twilio reproduce "servicio no disponible en este momento".

El perfil `corpus` **relaja** el rate SOLO en `backend-corpus`
(`docker-compose.yml`), sin tocar el stack operativo:

```yaml
COST_GUARD_RATE_LIMIT_CALLS: "200"
COST_GUARD_CALLER_RATE_LIMIT_CALLS: "200"
```

- Se recrea el servicio con `docker compose --profile corpus up -d backend-corpus`.
- La guarda sigue activa (presupuesto semanal, reserva por proveedor); solo cambia
  el rate de admision. Presupuesto estimado de la corrida: ~USD 0.013 por llamada
  x 81 = ~USD 1.1 (tope semanal default: USD 10).
- Una llamada denegada por la guarda NO graba ni crea ingreso (se corta antes de
  la grabacion), por lo que no contamina el corpus.


